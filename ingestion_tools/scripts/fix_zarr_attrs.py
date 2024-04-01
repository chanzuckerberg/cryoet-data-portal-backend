import json
import os
from typing import Any

import click
import mrcfile

from common.fs import FileSystemApi


@click.group()
@click.pass_context
def cli(ctx):
    pass


def fix_zarr(fs: Any, zarr_path: str, scale_z=False):
    mrc_filename = zarr_path.replace(".zarr", ".mrc")
    mrc_file = fs.read_block(mrc_filename)
    with mrcfile.open(mrc_file, permissive=True, header_only=True) as mrc:
        z, y, x = (round(item, 3) for item in mrc.voxel_size.tolist())

    zattrs_filename = os.path.join(zarr_path, ".zattrs")
    with fs.open(zattrs_filename, "r") as fh:
        zarrdata = json.load(fh)

    for axis in zarrdata["multiscales"][0]["axes"]:
        axis["unit"] = "angstrom"

    for dataset in zarrdata["multiscales"][0]["datasets"]:
        scale = 2 ** int(dataset["path"])
        new_z = z
        new_x = round(scale * x, 3)
        new_y = round(scale * y, 3)
        if scale_z:
            new_z = round(scale * z, 3)
        dataset["coordinateTransformations"][0]["scale"] = [new_z, new_y, new_x]

    with fs.open(zattrs_filename, "w") as fh:
        fh.write(json.dumps(zarrdata, indent=4))
        print(f"wrote {zattrs_filename}")


@cli.command()
@click.argument("bucket", required=True, type=str)
@click.argument("dataset", required=True, type=str)
@click.argument("run", required=True, type=str)
@click.pass_context
def upgrade(
    ctx,
    bucket: str,
    dataset: str,
    run: str,
):
    fs_mode = "s3"
    fs = FileSystemApi.get_fs_api(mode=fs_mode, force_overwrite=False)

    # Find tiltseries
    for rundir in fs.glob(f"{bucket}/{dataset}/*/run_metadata.json"):
        run = rundir.split("/")[-2]
        for file in fs.glob(f"{bucket}/{dataset}/{run}/TiltSeries/*.zarr"):
            fix_zarr(fs, file, False)
        # Find tomograms
        for file in fs.glob(f"{bucket}/{dataset}/{run}/Tomograms/VoxelSpacing*/CanonicalTomogram/*.zarr"):
            fix_zarr(fs, file, True)
        # Find annotations
        for file in fs.glob(f"{bucket}/{dataset}/{run}/Tomograms/VoxelSpacing*/Annotations/*.zarr"):
            fix_zarr(fs, file, True)


if __name__ == "__main__":
    cli()
