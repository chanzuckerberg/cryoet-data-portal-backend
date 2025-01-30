import os
import sys

import click

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CURRENT_DIR, "..", ".."))

from data_validation.shared.allure_runner import common_options, execute_allure_tests, update_with_default  # noqa: E402

DEFAULT_OVERRIDES = {
    "output_dir": "source_validation",
}


@click.command()
@click.option(
    "--ingestion-config",
    type=str,
    help="Path to the ingestion config file.",
)
@common_options
def main(
    ingestion_config: str,
    **kwargs,
):
    config_name = os.path.basename(ingestion_config).split(".")[0]
    updated_kwargs = update_with_default(kwargs, DEFAULT_OVERRIDES)
    additional_parameters = [
        f"--input-bucket {updated_kwargs['input_bucket']}",
        f"--ingestion-config {ingestion_config}",
    ]

    execute_allure_tests(
        identifier_name=config_name,
        additional_parameters=additional_parameters,
        default_overrides=DEFAULT_OVERRIDES,
        **updated_kwargs,
    )


if __name__ == "__main__":
    main()
