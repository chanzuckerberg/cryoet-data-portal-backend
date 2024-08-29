import datetime
import os
import sys
import tarfile

import click

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CURRENT_DIR, ".."))
from common.fs import FileSystemApi, S3FileSystem  # noqa: E402

STAGING_BUCKET = "cryoet-data-portal-staging"
OUTPUT_BUCKET = "cryoetportal-rawdatasets-dev"


def get_history(tar_report: str, destination: str, fs: FileSystemApi):
    with fs.open(tar_report, "rb") as f, tarfile.open(fileobj=f, mode="r:gz") as t:
        for file in t.getmembers():
            if file.name.startswith("history"):
                t.extract(file, path=f"{destination}/")


@click.group()
def cli():
    pass


@cli.command()
@click.argument("local_dst", default="./results", type=str)  # Local directory to store results.
@click.option(
    "--remote_dst",
    required=False,
    type=str,
    help="Remote directory on S3 to store results and obtain history.",
)
@click.option("--datasets", required=False, type=str, default=None, help="Comma separated list of dataset IDs.")
def all(
    local_dst: str,
    remote_dst: str,
    datasets: str | None,
):

    fs: S3FileSystem = FileSystemApi.get_fs_api(mode="s3", force_overwrite=False)
    if datasets is None:
        datasets = fs.glob(f"s3://{STAGING_BUCKET}/*")
        datasets = [os.path.basename(dataset) for dataset in datasets if "deposition" not in dataset]
    else:
        datasets = datasets.split(",")

    now = datetime.datetime.now().isoformat(sep="_", timespec="seconds").replace(":", "-")

    local_dst = f"{local_dst}/data_validation_{now}"

    remote_report_dir = f"s3://{OUTPUT_BUCKET}/{remote_dst}/data_validation" if remote_dst else None
    if remote_report_dir:
        fs.makedirs(remote_report_dir)

    for dataset in datasets:
        # Accumulate test results here
        localdir_raw = f"{local_dst}/{dataset}_raw"
        # Generate report here
        localdir_rep = f"{local_dst}/{dataset}"
        # Zip for upload to S3
        # report_tar = f"{localdir_rep}/{dataset}.tar.gz"
        # Locations on S3
        remote_dataset_tar = f"{remote_report_dir}/{dataset}.tar.gz" if remote_report_dir else None
        # remote_history_dir = f"{remote_dataset_dir}/history"

        os.makedirs(localdir_raw, exist_ok=True)
        os.makedirs(localdir_rep, exist_ok=True)

        # Test and report generation
        os.system(f"pytest -n auto --dist loadscope --dataset={dataset} --alluredir={localdir_raw}")

        # Get the history from S3
        if remote_dataset_tar and fs.exists(remote_dataset_tar):
            get_history(remote_dataset_tar, localdir_raw, fs)

        # if fs.exists(remote_history_dir):
        #     fs.s3fs.get(remote_history_dir, localdir_raw, recursive=True)

        os.system(f"allure generate --output {localdir_rep} {localdir_raw}")

        # Upload report to S3
        # os.system(f"cd {localdir_rep} && tar -czf {report_tar} *")

        # fs.s3fs.put(f"{report_tar}", remote_dataset_tar)


if __name__ == "__main__":
    cli()
