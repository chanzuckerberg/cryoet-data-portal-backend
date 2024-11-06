from datetime import datetime

from playhouse.shortcuts import model_to_dict

from common.db_models import (
    Annotation,
    AnnotationAuthor,
    AnnotationFiles,
    BaseModel,
    Dataset,
    DatasetAuthor,
    DatasetFunding,
    Deposition,
    DepositionAuthor,
    Run,
    TiltSeries,
    Tomogram,
    TomogramAuthor,
    TomogramVoxelSpacing,
)

DATASET_ID = 30001
DATASET_AUTHOR_ID = 301
DATASET_FUNDING_ID = 302
DEPOSITION_ID1 = 300
DEPOSITION_ID2 = 301
DEPOSITION_AUTHOR_ID = 201
RUN1_ID = 401
RUN4_ID = 402
TILTSERIES_ID = 501
TOMOGRAM_VOXEL_ID1 = 502
TOMOGRAM_VOXEL_ID2 = 503
TOMOGRAM_ID = 601
TOMOGRAM_AUTHOR_ID = 701
ANNOTATION_ID = 602
ANNOTATION_FILE_ID = 701
ANNOTATION_AUTHOR_ID = 702

STALE_RUN_ID = 902
STALE_TOMOGRAM_ID = 903
STALE_ANNOTATION_ID = 904


def stale_deposition_metadata() -> dict:
    return {
        "id": DEPOSITION_ID1,
        "title": "Test Deposition",
        "description": "Test Description",
        "deposition_date": datetime.now().date(),
        "release_date": datetime.now().date(),
        "last_modified_date": datetime.now().date(),
        "deposition_types": "annotation",
        "s3_prefix": "s3://invalid_bucket/dep1",
        "https_prefix": "https://invalid-site.com/1234",
    }


def populate_deposition() -> None:
    Deposition.create(**stale_deposition_metadata())


def stale_deposition_author() -> dict:
    return {
        "id": DEPOSITION_AUTHOR_ID,
        "deposition_id": DEPOSITION_ID1,
        "name": "Author 1",
        "author_list_order": 1,
        "corresponding_author_status": False,
        "primary_author_status": False,
    }


def populate_deposition_authors() -> None:
    DepositionAuthor.create(**stale_deposition_author())


def populate_dataset() -> None:
    today = datetime.now().date()
    Dataset.create(
        id=DATASET_ID,
        title="foo",
        description="bar",
        deposition_date=today,
        release_date=today,
        last_modified_date=today,
        sample_type="test",
        s3_prefix="s3://invalid_bucket/",
        https_prefix="https://invalid-site.com/1234",
    )


def populate_dataset_authors() -> None:
    DatasetAuthor.create(id=DATASET_AUTHOR_ID, dataset_id=DATASET_ID, name="Virginia Woolf", author_list_order=3)


def populate_stale_dataset_authors() -> None:
    DatasetAuthor.create(dataset_id=DATASET_ID, name="Stale Author", author_list_order=1)


def populate_dataset_funding() -> None:
    DatasetFunding.create(
        id=DATASET_FUNDING_ID,
        dataset_id=DATASET_ID,
        funding_agency_name="Grant Provider 1",
        grant_id="foo",
    )


def populate_stale_dataset_funding() -> None:
    DatasetFunding.create(dataset_id=DATASET_ID, funding_agency_name="Stale Grant Entry")


def populate_run() -> None:
    populate_dataset()
    run = Run.create(
        id=RUN1_ID,
        dataset_id=DATASET_ID,
        name="RUN1",
        s3_prefix="s3://test-bucket/RUN1",
        https_prefix="http://test.com/RUN1",
    )
    update_and_save(run, {"name": "RUN4", "id": RUN4_ID})


def populate_stale_run() -> None:
    Run.create(
        id=STALE_RUN_ID,
        dataset_id=DATASET_ID,
        name="RUN5",
        s3_prefix="s3://test-bucket/RUN5",
        https_prefix="http://test.com/RUN5",
    )
    populate_stale_tomogram_voxel_spacing(STALE_RUN_ID)


def populate_tomogram_voxel_spacing() -> None:
    populate_run()
    https_prefix = "http://test.com/RUN1/VoxelSpacing{vs}"
    TomogramVoxelSpacing.create(
        run_id=RUN1_ID,
        voxel_spacing=3.456,
        s3_prefix="s3://test-public-bucket/VoxelSpacing3.456/",
        https_prefix=https_prefix.format(vs=3.456),
    )
    TomogramVoxelSpacing.create(
        id=TOMOGRAM_VOXEL_ID1,
        run_id=RUN1_ID,
        voxel_spacing=12.3,
        s3_prefix="s3://test-public-bucket/VoxelSpacing12.3/",
        https_prefix=https_prefix.format(vs=12.3),
    )
    TomogramVoxelSpacing.create(
        id=TOMOGRAM_VOXEL_ID2,
        run_id=RUN1_ID,
        voxel_spacing=9.876,
        s3_prefix="s3://test-public-bucket/VoxelSpacing9.876/",
        https_prefix=https_prefix.format(vs=9.876),
    )


def populate_stale_tomogram_voxel_spacing(run_id: int = RUN1_ID) -> None:
    stale_voxel_spacing = TomogramVoxelSpacing.create(
        run_id=run_id,
        voxel_spacing=10.345,
        s3_prefix="s3://test-public-bucket/VoxelSpacing10.345/",
        https_prefix="http://test.com/RUN1/VoxelSpacing10.345/",
    )
    stale_tomogram = Tomogram.create(
        tomogram_voxel_spacing_id=stale_voxel_spacing.id,
        name="RUN1",
        voxel_spacing=10.345,
        s3_omezarr_dir="s3://stale.zarr",
        https_omezarr_dir="http://test.com/stale.zarr",
        s3_mrc_scale0="s3://stale.mrc",
        https_mrc_scale0="http://test.com/stale.mrc",
        size_x=2,
        size_y=2,
        size_z=2,
        fiducial_alignment_status="foo",
        reconstruction_method="",
        reconstruction_software="",
        tomogram_version="0.5",
        scale0_dimensions="",
        scale1_dimensions="",
        scale2_dimensions="",
        processing="",
        offset_x=0,
        offset_y=0,
        offset_z=0,
    )
    TomogramAuthor.create(tomogram_id=stale_tomogram.id, name="Jane Smith", author_list_order=1)
    TomogramAuthor.create(tomogram_id=stale_tomogram.id, name="John John", author_list_order=2)
    stale_annotation = Annotation.create(
        tomogram_voxel_spacing_id=stale_voxel_spacing.id,
        deposition_id=DEPOSITION_ID2,
        s3_metadata_path="foo",
        https_metadata_path="foo",
        deposition_date="2025-04-01",
        release_date="2025-06-01",
        last_modified_date="2025-06-01",
        annotation_method="",
        ground_truth_status=False,
        object_name="bar",
        object_id="invalid-id",
        object_count=200,
        annotation_software="bar",
    )
    AnnotationAuthor.create(annotation_id=stale_annotation.id, name="Jane Smith", author_list_order=1)
    AnnotationAuthor.create(annotation_id=stale_annotation.id, name="John John", author_list_order=2)


def populate_tomograms() -> None:
    populate_tomogram_voxel_spacing()
    Tomogram.create(
        id=TOMOGRAM_ID,
        tomogram_voxel_spacing_id=TOMOGRAM_VOXEL_ID1,
        name="RUN1",
        voxel_spacing=12.3,
        s3_omezarr_dir="s3://RUN1.zarr",
        https_omezarr_dir="http://test.com/RUN1.zarr",
        s3_mrc_scale0="s3://RUN1.mrc",
        https_mrc_scale0="http://test.com/RUN1.mrc",
        size_x=25,
        size_y=25,
        size_z=25,
        fiducial_alignment_status="foo",
        reconstruction_method="WBP",
        reconstruction_software="",
        tomogram_version="0.5",
        scale0_dimensions="",
        scale1_dimensions="",
        scale2_dimensions="",
        processing="raw",
        processing_software="tomo3D",
        deposition_id=DEPOSITION_ID1,
        offset_x=0,
        offset_y=0,
        offset_z=0,
    )


def populate_stale_tomograms() -> None:
    Tomogram.create(
        id=STALE_TOMOGRAM_ID,
        tomogram_voxel_spacing_id=TOMOGRAM_VOXEL_ID2,
        name="RUN1",
        voxel_spacing=12.3,
        s3_omezarr_dir="s3://stale.zarr",
        https_omezarr_dir="http://test.com/stale.zarr",
        s3_mrc_scale0="s3://stale.mrc",
        https_mrc_scale0="http://test.com/stale.mrc",
        size_x=2,
        size_y=2,
        size_z=2,
        fiducial_alignment_status="foo",
        reconstruction_method="",
        reconstruction_software="",
        tomogram_version="0.5",
        scale0_dimensions="",
        scale1_dimensions="",
        scale2_dimensions="",
        processing="",
        offset_x=0,
        offset_y=0,
        offset_z=0,
    )


def populate_tomogram_authors() -> None:
    populate_tomograms()
    TomogramAuthor.create(id=TOMOGRAM_AUTHOR_ID, tomogram_id=TOMOGRAM_ID, name="Jane Smith", author_list_order=1)


def populate_stale_tomogram_authors() -> None:
    author = TomogramAuthor.create(
        tomogram_id=STALE_TOMOGRAM_ID,
        name="Stale Author 2",
        primary_author_status=True,
        author_list_order=3,
    )
    update_and_save(author, {"tomogram_id": TOMOGRAM_ID})


def populate_tiltseries() -> None:
    populate_run()
    TiltSeries.create(
        id=TILTSERIES_ID,
        run_id=RUN1_ID,
        s3_mrc_bin1="ts_foo.mrc",
        https_mrc_bin1="ts_foo.mrc",
        s3_omezarr_dir="ts_foo.zarr",
        https_omezarr_dir="ts_foo.zarr",
        acceleration_voltage=100,
        spherical_aberration_constant=1.0,
        microscope_manufacturer="unknown",
        microscope_model="unknown",
        microscope_energy_filter="unknown",
        camera_manufacturer="unknown",
        camera_model="unknown",
        tilt_min=0,
        tilt_max=0,
        tilt_range=0,
        tilt_step=0,
        tilt_axis=1.0,
        tilt_series_quality=3,
        total_flux=0,
        is_aligned=False,
        pixel_spacing=0.3,
        tilting_scheme="unknown",
        data_acquisition_software="unknown",
    )


def populate_stale_tiltseries() -> None:
    tilt_series = TiltSeries(
        run_id=RUN4_ID,
        s3_mrc_bin1="ts_foo.mrc",
        https_mrc_bin1="ts_foo.mrc",
        s3_omezarr_dir="ts_foo.zarr",
        https_omezarr_dir="ts_foo.zarr",
        acceleration_voltage=100,
        spherical_aberration_constant=1.0,
        microscope_manufacturer="unknown",
        microscope_model="unknown",
        microscope_energy_filter="unknown",
        camera_manufacturer="unknown",
        camera_model="unknown",
        tilt_min=0,
        tilt_max=0,
        tilt_range=0,
        tilt_step=0,
        tilt_axis=1.0,
        tilt_series_quality=3,
        total_flux=0,
        is_aligned=False,
        pixel_spacing=0.3,
        tilting_scheme="unknown",
        data_acquisition_software="unknown",
    )
    update_and_save(tilt_series, {"run_id": STALE_RUN_ID})


def populate_annotations() -> None:
    populate_tomogram_voxel_spacing()
    Annotation.create(
        id=ANNOTATION_ID,
        tomogram_voxel_spacing_id=TOMOGRAM_VOXEL_ID1,
        deposition_id=DEPOSITION_ID2,
        s3_metadata_path="s3://test-public-bucket/30001/RUN1/Tomograms/VoxelSpacing12.300/Annotations/100-foo-1.0.json",
        https_metadata_path="foo",
        deposition_date="2025-04-01",
        release_date="2025-06-01",
        last_modified_date="2025-06-01",
        annotation_method="2D CNN predictions",
        ground_truth_status=False,
        object_name="foo",
        object_count=0,
        object_id="invalid-id",
        annotation_software="bar",
    )


def populate_stale_annotations() -> None:
    Annotation.create(
        id=STALE_ANNOTATION_ID,
        tomogram_voxel_spacing_id=TOMOGRAM_VOXEL_ID1,
        deposition_id=DEPOSITION_ID2,
        s3_metadata_path="foo",
        https_metadata_path="foo",
        deposition_date="2025-04-01",
        release_date="2025-06-01",
        last_modified_date="2025-06-01",
        annotation_method="",
        ground_truth_status=False,
        object_name="bar",
        object_id="invalid-id",
        object_count=200,
        annotation_software="bar",
    )


def populate_annotation_files() -> None:
    populate_annotations()
    file = AnnotationFiles.create(
        id=ANNOTATION_FILE_ID,
        annotation_id=ANNOTATION_ID,
        s3_path="s3://foo",
        https_path="https://foo",
        shape_type="Point",
        format="ndjson",
    )
    update_and_save(file, {"shape_type": "ZZOrientedPoint", "format": "ndjson"})


def populate_stale_annotation_files() -> None:
    populate_stale_annotations()
    file = AnnotationFiles.create(
        annotation_id=STALE_ANNOTATION_ID,
        s3_path="s3://foo-stale-annotation/point",
        https_path="https://foo-stale-annotation/point",
        shape_type="Point",
        format="ndjson",
    )
    update_and_save(file, {"shape_type": "SegmentationMask", "format": "mrc"})


def populate_annotation_authors() -> None:
    populate_annotations()
    author = AnnotationAuthor.create(
        id=ANNOTATION_AUTHOR_ID,
        annotation_id=ANNOTATION_ID,
        name="Jane Smith",
        author_list_order=1,
    )
    update_and_save(author, {"name": "Stale Author", "corresponding_author_status": True, "author_list_order": 3})


def populate_stale_annotation_authors() -> None:
    populate_stale_annotations()
    author = AnnotationAuthor.create(annotation_id=STALE_ANNOTATION_ID, name="Jane Smith", author_list_order=1)
    update_and_save(author, {"name": "Stale Author", "corresponding_author_status": True, "author_list_order": 3})


def update_and_save(model: BaseModel, new_values: dict) -> BaseModel:
    data = model_to_dict(model, recurse=False, backrefs=False)
    data.pop("id")
    data = {**data, **new_values}
    return model.insert(data).execute()


def clean_all_mock_data() -> None:
    for dataset in Dataset.select().where(Dataset.id << [DATASET_ID]):
        for author in dataset.authors:
            author.delete_instance()
        for funding_source in dataset.funding_sources:
            funding_source.delete_instance()
        for run in dataset.runs:
            for ts in run.tiltseries:
                ts.delete_instance()
            for voxel_spacing in run.tomogram_voxel_spacings:
                for tomogram in voxel_spacing.tomograms:
                    for author in tomogram.authors:
                        author.delete_instance()
                    tomogram.delete_instance()
                for annotation in voxel_spacing.annotations:
                    for file in annotation.files:
                        file.delete_instance()
                    for author in annotation.authors:
                        author.delete_instance()
                    annotation.delete_instance()
                voxel_spacing.delete_instance()
            run.delete_instance()
        dataset.delete_instance()

    for deposition in Deposition.select().where(Deposition.id << [DEPOSITION_ID1, DEPOSITION_ID2]):
        for author in deposition.authors:
            author.delete_instance()
        deposition.delete_instance()
