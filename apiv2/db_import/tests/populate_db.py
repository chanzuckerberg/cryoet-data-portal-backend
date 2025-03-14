from datetime import date, datetime

import sqlalchemy as sa
from database.models import (
    Alignment,
    Annotation,
    AnnotationAuthor,
    AnnotationFile,
    AnnotationMethodLink,
    AnnotationShape,
    Dataset,
    DatasetAuthor,
    DatasetFunding,
    Deposition,
    DepositionAuthor,
    Frame,
    PerSectionAlignmentParameters,
    PerSectionParameters,
    Run,
    Tiltseries,
    Tomogram,
    TomogramAuthor,
    TomogramVoxelSpacing,
)

FRAME_ID = 333
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
ANNOTATION_METHOD_LINK_ID = 802
ALIGNMENT_ID = 801
PER_SECTION_ALIGNMENT_PARAMETERS_ID = 901

STALE_RUN_ID = 902
STALE_TOMOGRAM_ID = 903
STALE_ANNOTATION_ID = 904
STALE_ALIGNMENT_ID = 1004


def model_to_dict(sa_object):
    return {item.key: getattr(sa_object, item.key) for item in sa.inspect(sa_object).mapper.column_attrs}


def stale_deposition_metadata() -> dict:
    return {
        "id": DEPOSITION_ID1,
        "title": "Test Deposition",
        "description": "Test Description",
        "deposition_date": date(2022, 4, 2),
        "release_date": date(2022, 6, 1),
        "last_modified_date": date(2022, 9, 2),
        "deposition_publications": "Publications",
    }


def stale_deposition_author() -> dict:
    return {
        "id": DEPOSITION_AUTHOR_ID,
        "deposition_id": DEPOSITION_ID1,
        "name": "Author 1",
        "author_list_order": 1,
        "corresponding_author_status": False,
        "primary_author_status": False,
    }


def write_data(function):
    def wrapper(session: sa.orm.Session, *args, **kwargs):
        obj = function(session, *args, **kwargs)
        if obj:
            session.add(obj)
        session.flush()

    return wrapper


@write_data
def populate_deposition2(session: sa.orm.Session) -> Deposition:
    metadata = stale_deposition_metadata()
    metadata["id"] = DEPOSITION_ID2
    return Deposition(**metadata)


@write_data
def populate_deposition(session: sa.orm.Session) -> Deposition:
    return Deposition(**stale_deposition_metadata())


@write_data
def populate_deposition_authors(session: sa.orm.Session) -> DepositionAuthor:
    return DepositionAuthor(**stale_deposition_author())


@write_data
def populate_dataset(session: sa.orm.Session) -> Dataset:
    today = datetime.now().date()
    populate_deposition(session)
    return Dataset(
        id=DATASET_ID,
        deposition_id=DEPOSITION_ID1,
        title="foo",
        description="bar",
        deposition_date=today,
        release_date=today,
        organism_name="bacteria x",
        last_modified_date=today,
        sample_type="cell",
        s3_prefix="s3://invalid_bucket/",
        https_prefix="https://invalid-site.com/1234",
    )


@write_data
def populate_dataset_authors(session: sa.orm.Session) -> DatasetAuthor:
    """`populate_dataset` must be called **before** calling this method!"""
    return DatasetAuthor(id=DATASET_AUTHOR_ID, dataset_id=DATASET_ID, name="Virginia Woolf", author_list_order=3)


@write_data
def populate_stale_dataset_authors(session: sa.orm.Session) -> DatasetAuthor:
    """`populate_dataset` must be called **before** calling this method!"""
    return DatasetAuthor(dataset_id=DATASET_ID, name="Stale Author", author_list_order=1)


@write_data
def populate_dataset_funding(session: sa.orm.Session) -> DatasetFunding:
    return DatasetFunding(
        id=DATASET_FUNDING_ID,
        dataset_id=DATASET_ID,
        funding_agency_name="Grant Provider 1",
        grant_id="1234",
    )


@write_data
def populate_stale_dataset_funding(session: sa.orm.Session) -> DatasetFunding:
    return DatasetFunding(dataset_id=DATASET_ID, funding_agency_name="Stale Grant Entry")


@write_data
def populate_run(session: sa.orm.Session) -> None:
    populate_dataset(session)
    default_args = {
        "dataset_id": DATASET_ID,
        "s3_prefix": "s3://test-bucket/RUN1",
        "https_prefix": "http://test.com/RUN1",
    }
    obj1 = Run(
        id=RUN1_ID,
        name="RUN1",
        **default_args,
    )
    obj2 = Run(
        id=RUN4_ID,
        name="RUN4",
        **default_args,
    )
    session.add(obj1)
    session.add(obj2)


@write_data
def populate_stale_run(session: sa.orm.Session) -> None:
    obj = Run(
        id=STALE_RUN_ID,
        dataset_id=DATASET_ID,
        name="RUN5",
        s3_prefix="s3://test-bucket/RUN5",
        https_prefix="http://test.com/RUN5",
    )
    session.add(obj)
    session.flush()
    populate_stale_tomogram_voxel_spacing(session, STALE_RUN_ID)


@write_data
def populate_tomogram_voxel_spacing(session: sa.orm.Session) -> None:
    populate_run(session)
    https_prefix = "http://test.com/RUN1/VoxelSpacing{vs}"
    session.add(
        TomogramVoxelSpacing(
            run_id=RUN1_ID,
            voxel_spacing=3.456,
            s3_prefix="s3://test-public-bucket/VoxelSpacing3.456/",
            https_prefix=https_prefix.format(vs=3.456),
        ),
    )
    session.add(
        TomogramVoxelSpacing(
            id=TOMOGRAM_VOXEL_ID1,
            run_id=RUN1_ID,
            voxel_spacing=12.3,
            s3_prefix="s3://test-public-bucket/VoxelSpacing12.3/",
            https_prefix=https_prefix.format(vs=12.3),
        ),
    )
    session.add(
        TomogramVoxelSpacing(
            id=TOMOGRAM_VOXEL_ID2,
            run_id=RUN1_ID,
            voxel_spacing=9.876,
            s3_prefix="s3://test-public-bucket/VoxelSpacing9.876/",
            https_prefix=https_prefix.format(vs=9.876),
        ),
    )


@write_data
def populate_stale_tomogram_voxel_spacing(session: sa.orm.Session, run_id: int = RUN1_ID) -> None:
    stale_voxel_spacing = TomogramVoxelSpacing(
        run_id=run_id,
        voxel_spacing=10.345,
        s3_prefix="s3://test-public-bucket/VoxelSpacing10.345/",
        https_prefix="http://test.com/RUN1/VoxelSpacing10.345/",
    )
    session.add(stale_voxel_spacing)
    stale_tomogram = Tomogram(
        tomogram_voxel_spacing_id=stale_voxel_spacing.id,
        deposition_id=DEPOSITION_ID1,
        name="RUN1",
        voxel_spacing=10.345,
        s3_omezarr_dir="s3://stale.zarr",
        https_omezarr_dir="http://test.com/stale.zarr",
        s3_mrc_file="s3://stale.mrc",
        https_mrc_file="http://test.com/stale.mrc",
        size_x=2,
        size_y=2,
        size_z=2,
        fiducial_alignment_status="FIDUCIAL",
        reconstruction_method="SART",
        reconstruction_software="",
        tomogram_version="0.5",
        scale0_dimensions="",
        scale1_dimensions="",
        scale2_dimensions="",
        processing="denoised",
        offset_x=0,
        offset_y=0,
        offset_z=0,
        is_portal_standard=True,
        deposition_date=datetime.min,
        release_date=datetime.min,
        last_modified_date=datetime.min,
    )
    session.add(stale_tomogram)
    session.add(TomogramAuthor(tomogram=stale_tomogram, name="Jane Smith", author_list_order=1))
    session.add(TomogramAuthor(tomogram=stale_tomogram, name="John John", author_list_order=2))
    stale_annotation = Annotation(
        s3_metadata_path="foo",
        https_metadata_path="foo",
        deposition_date="2025-04-01",
        release_date="2025-06-01",
        last_modified_date="2025-06-01",
        annotation_method="manual",
        method_type="manual",
        ground_truth_status=False,
        object_name="bar",
        object_id="invalid-id",
        object_count=200,
        annotation_software="bar",
    )
    session.add(stale_annotation)
    session.add(AnnotationAuthor(annotation=stale_annotation, name="Jane Smith", author_list_order=1))
    session.add(AnnotationAuthor(annotation=stale_annotation, name="John John", author_list_order=2))


@write_data
def populate_tomograms(session: sa.orm.Session) -> Tomogram:
    populate_tomogram_voxel_spacing(session)
    return Tomogram(
        id=TOMOGRAM_ID,
        deposition_id=DEPOSITION_ID1,
        run_id=RUN1_ID,
        tomogram_voxel_spacing_id=TOMOGRAM_VOXEL_ID1,
        name="RUN1",
        voxel_spacing=12.3,
        s3_omezarr_dir="s3://RUN1.zarr",
        https_omezarr_dir="http://test.com/RUN1.zarr",
        s3_mrc_file="s3://RUN1.mrc",
        https_mrc_file="http://test.com/RUN1.mrc",
        size_x=25,
        size_y=25,
        size_z=25,
        fiducial_alignment_status="FIDUCIAL",
        reconstruction_method="WBP",
        reconstruction_software="",
        tomogram_version="0.5",
        scale0_dimensions="",
        scale1_dimensions="",
        scale2_dimensions="",
        processing="raw",
        processing_software="tomo3D",
        offset_x=0,
        offset_y=0,
        offset_z=0,
        is_portal_standard=True,
        deposition_date=datetime.min,
        release_date=datetime.min,
        last_modified_date=datetime.min,
    )


@write_data
def populate_stale_tomograms(session: sa.orm.Session) -> Tomogram:
    return Tomogram(
        id=STALE_TOMOGRAM_ID,
        deposition_id=DEPOSITION_ID1,
        tomogram_voxel_spacing_id=TOMOGRAM_VOXEL_ID2,
        name="RUN1",
        voxel_spacing=12.3,
        s3_omezarr_dir="s3://stale.zarr",
        https_omezarr_dir="http://test.com/stale.zarr",
        s3_mrc_file="s3://stale.mrc",
        https_mrc_file="http://test.com/stale.mrc",
        size_x=2,
        size_y=2,
        size_z=2,
        fiducial_alignment_status="FIDUCIAL",
        reconstruction_method="SART",
        reconstruction_software="",
        tomogram_version="0.5",
        scale0_dimensions="",
        scale1_dimensions="",
        scale2_dimensions="",
        processing="denoised",
        offset_x=0,
        offset_y=0,
        offset_z=0,
        is_portal_standard=True,
        deposition_date=datetime.min,
        release_date=datetime.min,
        last_modified_date=datetime.min,
    )


@write_data
def populate_tomogram_authors(session: sa.orm.Session) -> TomogramAuthor:
    populate_tomograms(session)
    return TomogramAuthor(id=TOMOGRAM_AUTHOR_ID, tomogram_id=TOMOGRAM_ID, name="Jane Smith", author_list_order=1)


def populate_stale_tomogram_authors(session: sa.orm.Session) -> None:
    default_kwargs = {
        "name": "Stale Author 2",
        "primary_author_status": True,
        "author_list_order": 3,
    }
    author = TomogramAuthor(
        tomogram_id=STALE_TOMOGRAM_ID,
        **default_kwargs,
    )
    session.add(author)
    author2 = TomogramAuthor(
        tomogram_id=TOMOGRAM_ID,
        **default_kwargs,
    )
    session.add(author2)


@write_data
def populate_tiltseries(session: sa.orm.Session) -> Tiltseries:
    populate_run(session)
    tiltseries = Tiltseries(
        id=TILTSERIES_ID,
        run_id=RUN1_ID,
        s3_mrc_file="ts_foo.mrc",
        https_mrc_file="ts_foo.mrc",
        s3_omezarr_dir="ts_foo.zarr",
        https_omezarr_dir="ts_foo.zarr",
        acceleration_voltage=100,
        spherical_aberration_constant=1.0,
        microscope_manufacturer="FEI",
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
    frame = Frame(
        run_id=RUN1_ID,
        id=FRAME_ID,
        acquisition_order=0,
        deposition_id=DEPOSITION_ID1,
        s3_frame_path="s3://test-public-bucket/30001/RUN1/Frames/frame1",
        https_frame_path="https://foo.com/30001/RUN1/Frames/frame1",
    )
    session.add(frame)
    per_section_parameters = PerSectionParameters(
        astigmatic_angle=0.5,
        frame_id=FRAME_ID,
        major_defocus=0.5,
        minor_defocus=0.5,
        phase_shift=0.5,
        max_resolution=0.5,
        raw_angle=0.5,
        run_id=RUN1_ID,
        tiltseries_id=TILTSERIES_ID,
        z_index=0,
    )
    session.add(per_section_parameters)
    return tiltseries


@write_data
def populate_stale_tiltseries(session: sa.orm.Session) -> None:
    default_kwargs = {
        "s3_mrc_file": "ts_foo.mrc",
        "https_mrc_file": "ts_foo.mrc",
        "s3_omezarr_dir": "ts_foo.zarr",
        "https_omezarr_dir": "ts_foo.zarr",
        "acceleration_voltage": 100,
        "spherical_aberration_constant": 1.0,
        "microscope_manufacturer": "FEI",
        "microscope_model": "unknown",
        "microscope_energy_filter": "unknown",
        "camera_manufacturer": "unknown",
        "camera_model": "unknown",
        "tilt_min": 0,
        "tilt_max": 0,
        "tilt_range": 0,
        "tilt_step": 0,
        "tilt_axis": 1.0,
        "tilt_series_quality": 3,
        "total_flux": 0,
        "is_aligned": False,
        "pixel_spacing": 0.3,
        "tilting_scheme": "unknown",
        "data_acquisition_software": "unknown",
    }
    session.add(
        Tiltseries(
            run_id=RUN4_ID,
            **default_kwargs,
        ),
    )
    session.add(
        Tiltseries(
            run_id=STALE_RUN_ID,
            **default_kwargs,
        ),
    )


@write_data
def populate_stale_per_section_parameters(session: sa.orm.Session) -> PerSectionParameters:
    session.add(
        PerSectionParameters(
            run_id=STALE_RUN_ID,
            astigmatic_angle=0.1,
            frame_id=FRAME_ID,
            major_defocus=0.5,
            minor_defocus=0.5,
            phase_shift=0.5,
            max_resolution=0.5,
            raw_angle=0.5,
            tiltseries_id=TILTSERIES_ID,
            z_index=0,
        ))

@write_data
def populate_annotations(session: sa.orm.Session) -> Annotation:
    populate_deposition2(session)
    populate_tomogram_voxel_spacing(session)
    return Annotation(
        id=ANNOTATION_ID,
        run_id=RUN1_ID,
        deposition_id=DEPOSITION_ID2,
        s3_metadata_path=(
            "s3://test-public-bucket/30001/RUN1/Reconstructions/VoxelSpacing12.300/Annotations/100/foo-1.0.json"
        ),
        https_metadata_path="foo",
        deposition_date="2025-04-01",
        release_date="2025-06-01",
        last_modified_date="2025-06-01",
        annotation_method="2D CNN predictions",
        method_type="manual",
        ground_truth_status=False,
        object_name="foo",
        object_count=0,
        object_id="invalid-id",
        annotation_software="bar",
    )


@write_data
def populate_stale_annotations(session: sa.orm.Session) -> Annotation:
    return Annotation(
        id=STALE_ANNOTATION_ID,
        run_id=RUN1_ID,
        s3_metadata_path="foo",
        https_metadata_path="foo",
        deposition_date="2025-04-01",
        release_date="2025-06-01",
        last_modified_date="2025-06-01",
        annotation_method="manual",
        method_type="manual",
        ground_truth_status=False,
        object_name="bar",
        object_id="invalid-id",
        object_count=200,
        annotation_software="bar",
    )


@write_data
def populate_annotation_files(session: sa.orm.Session) -> None:
    populate_annotations(session)
    default_kwargs = {
        "s3_path": "s3://foo",
        "https_path": "https://foo",
    }
    shape = AnnotationShape(
        annotation_id=ANNOTATION_ID,
        shape_type="Point",
    )
    file = AnnotationFile(
        id=ANNOTATION_FILE_ID,
        annotation_shape=shape,
        tomogram_voxel_spacing_id=TOMOGRAM_VOXEL_ID1,
        format="ndjson",
        **default_kwargs,
    )
    file2 = AnnotationFile(
        tomogram_voxel_spacing_id=TOMOGRAM_VOXEL_ID1,
        annotation_shape=shape,
        format="mrc",
        **default_kwargs,
    )
    session.add(file)
    session.add(file2)


@write_data
def populate_stale_annotation_files(session: sa.orm.Session) -> None:
    populate_stale_annotations(session)
    default_kwargs = {
        "s3_path": "s3://foo-stale-annotation/point",
        "https_path": "https://foo-stale-annotation/point",
    }
    pointshape = AnnotationShape(
        annotation_id=STALE_ANNOTATION_ID,
        shape_type="Point",
    )
    segmaskshape = AnnotationShape(
        annotation_id=STALE_ANNOTATION_ID,
        shape_type="SegmentationMask",
    )
    file = AnnotationFile(
        annotation_shape=pointshape,
        format="ndjson",
        **default_kwargs,
    )
    session.add(file)
    file2 = AnnotationFile(
        annotation_shape=segmaskshape,
        format="mrc",
        **default_kwargs,
    )
    session.add(file2)


@write_data
def populate_annotation_authors(session: sa.orm.Session) -> None:
    populate_annotations(session)
    author = AnnotationAuthor(
        id=ANNOTATION_AUTHOR_ID,
        annotation_id=ANNOTATION_ID,
        name="Jane Smith",
        author_list_order=1,
    )
    session.add(author)
    author2 = AnnotationAuthor(
        name="Stale Author",
        annotation_id=ANNOTATION_ID,
        corresponding_author_status=True,
        author_list_order=1,
    )
    session.add(author2)


@write_data
def populate_stale_annotation_method_links(session: sa.orm.Session) -> None:
    populate_stale_annotations(session)
    session.add(
        AnnotationMethodLink(
            annotation_id=STALE_ANNOTATION_ID,
            name="Stale Link 0",
            link_type="other",
            link="https://some-link.com",
        ),
    )
    session.add(
        AnnotationMethodLink(
            annotation_id=STALE_ANNOTATION_ID,
            name="Stale link",
            link_type="source_code",
            link="https://stale-link.com",
        ),
    )


@write_data
def populate_annotation_method_links(session: sa.orm.Session) -> None:
    populate_annotations(session)
    row = AnnotationMethodLink(
        id=ANNOTATION_METHOD_LINK_ID,
        annotation_id=ANNOTATION_ID,
        link="https://fake-link.com/resources/100-foo-1.0_method.pdf",
        link_type="documentation",
        name="Method Documentation",
    )
    session.add(row)
    row2 = AnnotationMethodLink(
        annotation_id=ANNOTATION_ID,
        link="https://another-link.com",
        link_type="website",
        name="Stale Link",
    )
    session.add(row2)


@write_data
def populate_stale_annotation_authors(session: sa.orm.Session) -> None:
    populate_stale_annotations(session)
    session.add(AnnotationAuthor(annotation_id=STALE_ANNOTATION_ID, name="Jane Smith", author_list_order=1))
    session.add(
        AnnotationAuthor(
            annotation_id=STALE_ANNOTATION_ID,
            name="Stale Author",
            corresponding_author_status=True,
            author_list_order=3,
        ),
    )


@write_data
def populate_alignments(session: sa.orm.Session) -> Alignment:
    populate_tiltseries(session)
    return Alignment(
        id=ALIGNMENT_ID,
        run_id=RUN1_ID,
        deposition_id=DEPOSITION_ID1,
        tiltseries_id=TILTSERIES_ID,
        alignment_type="GLOBAL",
        volume_x_dimension=6300,
        volume_y_dimension=6300,
        volume_z_dimension=2000,
        volume_x_offset=0,
        volume_y_offset=0,
        volume_z_offset=0,
        tilt_offset=0,
        x_rotation_offset=0,
        affine_transformation_matrix="[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]",
        s3_alignment_metadata="alignment_metadata.json",
        https_alignment_metadata="alignment_metadata.json",
        is_portal_standard=True,
    )


@write_data
def populate_stale_alignments(session: sa.orm.Session) -> Alignment:
    populate_deposition2(session)
    populate_stale_tiltseries(session)
    return Alignment(
        id=STALE_ALIGNMENT_ID,
        tiltseries_id=TILTSERIES_ID,
        deposition_id=DEPOSITION_ID2,
        run_id=RUN1_ID,
        alignment_type="GLOBAL",
        volume_x_dimension=6300,
        volume_y_dimension=6300,
        volume_z_dimension=2000,
        volume_x_offset=0,
        volume_y_offset=0,
        volume_z_offset=0,
        tilt_offset=0,
        x_rotation_offset=0,
        affine_transformation_matrix="{1,0,0,0},{0,1,0,0},{0,0,1,0},{0,0,0,1}",
        s3_alignment_metadata="foo",
        https_alignment_metadata="foo",
        is_portal_standard=True,
    )


@write_data
def populate_per_section_alignment_parameters(session: sa.orm.Session) -> None:
    populate_alignments(session)
    per_section_alignment_params = PerSectionAlignmentParameters(
        alignment_id=ALIGNMENT_ID,
        in_plane_rotation=[0.5, 0.4, -0.7, 0.4],
        x_offset=-9.345,
        y_offset=4.789,
        z_index=0,
        tilt_angle=None,
        volume_x_rotation=1,
    )
    session.add(per_section_alignment_params)


@write_data
def populate_stale_per_section_alignment_parameters(session: sa.orm.Session) -> None:
    populate_stale_alignments(session)
    default_kwargs = {
        "in_plane_rotation": [0.4, 0.2, -0.3, 0.4],
        "x_offset": -5.345,
        "y_offset": 5.789,
        "z_index": 7,
        "tilt_angle": None,
        "volume_x_rotation": 0,
    }
    session.add(
        PerSectionAlignmentParameters(
            id=PER_SECTION_ALIGNMENT_PARAMETERS_ID,
            alignment_id=STALE_ALIGNMENT_ID,
            **default_kwargs,
        ),
    )
