"""
This script migrates the ingest config files to a new schema based on the changes outlines in
https://github.com/chanzuckerberg/cryoet-data-portal/issues/997
"""
import glob
import itertools
from typing import Union

import numpy as np
import yaml


def rawtilts_to_collection_metadata(config: dict) -> bool:
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

    return bool(list_globs)


def rawtilts_to_alignments(config: dict) -> bool:
    list_globs = []
    format_dict = {
        "IMOD": [],
        "ARETOMO3": [],
    }

    def valid_file(file):
        return any(file.endswith(ext) for ext in ['.tlt', ".xf", ".aln", ".com"])

    def get_format(file):
        if any(file.endswith(ext) for ext in ['.tlt', ".xf", ".com"]):
            format_dict["IMOD"].append(file)
        elif any(file.endswith(ext) for ext in ['.aln']):
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
                    alignment = {
                        "metadata": {"format": key},
                        "sources": [{"source_multi_glob": {"list_globs": files}}]}

                    if 'tomograms' in config:
                        for i in config['tomograms']:
                            if "metadata" not in i:
                                continue
                            affine_transformation_matrix = i["metadata"].pop("affine_transformation_matrix", None)
                            if affine_transformation_matrix:
                                alignment["metadata"]["affine_transformation_matrix"] = affine_transformation_matrix
                    config["alignments"].append(alignment)
    return bool(list_globs)


def update_tomogram_metadata(config: dict) -> bool:
    changed = False
    if tomograms := config.get("tomograms"):
        for tomogram in tomograms:
            if metadata := tomogram.get("metadata"):
                changed = True
                metadata["is_visualization_default"] = True
                try:
                    dates = config["depositions"][0]["metadata"]["dates"]
                except (KeyError, IndexError):
                    dates = {
                        "deposition_date": '1970-01-01',
                        "last_modified_date": '1970-01-01',
                        "release_date": '1970-01-01'}
                metadata["dates"] = dates
                affine_transformation_matrix = metadata.pop("affine_transformation_matrix", None)
                if affine_transformation_matrix and not np.allclose(affine_transformation_matrix, np.eye(4)):
                    ValueError("affine_transformation_matrix is not an identity matrix")
    return changed


def update_annotation_sources(config: dict) -> bool:
    changed = False
    if annotations := config.get('annotations'):
        for annotation in annotations:
            if sources := annotation.get("sources"):
                changed = True
                for source in sources:
                    for value in source.values():
                        value["is_portal_standard"] = False
    return changed


def remove_empty_fields(config: Union[list, dict]) -> bool:
    changed = False
    remove_key = []
    exclude_keys = ['annotations']
    if isinstance(config, list):
        for i in config:
            if isinstance(i, (list, dict)):
                changed = remove_empty_fields(i)
                if len(i) == 0:
                    remove_key.append(i)
        if remove_key:
            changed = True
            for key in remove_key:
                config.remove(key)
    elif isinstance(config, dict):
        for key, value in config.items():
            if isinstance(value, (list, dict)):
                changed = remove_empty_fields(value)
                if len(value) == 0:
                    remove_key.append(key)
        if remove_key:
            changed = True
            for key in remove_key:
                if key in exclude_keys:
                    continue
                config.pop(key)
    return changed


def migrate_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)

    changes: list[bool] = []
    try:
        changes.append(rawtilts_to_collection_metadata(config))
        changes.append(rawtilts_to_alignments(config))
        changes.append(update_tomogram_metadata(config))
    except Exception as e:
        print(f"Error in {get_relative_path(file_path)}: {e}")
        return

    if any(changes):
        remove_empty_fields(config)
        relative_path = file_path[file_path.find("cryoet-data-portal-backend"):]
        print(f"modified: {relative_path}")
        with open(file_path, 'w') as file:
            yaml.safe_dump(config, file)


def get_relative_path(file_path):
    return file_path[file_path.find("cryoet-data-portal-backend"):]


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
