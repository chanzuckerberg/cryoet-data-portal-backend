import json
import logging
import os
import re
import shutil
import sys
import traceback
from typing import List, Union

import click
import yaml
from ingestion_config_models_extended import ExtendedValidationContainer
from pydantic import ValidationError

ORIGINAL_DIR = os.getcwd()
THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__)) + "/"
ROOT_DIR = "../../../"
sys.path.append(THIS_FILE_DIR + ROOT_DIR)  # To import the helper function from common.py
from ingestion_tools.scripts.common.yaml_files import EXCLUDE_KEYWORDS_LIST, get_yaml_config_files  # noqa: E402

logger = logging.getLogger(__name__)
log_handler = logging.StreamHandler()
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)

DATASET_CONFIGS_DIR = THIS_FILE_DIR + "../../../ingestion_tools/dataset_configs/"
ERRORS_OUTPUT_DIR = THIS_FILE_DIR + "ingestion_config_validate_errors"
VALIDATION_EXCLUSIONS_FILE = THIS_FILE_DIR + "ingestion_config_validation_exclusions.json"

# The permitted parent attribute for formatted strings and its corresponding depth
# If the attribute has a parent attribute in this list, it is allowed to be a formatted string
# The key is the parent attribute and the value is the depth of the parent attribute (0 is at the root of the YAML file)
# E.g., any attribute that has a parent attribute of "sources" (where "sources" is one-level nested) is allowed to be a formatted string
PERMITTED_FORMATTED_STRINGS = {"tiltseries": 0, "tomograms": 0, "sources": 1}
FLOAT_FORMATTED_STRING_REGEX = r"^float\s*{[a-zA-Z0-9_-]+}\s*$"
INTEGER_FORMATTED_STRING_REGEX = r"^int\s*{[a-zA-Z0-9_-]+}\s*$"


def log_file_errors(filename: str, error: List[Union[ValidationError, Exception]]) -> None:
    """
    Log an error message to stdout.
    """
    logger.error('FAIL: "%s":', filename)
    for e in error:
        if not isinstance(e, dict) or any(key not in e for key in ["loc", "msg"]):
            logger.error("\t- error: %s", str(e))
        else:
            loc = ".".join([str(x) for x in e["loc"]])
            logger.error("\t- %s: %s", e["msg"], loc)


def replace_formatted_string(value: str) -> Union[str, bool, float, int]:
    """
    Replace formatted string with a placeholder value.
    """
    if "{" not in value or "}" not in value:
        return value

    # TODO: replace with actual formatted string values?
    elif re.match(FLOAT_FORMATTED_STRING_REGEX, value):
        return 1.0
    elif re.match(INTEGER_FORMATTED_STRING_REGEX, value):
        return 1
    return value


def replace_formatted_strings(config_data: dict, depth: int, permitted_parent: bool) -> dict:
    """
    Recursively iterate through a dictionary (YAML config file) and replace formatted strings with placeholder values.
    Modifies the dictionary in-place.

    Args:
        config_data (dict): The dictionary to iterate through
        depth (int): The depth of the current dictionary (0 is at the root of the YAML file)
        permitted_parent (bool): Whether the current parent attribute is permitted to have formatted strings
            - A write-once flag that is set to True if the current parent attribute is in the PERMITTED_FORMATTED_STRINGS list
    """
    for key, value in config_data.items():
        curr_permitted_parent = permitted_parent or (
            key in PERMITTED_FORMATTED_STRINGS and depth == PERMITTED_FORMATTED_STRINGS[key]
        )

        if isinstance(value, dict):
            config_data[key] = replace_formatted_strings(value, depth + 1, curr_permitted_parent)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    value[i] = replace_formatted_strings(item, depth + 1, curr_permitted_parent)
                elif isinstance(item, str) and curr_permitted_parent:
                    value[i] = replace_formatted_string(item)
        elif isinstance(value, str) and curr_permitted_parent:
            config_data[key] = replace_formatted_string(value)

    return config_data


@click.command()
@click.argument("input-files", type=str, nargs=-1)
@click.option(
    "--input-dir",
    type=str,
    help="Directory containing ingestion config files to validate. Use this OR provide input files, not both.",
)
@click.option(
    "--include-glob",
    type=str,
    default=None,
    help="Include only files that match the given glob pattern, can be used for both --input-dir and input files.",
)
@click.option(
    "--exclude-keywords",
    type=str,
    default=EXCLUDE_KEYWORDS_LIST,
    multiple=True,
    help="Exclude files that contain the following keywords in the filename, can be used for both --input-dir and input files.",
)
@click.option(
    "--validation-exclusions-file",
    type=str,
    default=VALIDATION_EXCLUSIONS_FILE,
    help="Path to the validation exclusions file containing class-field-value mappings to ignore during validation. See docs for more information.",
)
@click.option(
    "--output-dir",
    type=str,
    default=ERRORS_OUTPUT_DIR,
    help="Output directory for validation errors",
)
@click.option(
    "--network-validation",
    is_flag=True,
    help="Run extended network validation with HTTPS requests to verify data",
)
@click.option("--verbose", is_flag=True, help="Print verbose output")
def main(
    input_files: str,
    input_dir: str,
    include_glob: str,
    exclude_keywords: list[str],
    validation_exclusions_file: str,
    output_dir: str,
    network_validation: bool,
    verbose: bool,
):
    """
    See schema/ingestion_config/latest/docs/ingestion_config_validate.md for more information.
    """
    if verbose:
        logger.setLevel(logging.DEBUG)

    if input_files and input_dir:
        logger.error("Provide input files or --input-dir, not both.")
        exit(1)

    # if input files are relative paths, make them absolute
    if input_files:
        input_files = [os.path.join(ORIGINAL_DIR, file) if not os.path.isabs(file) else file for file in input_files]

    files_to_validate = get_yaml_config_files(
        input_files=input_files,
        include_glob=include_glob,
        exclude_keywords_list=exclude_keywords,
        dataset_configs_dir=input_dir,
        verbose=verbose,
        logger_name=__name__,
    )

    if not files_to_validate:
        logger.warning("No files to validate.")
        return

    with open(validation_exclusions_file, "r") as f:
        validation_exclusions = json.load(f)
    logger.info("Using validation exclusions file: %s", validation_exclusions_file)

    if output_dir[-1] != "/":
        output_dir += "/"
    # Remove existing dir
    if os.path.exists(output_dir):
        logger.warning("Removing existing %s directory.", output_dir)
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Run validation and save output
    validation_succeeded = True
    errors = {}
    files_to_validate = sorted(files_to_validate)
    for file in files_to_validate:
        try:
            with open(file, "r") as stream:
                logger.debug("Validating %s", file)
                config_data = yaml.safe_load(stream)
                # TODO: Remove this once issue below is fixed
                # Being done because "any_of" doesn't work on LinkML right now (so we can't support both
                # formatted strings and the base type in the same field)
                # https://github.com/linkml/linkml/issues/1521
                config_data = replace_formatted_strings(config_data, 0, False)
                ExtendedValidationContainer(
                    **config_data,
                    network_validation=network_validation,
                    validation_exclusions=validation_exclusions,
                    logger_name=__name__,
                )
        except ValidationError as e:
            validation_succeeded = False
            # Get all errors and convert them to strings
            errors[file] = e.errors()
            log_file_errors(file, errors[file])

        except Exception as exc:
            validation_succeeded = False
            errors[file] = [exc, traceback.format_exc()]
            log_file_errors(file, errors[file])

    if validation_succeeded:
        logger.info("Success: All files passed validation.")
        return

    # Write all errors to a file
    with open(os.path.join(output_dir, "ingestion_config_validate_errors.json"), "w") as f:
        json.dump(dict(sorted(errors.items())), f, indent=2, default=str)

    logger.error("Validation failed. See %s for errors.", output_dir)
    exit(1)


if __name__ == "__main__":
    main()
