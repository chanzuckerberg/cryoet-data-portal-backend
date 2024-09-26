# Ingestion Config Validation Script

`ingestion_config_validate.py` is used to validate the ingestion configuration files for a dataset. Called by the `schema` Makefile commands as well as pre-commit hooks.

See `ingestion_config_validate.py --help` for more information.

## Caveats

Currently, all formatted strings are getting replaced by the validation script with placeholder values. Specifically, float and int formatted strings. This is because currently we run into some bugs when trying to support both strings and numerical values with the `any_of` feature with LinkML while also trying to restrain the numerical values to a specific range. Pydantic-gen'd LinkML will attempt to compare the string to the numerical constraints (greater than or equal to) and throw an error. This is a known issue and will be fixed in the future (not sure when).
