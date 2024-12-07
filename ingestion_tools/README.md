# Ingestion utilities

This package contains ingestion scripts, libraries, and configurations for converting raw research datasets into a format compatible with the CryoET Data Portal.


## Setting up your local python environment

To set up your local python environment for ingestion tools, follow these steps:

### Install poetry
The dependencies are managed using [poetry](https://python-poetry.org/). Install poetry if you don't have it already.

```bash
# Activate a python virtualenv
python3 -m venv $VENV_PATH

# Install pip and setuptools
$VENV_PATH/bin/pip install -U pip setuptools

# Install poetry
pip install poetry
```
### Ensuring your python version is compatible with the project

To ensure that your python version is compatible with the project, you can check the python version in the pyproject.toml file.

You can use pyenv or similar tools to manage your python versions.


### Initialize your shell and install dependencies

Poetry provides an easy way to create a virtual environment with shell and install your dependencies. This ensures that same versions of the dependencies are used across different environments, as all the dependencies are tracked in the poetry.lock file.

```bash
# Make the ingestion_tools your working directory
cd ingestion_tools
# Initialize the poetry shell
poetry shell
# Install the dependencies
poetry install
```

**Note:** If you have multiple python versions, look at the guide [here](https://python-poetry.org/docs/managing-environments/) to configure your poetry environment to use a compatible python version.
