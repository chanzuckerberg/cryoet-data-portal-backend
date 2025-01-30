## S3 Source Validation Test Scripts

Pytest-based data validation tests for the source data entities in the S3 buckets of the CryoET Data Portal. Fetches test entites from the S3 bucket using the ingestion config and parametrizes tests based on the combinations found in the source bucket. Utilizes pytest-xdist's multiprocessing features to run tests quicker. See below for more information.

### Writing New Tests

If new `helper_*` files are added, make sure to update the `__init__.py` file and add them to the `pytest.register_assert_rewrite` call to ensure that detailed, custom error messages are displayed when the tests fail.

### Pytest

To run (from this directory):

```
pytest --input-bucket [BUCKET_NAME] --ingestion-config [CONFIG_FILE] --run-filter-name [regex value] --frame-filter-name [regex-value]

input-bucket: The S3 bucket where the data is stored. No default value available.
ingestion-config: The name of the ingestion config file, relative to the dataset_config folder
run-filter-name: Similar to the ingestion, the tests can be filtered by any entities name.
```

Custom Marks:

Tests are marked according to the type of data they validate. Use `-m MARK` to select a subset of tests to run.

Available marks:

- frame
- mdoc
- gain
- tiltseries
- tilt_angles

Additional pytest helpful parameters:

```
-n [NUM]: Run tests in parallel with [NUM] workers (pytest-xdist plugin)
    - Use `auto` to automatically determine the number of workers based on the number of CPU cores.
    - Recommended for validating large / multiple datasets. Note: for smaller datasets, this is likely slower because of the worker setup overhead.
    - Use this with `--dist loadscope` to prevent fixtures from being reloaded for each worker
-v: Verbose output
-s: Print stdout to console
-k: Run tests that match the given substring (even further granularity than -m)
    (see: https://docs.pytest.org/en/latest/example/markers.html#using-k-expr-to-select-tests-based-on-their-name)
```

### Examples

Run all data validation for ingestion config 10000.yaml:

```
pytest --ingestion-config 10000.yaml --input-bucket cryoetportal-rawdatasets-dev
```

Run all data validation, with multiple workers, for ingestion config 10000.yaml.

```
pytest --ingestion-config 10000.yaml --input-bucket cryoetportal-rawdatasets-dev -s -v -n auto --dist loadscope
```

Run frames and mdoc validation for run "TS_026" in ingestion config 10000.yaml

```
pytest --ingestion-config 10000.yaml --input-bucket cryoetportal-rawdatasets-dev   --filter-run-name TS_026 -s -v -m "mdoc or frame"
```

### Allure + Pytest

For large validation runs, it may be helpful to generate an Allure report to view the results. `allure_tests.py` is a wrapper script that runs the pytest tests and generates an Allure report, with ability to upload the report to S3.

Ensure you have the allure command line tool installed (e.g. `brew install allure`). See: https://allurereport.org/docs/install/

To run (from this directory):

```
python allure_tests.py --local-dir [LOCAL_DIR] --input-bucket [BUCKET_NAME] --output-bucket [OUTPUT_BUCKET_NAME] --datasets [DATASET_ID] --multiprocessing/--no-multiprocessing --save-history/--no-save-history --extra-args [EXTRA_ARGS]

--local-dir: Local directory to store the results. Default: `./results`
--input-bucket: The S3 bucket where the data is stored.
--output-bucket: The S3 bucket where the Allure report will be uploaded. Default: `cryoetportal-output-test`
--output-dir: The remote s3 directory to store the results. Default: `source_validation`
--ingestion-config: The path of the ingestion config file, relative to the dataset_config folder.
--multiprocessing/--no-multiprocessing: Run tests in parallel with multiple workers (pytest-xdist). Default: `--multiprocessing`
--history/--no-history: Save the history to S3 and retrieve the history of the report. If testing multiple datasets, saving history will result in longer execution time (each dataset has to be an individual `pytest` call). Default: `--history`
--extra-args: Additional arguments to pass to pytest. See pytest arguments above.
--update-s3/--no-update-s3: Update remote s3 directory to store the results from this validation run. Default: `--update-s3`
```

### Note for the --local-dir option: If the specified folder is in the data_validation folder (as is the default value), it should be added to the pytest call via `--ignore=[FOLDER_NAME]` or to the `pytest.ini` file to prevent pytest from wasting time trying to discover tests (we default ignore ./results in `pytest.ini`.)

### Examples

Run all data validation for ingestion config 10000.yaml, and save the test results to S3.

```
python allure_tests.py --ingestion-config 10000.yaml --input-bucket cryoetportal-rawdatasets-dev
```

Run only mdoc validation for ingestion config 10000.yaml, and save the test results to S3.

```
python allure_tests.py --ingestion-config 10000.yaml --input-bucket cryoetportal-rawdatasets-dev --extra-args "-m mdoc"
```

Run on a smaller dataset, so no need for multiprocessing (multiprocessing worker setup overhead makes it slower than no multiprocessing).

```
python allure_tests.py --datasets gjensen/10027.yaml --input-bucket cryoetportal-rawdatasets-dev --no-multiprocessing
```


Run all data validation for ingestion config 10000.yaml only locally, and don't push the test results to S3.

```
python allure_tests.py --ingestion-config 10000.yaml --input-bucket cryoetportal-rawdatasets-dev --no-update-s3
```
