# Ingestion utilities

This package contains scripts, libraries, and configurations for converting raw research datasets into a format compatible with the CryoET Data Portal. 


## Start here

If you're new to CryoET and the data ingestion process, here are some helpful resources to get you started:

- **Learn about CryoET**: Check out this [introductory guide to CryoET](https://chanzuckerberg.github.io/cryoet-data-portal/intro_cryoet.html#cryoet-intro)  to familiarize yourself with the project.

- **Set up your local Python environment**: Follow the instructions [here](https://github.com/chanzuckerberg/cryoet-data-portal-backend/tree/main/ingestion_tools#setting-up-your-local-python-environment) to set up your Python environment.

- **Run tests locally:** Find test instructions [here](./docs/running_tests.md).

- **Useful commands:** You’ll find a list of useful commands to help you get started [here](https://github.com/chanzuckerberg/cryoet-data-portal-backend/tree/main/ingestion_tools#useful-commands).

- **Directory structure**: The [directory_layout](./docs/directory_layout.md) documentation explains the folder structure.

- **Further documentation**: For additional documentation, check the [docs folder](./docs/)


## Setting Up Your Local Python Environment

### Prerequisites
- Python 3.11+ 


To set up your local python environment for ingestion tools, follow these steps:

### 1. Install poetry
The dependencies are managed using [poetry](https://python-poetry.org/). Install poetry if you don't have it already.

```bash
# Activate a python virtualenv
python3 -m venv $VENV_PATH

# Install pip and setuptools
$VENV_PATH/bin/pip install -U pip setuptools

# Install poetry
pip install poetry
```

### 2. Ensure Python Compatibility

To ensure that your python version is compatible with the project, you can check the python version in the pyproject.toml file.

You can use pyenv or similar tools to manage your python versions.


### 3. Initialize Your Environment and Install Dependencies

Poetry makes it easy to create a virtual environment and install dependencies. This ensures that the same versions of dependencies are used across different environments (tracked in the `poetry.lock` file).

```bash
# Make the ingestion_tools your working directory
cd ingestion_tools
# Initialize the poetry shell
poetry shell
# Install the dependencies
poetry install
```

**Note:** If you have multiple python versions, refer to [this guide](https://python-poetry.org/docs/managing-environments/) to configure Poetry to use the correct version.


## Useful Commands

There are make commands available to run the ingestor, tests for the ingestion, pushing the image to remote, etc. They require docker to run. 

### Setup Docker

If you don't already have docker setup, follow the instructions provided [here](https://www.docker.com/get-started/).

`docker compose` utility is needed to execute the make commands, as the local application requires multiple containers to run simultaneously. Learn more about docker compose [here](https://docs.docker.com/compose/). To install `docker compose` follow the instructions provided [here](https://docs.docker.com/compose/install/).

### Make Commands

| Command                                                                                 | Description                                                             |
|-----------------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| `make ingestor-init`                                                                    | Starts the container for ingestor locally along with required resource. |
| `make ingestor-test-s3`                                                                 | Runs unit tests for s3 ingestion.                                       |
| `make ingestor-test-db`                                                                 | Runs unit tests for db ingestion for api v1.                            |
| `AWS_PROFILE=<relevant-aws-profile> make push-local-ingestor-build tag=<tag-for-build>` | Builds and pushes image of ingestor to remote ECR.                      |
| `AWS_PROFILE=<relevant-aws-profile> make push-ingestor-build tag=<tag-for-build> region=<AWS-REGION>` | Pushes image of ingestor to remote ECR.                      |

