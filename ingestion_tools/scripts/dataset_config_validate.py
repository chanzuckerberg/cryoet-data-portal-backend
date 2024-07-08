import click
import os
import re
import subprocess
import shutil

SCHEMA_VERSION = "v1.1.0"
DATASET_CONFIGS_DIR = "../dataset_configs/"
DATASET_CONFIG_VALIDATION_FILE = f"../../schema/{SCHEMA_VERSION}/dataset_config_validate.yaml"
ERRORS_OUTPUT_DIR = "./dataset_config_validate_errors"
EXCLUDE_LIST = ["template.yaml", "dataset_config_merged.yaml"]
EXCLUDE_KEYWORDS = ["draft"]
YAML_EXTENSIONS = ('.yaml', '.yml')

@click.command()
@click.option(
    "--include-glob",
    type=str,
    default=None,
    help="Include only files that match the given glob pattern",
)
def main(include_glob):
    if not os.path.isfile(DATASET_CONFIG_VALIDATION_FILE):
        print(f"[ERROR]: Validation not found: {DATASET_CONFIG_VALIDATION_FILE}")
        exit(1)

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
        if any(keyword in filename for keyword in EXCLUDE_KEYWORDS):
            print(f"[INFO]: Excluding {file} because it contains an exclude keyword")
            continue
        files_to_validate.append(file)

    # Filter files based on the include
    if include_glob:
        print(f"[INFO]: Filtering files based on include glob: {include_glob}")
        files_to_validate = [file for file in files_to_validate if re.search(include_glob, file)]

    if files_to_validate:
        # Remove existing dir
        if os.path.exists(ERRORS_OUTPUT_DIR):
            print(f"[WARNING]: Removing existing {ERRORS_OUTPUT_DIR} directory.")
            shutil.rmtree(ERRORS_OUTPUT_DIR)
        os.makedirs(ERRORS_OUTPUT_DIR, exist_ok=True)

        # Run validation and save output
        result = subprocess.run(
            ["linkml-validate", "-s", DATASET_CONFIG_VALIDATION_FILE] + files_to_validate,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        with open(os.path.join(ERRORS_OUTPUT_DIR, "dataset_config_validate_errors.txt"), "wb") as f:
            f.write(result.stdout + result.stderr)
        
        if result.returncode == 0:
            print("[SUCCESS]: All files passed validation.")
        else:
            with open(os.path.join(ERRORS_OUTPUT_DIR, "dataset_config_validate_errors.txt"), "r") as f:
                errors = f.readlines()

            # Filter out file paths and sort errors
            filtered_errors = []
            for error in errors:
                error = error.split('] ')[2:]
                error = '] '.join(error)
                error = error.rsplit(' in /', 1)[0]  # Remove context after "in /"
                filtered_errors.append(error)
            filtered_errors = sorted(set(filtered_errors))

            with open(os.path.join(ERRORS_OUTPUT_DIR, "dataset_config_validate_errors_filtered.txt"), "w") as f:
                f.write("\n".join(filtered_errors))
            
            print("[ERROR]: Validation failed. See dataset_config_validate_errors.txt for details.")
            exit(1)
    else:
        print("[WARNING]: No files to validate.")

if __name__ == "__main__":
    main()