"""
A script to check if all the files / globs in the sources of a dataset configuration (YAML) file are valid.
Currently only supports run_data_map_file, but looking to extend to other standardization_config fields in the future.
Requires AWS credentials to access the S3 bucket where the files are stored.
Attempts to replace any formatted strings with their corresponding values from the run_data_map_file.
"""

import copy
import logging
import re

import click
import yaml
from boto3 import Session

logger = logging.getLogger("db_import")
logging.basicConfig(level=logging.INFO)

KEY_EXCLUDE_LIST = ["file_format", "value", "name_regex", "match_regex"]


def get_header_data_maps(data: str, filetype: str) -> dict[str, str]:
    """
    Given the run_data_map_file data (as a string) and the filetype (csv or tsv), return a list of dictionaries
    where each dictionary is a header to data map.
    """
    data_header = None
    data_body = None

    data_split = data.split("\r\n")
    if filetype == "csv":
        data_header = data_split[0].split(",")
        data_body = [row.split(",") for row in data_split[1:]]
    elif filetype == "tsv":
        data_header = data_split[0].split("\t")
        data_body = [row.split("\t") for row in data_split[1:]]
    if data_body[-1][0] == "":
        data_body = data_body[:-1]

    return [(dict(zip(data_header, row))) for row in data_body]


def replace_if_formatted_string(value: str, header_data_map: dict[str, str]) -> str:
    """
    Given a value, replace it with the corresponding value from the header_data_map if it is a formatted string.
    """
    if "{" not in value or "}" not in value:
        return value
    header = value.split("{")[1].split("}")[0]
    if header.isnumeric():
        return value
    if header in header_data_map:
        return value.replace("{" + header + "}", header_data_map[header])
    else:
        raise ValueError(f"Header {header} not found in header data map")


def recursive_replace(yaml_data: dict, header_data_map: dict[str, str]) -> dict:
    """
    Recursively iterate through a dictionary (YAML config file) and replace formatted strings with placeholder values.
    Modifies the dictionary in-place.
    """
    for key, value in yaml_data.items():
        if isinstance(value, dict):
            yaml_data[key] = recursive_replace(value, header_data_map)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    value[i] = recursive_replace(item, header_data_map)
                elif isinstance(item, str):
                    value[i] = replace_if_formatted_string(item, header_data_map)
        elif isinstance(value, str):
            yaml_data[key] = replace_if_formatted_string(value, header_data_map)

    return yaml_data


def check_glob_exists(glob, all_files: list[str]) -> list[str]:
    """
    Check if the glob exists in the all_files list. Returns the list of files found.
    Note that file names can be provided as globs, but they will only match themselves.
    """
    if "*" in glob:
        return [file for file in all_files if re.match(glob.replace("*", ".*"), file)]
    return [glob] if glob in all_files else []


def recursive_check_files_exist(data: dict, all_files: list[str]) -> list[str]:
    """
    Given a dictionary, recursively check if all the files / globs in the sources match at least one file in a provided
    list of all files. Returns the list of files found.
    """
    files_found = []
    for key, value in data.items():
        if isinstance(value, dict):
            files_found += recursive_check_files_exist(value, all_files)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    files_found += recursive_check_files_exist(item, all_files)
                elif isinstance(item, str) and key not in KEY_EXCLUDE_LIST:
                    hits = check_glob_exists(item, all_files)
                    if len(hits) == 0:
                        logger.error("Field %s: %s did not match any files", key, item)
                    files_found += hits
        elif isinstance(value, str) and key not in KEY_EXCLUDE_LIST:
            hits = check_glob_exists(value, all_files)
            if len(hits) == 0:
                logger.error("Field %s: %s did not match any files", key, value)
            files_found += hits

    return files_found


def check_yaml_sources_valid(yaml_data: dict, all_files: list[str], exclude_root_entries: list[str]) -> list[str]:
    """
    Given the provided yaml, look into all the sources and see if any file / glob strings are invalid.
    """
    files_found = []

    for key, value in yaml_data.items():
        if key in exclude_root_entries or key == "standardization_config":
            continue
        # every value should be a list element, as per validation
        if not isinstance(value, list):
            logger.error("%s is not a list", key)
            continue
        for item in value:
            if "sources" not in item:
                logger.error("Source key not found in %s", key)
                continue
            for source in item["sources"]:
                files_found += recursive_check_files_exist(source, all_files)

    return list(set(files_found))


def config_check_valid_files(
    yaml_data: dict,
    input_bucket: str,
    region: str,
    profile: str | None,
    exclude_root_entries: list[str],
):
    """
    Given the provided yaml data and S3 bucket, check if all the files / globs in the sources are valid.
    Pull down the run_data_map_file and replace any formatted strings with their corresponding values.
    Also retrieve a full list of files in the bucket to determine which files were not referenced at all.
    """
    standardization_config = yaml_data.get("standardization_config")
    session = Session(region_name=region, profile_name=profile)
    s3 = session.client("s3")
    prefix = standardization_config["source_prefix"]
    if not prefix.endswith("/"):
        prefix += "/"
    run_data_map_file = standardization_config.get("run_data_map_file")
    # run_to_frame_map_csv = standardization_config.get("run_to_frame_map_csv")
    # run_to_tomo_map_csv = standardization_config.get("run_to_tomo_map_csv")
    # run_to_ts_map_csv = standardization_config.get("run_to_ts_map_csv")
    all_files = []
    paginator = s3.get_paginator("list_objects_v2")
    for result in paginator.paginate(Bucket=input_bucket, Prefix=standardization_config["source_prefix"]):
        all_files += [content["Key"].replace(prefix, "") for content in result.get("Contents", [])]

    # read files
    all_files_found = []
    run_data_map_data = None
    if run_data_map_file:
        run_data_map_data = (
            s3.get_object(Bucket=input_bucket, Key=prefix + run_data_map_file)["Body"].read().decode("utf-8")
        )
        filetype = run_data_map_file.split(".")[-1]
        header_data_maps = get_header_data_maps(run_data_map_data, filetype)
        for i, header_data_map in enumerate(header_data_maps):
            logger.info("=====================================")
            logger.info("Checking header data map %d", i)
            replaced_yaml_data = recursive_replace(copy.deepcopy(yaml_data), header_data_map)
            all_files_found += check_yaml_sources_valid(replaced_yaml_data, all_files, exclude_root_entries)

    files_not_found = list(set(all_files) - set(all_files_found) - set(run_data_map_file))
    files_not_found.sort()
    if len(files_not_found) == 0:
        logger.info("SUCCESS: All files were at referenced by at least one source")
    else:
        logger.info("=====================================")
        logger.error("ERROR: Some files were not referenced by any source:")
        for file in files_not_found:
            logger.error(file)

    # run_to_frame_map_data = None
    # if run_to_frame_map_csv:
    #     run_to_frame_map_data = s3.get_object(Bucket=input_bucket, Key=prefix + run_to_frame_map_csv)['Body'].read().decode('utf-8')
    #     replace_formatted_strings(yaml_data, run_to_frame_map_data, "csv")
    # run_to_tomo_map_data = None
    # if run_to_tomo_map_csv:
    #     run_to_tomo_map_data = s3.get_object(Bucket=input_bucket, Key=prefix + run_to_tomo_map_csv)['Body'].read().decode('utf-8')
    #     replace_formatted_strings(yaml_data, run_to_tomo_map_data, "csv")
    # run_to_ts_map_data = None
    # if run_to_ts_map_csv:
    #     run_to_ts_map_data = s3.get_object(Bucket=input_bucket, Key=prefix + run_to_ts_map_csv)['Body'].read().decode('utf-8')
    #     replace_formatted_strings(yaml_data, run_to_ts_map_data, "csv")


@click.command()
@click.option("--yaml-file", type=str, required=True, help="The YAML file to check.")
@click.option("--input-bucket", type=str, required=True, help="The S3 bucket to check.")
@click.option("--region", type=str, required=True, help="The AWS region to use.")
@click.option("--profile", type=str, default=None, help="The AWS profile to use.")
@click.option(
    "--exclude-root-entries",
    type=str,
    default="",
    help="Comma-separated list of root entries to exclude from file checking.",
)
def main(yaml_file: str, input_bucket: str, region: str, profile: str | None, exclude_root_entries: str):
    with open(yaml_file, "r") as file:
        try:
            yaml_data = yaml.safe_load(file)
            config_check_valid_files(yaml_data, input_bucket, region, profile, exclude_root_entries.split(","))
        except yaml.YAMLError as exc:
            logger.error("Error in file %s: %s", yaml_file, exc)
            exit(1)


if __name__ == "__main__":
    main()
