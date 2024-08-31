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
@click.option("--datasets", required=False, type=str, default=None, help="Comma separated list of dataset IDs.")
@click.option("--save-history/--no-save-history", default=True, help="Save the history of the report.")
@click.option(
    "--extra-args",
    required=False,
    type=str,
    default=None,
    help="Extra arguments to pass to pytest (in one string).",
)
def main(
    local_dst: str,
    bucket: str,
    output_bucket: str,
    datasets: str | None,
    save_history: bool,
    extra_args: str | None,
):
    fs: S3Filesystem = FileSystemApi.get_fs_api(mode="s3", force_overwrite=False)
    now = datetime.datetime.now().isoformat(sep="_", timespec="seconds").replace(":", "-")

    if datasets is None:
        datasets = fs.glob(f"s3://{bucket}/*")
        datasets = [os.path.basename(dataset) for dataset in datasets if os.path.basename(dataset).isdigit()]
    else:
        datasets = datasets.split(",")

    extra_args = extra_args if extra_args else ""

    for dataset in datasets:
        # Accumulate test results here
        localdir_raw = f"{local_dst}/{dataset}_raw/{now}"
        # Generate report here
        localdir_rep = f"{local_dst}/{dataset}/{now}"
        # Archive location
        local_tar = f"{local_dst}/{dataset}/{dataset}_{now}.tar.gz"

        os.makedirs(localdir_raw, exist_ok=True)
        os.makedirs(localdir_rep, exist_ok=True)

        # Run tests and generate results
        os.system(f"pytest -n auto --dist worksteal --dataset {dataset} --alluredir {localdir_raw} {extra_args}")

        # Get the history from S3 (Must do this before generating the report)
        remote_dataset_dir = f"{output_bucket}/data_validation/{dataset}"
        remote_dataset_tar = f"{remote_dataset_dir}/{dataset}.tar.gz"
        fs.makedirs(remote_dataset_dir)

        if fs.exists(remote_dataset_tar):
            get_history(remote_dataset_tar, localdir_raw, fs)

        # Generate the report
        os.system(f"allure generate --output {localdir_rep} {localdir_raw}")

        # Upload the new report
        if save_history:
            os.system(f"tar -czf {local_tar} -C {localdir_rep} .")
            fs.s3fs.put(local_tar, remote_dataset_tar)
            os.system(f"rm -rf {local_tar}")


if __name__ == "__main__":
    main()
