import json
import logging
import os
import os.path
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Literal, Tuple

import mrcfile
import numpy as np
import ome_zarr
import ome_zarr.io
import ome_zarr.writer
import zarr
from mrcfile.mrcfile import MrcFile
from ome_zarr.io import ZarrLocation
from ome_zarr.reader import Reader as Reader
from skimage.measure import block_reduce
from skimage.transform import resize_local_mean
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
)

from common.config import DepositionImportConfig
from common.fs import FileSystemApi, S3Filesystem
from common.retry import (
    RETRY_INITIAL_WAIT_SECONDS,
    RETRY_JITTER_SECONDS,
    RETRY_MAX_ATTEMPTS,
    RETRY_MAX_WAIT_SECONDS,
    is_s3_throttling,
    logger,
)


@dataclass
class VolumeInfo:
    voxel_size: float

    # start coords
    xstart: int
    ystart: int
    zstart: int

    # end coords
    xend: int
    yend: int
    zend: int

    # Data we save
    rms: float
    dmean: float

    def get_dimensions(self) -> Dict[str, int]:
        return {d: getattr(self, f"{d}end") - getattr(self, f"{d}start") for d in "xyz"}

    def get_max_dimension(self) -> int:
        return max(self.get_dimensions().values())

    def get_center_coords(self) -> List[int]:
        return [np.round(np.mean([getattr(self, f"{d}end"), getattr(self, f"{d}start")])) for d in "xyz"]


class ZarrReader:
    def __init__(self, fs, zarrdir):
        self.fs = fs
        self.zarrdir = zarrdir
        self._loc = None

    def get_data(self):
        loc = self._load_zarr_loc()
        data = loc.load("0")
        return data

    @property
    def attrs(self):
        loc = self._load_zarr_loc()
        group = zarr.group(loc.store)
        return group.attrs

    def _load_zarr_loc(self):
        if self._loc is None:
            self._loc = ome_zarr.io.ZarrLocation(self.fs.destformat(self.zarrdir))
        return self._loc


class ZarrWriter:
    def __init__(self, fs: FileSystemApi, zarrdir: str):
        self._init_zarr_store(fs, zarrdir)

    @retry(
        stop=stop_after_attempt(RETRY_MAX_ATTEMPTS),
        wait=wait_exponential_jitter(
            initial=RETRY_INITIAL_WAIT_SECONDS,
            max=RETRY_MAX_WAIT_SECONDS,
            jitter=RETRY_JITTER_SECONDS,
        ),
        retry=retry_if_exception(is_s3_throttling),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def _init_zarr_store(self, fs: FileSystemApi, zarrdir: str):
        if isinstance(fs, S3Filesystem):
            fsstore = zarr.storage.FSStore(url=zarrdir, mode="w", fs=fs.s3fs, dimension_separator="/")
            self.loc = ZarrLocation(fsstore)
        else:
            self.loc = ome_zarr.io.parse_url(zarrdir, mode="w")
        self.root_group = zarr.group(self.loc.store, overwrite=True)

    def ome_zarr_axes(self) -> List[Dict[str, str]]:
        return [
            {
                "name": "z",
                "type": "space",
                "unit": "angstrom",
            },
            {
                "name": "y",
                "type": "space",
                "unit": "angstrom",
            },
            {
                "name": "x",
                "type": "space",
                "unit": "angstrom",
            },
        ]

    def ome_zarr_transforms(self, voxel_size: Tuple[float, float, float]) -> List[Dict[str, Any]]:
        return [{"scale": [voxel_size[0], voxel_size[1], voxel_size[2]], "type": "scale"}]

    @retry(
        stop=stop_after_attempt(RETRY_MAX_ATTEMPTS),
        wait=wait_exponential_jitter(
            initial=RETRY_INITIAL_WAIT_SECONDS,
            max=RETRY_MAX_WAIT_SECONDS,
            jitter=RETRY_JITTER_SECONDS,
        ),
        retry=retry_if_exception(is_s3_throttling),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def write_data(
        self,
        data: List[np.ndarray],
        voxel_spacing: List[Tuple[float, float, float]],
        chunk_size: Tuple[int, int, int] = (256, 256, 256),
        scale_z_axis: bool = True,
        store_labels_metadata: bool = False,
    ):
        pyramid = []
        scales = []

        # If voxel_size is a list, it must match the length of the data
        if len(voxel_spacing) != len(data):
            raise ValueError(f"Length of voxel_size ({len(voxel_spacing)}) must match length of data ({len(data)})")

        # Store each layer of the pyramid and its corresponding voxel size
        for d, vs in zip(data, voxel_spacing):
            pyramid.append(d)
            scales.append(self.ome_zarr_transforms(vs))

        # Store the labels contained in the data if the flag is activated
        metadata = {}
        if store_labels_metadata:
            arr = data[0]
            labels = [int(label) for label in np.unique(arr) if label > 0]
            label_values = [{"label-value": label} for label in labels]
            metadata["image-label"] = {"version": "0.4", "colors": label_values}

        # TODO: Currently not being used because of memory spikes for large volumes (100GB+ memory spikes for 10GB+ data)
        # Fixed in latest version of ome_zarr (0.12.2), but can't upgrade because Zarr V3 is required and we don't support Zarr V3 yet.
        # # Write the pyramid to the zarr store
        # return ome_zarr.writer.write_multiscale(
        #     pyramid,
        #     group=self.root_group,
        #     axes=self.ome_zarr_axes(),
        #     coordinate_transformations=scales,
        #     storage_options=dict(chunks=chunk_size, overwrite=True),
        #     compute=True,
        #     metadata=metadata,
        # )
        # TODO: Remove this temporary workaround
        datasets_meta = []

        for i, (arr, vs) in enumerate(zip(data, voxel_spacing)):
            path = str(i)
            zds = self.root_group.create_dataset(
                path,
                shape=arr.shape,
                dtype=arr.dtype,
                chunks=chunk_size,
                overwrite=True,
            )

            z, y, x = map(int, arr.shape)
            zc, yc, xc = map(int, chunk_size)

            for z0 in range(0, z, zc):
                z1 = min(z0 + zc, z)
                for y0 in range(0, y, yc):
                    y1 = min(y0 + yc, y)
                    for x0 in range(0, x, xc):
                        x1 = min(x0 + xc, x)
                        zds[z0:z1, y0:y1, x0:x1] = np.asarray(arr[z0:z1, y0:y1, x0:x1], dtype=arr.dtype, order="C")

            datasets_meta.append(
                {
                    "path": path,
                    "coordinateTransformations": self.ome_zarr_transforms(vs),
                },
            )

        ome_zarr.writer.write_multiscales_metadata(
            group=self.root_group,
            axes=self.ome_zarr_axes(),
            datasets=datasets_meta,
            name="/",
            metadata=metadata,
        )


class VolumeReader(ABC):
    data: np.ndarray | None
    filename: str

    @abstractmethod
    def get_pyramid_base_data(self) -> np.ndarray:
        pass

    @abstractmethod
    def get_volume_info(self) -> VolumeInfo:
        pass

    def get_mrc_extended_header(self) -> np.ndarray | np.recarray | None:
        return None

    def get_mrc_header(self) -> np.recarray | None:
        return None


class MRCReader(VolumeReader):
    filename: str
    header: np.rec.array
    extended_header: np.rec.array
    _voxel_size: float

    def __init__(self, fs: FileSystemApi, filename: str, header_only: bool = False):
        if header_only:
            self.filename = fs.read_block(filename)
        else:
            self.filename = fs.localreadable(filename)
        with mrcfile.open(self.filename, permissive=True, header_only=header_only) as mrc:
            if mrc.data is None and not header_only:
                raise Exception("missing mrc data")
            self.header = mrc.header
            self._voxel_size = mrc.voxel_size.y.item()
            self.extended_header = mrc.extended_header
            self.data: np.ndarray = mrc.data

    def get_mrc_header(self) -> np.recarray:
        return self.header

    def get_mrc_extended_header(self) -> np.ndarray | np.recarray:
        return self.extended_header

    def get_pyramid_base_data(self) -> np.ndarray:
        # We have some tomograms that were written before the 2014 spec was finalized and
        # decided that MRC type 0 should store *signed* integers. The older mrc's store each
        # voxel value as *unsigned* int8, while the MRC library reads that data as signed
        # int8. Here we're remapping the overflowed/mangled uint8 data to a continuous
        # range of int8 data. We're using the `dtype` header field to determine whether data
        # has likely overflowed and needs to be corrected. This field is marked as optional in
        # the spec, so it's possible some volumes that need correction will escape this check.
        if self.header.dmax > 127 and self.data.dtype == np.int8:
            return np.where(self.data < 0, 128 + self.data, -128 + self.data).astype(np.float32)
        return self.data.astype(np.float32)

    def get_volume_info(self) -> VolumeInfo:
        return VolumeInfo(
            self._voxel_size,
            self.header.nxstart.item(),
            self.header.nystart.item(),
            self.header.nzstart.item(),
            self.header.nx.item(),
            self.header.ny.item(),
            self.header.nz.item(),
            self.header.rms.item(),
            self.header.dmean.item(),
        )


class OMEZarrReader(VolumeReader):
    _header_only: bool
    _attrs: dict[str, Any]

    def __init__(self, fs: FileSystemApi, filename: str, header_only: bool = False, level: int = 0):
        self.filename = filename

        if isinstance(fs, S3Filesystem):
            fsstore = zarr.storage.FSStore(url=filename, mode="w", fs=fs.s3fs)
            self.loc = ZarrLocation(fsstore)
        else:
            self.loc = ome_zarr.io.parse_url(filename, mode="w")

        # parsed_url = zarr_parse_url(filename, mode="r")
        reader = Reader(self.loc)

        nodes = list(reader())
        self._attrs = self.loc.root_attrs
        self._shape = nodes[0].data[0].shape
        self._header_only = header_only

        if not header_only:
            self.data = np.asarray(nodes[0].data[level])

    def get_pyramid_base_data(self) -> np.ndarray:
        return self.data.astype(np.float32)

    def get_volume_info(self) -> VolumeInfo:
        rms = 0.0
        dmean = 0.0

        # TODO - We don't currently need to return dmean/rms for zarrs, so let's skip it for now.
        # if not self._header_only:
        #     rms = np.sqrt(np.mean((self.data - np.mean(self.data)) ** 2))  # Calculate RMS,
        #     dmean = np.mean(self.data)  # Calculate dmean

        z, y, x = self._shape
        return VolumeInfo(
            self._attrs["multiscales"][0]["datasets"][0]["coordinateTransformations"][0]["scale"][1],
            0,
            0,
            0,
            x,
            y,
            z,
            rms,
            dmean,
        )


class TomoConverter:
    def __init__(
        self,
        fs: FileSystemApi,
        filename: str,
        header_only: bool = False,
        scale_0_dims: tuple[int, int, int] | None = None,
        level=0,
    ):
        if ".zarr" in filename:
            self.volume_reader = OMEZarrReader(fs, filename, header_only, level=level)
        else:
            self.volume_reader = MRCReader(fs, filename, header_only)
        self.scale_0_dims = scale_0_dims

    def get_pyramid_base_data(self) -> np.ndarray:
        """Returns the base data for the pyramid. Resizes the data to scale_0_dims if it is set."""
        if self.scale_0_dims is not None:
            return resize_local_mean(self.volume_reader.get_pyramid_base_data(), self.scale_0_dims, preserve_range=True)
        else:
            return self.volume_reader.get_pyramid_base_data()

    @classmethod
    def scaled_data_transformation(cls, data: np.ndarray) -> np.ndarray:
        return data

    def get_voxel_size(self) -> float:
        return self.get_volume_info().voxel_size

    def get_volume_info(self) -> VolumeInfo:
        return self.volume_reader.get_volume_info()

    def get_contrast_limits(self, method: Literal["gmm", "cdf"] = "gmm"):
        assert isinstance(self.volume_reader, OMEZarrReader)
        from cryoet_data_portal_neuroglancer.precompute.contrast_limits import compute_contrast_limits

        return compute_contrast_limits(self.volume_reader.data, method=method)

    def get_downscale_interpolation_func(self):
        def downscale_method(data: np.ndarray, block_size: Tuple[int, int, int]) -> np.ndarray:
            return block_reduce(data, block_size=block_size, func=np.mean)
        return downscale_method

    # Make an array of an original size image, plus `max_layers` half-scaled images
    def make_pyramid(
        self,
        max_layers: int = 2,
        scale_z_axis: bool = True,
        voxel_spacing: float = None,
        dtype: str = None,
    ) -> Tuple[List[np.ndarray], List[Tuple[float, float, float]]]:
        # Voxel size for unbinned
        if not voxel_spacing:
            voxel_spacing = self.get_voxel_size()

        # Ensure voxel spacing rounded to 3rd digit
        voxel_spacing = round(voxel_spacing, 3)

        pyramid = [self.scaled_data_transformation(self.get_pyramid_base_data())]
        pyramid_voxel_spacing = [(voxel_spacing, voxel_spacing, voxel_spacing)]
        z_scale = 2 if scale_z_axis else 1
        # Then make a pyramid of 100/50/25 percent scale volumes
        downscale_method = self.get_downscale_interpolation_func()
        for i in range(max_layers):
            downscaled_data = self.scaled_data_transformation(
                downscale_method(data=pyramid[i], block_size=(z_scale, 2, 2)),
            )
            pyramid.append(downscaled_data.astype(dtype) if dtype else downscaled_data)
            pyramid_voxel_spacing.append(
                (
                    pyramid_voxel_spacing[i][0] * z_scale,
                    pyramid_voxel_spacing[i][1] * 2,
                    pyramid_voxel_spacing[i][2] * 2,
                ),
            )

        return pyramid, pyramid_voxel_spacing

    def pyramid_to_mrc(
        self,
        fs: FileSystemApi,
        pyramid: List[np.ndarray],
        filename: str,
        write: bool = True,
        header_mapper: Callable[[np.array], None] = None,
        voxel_spacing: float = None,
    ) -> List[str]:
        mrcfiles = []
        # NOTE - 2023-10-24
        # We are no longer binning tomograms to multiple scales. We can include multiscale
        # in our omezarr's but generating smaller MRC's just confuses everyone.
        filename = fs.localwritable(filename)
        mrcfiles.append(os.path.basename(filename))

        if write:
            newfile = mrcfile.new(filename, pyramid[0], overwrite=True)
            self.update_headers(newfile, header_mapper, voxel_spacing)
            newfile.flush()
            newfile.close()

            fs.push(filename)
        else:
            print(f"skipping remote push for {filename}")
        return mrcfiles

    def pyramid_to_omezarr(
        self,
        fs: FileSystemApi,
        pyramid: List[np.ndarray],
        zarrdir: str,
        write: bool = True,
        pyramid_voxel_spacing: List[Tuple[float, float, float]] = None,
        chunk_size: Tuple[int, int, int] = (256, 256, 256),
        store_labels_metadata: bool = False,
    ) -> str:
        destination_zarrdir = fs.destformat(zarrdir)
        # Write zarr data as 256^3 voxel chunks
        if write:
            writer = ZarrWriter(fs, destination_zarrdir)
            writer.write_data(
                pyramid,
                voxel_spacing=pyramid_voxel_spacing,
                chunk_size=chunk_size,
                store_labels_metadata=store_labels_metadata,
            )
        else:
            print(f"skipping remote push for {destination_zarrdir}")
        return os.path.basename(zarrdir)

    def update_headers(self, mrcfile: MrcFile, header_mapper, voxel_spacing):
        header = mrcfile.header
        data = mrcfile.data
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        isotropic_voxel_size = np.float32(voxel_spacing) if voxel_spacing else self.get_voxel_size()
        header.cella.x = isotropic_voxel_size * data.shape[2]
        header.cella.y = isotropic_voxel_size * data.shape[1]
        header.cella.z = isotropic_voxel_size * data.shape[0]
        header.label[0] = "{0:40s}{1:>39s}".format("Validated by cryoET data portal.", time)
        header.rms = np.sqrt(np.mean((data - np.mean(data)) ** 2))

        header.nsymbt = np.array(0, dtype="i4")
        header.exttyp = np.array(b"MRCO", dtype="S4")

        # If we're converting an MRC to another MRC, copy over some header info.
        if old_header := self.volume_reader.get_mrc_header():
            header.extra1 = old_header.extra1
            header.extra2 = old_header.extra2
            if old_header.exttyp.item().decode().strip():
                ext = self.volume_reader.get_mrc_extended_header()
                # In order to cover the following cases:
                # 1. do set on filled np.ndarray > np.array(val: np.ndarray).tolist() -> list
                # 2. do set on filled np.recarray > np.array(val: np.recarray).tolist() -> list
                # 3. skip setting on empty np.ndarray > np.array(np.empty(0)).tolist() == []
                # 4. skip setting on None > np.array(None).tolist() == None
                if np.array(ext).tolist():
                    header.exttyp = old_header.exttyp
                    mrcfile.set_extended_header(ext)
                else:
                    # Empty extended header
                    header.exttyp = b"MRCO"
                    header.nsymbt = 0

        if header_mapper:
            header_mapper(header)


class MaskConverter(TomoConverter):
    def __init__(
        self,
        fs: FileSystemApi,
        filename: str,
        label: int = 1,
        header_only: bool = False,
        scale_0_dims: tuple[int, int, int] | None = None,
        threshold: float | None = None,
    ):
        super().__init__(fs=fs, filename=filename, header_only=header_only, scale_0_dims=scale_0_dims)
        self.label = label
        self.threshold = threshold

    def get_pyramid_base_data(self) -> np.ndarray:
        # When thresholding, do it after scaling. When already binary, extract the mask before scaling.
        if self.threshold is not None and self.scale_0_dims is not None:
            scale_before = True
            scale_after = False
        elif self.threshold is None and self.scale_0_dims is not None:
            scale_before = False
            scale_after = True
        else:
            scale_before = False
            scale_after = False

        if scale_before:
            data = resize_local_mean(self.volume_reader.get_pyramid_base_data(), self.scale_0_dims, preserve_range=True)
        else:
            data = self.volume_reader.get_pyramid_base_data()

        if self.threshold is not None:
            data = (data >= self.threshold).astype(np.int8)
        else:
            data = (data == self.label).astype(np.int8)

        if scale_after:
            data = resize_local_mean(data, self.scale_0_dims, preserve_range=True)

        return self.scaled_data_transformation(data)

    @classmethod
    def scaled_data_transformation(cls, data: np.ndarray) -> np.ndarray:
        # For semantic segmentation masks we want to have a binary output.
        # downscale_local_mean will return float array even for bool input with non-binary values
        return (data > 0).astype(np.int8)

    def has_label(self) -> bool:
        if self.threshold is not None:
            return bool(np.any(self.volume_reader.get_pyramid_base_data() >= self.threshold))
        else:
            return bool(np.any(self.volume_reader.get_pyramid_base_data() == self.label))


class MultiLabelMaskConverter(TomoConverter):
    def __init__(
        self,
        fs: FileSystemApi,
        filename: str,
        header_only: bool = False,
        scale_0_dims: tuple[int, int, int] | None = None,
    ):
        super().__init__(fs=fs, filename=filename, header_only=header_only, scale_0_dims=scale_0_dims)

    def get_pyramid_base_data(self) -> np.ndarray:
        data = self.volume_reader.get_pyramid_base_data()

        if not self.scale_0_dims:
            return self.scaled_data_transformation(data)

        from scipy.ndimage import zoom

        x, y, z = data.shape
        nx, ny, nz = self.scale_0_dims
        zoom_factor = (nx / x, ny / y, nz / z)
        if zoom_factor == (1.0, 1.0, 1.0):
            return self.scaled_data_transformation(data)

        rescaled = zoom(data, zoom=zoom_factor, order=0)

        return self.scaled_data_transformation(rescaled)

    @classmethod
    def scaled_data_transformation(cls, data: np.ndarray) -> np.ndarray:
        # For instance segmentation masks we have multiple labels, so we want an uint 16 output.
        # We used uint16 and not uint32 as it seems MRC format doesn't handle well int > 16.
        # zoom will return float array even for bool input with non-binary values
        return data.astype(np.uint16)

    def get_downscale_interpolation_func(self):
        # nearest-neighbor interpolation
        def downscale_method(data: np.ndarray, block_size: Tuple[int, int, int]) -> np.ndarray:
            bz, by, bx = block_size
            return data[::bz, ::by, ::bx]
        return downscale_method


def get_volume_metadata(config: DepositionImportConfig, output_prefix: str) -> dict[str, Any]:
    # Generates metadata related to volume files.
    scales = []
    fs = config.fs
    size: dict[str, float] = {}
    omezarr_dir = f"{output_prefix}.zarr"
    dest_zarr_dir = fs.destformat(omezarr_dir)
    with open(fs.localreadable(os.path.join(dest_zarr_dir, ".zattrs")), "r") as fh:
        zarrinfo = json.loads(fh.read())
    multiscales = zarrinfo["multiscales"][0]["datasets"]
    for scale in multiscales:
        with open(fs.localreadable(os.path.join(dest_zarr_dir, scale["path"], ".zarray")), "r") as fh:
            scaleinfo = json.loads(fh.read())
        shape = scaleinfo["shape"]
        dims = {"z": shape[0], "y": shape[1], "x": shape[2]}
        if not size:
            size = dims
        scales.append(dims)
    return {
        "scales": scales,
        "size": size,
        "omezarr_dir": config.to_formatted_path(omezarr_dir),
        "mrc_file": config.to_formatted_path(f"{output_prefix}.mrc"),
    }


def get_voxel_size(fs: FileSystemApi, tomo_filename: str) -> float:
    return get_volume_info(fs, tomo_filename).voxel_size


def get_volume_info(fs: FileSystemApi, tomo_filename: str) -> VolumeInfo:
    return TomoConverter(fs, tomo_filename, header_only=True).get_volume_info()


def get_volume_contrast_limits(
    fs: FileSystemApi,
    tomo_filename: str,
    method: Literal["gmm", "cdf"] = "gmm",
) -> tuple[float, float]:
    return TomoConverter(fs, tomo_filename, level=-1).get_contrast_limits(method=method)


def get_converter(
    fs: FileSystemApi,
    tomo_filename: str,
    label: int | None = None,
    scale_0_dims: tuple[int, int, int] | None = None,
    threshold: float | None = None,
    multilabels: bool = False,
) -> TomoConverter | MaskConverter:
    if multilabels:
        return MultiLabelMaskConverter(fs, tomo_filename, scale_0_dims=scale_0_dims)
    if label is not None:
        return MaskConverter(fs, tomo_filename, label, scale_0_dims=scale_0_dims, threshold=threshold)
    return TomoConverter(fs, tomo_filename, scale_0_dims=scale_0_dims)


def make_pyramids(
    fs: FileSystemApi,
    output_prefix: str,
    tomo_filename: str,
    scale_z_axis: bool = True,
    write_mrc: bool = True,
    write_zarr: bool = True,
    header_mapper: Callable[[np.array], None] = None,
    voxel_spacing: float | None = None,
    label: int = None,
    scale_0_dims=None,
    threshold: float | None = None,
    chunk_size: Tuple[int, int, int] = (256, 256, 256),
    multilabels: bool = False,
    dtype: str = None,
):
    tc = get_converter(fs, tomo_filename, label, scale_0_dims, threshold, multilabels=multilabels)
    pyramid, pyramid_voxel_spacing = tc.make_pyramid(
        scale_z_axis=scale_z_axis,
        voxel_spacing=voxel_spacing,
        dtype=dtype,
    )
    _ = tc.pyramid_to_omezarr(
        fs,
        pyramid,
        f"{output_prefix}.zarr",
        write_zarr,
        pyramid_voxel_spacing=pyramid_voxel_spacing,
        chunk_size=chunk_size,
        store_labels_metadata=multilabels,
    )
    _ = tc.pyramid_to_mrc(fs, pyramid, f"{output_prefix}.mrc", write_mrc, header_mapper, voxel_spacing)


def check_mask_for_label(
    fs: FileSystemApi,
    tomo_filename: str,
    label: int,
    threshold: float | None = None,
) -> bool:
    mc = MaskConverter(fs, tomo_filename, label, threshold=threshold)
    return mc.has_label()
