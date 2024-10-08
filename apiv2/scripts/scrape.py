# Copies data from a v1 GraphQL api into a v2 database.
import contextlib
import json
import os
from concurrent.futures import ProcessPoolExecutor, as_completed

import click
import cryoet_data_portal as cdp
import requests
from database import models
from support.enums import tomogram_reconstruction_method_enum as reconstruction_enum

from platformics.database.connect import init_sync_db

# cleanup:
# delete from deposition_type; delete from annotation_author; delete from dataset_author; delete from deposition_author; delete from annotation_file ; delete from annotation_shape ; delete from dataset_funding; delete from tomogram_author; delete from tomogram; delete from annotation; delete from annotation; delete from tomogram_voxel_spacing; delete from per_section_alignment_parameters; delete from per_section_parameters; delete from alignment; delete from frame; delete from tiltseries; delete from run; delete from run; delete from dataset; delete from deposition;

# CLIENT_URL="https://graphql-cryoet-api.cryoet.staging.si.czi.technology/v1/graphql"
CLIENT_URL = "https://graphql.cryoetdataportal.cziscience.com/v1/graphql"


# Adapted from https://github.com/sqlalchemy/sqlalchemy/wiki/UniqueObject
def get_or_create(session, cls, row_id, filters, data):
    query = session.query(cls)
    for filter in filters:
        query = query.where(filter)
    obj = query.first()
    if obj:
        for k, v in data.items():
            try:
                setattr(obj, k, v)
            except:
                print(cls)
                print(data)
                raise
    else:
        obj = cls(id=row_id, **data)
        session.add(obj)
    return obj


def add(session, model, item, parents):
    remote_item = item
    # Sometimes we send in a dict instead of an object, so it's ok to ignore errors here.
    with contextlib.suppress(AttributeError):
        remote_item = item.to_dict()

    local_item_data = {}

    # Set some default arguments for `get_or_create` that can be mutated for special cases below.
    new_item_id = remote_item.get("id")
    find_item_filters = [(model.id == new_item_id)]

    if model == models.DepositionAuthor:
        local_item_data = {
            "deposition_id": remote_item["deposition_id"],
            "author_list_order": remote_item["author_list_order"],
            "name": remote_item["name"],
            "email": remote_item["email"],
            "affiliation_name": remote_item["affiliation_name"],
            "affiliation_address": remote_item["affiliation_address"],
            "affiliation_identifier": remote_item["affiliation_identifier"],
            "corresponding_author_status": remote_item["corresponding_author_status"],
            "primary_author_status": remote_item["primary_author_status"],
            "orcid": remote_item["orcid"],
        }
    if model == models.DepositionType:
        local_item_data = {
            "deposition_id": parents["deposition_id"],
            "type": remote_item["deposition_types"],
        }
        new_item_id = None
        find_item_filters = [
            (models.DepositionType.deposition_id == parents["deposition_id"]),
            (models.DepositionType.type == remote_item["deposition_types"]),
        ]
    if model == models.Deposition:
        local_item_data = {
            "title": remote_item["title"],
            "description": remote_item["description"],
            "deposition_publications": remote_item["deposition_publications"],
            "related_database_entries": remote_item["related_database_entries"],
            "deposition_date": remote_item["deposition_date"],
            "release_date": remote_item["release_date"],
            "last_modified_date": remote_item["last_modified_date"],
            "key_photo_url": remote_item["key_photo_url"],
            "key_photo_thumbnail_url": remote_item["key_photo_thumbnail_url"],
        }
    if model == models.Annotation:
        local_item_data = {
            # "primary_author_status": remote_item.get["primary_annotator_status"],
            # "corresponding_author_status": remote_item.get("corresponding_annotator_status"),
            "run_id": parents["run_id"],
            "deposition_id": parents["deposition_id"],  # Doesn't exist in the old api.
            "s3_metadata_path": remote_item["s3_metadata_path"],
            "https_metadata_path": remote_item["https_metadata_path"],
            "annotation_publication": remote_item["annotation_publication"],
            "annotation_method": remote_item["annotation_method"],
            "ground_truth_status": remote_item["ground_truth_status"],
            "object_id": remote_item["object_id"],
            "object_name": remote_item["object_name"],
            "object_description": remote_item["object_description"],
            "object_state": remote_item["object_state"],
            "object_count": remote_item["object_count"],
            "confidence_precision": remote_item["confidence_precision"],
            "confidence_recall": remote_item["confidence_recall"],
            "ground_truth_used": remote_item["ground_truth_used"],
            "annotation_software": remote_item["annotation_software"],
            "is_curator_recommended": remote_item["is_curator_recommended"],
            "method_type": remote_item["method_type"],
            "deposition_date": remote_item["deposition_date"],
            "release_date": remote_item["release_date"],
            "last_modified_date": remote_item["last_modified_date"],
        }
    if model == models.AnnotationMethodLink:
        local_item_data = {
            "annotation_id": parents["annotation_id"],
            "link_type": remote_item["link_type"],
            "name": remote_item["custom_name"],
            "link": remote_item["link"],
        }
        new_item_id = None
        find_item_filters = [
            (models.AnnotationMethodLink.annotation_id == parents["annotation_id"]),
            (models.AnnotationMethodLink.link_type == remote_item["link_type"]),
            (models.AnnotationMethodLink.name == remote_item["custom_name"]),
        ]
    if model == models.AnnotationAuthor:
        if "author_list_order" not in remote_item:
            remote_item["author_list_order"] = 1  # TODO FIXME this isn't quite accurate!
        local_item_data = {
            "annotation_id": parents["annotation_id"],
            "author_list_order": remote_item["author_list_order"],
            "orcid": remote_item["orcid"],
            "name": remote_item["name"],
            "email": remote_item["email"],
            "affiliation_name": remote_item["affiliation_name"],
            "affiliation_address": remote_item["affiliation_address"],
            "affiliation_identifier": remote_item["affiliation_identifier"],
            "corresponding_author_status": remote_item["corresponding_author_status"],
        }
        if remote_item.get("primary_annotator_status") or remote_item.get("primary_annotator_status"):
            local_item_data["primary_author_status"] = True
        if remote_item.get("corresponding_annotator_status") or remote_item.get("corresponding_annotator_status"):
            local_item_data["corresponding_author_status"] = True
    if model == models.AnnotationFile:
        # Get-Or-Create annotation shapes first.
        shape_data = {
            "annotation_id": parents["annotation_id"],
            "shape_type": remote_item["shape_type"],
        }
        shape = get_or_create(
            session,
            models.AnnotationShape,
            remote_item[
                "id"
            ],  # The first annotation file/shape to be inserted will get the previous annotation file id
            [
                (models.AnnotationShape.annotation_id == parents["annotation_id"]),
                (models.AnnotationShape.shape_type == remote_item["shape_type"]),
            ],
            shape_data,
        )
        session.add(shape)

        local_item_data = {
            "alignment_id": parents["alignment_id"],  # Doesn't exist in the old API
            "annotation_shape_id": shape.id,
            "tomogram_voxel_spacing_id": parents["tomogram_voxel_spacing_id"],
            "format": remote_item["format"],
            "s3_path": remote_item["s3_path"],
            "https_path": remote_item["https_path"],
            "is_visualization_default": remote_item["is_visualization_default"],
            # "source": remote_item["source"], # Doesn't exist in the old api
        }

    if model == models.Dataset:
        local_item_data = {
            "deposition_id": remote_item["deposition_id"],
            "title": remote_item["title"],
            "description": remote_item["description"],
            "organism_name": remote_item["organism_name"],
            "organism_taxid": remote_item["organism_taxid"],
            "tissue_name": remote_item["tissue_name"],
            "tissue_id": remote_item["tissue_id"],
            "cell_name": remote_item["cell_name"],
            "cell_type_id": remote_item["cell_type_id"],
            "cell_strain_name": remote_item["cell_strain_name"],
            "cell_strain_id": remote_item["cell_strain_id"],
            "sample_type": remote_item["sample_type"].lower(),  # Value change to lowercase
            "sample_preparation": remote_item["sample_preparation"],
            "grid_preparation": remote_item["grid_preparation"],
            "other_setup": remote_item["other_setup"],
            "key_photo_url": remote_item["key_photo_url"],
            "key_photo_thumbnail_url": remote_item["key_photo_thumbnail_url"],
            "cell_component_name": remote_item["cell_component_name"],
            "cell_component_id": remote_item["cell_component_id"],
            "deposition_date": remote_item["deposition_date"],
            "release_date": remote_item["release_date"],
            "last_modified_date": remote_item["last_modified_date"],
            "dataset_publications": remote_item["dataset_publications"],  # Field name change
            "related_database_entries": remote_item["related_database_entries"],
            "s3_prefix": remote_item["s3_prefix"],
            "https_prefix": remote_item["https_prefix"],
        }
    if model == models.DatasetAuthor:
        local_item_data = {
            "dataset_id": remote_item["dataset_id"],
            "author_list_order": remote_item["author_list_order"],
            "name": remote_item["name"],
            "email": remote_item["email"],
            "affiliation_name": remote_item["affiliation_name"],
            "affiliation_address": remote_item["affiliation_address"],
            "affiliation_identifier": remote_item["affiliation_identifier"],
            "corresponding_author_status": remote_item["corresponding_author_status"],
            "primary_author_status": remote_item["primary_author_status"],
            "orcid": remote_item["orcid"],
        }
    if model == models.DatasetFunding:
        local_item_data = {
            "dataset_id": parents["dataset_id"],
            "funding_agency_name": remote_item["funding_agency_name"],
            "grant_id": remote_item["grant_id"],
        }
    if model == models.Run:
        local_item_data = {
            "dataset_id": parents["dataset_id"],
            "name": remote_item["name"],
            "s3_prefix": remote_item["s3_prefix"],
            "https_prefix": remote_item["https_prefix"],
        }
    if model == models.Tiltseries:
        local_item_data = {
            "run_id": parents["run_id"],
            "deposition_id": parents["deposition_id"],  # We don't have deposition id's yet
            "s3_omezarr_dir": remote_item["s3_omezarr_dir"],
            "s3_mrc_file": remote_item["s3_mrc_bin1"],
            "https_omezarr_dir": remote_item["https_omezarr_dir"],
            "https_mrc_file": remote_item["https_mrc_bin1"],
            "s3_angle_list": remote_item["s3_angle_list"],
            "https_angle_list": remote_item["https_angle_list"],
            "acceleration_voltage": remote_item["acceleration_voltage"],
            "spherical_aberration_constant": remote_item["spherical_aberration_constant"],
            "microscope_manufacturer": remote_item["microscope_manufacturer"],
            "microscope_model": remote_item["microscope_model"],
            "microscope_energy_filter": remote_item["microscope_energy_filter"],
            "microscope_phase_plate": remote_item["microscope_phase_plate"],
            "microscope_image_corrector": remote_item["microscope_image_corrector"],
            "microscope_additional_info": remote_item["microscope_additional_info"],
            "camera_manufacturer": remote_item["camera_manufacturer"],
            "camera_model": remote_item["camera_model"],
            "tilt_min": remote_item["tilt_min"],
            "tilt_max": remote_item["tilt_max"],
            "tilt_range": remote_item["tilt_range"],
            "tilt_step": remote_item["tilt_step"],
            "tilting_scheme": remote_item["tilting_scheme"],
            "tilt_axis": remote_item["tilt_axis"],
            "total_flux": remote_item["total_flux"],
            "data_acquisition_software": remote_item["data_acquisition_software"],
            "related_empiar_entry": remote_item["related_empiar_entry"],
            "binning_from_frames": remote_item["binning_from_frames"],
            "tilt_series_quality": remote_item["tilt_series_quality"],
            "is_aligned": remote_item["is_aligned"],
            "pixel_spacing": remote_item["pixel_spacing"],
            "aligned_tiltseries_binning": remote_item["aligned_tiltseries_binning"],
        }
    if model == models.TomogramAuthor:
        local_item_data = {
            "tomogram_id": parents["tomogram_id"],
            "author_list_order": remote_item["author_list_order"],
            "orcid": remote_item["orcid"],
            "name": remote_item["name"],
            "email": remote_item["email"],
            "affiliation_name": remote_item["affiliation_name"],
            "affiliation_address": remote_item["affiliation_address"],
            "affiliation_identifier": remote_item["affiliation_identifier"],
            "corresponding_author_status": remote_item["corresponding_author_status"],
            "primary_author_status": remote_item["primary_author_status"],
        }
    if model == models.Alignment:
        if not remote_item.get("affine_transformation_matrix"):
            remote_item["affine_transformation_matrix"] = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        local_item_data = {
            "affine_transformation_matrix": json.dumps(remote_item["affine_transformation_matrix"]),  # Json handling
            "volume_x_dimension": remote_item["size_x"] * parents["voxel_spacing"],  # Key name change
            "volume_y_dimension": remote_item["size_y"] * parents["voxel_spacing"],  # Key name change
            "volume_z_dimension": remote_item["size_z"] * parents["voxel_spacing"],  # Key name change
            "tiltseries_id": parents.get("tiltseries_id"),  # Key name change
            "run_id": parents["run_id"],  # Key name change
            "deposition_id": parents["deposition_id"],  # Key name change
        }
    if model == models.Tomogram:
        local_item_data = {
            "alignment_id": parents["alignment_id"],
            "deposition_id": parents["deposition_id"],
            "tomogram_voxel_spacing_id": parents["tomogram_voxel_spacing_id"],
            "run_id": parents["run_id"],
            "name": remote_item["name"],
            "size_x": remote_item["size_x"],
            "size_y": remote_item["size_y"],
            "size_z": remote_item["size_z"],
            "voxel_spacing": remote_item["voxel_spacing"],
            "fiducial_alignment_status": remote_item["fiducial_alignment_status"],
            "processing": remote_item["processing"],
            "tomogram_version": remote_item["tomogram_version"],
            "processing_software": remote_item["processing_software"],
            "reconstruction_software": remote_item["reconstruction_software"],
            "is_author_submitted": remote_item["is_canonical"],
            "is_portal_standard": False,
            "is_standardized": False,
            "is_visualization_default": False,
            "s3_omezarr_dir": remote_item["s3_omezarr_dir"],
            "https_omezarr_dir": remote_item["https_omezarr_dir"],
            "s3_mrc_file": remote_item["s3_mrc_scale0"],
            "https_mrc_file": remote_item["https_mrc_scale0"],
            "scale0_dimensions": remote_item["scale0_dimensions"],
            "scale1_dimensions": remote_item["scale1_dimensions"],
            "scale2_dimensions": remote_item["scale2_dimensions"],
            "ctf_corrected": remote_item["ctf_corrected"],
            "offset_x": remote_item["offset_x"],
            "offset_y": remote_item["offset_y"],
            "offset_z": remote_item["offset_z"],
            "key_photo_url": remote_item["key_photo_url"],
            "key_photo_thumbnail_url": remote_item["key_photo_thumbnail_url"],
            "neuroglancer_config": remote_item["neuroglancer_config"],
        }
        # Special handling for converting values.
        reconstruction_method = remote_item["reconstruction_method"].lower()
        if "wbp" in reconstruction_method or "weighted" in reconstruction_method:
            local_item_data["reconstruction_method"] = reconstruction_enum.WBP
        elif "sirt" in reconstruction_method or "iterative" in reconstruction_method:
            local_item_data["reconstruction_method"] = reconstruction_enum.SIRT
        elif "sart" in reconstruction_method or "algebraic" in reconstruction_method:
            local_item_data["reconstruction_method"] = reconstruction_enum.SART
        elif "fourier" in reconstruction_method:
            local_item_data["reconstruction_method"] = reconstruction_enum.Fourier_Space
        else:
            local_item_data["reconstruction_method"] = reconstruction_enum.Unknown
    if model == models.TomogramVoxelSpacing:
        local_item_data = {
            "run_id": parents["run_id"],
            "voxel_spacing": remote_item["voxel_spacing"],
            "s3_prefix": remote_item["s3_prefix"],
            "https_prefix": remote_item["https_prefix"],
        }
    item = get_or_create(
        session,
        model,
        new_item_id,  # Use the possibly-mutated value assigned above
        find_item_filters,  # Use the possibly-mutated value assigned above
        local_item_data,
    )

    session.add(item)
    session.flush()
    return item


def import_deposition(deposition_id: int):
    db = init_sync_db(
        f"postgresql+psycopg://{os.environ['PLATFORMICS_DATABASE_USER']}:{os.environ['PLATFORMICS_DATABASE_PASSWORD']}@{os.environ['PLATFORMICS_DATABASE_HOST']}:{os.environ['PLATFORMICS_DATABASE_PORT']}/{os.environ['PLATFORMICS_DATABASE_NAME']}",
    )
    client = cdp.Client(CLIENT_URL)
    dep = cdp.Deposition.get_by_id(client, deposition_id)
    with db.session() as session:
        print(f"processing {dep.id}")
        d = add(session, models.Deposition, dep, {})
        # TODO this is assuming only a single deposition type per deposition in the old db!
        for deptype in dep.deposition_types.split(","):
            add(session, models.DepositionType, {"deposition_types": deptype}, {"deposition_id": dep.id})
        for author in cdp.DepositionAuthor.find(client, [cdp.DepositionAuthor.deposition_id == d.id]):
            add(session, models.DepositionAuthor, author, {"deposition_id": d.id})
        print(f"deposition {dep.id} done")
        session.commit()


# Method links isn't exposed by the v2 client for some reason
def fetch_method_links(annotation):
    headers = {
        "Content-type": "application/json",
    }
    query = (
        """
        query MyQuery {
            annotations(where: {id: {_eq: %d }}) {
                method_links
            }
        }
    """
        % annotation.id
    )
    payload = json.dumps({"query": query, "variables": None, "operationName": "MyQuery"})
    res = requests.post(CLIENT_URL, headers=headers, data=payload)
    data = res.json()
    anno = data["data"]["annotations"][0]
    if anno and anno.get("method_links"):
        return anno["method_links"]
    return []


def import_dataset(dataset_id: int):
    db = init_sync_db(
        f"postgresql+psycopg://{os.environ['PLATFORMICS_DATABASE_USER']}:{os.environ['PLATFORMICS_DATABASE_PASSWORD']}@{os.environ['PLATFORMICS_DATABASE_HOST']}:{os.environ['PLATFORMICS_DATABASE_PORT']}/{os.environ['PLATFORMICS_DATABASE_NAME']}",
    )
    client = cdp.Client(CLIENT_URL)
    dataset = cdp.Dataset.get_by_id(client, dataset_id)
    with db.session() as session:
        print(f"processing {dataset_id}")
        ds = add(session, models.Dataset, dataset, {})
        parents = {"deposition_id": ds.deposition_id, "dataset_id": ds.id}
        for dsauthor in cdp.DatasetAuthor.find(client, [cdp.DatasetAuthor.dataset_id == dataset.id]):
            add(session, models.DatasetAuthor, dsauthor, parents)
        for dsfunding in cdp.DatasetFunding.find(client, [cdp.DatasetFunding.dataset_id == dataset.id]):
            add(session, models.DatasetFunding, dsfunding, parents)
        for run in cdp.Run.find(client, [cdp.Run.dataset_id == dataset.id]):
            r = add(session, models.Run, run, parents)
            parents["run_id"] = r.id
            for tiltseries in cdp.TiltSeries.find(client, [cdp.TiltSeries.run_id == run.id]):
                ts = add(session, models.Tiltseries, tiltseries, parents)
                parents["tiltseries_id"] = ts.id
            for vs in cdp.TomogramVoxelSpacing.find(client, [cdp.TomogramVoxelSpacing.run_id == run.id]):
                v = add(session, models.TomogramVoxelSpacing, vs, parents)
                parents["tomogram_voxel_spacing_id"] = v.id
                parents["voxel_spacing"] = v.voxel_spacing
                for tomo in cdp.Tomogram.find(client, [cdp.Tomogram.tomogram_voxel_spacing_id == vs.id]):
                    aln = add(session, models.Alignment, tomo, parents)
                    parents["alignment_id"] = aln.id
                    t = add(session, models.Tomogram, tomo, parents)
                    parents["tomogram_id"] = t.id
                    for tomoauthor in cdp.TomogramAuthor.find(client, [cdp.TomogramAuthor.tomogram_id == tomo.id]):
                        add(session, models.TomogramAuthor, tomoauthor, parents)
                for anno in cdp.Annotation.find(client, [cdp.Annotation.tomogram_voxel_spacing_id == vs.id]):
                    a = add(session, models.Annotation, anno, parents)
                    parents["annotation_id"] = a.id
                    for methodlink in fetch_method_links(anno):
                        add(session, models.AnnotationMethodLink, methodlink, parents)
                    for annofile in cdp.AnnotationFile.find(client, [cdp.AnnotationFile.annotation_id == anno.id]):
                        add(session, models.AnnotationFile, annofile, parents)
                    for annoauthor in cdp.AnnotationAuthor.find(
                        client,
                        [cdp.AnnotationAuthor.annotation_id == anno.id],
                    ):
                        add(session, models.AnnotationAuthor, annoauthor, parents)
            # Reset parents so ID's don't spill over from one run to the next.
            parents = {k: parents[k] for k in ["deposition_id", "dataset_id", "run_id"]}

            print(f"run {dataset.id}/{run.name} done")
            session.commit()
        print(f"dataset {dataset.id} done")
        session.commit()
    print(f"DATASET {dataset_id} done")
    session.commit()
    return dataset_id


@click.command()
@click.option("--skip-until", help="skip all datasets until and including this one")
@click.option("--parallelism", help="how many processes to run in parallel", required=True, default=10)
def do_import(skip_until, parallelism):
    client = cdp.Client(CLIENT_URL)
    futures = []
    with ProcessPoolExecutor(max_workers=parallelism) as workerpool:
        depositions = cdp.Deposition.find(client)
        depositions.sort(key=lambda a: a.id)  # Sort datasets by id
        for dep in depositions:
            futures.append(
                workerpool.submit(
                    import_deposition,
                    dep.id,
                ),
            )
        datasets = cdp.Dataset.find(client)
        datasets.sort(key=lambda a: a.id)  # Sort datasets by id
        for dataset in datasets:
            if skip_until:
                if dataset.id == int(skip_until):
                    skip_until = None
                continue

            futures.append(
                workerpool.submit(
                    import_dataset,
                    dataset.id,
                ),
            )
    for future in as_completed(futures):
        if exc := future.exception():
            print(exc)
        else:
            print(f"success: {future.result}")


if __name__ == "__main__":
    do_import()
