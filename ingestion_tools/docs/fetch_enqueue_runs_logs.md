# fetch_enqueue_runs_logs.py

This script is used for fetching logs for the jobs run with `enqueue_runs.py` and categorizing them into success and failed directories based on the execution status. It looks into the AWS Step Functions executions and categorizes them into failed and success directories based on the execution status. The logs are retrieved using AWS CloudWatch Logs.

## One-time Setup
Make sure you have at least python 3.11 installed. If you need to work with multiple versions of python, [pyenv](https://github.com/pyenv/pyenv) can help with that.

Before running the script, ensure all the required packages are installed in a virtualenv:
```bash
cd ingestion_tools
python3 -m venv .venv  # create a virtualenv
source .venv/bin/activate  # activate the virtualenv
python3 -m pip install poetry  # Install the poetry package manager
poetry install  # Use poetry to install this package's dependencies
```

## Setting Up AWS Profile
Before running the script, you need to set up your AWS profile. This can be done by setting the AWS_PROFILE environment variable to the desired profile name. You can set the `AWS_PROFILE` variable using the following command:

`export AWS_PROFILE=your-profile-name`

## Script Usage
To generate the log file for the jobs run with `enqueue_runs.py`, run `enqueue_runs.py` with an output log file specified using the `--execution-machine-log` flag. This will generate a file containing the execution ARNs of the jobs run with `enqueue_runs.py`. This file can be used as input to `fetch_enqueue_runs_logs.py` to fetch the logs for the jobs.

Command-Line Arguments

`execution-arn`: One or more AWS Step Function execution ARNs. If multiple ARNs are provided, they should be separated by space.

`--input-file`: Path to a file containing a list of execution ARNs, one per line.

`--output-dir`: Directory to save the fetched logs. Defaults to ./fetch-logs.

`--profile`: AWS profile to use. If not provided, your default profile will be used.

`--failed-only`: Fetch logs only for failed executions.

`--links-only`: Only retrieve links to the CloudWatch logs, don't fetch any actual logs.

## Examples:

Fetch logs for specific execution ARNs:

`python db_import.py arn:aws:states:us-west-2:123456789012:execution:StateMachineName:execution1 arn:aws:states:us-west-2:123456789012:execution:StateMachineName:execution2`

Fetch logs using an input file containing execution ARNs:

`python db_import.py --input-file execution_arns.txt --output-dir /tmp/fetch-logs`