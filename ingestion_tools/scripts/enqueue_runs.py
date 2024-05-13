import json
import os
import os.path
import re
import time

import boto3
import click
from boto3 import Session
from importers.dataset import DatasetImporter
from importers.run import RunImporter

from common.config import DepositionImportConfig
from common.fs import FileSystemApi


@click.group()
@click.pass_context
def cli(ctx):
    pass


def run_job(
    execution_name: str,
    config_file: str,
    input_bucket: str,
    output_path: str,
    flags: str,
    aws_region: str,
    aws_account_id: str,
    sfn_name: str,
    swipe_comms_bucket: str,
    swipe_wdl_bucket: str,
    swipe_wdl_key: str,
    ecr_repo: str,
    ecr_tag: str,
    memory: int | None = None,
):
    # TODO, pull these from the

    if not memory:
        memory = 24000

    state_machine_arn = f"arn:aws:states:{aws_region}:{aws_account_id}:stateMachine:{sfn_name}"

    execution_name = re.sub(r"[^0-9a-zA-Z-]", r"-", execution_name)
    sfn_input_json = {
        "Input": {
            "Run": {
                "aws_region": aws_region,
                "docker_image_id": f"{aws_account_id}.dkr.ecr.{aws_region}.amazonaws.com/{ecr_repo}:{ecr_tag}",
                "config_file": config_file,
                "input_bucket": input_bucket,
                "output_path": output_path,
                "flags": flags,
            },
        },
        "OutputPrefix": f"s3://{swipe_comms_bucket}/swipe/standardize-dirs-sfn/{execution_name}/results",
        "RUN_WDL_URI": f"s3://{swipe_wdl_bucket}/{swipe_wdl_key}",
        "RunEC2Memory": memory,
        "RunEC2Vcpu": 1,
        "RunSPOTMemory": memory,
        "RunSPOTVcpu": 1,
        "StateMachineArn": state_machine_arn,
    }

    session = Session(region_name=aws_region)
    client = session.client(
        service_name="stepfunctions",
    )

    return client.start_execution(
        stateMachineArn=state_machine_arn,
        name=execution_name,
        input=json.dumps(sfn_input_json),
    )


@cli.command()
@click.argument("config_file", required=True, type=str)
@click.argument("input_bucket", required=True, type=str)
@click.argument("output_path", required=True, type=str)
@click.option(
    "--env-name",
    type=str,
    required=True,
    default="staging",
    help="Specify environment, defaults to staging",
)
@click.option(
    "--ecr-repo",
    type=str,
    required=True,
    default="cryoet-staging",
    help="Specify ecr-repo name, defaults to 'cryoet-staging'",
)
@click.option(
    "--ecr-tag",
    type=str,
    required=True,
    default="ci-staging",
    help="Specify docker image tag, defaults to 'ci-staging'",
)
@click.option(
    "--swipe-wdl-key",
    type=str,
    required=True,
    default="standardize_dirs.wdl-v0.0.1.wdl",
    help="Specify wdl key for custom workload",
)
@click.option("--force-overwrite", is_flag=True, default=False, help="Overwrite of volumes if they it already exist")
@click.option("--import-tomograms", is_flag=True, default=False, help="Import tomogram volumes")
@click.option("--import-tomogram-metadata", is_flag=True, default=False, help="Import tomogram metadata")
@click.option("--import-annotations", is_flag=True, default=False, help="Import annotation files")
@click.option("--import-annotation-metadata", is_flag=True, default=False, help="Import annotation metadata")
@click.option("--import-metadata", is_flag=True, default=False, help="Import all metadata")
@click.option("--import-frames", is_flag=True, default=False, help="Import frame files")
@click.option("--import-tiltseries", is_flag=True, default=False, help="Import tiltseries volumes")
@click.option("--import-tiltseries-metadata", is_flag=True, default=False, help="Import tiltseries metadata")
@click.option("--import-run-metadata", is_flag=True, default=False, help="Import run metadata")
@click.option("--import-datasets", is_flag=True, default=False, help="Import dataset key photos")
@click.option("--import-dataset-metadata", is_flag=True, default=False, help="Import dataset metadata")
@click.option("--import-everything", is_flag=True, default=False, help="Import everything for the dataset")
@click.option(
    "--filter-run-name",
    type=str,
    default=None,
    multiple=True,
    help="Only process runs matching the regex. If not specified, all runs are processed",
)
@click.option(
    "--filter-dataset-name",
    type=str,
    default=None,
    multiple=True,
    help="Only process runs matching the regex. If not specified, all runs are processed",
)
@click.option(
    "--exclude-run-name",
    type=str,
    default=None,
    multiple=True,
    help="Exclude runs matching this regex. If not specified, all runs are processed",
)
@click.option(
    "--skip-until-run-name",
    type=str,
    default=None,
    multiple=False,
    help="Exclude runs matching this regex. If not specified, all runs are processed",
)
@click.option("--make-key-image", type=bool, is_flag=True, default=False, help="Create key image for run from tomogram")
@click.option(
    "--make-neuroglancer-config",
    type=bool,
    is_flag=True,
    default=False,
    help="Create neuroglancer config for run",
)
@click.option(
    "--write-mrc/--no-write-mrc",
    default=True,
    help="Specify if mrc volumes should be written, defaults to True.",
)
@click.option(
    "--write-zarr/--no-write-zarr",
    default=True,
    help="Specify if zarr volumes should be written, defaults to True.",
)
@click.option("--memory", type=int, default=None, help="Specify memory allocation override")
@click.pass_context
def queue(
    ctx,
    config_file: str,
    input_bucket: str,
    output_path: str,
    env_name: str,
    ecr_repo: str,
    ecr_tag: str,
    swipe_wdl_key: str,
    force_overwrite: bool,
    import_tomograms: bool,
    import_tomogram_metadata: bool,
    import_annotations: bool,
    import_annotation_metadata: bool,
    import_metadata: bool,
    import_frames: bool,
    import_tiltseries: bool,
    import_tiltseries_metadata: bool,
    import_run_metadata: bool,
    import_datasets: bool,
    import_dataset_metadata: bool,
    import_everything: bool,
    filter_run_name: list[str],
    filter_dataset_name: list[str],
    exclude_run_name: list[str],
    skip_until_run_name: str,
    make_key_image: bool,
    make_neuroglancer_config: bool,
    write_mrc: bool,
    write_zarr: bool,
    memory: int | None,
):
    fs_mode = "s3"
    fs = FileSystemApi.get_fs_api(mode=fs_mode, force_overwrite=force_overwrite)

    config = DepositionImportConfig(fs, config_file, output_path, input_bucket)
    os.makedirs(os.path.join(output_path, config.destination_prefix), exist_ok=True)
    config.load_map_files()

    exclude_run_name_patterns = [re.compile(pattern) for pattern in exclude_run_name]
    filter_run_name_patterns = [re.compile(pattern) for pattern in filter_run_name]
    filter_ds_name_patterns = [re.compile(pattern) for pattern in filter_dataset_name]

    bool_args = {
        "force-overwrite": force_overwrite,
        "import-tomograms": import_tomograms,
        "import-tomogram-metadata": import_tomogram_metadata,
        "import-annotations": import_annotations,
        "import-annotation-metadata": import_annotation_metadata,
        "import-metadata": import_metadata,
        "import-frames": import_frames,
        "import-tiltseries": import_tiltseries,
        "import-tiltseries-metadata": import_tiltseries_metadata,
        "import-run-metadata": import_run_metadata,
        "import-datasets": import_datasets,
        "import-dataset-metadata": import_dataset_metadata,
        "import-everything": import_everything,
        "make-key-image": make_key_image,
        "make-neuroglancer-config": make_neuroglancer_config,
        "no-write-mrc": not write_mrc,
        "no-write-zarr": not write_zarr,
    }
    args = [f"--{arg_name}" for arg_name, is_enabled in bool_args.items() if is_enabled]

    # Learn more about our AWS environment
    swipe_comms_bucket = None
    swipe_wdl_bucket = None
    sfn_name = f"cryoet-ingestion-{env_name}-default-wdl"

    sts = boto3.client("sts")
    aws_account_id = sts.get_caller_identity()["Account"]
    session = Session()
    aws_region = session.region_name
    s3_client = session.client("s3")
    buckets = s3_client.list_buckets()
    for bucket in buckets["Buckets"]:
        bucket_name = bucket["Name"]
        if "swipe-wdl" in bucket_name and env_name in bucket_name:
            swipe_wdl_bucket = bucket_name
        if "swipe-comms" in bucket_name and env_name in bucket_name:
            swipe_comms_bucket = bucket_name

    skip_run_until_regex = None
    skip_run = False
    if skip_until_run_name:
        skip_run = True
        skip_run_until_regex = re.compile(skip_until_run_name)

    # Always iterate over datasets and runs.
    if config.dataset_finder_config:
        datasets = config.dataset_finder_config.find(DatasetImporter, None, config, fs)
    else:
        # Maintain reverse compatibility
        datasets = [DatasetImporter(config, None, name=config.destination_prefix, path=config.source_prefix)]
    for dataset in datasets:
        if filter_dataset_name and not list(filter(lambda x: x.match(dataset.name), filter_ds_name_patterns)):
            print(f"Skipping dataset {dataset.name}..")
            continue
        if config.run_finder_config:
            runs = config.run_finder_config.find(RunImporter, dataset, config, fs)
        else:
            # Maintain reverse compatibility
            runs = RunImporter.find_runs(config, dataset)
        for run in runs:
            if skip_run and not skip_run_until_regex.match(run.run_name):
                print(f"Skipping {run.run_name}..")
                continue
            skip_run = False

            if list(filter(lambda x: x.match(run.name), exclude_run_name_patterns)):
                print(f"Excluding {run.name}..")
                continue
            if filter_run_name and not list(filter(lambda x: x.match(run.name), filter_run_name_patterns)):
                print(f"Skipping {run.name}..")
                continue
            print(f"Processing {run.name}...")
            new_args = list(args)  # make a copy
            new_args.append(f"--filter-dataset-name '^{dataset.name}$'")
            new_args.append(f"--filter-run-name '^{run.name}$'")
            dataset_id = dataset.name
            deposition_id = config.deposition_id
            execution_name = f"{int(time.time())}-dep{deposition_id}-ds{dataset_id}-run{run.name}"

            # execution name greater than 80 chars causes boto ValidationException
            if len(execution_name) > 80:
                execution_name = execution_name[-80:]

            run_job(
                execution_name,
                config_file,
                input_bucket,
                output_path,
                " ".join(new_args),
                aws_region=aws_region,
                aws_account_id=aws_account_id,
                sfn_name=sfn_name,
                swipe_comms_bucket=swipe_comms_bucket,
                swipe_wdl_bucket=swipe_wdl_bucket,
                swipe_wdl_key=swipe_wdl_key,
                ecr_repo=ecr_repo,
                ecr_tag=ecr_tag,
                memory=memory,
            )


if __name__ == "__main__":
    cli()
