from typing import Any

import click
import yaml


@click.group()
def cli():
    pass


def create_deposition_metadata(deposition_id: str, config_data: dict[str, Any]) -> dict[str, Any]:
    dataset = config_data.get("datasets", [])
    metadata = dataset[0].get("metadata", {}) if dataset else {}
    if metadata:
        deposition_types = ["dataset"]
    elif config_data.get("tomograms"):
        metadata = config_data["tomograms"][0].get("metadata", {})
        deposition_types = ["tomogram"]
    elif config_data.get("annotations"):
        metadata = config_data["annotations"][0].get("metadata", {})
        deposition_types = ["annotation"]

    return {
        "deposition_identifier": deposition_id,
        "deposition_title": "TBA",
        "deposition_description": "TBA",
        "deposition_types": deposition_types,
        "dates": metadata.get("dates", {}),
        "authors": metadata.get("authors", []),
    }


def has_no_sources(data: list[dict[str, Any]] | dict[str, Any]) -> bool:
    return isinstance(data, dict) or not any(row.get("sources") for row in data)


def rawtilts_to_alignments(data: dict) -> None:
    list_globs = []
    format_dict = {
        "IMOD": [],
        "ARETOMO3": [],
    }

    def valid_file(file):
        return any(file.endswith(ext) for ext in ['.tlt', ".xf", ".aln", ".com", ".txt", ".csv", ".tiltx"])

    def get_format(file):
        if any(file.endswith(ext) for ext in ['.tlt', ".xf", ".com", ".xtlt"]):
            format_dict["IMOD"].append(file)
        elif any(file.endswith(ext) for ext in ['.aln', ".txt", ".csv"]):
            format_dict["ARETOMO3"].append(file)

    if len(data.get('tomograms', [])) > 1 or len(data.get("rawtilts", [])) > 1:
        raise ValueError("More than one tomogram or rawtilt")

    if 'rawtilts' in data:
        for i in data['rawtilts']:
            if "sources" not in i:
                continue
            old_source = i["sources"][0]["source_multi_glob"]["list_globs"]
            list_globs.extend(s for s in old_source if valid_file(s))
            for source in list_globs:
                old_source.remove(source)
                get_format(source)
        if list_globs:
            if 'alignments' not in data:
                data['alignments'] = []
            for key, files in format_dict.items():
                if files:
                    # check if there is an alignment with the key in the metadata.format
                    alignment = [a for a in data.get("alignments", []) if a["metadata"]["format"] == key]
                    if alignment:
                        alignment = alignment.pop()
                    else:
                        alignment = {
                            "metadata": {"format": key},
                            "sources": [{"source_multi_glob": {"list_globs": files}}]}

                    if 'tomograms' in data:
                        for i in data['tomograms']:
                            if "metadata" not in i:
                                continue
                            affine_transformation_matrix = i["metadata"].get("affine_transformation_matrix", None)
                            if affine_transformation_matrix and np.allclose(affine_transformation_matrix,np.eye(4)):
                                # skip if is an idenity matrix
                                continue
                            if affine_transformation_matrix:
                                alignment["metadata"]["affine_transformation_matrix"] = affine_transformation_matrix
                    data["alignments"].append(alignment)


def update_config(data: dict[str, Any]) -> dict[str, Any]:
    standardization_config = data["standardization_config"]
    if data.get("overrides_by_run"):
        # We only have two datasets that specify overrides. It's easier to just
        # translate these manually than deal with automating it.
        del data["overrides_by_run"]
    if not data.get("datasets"):
        if not data["standardization_config"]["deposition_id"]:
            data["standardization_config"]["deposition_id"] = data["dataset"]["dataset_identifier"]
        data["datasets"] = [
            {
                "metadata": data.get("dataset"),
                "sources": [{"literal": {"value": [str(standardization_config.get("destination_prefix"))]}}],
            },
        ]
        del data["dataset"]
    if not data.get("runs"):
        data["runs"] = [
            {
                "sources": [
                    {
                        "source_glob": {
                            "list_glob": standardization_config["run_glob"],
                            "match_regex": standardization_config["run_regex"],
                            "name_regex": standardization_config["run_name_regex"],
                        },
                    },
                ],
            },
        ]
    if not data.get("gains") and standardization_config.get("gain_glob"):
        data["gains"] = [
            {
                "sources": [
                    {
                        "source_glob": {
                            "list_glob": standardization_config["gain_glob"],
                        },
                    },
                ],
            },
        ]
    if not data.get("frames") and standardization_config.get("frames_glob"):
        data["frames"] = [
            {
                "sources": [
                    {
                        "source_glob": {
                            "list_glob": standardization_config["frames_glob"],
                        },
                    },
                ],
            },
        ]
    if has_no_sources(data.get("tiltseries", [])) and standardization_config.get("tiltseries_glob"):
        data["tiltseries"] = [
            {
                "metadata": data.get("tiltseries"),
                "sources": [
                    {
                        "source_glob": {
                            "list_glob": standardization_config["tiltseries_glob"],
                            "match_regex": standardization_config.get("ts_name_regex", ".*"),
                        },
                    },
                ],
            },
        ]
    if has_no_sources(data.get("tomograms", [])) and standardization_config.get("tomo_glob"):
        data["tomograms"] = [
            {
                "metadata": data.get("tomograms"),
                "sources": [
                    {
                        "source_glob": {
                            "list_glob": standardization_config["tomo_glob"],
                            "match_regex": standardization_config.get("tomo_regex", ".*"),
                        },
                    },
                ],
            },
        ]
    if not data.get("depositions"):
        deposition_id = data["standardization_config"]["deposition_id"]
        data["depositions"] = [
            {
                "metadata": data.get(
                    "deposition",
                    create_deposition_metadata(deposition_id, data),
                ),
                "sources": [{"literal": {"value": [deposition_id]}}],
            },
        ]
    if not data.get("dataset_keyphotos") and [d for d in data["datasets"] if d.get("metadata")]:
        if data["datasets"][0]["metadata"].get("key_photos"):
            keyphotos = data["datasets"][0]["metadata"]["key_photos"]
            del data["datasets"][0]["metadata"]["key_photos"]
        else:
            keyphotos = {"snapshot": None, "thumbnail": None}

        data["dataset_keyphotos"] = [
            {
                "sources": [
                    {
                        # TODO what if we don't have keyphotos defined?
                        "literal": {"value": keyphotos},
                    },
                ],
            },
        ]
    if not data.get("key_images") and [d for d in data["datasets"] if d.get("metadata")]:
        if standardization_config.get("tomo_key_photo_glob"):
            # TODO what if we don't have key images defined?
            data["key_images"] = [
                {
                    "sources": [
                        {
                            "source_glob": {
                                "list_glob": standardization_config["tomo_key_photo_glob"],
                            },
                        },
                    ],
                },
            ]
        else:
            data["key_images"] = [
                {
                    "sources": [
                        {
                            "literal": {
                                "value": ["from_tomogram"],
                            },  # This is just a placeholder when keyphotos are created from their parent tomos.
                        },
                    ],
                },
            ]
    if not data.get("rawtilts") and standardization_config.get("rawtlt_files"):
        data["rawtilts"] = [
            {
                "sources": [
                    {
                        "source_multi_glob": {
                            "list_globs": standardization_config["rawtlt_files"],
                        },
                    },
                ],
            },
        ]
    if not data.get("voxel_spacings"):
        vs = data["tomograms"][0]["metadata"]["voxel_spacing"]
        # Make sure voxel spacing is a float.
        if isinstance(vs, str) and "{" in vs and not vs.strip().startswith("float"):
            vs = f"float {vs}"
        data["voxel_spacings"] = [
            {
                "sources": [
                    {
                        "literal": {"value": [vs]},
                    },
                ],
            },
        ]
    valid_standardization_keys = [
        "deposition_id",
        "source_prefix",
        "run_to_frame_map_csv",
        "run_data_map_file",
        "run_to_tomo_map_csv",
        "run_to_ts_map_csv",
    ]
    data["standardization_config"] = {
        k: v for k, v in data["standardization_config"].items() if k in valid_standardization_keys
    }
    return data


def update_file(filename: str) -> None:
    with open(filename, "r") as fh:
        data = yaml.safe_load(fh.read())

    data = update_config(data)

    with open(filename, "w") as fh:
        fh.write(yaml.dump(data))


@cli.command()
@click.argument("conf_file", required=True, type=str, nargs=-1)
def upgrade(conf_file: list[str]) -> None:
    for filename in conf_file:
        update_file(filename)


if __name__ == "__main__":
    cli()
