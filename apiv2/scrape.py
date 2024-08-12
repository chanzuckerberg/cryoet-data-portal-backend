import json

import cryoet_data_portal as cdp

from database import models
from platformics.database.connect import init_sync_db

# cleanup:
# delete from annotation_author; delete from dataset_author; delete from deposition_author; delete from annotation_file ; delete from annotation_shape ; delete from dataset_funding; delete from tomogram_author; delete from tomogram; delete from annotation; delete from annotation; delete from tomogram_voxel_spacing; delete from per_section_alignment_parameters; delete from per_section_parameters; delete from alignment; delete from frame; delete from tiltseries; delete from run; delete from run; delete from dataset; delete from deposition;


# Adapted from https://github.com/sqlalchemy/sqlalchemy/wiki/UniqueObject


def get_or_create(session, cls, row_id, data):
    obj = session.query(cls).where(cls.id == row_id).first()
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
    remote_item = item.to_dict()

    local_item_data = {}
    if model == models.Annotation:
        local_item_data = {
            # "primary_author_status": remote_item.get["primary_annotator_status"],
            # "corresponding_author_status": remote_item.get("corresponding_annotator_status"),
            "run_id": parents["run_id"],
            # "deposition_id": remote_item["deposition_id"], # Doesn't exist in the old api.
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
    if model == models.AnnotationAuthor:
        local_item_data = {
            "author_list_order": 1,
        }
    if model == models.AnnotationFile:
        pass
    if model == models.Dataset:
        local_item_data = {
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
            "publications": remote_item["dataset_publications"],  # Field name change
            "related_database_entries": remote_item["related_database_entries"],
            "related_database_links": remote_item["related_database_links"],
            "dataset_citations": remote_item["dataset_citations"],
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
            # "deposition_id": remote_item["deposition_id"], # We don't have deposition id's yet
            "s3_omezarr_dir": remote_item["s3_omezarr_dir"],
            "s3_mrc_bin1": remote_item["s3_mrc_bin1"],
            "https_omezarr_dir": remote_item["https_omezarr_dir"],
            "https_mrc_bin1": remote_item["https_mrc_bin1"],
            "s3_collection_metadata": remote_item["s3_collection_metadata"],
            "https_collection_metadata": remote_item["https_collection_metadata"],
            "s3_angle_list": remote_item["s3_angle_list"],
            "https_angle_list": remote_item["https_angle_list"],
            # "s3_gain_file": remote_item["s3_gain_file"], # This doesn't exist in the old api
            # "https_gain_file": remote_item["https_gain_file"], # This doesn't exist in the old api
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
            # "tiltseries_frames_count": remote_item["tiltseries_frames_count"], # This doesn't exist in the old api
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
    if model == models.Tomogram:
        local_item_data = {
            "affine_transformation_matrix": json.dumps(remote_item["affine_transformation_matrix"]),  # Json handling
            "tomogram_type": remote_item["type"],  # Key name change
            # "alignment_id": remote_item["alignment_id"],  # Doesn't exist in the old api
            # "deposition_id": remote_item["deposition_id"], # Doesn't exist in old api
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
            "is_canonical": remote_item["is_canonical"],
            "s3_omezarr_dir": remote_item["s3_omezarr_dir"],
            "https_omezarr_dir": remote_item["https_omezarr_dir"],
            "s3_mrc_scale0": remote_item["s3_mrc_scale0"],
            "https_mrc_scale0": remote_item["https_mrc_scale0"],
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
            "is_standardized": False,  # We don't have standardized tomos yet.
        }
        # Special handling for converting values.
        reconstruction_method = remote_item["reconstruction_method"].lower()
        if "weighted" in reconstruction_method:
            local_item_data["reconstruction_method"] = "WBP"
        elif "iterative" in reconstruction_method:
            local_item_data["reconstruction_method"] = "SIRT"
        elif "algebraic" in reconstruction_method:
            local_item_data["reconstruction_method"] = "SART"
        elif "fourier" in reconstruction_method:
            local_item_data["reconstruction_method"] = "Fourier Space"
        else:
            # TODO FIXME THIS IS A NOT NULL COL!!
            print(f"Error: could not map reconstruction method {reconstruction_method}")
            local_item_data["reconstruction_method"] = None
    if model == models.TomogramVoxelSpacing:
        local_item_data = {
            "voxel_spacing": remote_item["voxel_spacing"],
            "s3_prefix": remote_item["s3_prefix"],
            "https_prefix": remote_item["https_prefix"],
        }
    item = get_or_create(
        session,
        model,
        remote_item["id"],
        local_item_data,
    )

    session.add(item)
    session.flush()
    return item


def do_import():
    annotation = models.Annotation
    client = cdp.Client()
    db = init_sync_db("postgresql+psycopg://postgres:password_postgres@platformics-db:5432/platformics")
    with db.session() as session:
        for dataset in cdp.Dataset.find(client):
            ds = add(session, models.Dataset, dataset, {})
            for dsauthor in cdp.DatasetAuthor.find(client, [cdp.DatasetAuthor.dataset_id == dataset.id]):
                dsa = add(session, models.DatasetAuthor, dsauthor, {"dataset_id": ds.id})
            for dsfunding in cdp.DatasetFunding.find(client, [cdp.DatasetFunding.dataset_id == dataset.id]):
                dsf = add(session, models.DatasetFunding, dsfunding, {"dataset_id": ds.id})
            for run in cdp.Run.find(client, [cdp.Run.dataset_id == dataset.id]):
                r = add(session, models.Run, run, {"dataset_id": ds.id})
                for vs in cdp.TomogramVoxelSpacing.find(client, [cdp.TomogramVoxelSpacing.run_id == run.id]):
                    v = add(session, models.TomogramVoxelSpacing, vs, {"run_id": r.id})
                    for tomo in cdp.Tomogram.find(client, [cdp.Tomogram.tomogram_voxel_spacing_id == vs.id]):
                        t = add(session, models.Tomogram, tomo, {"run_id": r.id, "tomogram_voxel_spacing_id": v.id})
                        for tomoauthor in cdp.TomogramAuthor.find(client, [cdp.TomogramAuthor.tomogram_id == tomo.id]):
                            ta = add(session, models.TomogramAuthor, tomoauthor, {"tomogram_id": t.id})
                    continue
                    for anno in cdp.Annotation.find(client, [cdp.Annotation.tomogram_voxel_spacing_id == vs.id]):
                        a = add(session, models.Annotation, anno, {"run_id": r.id})
                        # TODO this needs a bit of work.
                        # for annofile in cdp.AnnotationFile.find(client, [cdp.AnnotationFile.annotation_id == anno.id]):
                        #     af = add(session, models.AnnotationFile, annofile, {"annotation_id": a.id})
                        for annoauthor in cdp.AnnotationAuthor.find(
                            client,
                            [cdp.AnnotationAuthor.annotation_id == anno.id],
                        ):
                            aa = add(session, models.AnnotationAuthor, annoauthor, {"annotation_id": a.id})
                for tiltseries in cdp.TiltSeries.find(client, [cdp.TiltSeries.run_id == run.id]):
                    ts = add(session, models.Tiltseries, tiltseries, {"run_id": r.id})
                print(f"run {dataset.id}/{run.name} done")
                session.commit()
            print(f"dataset {dataset.id} done")
            session.commit()
        print("done")
        session.commit()
    return annotation


if __name__ == "__main__":
    do_import()
