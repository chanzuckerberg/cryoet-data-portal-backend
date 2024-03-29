import json
import re
import time

import boto3
import click
from boto3 import Session

from common.fs import FileSystemApi


@click.group()
@click.pass_context
def cli(ctx):
    pass


def run_job(
    execution_name: str,
    input_bucket: str,
    dataset: str,
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
        memory = 4000

    state_machine_arn = f"arn:aws:states:{aws_region}:{aws_account_id}:stateMachine:{sfn_name}"

    execution_name = re.sub(r"[^0-9a-zA-Z-]", r"-", execution_name)
    sfn_input_json = {
        "Input": {
            "Run": {
                "aws_region": aws_region,
                "docker_image_id": f"{aws_account_id}.dkr.ecr.{aws_region}.amazonaws.com/{ecr_repo}:{ecr_tag}",
                "input_bucket": input_bucket,
                "dataset": dataset,
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
@click.argument("input_bucket", required=True, type=str)
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
@click.option(
    "--filter-dataset-name",
    type=str,
    default=None,
    multiple=True,
    help="Only process runs matching the regex. If not specified, all runs are processed",
)
@click.option("--memory", type=int, default=None, help="Specify memory allocation override")
@click.pass_context
def queue(
    ctx,
    input_bucket: str,
    env_name: str,
    ecr_repo: str,
    ecr_tag: str,
    swipe_wdl_key: str,
    filter_dataset_name: list[str],
    memory: int | None,
):
    fs_mode = "s3"
    fs = FileSystemApi.get_fs_api(mode=fs_mode, force_overwrite=False)

    filter_ds_name_patterns = [re.compile(pattern) for pattern in filter_dataset_name]

    fs = FileSystemApi.get_fs_api(mode=fs_mode, force_overwrite=False)

    # Find tiltseries
    datasets = fs.glob(f"{input_bucket}/*/dataset_metadata.json")
    for ds_path in datasets:
        dataset_id = ds_path.split("/")[-2]
        if filter_dataset_name and not list(filter(lambda x: x.match(dataset_id), filter_ds_name_patterns)):
            print(f"Skipping dataset {dataset_id}..")
            continue
        execution_name = f"{int(time.time())}-fix-ds{dataset_id}"

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

        run_job(
            execution_name,
            input_bucket,
            dataset_id,
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
