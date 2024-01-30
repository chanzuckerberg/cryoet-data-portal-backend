import json
import os
import os.path
import re
from urllib import parse

import click

from common.config import DataImportConfig
from common.fs import FileSystemApi
from importers.annotation import AnnotationImporter
from importers.dataset import DatasetImporter
from importers.dataset_key_photo import DatasetKeyPhotoImporter
from importers.frames import FramesImporter
from importers.key_image import KeyImageImporter
from importers.neuroglancer import NeuroglancerImporter
from importers.run import RunImporter
from importers.tiltseries import RawTiltImporter, TiltSeriesImporter
from importers.tomogram import TomogramImporter


def format_ng_link(neuroglancer_data):
    encoded_data = parse.quote(json.dumps(neuroglancer_data, separators=(",", ":")), safe=":/#")
    final_link = f"https://neuroglancer-demo.appspot.com/#!{encoded_data}"
    return final_link


@click.group()
@click.pass_context
def cli(ctx):
    pass


@cli.command()
@click.option("--debug/--no-debug", is_flag=True, default=False)
@click.argument("dataset", required=True, type=str)
@click.argument("run", required=True, type=str)
@click.pass_context
def getlink(
    ctx,
    debug,
    dataset: str,
    run: str,
):
    fs = FileSystemApi.get_fs_api(mode="s3", force_overwrite=False)

    script_location = os.path.dirname(os.path.realpath(__file__))
    dataset_path = f"{dataset}"
    if int(dataset) >= 10013:
        dataset_path = f"gjensen/{dataset}"
    config_file = os.path.abspath(os.path.join(script_location, f"../dataset_configs/{dataset_path}.yaml"))
    config = DataImportConfig(fs, config_file, "cryoet-data-portal-staging", "cryoetportal-rawdatasets-dev")
    config.load_map_files()

    # Always iterate over datasets and runs.
    ds = DatasetImporter(config, None)
    for iter_run in RunImporter.find_runs(config, ds):
        if iter_run.run_name != run:
            if debug:
                print(f"Skipping {iter_run.run_name}..")
            continue
        if debug:
            print(f"Processing {iter_run.run_name}...")
        for tomo in TomogramImporter.find_tomograms(config, iter_run):
            iter_run.set_voxel_spacing(tomo.get_voxel_spacing())
            for item in NeuroglancerImporter.find_ng(config, tomo):
                ng_contents = item.get_config_json(item.parent.get_output_path() + ".zarr")
                print(format_ng_link(ng_contents))
                return
    print("run not found")


if __name__ == "__main__":
    cli()
