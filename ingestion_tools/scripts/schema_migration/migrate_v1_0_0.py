import logging
from typing import Any

logger = logging.getLogger(__name__)


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


def upgrade(data: dict[str, Any]) -> dict[str, Any]:
    standardization_config = data["standardization_config"]
    data["version"] = "1.0.0"
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
