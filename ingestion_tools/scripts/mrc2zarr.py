import math

import click
import mrcfile
import zarr
from scipy.ndimage import zoom


@click.group()
@click.pass_context
def cli(ctx):
    pass


@cli.command()
@click.argument("mrcfilename", required=True, type=str)  # TODO - use click types
@click.argument("zarrdir", required=True, type=str)  # TODO - use click types
@click.pass_context
def convert(ctx, mrcfilename: str, zarrdir: str):
    with mrcfile.open(mrcfilename) as mrc:
        if not mrc.header:
            raise Exception("missing mrc header")

        # Header columns: https://bio3d.colorado.edu/imod/doc/mrc_format.txt
        (xsize, ysize, zsize, mode) = (
            mrc.header.nx,
            mrc.header.ny,
            mrc.header.nz,
            mrc.header.mode,
        )
        # 32 bit floats
        dtype = "f4"
        if mode == 1:
            # 16 bit signed ints
            dtype = "i2"

        store = zarr.DirectoryStore(zarrdir)
        root_group = zarr.group(store, overwrite=True)
        original_size = root_group.create_dataset(
            "full_size",
            shape=(zsize, ysize, xsize),
            chunks=(64, 64, 64),
            dtype=dtype,
        )
        original_size[::] = mrc.data

        # Constrain the width of our image to 256px
        scale_factor = 256 / xsize
        preview_data = zoom(mrc.data, scale_factor, mode="nearest")
        preview_size = root_group.create_dataset(
            "preview",
            shape=preview_data.shape,
            chunks=(64, 64, 64),
            dtype=dtype,
        )
        preview_size[::] = preview_data


if __name__ == "__main__":
    cli()
