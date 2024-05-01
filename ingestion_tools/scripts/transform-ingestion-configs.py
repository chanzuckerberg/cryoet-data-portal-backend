import click
import yaml


@click.group()
def cli():
    pass


def update_file(filename: str) -> None:
    with open(filename, "r") as fh:
        data = yaml.safe_load(fh.read())
    standardization_config = data["standardization_config"]
    if data.get("overrides_by_run")
        # We only have two datasets that specify overrides. It's easier to just
        # translate these manually than deal with automating it.
        del data["overrides_by_run"]
    if not data.get("datasets"):
        data["datasets"] = [{
            "metadata": {data.get("dataset")},
            "sources": [{"literal": {"value": [str(standardization_config.get("destination_prefix"))]}}],
        }]
        del data["dataset"]
        del standardization_config["destination_prefix"]
    if not data.get("runs"):
        data["runs"] = [{
            "metadata": {data.get("run")},
            "sources": [{
                "source_glob": {
                    "list_glob": standardization_config["run_glob"],
                    "match_regex": standardization_config["run_regex"],
                    "name_regex": standardization_config["run_name_regex"],
                },
            }],
        }]
        del standardization_config["run_glob"]
        del standardization_config["run_regex"]
        del standardization_config["run_name_regex"]
        del data["run"]
    if not data.get("gains"):
        standardization_config["gains"] = [{
            "sources": [{
                "source_glob": {
                    "list_glob": standardization_config["gain_glob"],
                },
            }],
        }]
        del standardization_config["gain_glob"]
    if not data.get("frames"):
        standardization_config["frames"] = [{
            "sources": [{
                "source_glob": {
                    "list_glob": standardization_config["frames_glob"],
                },
            }],
        }]
        del standardization_config["frames_glob"]
    if not data.get("tiltseries", {}).get("sources"):
        data["tiltseries"] = [{
            "metadata": {data.get("tiltseries")},
            "sources": [{
                "source_glob": {
                    "list_glob": standardization_config["tiltseries_glob"],
                    "name_regex": standardization_config.get("ts_name_regex", ".*"),
                },
            }],
        }]
        del standardization_config["tiltseries_glob"]
        if "ts_name_regex" in standardization_config:
            del standardization_config["ts_name_regex"]
    if not data.get("tomograms", {}).get("sources"):
        data["tomograms"] = [{
            "metadata": {data.get("tomogram")},
            "sources": [{
                "source_glob": {
                    "list_glob": standardization_config["tomo_glob"],
                    "match_regex": standardization_config.get("tomo_regex", ".*"),
                },
            }],
        }]
        del standardization_config["tomo_glob"]
        if "tomo_regex" in standardization_config:
            del standardization_config["tomo_regex"]
    if not data.get("neuroglancer"):
        standardization_config["neuroglancer"] = [{
            "sources": [{
                "literal": {"value": ["from_tomogram"]},  # This is just a placeholder when keyphotos are created from their parent tomos.
            }],
        }]
    # TODO should we instantiate a finder for each image size?
    if not data.get("dataset_keyphotos"):
        standardization_config["dataset_keyphotos"] = [{
            "sources": [{
                "literal": {"value": ["from_dataset"]},  # This is just a placeholder when keyphotos are created from their parent tomos.
            }],
        }]
    if not data.get("key_images"):
        if standardization_config.get("tomo_key_photo_glob"):
            standardization_config["key_images"] = [{
                "sources": [{
                    "source_glob": {
                        "list_glob": standardization_config["tomo_key_photo_glob"],
                    },
                }],
            }]
        else:
            standardization_config["key_images"] = [{
                "sources": [{
                    "literal": {"value": ["from_tomogram"]},  # This is just a placeholder when keyphotos are created from their parent tomos.
                }],
            }]
            del standardization_config["tomo_key_photo_glob"]
    if not data.get("rawtilts"):
        data["rawtilts"] = [{
            "sources": [{
                "source_multi_glob": {
                    "list_glob": standardization_config["rawtlt_files"],
                },
            }],
        }]
        del standardization_config["rawtlt_files"]
    if not data.get("voxel_spacing"):
        data["voxel_spacings"] = [{
            "sources": [{
                "literal": {"value": [data["tomograms"]["voxel_spacing"]]},
            }],
        }]

    with open(filename, "w") as fh:
        fh.write(yaml.dump(data))


@cli.command()
@click.argument("conf_file", required=True, type=str, nargs=-1)
def upgrade(conf_file: list[str]) -> None:
    for filename in conf_file:
        update_file(filename)


if __name__ == "__main__":
    cli()
