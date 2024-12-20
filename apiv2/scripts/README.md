# Utility Scripts

This folder contains scripts that are used to interact with the data in api v2. Below is a brief description of each script.

### Scrape

To maintain the consistencies of ids for the entities between the api v1 and api v2, the `scrape.py` script is used. It ports the data from api v1 to api v2. This script is used to port the data from the api v1 database to the api v2 database.

It fetches the data from v1 api using an older version of the client, translates the data to V2 api models and then inserts the data into the v2 database.

### Required arguments

| Argument | Explanation                                                                                  |
|----------|----------------------------------------------------------------------------------------------|
| env      | The environment where the scraping is happening. Acceptable values are: local, staging, prod |


### Commonly used options

| Argument            | Default | Explanation                                                                                      |
|---------------------|---------|--------------------------------------------------------------------------------------------------|
| --db-uri            | None    | Provide the uri for the db. If this is not passed, an uri is constructed from environment variables.|
| --import-dataset    | None    | Ids of the dataset to be imported. This flag can be used to specify multiple datasets.           |
| --import-deposition | None    | Ids of the depositions to be imported. This flag can be used to specify multiple depositions     |

### Note
If no value is specified for the `--import-dataset` or `--skip-until` flags, the script will process all the datasets in the v1 api to the v2 api.

If the `--db-uri` is not passed, and there are no environment variables configured for `PLATFORMICS_DATABASE_USER`, `PLATFORMICS_DATABASE_PASSWORD`, `PLATFORMICS_DATABASE_HOST`, `PLATFORMICS_DATABASE_PORT`, `PLATFORMICS_DATABASE_NAME` then the script will fail.

### Other options

| Argument        | Default | Explanation                                           |
|-----------------|--------|-------------------------------------------------------|
| --skip-until | None   | Ignores all datasets with ids until this dataset.     |
| --import-all-depositions | None   | If this flag is set, all the depositions are imported |
| --parallelism   | 10     | Specify how many parallel jobs can run                |


### Running the script

The snippet below shows how to run the scrape script to port the dataset 10000 from v1 to v2 api.

```
cd apiv2/scripts

# Activate a python virtualenv
source ../.venv/bin/activate

# Run the script
python3 -m scrape local --db-uri postgresql://postgres:postgres@localhost:5432/cryoetv2 --import-dataset 10000
```

### Delete Dataset

The `delete_dataset.py` script is used to delete a dataset completely from the api v2 database. It relies on the foreign key relationships between entities to delete all the related entities when a dataset is deleted. This is done to ensure that the database is in a consistent state after the deletion.

**Please use this script with extreme caution.**

### Required arguments

| Argument | Explanation |
| --- | --- |
| dataset_id | The dataset to be deleted |


### Commonly used options

| Argument          | Default | Explanation                                                                                          |
|-------------------|---|------------------------------------------------------------------------------------------------------|
| --db-uri          | None   | Provide the uri for the db. If this is not passed, an uri is constructed from environment variables. |
| --i-am-super-sure | None   | This needs to be set to "yes" only if you are super sure you want to delete the dataset              |

### Note
If the `--db-uri` is not passed, and there are no environment variables configured for `PLATFORMICS_DATABASE_USER`, `PLATFORMICS_DATABASE_PASSWORD`, `PLATFORMICS_DATABASE_HOST`, `PLATFORMICS_DATABASE_PORT`, `PLATFORMICS_DATABASE_NAME` then the script will fail.

### Running the script

The snippet below shows how to run the script to delete a dataset with id 1001 in your local environment.
```
cd apiv2/scripts

# Activate a python virtualenv
source ../.venv/bin/activate

# Run the script
python3 -m delete_dataset --db-uri postgresql://postgres:postgres@localhost:5432/cryoetv2 --i-am-super-sure yes 1001
```
