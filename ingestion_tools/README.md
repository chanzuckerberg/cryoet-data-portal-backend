# Ingestion utilities

This package contains ingestion scripts, libraries, and configurations for converting raw research datasets into a format compatible with the CryoET Data Portal.

## Running tests

Whether running tests on Docker or locally, please ensure that your Docker environment is set up and has the test data as described in the [README](../README.md) before running tests.
Either way, `breakpoint()` statements can be added to the code to pause execution and allow for debugging.

### Running tests on Docker

From the root of the repository, run the following command to build the Docker image and run the tests:
```bash
make ingestor-test-db
make ingestor-test-s3
```

### Running tests locally

Install dependencies with (from the `ingestion_tools/scripts` directory):
```bash
pip install poetry
poetry install
```

If running these tests locally with a Dockerized database, set the `DB_CONNECTION` and `ENDPOINT_URL` environment variables:
```bash
export DB_CONNECTION=postgresql://postgres:postgres@127.0.0.1:5433/cryoet
export ENDPOINT_URL=http://127.0.0.1:5566/
export AWS_REGION=us-west-2
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
```

Run the tests with (from the `ingestion_tools/scripts` directory):
```bash
python -m pytest
```

### Forwarding nginx port 80 to 4444

When running tests locally, note that any URLs in test dataset files referencing `nginx:80` in the tests will fail with the above code. To prevent this, a workaround is
 to run the following commands instead (`socat` must be installed, `sudo` is required):

In a new terminal terminal (to forward port 80 to 4444):
```bash
sudo socat TCP-LISTEN:80,fork,reuseaddr TCP:localhost:4444
```

In the terminal which your environmenmt variables are set (from the `ingestion_tools/scripts` directory):
```bash
sudo bash -c 'echo "127.0.0.1 nginx # temp entry" >> /etc/hosts'
python -m pytest
sudo sed -i '/127.0.0.1 nginx # temp entry/d' /etc/hosts
```
