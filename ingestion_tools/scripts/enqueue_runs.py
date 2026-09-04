import json
import logging
import os.path
import re
import shlex
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial
from typing import Any

import boto3
import click
from boto3 import Session
from botocore import UNSIGNED
from botocore.config import Config
from db_import.common.config import DBImportConfig
from db_import.importer import db_import_options
from db_import.importers.dataset import DatasetDBImporter
from db_import.importers.deposition import DepositionDBImporter
from importers.dataset import DatasetImporter
from importers.deposition import DepositionImporter
from importers.run import RunImporter
from importers.utils import IMPORTERS
from standardize_dirs import common_options as ingest_common_options

from common.config import PROD_URL, STAGING_URL, DepositionImportConfig
from common.fs import FileSystemApi

logger = logging.getLogger("db_import")
logging.basicConfig(level=logging.INFO)


def environment_option(func):
    """Kept out of `enqueue_common_options` because `sync` has no environment to select: it
    always runs on the staging deployment, and always syncs staging -> public.

    Apply it *below* `enqueue_common_options` so it is evaluated first and `--environment`
    keeps its position in `--help`.
    """
    return click.option(
        "--environment",
        type=str,
        required=True,
        default="staging",
        help="Specify environment, defaults to staging",
    )(func)


def enqueue_common_options(func):
    options = []
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
    options.append(
        click.option(
            "--vcpu",
            type=int,
            default=None,
            help="Specify vCPU allocation override. Jobs default to 1 vCPU; `sync` defaults to 4 "
            "because `aws s3 sync` is bottlenecked on request concurrency, not bandwidth.",
        ),
    )
    options.append(click.option("--parallelism", required=True, type=int, default=20))
    for option in options:
        func = option(func)
    return func


def handle_common_options(ctx, kwargs):
    ctx.obj = {
        "environment": kwargs["environment"],
        "ecr_repo": kwargs["ecr_repo"],
        "ecr_tag": kwargs["ecr_tag"],
        "memory": kwargs["memory"],
        "vcpu": kwargs["vcpu"],
        "parallelism": kwargs["parallelism"],
        **get_aws_env(kwargs["environment"]),
    }
    enqueue_common_keys = ["environment", "ecr_repo", "ecr_tag", "memory", "vcpu", "parallelism"]
    # Make sure to remove these common options from the list of args processed by commands.
    for opt in enqueue_common_keys:
        del kwargs[opt]


@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = {}


def wait_for_futures(futures, on_success=None):
    """Wait for all submitted jobs, re-raising any errors instead of swallowing them.

    `futures` may be a mapping of future -> label, in which case `on_success` is called with
    the label of each submission that actually succeeded -- so nothing is announced before
    the submission it describes has resolved.
    """
    errors = 0
    for future in as_completed(futures):
        try:
            future.result()
        except Exception:
            errors += 1
            logger.exception("Failed to submit job")
            continue
        if on_success:
            on_success(futures[future])
    if errors:
        raise RuntimeError(f"{errors} of {len(futures)} job submissions failed; see logs above.")


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
    vcpu: int | None = None,
    **kwargs,  # Ignore any the extra vars this method doesn't need.
):
    if not memory:
        memory = 24000
    if not vcpu:
        vcpu = 1

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
        "RunEC2Vcpu": vcpu,
        "RunSPOTMemory": memory,
        "RunSPOTVcpu": vcpu,
        "StateMachineArn": state_machine_arn,
    }

    session = Session(region_name=aws_region)
    client = session.client(service_name="stepfunctions")
    return client.start_execution(
        stateMachineArn=state_machine_arn,
        name=execution_name,
        input=json.dumps(sfn_input_json),
    )


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
    # Fail fast on missing infra, usually a wrong AWS_PROFILE for the environment.
    missing_buckets = [
        name
        for name, value in (("swipe-comms", swipe_comms_bucket), ("swipe-wdl", swipe_wdl_bucket))
        if value is None
    ]
    if missing_buckets:
        raise RuntimeError(
            f"Could not find {', '.join(missing_buckets)} bucket(s) for environment "
            f"'{environment}' in AWS account {aws_account_id}. Are you using the right "
            f"AWS_PROFILE for this environment?",
        )

    state_machine_arn = f"arn:aws:states:{aws_region}:{aws_account_id}:stateMachine:{sfn_name}"
    try:
        boto3.client("stepfunctions").describe_state_machine(stateMachineArn=state_machine_arn)
    except Exception as err:
        raise RuntimeError(
            f"State machine '{sfn_name}' not found in AWS account {aws_account_id} "
            f"(region {aws_region}). Are you using the right AWS_PROFILE for environment "
            f"'{environment}'?",
        ) from err

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
    config = DBImportConfig(s3_client, None, s3_bucket, https_prefix, None)

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


def get_depositions(s3_bucket, include_depositions, anonymous: bool):
    s3_config = Config(signature_version=UNSIGNED) if anonymous else None
    s3_client = boto3.client("s3", config=s3_config)
    config = DBImportConfig(s3_client, None, s3_bucket, "", None)
    for dep in include_depositions:
        for deposition in DepositionDBImporter.get_items(config, dep):
            deposition_id = os.path.basename(deposition.dir_prefix.strip("/"))
            yield deposition_id, deposition


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
    default="db_import-v0.0.3.wdl",
    help="Specify wdl key for custom workload",
)
@db_import_options
@enqueue_common_options
@environment_option
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
        https_prefix = STAGING_URL
        if env == "prod":
            https_prefix = PROD_URL

    # Default to using a lot less memory than the ingestion job.
    if not ctx.obj.get("memory"):
        ctx.obj["memory"] = 4000

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
            scrape_args = ["--import-dataset", f"{dataset_id}"]
            for idx, arg in enumerate(new_args):
                if arg == "--deposition-id":
                    scrape_args.append("--import-deposition")
                    scrape_args.append(new_args[idx + 1])

            execution_name = f"{int(time.time())}-dbimport-{dataset_id}"

            # execution name greater than 80 chars causes boto ValidationException
            if len(execution_name) > 80:
                execution_name = execution_name[-80:]

            aws_region = ctx.obj["aws_region"]
            ecr_tag = ctx.obj["ecr_tag"]
            wdl_args = {
                "s3_bucket": s3_bucket,
                "https_prefix": https_prefix,
                "flags": " ".join(new_args),
                "environment": ctx.obj["environment"],
                "v2_docker_image_id": f"908710317728.dkr.ecr.{aws_region}.amazonaws.com/apiv2-x86:{ecr_tag}",
            }
            futures.append(
                workerpool.submit(
                    partial(
                        run_job,
                        execution_name,
                        wdl_args,
                        swipe_wdl_key=swipe_wdl_key,
                        **ctx.obj,
                    ),
                ),
            )
        wait_for_futures(futures)


@cli.command()
@click.argument("config_file", required=True, type=str)
@click.argument("input_bucket", required=True, type=str)
@click.argument("output_path", required=True, type=str)
@click.option("--https-prefix", required=False, type=str, help="protocol + domain for where to fetch files via HTTP")
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
@ingest_common_options
@enqueue_common_options
@environment_option
@click.pass_context
def queue(
    ctx,
    config_file: str,
    input_bucket: str,
    output_path: str,
    https_prefix: str,
    import_everything: bool,
    import_all_metadata: bool,
    write_mrc: bool,
    write_zarr: bool,
    force_overwrite: bool,
    swipe_wdl_key: str,
    skip_until_run_name: str,
    **kwargs,
):
    handle_common_options(ctx, kwargs)
    fs_mode = "s3"
    fs = FileSystemApi.get_fs_api(mode=fs_mode, force_overwrite=force_overwrite)

    if not https_prefix:
        https_prefix = PROD_URL
    config = DepositionImportConfig(fs, config_file, output_path, input_bucket, IMPORTERS, https_prefix=https_prefix)
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
                            continue
                        per_run_args[k] = v
                    new_args = to_args(
                        https_prefix=https_prefix,
                        import_everything=import_everything,
                        import_all_metadata=import_all_metadata,
                        write_mrc=write_mrc,
                        write_zarr=write_zarr,
                        force_overwrite=force_overwrite,
                        **per_run_args,
                    )  # make a copy
                    new_args.append(f"--filter-dataset-name '^{dataset.name}$'")
                    new_args.append(f"--filter-run-name '^{run.name}$'")

                    dataset_id = dataset.name
                    deposition_id = deposition.name
                    prefix = f"{int(time.time())}-dep{deposition_id}-ds{dataset_id}"
                    execution_name = f"{prefix}-run{run.name}"

                    # execution name greater than 80 chars causes boto ValidationException
                    if len(execution_name) > 80:
                        run_size = 76 - len(prefix)
                        execution_name = f"{prefix}-run{run.name[-run_size:]}"

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
                                **ctx.obj,
                            ),
                        ),
                    )
                wait_for_futures(futures)


class OrderedSyncFilters(click.Command):
    """Preserves the relative order of --include/--exclude, which `aws s3 sync` is sensitive to."""

    def parse_args(self, ctx, args):
        parser = self.make_parser(ctx)
        opts, _, param_order = parser.parse_args(args=list(args))
        # Instance-level, not class-level: a class attribute accumulates filters across
        # invocations and makes the command non-reentrant.
        self.ordered_filters = []
        for param in param_order:
            if param.name not in ["include", "exclude"]:
                continue
            self.ordered_filters.append((param.name, opts[param.name].pop(0)))

        return super().parse_args(ctx, args)


def parse_s3_uri(uri: str, param_hint: str) -> tuple[str, str]:
    """Split an ``s3://bucket/prefix`` URI into ``(bucket, prefix)``."""
    if not uri.startswith("s3://"):
        raise click.BadParameter(f"must be an s3:// URI, got {uri!r}", param_hint=param_hint)
    remainder = uri[len("s3://") :].strip("/")
    if not remainder:
        raise click.BadParameter("must name a bucket", param_hint=param_hint)
    bucket, _, prefix = remainder.partition("/")
    return bucket, prefix


def resolve_exact_ids(found, requested, bucket, entity, param_hint, note="") -> list[str]:
    """Keep only the ids matching `requested` exactly, in the order they were requested.

    The listing helpers select by S3 key prefix -- `db-import` relies on that -- so without
    this `--dataset 1052` would quietly sync 10521 through 10526, and a typo would fall
    through to "Nothing to sync." and exit 0. Repeats are collapsed too: two jobs for one id
    generate the same execution name, and the second submission is rejected.
    """
    available = set(found)
    ordered = list(dict.fromkeys(requested))
    missing = [item for item in ordered if item not in available]
    if missing:
        raise click.BadParameter(
            f"must name a {entity} exactly, and these matched nothing in "
            f"s3://{bucket}: {', '.join(missing)}.{note}",
            param_hint=param_hint,
        )
    return ordered


def build_aws_sync_flags(ctx, delete, dryrun, exact_timestamps, size_only) -> list[str]:
    """The `aws s3 sync` flags, as an argv list. Filters keep their command-line order."""
    flags = []
    if delete:
        flags.append("--delete")
    if dryrun:
        flags.append("--dryrun")
    if exact_timestamps:
        flags.append("--exact-timestamps")
    if size_only:
        flags.append("--size-only")
    for name, value in getattr(ctx.command, "ordered_filters", []):
        flags.extend([f"--{name}", value])
    return flags


def aws_sync_argv(src_bucket, src_path, dest_bucket, dest_path, flags) -> list[str]:
    return [
        "aws",
        "s3",
        "sync",
        *flags,
        f"s3://{os.path.join(src_bucket, src_path)}",
        f"s3://{os.path.join(dest_bucket, dest_path)}",
    ]


def execute_sync(ctx, jobs, src_bucket, dest_bucket, flags, swipe_wdl_key):
    """Submit one SWIPE job per entry in `jobs`. Real syncs need write access to the
    destination bucket, so they always run remotely rather than locally."""
    # The container shell re-parses this string, so quote each token exactly once.
    shell_flags = " ".join(shlex.quote(flag) for flag in flags)
    comms_bucket = ctx.obj.get("swipe_comms_bucket")

    def print_submitted(execution_name):
        """Called once a submission has resolved, so a failed one is never announced."""
        print(f"submitted {execution_name}")
        print(
            f"  aws s3 cp s3://{comms_bucket}/swipe/swipe-job-output/"
            f"{execution_name}/results/output.txt -",
        )

    futures = {}
    with ProcessPoolExecutor(max_workers=ctx.obj["parallelism"]) as workerpool:
        for label, src_path, dest_path in jobs:
            # Match run_job's own sanitisation so the name we print is the name it uses.
            execution_name = re.sub(r"[^0-9a-zA-Z-]", r"-", f"{int(time.time())}-sync-{label}")[-80:]
            wdl_args = {
                "input_bucket": src_bucket,
                "input_path": src_path,
                "output_bucket": dest_bucket,
                "output_path": dest_path,
                "flags": shell_flags,
            }
            future = workerpool.submit(
                partial(run_job, execution_name, wdl_args, swipe_wdl_key=swipe_wdl_key, **ctx.obj),
            )
            futures[future] = execution_name
        wait_for_futures(futures, on_success=print_submitted)


def run_local_dryrun(jobs, src_bucket, dest_bucket, flags) -> None:
    """Run the dry run locally and stream it to this terminal.

    A dry run only lists and compares, so it needs read access to both buckets and nothing
    else -- unlike a real sync, which needs write access to the destination and therefore a
    different role. Running it here avoids waiting for a spot instance and then digging the
    result out of CloudWatch.
    """
    failures = 0
    for label, src_path, dest_path in jobs:
        if len(jobs) > 1:
            print(f"\n=== {label} ===", flush=True)
        argv = aws_sync_argv(src_bucket, src_path, dest_bucket, dest_path, flags)
        result = subprocess.run(argv, check=False)  # noqa: S603 - argv is built from validated input
        if result.returncode != 0:
            failures += 1
            logger.error("dry run failed for %s (exit %s)", label, result.returncode)
    if failures:
        raise RuntimeError(f"{failures} of {len(jobs)} dry runs failed; see errors above.")


@cli.command(name="sync", cls=OrderedSyncFilters)
@click.argument("source", required=True, type=str)
@click.argument("dest", required=True, type=str)
# Options below mirror `aws s3 sync` and are passed straight through to it.
@click.option("--include", type=str, default=None, multiple=True, help="Path pattern to include. Order relative to --exclude matters; see the aws s3 sync docs.")
@click.option("--exclude", type=str, default=None, multiple=True, help="Path pattern to exclude. Order relative to --include matters; see the aws s3 sync docs.")
@click.option("--delete", is_flag=True, default=False, help="Delete files in DEST that are not in SOURCE.")
@click.option("--dryrun", is_flag=True, default=False, help="Show what would be copied without copying it. Runs locally and prints to this terminal.")
@click.option("--exact-timestamps", is_flag=True, default=False, help="Passed through to aws s3 sync.")
@click.option("--size-only", is_flag=True, default=False, help="Passed through to aws s3 sync.")
# Options below are specific to this wrapper.
@click.option("--per-dataset/--single-job", default=None, help="Submit one job per dataset rather than one job for the whole SOURCE prefix. Requires SOURCE and DEST to be bucket roots. Defaults to per-dataset when SOURCE is a bucket root.")
@click.option("--dataset", type=str, default=None, multiple=True, help="Only sync these datasets, named by exact id (repeatable). Implies --per-dataset; an id matching no dataset is an error.")
@click.option("--exclude-dataset", type=str, default=None, multiple=True, help="Skip datasets whose id matches this regex (repeatable).")
@click.option("--include-deposition", type=str, default=None, multiple=True, help="Also sync depositions_metadata for these depositions, named by exact id (repeatable).")
@click.option("--no-sync-dataset", is_flag=True, default=False, help="Skip dataset syncing; useful with --include-deposition.")
@click.option("--print-command", is_flag=True, default=False, help="Print the aws s3 sync command(s) that would run, then exit.")
@click.option(
    "--swipe-wdl-key",
    type=str,
    required=True,
    default="sync-v0.0.2.wdl",
    help="Specify wdl key for custom workload",
)
@enqueue_common_options
@click.pass_context
def sync(
    ctx,
    source: str,
    dest: str,
    delete: bool,
    dryrun: bool,
    exact_timestamps: bool,
    size_only: bool,
    per_dataset: bool | None,
    dataset: list[str],
    exclude_dataset: list[str],
    include_deposition: list[str],
    no_sync_dataset: bool,
    print_command: bool,
    swipe_wdl_key: str,
    **kwargs,
):
    """Sync data between two S3 locations, e.g.

        enqueue_runs.py sync s3://cryoet-data-portal-staging/10001 s3://cryoet-data-portal-public/10001

    SOURCE and DEST are s3:// URIs, as with `aws s3 sync`.
    """
    src_bucket, src_prefix = parse_s3_uri(source, "SOURCE")
    dest_bucket, dest_prefix = parse_s3_uri(dest, "DEST")
    flags = build_aws_sync_flags(ctx, delete, dryrun, exact_timestamps, size_only)

    # A single job runs a single `aws s3 sync`, which takes a single source, so this asks for
    # something that cannot exist -- an explicit choice to discard rather than to resolve.
    if dataset and per_dataset is False:
        raise click.BadParameter(
            "--single-job syncs one prefix, so it cannot be combined with --dataset. Drop "
            "--single-job, or name the dataset in SOURCE and DEST instead.",
            param_hint="--dataset",
        )

    # Fanning out per dataset is the useful default for a whole-bucket sync, and the wrong
    # one when the caller already named a single prefix.
    if per_dataset is None:
        per_dataset = not src_prefix
    if dataset:
        per_dataset = True

    # Dataset and deposition ids are resolved from the bucket root, so a prefix here would be
    # applied a second time: `--dataset 10002 s3://stg/10002` would sync s3://stg/10002/10002,
    # which holds nothing, onto the real dataset under DEST -- emptying it under --delete.
    if per_dataset or include_deposition:
        for hint, uri, bucket, prefix in (
            ("SOURCE", source, src_bucket, src_prefix),
            ("DEST", dest, dest_bucket, dest_prefix),
        ):
            if prefix:
                raise click.BadParameter(
                    f"must be a bucket root when syncing whole datasets or depositions, got "
                    f"{uri!r}. Use s3://{bucket} and select with --dataset / --include-deposition.",
                    param_hint=hint,
                )

    jobs = []
    if not no_sync_dataset:
        if per_dataset:
            found = [entity_id for entity_id, _ in get_datasets(src_bucket, "", (), dataset, exclude_dataset, "", False)]
            if dataset:
                note = " (--exclude-dataset is applied first.)" if exclude_dataset else ""
                found = resolve_exact_ids(found, dataset, src_bucket, "dataset", "--dataset", note)
            # SOURCE and DEST are bucket roots here, so an id is already the whole path.
            jobs.extend((f"ds-{entity_id}", entity_id, entity_id) for entity_id in found)
        else:
            jobs.append((f"ds-{src_prefix or src_bucket}", src_prefix, dest_prefix))

    if include_deposition:
        found = [dep_id for dep_id, _ in get_depositions(src_bucket, include_deposition, False)]
        deposition_ids = resolve_exact_ids(
            found, include_deposition, src_bucket, "deposition", "--include-deposition",
        )
        for deposition_id in deposition_ids:
            path = os.path.join("depositions_metadata", deposition_id)
            jobs.append((f"dep-{deposition_id}", path, path))

    if not jobs:
        print("Nothing to sync.")
        return

    if print_command:
        for _, src_path, dest_path in jobs:
            print(shlex.join(aws_sync_argv(src_bucket, src_path, dest_bucket, dest_path, flags)))
        return

    if dryrun:
        # A dry run copies nothing, so run it here rather than paying for a spot instance
        # and then having to read the result out of CloudWatch.
        run_local_dryrun(jobs, src_bucket, dest_bucket, flags)
        return

    # Syncs always run on the staging SWIPE deployment -- the direction is always
    # staging -> public -- so there is no environment to select, and `sync` does not take
    # the flag. Only a real sync needs the environment resolved, so it stays lazy.
    kwargs["environment"] = "staging"
    handle_common_options(ctx, kwargs)
    if not ctx.obj.get("memory"):
        ctx.obj["memory"] = 4000
    if not ctx.obj.get("vcpu"):
        # aws s3 sync is bound by request concurrency; 1 vCPU cannot keep 100 requests busy.
        ctx.obj["vcpu"] = 4

    print(f"Submitting {len(jobs)} job(s)...")
    execute_sync(ctx, jobs, src_bucket, dest_bucket, flags, swipe_wdl_key)


def execute_validate(
    ctx,
    workerpool: ProcessPoolExecutor,
    identifier: str,
    input_bucket: str,
    output_dir: str,
    swipe_wdl_key: str,
    test_entity: str,
    additional_params: dict[str, str],
):
    execution_name = f"{int(time.time())}-{identifier}"
    # execution name greater than 80 chars causes boto ValidationException
    if len(execution_name) > 80:
        execution_name = execution_name[-80:]

    # Default to using a lot less memory than the ingestion job.
    if not ctx.obj.get("memory"):
        ctx.obj["memory"] = 4000

    wdl_args = {
        "dataset": additional_params.get("dataset_id", ""),
        "input_bucket": input_bucket,
        "output_bucket": "cryoet-data-portal-staging",
        "output_dir": output_dir,
        "extra_args": additional_params.get("extra_args", ""),
        "config_file": additional_params.get("config_file", ""),
        "flags": additional_params.get("flags", ""),
        "test_entity": test_entity,
    }
    return workerpool.submit(
        partial(
            run_job,
            execution_name,
            wdl_args,
            swipe_wdl_key=swipe_wdl_key,
            **ctx.obj,
        ),
    )


@cli.command(name="validate")
@click.argument("dataset_ids", nargs=-1, required=True, type=str)
@click.option(
    "--swipe-wdl-key",
    type=str,
    required=True,
    default="validate_dataset-v0.0.2.wdl",
    help="Specify wdl key for custom workload",
)
@enqueue_common_options
@environment_option
@click.pass_context
def validate(
    ctx,
    dataset_ids: list[str],
    swipe_wdl_key: str,
    **kwargs,
):
    # The environment flag only switches which bucket we're validating
    input_bucket = "cryoet-data-portal-public"
    output_dir = "prod_validation"
    env = "prod"
    if kwargs.get("environment") == "staging":
        env = "staging"
        input_bucket = "cryoet-data-portal-staging"
        output_dir = "staging_validation"

    # We always run validation in the staging env.
    kwargs["environment"] = "staging"
    handle_common_options(ctx, kwargs)

    futures = []
    with ProcessPoolExecutor(max_workers=ctx.obj["parallelism"]) as workerpool:
        for dataset_id in dataset_ids:
            print(f"Processing {dataset_id}...")
            validation_params = {
                "dataset_id": dataset_id,
            }
            future = execute_validate(
                ctx=ctx,
                identifier=f"validate-{env}-{dataset_id}",
                input_bucket=input_bucket,
                output_dir=output_dir,
                swipe_wdl_key=swipe_wdl_key,
                test_entity="standardized",
                additional_params=validation_params,
                workerpool=workerpool,
            )
            futures.append(future)
        wait_for_futures(futures)


@cli.command(name="source-validate")
@click.argument("ingestion-config", required=True, type=str)
@click.argument("input-bucket", required=False, type=str, default="cryoetportal-rawdatasets-dev")
@click.option(
    "--swipe-wdl-key",
    type=str,
    required=True,
    default="validate_dataset-v0.0.2.wdl",
    help="Specify wdl key for custom workload",
)
@enqueue_common_options
@environment_option
@click.pass_context
def source_validate(
    ctx,
    ingestion_config: str,
    input_bucket: str,
    swipe_wdl_key: str,
    **kwargs,
):
    output_dir = "source_validation"

    # We always run validation in the staging env.
    kwargs["environment"] = "staging"
    handle_common_options(ctx, kwargs)

    futures = []
    with ProcessPoolExecutor(max_workers=ctx.obj["parallelism"]) as workerpool:
        print(f"Processing {ingestion_config}...")
        validation_params = {
            "config_file": ingestion_config,
            "flags": "--no-multiprocessing",
        }
        future = execute_validate(
            ctx=ctx,
            identifier=f"validate-src-{os.path.basename(ingestion_config)}",
            input_bucket=input_bucket,
            output_dir=output_dir,
            swipe_wdl_key=swipe_wdl_key,
            test_entity="source",
            additional_params=validation_params,
            workerpool=workerpool,
        )
        futures.append(future)
        wait_for_futures(futures)


if __name__ == "__main__":
    cli()
