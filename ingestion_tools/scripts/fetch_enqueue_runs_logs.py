import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor
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
    if len(history) == 0:
        logger.error("Skipping, no log stream found for %s", execution_arn)
        return False, None
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


def process_arn(arn: str, session: Session, output_dir: str, failed_only: bool, links_only: bool) -> str:
    log_stream_failed, log_stream_name = get_log_stream(session, arn)
    if not log_stream_name:
        logger.warning("No log stream found for %s, possibly still running", arn)
        return

    result = "FAILED" if log_stream_failed else "SUCCESS"
    logger.info("%s: %s", result, arn)
    output_file = (
        output_dir + ("failed/" if log_stream_failed else "success/") + arn.replace("/", "_").replace(":", "_") + ".log"
    )

    if links_only:
        link = f"https://console.aws.amazon.com/cloudwatch/home?region={session.region_name}#logEventViewer:group={LOG_GROUP_NAME};stream={log_stream_name}"
        logger.info("Link: %s", link)
        return result

    if failed_only and not log_stream_failed:
        return result

    logs = get_log_events(session, LOG_GROUP_NAME, log_stream_name)
    if os.path.exists(output_file):
        logger.warning("Removing existing %s", output_file)
        os.remove(output_file)
    logger.info("Writing to %s", output_file)
    with open(output_file, "w") as f:
        f.write("\n".join(logs))

    return result


@click.command()
@click.argument("execution-arn", type=str, nargs=-1)
@click.option("--input-file", type=str, help="A file containing a list of execution ARNs.")
@click.option("--output-dir", type=str, default="./fetch-logs", help="The directory to save the logs to.")
@click.option("--profile", type=str, default=None, help="The AWS profile to use.")
@click.option("--failed-only", is_flag=True, help="Only fetch logs for failed executions.")
@click.option("--links-only", is_flag=True, help="Only get CloudWatch log links, not the logs themselves.")
def main(execution_arn: list[str], input_file: str, output_dir: str, profile: str, failed_only: bool, links_only: bool):
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

    if output_dir[-1] != "/":
        output_dir += "/"

    # setup output directory
    if not links_only:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        if not os.path.exists(f"{output_dir}failed"):
            os.makedirs(f"{output_dir}failed")
        if not os.path.exists(f"{output_dir}success"):
            os.makedirs(f"{output_dir}success")

    input_execution_arn = list(set(input_execution_arn))
    session = Session(region_name=input_execution_arn[0].split(":")[3], profile_name=profile)

    failed_count = 0
    successful_count = 0

    # fetch logs, multithreaded
    with ThreadPoolExecutor() as executor:
        results = executor.map(
            lambda arn: process_arn(arn, session, output_dir, failed_only, links_only),
            input_execution_arn,
        )
        for result in results:
            if result == "FAILED":
                failed_count += 1
            elif result == "SUCCESS":
                successful_count += 1

    logger.info("====================================")
    logger.info("TOTAL FAILED: %d/%d", failed_count, len(input_execution_arn))
    logger.info("TOTAL SUCCEEDED %d/%d", successful_count, len(input_execution_arn))
    logger.info("TOTAL SKIPPED: %d", len(input_execution_arn) - failed_count - successful_count)


if __name__ == "__main__":
    main()
