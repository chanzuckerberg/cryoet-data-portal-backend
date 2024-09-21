"""
This script migrates the ingest config files to a new schema based on the changes outlines in
https://github.com/chanzuckerberg/cryoet-data-portal/issues/997
"""
import glob
import itertools
import json
import traceback
from typing import Union

import numpy as np
import yaml


def rawtilts_to_collection_metadata(config: dict) -> None:
    list_globs = []
    if 'rawtilts' in config:
        for i in config['rawtilts']:
            if "sources" not in i:
                continue
            old_source = i["sources"][0]["source_multi_glob"]["list_globs"]
            list_globs.extend(s for s in old_source if s.endswith('.mdoc') or "{mdoc_name}" in s)
            for source in list_globs:
                old_source.remove(source)
        if list_globs:
            if 'collection_metadata' not in config:
                config['collection_metadata'] = [{"sources": [{"source_multi_glob": {"list_globs": []}}]}]
            config["collection_metadata"][0]["sources"][0]["source_multi_glob"]["list_globs"].extend(list_globs)


def rawtilts_to_alignments(config: dict) -> None:
    list_globs = []
    format_dict = {
        "IMOD": [],
        "ARETOMO3": [],
    }

    def valid_file(file):
        return any(file.endswith(ext) for ext in ['.tlt', ".xf", ".aln", ".com", ".txt", ".csv"])

    def get_format(file):
        if any(file.endswith(ext) for ext in ['.tlt', ".xf", ".com"]):
            format_dict["IMOD"].append(file)
        elif any(file.endswith(ext) for ext in ['.aln', ".txt", ".csv"]):
            format_dict["ARETOMO3"].append(file)

    if len(config.get('tomograms', [])) > 1 or len(config.get("rawtilts", [])) > 1:
        raise ValueError("More than one tomogram or rawtilt")

    if 'rawtilts' in config:
        for i in config['rawtilts']:
            if "sources" not in i:
                continue
            old_source = i["sources"][0]["source_multi_glob"]["list_globs"]
            list_globs.extend(s for s in old_source if valid_file(s))
            for source in list_globs:
                old_source.remove(source)
                get_format(source)
        if list_globs:
            if 'alignments' not in config:
                config['alignments'] = []
            for key, files in format_dict.items():
                if files:
                    # check if there is an alignment with the key in the metadata.format
                    alignment = [a for a in config.get("alignments", []) if a["metadata"]["format"] == key]
                    if alignment:
                        alignment = alignment.pop()
                    else:
                        alignment = {
                            "metadata": {"format": key},
                            "sources": [{"source_multi_glob": {"list_globs": files}}]}

                    if 'tomograms' in config:
                        for i in config['tomograms']:
                            if "metadata" not in i:
                                continue
                            affine_transformation_matrix = i["metadata"].get("affine_transformation_matrix", None)
                            if affine_transformation_matrix and np.allclose(affine_transformation_matrix,np.eye(4)):
                                # skip if is an idenity matrix
                                continue
                            if affine_transformation_matrix:
                                alignment["metadata"]["affine_transformation_matrix"] = affine_transformation_matrix
                    config["alignments"].append(alignment)


def update_tomogram_metadata(config: dict) -> None:
    if tomograms := config.get("tomograms"):
        for tomogram in tomograms:
            if metadata := tomogram.get("metadata"):
                metadata["is_visualization_default"] = True
                if not metadata.get("dates"):
                    try:
                        dates = config["depositions"][0]["metadata"]["dates"]
                    except (KeyError, IndexError):
                        dates = {
                            "deposition_date": '1970-01-01',
                            "last_modified_date": '1970-01-01',
                            "release_date": '1970-01-01'}
                    metadata["dates"] = dates
                affine_transformation_matrix = metadata.get("affine_transformation_matrix", None)
                if not affine_transformation_matrix:
                    metadata["affine_transformation_matrix"] = np.eye(4, dtype=int).tolist()


def update_annotation_sources(config: dict) -> None:
    if annotations := config.get('annotations'):
        for annotation in annotations:
            if sources := annotation.get("sources"):
                for source in sources:
                    for value in source.values():
                        value["is_portal_standard"] = False

def remove_empty_fields(config: Union[list, dict]) -> None:
    remove_key = []
    exclude_keys = ['annotations']
    if isinstance(config, list):
        for i in config:
            if isinstance(i, (list, dict)):
                remove_empty_fields(i)
                if len(i) == 0:
                    remove_key.append(i)
        if remove_key:
            for key in remove_key:
                config.remove(key)
    elif isinstance(config, dict):
        for key, value in config.items():
            if isinstance(value, (list, dict)):
                remove_empty_fields(value)
                if len(value) == 0:
                    remove_key.append(key)
        if remove_key:
            for key in remove_key:
                if key in exclude_keys:
                    continue
                config.pop(key)

def check_deposition(config: dict) -> bool:
    if "depositions" in config:
        return True
    raise ValueError("depositions is not in the config")

def has_changes(file, config):
    with open(file, 'r') as file:
        old_config = yaml.safe_load(file)
    return json.dumps(old_config) != json.dumps(config)

def migrate_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)

    try:
        rawtilts_to_collection_metadata(config)
        rawtilts_to_alignments(config)
        update_tomogram_metadata(config)
        check_deposition(config)
        update_annotation_sources(config)
        remove_empty_fields(config)
    except Exception as e:
        print(f"Error in {get_relative_path(file_path)}: missing {e}")
        print(traceback.format_exc())
        return

    if has_changes(file_path, config):
        relative_path = file_path[file_path.find("cryoet-data-portal-backend"):]
        print(f"modified: {relative_path}")
        with open(file_path, 'w') as file:
            yaml.safe_dump(config, file)

def get_relative_path(file_path):
    return file_path[file_path.find("cryoet-data-portal-backend"):]


if __name__ == "__main__":
    # Update all config files
    config_files = glob.glob(
        '/Users/trentsmith/workspace/cryoet/cryoet-data-portal-backend/ingestion_tools/dataset_configs/**/*.yaml',
        recursive=True)
    test_config_files = glob.glob(
        '/Users/trentsmith/workspace/cryoet/cryoet-data-portal-backend/ingestion_tools/dataset_configs/tests/**/*.yaml',
        recursive=True)
    configs = itertools.chain(config_files, test_config_files)
    for config_file in configs:
        if "template" in config_file:
            continue
        migrate_config(config_file)
