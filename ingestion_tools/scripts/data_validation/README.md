## S3 Data Validation

Pytest-based data validation tests for the data S3 buckets. This includes both the source and the standardized output data. As a large number of tests are similar sanity checks between the source and the output data, we have a shared folder to reuse the tests.

Utilizes pytest-xdist's multiprocessing features to run tests quicker, and allure for visualizing the report on the test results.

### The folder structure

#### shared
Contains all the common tests shared between both the source and the standardized output s3 data

#### source
Contains code related to tests for the source data. The entities to be tested are fetched by the ingestion config.

#### standardized
Contains code related to tests for the output data. The entities to be tested are fetched by dataset_id

### Running Pytest

The pytests are meant to be run from their respective directories. The readmes of the test directories should have more information on this.



### Viewing Allure Report

After running `allure_tests.py`, a folder with the results (default `./results`) will be created. To view the Allure report:

```
cd results
python -m http.server [OPTIONAL_PORT]
```

Then navigate to `http://localhost:8000` in your browser (or the port you specified).

#### Viewing Allure Reports Stored in S3

First, download the tar.gz file of the report from S3. Then extract the contents:

```
tar -xvf [TAR_FILE]
```

Then navigate to the extracted folder and run the Python HTTP server:

```
cd [EXTRACTED_FOLDER]
python -m http.server [OPTIONAL_PORT]
```

Then navigate to `http://localhost:8000` in your browser (or the port you specified).
