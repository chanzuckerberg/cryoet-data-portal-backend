import json
import os
import os.path
from datetime import datetime
from typing import Any, Callable, List

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
        loc = ome_zarr.io.ZarrLocation(f"s3://{self.zarrdir}")
        data = loc.load("0")
        return data


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

    # Make an array of an original size image, plus `max_layers` half-scaled images
    def make_pyramid(self, max_layers: int = 2, scale_z_axis: bool = True) -> List[np.ndarray]:
        pyramid = [self.data.astype("f4")]
        # Then make a pyramid of 100/50/25 percent scale volumes
        for i in range(max_layers):
            z_scale = 1
            if scale_z_axis:
                z_scale = 2
            downscaled_data = downscale_local_mean(pyramid[i], (z_scale, 2, 2))
            pyramid.append(downscaled_data)
        return pyramid

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
    ) -> str:
        destination_zarrdir = fs.destformat(zarrdir)

        # Write zarr data as 256^3 voxel chunks
        if write:
            loc = ome_zarr.io.parse_url(destination_zarrdir, mode="w")
            root_group = zarr.group(loc.store, overwrite=True)
            ome_zarr.writer.write_multiscale(
                pyramid,
                group=root_group,
                axes="zyx",
                storage_options=dict(chunks=(256, 256, 256), overwrite=True),
            )
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
    def __init__(self, fs: FileSystemApi, mrc_filename: str, label: int = 1):
        super().__init__(fs, mrc_filename)
        self.label = label

    def make_pyramid(self, max_layers: int = 2, scale_z_axis: bool = True) -> List[np.ndarray]:
        pyramid = [(self.data == self.label).astype(np.float32)]
        # Then make a pyramid of 100/50/25 percent scale volumes
        for i in range(max_layers):
            z_scale = 1
            if scale_z_axis:
                z_scale = 2

            # For semantic segmentation masks we want to have a binary output.
            # downscale_local_mean will return float array even for bool input with non-binary values
            scaled = (downscale_local_mean(pyramid[i] == 1, (z_scale, 2, 2)) > 0).astype(np.int8)
            pyramid.append(scaled)

        return pyramid

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


def scale_mrcfile(
    fs: FileSystemApi,
    output_prefix: str,
    tomo_filename: str,
    scale_z_axis: bool = True,
    write_mrc: bool = True,
    write_zarr: bool = True,
    header_mapper: Callable[[np.array], None] = None,
    voxel_spacing=None,
):
    tc = TomoConverter(fs, tomo_filename)
    pyramid = tc.make_pyramid(scale_z_axis=scale_z_axis)
    _ = tc.pyramid_to_omezarr(fs, pyramid, f"{output_prefix}.zarr", write_zarr)
    _ = tc.pyramid_to_mrc(fs, pyramid, f"{output_prefix}.mrc", write_mrc, header_mapper, voxel_spacing)


def scale_maskfile(
    fs: FileSystemApi,
    output_prefix: str,
    tomo_filename: str,
    label: int,
    scale_z_axis: bool = True,
    write: bool = True,
    voxel_spacing=None,
):
    mc = MaskConverter(fs, tomo_filename, label)
    pyramid = mc.make_pyramid(scale_z_axis=scale_z_axis)
    _ = mc.pyramid_to_omezarr(fs, pyramid, f"{output_prefix}.zarr", write)
    _ = mc.pyramid_to_mrc(
        fs,
        pyramid,
        f"{output_prefix}.mrc",
        write,
        voxel_spacing=voxel_spacing,
    )


def check_mask_for_label(
    fs: FileSystemApi,
    tomo_filename: str,
    label: int,
) -> bool:
    mc = MaskConverter(fs, tomo_filename, label)
    return mc.has_label()
