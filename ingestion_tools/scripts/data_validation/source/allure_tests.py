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
    config_name = os.path.basename(ingestion_config).split(".")[0]
    updated_kwargs = update_with_default(kwargs, DEFAULT_OVERRIDES)
    additional_parameters = [
        f"--input-bucket {updated_kwargs['input_bucket']}",
        f"--ingestion-config {ingestion_config}",
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
