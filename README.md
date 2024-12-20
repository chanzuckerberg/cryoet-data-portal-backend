# Community Tomography Data Portal Backend
CryoET Portal API server and ingestion tools forms the backend for the Community Tomography Data Portal. The API server is responsible for serving the data and the ingestion tools are for ingesting the data from the source, transforming them and landing them in the database.


## Code of Conduct

This project adheres to the Contributor Covenant [code of conduct](https://github.com/chanzuckerberg/.github/blob/master/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [opensource@chanzuckerberg.com](mailto:opensource@chanzuckerberg.com).

## Reporting Security Issues

If you believe you have found a security issue, please responsibly disclose by contacting us at [security@chanzuckerberg.com](mailto:security@chanzuckerberg.com).

## Developer Guidelines
### Pre-requisite installations and setups

**Note**: Before you begin to install any Python packages, make sure you have activated your Python virtual environment.

1. Install pre-commit: `pre-commit install` or check doc [here](https://pre-commit.com/)
2. Set up your machine to be able to work with AWS using the instructions [here](https://czi.atlassian.net/wiki/spaces/DC/pages/332892073/Getting+started+with+AWS). Please ensure to follow the step 3 `AWS CLI access` instructions all the way to the bottom so that you are also set up for SSH access.
3. [install jq](https://stedolan.github.io/jq/download/). If brew is installed run `brew install jq`.

### PR Guidelines
1. PR name should follow the conventional commit format. For example, `feat: add new annotation type` or `fix: fixing error from x`.
2. PR description should be detailed and should follow the template provided.
3. PR should have at least one approved reviewer.
4. PR should pass all the checks before merging.
5. PR should be squashed and merged.

### Common Commands

| Command                                                                                 | Description                                                             |
|-----------------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| `make ingestor-init`                                                                    | Starts the container for ingestor locally along with required resource. |
| `make api-init`                                                                         | Starts the API V1 locally.                                              |
| `make apiv2-init`                                                                       | Starts the API V2 locally.                                              |
| `make ingestor-test-s3`                                                                 | Runs unit tests for s3 ingestion.                                       |
| `make ingestor-test-db`                                                                 | Runs unit tests for db ingestion for api v1.                            |
| `make apiv2-test`                                                                       | Runs unit tests for db ingestion for api v2.                            |
| `AWS_PROFILE=<relevant-aws-profile> make push-local-ingestor-build tag=<tag-for-build>` | Builds and pushes image of ingestor to remote ECR.                      |


### Environment variables

Environment variables are set using the command `export <name>=<value>`.

| Name                | Description                                                                  | Values                      |
| ------------------- |------------------------------------------------------------------------------|-----------------------------|
| `AWS_PROFILE`       | Specifies the profile used to interact with AWS resources via the awscli.    | `cryoet-dev`, `cryoet-prod` |



#### Building the image

The base image is built using Github actions whenever a relevant code change is merged into main. The image build is tagged as `main`.

In the rare event a new build of the image needs to be built without Github Actions, follow the steps below to build the images locally and push it to remote, replacing `<tag-for-build>` with the desired tag for the image.:
```bash
make push-local-ingestor-build tag=<tag-for-build>
```
