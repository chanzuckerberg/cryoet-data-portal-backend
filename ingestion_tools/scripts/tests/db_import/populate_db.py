from datetime import datetime

from common.db_models import (
    Annotation,
    AnnotationAuthor,
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
DATASET_AUTHOR_ID = 301
DATASET_FUNDING_ID = 302
RUN_ID = 401
TILTSERIES_ID = 501
TOMOGRAM_VOXEL_ID1 = 502
TOMOGRAM_VOXEL_ID2 = 503
TOMOGRAM_ID = 601
TOMOGRAM_AUTHOR_ID = 701
ANNOTATION_ID = 602
ANNOTATION_FILE_ID = 701
ANNOTATION_AUTHOR_ID = 702

STALE_TOMOGRAM_ID = 902
STALE_ANNOTATION_ID = 903


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
        id=TOMOGRAM_VOXEL_ID1,
        run_id=RUN_ID,
        voxel_spacing=12.3,
        s3_prefix="s3://test-public-bucket/VoxelSpacing12.3/",
        https_prefix="http://test.com/RUN1/VoxelSpacing12.3/",
    ).save(force_insert=True)
    TomogramVoxelSpacing(
        id=TOMOGRAM_VOXEL_ID2,
        run_id=RUN_ID,
        voxel_spacing=9.876,
        s3_prefix="s3://test-public-bucket/VoxelSpacing9.876/",
        https_prefix="http://test.com/RUN1/VoxelSpacing9.876/",
    ).save(force_insert=True)


def populate_stale_tomogram_voxel_spacing_data() -> None:
    stale_tomogram_voxel_id = 1000
    stale_tomogram_id = 1001
    stale_annotation_id = 10002
    TomogramVoxelSpacing(
        id=stale_tomogram_voxel_id,
        run_id=RUN_ID,
        voxel_spacing=10.345,
        s3_prefix="s3://test-public-bucket/VoxelSpacing10.345/",
        https_prefix="http://test.com/RUN1/VoxelSpacing10.345/",
    ).save(force_insert=True)
    Tomogram(
        id=stale_tomogram_id,
        tomogram_voxel_spacing_id=stale_tomogram_voxel_id,
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
    ).save(force_insert=True)
    TomogramAuthor(tomogram_id=stale_tomogram_id, name="Jane Smith", author_list_order=1).save(force_insert=True)
    Annotation(
        id=stale_annotation_id,
        tomogram_voxel_spacing_id=stale_tomogram_voxel_id,
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
    ).save(force_insert=True)
    AnnotationAuthor(annotation_id=stale_annotation_id, name="Jane Smith", author_list_order=1).save(force_insert=True)


def populate_tomograms_table() -> None:
    populate_tomogram_voxel_spacing_table()
    Tomogram(
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
    Tomogram(
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
    ).save(force_insert=True)


def populate_tomogram_authors_table() -> None:
    populate_tomograms_table()
    TomogramAuthor(id=TOMOGRAM_AUTHOR_ID, tomogram_id=TOMOGRAM_ID, name="Jane Smith", author_list_order=1).save(
        force_insert=True,
    )
    TomogramAuthor(
        id=200,
        tomogram_id=TOMOGRAM_ID,
        name="Stale Author",
        corresponding_author_status=True,
        author_list_order=3,
    ).save(force_insert=True)
    TomogramAuthor(
        tomogram_id=STALE_TOMOGRAM_ID,
        name="Stale Author 2",
        primary_author_status=True,
        author_list_order=3,
    ).save(force_insert=True)


def populate_tiltseries_table() -> None:
    populate_runs_table()
    TiltSeries(
        id=TILTSERIES_ID,
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
        tomogram_voxel_spacing_id=TOMOGRAM_VOXEL_ID1,
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
    Annotation(
        id=STALE_ANNOTATION_ID,
        tomogram_voxel_spacing_id=TOMOGRAM_VOXEL_ID1,
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
    ).save(force_insert=True)


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
    AnnotationFiles(
        annotation_id=ANNOTATION_ID,
        s3_path="s3://foo-stale-annotation",
        https_path="https://foo-stale-annotation",
        shape_type="ZZOrientedPoint",
        format="ndjson",
    ).save(force_insert=True)
    AnnotationFiles(
        annotation_id=STALE_ANNOTATION_ID,
        s3_path="s3://foo-stale-annotation/point",
        https_path="https://foo-stale-annotation/point",
        shape_type="Point",
        format="ndjson",
    ).save(force_insert=True)
    AnnotationFiles(
        annotation_id=STALE_ANNOTATION_ID,
        s3_path="s3://foo-stale-annotation/seg_mask",
        https_path="https://foo-stale-annotation/seg_mask",
        shape_type="SegmentationMask",
        format="mrc",
    ).save(force_insert=True)


def populate_annotation_authors_table() -> None:
    populate_annotations()
    AnnotationAuthor(id=ANNOTATION_AUTHOR_ID, annotation_id=ANNOTATION_ID, name="Jane Smith", author_list_order=1).save(
        force_insert=True,
    )
    AnnotationAuthor(
        id=200,
        annotation_id=ANNOTATION_ID,
        name="Stale Author",
        corresponding_author_status=True,
        author_list_order=3,
    ).save(force_insert=True)
    AnnotationAuthor(annotation_id=STALE_ANNOTATION_ID, name="Jane Smith", author_list_order=1).save(
        force_insert=True,
    )
    AnnotationAuthor(
        annotation_id=STALE_ANNOTATION_ID,
        name="Stale Author",
        corresponding_author_status=True,
        author_list_order=3,
    ).save(force_insert=True)


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
