from peewee import (
    BooleanField,
    CharField,
    DateField,
    FloatField,
    ForeignKeyField,
    IntegerField,
    Model,
    PostgresqlDatabase,
)
from playhouse.postgres_ext import ArrayField

db = PostgresqlDatabase(None)


class BaseModel(Model):
    class Meta:
        database = db


class Dataset(BaseModel):
    class Meta:
        db_table = "datasets"

    id = IntegerField()
    title = CharField()
    description = CharField()
    deposition_date = DateField()
    release_date = DateField()
    last_modified_date = DateField()
    related_database_entries = CharField()
    related_database_links = CharField()
    dataset_publications = CharField()
    dataset_citations = CharField()
    sample_type = CharField()
    organism_name = CharField()
    organism_taxid = CharField()
    tissue_name = CharField()
    tissue_id = CharField()
    cell_name = CharField()
    cell_type_id = CharField()
    cell_strain_name = CharField()
    cell_strain_id = CharField()
    sample_preparation = CharField()
    grid_preparation = CharField()
    other_setup = CharField()
    s3_prefix = CharField()
    https_prefix = CharField()
    cell_component_name = CharField()
    cell_component_id = CharField()
    key_photo_url = CharField()
    key_photo_thumbnail_url = CharField()


class DatasetAuthor(BaseModel):
    class Meta:
        db_table = "dataset_authors"

    id = IntegerField()
    dataset_id = ForeignKeyField(Dataset, backref="authors")
    orcid = CharField()
    name = CharField()
    corresponding_author_status = BooleanField()
    primary_author_status = BooleanField()
    email = CharField()
    affiliation_name = CharField()
    affiliation_address = CharField()
    affiliation_identifier = CharField()
    author_list_order = IntegerField()


class DatasetFunding(BaseModel):
    class Meta:
        db_table = "dataset_funding"

    id = IntegerField()
    dataset_id = ForeignKeyField(Dataset, backref="funding_sources")
    funding_agency_name = CharField()
    grant_id = CharField()


class Run(BaseModel):
    class Meta:
        db_table = "runs"

    id = IntegerField()
    dataset_id = ForeignKeyField(Dataset, backref="runs")
    name = CharField()
    s3_prefix = CharField()
    https_prefix = CharField()


class TomogramVoxelSpacing(BaseModel):
    class Meta:
        db_table = "tomogram_voxel_spacings"

    id = IntegerField()
    run_id = ForeignKeyField(Run, backref="tomogram_voxel_spacings")
    voxel_spacing = FloatField()
    s3_prefix = CharField()
    https_prefix = CharField()


class Tomogram(BaseModel):
    class Meta:
        db_table = "tomograms"

    id = IntegerField()
    tomogram_voxel_spacing_id = ForeignKeyField(TomogramVoxelSpacing, backref="tomograms")
    name = CharField()
    size_x = IntegerField()
    size_y = IntegerField()
    size_z = IntegerField()
    voxel_spacing = FloatField()
    fiducial_alignment_status = CharField()
    reconstruction_method = CharField()
    reconstruction_software = CharField()
    processing = CharField()
    processing_software = CharField()
    tomogram_version = CharField()
    is_canonical = BooleanField()
    s3_omezarr_dir = CharField()
    https_omezarr_dir = CharField()
    s3_mrc_scale0 = CharField()
    https_mrc_scale0 = CharField()
    scale0_dimensions = CharField()
    scale1_dimensions = CharField()
    scale2_dimensions = CharField()
    ctf_corrected = BooleanField()
    offset_x = IntegerField()
    offset_y = IntegerField()
    offset_z = IntegerField()
    affine_transformation_matrix = ArrayField(dimensions=2)
    key_photo_url = CharField()
    key_photo_thumbnail_url = CharField()
    neuroglancer_config = CharField()
    type = CharField()


class TomogramAuthor(BaseModel):
    class Meta:
        db_table = "tomogram_authors"

    id = IntegerField()
    tomogram_id = ForeignKeyField(Tomogram, backref="authors")
    orcid = CharField()
    name = CharField()
    corresponding_author_status = BooleanField()
    primary_author_status = BooleanField()
    email = CharField()
    affiliation_name = CharField()
    affiliation_address = CharField()
    affiliation_identifier = CharField()
    author_list_order = IntegerField()


class Annotation(BaseModel):
    class Meta:
        db_table = "annotations"

    id = IntegerField()
    tomogram_voxel_spacing_id = ForeignKeyField(TomogramVoxelSpacing, backref="runs")
    s3_metadata_path = CharField()
    https_metadata_path = CharField()
    deposition_date = DateField()
    release_date = DateField()
    last_modified_date = DateField()
    annotation_publication = CharField()
    annotation_software = CharField()
    annotation_method = CharField()
    ground_truth_status = BooleanField()
    object_name = CharField()
    object_id = CharField()
    object_description = CharField()
    object_state = CharField()
    object_count = IntegerField()
    confidence_precision = FloatField()
    confidence_recall = FloatField()
    ground_truth_used = CharField()
    is_curator_recommended = BooleanField()


class AnnotationFiles(BaseModel):
    class Meta:
        db_table = "annotation_files"

    id = IntegerField()
    annotation_id = ForeignKeyField(Annotation, backref="files")
    shape_type = CharField()
    format = CharField()
    s3_path = CharField()
    https_path = CharField()
    is_visualization_default = BooleanField()


class AnnotationAuthor(BaseModel):
    class Meta:
        db_table = "annotation_authors"

    id = IntegerField()
    annotation_id = IntegerField()
    name = CharField()
    orcid = CharField()
    corresponding_author_status = BooleanField()
    primary_annotator_status = BooleanField()
    email = CharField()
    affiliation_name = CharField()
    affiliation_address = CharField()
    affiliation_identifier = CharField()
    author_list_order = IntegerField()


class TiltSeries(BaseModel):
    class Meta:
        db_table = "tiltseries"

    id = IntegerField()
    run_id = ForeignKeyField(Run, backref="tiltseries")
    s3_mrc_bin1 = CharField()
    s3_omezarr_dir = CharField()
    https_mrc_bin1 = CharField()
    https_omezarr_dir = CharField()
    s3_collection_metadata = CharField()
    https_collection_metadata = CharField()
    s3_angle_list = CharField()
    https_angle_list = CharField()
    s3_alignment_file = CharField()
    https_alignment_file = CharField()
    acceleration_voltage = IntegerField()
    spherical_aberration_constant = FloatField()
    microscope_manufacturer = CharField()
    microscope_model = CharField()
    microscope_energy_filter = CharField()
    microscope_phase_plate = CharField()
    microscope_image_corrector = CharField()
    microscope_additional_info = CharField()
    camera_manufacturer = CharField()
    camera_model = CharField()
    tilt_min = FloatField()
    tilt_max = FloatField()
    tilt_range = FloatField()
    tilt_step = FloatField()
    tilting_scheme = CharField()
    tilt_axis = FloatField()
    total_flux = FloatField()
    data_acquisition_software = FloatField()
    related_empiar_entry = CharField()
    binning_from_frames = FloatField()
    tilt_series_quality = IntegerField()
    is_aligned = BooleanField()
    pixel_spacing = FloatField()
    aligned_tiltseries_binning = IntegerField()
    frames_count = IntegerField()
