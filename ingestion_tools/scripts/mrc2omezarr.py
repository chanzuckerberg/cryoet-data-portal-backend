from typing import List

import click
import mrcfile
import numpy as np
import ome_zarr
import ome_zarr.io
import ome_zarr.writer
import zarr
from skimage.transform import downscale_local_mean


@click.group()
@click.pass_context
def cli(ctx):
    pass


# Make an array of an original size image, plus `max_layers` half-scaled images
def make_pyramid(base: np.ndarray, max_layers: int = 2) -> List[np.ndarray]:
    rv = [base]
    for i in range(max_layers):
        rv.append(downscale_local_mean(rv[i], (2, 2, 2)))
    return rv


@cli.command()
@click.argument("mrcfilename", required=True, type=str)  # TODO - use click types
@click.argument("zarrdir", required=True, type=str)  # TODO - use click types
@click.pass_context
def convert(ctx, mrcfilename: str, zarrdir: str):
    with mrcfile.open(mrcfilename) as mrc:
        if mrc.data is None:
            raise Exception("missing mrc data")

        # Convert our input type to 32bit floats, which is our standard output format.
        # Then make a pyramid of 100/50/25 percent scale volumes
        mip = make_pyramid(mrc.data.astype("f4"))

        loc = ome_zarr.io.parse_url(zarrdir, mode="w")
        root_group = zarr.group(loc.store, overwrite=True)

        # Write zarr data as 256^3 voxel chunks
        ome_zarr.writer.write_multiscale(
            mip,
            group=root_group,
            axes="zyx",
            storage_options=dict(chunks=(256, 256, 256)),
        )


if __name__ == "__main__":
    cli()
