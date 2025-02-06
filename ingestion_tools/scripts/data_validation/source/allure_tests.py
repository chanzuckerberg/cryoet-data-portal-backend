import os
import sys

import click

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CURRENT_DIR, "..", ".."))

from importers.utils import IMPORTERS  # noqa: E402

from data_validation.shared.allure_runner import common_options, execute_allure_tests, update_with_default  # noqa: E402

DEFAULT_OVERRIDES = {
    "output_dir": "source_validation",
}


def filter_options(func):
    options = []
    for cls in IMPORTERS:
        importer_key = cls.type_key.replace("_", "-")
        options.append(
            click.option(
                f"--filter-{importer_key}-name",
                type=str,
                default=None,
                help=f"Filter pattern for {importer_key}",
            ),
        )
    for option in options:
        func = option(func)
    return func


def generate_filters(kwargs) -> str:
    filters = []
    for cls in IMPORTERS:
        importer_key = cls.type_key.replace("_", "-")
        if value := kwargs.get(f"filter_{importer_key}_name"):
            filters.append(f"--filter-{importer_key}-name {value}")
    return " ".join(filters) if filters else ""


def validate_config_path(path: str) -> str:
    if os.path.exists(path):
        return path

    directory_path = os.path.dirname(os.path.abspath(path))
    expected_directory_path = os.path.abspath(os.path.join(os.getcwd(), "..", "..", "..", "dataset_configs"))
    if os.path.basename(directory_path) == "dataset_configs" and directory_path != expected_directory_path:
        new_path = os.path.join(expected_directory_path, os.path.basename(path))
        print(f"Updating the path from {path} to {new_path}")
        return new_path
    raise RuntimeError(f"{os.path.basename(path)} does not exist in {os.path.abspath(path)}")


@click.command()
@click.option(
    "--ingestion-config",
    type=str,
    help="Path to the ingestion config file.",
)
@common_options
@filter_options
def main(
    ingestion_config: str,
    **kwargs,
):
    config_path = validate_config_path(ingestion_config)
    config_name = os.path.basename(config_path).split(".")[0]
    updated_kwargs = update_with_default(kwargs, DEFAULT_OVERRIDES)
    additional_parameters = [
        f"--input-bucket {updated_kwargs['input_bucket']}",
        f"--ingestion-config {config_path}",
        generate_filters(kwargs),
    ]

    execute_allure_tests(
        identifier_name=config_name,
        additional_parameters=additional_parameters,
        default_overrides=DEFAULT_OVERRIDES,
        **updated_kwargs,
    )


if __name__ == "__main__":
    main()
