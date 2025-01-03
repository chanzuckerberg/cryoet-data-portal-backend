# Directory Overview

This directory contains files and configurations related to the data ingestion process. It is organized into several folders, each serving a specific purpose. Below is a breakdown of each folder and its contents.

## dataset_configs

This folder holds the configuration files used during the data ingestion process.The YAML files specify the metadata and source location for the entities.

### Naming convention

- If the file name is a number (e.g., 12345.yaml), it corresponds to the dataset with the same ID.
- If the file name starts with deposition_ (e.g., deposition_12345.yaml), it corresponds to the deposition with the ID specified in the file name.

For more information on datasets and depositions refer [here](https://chanzuckerberg.github.io/cryoet-data-portal/cryoet_data_portal_docsite_data.html). 

### Validation 

Configuration file validation is handled by the [schema section](https://github.com/chanzuckerberg/cryoet-data-portal-backend/tree/main/schema/) of the repository.


## docs 

This folder contains documentation related to the ingestion tools and processes.


## infra 

This folder contains WDL (Workflow Description Language) files that specify executions. These files define the steps and order of operations in the data ingestion pipeline.

### Naming Convention
WDL files in this folder typically follow this naming convention:

- The file name begins with the workflow it orchestrates, followed by the version number.
- Common prefixes include:
  - db_import: Handles database imports.
  - standardize_dirs: Handles S3 data ingestion.
  - sync: Syncs data between different environments.
  - validate: Validates the ingested data.

For more about WDL, visit [OpenWDL](https://openwdl.org/). 


## scripts

This folder contains all the scripts that power the workflows. It is organized into different modules:

#### data_validation 
This module contains scripts for validating data. Instructions for running the validation tests can be found in the README within this folder.

#### importers
This module contains scripts for ingesting data:

- The root-level importers handle S3 ingestion.
- The importers.db submodule contains importers for the v1 database.

#### schema_migration
This module helps keep schema configurations up to date as they evolve. It includes tools for managing schema changes.

