
# ingestion_config_validate.py
This script enables us to run ingestion config validation checks on all (or a glob-specified) set of ingestion config files. It will output the full set of validation errors to `schema/ingestion_config/latest/ingestion_config_validate_errors`, while outputting a summary of the errors to stdout.

## One-time Setup
Make sure you have at least python 3.11 installed. If you need to work with multiple versions of python, [pyenv](https://github.com/pyenv/pyenv) can help with that.

Before running the script, ensure all the required packages are installed in a virtualenv:
```bash
cd schema/
python3 -m venv .venv  # create a virtualenv
source .venv/bin/activate  # activate the virtualenv
python3 -m pip install poetry  # Install the poetry package manager
poetry install  # Use poetry to install this package's dependencies
cd ../ingestion_tools/  # Move to the ingestion_tools directory
poetry install  # Use poetry to install this package's dependencies
```

## Running the script

To run the script, you can use the following command, from the `schema/ingestion_config/latest/` directory:
```bash
python ingestion_config_validate.py [OPTIONS] [INPUT_FILES]
```

## Command Line Options
This script supports several command line options that allow for selective validation:

### `INPUT_FILES`
A non-option argument that specifies the ingestion configuration files to validate. If no files are specified, all ingestion configuration files in the specified `--input-dir` will be validated (or all files in the default directory if no `--input-dir` is specified).

### `--help`
Shows the help message with all available options.

### `--input-dir`
Specifies the directory where all ingestion configuration files are stored. The default is `ingestion_tools/dataset_configs/`.

### `--include-glob`
Specifies a glob pattern to include only specific files for validation. This option is helpful when you want to validate a subset of all available YAML configuration files. Note that only YAML files are considered for validation, regardless of this option.

Example:
```bash
python ingestion_config_validate.py --include-glob ".*104[0-9]{2}.*"
```

### `--exclude-keywords`
Exclude files that contain the following keywords in the filename. Repeat the flag for multiple keywords. By default, any file containing "draft" will be excluded. Note that this exclude option takes superiority over the include option.

Example:
```bash
python ingestion_config_validate.py --exclude-keywords "draft" --exclude-keywords "test"
```

### `--validation-exclusions-file`
A JSON file specifying which class-field-value mappings do not need to be validated when running Pydantic **extended validation**. Note that requirement / pattern / enum / type validation will still be performed.

**Currently only supports skipping ontology object validation (ingestion config fields: annotation_object, cell_component, cell_strain, cell_type, organism, tissue)**. This option is useful when you want to skip certain fields that intentionally fail validation. For example, sometimes validation doesn't want to be run on the name of a cell_strain, as it may not be what the cell strain's id corresponds to online.

JSON file format (note that the `ClassNameToSkipOn` is the class name in the `schema/latest/codegen/ingestion_config_models.py`, which may be different from the class name in the ingestion configuration file):
```json
{
    "ClassNameToSkipOn": {
        "field_name_to_skip_on1": ["field_value_to_skip1", "field_value_to_skip2"]
        "field_name_to_skip_on2": ["field_value_to_skip3", ...],
        ...
    },
    "AnotherClassNameToSkipOn": {
        ...
    },
    ...
}
```

Example file:
```json
{
    "AnnotationObject": {
        "id": ["GO:0030992", "GO:0035869"],
        "name": []
    },
    "CellType": {
        "id": [],
        "name": ["umbilical vein endothelial cell"]
    }
}
```

### `--output-dir`
Sets the directory where all validation errors will be saved. The default is `./ingestion_config_validate_errors`, and the directory will be recreated at each script run, removing previous contents.

### `--network-validation`
Enables network validation, which checks for the existence of all referenced files in the ingestion configuration files by sending HTTPS requests to relevant APIs. This option is disabled by default and increases the runtime of the script considerably.

### `--verbose`
Enables verbose output, showing all validation errors for each ingestion configuration file.
