import csv
import datetime
import json
import os
import re
from collections import defaultdict
from copy import deepcopy
from functools import partial
from typing import Any, Callable, Optional

import click
import yaml
from transform_ingestion_configs import update_config

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


def to_dataset_author(data: dict[str, Any]) -> list[dict[str, Any]]:
    authors_data = data["authors"]
    primary_author = set(authors_data["first_authors"])
    corresponding_authors = set(authors_data["corresponding_authors"])
    authors = [
        {
            "name": name,
            "primary_author_status": name in primary_author,
            "corresponding_author_status": name in corresponding_authors,
        }
        for name in authors_data["authors"]
    ]
    return sorted(
        authors,
        key=lambda x: (x["primary_author_status"], not x["corresponding_author_status"]),
        reverse=True,
    )


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
    dataset = data.get("dataset")

    config = {
        "dataset_identifier": dataset_id,
        "dataset_description": dataset["description"],
        "dataset_title": dataset["title"],
        "authors": authors,
        "organism": dataset["organism"],
        "sample_type": dataset["sample_type"],
        "sample_preparation": clean(dataset.get("sample_prep")),
        "grid_preparation": clean(dataset.get("grid_prep")),
        "dates": {
            "deposition_date": datetime.date(2023, 10, 1),
            "last_modified_date": datetime.date(2023, 12, 1),
            "release_date": datetime.date(2023, 12, 1),
        },
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
        config["cell_component"] = {"id": ",".join(ids)}
    if dataset["cellular_strain"]:
        config["cell_strain"] = dataset["cellular_strain"]
    if dataset["cell_type"]:
        cell_type = dataset["cell_type"]
        config["cell_type"] = {
            "id": cell_type.get("id") or cell_type.get("cell_type_id"),
            "name": cell_type.get("name") or cell_type.get("cell_name"),
        }
    if dataset["tissue"]:
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
            "{run_name}/rawdata/*.mdoc",
            "{run_name}/file_*/*.rawtlt",
            f"{{run_name}}/{tlt_tomo_path}/*.rawtlt",
        ],
        "tiltseries_glob": "{run_name}/rawdata/*",
        "ts_name_regex": r".*/rawdata/[^\._].*\.(mrc|st|ali)$",
        "tomo_format": "mrc",
        "tomo_glob": f"{{run_name}}/{tomo_path}",
        "tomo_regex": r".*\.(mrc|rec)$",
        "tomo_voxel_size": "",
        "tomo_key_photo_glob": "{run_name}/keyimg_{run_name}.jpg",
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
    "ts-tilt_axis",
    "ts-tilt_step",
    "ts-tilt_range-min",
    "ts-tilt_range-max",
}


def to_template_by_run(templates, run_data_map, prefix: str, path) -> dict[str, Any]:
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
    tilt_series = deepcopy(data["tilt_series"])
    microscope = tilt_series.get("microscope", {})
    phase_plate = microscope.pop("phase_plate")
    tilt_series["microscope_optical_setup"] = {
        "phase_plate": phase_plate if phase_plate else "None",
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


def normalize_invalid_to_none(value: str) -> str:
    return value if value else "None"


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
    templates = {}
    for entry in data:
        template = mapper(entry)
        metadata_key = json.dumps(template, separators=(",", ":"))

        if metadata_key not in templates:
            templates[metadata_key] = {"metadata": template, "sources": [entry["run_name"]]}
        else:
            templates[metadata_key]["sources"].append(entry["run_name"])

    if len(templates) <= 1:
        return next(iter(templates.values()), {}).get("metadata")

    print(f"{dataset_id} has {len(templates)} configs for {prefix}")
    return to_template_by_run(list(templates.values()), run_data_map, prefix, [])


@click.group()
@click.pass_context
def cli(ctx):
    pass


def get_deposition_map(input_dir: str) -> dict[int, int]:
    with open(os.path.join(input_dir, "portal_dataset_grouping.json"), "r") as file:
        groupings = json.load(file)

    deposition_id = 10014
    data = next(entry["data"] for entry in groupings if entry["type"] == "table" and entry["name"] == "SubDatasetData")

    dataset_deposition_id_mapping = {}
    deposition_id_mapping = {}
    for entry in data:
        dataset_group = int(entry["dataset_group"])
        if dataset_group not in deposition_id_mapping:
            deposition_id_mapping[dataset_group] = deposition_id
            deposition_id += 1
        dataset_id = int(entry["czportal_dataset_id"])
        dataset_deposition_id_mapping[dataset_id] = deposition_id_mapping[dataset_group]

    return dataset_deposition_id_mapping


def get_cross_reference_mapping(input_dir: str) -> dict[int, dict[str, str]]:
    with open(os.path.join(input_dir, "cross_references.json"), "r") as file:
        data = json.load(file)
    return {int(key): val for key, val in data.items()}


@cli.command()
@click.argument("input_dir", required=True, type=str)
@click.argument("output_dir", type=str, default="../dataset_configs/gjensen")
@click.pass_context
def create(ctx, input_dir: str, output_dir: str) -> None:
    fs = LocalFilesystem(force_overwrite=True)
    fs.makedirs(output_dir)
    run_data_map_path = os.path.join(output_dir, "run_data_map")
    run_tomo_map_path = os.path.join(output_dir, "run_tomo_map")
    run_frames_map_path = os.path.join(output_dir, "run_frames_map")
    fs.makedirs(run_data_map_path)
    fs.makedirs(run_tomo_map_path)
    fs.makedirs(run_frames_map_path)
    deposition_mapping = get_deposition_map(input_dir)
    cross_reference_mapping = get_cross_reference_mapping(input_dir)
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

        authors = to_dataset_author(val.get("dataset"))
        run_data_map = defaultdict(dict)
        dataset_config = {
            "dataset": to_dataset_config(dataset_id, val, authors, cross_reference_mapping.get(dataset_id, {})),
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
            "annotations": {},
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
        with open(dataset_config_file_path, "w") as outfile:
            yaml.dump(update_config(dataset_config), outfile, sort_keys=True)


if __name__ == "__main__":
    cli()
