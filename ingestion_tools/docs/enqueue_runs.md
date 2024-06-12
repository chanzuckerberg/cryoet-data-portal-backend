
# enqueue_runs.py
This script enables us to run dataset ingestions and db ingestions quickly. Its interface is very similar to the `standardize_dirs.py` script, because it's a wrapper around that script, that breaks down a larger ingestion job into per-run chunks, and queues each of those per-run chunks of work into a batch processing system.

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

## File ingestion (`queue` subcommand)

The `enqueue_runs.py queue` queues up dataset ingestion work to read data from the raw form uploaded by dataset submitters, to the formats expected by the data portal. It launches one task per **run**.

### tl;dr:
```bash
cd ingestion_tools/scripts

# Activate a python virtualenv
source ../.venv/bin/activate

# Set up any required AWS env vars
EXPORT AWS_PROFILE=cryoet-dev

# Main args
# python3 enqueue_runs.py queue [path to dataset config] [source bucket] [destination bucket] [--stuff-to-import]

# Get information on what types of stuff we can import
python3 enqueue_runs.py queue --help

# Example
python3 enqueue_runs.py queue dataset_configs/10000.yaml cryoetportal-rawdatasets-dev cryoetportal-output-test --import-everything
```


### Required arguments

| Argument | Explanation |
| --- | --- |
| CONFIG_FILE | This is the path (relative to $CWD) to the dataset ingestion config file, e.g `dataset_configs/10001.yaml` |
| INPUT_BUCKET | Name of the bucket where the deposited data lives (this is usally `cryoetportal-rawdatasets-dev`) |
| OUTPUT_PATH | Output bucket and/or optional prefix for where the transformed data should be written. This is usually `cryoet-data-portal-staging` when ingesting data, but for testing, something like `cryoetportal-output-test/mytestprefix` is common |

### Commonly used options
| Option | Default | Explanation |
| --- | --- | -- |
| --ecr-tag | main | If you're experimenting with code/config changes, you may have pushed a docker image to the image registry with a different tag, such as `my_name_here`. Use this flag to tell the workers to use the image with this tag to process the dataset. |
| --memory | 24000 | This script creates one job for each `run` found by the script. If some runs have very large tomograms, it may be necessary to increase the amount of memory allocated to each job |
| --import-everything | | If this flag is passed in, the script will attempt to ingest all data specified in the dataset config, (datasets, runs, annotations, etc etc) |

### Other interesting options to be aware of
| Option | Default | Explanation |
| --- | --- | -- |
| --filter-{type}-name | null | If you only want to import a particular run or voxel spacing, you can filter which objects are ingested by specifying this option with a regular expression that matches the object's name. This option can be specified multiple times with multiple regular expressions |
| --exclude-{type}-name | null | If you want to **exclude** a particular run or voxel spacing, you can filter which objects are ingested by specifying this option with a regular expression that matches the object's name. This option can be specified multiple times with multiple regular expressions |

## Database ingestion (`db-import` subcommand)

The `enqueue_runs.py db-import` queues up jobs to read data from S3 and import into the database, making data available via the API. It launches one task per **dataset** and by default it will import **all datasets** unless filters or a list of specific datasets to import are provided.

### tl;dr:
```bash
cd ingestion_tools/scripts

# Activate a python virtualenv
source ../.venv/bin/activate

# Set up any required AWS env vars
EXPORT AWS_PROFILE=cryoet-dev

# Main args
# python3 enqueue_runs.py db-import [--stuff-to-import]

# Get information on what types of stuff we can import
python3 enqueue_runs.py db-import --help

# Staging Example
python3 enqueue_runs.py db-import --import-everything --include-dataset 10001 --include-dataset 10002

# Prod example
export AWS_PROFILE=cryoet-prod
python3 enqueue_runs.py db-import --environment prod --import-annotation-authors --filter-datasets '.000[12]'

```


### Commonly used options
| Option | Default | Explanation |
| --- | --- | -- |
| --environment | staging | Whether to import data into the `staging` (default) or `prod` database/api |
| --s3-bucket | `cryoet-data-portal-staging` in staging, or `cryoet-data-portal-public` in prod | Which S3 bucket to read files and metadata from |
| --https-prefix | `https://files.cryoet.staging.si.czi.technology` in staging or `https://files.cryoetdataportal.cziscience.com` in prod | This is the https protocol and domain that will be prefixed to all file paths. It's used to generate the https url's for files referenced by the api |
| --ecr-tag | main | If you're experimenting with code/config changes, you may have pushed a docker image to the image registry with a different tag, such as `my_name_here`. Use this flag to tell the workers to use the image with this tag to process the dataset. |
| --import-everything | | If this flag is passed in, the script will attempt to ingest all data specified in the dataset config, (datasets, runs, annotations, etc etc) |

### Other interesting options to be aware of
| Option | Default | Explanation |
| --- | --- | -- |
| --filter-datasets | null | Supply a regular expression to apply to the list of available dataset ID's, to only run import for certain datasets. This option can be specified multiple times with multiple regular expressions |
| --include-datasets | null | Specify specific datasets to import. This option can be specified multiple times with multiple dataset id's |
| --s3-prefix | null | Only look for datasets in a particular subdirectory (this is faster than the filter/include filters) when importing a single dataset |


## Building and pushing up a dev/test image:

### To build and push an image to ECR with a dev/test tag:
```bash
# From the root of the repo
make push-local-ingestor-build tag=my-test-tag-name
```
