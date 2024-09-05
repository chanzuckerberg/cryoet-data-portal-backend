## S3 Data Validation Test Scripts

### Pytest

To run (from this directory):

```
pytest --bucket [BUCKET_NAME] --datasets [DATASET_ID] --run-glob [RUN_GLOB] --voxel-spacing-glob [VOXEL_SPACING_GLOB]

bucket: The S3 bucket where the data is stored. Default: `cryoet-data-portal-staging`
datasets: A comma-separated list of dataset IDs to validate. If not provided, all datasets will be validated.
run-glob: A glob pattern to match the run directories to validate. Default: `*`
voxel-spacing-glob: A glob pattern to match the voxel spacing directories to validate. Default: `*`
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
    - Recommended for validating large / multiple datasets. Note: for smaller datasets, this is likely slower because of the worker setup overhead.
    - Use this with `--dist loadscope` to prevent fixtures from being reloaded for each worker
-v: Verbose output
-s: Print stdout to console
-k: Run tests that match the given substring (even further granularity than -m)
    (see: https://docs.pytest.org/en/latest/example/markers.html#using-k-expr-to-select-tests-based-on-their-name)
```

Example:

Run all data validation for dataset 10027.

```
pytest --datasets 10027 -s -v
```

Run all data validation for datasets 10040 and 10041.

```
pytest --datasets 10040,10041 -s -v
```

Run all data validation, with multiple workers, for dataset 10200.

```
pytest --datasets 10200 -s -v -n auto --dist loadscope
```

Run tiltseries and tomogram validation for run "TS_026" in dataset 10000.

```
pytest --datasets 10000 --run-glob "TS_026" -s -v -m tiltseries -m tomogram
```

Run data validation for run "17072022_BrnoKrios_Arctis_p3ar_grid_Position_76" in dataset 10301, skipping TestGain validation.

```
pytest --datasets 10301 --run-glob "17072022_BrnoKrios_Arctis_p3ar_grid_Position_76" -s -v -k "not TestGain"
```

### Allure + Pytest

For large validation runs, it may be helpful to generate an Allure report to view the results. `run_tests.py` is a wrapper script that runs the pytest tests and generates an Allure report, with ability to upload the report to S3.

Ensure you have the allure command line tool installed (e.g. `brew install allure`). See: https://allurereport.org/docs/install/

To run (from this directory):

```
python run_tests.py --local-dir [LOCAL_DIR] --input-bucket [BUCKET_NAME] --output-bucket [OUTPUT_BUCKET_NAME] --datasets [DATASET_ID] --multiprocessing/--no-multiprocessing --save-history/--no-save-history --extra-args [EXTRA_ARGS]

--local-dir: Local directory to store the results. Note that if this folder is in the data_validation folder (as is the default value), it should be added to the pytest call via `--ignore=[FOLDER_NAME]` to prevent pytest from wasting time trying to discover tests (we default ignore ./results in `pytest.ini`.) Default: `./results`
--input-bucket: The S3 bucket where the data is stored. Default: `cryoet-data-portal-staging`
--output-bucket: The S3 bucket where the Allure report will be uploaded. Default: `cryoetportal-output-test`
--output-dir: The remote s3 directory to store the results. Default: `data_validation`
--datasets: A comma-separated list of dataset IDs to validate. If not provided, all datasets will be validated.
--multiprocessing/--no-multiprocessing: Run tests in parallel with multiple workers (pytest-xdist). Default: `--multiprocessing`
--history/--no-history: Save the history to S3 and retrieve the history of the report. If testing multiple datasets, saving history will result in longer execution time (each dataset has to be an individual `pytest` call). Default: `--history`
--extra-args: Additional arguments to pass to pytest. See pytest arguments above.
```

Example:

Run all data validation for datasets 10027 and 10200, and save the test results to S3.

```
python run_tests.py --datasets 10027,10200
```

Run only tiltseries validation for all datasets, and save the test results to S3.

```
python run_tests.py --extra-args "-k TestTiltseries"
```

Run on a smaller dataset, so no need for multiprocessing (multiprocessing worker setup overhead makes it slower than no multiprocessing).

```
python run_tests.py --datasets 10031 --no-multiprocessing
```

Run all data validation for everything, and save the test results to S3 (not recommended, can take very long, on the scale of a day possibly).

```
python run_tests.py
```

#### Viewing Allure Report

After running `run_tests.py`, a folder with the results (default `./results`) will be created. To view the Allure report:

```
cd results
python -m http.server
```

Then navigate to `http://localhost:8000` in your browser.
