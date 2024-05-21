import click
import yaml


@click.group()
def cli():
    pass


def update_file(filename: str) -> None:
    with open(filename, "r") as fh:
        data = yaml.safe_load(fh.read())
    standardization_config = data["standardization_config"]
    if data.get("overrides_by_run"):
        # We only have two datasets that specify overrides. It's easier to just
        # translate these manually than deal with automating it.
        del data["overrides_by_run"]
    if not data.get("datasets"):
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
    if not data.get("tiltseries", {}).get("sources") and standardization_config.get("tiltseries_glob"):
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
    if not data.get("tomograms", {}).get("sources"):
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
    if not data.get("dataset_keyphotos") and data["datasets"][0]["metadata"].get("key_photos"):
        data["dataset_keyphotos"] = [
            {
                "sources": [
                    {
                        # TODO what if we don't have keyphotos defined?
                        "literal": {"value": data["datasets"][0]["metadata"]["key_photos"]},
                    },
                ],
            },
        ]
        del data["datasets"][0]["metadata"]["key_photos"]
    if not data.get("key_images"):
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
                            "list_glob": standardization_config["rawtlt_files"],
                        },
                    },
                ],
            },
        ]
    if not data.get("voxel_spacing"):
        vs = data["tomograms"][0]["metadata"]["voxel_spacing"]
        # Make sure voxel spacing is a float.
        if isinstance(vs, str) and "{" in vs:
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

    with open(filename, "w") as fh:
        fh.write(yaml.dump(data))


@cli.command()
@click.argument("conf_file", required=True, type=str, nargs=-1)
def upgrade(conf_file: list[str]) -> None:
    for filename in conf_file:
        update_file(filename)


if __name__ == "__main__":
    cli()
