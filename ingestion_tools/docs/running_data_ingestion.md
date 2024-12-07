# Running Data Ingestion

## Introduction
You have a new dataset that you want to ingest or a cool new update that you want to add to an existing dataset. How do you do it? This document will guide you through the process of running data ingestion from start to finish.

## Prerequisites
Before you start, please make sure you have the following setup.

### 1. Access to the relevant AWS Accounts
Permissions to the relevant aws accounts. If you are not sure what the relevant accounts are, holler at your team they will be happy to provide you with the information.
Once you have the access, make sure you have the necessary credentials set up in your local environment.
### 2. Your local python environment
Set up your local python environment for ingestion tools. Refer to the [Setting up your local python environment](../README.md#setting-up-your-local-python-environment) section in the README for more information.


## Ingesting Data

There are 2 main steps to ingesting data into the staging environment.

1. Running the s3 ingestion to update the files in the s3 bucket
2. Running the db ingestion to update the data in the staging database

## Ingesting data into the Staging Environment

### Before you start

Before you kick off any ingestion process in aws, make sure your changes are deployed to the AWS ECR in the staging environment.

Once you have merged your changes into main, a [github workflow](https://github.com/chanzuckerberg/cryoet-data-portal-backend/blob/6b82b3c7948af05b5edc17eb4a42b4984999d53a/.github/workflows/push-ingestor-build.yaml) should run to build and deploy the docker image to the staging environment. You can check the status of the workflow in the [github actions](https://github.com/chanzuckerberg/cryoet-data-portal-backend/actions/workflows/push-ingestor-build.yaml) page.


### Running the s3 ingestion

The s3 ingestion will fetch the data from the source bucket, transform it, and write it to the destination bucket. You can learn more about the script in the [standardize_dirs.md](standardize_dirs.md) document.

To run this workflow in the aws environment, you can use the `enqueue_runs.py` script. This script will handle the orchestration of the s3 ingestion for runs specified in a dataset. You can learn more about the script in the [enqueue_runs.md](enqueue_runs.md#file-ingestion-queue-subcommand) document.

Example:

```bash
python enqueue_runs.py queue dataset_configs/10000.yaml <source_bucket> <destination_bucket> --import-dataset-metadata --import-run-metadata
```


### Running the db ingestion

The db ingestion will fetch the data from the s3 bucket, transform it, and write it to the staging databases (both v1 and v2). Only after running this step, will you be able to see the changes reflected in the api.

To run this workflow in the aws environment, you can use the `enqueue_runs.py` script. This script will handle the orchestration of the db ingestions for the specified dataset. You can learn more about the script in the [enqueue_runs.md](enqueue_runs.md#database-ingestion-db-import-subcommand) document.

Example:

```bash
python enqueue_runs.py db-import --import-runs --include-dataset 10000
```


### Running validation tests
Coming soon..


### Tracking the progress of your ingestion

Log into the aws console. You should be able to see the progress of your ingestion workflow you queued up in the step functions page.


## Ingesting Data into the Production

### Syncing the data to the production
Once the data has been validated in staging, you can copy the updates from the staging bucket to the production bucket.
To run this workflow in, you can use the `enqueue_runs.py` script. This script will handle the syncing for the specified data. You can learn more about the script in the [enqueue_runs.md](enqueue_runs.md#enqueue_runs.md#s3-file-sync-sync-subcommand) document.


### Getting the prod API updated
Similar to staging, only after running this step, will you be able to see the changes reflected in the API.

To run this workflow in the aws environment, you can use the `enqueue_runs.py` script. This script will handle the orchestration of the db ingestions for the specified dataset. You can learn more about the script in the [enqueue_runs.md](enqueue_runs.md#database-ingestion-db-import-subcommand) document.

The main difference is that you will have to ensure your aws credentials are set up to access the production environment. and you will have to run the script with the `--environment prod` flag.

Example:

```bash
python enqueue_runs.py db-import --import-runs --include-dataset 10000 --environment prod
```
