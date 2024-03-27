import click
import yaml


@click.group()
@click.pass_context
def cli(ctx):
    pass


def update_file(filename: str) -> bool:
    with open(filename, "r") as fh:
        data = yaml.safe_load(fh.read())
    standardization_config = data["standardization_config"]
    if not standardization_config.get("dataset"):
        standardization_config["dataset"] = {"source": {"literal": {"value": [data.get("destination_prefix")]}}}
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
    if not standardization_config.get("frames"):
        standardization_config["frames"] = {
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
                    "name_regex": standardization_config["ts_name_regex"],
                },
            },
        }
        del standardization_config["tiltseries_glob"]
        del standardization_config["ts_name_regex"]
    if not standardization_config.get("tomogram"):
        standardization_config["tomogram"] = {
            "source": {
                "source_glob": {
                    "list_glob": standardization_config["tomo_glob"],
                    "match_regex": standardization_config["tomo_regex"],
                },
            },
        }
        del standardization_config["tomo_glob"]
        del standardization_config["tomo_regex"]
    if not standardization_config.get("key_image"):
        standardization_config["key_image"] = {
            "source": {
                "source_glob": {
                    "list_glob": standardization_config["tomo_key_photo_glob"],
                },
            },
        }
        del standardization_config["rawtlt_files"]
    if not standardization_config.get("rawtlt"):
        standardization_config["rawtlt"] = {
            "source": {
                "source_multi_glob": {
                    "list_globs": standardization_config["rawtlt_files"],
                },
            },
        }
        del standardization_config["rawtlt_files"]
    # TODO FIXME
    if not standardization_config.get("voxel_spacing"):
        standardization_config["voxel_spacing"] = {
            "source": {
                "source_glob": {
                    "list_glob": standardization_config["run_glob"],
                    "match_regex": standardization_config["run_regex"],
                    "name_regex": standardization_config["run_name_regex"],
                },
            },
        }

    with open(filename, "w") as fh:
        fh.write(yaml.dump(data))


@cli.command()
@click.argument("conf_file", required=True, type=str, nargs="*")
def upgrade(conf_file: list[str]) -> None:
    for filename in conf_file:
        update_file(filename)


if __name__ == "__main__":
    cli()
