```mermaid
erDiagram
Tomogram {
    string name
    integer size_x
    integer size_y
    integer size_z
    float voxel_spacing
    fiducial_alignment_status_enum fiducial_alignment_status
    tomogram_reconstruction_method_enum reconstruction_method
    tomogram_processing_enum processing
    float tomogram_version
    string processing_software
    string reconstruction_software
    boolean is_canonical
    string s3_omezarr_dir
    string https_omezarr_dir
    string s3_mrc_file
    string https_mrc_file
    string scale0_dimensions
    string scale1_dimensions
    string scale2_dimensions
    boolean ctf_corrected
    integer offset_x
    integer offset_y
    integer offset_z
    string key_photo_url
    string key_photo_thumbnail_url
    string neuroglancer_config
    boolean is_standardized
    integer id
}
TomogramVoxelSpacing {
    float voxel_spacing
    string s3_prefix
    string https_prefix
    integer id
}
TomogramAuthor {
    integer id
    integer author_list_order
    string orcid
    string name
    string email
    string affiliation_name
    string affiliation_address
    string affiliation_identifier
    boolean corresponding_author_status
    boolean primary_author_status
}
Tiltseries {
    string s3_omezarr_dir
    string s3_mrc_file
    string https_omezarr_dir
    string https_mrc_file
    string s3_collection_metadata
    string https_collection_metadata
    string s3_angle_list
    string https_angle_list
    string s3_gain_file
    string https_gain_file
    integer acceleration_voltage
    float spherical_aberration_constant
    tiltseries_microscope_manufacturer_enum microscope_manufacturer
    string microscope_model
    string microscope_energy_filter
    string microscope_phase_plate
    string microscope_image_corrector
    string microscope_additional_info
    string camera_manufacturer
    string camera_model
    float tilt_min
    float tilt_max
    float tilt_range
    float tilt_step
    string tilting_scheme
    float tilt_axis
    float total_flux
    string data_acquisition_software
    string related_empiar_entry
    float binning_from_frames
    integer tilt_series_quality
    boolean is_aligned
    float pixel_spacing
    integer aligned_tiltseries_binning
    integer frames_count
    integer id
}
Run {
    string name
    string s3_prefix
    string https_prefix
    integer id
}
PerSectionParameters {
    integer z_index
    float defocus
    float astigmatism
    float astigmatic_angle
    integer id
}
PerSectionAlignmentParameters {
    integer z_index
    float x_offset
    float y_offset
    float in_plane_rotation
    float beam_tilt
    float tilt_angle
    integer id
}
Frame {
    float raw_angle
    integer acquisition_order
    float dose
    boolean is_gain_corrected
    string s3_gain_file
    string https_gain_file
    string s3_prefix
    string https_prefix
    integer id
}
Deposition {
    string title
    string description
    string deposition_publications
    string related_database_entries
    date deposition_date
    date release_date
    date last_modified_date
    string key_photo_url
    string key_photo_thumbnail_url
    integer id
}
DepositionAuthor {
    integer id
    integer author_list_order
    string orcid
    string name
    string email
    string affiliation_name
    string affiliation_address
    string affiliation_identifier
    boolean corresponding_author_status
    boolean primary_author_status
}
Dataset {
    string title
    string description
    string organism_name
    integer organism_taxid
    string tissue_name
    string tissue_id
    string cell_name
    string cell_type_id
    string cell_strain_name
    string cell_strain_id
    sample_type_enum sample_type
    string sample_preparation
    string grid_preparation
    string other_setup
    string key_photo_url
    string key_photo_thumbnail_url
    string cell_component_name
    string cell_component_id
    date deposition_date
    date release_date
    date last_modified_date
    string dataset_publications
    string related_database_entries
    string s3_prefix
    string https_prefix
    integer id
}
DatasetFunding {
    string funding_agency_name
    string grant_id
    integer id
}
DatasetAuthor {
    integer id
    integer author_list_order
    string orcid
    string name
    string email
    string affiliation_name
    string affiliation_address
    string affiliation_identifier
    boolean corresponding_author_status
    boolean primary_author_status
}
Annotation {
    string s3_metadata_path
    string https_metadata_path
    string annotation_publication
    string annotation_method
    string method_links
    boolean ground_truth_status
    string object_id
    string object_name
    string object_description
    string object_state
    integer object_count
    float confidence_precision
    float confidence_recall
    string ground_truth_used
    string annotation_software
    boolean is_curator_recommended
    annotation_method_type_enum method_type
    date deposition_date
    date release_date
    date last_modified_date
    integer id
}
AnnotationShape {
    annotation_file_shape_type_enum shape_type
    integer id
}
AnnotationFile {
    string format
    string s3_path
    string https_path
    boolean is_visualization_default
    annotation_file_source_enum source
    integer id
}
AnnotationAuthor {
    integer id
    integer author_list_order
    string orcid
    string name
    string email
    string affiliation_name
    string affiliation_address
    string affiliation_identifier
    boolean corresponding_author_status
    boolean primary_author_status
}
Alignment {
    alignment_type_enum alignment_type
    float volume_x_dimension
    float volume_y_dimension
    float volume_z_dimension
    float volume_x_offset
    float volume_y_offset
    float volume_z_offset
    float x_rotation_offset
    float tilt_offset
    string local_alignment_file
    string affine_transformation_matrix
    integer id
}

Tomogram ||--|o Alignment : "alignment"
Tomogram ||--}o TomogramAuthor : "authors"
Tomogram ||--|| Deposition : "deposition"
Tomogram ||--|o Run : "run"
Tomogram ||--|o TomogramVoxelSpacing : "tomogram_voxel_spacing"
TomogramVoxelSpacing ||--}o AnnotationFile : "annotation_files"
TomogramVoxelSpacing ||--|o Run : "run"
TomogramVoxelSpacing ||--}o Tomogram : "tomograms"
TomogramAuthor ||--|o Tomogram : "tomogram"
Tiltseries ||--}o Alignment : "alignments"
Tiltseries ||--}o PerSectionParameters : "per_section_parameters"
Tiltseries ||--|| Run : "run"
Tiltseries ||--|o Deposition : "deposition"
Run ||--}o Alignment : "alignments"
Run ||--}o Annotation : "annotations"
Run ||--|| Dataset : "dataset"
Run ||--}o Frame : "frames"
Run ||--}o Tiltseries : "tiltseries"
Run ||--}o TomogramVoxelSpacing : "tomogram_voxel_spacings"
Run ||--}o Tomogram : "tomograms"
PerSectionParameters ||--|| Frame : "frame"
PerSectionParameters ||--|| Tiltseries : "tiltseries"
PerSectionAlignmentParameters ||--|| Alignment : "alignment"
Frame ||--|o Deposition : "deposition"
Frame ||--}o PerSectionParameters : "per_section_parameters"
Frame ||--|o Run : "run"
Deposition ||--}o DepositionAuthor : "authors"
Deposition ||--}o Alignment : "alignments"
Deposition ||--}o Annotation : "annotations"
Deposition ||--}o Dataset : "datasets"
Deposition ||--}o Frame : "frames"
Deposition ||--}o Tiltseries : "tiltseries"
Deposition ||--}o Tomogram : "tomograms"
Deposition ||--}o DepositionType : "deposition_types"
DepositionAuthor ||--|| Deposition : "deposition"
Dataset ||--|| Deposition : "deposition"
Dataset ||--}o DatasetFunding : "funding_sources"
Dataset ||--}o DatasetAuthor : "authors"
Dataset ||--}o Run : "runs"
DatasetFunding ||--|o Dataset : "dataset"
DatasetAuthor ||--|o Dataset : "dataset"
Annotation ||--|o Run : "run"
Annotation ||--}o AnnotationShape : "annotation_shapes"
Annotation ||--}o AnnotationAuthor : "authors"
Annotation ||--|o Deposition : "deposition"
AnnotationShape ||--|o Annotation : "annotation"
AnnotationShape ||--}o AnnotationFile : "annotation_files"
AnnotationFile ||--|o Alignment : "alignment"
AnnotationFile ||--|o AnnotationShape : "annotation_shape"
AnnotationFile ||--|o TomogramVoxelSpacing : "tomogram_voxel_spacing"
AnnotationAuthor ||--|o Annotation : "annotation"
Alignment ||--}o AnnotationFile : "annotation_files"
Alignment ||--}o PerSectionAlignmentParameters : "per_section_alignments"
Alignment ||--|o Deposition : "deposition"
Alignment ||--|o Tiltseries : "tiltseries"
Alignment ||--}o Tomogram : "tomograms"
Alignment ||--|o Run : "run"

```
