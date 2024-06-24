#!/bin/bash
# Validate all YAML files in the current directory and subdirectories
# TODO: pull from config-attribute-discovery.py?
if [ ! -f validate.yaml ]; then
    echo "No validate.yaml file found. Skipping validation."
    exit 0
fi

exclude_list=("validate.yaml" "template.yaml" "template_draft.yaml" "config-attribute-discovery-output.yaml")

all_files=$(find . -type f \( -name "*.yaml" -o -name "*.yml" \))

files_to_validate=()
for file in $all_files; {
    filename=$(basename "$file")
    if [[ ! " ${exclude_list[@]} " =~ " ${filename} " ]]; then
        files_to_validate+=("$file")
    fi
}

# Run linkml-validate if there are files to validate
if [ ${#files_to_validate[@]} -gt 0 ]; then
    if linkml-validate -s validate.yaml "${files_to_validate[@]}" ; then
        echo "All files passed validation."
    else
        exit 1
    fi
else
    echo "No files to validate based on the whitelist."
fi