import datetime
import os
import sys

import click

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CURRENT_DIR, ".."))
from common.fs import FileSystemApi, S3Filesystem  # noqa: E402

STAGING_BUCKET = "cryoet-data-portal-staging"
OUTPUT_BUCKET = "cryoetportal-output-test"


def get_history(s3_report: str, destination: str, fs: S3Filesystem):
    fs.s3fs.get(f"{s3_report}/history/", f"{destination}/history", recursive=True)


@click.command()
@click.option(
    "--local-dir",
    default="./results",
    type=str,
    help="Local directory to store the results. Note that if this folder is in the data_validation folder (as \
      is the default value), it should be added to the pytest call via `--ignore=[FOLDER_NAME]` to prevent pytest from \
      wasting time trying to discover tests (we default ignore ./results in `pytest.ini`.)",
)
@click.option("--input-bucket", default=STAGING_BUCKET, type=str, help="S3 bucket to search for datasets.")
@click.option("--output-bucket", default=OUTPUT_BUCKET, type=str, help="S3 bucket to store the report.")
@click.option("--output-dir", default="data_validation", type=str, help="Output directory in the S3 bucket.")
@click.option("--datasets", default="*", type=str, help="Comma separated list of dataset IDs.")
@click.option(
    "--multiprocessing/--no-multiprocessing",
    is_flag=True,
    default=True,
    help="Run tests simultaneously with multiple workers (pytest-xdist).",
)
@click.option(
    "--history/--no-history",
    is_flag=True,
    default=True,
    help="Save the history to S3 and retrieve the history of the report. If testing multiple datasets, \
    saving history will result in longer execution time (each dataset has to be an individual `pytest` call).",
)
@click.option(
    "--extra-args",
    default=None,
    type=str,
    help="Extra arguments to pass to pytest (in one string).",
)
def main(
    local_dir: str,
    output_dir: str,
    input_bucket: str,
    output_bucket: str,
    datasets: str | None,
    multiprocessing: bool,
    history: bool,
    extra_args: str | None,
):
    fs: S3Filesystem = FileSystemApi.get_fs_api(mode="s3", force_overwrite=False)

    if datasets is None:
        datasets = fs.glob(f"s3://{input_bucket}/*")
        datasets = [os.path.basename(dataset) for dataset in datasets if os.path.basename(dataset).isdigit()]
    else:
        datasets = datasets.split(",")

    datasets = sorted(datasets, key=lambda x: int(x))

    # If we are not saving history, we can run all datasets in one go (individual dataset runs don't need to be tracked)
    if not history:
        datasets = [",".join(datasets)]

    extra_args = extra_args if extra_args else ""

    for dataset in datasets:
        now = datetime.datetime.now().isoformat(sep="_", timespec="seconds").replace(":", "-")

        # Accumulate test results here
        localdir_raw = f"{local_dir}/{dataset}_raw/{now}"
        # Generate report here
        localdir_rep = f"{local_dir}/{dataset}/{now}"

        # Run tests and generate results
        os.system(
            f"pytest {'--dist worksteal -n auto' if multiprocessing else '--dist no'} --datasets {dataset} --alluredir {localdir_raw} {extra_args}",
        )

        # Get the history from S3 (Must do this before generating the report)
        remote_dataset_dir = f"{output_bucket}/{output_dir}/{dataset}"
        if fs.exists(remote_dataset_dir):
            get_history(remote_dataset_dir, localdir_raw, fs)
            fs.s3fs.rm(remote_dataset_dir, recursive=True)

        # Generate the report
        os.system(f"allure generate --output {localdir_rep} {localdir_raw}")

        # Upload the new report
        fs.s3fs.put(localdir_rep, remote_dataset_dir, recursive=True)


if __name__ == "__main__":
    main()
