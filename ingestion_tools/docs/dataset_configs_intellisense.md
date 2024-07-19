# Dataset Configuration Files Intellisense Setup Guide
Enable intellisense for dataset configuration files in your IDE. The schema checking is done against the JSONSchema in `dataset_config_models.schema.json`, which is automatically generated when running `make` in the `schema/v1.1.0` directory.

Note this does not include the extended validation done with Pydantic (network requests or non-network requests), it only includes the LinkML validation.
**You may still run into errors even though they do not apper with the intellisense hints, because the extended Pydantic validation checks are not supported by JSONSchema.**

## PyCharm

1. Open up any YAML file in the repository (ingestion_tools/dataset_configs/10000.yaml is the one in this example, but it doesn't matter which YAML file)
2. In the bottom right of your screen, click on the field that says "No JSON schema"
    2a. If you don't see this, go to File -> Settings -> Languages & Frameworks -> Schemas and DTDs -> JSON Schema Mappings and click the "+" sign (skip to step 4)
3. Then click New Schema Mapping
4. Enter in "Schema file or URL:" schema\v1.1.0\dataset_config_models.schema.json
5. Delete the current file entry (if it exists) and instead add a "Directory:" entry with the value: ingestion_tools\dataset_configs
6. Press "Apply" and "OK" and you should be all setup! Errors will now highlight in yellow!

## VSCode

1. Install the YAML extension and you should be all setup! Errors are highlighted in red! (the settings are pulled from .vscode/settings.json)
