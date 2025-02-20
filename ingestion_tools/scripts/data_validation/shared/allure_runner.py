import datetime
import json
import os
import sys
import tarfile

import click

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CURRENT_DIR, "..", ".."))
from common.fs import FileSystemApi  # noqa: E402

DEFAULT_OUTPUT_BUCKET = "cryoetportal-output-test"


def common_options(func):
    options = [
        click.option(
            "--local-dir",
            type=str,
            default="./results",
            help="Local directory to store the results. Note that if this folder is in the data_validation folder (as "
                 "is the default value), it should be added to the pytest call via `--ignore=[FOLDER_NAME]` to prevent "
                 "pytest from wasting time trying to discover tests (we default ignore ./results in `pytest.ini`.)",
        ),
        click.option(
            "--input-bucket",
            type=str,
            help="S3 bucket to use for the source data for the test run.",
        ),

        click.option(
            "--output-dir",
            type=str,
            help="Output directory in the S3 bucket.",
        ),
        click.option(
            "--output-bucket",
            default=DEFAULT_OUTPUT_BUCKET,
            type=str,
            help="S3 bucket to store the report.",
        ),
        click.option(
            "--multiprocessing/--no-multiprocessing",
            is_flag=True,
            default=True,
            help="Run tests simultaneously with multiple workers (pytest-xdist).",
        ),
        click.option(
            "--history/--no-history",
            is_flag=True,
            default=True,
            help="Save the history to S3 and retrieve the history of the report. If testing multiple datasets, saving "
                 "history will result in longer execution time (each dataset has to be an individual `pytest` call).",
        ),
        click.option(
            "--extra-args",
            default=None,
            type=str,
            help="Extra arguments to pass to pytest (in one string).",
        ),
        click.option(
            "--update-s3/--no-update-s3",
            is_flag=True,
            default=True,
            help="Write to S3 the results from this validation session.",
        ),
    ]

    for option in options:
        func = option(func)
    return func


def get_history(tar_report: str, destination: str, fs: FileSystemApi):
    print(f"Getting history from: {tar_report}")
    with fs.open(tar_report, "rb") as f, tarfile.open(fileobj=f, mode="r:gz") as t:
        for file in t.getmembers():
            if "/history/" in file.name and file.isfile():
                file.name = os.path.basename(file.name)
                t.extract(file, path=f"{destination}/history")

def update_with_default(input_options: dict, custom_default: dict) -> dict:
    return { k: v or custom_default.get(k) for k, v in input_options.items() }


def execute_allure_tests(
        identifier_name: str,
        additional_parameters: list[str],
        output_dir: str,
        **kwargs,
):
    now = datetime.datetime.now()
    now_str = now.isoformat(sep="_", timespec="seconds").replace(":", "-")
    version = now.strftime("%Y%m%d%H%M%S")  # Needs to parse-able as an int.

    local_dir = kwargs["local_dir"]
    # Accumulate test results here
    localdir_raw = f"{local_dir}/{identifier_name}_raw/{now_str}"
    # Generate report here
    localdir_rep = f"{local_dir}/{identifier_name}/{now_str}"

    executable_cmd_component = [
        "pytest",
        "--dist loadscope -n auto" if kwargs.get("multiprocessing") else "--dist no",
        f"--alluredir {localdir_raw}",
    ]

    if kwargs.get("extra_args"):
        executable_cmd_component.append(kwargs["extra_args"])

    executable_command = " ".join(executable_cmd_component + additional_parameters)
    print(f"Running: {executable_command}")
    os.system(executable_command)

    # Allure needs this file in order to generate reports with history
    with open(f"{localdir_raw}/executor.json", "w") as fh:
        fh.write(
            json.dumps(
                {
                    "reportName": f"Build {identifier_name}",
                    "buildOrder": version,
                    "name": f"Data validation for {identifier_name}",
                },
            ),
        )

    fs = FileSystemApi.get_fs_api(mode="s3", force_overwrite=False)
    output_bucket = kwargs["output_bucket"]
    # Get the history from S3 (Must do this before generating the report)
    remote_tar_report = f"{output_bucket}/{output_dir}/{identifier_name}.tar.gz"
    if fs.exists(remote_tar_report):
        get_history(remote_tar_report, localdir_raw, fs)

    # Generate the report
    os.system(f"allure generate --output {localdir_rep} {localdir_raw}")

    if kwargs["update_s3"]:
        # Compress and upload the new report
        tar_report = f"{localdir_rep}.tar.gz"
        print(f"Compressing {localdir_rep} to {tar_report} and replacing {remote_tar_report}")
        os.system(f"tar -czf {tar_report} {localdir_rep}")
        fs.s3fs.put(tar_report, remote_tar_report, recursive=True)
        remote_report_dir = f"s3://{output_bucket}/{output_dir}/{identifier_name}/"
        print(f"Syncing report from {localdir_rep} to {remote_report_dir}")
        fs.s3fs.put(f"{localdir_rep}/*", remote_report_dir, recursive=True)
        os.remove(tar_report)
