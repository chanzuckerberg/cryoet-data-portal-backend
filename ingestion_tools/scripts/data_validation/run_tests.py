import datetime
import os
import sys
import tarfile

import click

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CURRENT_DIR, ".."))
from common.fs import FileSystemApi, S3Filesystem  # noqa: E402

STAGING_BUCKET = "cryoet-data-portal-staging"
OUTPUT_BUCKET = "cryoetportal-rawdatasets-dev"


def get_history(tar_report: str, destination: str, fs: FileSystemApi):
    with fs.open(tar_report, "rb") as f, tarfile.open(fileobj=f, mode="r:gz") as t:
        for file in t.getmembers():
            # only extract everything in the history directory
            if file.name.startswith("./history"):
                t.extract(file, path=destination)


@click.command()
@click.argument("local-dst", default="./results", type=str)  # Local directory to store results.
@click.option("--bucket", default=STAGING_BUCKET, type=str, help="S3 bucket to search for datasets.")
@click.option("--output-bucket", default=OUTPUT_BUCKET, type=str, help="S3 bucket to store the report.")
@click.option("--datasets", default="*", type=str, help="Comma separated list of dataset IDs.")
@click.option(
    "--multiprocessing/--no-multiprocessing",
    is_flag=True,
    help="Run tests simultaneously with multiple workers (pytest-xdist).",
)
@click.option(
    "--history/--no-history",
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
    local_dst: str,
    bucket: str,
    output_bucket: str,
    datasets: str | None,
    multiprocessing: bool,
    history: bool,
    extra_args: str | None,
):
    fs: S3Filesystem = FileSystemApi.get_fs_api(mode="s3", force_overwrite=False)
    now = datetime.datetime.now().isoformat(sep="_", timespec="seconds").replace(":", "-")

    if datasets is None:
        datasets = fs.glob(f"s3://{bucket}/*")
        datasets = [os.path.basename(dataset) for dataset in datasets if os.path.basename(dataset).isdigit()]
    else:
        datasets = datasets.split(",")

    datasets = sorted(datasets, key=lambda x: int(x))

    # If we are not saving history, we can run all datasets in one go (individual dataset runs don't need to be tracked)
    if not history:
        datasets = [",".join(datasets)]

    extra_args = extra_args if extra_args else ""

    for dataset in datasets:
        # Accumulate test results here
        localdir_raw = f"{local_dst}/{dataset}_raw/{now}"
        # Generate report here
        localdir_rep = f"{local_dst}/{dataset}/{now}"
        # Archive location
        local_tar = f"{local_dst}/{dataset}/{dataset}_{now}.tar.gz"

        # Run tests and generate results
        exit_code = os.system(
            f"pytest {'--dist worksteal -n auto' if multiprocessing else '--dist no'} --datasets {dataset} --alluredir {localdir_raw} {extra_args}",
        )

        if exit_code != 0:
            print(f"Failed to run tests for dataset {dataset}. Skipping...")
            continue

        os.makedirs(localdir_raw, exist_ok=True)
        os.makedirs(localdir_rep, exist_ok=True)

        # Get the history from S3 (Must do this before generating the report)
        remote_dataset_dir = f"{output_bucket}/data_validation/{dataset}"
        remote_dataset_tar = f"{remote_dataset_dir}/{dataset}.tar.gz"
        fs.makedirs(remote_dataset_dir)

        if fs.exists(remote_dataset_tar):
            get_history(remote_dataset_tar, localdir_raw, fs)

        # Generate the report
        os.system(f"allure generate --output {localdir_rep} {localdir_raw}")

        # Upload the new report
        os.system(f"tar -czf {local_tar} -C {localdir_rep} .")
        fs.s3fs.put(local_tar, remote_dataset_tar)
        os.system(f"rm -rf {local_tar}")


if __name__ == "__main__":
    main()
