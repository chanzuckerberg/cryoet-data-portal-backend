import logging
import os
import re

DATASET_CONFIGS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../dataset_configs/"))
EXCLUDE_LIST = ["template.yaml", "dataset_config_merged.yaml"]
EXCLUDE_KEYWORDS_LIST = ["draft"]
YAML_EXTENSIONS = (".yaml", ".yml")


def get_yaml_config_files(
    input_files: list[str] = None,
    include_glob: str = None,
    exclude_keywords_list: list[str] = None,
    dataset_configs_dir: str = None,
    verbose: bool = False,
    logger_name: str = None,
) -> list:
    """
    Returns a list of files to validate based on the include glob and exclude keywords.
    """
    logger = logging.getLogger(logger_name) if logger_name else logging.getLogger(__name__)

    if verbose:
        logger.setLevel(logging.DEBUG)

    if not exclude_keywords_list:
        exclude_keywords_list = EXCLUDE_KEYWORDS_LIST

    logger.info("Excluding files that contain any of the following keywords: %s", exclude_keywords_list)

    # in the case that a None is passed in, set the default value
    if not dataset_configs_dir:
        dataset_configs_dir = DATASET_CONFIGS_DIR

    # If input_files is not defined,  Get all files in the dataset_configs_dir
    files_to_filter = (
        input_files
        if input_files
        else [
            os.path.join(dirpath, f)
            for (dirpath, dirnames, filenames) in os.walk(dataset_configs_dir)
            for f in filenames
        ]
    )

    # Filter files based on the exclude list
    files_to_validate = []
    for file in files_to_filter:
        filename = os.path.basename(file)
        if not filename.endswith(YAML_EXTENSIONS):
            continue
        if filename in EXCLUDE_LIST:
            continue
        if any(keyword in filename for keyword in exclude_keywords_list):
            logger.debug("Excluding %s because it contains an exclude keyword", file)
            continue
        files_to_validate.append(os.path.normpath(os.path.join(dataset_configs_dir, file)))

    # Filter files based on the include glob
    if include_glob:
        logger.info("Filtering files based on include glob: %s", include_glob)
        files_to_validate = [file for file in files_to_validate if re.search(include_glob, file)]
        if verbose:
            logger.debug("Files to validate:")
            for file in files_to_validate:
                logger.debug(file)

    return files_to_validate
