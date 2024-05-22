
# standardize_dirs.py
The `standardize_dirs.py` script runs locally, and reads both a source directory, and a deposition configuration file to figure out how to convert a deposition to the portal's output format, and writes the output to a local filesystem or S3 prefix.

## One-time Setup [docker]
This script is only supported on linux/x86 arch. That means if you're on OSX the preferred method of interacting with it for dev/testing is inside a docker container. If you're on linux and want to run it outside of a container, please see the setup instructions for the `enqueue_runs` script.

```bash
cd cryoet-data-portal-backend
make init  # Create a set of docker containers that mimics a prod environment
```

## Running inside a docker container
Typically local dev/testing is done with data that's been downloaded to a local fileystem, for better performance.

Don't forget to make sure there's some dev data available locally, this will help speed up tests!
```bash
aws s3 sync s3://some-bucket/some-path ingestion_tools/local_data/input_bucket/
```

To run the script inside a docker container against that data:
```bash
docker exec -ti cryoet-data-portal-backend-ingestor-1 bash
# Run the ingestion tool against the locally sync'd data
python3 standardize_dirs.py convert --local-fs ../dataset_configs/10002.yaml ../local_data/input_bucket ../local_data/output_bucket/ --import-key-images
```

## Running outside of a docker container

```bash
cd ingestion_tools/scripts

# Activate a python virtualenv
source ../.venv/bin/activate

# Set up any required AWS env vars
EXPORT AWS_PROFILE=cryoet-dev

# Main args
# python3 enqueue_runs.py queue [path to dataset config] [source bucket] [destination bucket] [--stuff-to-import]

# Get information on what types of stuff we can import
python3 standardize_dirs.py queue --help

# Example
python3 standardize_dirs.py convert dataset_configs/10000.yaml cryoetportal-rawdatasets-dev cryoetportal-output-test --import-everything
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
| --import-everything | | If this flag is passed in, the script will attempt to ingest all data specified in the dataset config, (datasets, runs, annotations, etc etc) |

### Other interesting options to be aware of
| Option | Default | Explanation |
| --- | --- | -- |
| --import-{plural_type} | null | Import data of this type (tomograms, tiltseries, etc) |
| --import-{type}-metadata | null | Import metadata for this type (tomograms, tiltseries, etc) |
| --filter-{type}-name | null | If you only want to import a particular run or voxel spacing, you can filter which objects are ingested by specifying this option with a regular expression that matches the object's name. This option can be specified multiple times with multiple regular expressions |
| --exclude-{type}-name | null | If you want to **exclude** a particular run or voxel spacing, you can filter which objects are ingested by specifying this option with a regular expression that matches the object's name. This option can be specified multiple times with multiple regular expressions |
| --local-fs | False | Allows for the script to be run against a local filesystem instead of assuming S3 input/output paths. This is useful for dev/testing! |
| --no-write-zarr | False | Skip writing zarr's if they don't need to be updated. |
| --no-write-mrc | False | Skip writing mrc's if they don't need to be updated. |
