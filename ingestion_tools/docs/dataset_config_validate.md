
# dataset_config_validate.py
This script enables us to run dataset config validation checks on all (or a glob-specified) set of dataset config files. It will output the full set of validation errors to `ingestion_tools/scripts/dataset_config_validate_errors`, while outputting a summary of the errors to stdout.

## One-time Setup
Make sure you have at least python 3.11 installed. If you need to work with multiple versions of python, [pyenv](https://github.com/pyenv/pyenv) can help with that.

Before running the script, ensure all the required packages are installed in a virtualenv:
```bash
cd ingestion_tools
python3 -m venv .venv  # create a virtualenv
source .venv/bin/activate  # activate the virtualenv
python3 -m pip install poetry  # Install the poetry package manager
poetry install  # Use poetry to install this package's dependencies
```

## Running the script

To run the script, you can use the following command, from the `ingestion_tools/scripts` directory:
```bash
python dataset_config_validate.py
```

## Command Line Options
This script supports several command line options that allow for selective validation:

`--help`: Shows the help message with all available options.

`--dataset-configs-dir`: Specifies the directory where all dataset configuration files are stored. The default is `../dataset_configs/`.

`--include-glob`: Specifies a glob pattern to include only specific files for validation. This option is helpful when you want to validate a subset of all available YAML configuration files. Note that only YAML files are considered for validation, regardless of this option.

Example:
```bash
python dataset_config_validate.py --include-glob ".*104[0-9]{2}.*"
```

`--exclude-keywords`: Allows excluding files containing specified keywords in their names, separated by commas. By default, any file containing "draft" will be excluded. Note that this exclude option is applied BEFORE the include option.

Example:
```bash
python dataset_config_validate.py --exclude-keywords "draft,old"
```

`--output-dir`: Sets the directory where all validation errors will be saved. The default is `./dataset_config_validate_errors`, and the directory will be recreated at each script run, removing previous contents.

`--verbose`: Enables verbose output, showing all validation errors for each dataset configuration file.