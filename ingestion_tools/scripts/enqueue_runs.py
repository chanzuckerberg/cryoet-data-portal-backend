import json
import re
import time

import boto3
import click
from boto3 import Session
from importers.dataset import DatasetImporter
from importers.run import RunImporter
from standardize_dirs import IMPORTERS, common_options

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


def get_aws_env(env_name):
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
    aws_env = {
        "aws_region": aws_region,
        "aws_account_id": aws_account_id,
        "sfn_name": sfn_name,
        "swipe_comms_bucket": swipe_comms_bucket,
        "swipe_wdl_bucket": swipe_wdl_bucket,
    }
    return aws_env


def to_args(**kwargs) -> list[str]:
    args = []
    for k, v in kwargs.items():
        if not v:
            continue
        if isinstance(v, bool):
            args.append(f"--{k.replace('_', '-')}")
        elif isinstance(v, tuple):
            for item in v:
                args.append(f"--{k.replace('_', '-')}")
                args.append(str(item))
        else:
            args.append(f"--{k.replace('_', '-')}")
            args.append(str(v))
    return args


@cli.command()
@click.argument("config_file", required=True, type=str)
@click.argument("input_bucket", required=True, type=str)
@click.argument("output_path", required=True, type=str)
@click.option("--import-everything", is_flag=True, default=False)
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
@click.option("--force-overwrite", is_flag=True, default=False)
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
    default="main",
    help="Specify docker image tag, defaults to 'main'",
)
@click.option(
    "--swipe-wdl-key",
    type=str,
    required=True,
    default="standardize_dirs.wdl-v0.0.1.wdl",
    help="Specify wdl key for custom workload",
)
@click.option("--memory", type=int, default=None, help="Specify memory allocation override")
@click.option(
    "--skip-until-run-name",
    type=str,
    default=None,
    multiple=False,
    help="Exclude runs matching this regex. If not specified, all runs are processed",
)
@common_options
@click.pass_context
def queue(
    ctx,
    config_file: str,
    input_bucket: str,
    output_path: str,
    import_everything: bool,
    write_mrc: bool,
    write_zarr: bool,
    force_overwrite: bool,
    env_name: str,
    ecr_repo: str,
    ecr_tag: str,
    swipe_wdl_key: str,
    memory: int | None,
    skip_until_run_name: str,
    **kwargs,
):
    fs_mode = "s3"
    fs = FileSystemApi.get_fs_api(mode=fs_mode, force_overwrite=force_overwrite)

    config = DepositionImportConfig(fs, config_file, output_path, input_bucket, IMPORTERS)
    config.write_mrc = write_mrc
    config.write_zarr = write_zarr
    config.load_map_files()

    skip_run_until_regex = None
    skip_run = False
    if skip_until_run_name:
        skip_run = True
        skip_run_until_regex = re.compile(skip_until_run_name)

    aws_env = get_aws_env(env_name)

    filter_runs = [re.compile(pattern) for pattern in kwargs.get("filter_run_name", [])]
    exclude_runs = [re.compile(pattern) for pattern in kwargs.get("exclude_run_name", [])]
    filter_datasets = [re.compile(pattern) for pattern in kwargs.get("filter_dataset_name", [])]
    exclude_datasets = [re.compile(pattern) for pattern in kwargs.get("exclude_dataset_name", [])]

    # Always iterate over datasets and runs.
    datasets = DatasetImporter.finder(config)
    for dataset in datasets:
        if list(filter(lambda x: x.match(dataset.name), exclude_datasets)):
            print(f"Excluding {dataset.name}..")
            continue
        if filter_datasets and not list(filter(lambda x: x.match(dataset.name), filter_datasets)):
            print(f"Skipping {dataset.name}..")
            continue
        runs = RunImporter.finder(config, dataset=dataset)
        for run in runs:
            if skip_run and not skip_run_until_regex.match(run.name):
                print(f"Skipping {run.name}..")
                continue
            skip_run = False

            if list(filter(lambda x: x.match(run.name), exclude_runs)):
                print(f"Excluding {run.name}..")
                continue
            if filter_runs and not list(filter(lambda x: x.match(run.name), filter_runs)):
                print(f"Skipping {run.name}..")
                continue
            print(f"Processing {run.name}...")

            per_run_args = {}
            # Don't copy over dataset and run name filters to the queued jobs - they're intended to be batched into 1-run chunks.
            excluded_args = ["filter_dataset_name", "filter_run_name"]
            for k, v in kwargs.items():
                if any(substring in k for substring in excluded_args):
                    break
                per_run_args[k] = v
            new_args = to_args(
                import_everything=import_everything,
                write_mrc=write_mrc,
                write_zarr=write_zarr,
                force_overwrite=force_overwrite,
                **per_run_args,
            )  # make a copy
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
                aws_region=aws_env["aws_region"],
                aws_account_id=aws_env["aws_account_id"],
                sfn_name=aws_env["sfn_name"],
                swipe_comms_bucket=aws_env["swipe_comms_bucket"],
                swipe_wdl_bucket=aws_env["swipe_wdl_bucket"],
                swipe_wdl_key=swipe_wdl_key,
                ecr_repo=ecr_repo,
                ecr_tag=ecr_tag,
                memory=memory,
            )


if __name__ == "__main__":
    cli()
