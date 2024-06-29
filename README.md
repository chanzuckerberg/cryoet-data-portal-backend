# Community Tomography Data Portal Backend
CryoET Portal API server and ingestion tools

To launch a local dev environment (Docker required):
```
make init
```

Wait another ~10s and then visit http://localhost:9695/ in your browser.

## Testing

To initialize the database with test data:
```
make ingestor-test-db-init
```

For ingestion process testing, see the [ingestion_tools README](ingestion_tools/README.md).

## Code of Conduct

This project adheres to the Contributor Covenant [code of conduct](https://github.com/chanzuckerberg/.github/blob/master/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [opensource@chanzuckerberg.com](mailto:opensource@chanzuckerberg.com).

## Reporting Security Issues

If you believe you have found a security issue, please responsibly disclose by contacting us at [security@chanzuckerberg.com](mailto:security@chanzuckerberg.com).
