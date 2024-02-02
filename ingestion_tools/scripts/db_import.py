import datetime
import json
import logging
import os.path
from pathlib import PurePath
from typing import Any, Optional

import boto3
import click
import peewee
from botocore import UNSIGNED
from botocore.client import Config
from botocore.exceptions import ClientError

from common import db_models
from common.normalize_fields import normalize_fiducial_alignment


@click.group()
def cli():
    pass


def find_subdirs_with_files(s3_client, bucket_name, prefix, target_filename):
    paginator = s3_client.get_paginator("list_objects_v2")
    print(f"looking for prefix {prefix}")
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix, Delimiter="/")

    for page in pages:
        for obj in page["CommonPrefixes"]:
            subdir = obj["Prefix"]
            try:
                metadata_key = f"{subdir}{target_filename}"
                s3_client.head_object(Bucket=bucket_name, Key=metadata_key)
            except:
                continue
            yield subdir


def glob_s3_prefixes(s3_client, bucket_name, prefix, glob_string):
    paginator = s3_client.get_paginator("list_objects_v2")
    print(f"looking for prefix {prefix}::{glob_string}")
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix, Delimiter="/")

    for page in pages:
        if not page.get("CommonPrefixes"):
            break
        for obj in page["CommonPrefixes"]:
            subdir = obj["Prefix"]
            if PurePath(subdir).match(glob_string):
                yield subdir


def glob_s3_files(s3_client, bucket_name, prefix, glob_string):
    paginator = s3_client.get_paginator("list_objects_v2")
    print(f"looking for prefix {prefix}{glob_string}")
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix, Delimiter="/")

    for page in pages:
        for obj in page.get("Contents", {}):
            if not obj:
                break
            if PurePath(obj["Key"]).match(glob_string):
                yield obj["Key"]


def load_key_json(s3_client, bucket_name, key, is_file_required=True):
    try:
        text = s3_client.get_object(Bucket=bucket_name, Key=key)
        data = json.loads(text["Body"].read())
        return data
    except ClientError as ex:
        if ex.response["Error"]["Code"] == "NoSuchKey" and not is_file_required:
            print(f"NoSuchKey on bucket_name={bucket_name} key={key}")
            return None
        else:
            raise


def join_path(*args) -> str:
    return os.path.join(*args)


def upsert(
    id_fields: list[str],
    klass: type,
    mapping: dict[str, Any],
    data: dict[str, Any],
):
    obj = klass()
    map_to_db(obj, mapping, data)
    identifiers = {id_field: getattr(obj, id_field) for id_field in id_fields}
    try:
        existing_obj = klass.get(*[getattr(klass, k) == v for k, v in identifiers.items()])
    except peewee.DoesNotExist:
        obj.save(force_insert=True)
        return obj

    # TODO - we shouldn't do double work!!
    map_to_db(existing_obj, mapping, data)
    existing_obj.save()
    return existing_obj


def map_to_db(obj: db_models.BaseModel, mapping: dict[str, Any], data: dict[str, Any]):
    for db_key, data_path in mapping.items():
        if type(data_path) != list:
            setattr(obj, db_key, data_path)
            continue
        value = None
        for pathpart in data_path:
            if not value:
                value = data.get(pathpart)
            else:
                value = value.get(pathpart)
            if not value:
                break
        if value and "date" in db_key:
            value = datetime.datetime.strptime(value, "%Y-%m-%d")
        setattr(obj, db_key, value)


def get_existing_objects(klass: type, filters: dict[str, Any], hash_attributes: list[str]) -> dict[str, type]:
    result = {}
    query = klass.select().where(*[getattr(klass, k) == v for k, v in filters.items()])
    for record in query:
        key = "-".join([f"{getattr(record, attr)}" for attr in hash_attributes])
        result[key] = record
    return result


def load_dataset_authors_data(dataset_id: int, metadata: dict[str, Any]):
    author_map = {
        "dataset_id": dataset_id,
        "orcid": ["ORCID"],
        "name": ["name"],
        "primary_author_status": ["primary_author_status"],
        "corresponding_author_status": ["corresponding_author_status"],
        "email": ["email"],
        "affiliation_name": ["affiliation_name"],
        "affiliation_address": ["affiliation_address"],
        "affiliation_identifier": ["affiliation_identifier"],
    }
    existing_objs = get_existing_objects(db_models.DatasetAuthor, {"dataset_id": dataset_id}, ["name", "dataset_id_id"])
    for index, author in enumerate(metadata["authors"]):
        author_map["author_list_order"] = index + 1
        # TODO Update upsert to use existing_obj
        dataset_author = upsert(["dataset_id", "name"], db_models.DatasetAuthor, author_map, author)
        existing_obj = existing_objs.pop("-".join([dataset_author.name, str(dataset_author.dataset_id_id)]), None)
    for stale_obj in existing_objs.values():
        stale_obj.delete_instance()


def load_dataset_funding_data(dataset_id: int, metadata: dict[str, Any]):
    funding_map = {
        "dataset_id": dataset_id,
        "funding_agency_name": ["funding_agency_name"],
        "grant_id": ["grant_id"],
    }
    # TODO this doesn't handle deleting unused rows.
    for funding in metadata.get("funding", []):
        upsert(
            ["dataset_id", "funding_agency_name"],
            db_models.DatasetFunding,
            funding_map,
            funding,
        )


def load_datasets_data(dir_prefix: str, metadata: dict[str, Any], s3_prefix, https_prefix):
    print(json.dumps(metadata, indent=4))
    key_photos = metadata.get("key_photos", {})
    data_map = {
        "id": ["dataset_identifier"],
        "title": ["dataset_title"],
        "description": ["dataset_description"],
        "deposition_date": ["dates", "deposition_date"],
        "release_date": ["dates", "release_date"],
        "last_modified_date": ["dates", "last_modified_date"],
        "related_database_entries": ["cross_references", "related_database_entries"],
        "related_database_links": ["cross_references", "related_database_links"],
        "dataset_publications": ["cross_references", "dataset_publications"],
        "dataset_citations": ["cross_references", "dataset_citations"],
        "sample_type": ["sample_type"],
        "organism_name": ["organism", "name"],
        "organism_taxid": ["organism", "taxonomy_id"],
        "tissue_name": ["tissue", "name"],
        "tissue_id": ["tissue", "id"],
        "cell_name": ["cell_type", "name"],
        "cell_type_id": ["cell_type", "id"],
        "cell_strain_name": ["cell_strain", "name"],
        "cell_strain_id": ["cell_strain", "id"],
        "cell_component_name": ["cell_component", "name"],
        "cell_component_id": ["cell_component", "id"],
        "sample_preparation": ["sample_preparation"],
        "grid_preparation": ["grid_preparation"],
        "other_setup": ["other_setup"],
        "s3_prefix": join_path(s3_prefix, dir_prefix),
        "https_prefix": join_path(https_prefix, dir_prefix),
        "key_photo_url": join_path(https_prefix, key_photos.get("snapshot")) if key_photos else None,
        "key_photo_thumbnail_url": join_path(https_prefix, key_photos.get("thumbnail")) if key_photos else None,
    }
    dataset = upsert(["id"], db_models.Dataset, data_map, metadata)
    return dataset


def load_runs_data(
    dataset: db_models.Dataset,
    dir_prefix: str,
    metadata: dict[str, Any],
    s3_prefix,
    https_prefix,
):
    data_map = {
        "dataset_id": dataset.id,
        "name": ["run_name"],
        "s3_prefix": join_path(s3_prefix, dir_prefix),
        "https_prefix": join_path(https_prefix, dir_prefix),
    }
    run = upsert(["name", "dataset_id"], db_models.Run, data_map, metadata)
    return run


def get_tomogram_type(dir_prefix: str) -> str:
    if "CanonicalTomogram" in dir_prefix:
        return "CANONICAL"
    return "UNKOWN"


def load_tomogram_authors_data(tomogram_id: int, metadata: dict[str, Any]):
    author_map = {
        "tomogram_id": tomogram_id,
        "orcid": ["ORCID"],
        "name": ["name"],
        "primary_author_status": ["primary_author_status"],
        "corresponding_author_status": ["corresponding_author_status"],
        "email": ["email"],
        "affiliation_name": ["affiliation_name"],
        "affiliation_address": ["affiliation_address"],
        "affiliation_identifier": ["affiliation_identifier"],
    }
    # TODO this doesn't handle deleting unused rows.
    for index, author in enumerate(metadata["authors"]):
        author_map["author_list_order"] = index + 1
        upsert(["tomogram_id", "name"], db_models.TomogramAuthor, author_map, author)
        del author_map["author_list_order"]


def load_tomo_data(
    voxelspacing: db_models.TomogramVoxelSpacing,
    dir_prefix,
    metadata,
    s3_prefix,
    https_prefix,
    neuroglancer_config,
):
    key_photos = metadata.get("key_photo")
    data_map = {
        "tomogram_voxel_spacing_id": voxelspacing.id,
        "name": ["run_name"],
        "size_x": ["size", "x"],
        "size_y": ["size", "y"],
        "size_z": ["size", "z"],
        "voxel_spacing": ["voxel_spacing"],
        "fiducial_alignment_status": normalize_fiducial_alignment(metadata["fiducial_alignment_status"]),
        "reconstruction_method": ["reconstruction_method"],
        "reconstruction_software": ["reconstruction_software"],
        "processing": ["processing"],
        "processing_software": ["processing_software"],
        "tomogram_version": ["tomogram_version"],
        "is_canonical": True,
        "s3_omezarr_dir": join_path(s3_prefix, dir_prefix, metadata["omezarr_dir"]),
        "https_omezarr_dir": join_path(https_prefix, dir_prefix, metadata["omezarr_dir"]),
        "s3_mrc_scale0": join_path(s3_prefix, dir_prefix, metadata["mrc_files"][0]),
        "https_mrc_scale0": join_path(https_prefix, dir_prefix, metadata["mrc_files"][0]),
        "scale0_dimensions": f"{metadata['scales'][0]['x']},{metadata['scales'][0]['y']},{metadata['scales'][0]['z']}",
        "scale1_dimensions": f"{metadata['scales'][1]['x']},{metadata['scales'][1]['y']},{metadata['scales'][1]['z']}",
        "scale2_dimensions": f"{metadata['scales'][2]['x']},{metadata['scales'][2]['y']},{metadata['scales'][2]['z']}",
        "ctf_corrected": ["ctf_corrected"],
        "offset_x": ["offset", "x"],
        "offset_y": ["offset", "y"],
        "offset_z": ["offset", "z"],
        "key_photo_url": join_path(https_prefix, key_photos.get("snapshot")) if key_photos else None,
        "key_photo_thumbnail_url": join_path(https_prefix, key_photos.get("thumbnail")) if key_photos else None,
        "neuroglancer_config": neuroglancer_config,
        "affine_transformation_matrix": ["affine_transformation_matrix"],
        "type": get_tomogram_type(dir_prefix),
    }
    return upsert(["name", "tomogram_voxel_spacing_id"], db_models.Tomogram, data_map, metadata)


def load_annotation_author_data(annotation_id: int, metadata: dict[str, Any]):
    authors_data_map = {
        "annotation_id": annotation_id,
        "name": ["name"],
        "orcid": ["ORCID"],
        "corresponding_author_status": ["corresponding_author_status"],
        "primary_annotator_status": ["primary_annotator_status"],
        "email": ["email"],
        "affiliation_name": ["affiliation_name"],
        "affiliation_address": ["affiliation_address"],
        "affiliation_identifier": ["affiliation_identifier"],
    }
    for index, author_metadata in enumerate(metadata["authors"]):
        authors_data_map["author_list_order"] = index + 1
        upsert(
            ["annotation_id", "name"],
            db_models.AnnotationAuthor,
            authors_data_map,
            author_metadata,
        )
        del authors_data_map["author_list_order"]


def load_annotation_data(
    spacing: db_models.TomogramVoxelSpacing,
    dir_prefix,
    metadata_filename,
    metadata,
    s3_prefix,
    https_prefix,
):
    data_map = {
        "tomogram_voxel_spacing_id": spacing.id,
        "s3_metadata_path": join_path(s3_prefix, metadata_filename),
        "https_metadata_path": join_path(https_prefix, metadata_filename),
        "deposition_date": ["dates", "deposition_date"],
        "release_date": ["dates", "release_date"],
        "last_modified_date": ["dates", "last_modified_date"],
        "annotation_publication": ["annotation_publications"],
        "annotation_method": ["annotation_method"],
        "ground_truth_status": ["ground_truth_status"],
        "object_name": ["annotation_object", "name"],
        "object_id": ["annotation_object", "id"],
        "object_description": ["annotation_object", "description"],
        "object_state": ["annotation_object", "state"],
        "object_count": ["object_count"],
        "confidence_precision": ["annotation_confidence", "precision"],
        "confidence_recall": ["annotation_confidence", "recall"],
        "ground_truth_used": ["annotation_confidence", "ground_truth_used"],
        "annotation_software": ["annotation_software"],
        "is_curator_recommended": ["is_curator_recommended"],
    }
    annotation = upsert(["s3_metadata_path"], db_models.Annotation, data_map, metadata)

    for file in metadata["files"]:
        file_data_map = {
            "annotation_id": annotation.id,
            "shape_type": ["shape"],
            "format": ["format"],
            "s3_path": join_path(s3_prefix, file["path"]),
            "https_path": join_path(https_prefix, file["path"]),
            "is_visualization_default": ["is_visualization_default"],
        }
        upsert(
            ["annotation_id", "format", "shape_type"],
            db_models.AnnotationFiles,
            file_data_map,
            file,
        )

    return annotation


def get_rawtlt(s3, s3_bucket, dir_prefix):
    for key in glob_s3_files(s3, s3_bucket, dir_prefix, "*.rawtlt"):
        return os.path.basename(key)
    for key in glob_s3_files(s3, s3_bucket, dir_prefix, "*.tlt"):
        return os.path.basename(key)


def get_xf(s3, s3_bucket, dir_prefix):
    for key in glob_s3_files(s3, s3_bucket, dir_prefix, "*.xf"):
        return os.path.basename(key)


def get_mdoc(s3, s3_bucket, dir_prefix):
    for key in glob_s3_files(s3, s3_bucket, dir_prefix, "*.mdoc"):
        return os.path.basename(key)


def load_voxel_spacing_data(
    run: db_models.Run,
    dir_prefix,
    voxel_spacing,
    s3_prefix,
    https_prefix,
):
    data_map = {
        "voxel_spacing": voxel_spacing,
        "s3_prefix": join_path(s3_prefix, dir_prefix),
        "https_prefix": join_path(https_prefix, dir_prefix),
        "run_id": run.id,
    }
    row = upsert(["run_id", "voxel_spacing"], db_models.TomogramVoxelSpacing, data_map, {})
    return row


def load_tiltseries_data(
    s3,
    s3_bucket,
    run: db_models.Run,
    dir_prefix,
    metadata,
    s3_prefix,
    https_prefix,
):
    if not metadata:
        return

    data_map = {
        "acceleration_voltage": ["acceleration_voltage"],
        "binning_from_frames": ["binning_from_frames"],
        "pixel_spacing": ["pixel_spacing"],
        "spherical_aberration_constant": ["spherical_aberration_constant"],
        "microscope_manufacturer": ["microscope", "manufacturer"],
        "microscope_model": ["microscope", "model"],
        "microscope_energy_filter": ["microscope_optical_setup", "energy_filter"],
        "microscope_phase_plate": ["microscope_optical_setup", "phase_plate"],
        "microscope_image_corrector": ["microscope_optical_setup", "image_corrector"],
        "microscope_additional_info": ["microscope_additional_info"],
        "camera_manufacturer": ["camera", "manufacturer"],
        "camera_model": ["camera", "model"],
        "tilt_min": ["tilt_range", "min"],
        "tilt_max": ["tilt_range", "max"],
        "tilt_range": abs(float(metadata["tilt_range"]["max"]) - float(metadata["tilt_range"]["min"])),
        "tilt_step": ["tilt_step"],
        "tilting_scheme": ["tilting_scheme"],
        "tilt_axis": ["tilt_axis"],
        "total_flux": ["total_flux"],
        "data_acquisition_software": ["data_acquisition_software"],
        "related_empiar_entry": ["empiar_entry"],
        "tilt_series_quality": ["tilt_series_quality"],
        "run_id": run.id,
        "is_aligned": ["is_aligned"],
        "aligned_tiltseries_binning": ["aligned_tiltseries_binning"],
        "frames_count": ["frames_count"],
    }

    mrc_bin1 = metadata["mrc_files"][0]
    if mrc_bin1:
        data_map["s3_mrc_bin1"] = join_path(s3_prefix, dir_prefix, mrc_bin1)
        data_map["https_mrc_bin1"] = join_path(https_prefix, dir_prefix, mrc_bin1)

    omezarr_dir = metadata["omezarr_dir"]
    if omezarr_dir:
        data_map["s3_omezarr_dir"] = join_path(s3_prefix, dir_prefix, omezarr_dir)
        data_map["https_omezarr_dir"] = join_path(https_prefix, dir_prefix, omezarr_dir)

    mdoc = get_mdoc(s3, s3_bucket, dir_prefix)
    if mdoc:
        data_map["s3_collection_metadata"] = join_path(s3_prefix, dir_prefix, mdoc)
        data_map["https_collection_metadata"] = join_path(https_prefix, dir_prefix, mdoc)

    rawtlt = get_rawtlt(s3, s3_bucket, dir_prefix)
    if rawtlt:
        data_map["s3_angle_list"] = join_path(s3_prefix, dir_prefix, rawtlt)
        data_map["https_angle_list"] = join_path(https_prefix, dir_prefix, rawtlt)

    xf = get_xf(s3, s3_bucket, dir_prefix)
    if xf:
        data_map["s3_alignment_file"] = join_path(s3_prefix, dir_prefix, xf)
        data_map["https_alignment_file"] = join_path(https_prefix, dir_prefix, xf)

    tiltseries = upsert(["run_id"], db_models.TiltSeries, data_map, metadata)
    return tiltseries


def generate_neuroglancer_data(s3, s3_bucket, tomo_prefix) -> Optional[str]:
    try:
        config = load_key_json(s3, s3_bucket, join_path(tomo_prefix, "neuroglancer_config.json"))
        return json.dumps(config, separators=(",", ":"))
    except ClientError:
        return None


@cli.command()
@click.argument("s3_bucket", required=True, type=str)
@click.argument("https_prefix", required=True, type=str)
@click.argument("postgres_url", required=True, type=str)
@click.option("--s3_prefix", required=True, default="", type=str)
@click.option(
    "--anonymous",
    is_flag=True,
    required=True,
    default=False,
    type=bool,
    help="Use anonymous access to S3",
)
@click.option(
    "--debug/--no-debug",
    is_flag=True,
    required=True,
    default=False,
    type=bool,
    help="Print DB Queries",
)
@click.option("--filter-dataset", type=str, default=None, multiple=True)
@click.option("--import-annotations", is_flag=True, default=False)
@click.option("--import-annotation-authors", is_flag=True, default=False)
@click.option("--import-dataset-authors", is_flag=True, default=False)
@click.option("--import-dataset-funding", is_flag=True, default=False)
@click.option("--import-runs", is_flag=True, default=False)
@click.option("--import-tiltseries", is_flag=True, default=False)
@click.option("--import-tomograms", is_flag=True, default=False)
@click.option("--import-tomogram-authors", is_flag=True, default=False)
@click.option("--import-everything", is_flag=True, default=False)
def load(
    s3_bucket: str,
    https_prefix: str,
    postgres_url: str,
    s3_prefix: str,
    anonymous: bool,
    debug: bool,
    filter_dataset: list[str],
    import_annotations: bool,
    import_annotation_authors: bool,
    import_dataset_authors: bool,
    import_dataset_funding: bool,
    import_runs: bool,
    import_tiltseries: bool,
    import_tomograms: bool,
    import_tomogram_authors: bool,
    import_everything: bool,
):
    db_models.db.init(postgres_url)
    if debug:
        logger = logging.getLogger("peewee")
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)
    if anonymous:
        s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED))
    else:
        s3 = boto3.client("s3")

    import_tomogram_voxel_spacing = False
    if import_everything:
        import_annotations = True
        import_annotation_authors = True
        import_dataset_authors = True
        import_dataset_funding = True
        import_runs = True
        import_tiltseries = True
        import_tomograms = True
        import_tomogram_authors = True
        import_tomogram_voxel_spacing = True
    else:
        import_annotations = max(import_annotations, import_annotation_authors)
        import_tomograms = max(import_tomograms, import_tomogram_authors)
        import_tomogram_voxel_spacing = max(import_annotations, import_tomograms, import_tomogram_voxel_spacing)
        import_runs = max(import_runs, import_tiltseries, import_tomogram_voxel_spacing)

    s3_path_prefix = f"s3://{s3_bucket}"
    for dataset_prefix in find_subdirs_with_files(s3, s3_bucket, s3_prefix, "dataset_metadata.json"):
        if filter_dataset and dataset_prefix not in filter_dataset:
            print(f"Skipping {dataset_prefix}...")
            continue
        dataset_metadata = load_key_json(s3, s3_bucket, join_path(dataset_prefix, "dataset_metadata.json"))
        dataset = load_datasets_data(dataset_prefix, dataset_metadata, s3_path_prefix, https_prefix)
        if import_dataset_authors:
            load_dataset_authors_data(dataset.id, dataset_metadata)
        if import_dataset_funding:
            load_dataset_funding_data(dataset.id, dataset_metadata)

        if not import_runs:
            continue
        # Runs
        for run_prefix in find_subdirs_with_files(s3, s3_bucket, dataset_prefix, "run_metadata.json"):
            run_metadata = load_key_json(s3, s3_bucket, join_path(run_prefix, "run_metadata.json"))
            run = load_runs_data(dataset, run_prefix, run_metadata, s3_path_prefix, https_prefix)

            if import_tiltseries:
                ts_path = os.path.join(run_prefix, "TiltSeries")
                ts_metadata_filename = os.path.join(ts_path, "tiltseries_metadata.json")
                ts_metadata = load_key_json(s3, s3_bucket, ts_metadata_filename, is_file_required=False)
                load_tiltseries_data(
                    s3,
                    s3_bucket,
                    run,
                    f"{ts_path}/",
                    ts_metadata,
                    s3_path_prefix,
                    https_prefix,
                )

            if not import_tomogram_voxel_spacing:
                continue

            # VoxelSpacings
            tomo_prefix = os.path.join(run_prefix, "Tomograms/")
            for spacing_prefix in glob_s3_prefixes(s3, s3_bucket, tomo_prefix, "VoxelSpacing*"):
                voxel_spacing = float(spacing_prefix.strip("/").split("/")[-1][len("VoxelSpacing") :])
                print(f"voxel spacing is {voxel_spacing}")
                spacing = load_voxel_spacing_data(run, spacing_prefix, voxel_spacing, s3_path_prefix, https_prefix)

                # Tomograms
                if import_tomograms:
                    tomo_prefix = join_path(spacing_prefix, "CanonicalTomogram")
                    print(f"Tomo prefix is {tomo_prefix}")
                    tomo_metadata = load_key_json(s3, s3_bucket, join_path(tomo_prefix, "tomogram_metadata.json"))
                    tomogram = load_tomo_data(
                        spacing,
                        tomo_prefix,
                        tomo_metadata,
                        s3_path_prefix,
                        https_prefix,
                        generate_neuroglancer_data(s3, s3_bucket, tomo_prefix),
                    )
                    if import_tomogram_authors:
                        load_tomogram_authors_data(tomogram.id, tomo_metadata)

                # Annotations
                if import_annotations:
                    anno_prefix = join_path(spacing_prefix, "Annotations")
                    for anno_file in glob_s3_files(s3, s3_bucket, f"{anno_prefix}/", "*.json"):
                        anno_metadata = load_key_json(s3, s3_bucket, anno_file)
                        annotation = load_annotation_data(
                            spacing,
                            anno_prefix,
                            anno_file,
                            anno_metadata,
                            s3_path_prefix,
                            https_prefix,
                        )
                        if import_annotation_authors:
                            load_annotation_author_data(annotation.id, anno_metadata)


if __name__ == "__main__":
    cli()
