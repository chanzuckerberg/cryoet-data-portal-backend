import click
import json
import os
import re
import sys
import yaml
import shutil

SCHEMA_VERSION = "v1.1.0"
DATASET_CONFIGS_MODELS_DIR = f"../../schema/{SCHEMA_VERSION}/"

sys.path.append(DATASET_CONFIGS_MODELS_DIR) # To import the dataset models

from pydantic import ValidationError
from dataset_config_models import Container

DATASET_CONFIGS_DIR = "../dataset_configs/"
ERRORS_OUTPUT_DIR = "./dataset_config_validate_errors"
EXCLUDE_LIST = ["template.yaml", "dataset_config_merged.yaml"]
EXCLUDE_KEYWORDS = "draft"
YAML_EXTENSIONS = ('.yaml', '.yml')

# The permitted parent attribute for formatted strings and its corresponding depth
PERMITTED_FORMATTED_STRINGS = {"tiltseries": 0, "tomograms": 0, "sources": 1}
BOOLEAN_FORMATTED_STRING_REGEX = r"^bool\s*{[a-zA-Z0-9_-]+}\s*$"
FLOAT_FORMATTED_STRING_REGEX = r"^float\s*{[a-zA-Z0-9_-]+}\s*$"
INTEGER_FORMATTED_STRING_REGEX = r"^int\s*{[a-zA-Z0-9_-]+}\s*$"

def _error_to_filtered_text(error_value):
    loc = "/".join([str(x) for x in error_value["loc"]])
    return f"{loc}: {error_value['msg']} (Input: {error_value['input']})"

def _error_to_filtered_text(error_value):
    return f"{error_value["loc"][-1]}: {error_value['msg']}"

def get_files_to_validate(include_glob, exclude_keywords):
    exclude_keywords_list = exclude_keywords.split(",")
    if (exclude_keywords_list[0] != ""):
        print(f"[INFO]: Excluding files that contain any of the following keywords: {exclude_keywords_list}")
    else: 
        exclude_keywords_list = []

    # Get all YAML files in the dataset_configs directory
    all_files = []
    for root, _, files in os.walk(DATASET_CONFIGS_DIR):
        for file in files:
            if file.endswith(YAML_EXTENSIONS):
                all_files.append(os.path.join(root, file))

    #  Filter files based on the whitelist
    files_to_validate = []
    for file in all_files:
        filename = os.path.basename(file)
        if filename in EXCLUDE_LIST:
            continue
        if any(keyword in filename for keyword in exclude_keywords_list):
            print(f"[INFO]: Excluding {file} because it contains an exclude keyword")
            continue
        files_to_validate.append(file)

    # Filter files based on the include
    if include_glob:
        print(f"[INFO]: Filtering files based on include glob: {include_glob}")
        files_to_validate = [file for file in files_to_validate if re.search(include_glob, file)]

    return files_to_validate

def replace_formatted_string(key, value):
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

def replace_formatted_strings(config_data, depth, permitted_parent):
    for key, value in config_data.items():
        curr_permitted_parent = (permitted_parent or 
                                 (key in PERMITTED_FORMATTED_STRINGS and depth == PERMITTED_FORMATTED_STRINGS[key]))

        if isinstance(value, dict):
            config_data[key] = replace_formatted_strings(value, depth + 1, curr_permitted_parent)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    value[i] = replace_formatted_strings(item, depth + 1, curr_permitted_parent)
                elif isinstance(item, str):
                    if curr_permitted_parent:
                        value[i] = replace_formatted_string(key, item)
        elif isinstance(value, str):
            if curr_permitted_parent:
                config_data[key] = replace_formatted_string(key, value)
            
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
def main(include_glob, exclude_keywords):
    files_to_validate = get_files_to_validate(include_glob, exclude_keywords)

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
                config_data = replace_formatted_strings(config_data, 0, False)
                config = Container(**config_data)
        except ValidationError as e:
            validation_succeeded = False
            curr_errors = e.errors()
            for curr_error in curr_errors:
                if "ctx" in curr_error and "error" in curr_error["ctx"]:
                    curr_error["ctx"]["error"] = str(curr_error["ctx"]["error"])
            errors[file] = curr_errors
            
        except Exception as exc:
            raise exc
    
    if validation_succeeded:
        print("[SUCCESS]: All files passed validation.")
        return
    
    # Write all errors to a file
    with open(os.path.join(ERRORS_OUTPUT_DIR, "dataset_config_validate_errors.json"), "w") as f:
        json.dump(dict(sorted(errors.items())), f, indent=2)

    errors_as_one_list = [error for error_list in errors.values() for error in error_list]

    # Write a filtered list of errors to a file
    with open(os.path.join(ERRORS_OUTPUT_DIR, "dataset_config_validate_errors_filtered.txt"), "w") as f:
        errors_as_filtered_text = map(_error_to_filtered_text, errors_as_one_list)
        errors_list = list(set(errors_as_filtered_text))
        errors_list.sort()
        f.write("\n".join(errors_list))

    # Write an even more filtered list of errors to a file
    with open(os.path.join(ERRORS_OUTPUT_DIR, "dataset_config_validate_errors_filtered_2.txt"), "w") as f:
        errors_as_filtered_2_text = map(_error_to_filtered_text, errors_as_one_list)
        errors_list = list(set(errors_as_filtered_2_text))
        errors_list.sort()
        f.write("\n".join(errors_list))
    
    print("[ERROR]: Validation failed. See dataset_config_validate_errors.json for details.")
    exit(1)

if __name__ == "__main__":
    main()