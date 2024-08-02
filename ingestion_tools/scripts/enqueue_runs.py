import json
import logging
import os
import re
import time
from concurrent.futures import ProcessPoolExecutor, wait
from functools import partial
from typing import Any

import boto3
import click
from boto3 import Session
from botocore import UNSIGNED
from botocore.config import Config
from db_import import db_import_options
from importers.dataset import DatasetImporter
from importers.db.base_importer import DBImportConfig
from importers.db.dataset import DatasetDBImporter
from importers.deposition import DepositionImporter
from importers.run import RunImporter
from standardize_dirs import IMPORTERS
from standardize_dirs import common_options as ingest_common_options

from common.config import DepositionImportConfig
from common.fs import FileSystemApi

logger = logging.getLogger("db_import")
logging.basicConfig(level=logging.INFO)


def enqueue_common_options(func):
    options = []
    options.append(
        click.option(
            "--environment",
            type=str,
            required=True,
            default="staging",
            help="Specify environment, defaults to staging",
        ),
    )
    options.append(
        click.option(
            "--ecr-repo",
            type=str,
            required=True,
            default="cryoet-staging",
            help="Specify ecr-repo name, defaults to 'cryoet-staging'",
        ),
    )
    options.append(
        click.option(
            "--ecr-tag",
            type=str,
            required=True,
            default="main",
            help="Specify docker image tag, defaults to 'main'",
        ),
    )
    options.append(click.option("--memory", type=int, default=None, help="Specify memory allocation override"))
    options.append(click.option("--parallelism", required=True, type=int, default=20))
    for option in options:
        func = option(func)
    return func


def create_execution_machine_log_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
        logger.warning("Removing existing %s file.", filename)

    os.makedirs(os.path.dirname(filename), exist_ok=True)


def handle_common_options(ctx, kwargs):
    ctx.obj = {
        "environment": kwargs["environment"],
        "ecr_repo": kwargs["ecr_repo"],
        "ecr_tag": kwargs["ecr_tag"],
        "memory": kwargs["memory"],
        "parallelism": kwargs["parallelism"],
        **get_aws_env(kwargs["environment"]),
    }
    enqueue_common_keys = ["environment", "ecr_repo", "ecr_tag", "memory", "parallelism"]
    # Make sure to remove these common options from the list of args processed by commands.
    for opt in enqueue_common_keys:
        del kwargs[opt]


@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = {}


def run_job(
    execution_name: str,
    wdl_args: dict[str, Any],
    aws_region: str,
    aws_account_id: str,
    sfn_name: str,
    swipe_comms_bucket: str,
    swipe_wdl_bucket: str,
    swipe_wdl_key: str,
    ecr_repo: str,
    ecr_tag: str,
    memory: int | None = None,
    execution_machine_log: str | None = None,
    **kwargs,  # Ignore any the extra vars this method doesn't need.
):
    if not memory:
        memory = 24000

    state_machine_arn = f"arn:aws:states:{aws_region}:{aws_account_id}:stateMachine:{sfn_name}"

    execution_name = re.sub(r"[^0-9a-zA-Z-]", r"-", execution_name)
    sfn_input_json = {
        "Input": {
            "Run": {
                "aws_region": aws_region,
                "docker_image_id": f"908710317728.dkr.ecr.{aws_region}.amazonaws.com/{ecr_repo}:{ecr_tag}",
                **wdl_args,
            },
        },
        "OutputPrefix": f"s3://{swipe_comms_bucket}/swipe/swipe-job-output/{execution_name}/results",
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

    execution = client.start_execution(
        stateMachineArn=state_machine_arn,
        name=execution_name,
        input=json.dumps(sfn_input_json),
    )

    if execution_machine_log is not None:
        with open(execution_machine_log, "a") as f:
            f.write(execution["executionArn"] + "\n")

    return execution


def get_aws_env(environment):
    # Learn more about our AWS environment
    swipe_comms_bucket = None
    swipe_wdl_bucket = None
    sfn_name = f"cryoet-ingestion-{environment}-default-wdl"

    sts = boto3.client("sts")
    aws_account_id = sts.get_caller_identity()["Account"]
    session = Session()
    aws_region = session.region_name
    s3_client = session.client("s3")
    buckets = s3_client.list_buckets()
    for bucket in buckets["Buckets"]:
        bucket_name = bucket["Name"]
        if "swipe-wdl" in bucket_name and environment in bucket_name:
            swipe_wdl_bucket = bucket_name
        if "swipe-comms" in bucket_name and environment in bucket_name:
            swipe_comms_bucket = bucket_name
    aws_env = {
        "aws_region": aws_region,
        "aws_account_id": aws_account_id,
        "sfn_name": sfn_name,
        "swipe_comms_bucket": swipe_comms_bucket,
        "swipe_wdl_bucket": swipe_wdl_bucket,
    }
    return aws_env


def get_datasets(
    s3_bucket,
    https_prefix,
    filter_datasets,
    include_dataset,
    exclude_dataset,
    s3_prefix,
    anonymous: bool,
):
    filter_datasets = [re.compile(pattern) for pattern in filter_datasets]
    exclude_datasets = [re.compile(pattern) for pattern in exclude_dataset]
    s3_config = Config(signature_version=UNSIGNED) if anonymous else None
    s3_client = boto3.client("s3", config=s3_config)
    config = DBImportConfig(s3_client, s3_bucket, https_prefix)

    datasets_to_check = []
    if include_dataset:
        for ds in include_dataset:
            datasets_to_check.extend(DatasetDBImporter.get_items(config, ds))
    else:
        datasets_to_check = DatasetDBImporter.get_items(config, s3_prefix)

    for dataset in datasets_to_check:
        dataset_id = dataset.dir_prefix.strip("/")
        if filter_datasets and not list(filter(lambda x: x.match(dataset_id), filter_datasets)):
            logger.info("Skipping %s...", dataset.dir_prefix)
            continue
        if exclude_dataset and list(filter(lambda x: x.match(dataset_id), exclude_datasets)):
            logger.info("Excluding %s...", dataset.dir_prefix)
            continue
        yield dataset_id, dataset


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


@cli.command(name="db-import")
@click.option("--s3-bucket", required=False, type=str, help="S3 bucket to read from")
@click.option("--https-prefix", required=False, type=str, help="protocol + domain for where to fetch files via HTTP")
@click.option("--s3-prefix", required=True, default="", type=str)
@click.option(
    "--debug/--no-debug",
    is_flag=True,
    required=True,
    default=True,
    type=bool,
    help="Print DB Queries",
)
@click.option("--filter-datasets", type=str, default=None, multiple=True)
@click.option("--include-dataset", type=str, default=None, multiple=True)
@click.option("--exclude-dataset", type=str, default=None, multiple=True)
@click.option(
    "--swipe-wdl-key",
    type=str,
    required=True,
    default="db_import-v0.0.1.wdl",
    help="Specify wdl key for custom workload",
)
@click.option(
    "--execution-machine-log",
    type=str,
    default=None,
    help="Log execution machine ARNs to this file",
)
@db_import_options
@enqueue_common_options
@click.pass_context
def db_import(
    ctx,
    s3_bucket: str | None,
    https_prefix: str | None,
    s3_prefix: str,
    debug: bool,
    filter_datasets: list[str],
    include_dataset: list[str],
    exclude_dataset: list[str],
    swipe_wdl_key: str,
    execution_machine_log: str,
    **kwargs,
):
    handle_common_options(ctx, kwargs)
    # Import data from S3 into the DB.

    # Set per-env defaults if values weren't provided.
    env = ctx.obj["environment"]
    if not s3_bucket:
        s3_bucket = "cryoet-data-portal-staging"
        if env == "prod":
            s3_bucket = "cryoet-data-portal-public"
    if not https_prefix:
        https_prefix = "https://files.cryoet.staging.si.czi.technology"
        if env == "prod":
            https_prefix = "https://files.cryoetdataportal.cziscience.com"

    # Default to using a lot less memory than the ingestion job.
    if not ctx.obj.get("memory"):
        ctx.obj["memory"] = 4000

    if execution_machine_log is not None:
        create_execution_machine_log_file(execution_machine_log)

    futures = []
    with ProcessPoolExecutor(max_workers=ctx.obj["parallelism"]) as workerpool:
        for dataset_id, _ in get_datasets(
            s3_bucket,
            https_prefix,
            filter_datasets,
            include_dataset,
            exclude_dataset,
            s3_prefix,
            kwargs.get("anonymous"),
        ):
            print(f"Processing dataset {dataset_id}...")

            new_args = to_args(**kwargs)
            new_args.append(f"--s3-prefix {dataset_id}")
            if debug:
                new_args.append("--debug")

            execution_name = f"{int(time.time())}-dbimport-{dataset_id}"

            # execution name greater than 80 chars causes boto ValidationException
            if len(execution_name) > 80:
                execution_name = execution_name[-80:]

            wdl_args = {
                "s3_bucket": s3_bucket,
                "https_prefix": https_prefix,
                "flags": " ".join(new_args),
                "environment": ctx.obj["environment"],
            }
            futures.append(
                workerpool.submit(
                    partial(
                        run_job,
                        execution_name,
                        wdl_args,
                        swipe_wdl_key=swipe_wdl_key,
                        execution_machine_log=execution_machine_log,
                        **ctx.obj,
                    ),
                ),
            )
        wait(futures)


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
    "--swipe-wdl-key",
    type=str,
    required=True,
    default="standardize_dirs.wdl-v0.0.1.wdl",
    help="Specify wdl key for custom workload",
)
@click.option(
    "--skip-until-run-name",
    type=str,
    default=None,
    multiple=False,
    help="Exclude runs matching this regex. If not specified, all runs are processed",
)
@click.option(
    "--execution-machine-log",
    type=str,
    default=None,
    help="Log execution machine ARNs to this file",
)
@ingest_common_options
@enqueue_common_options
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
    swipe_wdl_key: str,
    skip_until_run_name: str,
    execution_machine_log: str,
    **kwargs,
):
    handle_common_options(ctx, kwargs)
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

    filter_runs = [re.compile(pattern) for pattern in kwargs.get("filter_run_name", [])]
    exclude_runs = [re.compile(pattern) for pattern in kwargs.get("exclude_run_name", [])]
    filter_datasets = [re.compile(pattern) for pattern in kwargs.get("filter_dataset_name", [])]
    exclude_datasets = [re.compile(pattern) for pattern in kwargs.get("exclude_dataset_name", [])]

    if execution_machine_log is not None:
        create_execution_machine_log_file(execution_machine_log)

    # Always iterate over depostions, datasets and runs.
    for deposition in DepositionImporter.finder(config):
        print(f"Processing deposition: {deposition.name}")
        datasets = DatasetImporter.finder(config, deposition=deposition)
        for dataset in datasets:
            if list(filter(lambda x: x.match(dataset.name), exclude_datasets)):
                print(f"Excluding {dataset.name}..")
                continue
            if filter_datasets and not list(filter(lambda x: x.match(dataset.name), filter_datasets)):
                print(f"Skipping {dataset.name}..")
                continue
            print(f"Processing dataset: {dataset.name}")
            runs = RunImporter.finder(config, dataset=dataset)
            futures = []
            with ProcessPoolExecutor(max_workers=ctx.obj["parallelism"]) as workerpool:
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
                    # Don't copy over dataset and run name filters to the queued jobs - they're intended to be
                    # batched into 1-run chunks.
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
                    deposition_id = deposition.name
                    execution_name = f"{int(time.time())}-dep{deposition_id}-ds{dataset_id}-run{run.name}"

                    # execution name greater than 80 chars causes boto ValidationException
                    if len(execution_name) > 80:
                        execution_name = execution_name[-80:]

                    wdl_args = {
                        "config_file": config_file,
                        "input_bucket": input_bucket,
                        "output_path": output_path,
                        "flags": " ".join(new_args),
                    }
                    futures.append(
                        workerpool.submit(
                            partial(
                                run_job,
                                execution_name,
                                wdl_args,
                                swipe_wdl_key=swipe_wdl_key,
                                execution_machine_log=execution_machine_log,
                                **ctx.obj,
                            ),
                        ),
                    )
                wait(futures)


class OrderedSyncFilters(click.Command):
    _options = []

    def parse_args(self, ctx, args):
        parser = self.make_parser(ctx)
        opts, _, param_order = parser.parse_args(args=list(args))
        for param in param_order:
            if param.name not in ["include", "exclude"]:
                continue
            type(self)._options.append((param, opts[param.name].pop(0)))

        return super().parse_args(ctx, args)


@cli.command(name="sync", cls=OrderedSyncFilters)
@click.option("--input-bucket", required=True, type=str, default="cryoet-data-portal-staging")
@click.option("--output-bucket", required=True, type=str, default="cryoet-data-portal-public")
@click.option("--include", type=str, default=None, multiple=True, help="--include option to send to `aws s3 sync`")
@click.option("--exclude", type=str, default=None, multiple=True, help="--exclude option to send to `aws s3 sync`")
@click.option("--delete-files", is_flag=True, default=False)
@click.option("--dryrun", is_flag=True, default=False)
@click.option("--s3-prefix", required=True, default="", type=str)
@click.option("--filter-datasets", type=str, default=None, multiple=True)
@click.option("--include-dataset", type=str, default=None, multiple=True)
@click.option("--exclude-dataset", type=str, default=None, multiple=True)
@click.option(
    "--swipe-wdl-key",
    type=str,
    required=True,
    default="sync-v0.0.1.wdl",
    help="Specify wdl key for custom workload",
)
@click.option(
    "--execution-machine-log",
    type=str,
    default=None,
    help="Log execution machine ARNs to this file",
)
@enqueue_common_options
@click.pass_context
def sync(
    ctx,
    input_bucket: str,
    output_bucket: str,
    delete_files: bool,
    dryrun: bool,
    s3_prefix: str | None,
    filter_datasets: list[str],
    include_dataset: list[str],
    exclude_dataset: list[str],
    swipe_wdl_key: str,
    execution_machine_log: str,
    **kwargs,
):
    handle_common_options(ctx, kwargs)
    # Sync data from staging to prod s3 bucket

    # Default to using a lot less memory than the ingestion job.
    if not ctx.obj.get("memory"):
        ctx.obj["memory"] = 4000

    new_args = []
    if delete_files:
        new_args.append("--delete")
    if dryrun:
        new_args.append("--dryrun")

    for param, value in OrderedSyncFilters._options:
        new_args.append(f"--{param.name} '{value}'")

    if execution_machine_log is not None:
        create_execution_machine_log_file(execution_machine_log)

    futures = []
    with ProcessPoolExecutor(max_workers=ctx.obj["parallelism"]) as workerpool:
        for dataset_id, _ in get_datasets(
            input_bucket,
            "",
            filter_datasets,
            include_dataset,
            exclude_dataset,
            s3_prefix,
            False,
        ):
            print(f"Processing dataset {dataset_id}...")

            execution_name = f"{int(time.time())}-sync-{dataset_id}"

            # execution name greater than 80 chars causes boto ValidationException
            if len(execution_name) > 80:
                execution_name = execution_name[-80:]

            wdl_args = {
                "input_bucket": input_bucket,
                "input_path": dataset_id,
                "output_bucket": output_bucket,
                "output_path": dataset_id,
                "flags": " ".join(new_args),
            }
            futures.append(
                workerpool.submit(
                    partial(
                        run_job,
                        execution_name,
                        wdl_args,
                        swipe_wdl_key=swipe_wdl_key,
                        execution_machine_log=execution_machine_log,
                        **ctx.obj,
                    ),
                ),
            )
        wait(futures)


if __name__ == "__main__":
    cli()
