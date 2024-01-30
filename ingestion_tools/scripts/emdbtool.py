from typing import Optional

import click
import requests
import yaml

from common.merge import deep_merge


def fetch_orcid(orcid):
    response = requests.get(
        f"https://orcid.org/{orcid}/public-record.json",
        headers={"accept": "application/json"},
    )
    return response.json()


def get_orcid_name(orcid):
    data = fetch_orcid(orcid)
    return data["displayName"]


def fetch_emdb(emdb_id):
    response = requests.get(
        f"https://www.ebi.ac.uk/emdb/api/entry/{emdb_id}",
        headers={"accept": "application/json"},
    )
    return response.json()


def fetch_emdb_publications(emdb_id):
    response = requests.get(
        f"https://www.ebi.ac.uk/emdb/api/entry/publications/{emdb_id}",
        headers={"accept": "application/json"},
    )
    return response.json()


def fetch_emdb_imaging(emdb_id):
    response = requests.get(
        f"https://www.ebi.ac.uk/emdb/api/entry/imaging/{emdb_id}",
        headers={"accept": "application/json"},
    )
    return response.json()


def fetch_emdb_annotations(emdb_id: str):
    emdb_id_with_prefix = emdb_id if emdb_id.startswith("EMD-") else f"EMD-{emdb_id}"
    response = requests.get(
        f"https://www.ebi.ac.uk/emdb/api/annotations/{emdb_id_with_prefix}",
        headers={"accept": "application/json"},
    )
    return response.json()


def fetch_emdb_image_acquisition(emdb_id):
    response = requests.get(
        f"https://www.ebi.ac.uk/emdb/api/entry/image_acquisition/{emdb_id}",
        headers={"accept": "application/json"},
    )
    return response.json()


def fetch_emdb_sample(emdb_id):
    response = requests.get(
        f"https://www.ebi.ac.uk/emdb/api/entry/sample/{emdb_id}",
        headers={"accept": "application/json"},
    )
    return response.json()


def fetch_emdb_experiment(emdb_id):
    response = requests.get(
        f"https://www.ebi.ac.uk/emdb/api/entry/experiment/{emdb_id}",
        headers={"accept": "application/json"},
    )
    return response.json()


@click.group()
def cli():
    pass


@cli.command()
@click.argument("emdb_id", required=True, type=str)
def fetch(emdb_id):
    info = fetch_emdb(emdb_id)
    print(yaml.dump(info))


@cli.command()
@click.argument("emdb_id", required=True, type=str)
def fetch_experiment(emdb_id):
    info = fetch_emdb_experiment(emdb_id)
    print(yaml.dump(info))


@cli.command()
@click.argument("emdb_id", required=True, type=str)
def fetch_sample(emdb_id):
    info = fetch_emdb_sample(emdb_id)
    print(yaml.dump(info))


@cli.command()
@click.argument("emdb_id", required=True, type=str)
def fetch_image_acquisition(emdb_id):
    info = fetch_emdb_image_acquisition(emdb_id)
    print(yaml.dump(info))


@cli.command()
@click.argument("emdb_id", required=True, type=str)
def fetch_imaging(emdb_id):
    info = fetch_emdb_imaging(emdb_id)
    print(yaml.dump(info))


@cli.command()
@click.argument("emdb_id", required=True, type=str)
def fetch_publications(emdb_id):
    info = fetch_emdb_publications(emdb_id)
    print(yaml.dump(info))


@cli.command()
@click.argument("emdb_id", required=True, type=str)
def fetch_annotations(emdb_id):
    info = fetch_emdb_annotations(emdb_id)
    print(yaml.dump(info))


@cli.command()
@click.argument("emdb_id", required=True, type=str)
def fetch_all(emdb_id):
    info = fetch_emdb(emdb_id)
    print(yaml.dump(info))
    info = fetch_emdb_experiment(emdb_id)
    print(yaml.dump(info))
    info = fetch_emdb_sample(emdb_id)
    print(yaml.dump(info))
    try:
        info = fetch_emdb_image_acquisition(emdb_id)
        print(yaml.dump(info))
    except:
        print("Fetching image acquisition failed")
    info = fetch_emdb_imaging(emdb_id)
    print(yaml.dump(info))
    info = fetch_emdb_publications(emdb_id)
    print(yaml.dump(info))
    info = fetch_emdb_annotations(emdb_id)
    print(yaml.dump(info))


@cli.command()
@click.argument("emdb_id", required=True, type=str)
@click.option(
    "--merge", required=False, type=str, help="Merge in another metadata document"
)
def convert(emdb_id, merge):
    dataset_data = convert_dataset(emdb_id)
    tiltseries_data = convert_tiltseries(emdb_id)
    tomogram_data = convert_tomogram(emdb_id)
    annotations = convert_annotations(emdb_id)

    result = {
        "dataset": dataset_data,
        "tiltseries": tiltseries_data,
        "tomograms": tomogram_data,
        "annotations": annotations,
    }

    merge_data = {}
    if merge:
        with open(merge, "r") as fh:
            merge_data = yaml.safe_load(fh.read())

    result = deep_merge(merge_data, result)
    print(yaml.dump(result, sort_keys=False))


def convert_tomogram(emdb_id):
    experiment = fetch_emdb_experiment(emdb_id)
    reconstruction = experiment["structure_determination_list"][
        "structure_determination"
    ][0]["image_processing"][0]["final_reconstruction"]
    reconstruction_method = reconstruction.get("algorithm")
    if reconstruction_method == "BACK PROJECTION":
        reconstruction_method = "Weighted back projection"
    doc = {
        "voxel_spacing": None,
        "fiducial_alignment_status": None,
        "reconstruction_method": reconstruction_method,
        "reconstruction_software": ", ".join(
            [
                item["name"]
                for item in reconstruction.get("software_list", {}).get("software", [])
            ]
        ),
    }
    return doc


def convert_tiltseries(emdb_id):
    experiment = fetch_emdb_experiment(emdb_id)
    microscope = experiment["structure_determination_list"]["structure_determination"][
        0
    ]["microscopy_list"]["microscopy"][0]
    acceleration_voltage = int(microscope["acceleration_voltage"]["valueOf_"])
    ac_voltage_units = microscope["acceleration_voltage"]["units"]
    if ac_voltage_units.lower() == "kv":
        acceleration_voltage *= 1000
    energy_filter = (
        microscope.get("specialist_optics", {}).get("energy_filter", {}).get("name")
    )
    phase_plate = microscope.get("specialist_optics", {}).get("phase_plate", None)
    doc = {
        "microscope": {
            "manufacturer": microscope["microscope"].split()[0],
            "model": " ".join(microscope["microscope"].split()[1:]),
        },
        "spherical_aberration_constant": 2.7,
        "microscope_optical_setup": {
            "energy_filter": energy_filter,
            "phase_plate": phase_plate,
            "image_corrector": None,
        },
        "camera": {
            "manufacturer": microscope["image_recording_list"]["image_recording"][0][
                "film_or_detector_model"
            ]["valueOf_"].split()[0],
            "model": " ".join(
                microscope["image_recording_list"]["image_recording"][0][
                    "film_or_detector_model"
                ]["valueOf_"]
                .split("(")[0]  # filter out resolution
                .split()[1:]
            ),
        },
        "acceleration_voltage": acceleration_voltage,
    }
    try:
        phase_plate = microscope["specialist_optics"]["phase_plate"]
        doc["microscope_optical_setup"]["phase_plate"] = phase_plate
    except KeyError:
        pass
    try:
        energy_filter = microscope["specialist_optics"]["energy_filter"]["name"]
        doc["microscope_optical_setup"]["energy_filter"] = energy_filter
    except KeyError:
        pass
    return doc


def get_empiar_image_urls(related_databases: list[str]) -> Optional[dict[str, str]]:
    for entry in related_databases:
        if not entry.startswith("EMPIAR-"):
            continue
        id = entry.replace("EMPIAR-", "")
        urls = [
            f"https://www.ebi.ac.uk/pdbe/emdb-empiar/entryIcons/{name}.gif"
            for name in [f"{id}-l", f"{id}"]
        ]

        if all(list([requests.get(url).ok for url in urls])):
            return {"snapshot": urls[0], "thumbnail": urls[1]}
    return None


def convert_dataset(emdb_id):
    info = fetch_emdb(emdb_id)
    annotations = fetch_emdb_annotations(emdb_id)
    authors = []
    # Try harder to get ORCID's
    orcids = {
        item["title"]: item["id"]
        for item in annotations["annotations"].get("ORCID", [])
    }
    for item in info["crossreferences"]["citation_list"]["primary_citation"][
        "citation_type"
    ]["author"]:
        orcid = item.get("ORCID")
        if not orcid:
            orcid = orcids.get(item["valueOf_"])
        if orcid:
            # There's a data entry error in emdb for some datasets :(
            if item["valueOf_"] == "Goetz SK":
                orcid = "0000-0002-9903-3667"
            authors.append({"name": get_orcid_name(orcid), "ORCID": orcid})
        else:
            authors.append({"name": item["valueOf_"]})
    publications = []
    for item in info["crossreferences"]["citation_list"]["primary_citation"][
        "citation_type"
    ]["external_references"]:
        if item["type_"] == "DOI":
            publications.append(item["valueOf_"])

    related_databases = []
    if "EMPIAR" in annotations["annotations"]:
        related_databases = [
            item["id"] for item in annotations["annotations"]["EMPIAR"]
        ]

    organism = None
    try:
        organism = info["sample"]["supramolecule_list"]["supramolecule"][0][
            "natural_source"
        ][0]["organism"]["valueOf_"]
    except KeyError:
        pass
    if not organism:
        organism = info["sample"]["supramolecule_list"]["supramolecule"][0][
            "sci_species_name"
        ]["valueOf_"]

    metadata_doc = {
        "dataset_title": info["sample"]["name"]["valueOf_"],
        "authors": authors,
        "organism": {"name": organism},
        "cross_references": {
            "dataset_publications": ", ".join(publications),
            "related_database_entries": ", ".join(related_databases)
        },
        "funding": [
            {"funding_agency_name": item["funding_body"], "grant_id": item.get("code")}
            for item in info["admin"]["grant_support"]["grant_reference"]
            if "funding_body" in item
        ],
        "key_photos": get_empiar_image_urls(related_databases),
    }

    experiment = fetch_emdb_experiment(emdb_id)
    sample_prep = experiment["structure_determination_list"]["structure_determination"][
        0
    ]["specimen_preparation_list"]["specimen_preparation"][0]
    sample_prep_list = []
    for k, v in sample_prep.items():
        if k in ("grid", "preparation_id", "sectioning"):
            continue
        if isinstance(v, dict):
            for ksub, vsub in v.items():
                sample_prep_list.append(f"{k}_{ksub}: {vsub}")
        else:
            sample_prep_list.append(f"{k}: {v}")

    grid_prep_list = []
    for k, v in sample_prep.get("grid", {}).items():
        if isinstance(v, list):
            v = v[0]
        if isinstance(v, dict):
            for ksub, vsub in v.items():
                grid_prep_list.append(f"{k}_{ksub}: {vsub}")
        else:
            grid_prep_list.append(f"{k}: {v}")

    metadata_doc["sample_preparation"] = ", ".join(sample_prep_list)
    metadata_doc["grid_preparation"] = ", ".join(grid_prep_list)
    return metadata_doc


def convert_annotations(emdb_id):
    annotations = fetch_emdb_annotations(emdb_id)
    annotation_authors = [
        {"name": get_orcid_name(item["id"]), "ORCID": item["id"]}
        for item in annotations["annotations"].get("ORCID", [])
    ]

    metadata_doc = {
        "authors": annotation_authors,
    }

    return metadata_doc


if __name__ == "__main__":
    cli()
