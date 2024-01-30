import click
import yaml

from common.formats import tojson


@click.group()
def cli():
    pass


@cli.command()
@click.argument("yaml_file", required=True, type=str)
def tojson(yaml_file: str):
    with open(yaml_file, "r") as fh:
        data = yaml.safe_load(fh.read())
    print(tojson(data))


if __name__ == "__main__":
    cli()
