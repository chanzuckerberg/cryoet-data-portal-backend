import click

from schema_migration.upgrade import upgrade_file


@click.group()
def cli():
    pass


@cli.command(help="Upgrade a config file to the latest version.")
@click.argument("conf_file", required=True, type=str, nargs=-1)
def upgrade(conf_file: list[str]) -> None:
    """

    To add a new version upgrade function, add a new function that takes the data
    dictionary and returns the updated data dictionary. Then add the function to
    the VERSION_MAP dictionary with the key being the version to upgrade from.
    """
    for filename in conf_file:
        upgrade_file(filename)
