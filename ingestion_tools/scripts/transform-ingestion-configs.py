import click
import yaml


@click.group()
def cli():
    pass


def update_file(filename: str) -> None:
    with open(filename, "r") as fh:
        data = yaml.safe_load(fh.read())
    standardization_config = data["standardization_config"]
    overrides = data.get("overrides_by_run")
    if overrides:
        standardization_config["overrides"] = []
        for item in overrides:
            new_override = {"match": {"run": item["run_regex"]}}
            if item.get("tiltseries"):
                new_override["metadata"] = {"tiltseries": item["tiltseries"]}
            if item.get("tomograms"):
                new_override["sources"] = {
                    "voxel_spacing": {"literal": {"value": [item["tomograms"]["voxel_spacing"]]}},
                }
            standardization_config["overrides"].append(new_override)
        del data["overrides_by_run"]
    if not standardization_config.get("dataset"):
        standardization_config["dataset"] = {
            "source": {"literal": {"value": [str(standardization_config.get("destination_prefix"))]}},
        }
        del standardization_config["destination_prefix"]
    if not standardization_config.get("run"):
        standardization_config["run"] = {
            "source": {
                "source_glob": {
                    "list_glob": standardization_config["run_glob"],
                    "match_regex": standardization_config["run_regex"],
                    "name_regex": standardization_config["run_name_regex"],
                },
            },
        }
        del standardization_config["run_glob"]
        del standardization_config["run_regex"]
        del standardization_config["run_name_regex"]
    if not standardization_config.get("gain"):
        standardization_config["gain"] = {
            "source": {
                "source_glob": {
                    "list_glob": standardization_config["gain_glob"],
                },
            },
        }
        del standardization_config["gain_glob"]
    if not standardization_config.get("frame"):
        standardization_config["frame"] = {
            "source": {
                "source_glob": {
                    "list_glob": standardization_config["frames_glob"],
                },
            },
        }
        del standardization_config["frames_glob"]
    if not standardization_config.get("tilt_series"):
        standardization_config["tilt_series"] = {
            "source": {
                "source_glob": {
                    "list_glob": standardization_config["tiltseries_glob"],
                    "name_regex": standardization_config.get("ts_name_regex", ".*"),
                },
            },
        }
        del standardization_config["tiltseries_glob"]
        if "ts_name_regex" in standardization_config:
            del standardization_config["ts_name_regex"]
    if not standardization_config.get("tomogram"):
        standardization_config["tomogram"] = {
            "source": {
                "source_glob": {
                    "list_glob": standardization_config["tomo_glob"],
                    "match_regex": standardization_config.get("tomo_regex", ".*"),
                },
            },
        }
        del standardization_config["tomo_glob"]
        if "tomo_regex" in standardization_config:
            del standardization_config["tomo_regex"]
    if not standardization_config.get("key_image"):
        if standardization_config.get("tomo_key_photo_glob"):
            standardization_config["key_image"] = {
                "source": {
                    "source_glob": {
                        "list_glob": standardization_config["tomo_key_photo_glob"],
                    },
                },
            }
            del standardization_config["tomo_key_photo_glob"]
    if not standardization_config.get("rawtilt"):
        standardization_config["rawtilt"] = {
            "source": {
                "source_multi_glob": {
                    "list_globs": standardization_config["rawtlt_files"],
                },
            },
        }
        del standardization_config["rawtlt_files"]
    if not standardization_config.get("voxel_spacing"):
        standardization_config["voxel_spacing"] = {
            "source": {
                "literal": {"value": [data["tomograms"]["voxel_spacing"]]},
            },
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
