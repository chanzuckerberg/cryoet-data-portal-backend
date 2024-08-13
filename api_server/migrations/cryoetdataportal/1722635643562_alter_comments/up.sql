comment on table "public"."datasets" is E'Metadata for a dataset';
comment on column "public"."datasets"."cell_component_id" is E'If the dataset focuses on a specific part of a cell, the subset is included here';
comment on column "public"."datasets"."cell_strain_id" is E'Link to more information about the cell strain';
comment on column "public"."datasets"."related_database_links" is E'If a CryoET dataset is also deposited into another database, e.g. EMPIAR, enter the database identifier here (e.g.https://www.ebi.ac.uk/empiar/EMPIAR-12345/). Use a comma to separate multiple links.';

comment on table "public"."dataset_authors" is E'Metadata for authors of a dataset';
comment on column "public"."dataset_authors"."dataset_id" is E'Numeric identifier for the dataset this author corresponds to';
comment on column "public"."dataset_authors"."id" is E'A numeric identifier for this author (May change!)';
comment on column "public"."dataset_authors"."primary_author_status" is E'Indicating whether an author is the main person associated with the corresponding dataset';

comment on table "public"."dataset_funding" is E'Metadata for a dataset''s funding sources';
comment on column "public"."dataset_funding"."dataset_id" is E'Numeric identifier for the dataset this funding source corresponds to';
comment on column "public"."dataset_funding"."id" is E'A numeric identifier for this funding record (May change!)';

comment on table "public"."runs" is E'Metadata for an experiment run';
comment on column "public"."runs"."https_prefix" is E'The HTTPS directory path where this dataset is contained';
comment on column "public"."runs"."name" is E'Short name for this experiment run';

comment on table "public"."tomogram_voxel_spacings" is E'Metadata for a given voxel spacing related to tomograms and annotations';
comment on column "public"."tomogram_voxel_spacings"."https_prefix" is E'The HTTPS directory path where this tomogram voxel spacing is contained';
comment on column "public"."tomogram_voxel_spacings"."id" is E'Numeric identifier (May change!)';
comment on column "public"."tomogram_voxel_spacings"."run_id" is E'The ID of the run this tomogram voxel spacing is a part of';
comment on column "public"."tomogram_voxel_spacings"."s3_prefix" is E'The S3 public bucket path where this tomogram voxel spacing is contained';
comment on column "public"."tomogram_voxel_spacings"."voxel_spacing" is E'The voxel spacing for the tomograms in this set in angstroms';

comment on table "public"."tomograms" is E'Metadata for a tomogram';
comment on column "public"."tomograms"."ctf_corrected" is E'Whether this tomogram is CTF corrected';
comment on column "public"."tomograms"."deposition_id" is E'If the tomogram is part of a deposition, the related deposition''s id';
comment on column "public"."tomograms"."https_mrc_scale0" is E'HTTPS path to this tomogram in MRC format (no scaling)';
comment on column "public"."tomograms"."https_omezarr_dir" is E'HTTPS path to this tomogram in multiscale OME-Zarr format';
comment on column "public"."tomograms"."reconstruction_method" is E'Describe reconstruction method (Weighted back-projection, SART, SIRT)';
comment on column "public"."tomograms"."s3_omezarr_dir" is E'S3 path to this tomogram in multiscale OME-Zarr format';
comment on column "public"."tomograms"."tomogram_voxel_spacing_id" is E'The ID of the tomogram voxel spacing this tomogram is part of';
comment on column "public"."tomograms"."type" is E'Tomogram purpose (ex: CANONICAL)';

comment on table "public"."tomogram_authors" is E'Metadata for a tomogram''s authors';
comment on column "public"."tomogram_authors"."affiliation_address" is E'Address of the institution an author is affiliated with.';
comment on column "public"."tomogram_authors"."name" is E'Full name of an author (e.g. Jane Doe).';

comment on table "public"."annotations" is E'Metadata for an annotation';
comment on column "public"."annotations"."annotation_software" is E'Software used for generating this annotation';
comment on column "public"."annotations"."deposition_id" is E'If the annotation is part of a deposition, the related deposition''s id';
comment on column "public"."annotations"."https_metadata_path" is E'HTTPS path for the metadata json file for this annotation';
comment on column "public"."annotations"."method_type" is E'The method type for generating the annotation (e.g. manual, hybrid, automated)';
comment on column "public"."annotations"."s3_metadata_path" is E'S3 path for the metadata json file for this annotation';
comment on column "public"."annotations"."tomogram_voxel_spacing_id" is E'The ID of the tomogram voxel spacing this annotation is part of';

comment on table "public"."annotation_files" is E'Metadata for an annotation file';
comment on column "public"."annotation_files"."annotation_id" is E'The ID of the annotation this file applies to';
comment on column "public"."annotation_files"."format" is E'File format for this file';
comment on column "public"."annotation_files"."https_path" is E'HTTPS path for this annotation file';
comment on column "public"."annotation_files"."id" is E'Numeric identifier (May change!)';

comment on table "public"."annotation_authors" is E'Metadata for an annotation''s authors';
comment on column "public"."annotation_authors"."primary_author_status" is E'Indicating whether an author is the main person executing the annotation, especially on manual annotation (YES or NO)';

comment on table "public"."tiltseries" is E'Metadata about how a tilt series was generated, and locations of output files';
comment on column "public"."tiltseries"."aligned_tiltseries_binning" is E'Binning factor of the aligned tilt series';
comment on column "public"."tiltseries"."https_alignment_file" is E'HTTPS path to the alignment file for this tiltseries';
comment on column "public"."tiltseries"."https_angle_list" is E'HTTPS path to the angle list file for this tiltseries';
comment on column "public"."tiltseries"."https_collection_metadata" is E'HTTPS path to the collection metadata file for this tiltseries';
comment on column "public"."tiltseries"."https_mrc_bin1" is E'HTTPS path to this tiltseries in MRC format (no scaling)';
comment on column "public"."tiltseries"."https_omezarr_dir" is E'HTTPS path to this tomogram in multiscale OME-Zarr format';
comment on column "public"."tiltseries"."id" is E'Numeric identifier for this tilt series (this may change!)';
comment on column "public"."tiltseries"."pixel_spacing" is E'Pixel spacing equal in both axes in angstroms';
comment on column "public"."tiltseries"."related_empiar_entry" is E'If a tilt series is deposited into EMPIAR, the EMPIAR dataset identifier';
comment on column "public"."tiltseries"."run_id" is E'The ID of the experimental run this tilt series is part of';
comment on column "public"."tiltseries"."s3_alignment_file" is E'S3 path to the alignment file for this tilt series';
comment on column "public"."tiltseries"."s3_angle_list" is E'S3 path to the angle list file for this tilt series';
comment on column "public"."tiltseries"."s3_collection_metadata" is E'S3 path to the collection metadata file for this tiltseries';
comment on column "public"."tiltseries"."s3_mrc_bin1" is E'S3 path to this tiltseries in MRC format (no scaling)';
comment on column "public"."tiltseries"."s3_omezarr_dir" is E'S3 path to this tomogram in multiscale OME-Zarr format';
comment on column "public"."tiltseries"."tilt_range" is E'Total tilt range in degrees';
comment on column "public"."tiltseries"."tilt_step" is E'Tilt step in degrees';
