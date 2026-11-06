import os
import os.path
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property
from typing import Any, Callable, Dict, List, Literal, Tuple

import dask.array as da
import mrcfile
import numpy as np
from cryoet_data_portal_neuroglancer.io import OmeZarrImage, load_omezarr_data, open_omezarr
from mrcfile.mrcfile import MrcFile
from skimage.measure import block_reduce
from skimage.transform import resize_local_mean

from common.config import DepositionImportConfig
from common.fs import FileSystemApi
from common.ome_zarr_writer import write_label_pyramid, write_tilt_series, write_volume

# Image types written under the cryoET storage profile (common.cryoet_profile); other volumes (segmentation masks)
# keep their own conventions.
ProfileImageType = Literal["volume", "tilt_series"]


@dataclass
class VolumeInfo:
    voxel_size: float

    # dimensions
    xdim: int
    ydim: int
    zdim: int

    # Data we save
    rms: float
    dmean: float

    def get_dimensions(self) -> Dict[str, int]:
        return {d: getattr(self, f"{d}dim") for d in "xyz"}

    def get_max_dimension(self) -> int:
        return max(self.get_dimensions().values())


class ZarrReader:
    """An OME-Zarr image written by the Portal (Zarr v3 / OME-NGFF 0.5, or Zarr v2 / 0.4 from before the switch)."""

    def __init__(self, fs: FileSystemApi, zarrdir: str):
        self.fs = fs
        self.zarrdir = zarrdir

    @cached_property
    def image(self) -> OmeZarrImage:
        return open_omezarr(self.fs.zarr_store(self.fs.destformat(self.zarrdir)))

    def get_data(self, level: int | str = 0, decode: bool = False) -> da.Array:
        """A level as a 3-D dask array (singleton t/c axes dropped): stored values (int16 codes for profile
        volumes) unless ``decode``."""
        return load_omezarr_data(self.image.group, resolution_level=level, persist=False, decode=decode)

    @property
    def attrs(self) -> dict[str, Any]:
        return dict(self.image.group.attrs)

    @property
    def axes(self) -> list[str]:
        return self.image.axes

    @property
    def label_values(self) -> list[int] | None:
        return self.image.label_values

    def dataset_statistics(self) -> dict[str, float] | None:
        """Level-0 image statistics of a cryoET-profile image (in stored units), or None."""
        stats = self.attrs.get("dca", {}).get("normalization_statistics", {}).get("0", {})
        return stats.get("dataset_statistics")


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
            self.header.nx.item(),
            self.header.ny.item(),
            self.header.nz.item(),
            self.header.rms.item(),
            self.header.dmean.item(),
        )


class OMEZarrReader(VolumeReader):
    """An OME-Zarr volume: a source deposited as Zarr (v2 / OME-NGFF 0.4, e.g. copick) or a Portal output (v3 / 0.5).

    ``data`` holds the stored values of the requested level, as 3-D (singleton t/c axes dropped): int16 codes for
    cryoET-profile volumes. ``get_pyramid_base_data`` decodes them (CF ``scale_factor``/``add_offset``) to float32.
    """

    def __init__(self, fs: FileSystemApi, filename: str, header_only: bool = False, level: int = 0):
        self.filename = filename
        self.image = open_omezarr(fs.zarr_store(filename))
        self._shape = tuple(int(n) for n in self.image.array(0).shape[-3:])
        self._header_only = header_only
        if not header_only:
            self.data = np.asarray(load_omezarr_data(self.image.group, resolution_level=level, persist=False))

    def get_pyramid_base_data(self) -> np.ndarray:
        sf, ao = self.image.scale_factor, self.image.add_offset
        if sf is None and ao is None:
            return self.data.astype(np.float32)
        return (self.data.astype(np.float64) * (1.0 if sf is None else sf) + (ao or 0.0)).astype(np.float32)

    def get_voxel_size(self) -> float:
        return float(self.image.scale(0)[self.image.axes.index("x")])

    def get_volume_info(self) -> VolumeInfo:
        # dmean/rms are not needed for zarr sources (they are only read from MRC headers).
        z, y, x = self._shape
        return VolumeInfo(self.get_voxel_size(), x, y, z, 0.0, 0.0)


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
        """Write a segmentation-mask pyramid as Zarr v3 / OME-NGFF 0.5 (tomograms and tilt series are written by
        ``make_pyramids(image_type=...)`` under the cryoET profile instead)."""
        destination_zarrdir = fs.destformat(zarrdir)
        if write:
            label_values = None
            if store_labels_metadata:
                label_values = [int(label) for label in np.unique(pyramid[0]) if label > 0]
            write_label_pyramid(
                fs,
                pyramid,
                destination_zarrdir,
                voxel_spacing=pyramid_voxel_spacing,
                chunk_size=chunk_size,
                label_values=label_values,
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
    # Generates metadata related to volume files: the z, y, x sizes of every level (the last three axes, so 5-D
    # [t, c, z, y, x] volumes report the same keys as 3-D ones).
    scales = []
    fs = config.fs
    omezarr_dir = f"{output_prefix}.zarr"
    image = ZarrReader(fs, omezarr_dir).image
    for dataset in image.datasets:
        z, y, x = (int(n) for n in image.array(dataset["path"]).shape[-3:])
        scales.append({"z": z, "y": y, "x": x})
    size = scales[0] if scales else {}
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
    image_type: ProfileImageType | None = None,
):
    """Convert a volume to OME-Zarr (Zarr v3 / OME-NGFF 0.5) and MRC.

    With ``image_type`` ("volume" for tomograms, "tilt_series"), the Zarr follows the cryoET storage profile
    (``common.cryoet_profile``: int16 codes and mean-binned levels for volumes, Fourier-cropped float32 levels for
    tilt series); ``scale_z_axis``, ``chunk_size`` and ``dtype`` are then fixed by the profile. Without it (segmentation
    masks), a 3-level pyramid of the converter is written with ``chunk_size`` chunks. The MRC is level 0 as float32
    (or the mask dtype) in both cases.
    """
    if image_type is not None:
        tc = TomoConverter(fs, tomo_filename, scale_0_dims=scale_0_dims)
        base = tc.get_pyramid_base_data()
        spacing = round(voxel_spacing if voxel_spacing else tc.get_voxel_size(), 3)
        zarr_dir = fs.destformat(f"{output_prefix}.zarr")
        if write_zarr:
            writer = write_volume if image_type == "volume" else write_tilt_series
            writer(fs, base, zarr_dir, spacing)
        else:
            print(f"skipping remote push for {zarr_dir}")
        tc.pyramid_to_mrc(fs, [base], f"{output_prefix}.mrc", write_mrc, header_mapper, voxel_spacing)
        return

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
