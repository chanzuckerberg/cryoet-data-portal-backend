from datetime import datetime

from common.db_models import (
    Annotation,
    AnnotationFiles,
    Dataset,
    DatasetAuthor,
    DatasetFunding,
    Run,
    TiltSeries,
    Tomogram,
    TomogramAuthor,
    TomogramVoxelSpacing,
)

DATASET_ID = 30001
DATASET_AUTHOR_ID = 103
DATASET_FUNDING_ID = 105
RUN_ID = 102
TOMOGRAM_VOXEL_ID = 104
TOMOGRAM_ID = 103
ANNOTATION_ID = 100
ANNOTATION_FILE_ID = 110


def populate_dataset_table() -> None:
    today = datetime.now().date()
    Dataset(
        id=DATASET_ID,
        title="foo",
        description="bar",
        deposition_date=today,
        release_date=today,
        last_modified_date=today,
        sample_type="test",
        s3_prefix="s3://invalid_bucket/",
        https_prefix="https://invalid-site.com/1234",
    ).save(force_insert=True)


def populate_dataset_authors_table() -> None:
    DatasetAuthor(id=102, dataset_id=DATASET_ID, name="Stale Author", author_list_order=1).save(force_insert=True)
    DatasetAuthor(id=DATASET_AUTHOR_ID, dataset_id=DATASET_ID, name="Virginia Woolf", author_list_order=3).save(
        force_insert=True,
    )


def populate_dataset_funding_table() -> None:
    DatasetFunding(
        id=DATASET_FUNDING_ID,
        dataset_id=DATASET_ID,
        funding_agency_name="Grant Provider 1",
        grant_id="foo",
    ).save(
        force_insert=True,
    )
    DatasetFunding(id=109, dataset_id=30001, funding_agency_name="Stale Grant Entry").save(force_insert=True)


def populate_runs_table() -> None:
    populate_dataset_table()
    Run(
        id=RUN_ID,
        dataset_id=DATASET_ID,
        name="RUN1",
        s3_prefix="s3://test-bucket/RUN1",
        https_prefix="http://test.com/RUN1",
    ).save(force_insert=True)
    # TODO: Add functionality to remove stale data
    # Run(
    #     id=103,
    #     dataset_id=DATASET_ID,
    #     name="STALE_RUN",
    #     s3_prefix="s3://test-bucket/STALE_RUN",
    #     https_prefix="http://test.com/STALE_RUN",
    # )


def populate_tomogram_voxel_spacing_table() -> None:
    populate_runs_table()
    TomogramVoxelSpacing(
        id=103,
        run_id=RUN_ID,
        voxel_spacing=3.456,
        s3_prefix="s3://test-public-bucket/30001/RUN1/Tomograms/VoxelSpacing3.456/",
        https_prefix="http://test.com/RUN1/VoxelSpacing3.456/",
    ).save(force_insert=True)
    TomogramVoxelSpacing(
        id=TOMOGRAM_VOXEL_ID,
        run_id=RUN_ID,
        voxel_spacing=12.3,
        s3_prefix="s3://test-public-bucket/VoxelSpacing12.3/",
        https_prefix="http://test.com/RUN1/VoxelSpacing12.3/",
    ).save(force_insert=True)


def populate_tomograms_table() -> None:
    populate_tomogram_voxel_spacing_table()
    Tomogram(
        id=TOMOGRAM_ID,
        tomogram_voxel_spacing_id=TOMOGRAM_VOXEL_ID,
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
    ).save(force_insert=True)


def populate_tomogram_authors_table() -> None:
    populate_tomograms_table()
    TomogramAuthor(id=100, tomogram_id=TOMOGRAM_ID, name="Jane Smith", author_list_order=1).save(force_insert=True)
    TomogramAuthor(
        id=200,
        tomogram_id=TOMOGRAM_ID,
        name="Stale Author",
        corresponding_author_status=True,
        author_list_order=3,
    ).save(force_insert=True)


def populate_tiltseries_table() -> None:
    populate_runs_table()
    TiltSeries(
        id=101,
        run_id=RUN_ID,
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
    ).save(force_insert=True)


def populate_annotations() -> None:
    populate_tomogram_voxel_spacing_table()
    Annotation(
        id=ANNOTATION_ID,
        tomogram_voxel_spacing_id=TOMOGRAM_VOXEL_ID,
        s3_metadata_path="s3://test-public-bucket/30001/RUN1/Tomograms/VoxelSpacing12.300/Annotations/100-foo-1.0.json",
        https_metadata_path="foo",
        deposition_date="2025-04-01",
        release_date="2025-06-01",
        last_modified_date="2025-06-01",
        annotation_method="",
        ground_truth_status=False,
        object_name="bar",
        object_count=0,
        object_id="invalid-id",
        annotation_software="bar",
    ).save(force_insert=True)
    # Annotation(
    #     id=101,
    #     tomogram_voxel_spacing_id=TOMOGRAM_VOXEL_ID,
    #     s3_metadata_path="foo",
    #     https_metadata_path="foo",
    #     deposition_date="2025-04-01",
    #     release_date="2025-06-01",
    #     last_modified_date="2025-06-01",
    #     annotation_method="",
    #     ground_truth_status=False,
    #     object_name="bar",
    #     object_id="invalid-id",
    #     annotation_software="bar",
    # ).save(force_insert=True)


def populate_annotation_files() -> None:
    populate_annotations()
    AnnotationFiles(
        id=ANNOTATION_FILE_ID,
        annotation_id=ANNOTATION_ID,
        s3_path="s3://foo",
        https_path="https://foo",
        shape_type="Point",
        format="ndjson",
    ).save(force_insert=True)
    # AnnotationFiles(
    #     annotation_id=ANNOTATION_ID,
    #     s3_path="s3://foo",
    #     https_path="https://foo",
    #     shape_type="OrientedPoint",
    #     format="ndjson",
    # ).save(force_insert=True)


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
