import os

import click as click
import mrcfile as mrcfile
import numpy as np


@click.group()
def cli():
    pass


@cli.command()
@click.argument("dest_path")
@click.option("--size", type=str, help="mrc file dimensions, defaults to (x=20,y=10,z=4).", default="4,10,20")
@click.option("--voxel-spacing", type=float, help="mrc voxel spacing, defaults to 5.", default=5)
def create_mrc(dest_path: str, size: str, voxel_spacing: float):
    # dest_path = "test_infra/test_files/input_bucket/10001_input/tomograms/TS_run1.rec"
    # size = (4,10,20)
    dir_path = os.path.dirname(dest_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with mrcfile.new(dest_path, overwrite=True) as mrc:
        mrc.set_data(np.random.randint(low=0, high=20, size=tuple(int(i) for i in size.split(",")), dtype=np.int8))
        mrc.voxel_size = voxel_spacing


if __name__ == "__main__":
    cli()
