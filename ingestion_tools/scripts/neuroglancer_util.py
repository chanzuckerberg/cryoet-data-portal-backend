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
@click.argument("graphql_url", required=False, type=str, default=STAGING_GRAPHQL_URL)
@click.argument("output_fileserver", required=False, type=str, default=STAGING_FILESERVER)
@click.option(
    "-rn-id",
    "--run-id",
    type=int,
    default=None,
    help="id of the run in the environment where we are fetching the neuroglancer config",
)
@click.option("-ds-id", "--dataset-id", type=int, default=None, help="Dataset id to which the run belongs")
@click.option("-rn", "--run-name", type=str, default=None, help="Name of the run")
@click.option(
    "--print-link",
    type=bool,
    is_flag=True,
    default=False,
    help="print the neuroglancer link to the consoles",
)
def translate_env(
    graphql_url,
    output_fileserver: str,
    run_id: int,
    dataset_id: int,
    run_name: str,
    print_link: bool,
) -> None:
    """
    Translate the neuroglancer links from one environment to another. You can either provide the run_id or the
    dataset_id and run_name.

    @param graphql_url: graphql url of the environment the client should point to, defaults to staging
    @param output_fileserver: fileserver of the environment the client should point to, defaults to staging
    @param run_id: id of the run in the environment where we are fetching the neuroglancer config
    @param dataset_id: dataset id to which the run belongs
    @param run_name: Name of the run
    @param print_link: print the neuroglancer link to the consoles
    This can be called from the command line as follows:

      python3 neuroglancer_util.py translate-env --run-id 123 --print-link
      python3 neuroglancer_util.py translate-env --rn-id 123

      python3 neuroglancer_util.py translate-env --run-name "TS_026" --dataset-id 10000
      python3 neuroglancer_util.py translate-env -rn "TS_026" -ds-id 10000
    """
    client = cdp.Client(graphql_url)
    if run_id:
        print_neuroglancer_links(run_id, client, output_fileserver, print_link)
    elif dataset_id and run_name:
        run = cdp.Run.find(client, [cdp.Run.dataset_id == dataset_id, cdp.Run.name == run_name])
        if not run:
            print(f"No run found for dataset_id={dataset_id} and run_name={run_name}")
            return
        print_neuroglancer_links(run[0].id, client, output_fileserver, print_link)
    else:
        print("Please provide either run_id or dataset_id and run_name")


if __name__ == "__main__":
    cli()
