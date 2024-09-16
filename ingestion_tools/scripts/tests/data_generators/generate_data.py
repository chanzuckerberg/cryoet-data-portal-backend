import click as click
import mrcfile as mrcfile
import numpy as np


@click.group()
def cli():
    pass


@cli.command()
@click.argument("dest_path")
@click.option("--size", type=str, help="mrc file dimensions, defaults to (10, 8, 6).", default="10,8,6")
def create_mrc(dest_path: str, size: str):
    # dest_path = "test_infra/test_files/input_bucket/10001_input/tomograms/TS_run1.rec"
    # size = (10, 8, 6)
    with mrcfile.new(dest_path, overwrite=True) as mrc:
        mrc.set_data(np.random.randint(low=0, high=20, size=tuple(size.split(",")), dtype=np.int8))


if __name__ == "__main__":
    cli()
