## S3 Data Validation Test Scripts

### Pytest

To run (from this directory):

```
pytest --bucket [BUCKET_NAME] --dataset [DATASET_ID] --run-glob [RUN_GLOB] --voxel-spacing-glob [VOXEL_SPACING_GLOB]

bucket: The S3 bucket where the data is stored. Default: `cryoet-data-portal-staging`
dataset: The dataset ID to validate. Required.
run_glob: A glob pattern to match the run directories to validate. Default: `*`
voxel_spacing_glob: A glob pattern to match the voxel spacing directories to validate. Default: `*`
```

Custom Marks:

Tests are marked according to the type of data they validate. Use `-m MARK` to select a subset of tests to run.

Available marks:

- annotation
- dataset
- deposition
- frame
- gain
- run
- tiltseries
- tilt_angles (spans multiple entities: .tlt, .rawtlt, .mdoc, tiltseries_metadata.json, frames.)
- tomogram
- voxel_spacing

Additional pytest helpful parameters:
```
-n [NUM]: Run tests in parallel with [NUM] workers (pytest-xdist plugin)
    - Use `auto` to automatically determine the number of workers based on the number of CPU cores.
    - Recommended for validating large / multiple datasets
    - Use this with `--dist loadscope` to prevent fixtures from being reloaded for each worker
-v: Verbose output
-s: Print stdout to console
-k: Run tests that match the given substring (even further granularity than -m)
    (see: https://docs.pytest.org/en/latest/example/markers.html#using-k-expr-to-select-tests-based-on-their-name)
```

Example:

Run all data validation for dataset 10027.

```
pytest --dataset 10027 -s -v
```

Run all data validation, with multiple workers, for dataset 10200.

```
pytest --dataset 10200 -s -v -n auto --dist loadscope
```

Run tiltseries and tomogram validation for run "TS_026" in dataset 10000.

```
pytest --dataset 10000 --run-glob "TS_026" -s -v -m tiltseries -m tomogram
```

Run data validation for run "17072022_BrnoKrios_Arctis_p3ar_grid_Position_76" in dataset 10301, skipping TestGain validation.

```
pytest --dataset 10301 --run-glob "17072022_BrnoKrios_Arctis_p3ar_grid_Position_76" -s -v -k "not TestGain"
```

### Allure + Pytest

For large validation runs, it may be helpful to generate an Allure report to view the results. `run_tests.py` is a wrapper script that runs the pytest tests and generates an Allure report, with ability to upload the report to S3.

Ensure you have the allure command line tool installed (e.g. `brew install allure`). See: https://allurereport.org/docs/install/

To run (from this directory):

```
python run_tests.py --bucket [BUCKET_NAME] --output-bucket [OUTPUT_BUCKET_NAME] --datasets [DATASET_ID] --save-history/--no-save-history

bucket: The S3 bucket where the data is stored. Default: `cryoet-data-portal-staging`
output-bucket: The S3 bucket where the Allure report will be uploaded. Default: `cryoetportal-rawdatasets-dev`
datasets: A comma-separated list of dataset IDs to validate. If not provided, all datasets will be validated.
save-history/no-save-history: Save the test results to S3 for historical tracking. Default: `--save-history`
extra_args: Additional arguments to pass to pytest. See pytest arguments above.
```
