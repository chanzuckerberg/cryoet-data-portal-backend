# Database Ingestion

S3 is the source of truth for all the data in the CryoET data portal, but we provide a nice GraphQL API that makes it easy to query the portal for specific metadata. To accomplish this, we've built a utility that's aware of the portal's expected directory structure and writes most of the metadata that it finds to a PostgreSQL database. The code for this utility is in this directory.

## How to run this tool
To run database ingestion in staging/prod, please see the [docs for launching db ingestion in our batch cluster](https://github.com/chanzuckerberg/cryoet-data-portal-backend/blob/main/ingestion_tools/docs/enqueue_runs.md#database-ingestion-db-import-subcommand)
To run database ingestion locally, for testing or demonstration purposes:

```
make apiv2-init # If you don't have a local dev environment running already
export AWS_PROFILE=cryoet-dev # ANY valid aws credentials will do, since the data we're reading is in a public bucket
cd apiv2
python3 -m db_import.importer load --postgres_url postgresql://postgres:postgres@localhost:5432/cryoetv2 cryoet-data-portal-public https://localhost:8080 --import-everything --s3-prefix 10002 --import-depositions --deposition-id 10301 --deposition-id 10303
```

## Architecture
*** NOTE - we're currently partway through a migration!** The old base importer classes in `importers/base_importer.py` are being deprecated in favor of the base classes in `/importers/base.py` and the docs here reflect the newer functionality.

The architecture of the database importer tool is *similar* to the [architecture of the S3 ingestion tool](https://github.com/chanzuckerberg/cryoet-data-portal-backend/blob/main/ingestion_tools/docs/s3_ingestion.md#how-are-the-different-entities-related) tool:
1. We have a top-level script `importer.py` that processes the data in the portal hierarchically
2. For each object in our schema/database, we have a subclass of the `ItemDBImporter` class that gets instantiated for each instance of an object (eg. one `TomogramItem` instance represents one tomogram in the data portal) and one subclass of `IntegratedDBImporter` that represents a group of items at a particular point in our object hierarchy.
  a. `IntegratedDBImporter` is responsible for finding all relevant metadata at a particular S3 prefix, instantiating the appropriate `ItemDBImporter` objects, and deleting any stale DB rows once all items have been processed.
  b. `ItemDBImporter` is responsible for transforming JSON input data into database fields, and performing any necessary calculation.
3. Similar to the S3 ingestion tool, database ingestion has a set of `Finder` classes in `common/finders.py` that provide reusable helpers for finding files in s3 or finding specific fields within json files in S3. Each `IntegratedDBImporter` class specifies the relevant finder for its data type and provides arguments for how to find data.

## Testing
Tests for DB importers generally do something along the lines of:

1. Populate the database with some stale data, meaning some rows that should be modified by a relevant importer, and some that should be deleted.
2. Perform ingestion of a given type. The data we ingest comes from `test_infra/test_files` at the root of this repo. The seeded data in step one *should not match* the pre-populated data in step 1, this is because we want to ensure that we can accurately *update*, *delete* and *create* database rows that match the data in the "fake" s3 bucket represented by our `test_infra` directory.
3. Validate that new rows were created, stale rows were updated, and unneeded rows were deleted during ingestion, and that all fields match the expected values from `test_infra/test_files`

**NOTE** that if you change any files in `test_infra/test_files` you'll need to run `test_infra/seed_moto.sh` to upload the changes to the moto server we use for testing

