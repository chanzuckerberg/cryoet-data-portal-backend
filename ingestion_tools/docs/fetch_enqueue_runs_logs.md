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
Command-Line Arguments

`execution-arn`: One or more AWS Step Function execution ARNs. If multiple ARNs are provided, they should be separated by space.

`--input-file`: Path to a file containing a list of execution ARNs, one per line.

`--output-dir`: Directory to save the fetched logs. Defaults to ./fetch-logs.

`--region`: The AWS region to use for the API calls.

## Examples:

Fetch logs for specific execution ARNs:

`python db_import.py arn:aws:states:us-west-2:123456789012:execution:StateMachineName:execution1 arn:aws:states:us-west-2:123456789012:execution:StateMachineName:execution2 --region us-west-2`

Fetch logs using an input file containing execution ARNs:

`python db_import.py --input-file execution_arns.txt --region us-west-2`
