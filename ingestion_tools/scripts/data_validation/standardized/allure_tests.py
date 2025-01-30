import os
import sys

import click

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CURRENT_DIR, "..", ".."))

from common.fs import FileSystemApi, S3Filesystem  # noqa: E402
from data_validation.shared.allure_runner import common_options, execute_allure_tests, update_with_default  # noqa: E402

STAGING_BUCKET = "cryoet-data-portal-staging"
DEFAULT_OVERRIDES = {
    "output_dir": "data_validation",
    "input_bucket": STAGING_BUCKET,
}


@click.command()
@click.option("--datasets", default="*", type=str, help="Comma separated list of dataset IDs.")
@common_options
def main(
    datasets: str | None,
    **kwargs,
):
    fs: S3Filesystem = FileSystemApi.get_fs_api(mode="s3", force_overwrite=False)

    if datasets is None:
        datasets = fs.glob(f"s3://{kwargs['input_bucket']}/*")
        datasets = [os.path.basename(dataset) for dataset in datasets if os.path.basename(dataset).isdigit()]
    else:
        datasets = datasets.split(",")

    datasets = sorted(datasets, key=lambda x: int(x))

    # If we are not saving history, we can run all datasets in one go (individual dataset runs don't need to be tracked)
    if not kwargs["history"]:
        datasets = [",".join(datasets)]

    updated_kwargs = update_with_default(kwargs, DEFAULT_OVERRIDES)
    for dataset in datasets:
        additional_parameters = [
            f"--datasets {dataset}",
            f"--bucket {kwargs['input_bucket']}",
        ]

        execute_allure_tests(
            identifier_name=dataset,
            additional_parameters=additional_parameters,
            default_overrides=DEFAULT_OVERRIDES,
            **updated_kwargs,
        )


if __name__ == "__main__":
    main()
