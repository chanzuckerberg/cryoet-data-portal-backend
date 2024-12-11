# Community Tomography Data Portal Backend

The **CryoET Data Portal Backend** serves as the backbone for the [CryoET (Cryo-Electron Tomography) Data Portal](https://cryoetdataportal.czscience.com/), providing essential API services and data ingestion tools. This infrastructure enables users to access and manage CryoET datasets effectively.

Read more about CZI's CryoET Data Portal [here](https://chanzuckerberg.github.io/cryoet-data-portal/cryoet_data_portal_docsite_landing.html).

## Developer Guidelines

### Pre-requisite installations and setups

**Note**: Before you begin to install any Python packages, make sure you have activated your Python virtual environment.

1. From the root of the repo - create a new virtual env (using [venv](https://docs.python.org/3/library/venv.html) or your preferred virtual env tool) with python 3.12
1. Make sure you have docker installed and running on your machine
1. Install pre-commit: `pre-commit install` or check doc [here](https://pre-commit.com/)
1. Set up your machine to be able to work with AWS using the instructions [here](https://czi.atlassian.net/wiki/spaces/DC/pages/332892073/Getting+started+with+AWS). Please ensure to follow the step 3 `AWS CLI access` instructions all the way to the bottom so that you are also set up for SSH access.

### Development Quickstart

To launch a local dev environment:

```
make init
```

Wait another ~10s and then visit http://localhost:9695/ in your browser.

### API Server

To get started with `apiv2`, running the API server, updating schema and debugging follow the documentation [here](https://github.com/chanzuckerberg/cryoet-data-portal-backend/tree/main/apiv2).

### Ingestion Setup

Follow the steps [here](https://github.com/chanzuckerberg/cryoet-data-portal-backend/blob/main/ingestion_tools/README.md) to install all necessary requirements, and follow the instructions on how to run.

Documentation for running data ingestion scripts can be found [here](https://github.com/chanzuckerberg/cryoet-data-portal-backend/tree/main/ingestion_tools/docs/running_data_ingestion.md)

### Testing

For setting up local test infra, seed local database and running the test suite, follow the documentation [here](test_infra/README.md)

### Deployment

For pre-deployment, creating `rdev` and deploying to staging/prod - follow the guideline [here](docs/deployment.md).

## Related Repos

- Community Cryo-Electron Tomography Data Portal [repo](https://github.com/chanzuckerberg/cryoet-data-portal?tab=readme-ov-file)

- CryoET Data Portal Neuroglancer configuration helper [repo](https://github.com/chanzuckerberg/cryoet-data-portal-neuroglancer)

- A napari plugin to list, preview, and open data from the CZ Imaging Institute's CryoET Data Portal [repo](https://github.com/chanzuckerberg/napari-cryoet-data-portal)

## Code of Conduct

This project adheres to the Contributor Covenant [code of conduct](https://github.com/chanzuckerberg/.github/blob/master/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [opensource@chanzuckerberg.com](mailto:opensource@chanzuckerberg.com).

## Reporting Security Issues

If you believe you have found a security issue, please responsibly disclose by contacting us at [security@chanzuckerberg.com](mailto:security@chanzuckerberg.com).
