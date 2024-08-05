comment on column "public"."datasets" is E'Dataset Metadata';
comment on column "public"."datasets"."authors" is E'An array relationship';
comment on column "public"."datasets"."cell_component_id" is E'If this dataset only focuses on a specific part of a cell, include the subset here';
comment on column "public"."datasets"."cell_strain_id" is E'NCBI Identifier for the cell line or strain';
comment on column "public"."datasets"."funding_sources" is E'An array relationship';
comment on column "public"."datasets"."related_database_links" is E'If a CryoET dataset is also deposited into another database, e.g. EMPAIR, enter the database identifier here (e.g.https://www.ebi.ac.uk/empiar/EMPIAR-12345/).  Use a comma to separate multiple links.';
comment on column "public"."datasets"."runs" is E'An array relationship';

comment on column "public"."dataset_authors" is E'Authors of a dataset';
comment on column "public"."dataset_authors"."dataset" is E'An object relationship';
comment on column "public"."dataset_authors"."dataset_id" is NULL;
comment on column "public"."dataset_authors"."id" is NULL;
comment on column "public"."dataset_authors"."primary_author_status" is NULL;

comment on column "public"."dataset_funding" is E'Funding sources for a dataset';
comment on column "public"."dataset_funding"."dataset" is E'An object relationship';
comment on column "public"."dataset_funding"."dataset_id" is NULL;
comment on column "public"."dataset_funding"."id" is NULL;

comment on column "public"."runs" is E'Data related to an experiment run';
comment on column "public"."runs"."dataset" is E'An object relationship';
comment on column "public"."runs"."https_prefix" is E'The https directory path where this dataset is contained';
comment on column "public"."runs"."name" is E'Short name for the tilt series';
comment on column "public"."runs"."tiltseries" is E'An array relationship';
comment on column "public"."runs"."tomogram_voxel_spacings" is E'An array relationship';

comment on column "public"."tomogram_voxel_spacings" is E'The tomograms for each run are grouped by their voxel spacing';
comment on column "public"."tomogram_voxel_spacings"."annotations" is E'An array relationship';
comment on column "public"."tomogram_voxel_spacings"."https_prefix" is NULL;
comment on column "public"."tomogram_voxel_spacings"."id" is NULL;
comment on column "public"."tomogram_voxel_spacings"."run" is E'An object relationship';
comment on column "public"."tomogram_voxel_spacings"."run_id" is NULL;
comment on column "public"."tomogram_voxel_spacings"."s3_prefix" is NULL;
comment on column "public"."tomogram_voxel_spacings"."tomograms" is E'An array relationship';
comment on column "public"."tomogram_voxel_spacings"."voxel_spacing" is NULL;

comment on column "public"."tomograms" is E'information about the tomograms in the CryoET Data Portal';
comment on column "public"."tomograms"."authors" is E'An array relationship';
comment on column "public"."tomograms"."ctf_corrected" is NULL;
comment on column "public"."tomograms"."deposition_id" is E'id of the associated deposition.';
comment on column "public"."tomograms"."https_mrc_scale0" is E'https path to this tomogram in MRC format (no scaling)';
comment on column "public"."tomograms"."https_omezarr_dir" is E'HTTPS path to the this multiscale omezarr tomogram';
comment on column "public"."tomograms"."reconstruction_method" is E'Describe reconstruction method (Weighted backprojection, SART, SIRT)';
comment on column "public"."tomograms"."s3_omezarr_dir" is E'S3 path to the this multiscale omezarr tomogram';
comment on column "public"."tomograms"."tomogram_voxel_spacing" is E'An object relationship with a specific voxel spacing for this experiment run';
comment on column "public"."tomograms"."tomogram_voxel_spacing_id" is NULL;
comment on column "public"."tomograms"."type" is NULL;

comment on column "public"."tomogram_authors" is E'Authors for a tomogram';
comment on column "public"."tomogram_authors"."affiliation_address" is E'Address of the institution an annotator is affiliated with.';
comment on column "public"."tomogram_authors"."name" is E'Full name of an tomogram author (e.g. Jane Doe).';
comment on column "public"."tomogram_authors"."tomogram" is E'An object relationship';

comment on column "public"."annotations" is E'Inoformation about annotations for a given run';
comment on column "public"."annotations"."annotation_software" is NULL;
comment on column "public"."annotations"."authors" is E'An array relationship';
comment on column "public"."annotations"."deposition_id" is E'id of the associated deposition.';
comment on column "public"."annotations"."files" is E'An array relationship';
comment on column "public"."annotations"."https_metadata_path" is E'https path for the metadata json file for this annotation';
comment on column "public"."annotations"."method_type" is E'Provides information on the method type used for generating annotation';
comment on column "public"."annotations"."s3_metadata_path" is E's3 path for the metadata json file for this annotation';
comment on column "public"."annotations"."tomogram_voxel_spacing" is E'An object relationship';
comment on column "public"."annotations"."tomogram_voxel_spacing_id" is NULL;

comment on column "public"."annotation_files" is E'Information about associated files for a given annotation';
comment on column "public"."annotation_files"."annotation" is E'An object relationship';
comment on column "public"."annotation_files"."annotation_id" is NULL;
comment on column "public"."annotation_files"."format" is E'Format of the annotation object file';
comment on column "public"."annotation_files"."https_path" is E'https path of the annotation file';
comment on column "public"."annotation_files"."id" is NULL;

comment on column "public"."annotation_authors" is E'Authors for an annotation';
comment on column "public"."annotation_authors"."annotation" is E'An object relationship';
comment on column "public"."annotation_authors"."primary_author_status" is NULL;

comment on column "public"."tiltseries" is E'Tilt Series Metadata';
comment on column "public"."tiltseries"."aligned_tiltseries_binning" is E'The binning factor between the unaligned tilt series and the aligned tiltseries.';
comment on column "public"."tiltseries"."https_alignment_file" is NULL;
comment on column "public"."tiltseries"."https_angle_list" is NULL;
comment on column "public"."tiltseries"."https_collection_metadata" is NULL;
comment on column "public"."tiltseries"."https_mrc_bin1" is NULL;
comment on column "public"."tiltseries"."https_omezarr_dir" is NULL;
comment on column "public"."tiltseries"."id" is NULL;
comment on column "public"."tiltseries"."pixel_spacing" is E'Pixel spacing for the tilt series';
comment on column "public"."tiltseries"."related_empiar_entry" is E'If a tilt series is deposited into EMPIAR, enter the EMPIAR dataset identifier';
comment on column "public"."tiltseries"."run" is E'An object relationship';
comment on column "public"."tiltseries"."run_id" is NULL;
comment on column "public"."tiltseries"."s3_alignment_file" is NULL;
comment on column "public"."tiltseries"."s3_angle_list" is NULL; 
comment on column "public"."tiltseries"."s3_collection_metadata" is NULL;
comment on column "public"."tiltseries"."s3_mrc_bin1" is NULL;
comment on column "public"."tiltseries"."s3_omezarr_dir" is NULL;
comment on column "public"."tiltseries"."tilt_range" is E'The difference between tilt_min and tilt_max';
comment on column "public"."tiltseries"."tilt_step" is NULL;
