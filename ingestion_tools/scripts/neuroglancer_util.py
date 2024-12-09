import json
import urllib.parse
import webbrowser

import click
import cryoet_data_portal as cdp

STAGING_GRAPHQL_URL = "https://genuine-satyr.staging-cryoet.staging.czi.team/graphql"
STAGING_FILESERVER = "https://files.cryoet.staging.si.czi.technology/"

PROD_FILESERVER = "https://files.cryoetdataportal.cziscience.com/"


@click.group()
@click.pass_context
def cli(ctx):
    pass


def print_neuroglancer_links(run_id: int, client: cdp.Client, dest_fileserver: str, print_link: bool):
    run = cdp.Run.get_by_id(client, run_id)
    for tomogram in run.tomograms:
        if neuroglancer_config := tomogram.neuroglancer_config:
            new_config = neuroglancer_config.replace(PROD_FILESERVER, dest_fileserver)
            config_json = json.loads(new_config)
            ng_url = "https://neuroglancer-demo.appspot.com/#!" + urllib.parse.quote(
                json.dumps(config_json, separators=(",", ":")),
            )
            if print_link:
                print(f"Tomogram id={tomogram.id} processing={tomogram.processing}")
                print(ng_url + "\n" * 3)
            webbrowser.open(ng_url, new=0, autoraise=True)


@cli.command()
@click.argument("run_id", required=True, type=int)
@click.argument("graphql_url", required=False, type=str, default=STAGING_GRAPHQL_URL)
@click.argument("output_fileserver", required=False, type=str, default=STAGING_FILESERVER)
@click.option("--print-link", type=bool, is_flag=True, default=False)
def translate_env(run_id: int, graphql_url, output_fileserver: str, print_link: bool):
    print_neuroglancer_links(run_id, cdp.Client(graphql_url), output_fileserver, print_link)


if __name__ == "__main__":
    cli()
