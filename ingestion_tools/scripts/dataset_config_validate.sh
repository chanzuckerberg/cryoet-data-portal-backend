#!/bin/bash
# Validate all YAML files in the current directory and subdirectories

readonly SCHEMA_VERSION="v1.1.0"
readonly DATASET_CONFIGS_DIR=../dataset_configs/
readonly DATASET_CONFIG_VALIDATION_FILE="../../schema/$SCHEMA_VERSION/dataset_config_validate.yaml"
readonly ERRORS_OUTPUT_DIR=./dataset_config_validate_errors
readonly EXCLUDE_LIST=("template.yaml" "dataset_config_merged.yaml")
readonly EXCLUDE_KEYWORDS=("draft")

if [ ! -f $DATASET_CONFIG_VALIDATION_FILE ]; then
    echo "No validate.yaml file found. Skipping validation."
    exit 0
fi


all_files=$(find $DATASET_CONFIGS_DIR -type f \( -name "*.yaml" -o -name "*.yml" \))

# Filter out files in the exclude list and files with exclude keywords
files_to_validate=()
for file in $all_files; {
    filename=$(basename "$file")
    if [[ " ${EXCLUDE_LIST[@]} " =~ " ${filename} " ]]; then
        continue
    fi
    for keyword in "${EXCLUDE_KEYWORDS[@]}"; {
        if [[ $filename == *"$keyword"* ]]; then
            echo "Excluding $file because it contains the keyword $keyword"
            break
        fi
    }
    files_to_validate+=("$file")
}

# Run linkml-validate if there are files to validate
if [ ${#files_to_validate[@]} -gt 0 ]; then
    rm -rf $ERRORS_OUTPUT_DIR
    mkdir -p $ERRORS_OUTPUT_DIR
    if linkml-validate -s $DATASET_CONFIG_VALIDATION_FILE "${files_to_validate[@]}" > $ERRORS_OUTPUT_DIR/dataset_config_validate_errors.txt ; then
        echo "All files passed validation."
    else
        # Filter out the error message that includes the file path to get a more concise error log file (losing some context, but easier to read)
        sed -e 's/\[ERROR\] [\[\.\/a-zA-Z0-9_]*\] //g' $ERRORS_OUTPUT_DIR/dataset_config_validate_errors.txt | sort -u > $ERRORS_OUTPUT_DIR/dataset_config_validate_errors_filtered.txt 
        # Filter again, losing more context but getting a more concise error log file
        sed -e 's/ in \/[a-z]*\/[0-9]*\/[a-zA-Z\/_0-9]*$//g' $ERRORS_OUTPUT_DIR/dataset_config_validate_errors_filtered.txt | sort -u > $ERRORS_OUTPUT_DIR/dataset_config_validate_errors_filtered2.txt 
        echo "Validation failed. See dataset_config_validate_errors.txt for details."
        exit 1
    fi
else
    echo "No files to validate based on the whitelist."
fi