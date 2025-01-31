import csv
import datetime
import json
import os
import re
from collections import defaultdict
from copy import deepcopy
from functools import partial
from typing import Any, Callable, Optional, Union

import click
import yaml
from schema_migration.upgrade import upgrade_config

from common.fs import LocalFilesystem
from common.normalize_fields import normalize_fiducial_alignment

RAW_PROCESSING_TYPES = {
    "raptor",
    "ctffind4, novactf, custom bash and matlab scripts;imod, ctffind4, novactf, custom bash and matlab scripts",
    "imod",
    "tomo3d",
    "batchruntomo",
    "imod, sirt-like",
    "warp, dynamo",
    "sirt",
    "raw",
}
RELATED_DATES = {
    "deposition_date": datetime.date(2023, 10, 1).strftime("%Y-%m-%d"),
    "last_modified_date": datetime.date(2023, 12, 1).strftime("%Y-%m-%d"),
    "release_date": datetime.date(2023, 12, 1).strftime("%Y-%m-%d"),
}


def get_json_data(input_dir: str, file_name: str) -> dict[str, Any]:
    with open(os.path.join(input_dir, file_name), "r") as file:
        data = json.load(file)
    return data


def to_author(authors_data: dict[str, Any], existing_author_obj: dict[str, Any] = None) -> list[dict[str, Any]]:
    """
    Convert authors data with first_authors and corresponding_authors to a list of author objects with
    primary_author_status and corresponding_author_status.
    If the optional existing_author_obj is provided, return the existing_author_obj if the newly created author object
    is the same.
    """
    primary_authors = set(authors_data["first_authors"])
    corresponding_authors = set(authors_data["corresponding_authors"])
    authors = [
        {
            "name": name,
            "primary_author_status": name in primary_authors,
            "corresponding_author_status": name in corresponding_authors,
        }
        for name in authors_data["authors"]
    ]
    new_author_obj = sorted(
        authors,
        key=lambda x: (x["primary_author_status"], not x["corresponding_author_status"]),
        reverse=True,
    )
    return existing_author_obj if existing_author_obj == new_author_obj else new_author_obj


def clean(val: str) -> str | None:
    if not val:
        return None

    return re.sub(
        r"[\xc2-\xf4][\x80-\xbf]+",
        lambda m: m.group(0).encode("latin1").decode("utf8"),
        val.replace("\r\n", ""),
    )


def to_dataset_config(
    dataset_id: int,
    data: dict[str, Any],
    authors: list[dict[str, Any]],
    cross_reference: dict[str, str] | None,
) -> dict[str, Any]:
    """
    Create dataset config from the dataset field's to the relevant config fields.
    :param dataset_id:
    :param data:
    :param authors:
    :param cross_reference:
    :return: Metadata entity for dataset and key photos
    """
    dataset = data.get("dataset")

    config = {
        "dataset_identifier": dataset_id,
        "dataset_description": dataset["description"].strip(),
        "dataset_title": dataset["title"].strip(),
        "authors": authors,
        "organism": dataset["organism"],
        "sample_type": dataset["sample_type"],
        "sample_preparation": clean(dataset.get("sample_prep")),
        "grid_preparation": clean(dataset.get("grid_prep")),
        "dates": RELATED_DATES,
    }

    run_name = next((entry["run_name"] for entry in data.get("runs") if "run_name" in entry), None)
    if run_name:
        prefix = f"cryoetportal-rawdatasets-dev/GJensen_full/{run_name}"
        config["key_photos"] = {
            "snapshot": f"{prefix}/keyimg_{run_name}.jpg",
            "thumbnail": f"{prefix}/keyimg_{run_name}_s.jpg",
        }

    if dataset["cellular_component"]:
        ids = [entry for entry in dataset["cellular_component"] if entry.startswith("GO")]
        if ids:
            config["cell_component"] = {"id": ",".join(ids)}
    if dataset["cellular_strain"] and (dataset["cellular_strain"].get("id") or dataset["cellular_strain"].get("name")):
        config["cell_strain"] = dataset["cellular_strain"]
    if dataset["cell_type"]:
        cell_type = dataset["cell_type"]
        config["cell_type"] = {
            "id": cell_type.get("id") or cell_type.get("cell_type_id"),
            "name": cell_type.get("name") or cell_type.get("cell_name"),
        }
        if not config["cell_type"]["id"] and not config["cell_type"]["name"]:
            del config["cell_type"]
    if dataset["tissue"] and (dataset["tissue"].get("id") or dataset["tissue"].get("name")):
        config["tissue"] = dataset["tissue"]
    if cross_reference:
        config["cross_references"] = cross_reference

    return config


def get_canonical_tomogram_name(run: dict[str, Any]) -> Optional[str]:
    """
    Get name of the tomogram to treat as Canonical when there are multiple tomograms for a run. Use sorting to find
    the first tomogram alphabetically.
    """
    names = list(run.get("tomograms", {}).keys())
    names.sort()
    return next(iter(names), None)


def to_standardization_config(
    dataset_id: int,
    data: dict[str, Any],
    run_data_map: dict,
    run_data_map_path: str,
    run_tomo_map_path: str,
    run_frames_map_path: str,
    deposition_id: int | None,
) -> dict[str, Any]:
    """
    Creates standardization config entity.This adds all the required path globs and regexes needed for the sources.
    """
    run_names = []
    mapped_tomo_name = {}
    run_has_multiple_tomos = False
    for run in data.get("runs"):
        run_names.append(run["run_name"])
        if len(run["tomograms"]) > 1:
            run_has_multiple_tomos = True
        mapped_tomo_name[run["run_name"]] = get_canonical_tomogram_name(run) or "*"

    tlt_tomo_path = "{mapped_frame_name}" if run_has_multiple_tomos else "3dimage_*"
    tomo_path = "{mapped_tomo_name}" if run_has_multiple_tomos else "3dimage_*/*"

    config = {
        "deposition_id": deposition_id,
        "destination_prefix": str(dataset_id),
        "source_prefix": "GJensen_full",
        "frames_glob": None,
        "gain_glob": None,
        "rawtlt_files": [
            "{run_name}/*/*.mdoc", # The mdoc files can be in rawdata or file_* folders
            "{run_name}/generated/*.mdoc",
            "{run_name}/file_*/*.rawtlt",
            "{run_name}/generated/*.rawtlt",
            f"{{run_name}}/{tlt_tomo_path}/*.rawtlt",
        ],
        "tiltseries_glob": "{run_name}/rawdata/*",
        "ts_name_regex": r".*/rawdata/[^\._].*\.(mrc|st|ali)$",
        "tomo_format": "mrc",
        "tomo_glob": f"{{run_name}}/{tomo_path}",
        "tomo_regex": r".*\.(mrc|rec)$",
        "tomo_voxel_size": "",
        # "tomo_key_photo_glob": "{run_name}/keyimg_{run_name}.jpg",
        "run_glob": "*",
        "run_regex": f'({"|".join(run_names)})$',
        "run_name_regex": "(.*)",
    }

    if run_data_map:
        run_data_map_file = os.path.join(run_data_map_path, f"{dataset_id}.csv")
        with open(run_data_map_file, "w") as csvfile:
            fieldnames = ["run_name"] + sorted(next(iter(run_data_map.values())).keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for run_name, value in run_data_map.items():
                writer.writerow({"run_name": run_name} | value)

        config["run_data_map_file"] = f"run_data_map/{dataset_id}.csv"

    if run_has_multiple_tomos:
        run_tomo_map_file = os.path.join(run_tomo_map_path, f"{dataset_id}.csv")
        with open(run_tomo_map_file, "w") as csvfile:
            fieldnames = ["run_name", "mapped_tomo_name"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # writer.writeheader()
            for run_name, value in mapped_tomo_name.items():
                writer.writerow({"run_name": run_name, "mapped_tomo_name": value})

        config["run_to_tomo_map_csv"] = f"run_tomo_map/{dataset_id}.csv"

        run_frames_map_file = os.path.join(run_frames_map_path, f"{dataset_id}.csv")
        with open(run_frames_map_file, "w") as csvfile:
            fieldnames = ["run_name", "mapped_frame_name"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # writer.writeheader()
            for run_name, value in mapped_tomo_name.items():
                writer.writerow({"run_name": run_name, "mapped_frame_name": value.split("/")[0]})

        config["run_to_frame_map_csv"] = f"run_frames_map/{dataset_id}.csv"

    return config


int_fields = {"ts-tilt_series_quality"}
float_fields = {
    "tomo-voxel_spacing",
    "ts-pixel_spacing",
    "ts-spherical_aberration_constant",
    "ts-tilt_axis",
    "ts-tilt_step",
    "ts-tilt_range-min",
    "ts-tilt_range-max",
    "ts-total_flux",
}


def to_template_by_run(templates, run_data_map, prefix: str, path: list[str]) -> dict[str, Any]:
    """
    Iterates over the templates and extracting the metadata for each template. It then collects all the keys from the
    templates and generates a template that provides values for all the runs.
    For each key, it gets the corresponding value in the metadata. If it's a dictionary, it recursively calls itself
    with the updated path. If it's a list, it creates a set of distinct values.
    If there is only one distinct value, it uses that value in the template metadata.
    If there are multiple distinct values, it creates a formatted string keyed on the prefix and field name. It creates
    entries in run_data_map for each run and assigns the corresponding value from the metadata to that key.
    The function returns the generated template.
    """
    template_metadata = {}
    all_keys = set()

    templates_for_path = []
    for entry in templates:
        entry_md = entry["metadata"]
        for path_key in path:
            entry_md = entry_md.get(path_key, {})
        templates_for_path.append({"metadata": entry_md, "sources": entry["sources"]})
        all_keys = all_keys.union(entry_md.keys())

    for key in sorted(all_keys):
        if any(isinstance(entry["metadata"].get(key), dict) for entry in templates_for_path):
            template_metadata[key] = to_template_by_run(templates, run_data_map, f"{prefix}-{key}", path + [key])
        else:
            if any(isinstance(entry["metadata"].get(key), list) for entry in templates_for_path):
                distinct_vals = {str(entry["metadata"].get(key)) for entry in templates_for_path}
            else:
                distinct_vals = {entry["metadata"].get(key) for entry in templates_for_path}
            if len(distinct_vals) == 1:
                template_metadata[key] = templates_for_path[0]["metadata"].get(key)
            else:
                run_data_map_key = f"{prefix}-{key}"
                if run_data_map_key in int_fields:
                    template_metadata_value = f"int {{{run_data_map_key}}}"
                elif run_data_map_key in float_fields:
                    template_metadata_value = f"float {{{run_data_map_key}}}"
                else:
                    template_metadata_value = f"{{{run_data_map_key}}}"
                template_metadata[key] = template_metadata_value
                for entry in templates_for_path:
                    for source in entry["sources"]:
                        run_data_map[source][run_data_map_key] = entry["metadata"].get(key)
    return template_metadata


def to_tiltseries(data: dict[str, Any]) -> dict[str, Any]:
    tilt_series_path = data["tilt_series"].get("tilt_series_path")
    if not tilt_series_path:
        return {}

    tilt_series = deepcopy(data["tilt_series"])
    microscope = tilt_series.get("microscope", {})
    microscope["additional_info"] = microscope.pop("additional_scope_info", "")
    phase_plate = microscope.pop("phase_plate")
    tilt_series["microscope_optical_setup"] = {
        "phase_plate": "volta phase plate" if phase_plate is True else phase_plate if phase_plate else None,
        "image_corrector": microscope.pop("image_corrector"),
        "energy_filter": microscope.pop("engergy_filter"),
    }
    if "manufactorer" in tilt_series["camera"]:
        tilt_series["camera"]["manufacturer"] = tilt_series["camera"].pop("manufactorer", None)
    tilt_series["is_aligned"] = tilt_series.pop("tilt_series_is_aligned", False)
    tilt_series["tilt_range"] = {
        "min": tilt_series.pop("tilt_range_min"),
        "max": tilt_series.pop("tilt_range_max"),
    }

    tilt_series["tilt_series_quality"] = 4 if len(data["tomograms"]) else 1
    tilt_series["pixel_spacing"] = round(tilt_series["pixel_spacing"], 3) if tilt_series.get("pixel_spacing") else None

    tilt_series.pop("tilt_series_path", None)
    return tilt_series


def normalize_invalid_to_none(value: str) -> Union[str, None]:
    return value if value else None


def normalize_processing(input_processing: str) -> str:
    if not input_processing:
        return "raw"
    input_processing = input_processing.lower()

    if "filtered" in input_processing:
        return "filtered"
    elif input_processing == "denoised":
        return "denoised"
    elif input_processing in RAW_PROCESSING_TYPES:
        return "raw"


def to_tomogram(
    authors: list[dict[str, Any]],
    data: dict[str, Any],
) -> [dict[str, Any] | Any]:
    canonical_tomogram_name = get_canonical_tomogram_name(data)
    tomogram = deepcopy(data["tomograms"][canonical_tomogram_name]) if canonical_tomogram_name else {}
    if len(data["tomograms"].keys()) > 1:
        print(
            f'{data["run_name"]} has {len(data["tomograms"].values())} tomograms: '
            f'{",".join(set(data["tomograms"].keys()))}',
        )

    tomogram["fiducial_alignment_status"] = normalize_fiducial_alignment(
        tomogram.get("fiducial_alignment_status", False),
    )
    tomogram["offset"] = {"x": 0, "y": 0, "z": 0}
    tomogram["affine_transformation_matrix"] = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    tomogram["authors"] = authors
    tomogram["tomogram_version"] = 1
    tomogram["reconstruction_method"] = normalize_invalid_to_none(tomogram.get("reconstruction_method"))
    if tomogram["reconstruction_method"] == "Weighted back projection":
        tomogram["reconstruction_method"] = "WBP"
    tomogram["reconstruction_software"] = normalize_invalid_to_none(tomogram.get("reconstruction_software"))
    tomogram["align_software"] = "+".join(tomogram.pop("align_softwares", []))
    tomogram["processing"] = normalize_processing(tomogram.get("processing"))

    tomogram["voxel_spacing"] = round(tomogram["voxel_spacing"], 3) if "voxel_spacing" in tomogram else None

    return tomogram


def to_config_by_run(
    dataset_id: int,
    data: list,
    run_data_map: dict,
    mapper: Callable[[dict[str, Any]], dict[str, Any]],
    prefix: str,
) -> dict[str, Any]:
    """
     The method iterates over the runs in the dataset and gets all the distinct metadata by applying the mapper. It also
     keeps track of the runs that have each unique metadata.

     If number of distinct metadata == 0, it returns an empty dictionary.
     If number of distinct metadata == 1, it returns the metadata.
     If number of distinct metadata > 1, it creates a metadata with formatted string for fields that have different values,
    and adds the relevant fields to run_data_map.
    """
    templates = {}
    for entry in data:
        template = mapper(entry)
        if not template:
            continue
        metadata_key = json.dumps(template, separators=(",", ":"))

        if metadata_key not in templates:
            templates[metadata_key] = {"metadata": template, "sources": [entry["run_name"]]}
        else:
            templates[metadata_key]["sources"].append(entry["run_name"])

    if len(templates) == 0:
        return {}
    elif len(templates) <= 1:
        return next(iter(templates.values()), {}).get("metadata")

    print(f"{dataset_id} has {len(templates)} configs for {prefix}")
    return to_template_by_run(list(templates.values()), run_data_map, prefix, [])


@click.group()
@click.pass_context
def cli(ctx):
    pass


def get_deposition_id_mapping() -> dict[str, int]:
    """
    Hard coding this to prevent changes in the deposition ids due to external changes.
    """
    return {
        "8": 10014,
        "109": 10015,
        "158": 10016,
        "179": 10017,
        "68": 10018,
        "299": 10019,
        "224": 10020,
        "335": 10021,
        "241": 10022,
        "90": 10023,
        "181": 10024,
        "191": 10025,
        "311": 10026,
        "162": 10027,
        "173": 10028,
        "240": 10029,
        "91": 10030,
        "211": 10031,
        "180": 10032,
        "190": 10033,
        "126": 10034,
        "304": 10035,
        "143": 10036,
        "330": 10037,
        "102": 10038,
        "167": 10039,
        "337": 10040,
        "352": 10041,
        "243": 10042,
        "376": 10043,
        "327": 10044,
        "101": 10045,
        "186": 10046,
        "285": 10047,
        "182": 10048,
        "60": 10049,
        "161": 10050,
        "130": 10051,
        "104": 10052,
        "377": 10053,
        "348": 10054,
        "238": 10055,
        "188": 10056,
        "209": 10057,
    }


def get_deposition_map(input_dir: str) -> dict[int, int]:
    """
    Get mapping of dataset ids to deposition ids. The data for this is sourced from the portal_dataset_grouping.json
    file in the input directory.
    :param input_dir:
    :return: dict of dataset_id to deposition_id
    """
    deposition_id_mapping = get_deposition_id_mapping()
    deposition_id = max(deposition_id_mapping.values()) + 1
    data = next(
        entry["data"]
        for entry in get_json_data(input_dir, "portal_dataset_grouping.json")
        if entry["type"] == "table" and entry["name"] == "SubDatasetData"
    )

    dataset_deposition_id_mapping = {}
    data.sort(key=lambda x: x["czportal_dataset_id"])
    for entry in data:
        dataset_group = entry["dataset_group"]
        if dataset_group not in deposition_id_mapping:
            deposition_id_mapping[dataset_group] = deposition_id
            deposition_id += 1
            if deposition_id >= 10300:
                raise ValueError("Exceeded the maximum valid deposition id for Jensen datasets.")
        dataset_id = int(entry["czportal_dataset_id"])
        dataset_deposition_id_mapping[dataset_id] = deposition_id_mapping[dataset_group]

    return dataset_deposition_id_mapping


def clean_delimited_values(delimited_values: str, delimiter: str = ",") -> list[str]:
    return [r.strip() for r in delimited_values.split(delimiter)]


def create_deposition_entity_map(
    input_dir: str,
    cross_reference_mapping: dict[int, dict[str, str]],
    deposition_id_mapping: dict[int, int],
) -> dict[int, dict[str, Any]]:
    """
    Create deposition entity metadata for the config. The data is created from combining fields from
    deposition_dataset.json with data from the related dataset's cross-references.
    :param input_dir:
    :param cross_reference_mapping:
    :param deposition_id_mapping:
    :return: dict of deposition_id to deposition entity meppings
    """
    deposition_map = {}
    for entry in get_json_data(input_dir, "deposition_dataset.json"):
        deposition_ids = set()
        publications = set()
        related_database_entries = set()
        for ds_id in entry["portal_dataset_ids"]:
            deposition_ids.add(deposition_id_mapping.get(ds_id))
            ds_cross_reference = cross_reference_mapping.get(ds_id, {})
            if publication := ds_cross_reference.get("publications"):
                publications.update(clean_delimited_values(publication))
            if related_database_entry := ds_cross_reference.get("related_database_entries"):
                related_database_entries.update(clean_delimited_values(related_database_entry))

        entry_metadata = entry.get("deposition", {})
        if len(deposition_ids) != 1:
            print(f"Deposition ids found for {entry_metadata['deposition_title']}: {deposition_ids}")
            raise ValueError("Only one deposition ids should be mapped to a single deposition")

        deposition_id = deposition_ids.pop()
        metadata = {
            "authors": to_author(entry_metadata["deposition_authors"]),
            "dates": RELATED_DATES,
            "deposition_description": entry_metadata["deposition_description"].strip(),
            "deposition_identifier": deposition_id,
            "deposition_title": entry_metadata["deposition_title"].strip(),
            "deposition_types": ["dataset"],
        }
        cross_reference = {}
        if publications:
            cross_reference["publications"] = ",".join(sorted(publications))
        if related_database_entries:
            cross_reference["related_database_entries"] = ",".join(sorted(related_database_entries))
        if cross_reference:
            metadata["cross_references"] = cross_reference

        deposition_map[deposition_id] = {
            "metadata": metadata,
            "sources": [{"literal": {"value": [deposition_id]}}],
        }

    return deposition_map


def update_cross_reference(config) -> dict[str, str]:
    if config and "dataset_publications" in config:
        publications = clean_delimited_values(config.pop("dataset_publications").replace("https://doi.org/", ""))
        config["publications"] = ",".join(sorted(publications))
    if config and config.get("related_database_entries"):
        related_database_entries = sorted(clean_delimited_values(config.pop("related_database_entries")))
        config["related_database_entries"] = ",".join(related_database_entries)
    return config


def get_cross_reference_mapping(input_dir: str) -> dict[int, dict[str, str]]:
    """
    Get cross-references mapping for the dataset ids. The data for this is sourced from the cross_references.json file in
    the input directory.
    :param input_dir:
    :return: formatted cross-reference mapping keyed on dataset_id
    """
    return {
        int(key): update_cross_reference(val) for key, val in get_json_data(input_dir, "cross_references.json").items()
    }


def exclude_runs_parent_filter(entities: list, runs_to_exclude: list[str]) -> None:
    for entity in entities:
        for source in entity["sources"]:
            if "parent_filters" not in source:
                source["parent_filters"] = {}
            if "exclude" not in source["parent_filters"]:
                source["parent_filters"]["exclude"] = {}
            if "run" not in source["parent_filters"]["exclude"]:
                source["parent_filters"]["exclude"]["run"] = []
            source["parent_filters"]["exclude"]["run"].extend(runs_to_exclude)


@cli.command()
@click.argument("input_dir", required=True, type=str)
@click.argument("output_dir", type=str, default="../dataset_configs/gjensen")
@click.pass_context
def create(ctx, input_dir: str, output_dir: str) -> None:
    """
    Create dataset configs for Grant Jensen datasets from the data czii-data-portal-processing repository. The db data
    is store in the path czii-data-portal-processing/src/data_portal_processing/jensendb.
    Requires the latest version of https://github.com/czimaginginstitute/czii-data-portal-processing repository's
    src/data_portal_processing/jensendb to be available locally.
    :param ctx:
    :param input_dir: Path to the local jensendb directory containing the input files. "
    :param output_dir: The output directory to store the dataset configs.
    :return:
    """
    fs = LocalFilesystem(force_overwrite=True)
    fs.makedirs(output_dir)
    run_data_map_path = os.path.join(output_dir, "run_data_map")
    run_tomo_map_path = os.path.join(output_dir, "run_tomo_map")
    run_frames_map_path = os.path.join(output_dir, "run_frames_map")
    fs.makedirs(run_data_map_path)
    fs.makedirs(run_tomo_map_path)
    fs.makedirs(run_frames_map_path)
    cross_reference_mapping = get_cross_reference_mapping(input_dir)
    deposition_mapping = get_deposition_map(input_dir)
    deposition_entity_by_id = create_deposition_entity_map(input_dir, cross_reference_mapping, deposition_mapping)
    file_paths = fs.glob(os.path.join(input_dir, "portal_[0-9]*.json"))
    file_paths.sort()
    for file_path in file_paths:
        with open(file_path, "r") as file:
            val = json.load(file)
        print(f"Processing file {file_path}")
        dataset_id = val.get("dataset", {}).get("czportal_dataset_id")
        if not dataset_id or dataset_id > 10300:
            print(f"Skipping dataset with id: {dataset_id}")
            continue

        deposition_entity = deposition_entity_by_id.get(deposition_mapping.get(dataset_id))
        authors = to_author(val.get("dataset")["authors"], deposition_entity.get("metadata", {}).get("authors"))

        run_data_map = defaultdict(dict)
        dataset_config = {
            "dataset": to_dataset_config(dataset_id, val, authors, cross_reference_mapping.get(dataset_id, {})),
            "depositions": [deposition_entity],
            "runs": {},
            "tiltseries": to_config_by_run(
                dataset_id,
                val.get("runs"),
                run_data_map,
                partial(to_tiltseries),
                "ts",
            ),
            "tomograms": to_config_by_run(
                dataset_id,
                val.get("runs"),
                run_data_map,
                partial(to_tomogram, authors),
                "tomo",
            ),
            "annotations": [],
            "standardization_config": to_standardization_config(
                dataset_id,
                val,
                run_data_map,
                run_data_map_path,
                run_tomo_map_path,
                run_frames_map_path,
                deposition_mapping.get(dataset_id),
            ),
        }

        print(f"Writing file for {dataset_id}")
        dataset_config_file_path = os.path.join(output_dir, f"{dataset_id}.yaml")

        # Update the config formatting to a newer version
        updated_dataset_config = upgrade_config(dataset_config)
        # Remove empty tiltseries when all tiltseries associated to the dataset have no metadata
        if all(not ts.get("metadata") for ts in updated_dataset_config.get("tiltseries", [])):
            updated_dataset_config.pop("tiltseries")
        # Add filter to exclude tiltseries that have no file path specified
        elif runs_without_tilt := [
            f"^{run['run_name']}$" for run in val.get("runs") if not run.get("tilt_series", {}).get("tilt_series_path")
        ]:
            exclude_runs_parent_filter(updated_dataset_config.get("tiltseries", []), runs_without_tilt)
        # Add filter to exclude runs for tomograms that have no tomograms specified
        if runs_without_tomogram := [f"^{run['run_name']}$" for run in val.get("runs") if not run.get("tomograms")]:
            exclude_runs_parent_filter(updated_dataset_config.get("voxel_spacings", []), runs_without_tomogram)

        with open(dataset_config_file_path, "w") as outfile:
            yaml.dump(updated_dataset_config, outfile, sort_keys=True)


if __name__ == "__main__":
    cli()
