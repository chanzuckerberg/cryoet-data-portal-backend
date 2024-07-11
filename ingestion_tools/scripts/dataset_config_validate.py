import json
import os
import re
import shutil
import sys
from typing import Union

import click
import yaml
from pydantic import ValidationError

from common.yaml_files import get_yaml_config_files

SCHEMA_VERSION = "v1.1.0"
DATASET_CONFIGS_MODELS_DIR = f"../../schema/{SCHEMA_VERSION}/"

sys.path.append(DATASET_CONFIGS_MODELS_DIR)  # To import the Pydantic-generated dataset models

from dataset_config_models import Container  # noqa: E402

DATASET_CONFIGS_DIR = "../dataset_configs/"
ERRORS_OUTPUT_DIR = "./dataset_config_validate_errors"
# files to exclude from validation
EXCLUDE_LIST = ["template.yaml", "dataset_config_merged.yaml"]
# exclude files that contain any of the following keywords
EXCLUDE_KEYWORDS = "draft"
YAML_EXTENSIONS = (".yaml", ".yml")

# The permitted parent attribute for formatted strings and its corresponding depth
# If the attribute has a parent attribute in this list, it is allowed to be a formatted string
# The key is the parent attribute and the value is the depth of the parent attribute (0 is at the root of the YAML file)
# E.g., any attribute that has a parent attribute of "sources" (where "sources" is one-level nested) is allowed to be a formatted string
PERMITTED_FORMATTED_STRINGS = {"tiltseries": 0, "tomograms": 0, "sources": 1}
BOOLEAN_FORMATTED_STRING_REGEX = r"^bool\s*{[a-zA-Z0-9_-]+}\s*$"
FLOAT_FORMATTED_STRING_REGEX = r"^float\s*{[a-zA-Z0-9_-]+}\s*$"
INTEGER_FORMATTED_STRING_REGEX = r"^int\s*{[a-zA-Z0-9_-]+}\s*$"


def _error_to_filtered_text(error_value: Union[dict, str]) -> str:
    """
    Convert an error value to a filtered text string (for easier comparison and filtering of errors)
    """
    if not isinstance(error_value, dict) or any(key not in error_value for key in ["loc", "msg", "input"]):
        return str(error_value)
    loc = "/".join([str(x) for x in error_value["loc"]])
    return f"{loc}: {error_value['msg']} (Input: {error_value['input']})"


def _error_to_filtered_2_text(error_value: Union[dict, str]) -> str:
    """
    Convert an error value to a filtered text string (for easier comparison and filtering of errors)
    This one removes more attributes from the error value, so that the errors list can be filtered down even more.
    """
    if not isinstance(error_value, dict) or any(key not in error_value for key in ["loc", "msg"]):
        return str(error_value)
    return str(error_value["loc"][-1]) + ": " + str(error_value["msg"])


def replace_formatted_string(value: str) -> Union[str, bool, float, int]:
    """
    Replace formatted string with a placeholder value.
    """
    if "{" not in value or "}" not in value:
        return value

    # TODO: replace with actual formatted string values?
    if re.match(BOOLEAN_FORMATTED_STRING_REGEX, value):
        return False
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
@click.option(
    "--include-glob",
    type=str,
    default=None,
    help="Include only files that match the given glob pattern",
)
@click.option(
    "--exclude-keywords",
    type=str,
    default=EXCLUDE_KEYWORDS,
    help="Exclude files that are in the given comma-separated list",
)
def main(include_glob: str, exclude_keywords: str):
    files_to_validate = get_yaml_config_files(include_glob, exclude_keywords)

    if not files_to_validate:
        print("[WARNING]: No files to validate.")
        return

    # Remove existing dir
    if os.path.exists(ERRORS_OUTPUT_DIR):
        print(f"[WARNING]: Removing existing {ERRORS_OUTPUT_DIR} directory.")
        shutil.rmtree(ERRORS_OUTPUT_DIR)
    os.makedirs(ERRORS_OUTPUT_DIR, exist_ok=True)

    # Run validation and save output
    validation_succeeded = True
    errors = {}
    for file in files_to_validate:
        try:
            with open(file, "r") as stream:
                config_data = yaml.safe_load(stream)
                # TODO: Remove this once issue below is fixed
                # Being done because "any_of" doesn't work on LinkML right now (so we can't support both
                # formatted strings and the base type in the same field)
                # https://github.com/linkml/linkml/issues/1521
                # Note: currently not using right now, since we have a semi-fix that gives us 
                # better validation (although not perfect) for now
                # config_data = replace_formatted_strings(config_data, 0, False)
                Container(**config_data)
        except ValidationError as e:
            validation_succeeded = False
            # Get all errors and convert them to strings
            errors[file] = e.errors()

        except Exception as exc:
            errors[file] = [exc]

    if validation_succeeded:
        print("[SUCCESS]: All files passed validation.")
        return

    # Write all errors to a file
    with open(os.path.join(ERRORS_OUTPUT_DIR, "dataset_config_validate_errors.json"), "w") as f:
        json.dump(dict(sorted(errors.items())), f, indent=2, default=str)

    errors_as_one_list = [error for error_list in errors.values() for error in error_list]

    # Write a filtered list of errors to a file
    with open(os.path.join(ERRORS_OUTPUT_DIR, "dataset_config_validate_errors_filtered.txt"), "w") as f:
        errors_as_filtered_text = map(_error_to_filtered_text, errors_as_one_list)
        errors_list = list(set(errors_as_filtered_text))
        errors_list.sort()
        f.write("\n".join(errors_list))

    # Write an even more filtered list of errors to a file
    with open(os.path.join(ERRORS_OUTPUT_DIR, "dataset_config_validate_errors_filtered_2.txt"), "w") as f:
        errors_as_filtered_2_text = map(_error_to_filtered_2_text, errors_as_one_list)
        errors_list = list(set(errors_as_filtered_2_text))
        errors_list.sort()
        f.write("\n".join(errors_list))

    print("[ERROR]: Validation failed. See dataset_config_validate_errors.json for details.")
    exit(1)


if __name__ == "__main__":
    main()
