import json
import os
import os.path
from datetime import datetime
from typing import Any, Callable, Dict, List, Tuple

import mrcfile
import numpy as np
import ome_zarr
import ome_zarr.io
import ome_zarr.writer
import zarr
from mrcfile.mrcfile import MrcFile
from mrcfile.mrcobject import MrcObject
from skimage.transform import downscale_local_mean

from common.fs import FileSystemApi


class ZarrReader:
    def __init__(self, fs, zarrdir):
        self.fs = fs
        self.zarrdir = zarrdir

    def get_data(self):
        loc = ome_zarr.io.ZarrLocation(self.fs.destformat(self.zarrdir))
        data = loc.load("0")
        return data


class ZarrWriter:
    def __init__(self, zarrdir: str):
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

    def write_data(
        self,
        data: List[np.ndarray],
        voxel_spacing: List[Tuple[float, float, float]],
        chunk_size: Tuple[int, int, int] = (256, 256, 256),
        scale_z_axis: bool = True,
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

        # Write the pyramid to the zarr store
        return ome_zarr.writer.write_multiscale(
            pyramid,
            group=self.root_group,
            axes=self.ome_zarr_axes(),
            coordinate_transformations=scales,
            storage_options=dict(chunks=chunk_size, overwrite=True),
            compute=True,
        )


class TomoConverter:
    def __init__(self, fs: FileSystemApi, mrc_filename: str, header_only: bool = False):
        if header_only:
            self.mrc_filename = fs.read_block(mrc_filename)
        else:
            self.mrc_filename = fs.localreadable(mrc_filename)
        with mrcfile.open(self.mrc_filename, permissive=True, header_only=header_only) as mrc:
            if mrc.data is None and not header_only:
                raise Exception("missing mrc data")
            self.header = mrc.header
            self.extended_header = mrc.extended_header
            self.voxel_size: np.rec.array = mrc.voxel_size
            self.data: np.ndarray = mrc.data

    def get_pyramid_base_data(self) -> np.ndarray:
        return self.data.astype(np.float32)

    @classmethod
    def scaled_data_transformation(cls, data: np.ndarray) -> np.ndarray:
        return data

    # Make an array of an original size image, plus `max_layers` half-scaled images
    def make_pyramid(
        self,
        max_layers: int = 2,
        scale_z_axis: bool = True,
        voxel_spacing: float = None,
    ) -> Tuple[List[np.ndarray], List[Tuple[float, float, float]]]:
        # Voxel size for unbinned
        if not voxel_spacing:
            voxel_spacing = self.get_voxel_size()

        # Ensure voxel spacing rounded to 3rd digit
        voxel_spacing = round(voxel_spacing, 3)

        pyramid = [self.get_pyramid_base_data()]
        pyramid_voxel_spacing = [(voxel_spacing, voxel_spacing, voxel_spacing)]
        z_scale = 2 if scale_z_axis else 1
        # Then make a pyramid of 100/50/25 percent scale volumes
        for i in range(max_layers):
            downscaled_data = self.scaled_data_transformation(downscale_local_mean(pyramid[i], (z_scale, 2, 2)))
            pyramid.append(downscaled_data)
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
        mrc_filename: str,
        write: bool = True,
        header_mapper: Callable[[np.array], None] = None,
        voxel_spacing: float = None,
    ) -> List[str]:
        mrcfiles = []
        # NOTE - 2023-10-24
        # We are no longer binning tomograms to multiple scales. We can include multiscale
        # in our omezarr's but generating smaller MRC's just confuses everyone.
        filename = fs.localwritable(mrc_filename)
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
    ) -> str:
        destination_zarrdir = fs.destformat(zarrdir)
        # Write zarr data as 256^3 voxel chunks
        if write:
            writer = ZarrWriter(destination_zarrdir)
            writer.write_data(pyramid, voxel_spacing=pyramid_voxel_spacing, chunk_size=(256, 256, 256))
        else:
            print(f"skipping remote push for {destination_zarrdir}")
        return os.path.basename(zarrdir)

    def get_voxel_size(self) -> np.float32:
        return self.voxel_size.y

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
        header.extra1 = self.header.extra1
        header.extra2 = self.header.extra2

        if self.header.exttyp.item().decode().strip():
            mrcfile.set_extended_header(self.extended_header)
            header.nsymbt = self.header.nsymbt
            header.exttyp = self.header.exttyp
        else:
            header.nsymbt = np.array(0, dtype="i4")
            header.exttyp = np.array(b"MRCO", dtype="S4")

        if header_mapper:
            header_mapper(header)


class MaskConverter(TomoConverter):
    def __init__(self, fs: FileSystemApi, mrc_filename: str, label: int = 1, header_only: bool = False):
        super().__init__(fs, mrc_filename, header_only)
        self.label = label

    def get_pyramid_base_data(self) -> np.ndarray:
        return (self.data == self.label).astype(np.int8)

    @classmethod
    def scaled_data_transformation(cls, data: np.ndarray) -> np.ndarray:
        # For semantic segmentation masks we want to have a binary output.
        # downscale_local_mean will return float array even for bool input with non-binary values
        return (data > 0).astype(np.int8)

    def has_label(self) -> bool:
        return np.any(self.data == self.label)


def get_tomo_metadata(
    fs: FileSystemApi,
    output_prefix: str,
) -> dict[str, Any]:
    # Write a tomo metadata file.
    scales = []
    size: dict[str, float] = {}
    omezarr_dir = fs.destformat(f"{output_prefix}.zarr")
    with open(fs.localreadable(os.path.join(omezarr_dir, ".zattrs")), "r") as fh:
        zarrinfo = json.loads(fh.read())
    multiscales = zarrinfo["multiscales"][0]["datasets"]
    for scale in multiscales:
        with open(fs.localreadable(os.path.join(omezarr_dir, scale["path"], ".zarray")), "r") as fh:
            scaleinfo = json.loads(fh.read())
        shape = scaleinfo["shape"]
        dims = {"z": shape[0], "y": shape[1], "x": shape[2]}
        if not size:
            size = dims
        scales.append(dims)

    output_json = {
        "scales": scales,
        "size": size,
        "omezarr_dir": os.path.basename(omezarr_dir),
        "mrc_files": [os.path.basename(f"{output_prefix}.mrc")],
    }
    return output_json


def get_voxel_size(fs: FileSystemApi, tomo_filename: str) -> np.float32:
    return TomoConverter(fs, tomo_filename, header_only=True).get_voxel_size()


def get_header(fs: FileSystemApi, tomo_filename: str) -> MrcObject:
    return TomoConverter(fs, tomo_filename, header_only=True).header


def get_converter(fs: FileSystemApi, tomo_filename: str, label: int | None = None):
    if label is not None:
        return MaskConverter(fs, tomo_filename, label)
    return TomoConverter(fs, tomo_filename)


def scale_mrcfile(
    fs: FileSystemApi,
    output_prefix: str,
    tomo_filename: str,
    scale_z_axis: bool = True,
    write_mrc: bool = True,
    write_zarr: bool = True,
    header_mapper: Callable[[np.array], None] = None,
    voxel_spacing=None,
    label: int = None,
):
    tc = get_converter(fs, tomo_filename, label)
    pyramid, pyramid_voxel_spacing = tc.make_pyramid(scale_z_axis=scale_z_axis, voxel_spacing=voxel_spacing)
    _ = tc.pyramid_to_omezarr(
        fs,
        pyramid,
        f"{output_prefix}.zarr",
        write_zarr,
        pyramid_voxel_spacing=pyramid_voxel_spacing,
    )
    _ = tc.pyramid_to_mrc(fs, pyramid, f"{output_prefix}.mrc", write_mrc, header_mapper, voxel_spacing)


def check_mask_for_label(
    fs: FileSystemApi,
    tomo_filename: str,
    label: int,
) -> bool:
    mc = MaskConverter(fs, tomo_filename, label)
    return mc.has_label()
