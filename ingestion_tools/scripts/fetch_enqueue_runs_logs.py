import logging
import os
import re
import shutil
from typing import Tuple

import click
from boto3 import Session

logger = logging.getLogger("db_import")
logging.basicConfig(level=logging.INFO)

LOG_GROUP_NAME = "/aws/batch/job"


def get_log_stream(session: Session, execution_arn: str) -> Tuple[bool, str]:
    client = session.client("stepfunctions")
    response = client.get_execution_history(
        executionArn=execution_arn,
    )

    # get the last task scheduled with a log stream
    history = response["events"]
    history.sort(key=lambda x: x["timestamp"])
    history = [
        event
        for event in history
        if event["type"] == "TaskScheduled" and "LogStreamName" in event["taskScheduledEventDetails"]["parameters"]
    ]
    last_task_submitted = history[-1]
    parameters = last_task_submitted["taskScheduledEventDetails"]["parameters"]
    failed = re.search(r'"Status":"FAILED"', parameters, re.IGNORECASE)
    return failed, re.search(r'"LogStreamName":"([a-zA-Z-/0-9]*)"', parameters).group(1)


def get_log_events(session: Session, log_group_name, log_stream_name):
    client = session.client("logs")
    response = client.get_log_events(
        logGroupName=log_group_name,
        logStreamName=log_stream_name,
        startFromHead=True,
    )
    events = response["events"]
    return [event["message"] for event in events]


@click.command()
@click.argument("execution-arn", type=str, nargs=-1)
@click.option("--input-file", type=str, help="A file containing a list of execution ARNs.")
@click.option("--output-dir", type=str, default="./fetch-logs", help="The directory to save the logs to.")
@click.option("--profile", type=str, default=None, help="The AWS profile to use.")
def main(execution_arn: list[str], input_file: str, output_dir: str, profile: str):
    input_execution_arn = execution_arn

    if not execution_arn and not input_file:
        logger.error("Please provide at least one execution ARN.")
        return

    if input_file and execution_arn:
        logger.error("Please provide either execution ARNs or an execution ARN file, not both.")
        return

    if input_file:
        if not os.path.exists(input_file):
            logger.error("The provided execution ARN file does not exist.")
            return

        with open(input_file, "r") as f:
            input_execution_arn = f.read().splitlines()

    if os.path.exists(output_dir):
        logger.warning("Removing existing %s directory.", output_dir)
        shutil.rmtree(output_dir)

    os.makedirs(output_dir)
    os.makedirs(f"{output_dir}/failed")
    os.makedirs(f"{output_dir}/success")

    input_execution_arn = list(set(input_execution_arn))
    session = Session(region_name=input_execution_arn[0].split(":")[3], profile_name=profile)

    failed_count = 0
    successful_count = 0

    for arn in input_execution_arn:
        log_stream_failed, log_stream_name = get_log_stream(session, arn)
        logger.info("%s: %s", "FAILED" if log_stream_failed else "SUCCESS", log_stream_name)
        output_file = (
            output_dir
            + "/"
            + ("failed/" if log_stream_failed else "success/")
            + log_stream_name.replace("/", "_")
            + ".log"
        )
        if log_stream_failed:
            failed_count += 1
        else:
            successful_count += 1
        logs = get_log_events(session, LOG_GROUP_NAME, log_stream_name)
        with open(output_file, "w") as f:
            f.write("\n".join(logs))

    logger.info("====================================")
    logger.info("TOTAL FAILED: %d", failed_count)
    logger.info("TOTAL SUCCEEDED %d", successful_count)


if __name__ == "__main__":
    main()
