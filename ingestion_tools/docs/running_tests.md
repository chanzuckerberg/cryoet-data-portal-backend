# Running tests locally

The ingestion process' unit tests are written using pytest, and can be found [../tests](../tests).


## Running tests in docker

The tests can be run using the make commands specified in the [make file](../Makefile).

### Running tests for s3 ingestion
To run the tests for s3 ingestion, use the following commands:

```bash
# initializes the ingestion_tools image
make ingestor-init
# runs the tests for s3 ingestion
make ingestor-test-s3
```

The ingestion tests also have dependency on the motoserver for faking the aws interactions, and the nginx server for serving the files. The motoserver and nginx server are started as part of the `ingestor-init` command.

### Running tests for db ingestion
To run the tests for db ingestion, use the following commands:

```bash
# initializes the ingestion_tools image
make ingestor-init
# initializes the db, loads schema and seed data
make ingestor-test-db-init
# runs the tests for db ingestion
make ingestor-test-s3
```


## Running tests locally

To run the tests locally, you will have to set up a few environment variables.

| variable name         | value | required         | description                              |
|-----------------------|-------|------------------|------------------------------------------|
| AWS_ACCESS_KEY_ID     |   test    | yes              | Sets up AWS credentials for motoserver   |
| AWS_SECRET_ACCESS_KEY |     test  | yes              | Sets up AWS credentials for motoserver   |
| AWS_REGION            |    us-west-2   | yes   | -                                        |
| ENDPOINT_URL          |  http://localhost:5566     | yes | Points the aws calls to local motoserver |
| DB_CONNECTION         |  postgresql://postgres:postgres@localhost:5432/cryoet     | only for db test | Points db calls to local db              |

To run the tests, use the following commands:

```bash
cd ingestion_tools/scripts
# Run the tests for s3 ingestion
python pytest . -k s3_import
# Run the tests for db ingestion
python pytest . -k db_import
```

### Notes
Having an active `AWS_PROFILE` environment variable might interfere with the tests. It is recommended to unset the `AWS_PROFILE` variable before running the tests.
