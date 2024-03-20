from common.db_models import DatasetAuthor, DatasetFunding, Run, TiltSeries, TomogramVoxelSpacing


def populate_dataset_authors_table() -> None:
    DatasetAuthor(id=1, dataset_id=10000, name="Julia Child", author_list_order=1).save(force_insert=True)
    DatasetAuthor(id=2, dataset_id=30001, name="Stale Author", author_list_order=1).save(force_insert=True)
    DatasetAuthor(id=3, dataset_id=30001, name="Virginia Woolf", author_list_order=3).save(force_insert=True)


def populate_dataset_funding_table() -> None:
    DatasetFunding(id=1, dataset_id=10000, funding_agency_name="Grant Provider 1").save(force_insert=True)
    DatasetFunding(id=2, dataset_id=30001, funding_agency_name="Grant Provider 1", grant_id="foo").save(
        force_insert=True,
    )
    # TODO: Add functionality to remove stale data
    # models.DatasetFunding(id=3, dataset_id=30001, funding_agency_name="Grant Provider 2").save(force_insert=True)
    DatasetFunding(id=3, dataset_id=10000, funding_agency_name="Grant Provider 2").save(force_insert=True)


def populate_runs_table() -> None:
    Run(
        id=2,
        dataset_id=30001,
        name="RUN1",
        s3_prefix="s3://test-bucket/RUN1",
        https_prefix="http://test.com/RUN1",
    ).save(force_insert=True)


def populate_tomogram_voxel_spacing_table() -> None:
    TomogramVoxelSpacing(
        id=2,
        run_id=2,
        voxel_spacing=12.3,
        s3_prefix="s3://test/VS12.30",
        https_prefix="http://test.com/VS12.30",
    ).save(force_insert=True)


def populate_tiltseries_table() -> None:
    TiltSeries(
        id=2,
        run_id=2,
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


def populate_all_tables() -> None:
    populate_dataset_authors_table()
    populate_dataset_funding_table()
    populate_runs_table()
    populate_tiltseries_table()
    populate_tomogram_voxel_spacing_table()
