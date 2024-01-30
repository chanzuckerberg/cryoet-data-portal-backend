SET check_function_bodies = false;
CREATE TABLE public.annotation_authors (
    id integer NOT NULL,
    annotation_id integer NOT NULL,
    name character varying NOT NULL,
    orcid character varying,
    corresponding_author_status boolean,
    primary_annotator_status boolean,
    email character varying,
    affiliation_name character varying,
    affiliation_address character varying,
    affiliation_identifier character varying
);
COMMENT ON TABLE public.annotation_authors IS 'Authors for an annotation';
COMMENT ON COLUMN public.annotation_authors.id IS 'Numeric identifier for this annotation author (this may change!)';
COMMENT ON COLUMN public.annotation_authors.annotation_id IS 'Reference to the annotation this author contributed to';
COMMENT ON COLUMN public.annotation_authors.name IS 'Full name of an annotation author (e.g. Jane Doe).';
COMMENT ON COLUMN public.annotation_authors.orcid IS 'A unique, persistent identifier for researchers, provided by ORCID.';
COMMENT ON COLUMN public.annotation_authors.corresponding_author_status IS 'Indicating whether an annotator is the corresponding author (YES or NO)';
COMMENT ON COLUMN public.annotation_authors.primary_annotator_status IS 'Indicating whether an annotator is the main person executing the annotation, especially on manual annotation (YES or NO)';
COMMENT ON COLUMN public.annotation_authors.email IS 'Email address for this author';
COMMENT ON COLUMN public.annotation_authors.affiliation_name IS 'Name of the institution an annotator is affiliated with. Sometimes, one annotator may have multiple affiliations.';
COMMENT ON COLUMN public.annotation_authors.affiliation_address IS 'Address of the institution an annotator is affiliated with.';
COMMENT ON COLUMN public.annotation_authors.affiliation_identifier IS 'A unique identifier assigned to the affiliated institution by The Research Organization Registry (ROR).';
CREATE SEQUENCE public.annotation_authors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.annotation_authors_id_seq OWNED BY public.annotation_authors.id;
CREATE TABLE public.annotations (
    id integer NOT NULL,
    s3_metadata_path character varying NOT NULL,
    https_metadata_path character varying NOT NULL,
    s3_annotations_path character varying,
    https_annotations_path character varying,
    deposition_date date NOT NULL,
    release_date date NOT NULL,
    last_modified_date date,
    annotation_publication character varying,
    annotation_method character varying NOT NULL,
    ground_truth_status boolean NOT NULL,
    object_name character varying NOT NULL,
    object_id character varying NOT NULL,
    object_description character varying,
    object_state character varying,
    shape_type character varying NOT NULL,
    object_weight numeric,
    object_diameter numeric,
    object_width numeric,
    object_count integer NOT NULL,
    confidence_precision numeric,
    confidence_recall numeric,
    ground_truth_used character varying,
    tomogram_voxel_spacing_id integer,
    annotation_software character varying
);
COMMENT ON TABLE public.annotations IS 'Inoformation about annotations for a given run';
COMMENT ON COLUMN public.annotations.id IS 'Numeric identifier (May change!)';
COMMENT ON COLUMN public.annotations.s3_metadata_path IS 's3 path for the metadata json file for this annotation';
COMMENT ON COLUMN public.annotations.https_metadata_path IS 'https path for the metadata json file for this annotation';
COMMENT ON COLUMN public.annotations.s3_annotations_path IS 's3 path for the annotations file for these annotations';
COMMENT ON COLUMN public.annotations.https_annotations_path IS 'https path for the annotations file for these annotations';
COMMENT ON COLUMN public.annotations.deposition_date IS 'Date when an annotation set is initially received by the Data Portal.';
COMMENT ON COLUMN public.annotations.release_date IS 'Date when annotation data is made public by the Data Portal.';
COMMENT ON COLUMN public.annotations.last_modified_date IS 'Date when an annotation was last modified in the Data Portal';
COMMENT ON COLUMN public.annotations.annotation_publication IS 'DOIs for publications that describe the dataset. Use a comma to separate multiple DOIs.';
COMMENT ON COLUMN public.annotations.annotation_method IS 'Describe how the annotation is made (e.g. Manual, crYoLO, Positive Unlabeled Learning, template matching)';
COMMENT ON COLUMN public.annotations.ground_truth_status IS 'Whether an annotation is considered ground truth, as determined by the annotator.';
COMMENT ON COLUMN public.annotations.object_name IS 'Name of the object being annotated (e.g. ribosome, nuclear pore complex, actin filament, membrane)';
COMMENT ON COLUMN public.annotations.object_id IS 'Gene Ontology Cellular Component identifier for the annotation object';
COMMENT ON COLUMN public.annotations.object_description IS 'A textual description of the annotation object, can be a longer description to include additional information not covered by the Annotation object name and state.';
COMMENT ON COLUMN public.annotations.object_state IS 'Molecule state annotated (e.g. open, closed)';
COMMENT ON COLUMN public.annotations.shape_type IS 'The format are the individual annotations are stored in';
COMMENT ON COLUMN public.annotations.object_weight IS 'Molecular weight of the annotation object, in Dalton';
COMMENT ON COLUMN public.annotations.object_diameter IS 'Diameter of the annotation object in Angstrom; applicable if the object shape is point or vector';
COMMENT ON COLUMN public.annotations.object_width IS 'Average width of the annotation object in Angstroms; applicable if the object shape is line';
COMMENT ON COLUMN public.annotations.object_count IS 'Number of objects identified';
COMMENT ON COLUMN public.annotations.confidence_precision IS 'Describe the confidence level of the annotation. Precision is defined as the % of annotation objects being true positive';
COMMENT ON COLUMN public.annotations.confidence_recall IS 'Describe the confidence level of the annotation. Recall is defined as the % of true positives being annotated correctly';
COMMENT ON COLUMN public.annotations.ground_truth_used IS 'Annotation filename used as ground truth for precision and recall';
CREATE SEQUENCE public.annotations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.annotations_id_seq OWNED BY public.annotations.id;
CREATE TABLE public.dataset_authors (
    id integer NOT NULL,
    name character varying NOT NULL,
    orcid character varying,
    corresponding_author_status boolean,
    email character varying,
    affiliation_name character varying,
    affiliation_address character varying,
    affiliation_identifier character varying,
    dataset_id integer NOT NULL,
    primary_author_status boolean
);
COMMENT ON TABLE public.dataset_authors IS 'Authors of a dataset';
COMMENT ON COLUMN public.dataset_authors.name IS 'Full name of a dataset author (e.g. Jane Doe).';
COMMENT ON COLUMN public.dataset_authors.orcid IS 'A unique, persistent identifier for researchers, provided by ORCID.';
COMMENT ON COLUMN public.dataset_authors.corresponding_author_status IS 'Indicating whether an author is the corresponding author';
COMMENT ON COLUMN public.dataset_authors.email IS 'Email address for each author';
COMMENT ON COLUMN public.dataset_authors.affiliation_name IS 'Name of the institutions an author is affiliated with. Comma separated';
COMMENT ON COLUMN public.dataset_authors.affiliation_address IS 'Address of the institution an author is affiliated with.';
COMMENT ON COLUMN public.dataset_authors.affiliation_identifier IS 'A unique identifier assigned to the affiliated institution by The Research Organization Registry (ROR).';
CREATE SEQUENCE public.dataset_authors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.dataset_authors_id_seq OWNED BY public.dataset_authors.id;
CREATE TABLE public.dataset_funding (
    id integer NOT NULL,
    dataset_id integer NOT NULL,
    funding_agency_name character varying NOT NULL,
    grant_id character varying
);
COMMENT ON TABLE public.dataset_funding IS 'Funding sources for a dataset';
COMMENT ON COLUMN public.dataset_funding.funding_agency_name IS 'Name of the funding agency.';
COMMENT ON COLUMN public.dataset_funding.grant_id IS 'Grant identifier provided by the funding agency.';
CREATE SEQUENCE public.dataset_funding_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.dataset_funding_id_seq OWNED BY public.dataset_funding.id;
CREATE TABLE public.datasets (
    id integer NOT NULL,
    title character varying NOT NULL,
    description character varying NOT NULL,
    deposition_date date NOT NULL,
    release_date date NOT NULL,
    last_modified_date date,
    related_database_entries character varying,
    related_database_links character varying,
    dataset_publications character varying,
    dataset_citations character varying,
    sample_type character varying NOT NULL,
    organism_name character varying,
    organism_taxid character varying,
    tissue_name character varying,
    tissue_id character varying,
    cell_name character varying,
    cell_type_id character varying,
    cell_strain_name character varying,
    cell_strain_id character varying,
    sample_preparation character varying,
    grid_preparation character varying,
    other_setup character varying,
    s3_prefix character varying NOT NULL,
    https_prefix character varying NOT NULL
);
COMMENT ON TABLE public.datasets IS 'Dataset Metadata';
COMMENT ON COLUMN public.datasets.id IS 'An identifier for a CryoET dataset, assigned by the Data Portal. Used to identify the dataset as the directory name in data tree';
COMMENT ON COLUMN public.datasets.title IS 'Title of a CryoET dataset';
COMMENT ON COLUMN public.datasets.description IS 'A short description of a CryoET dataset, similar to an abstract for a journal article or dataset.';
COMMENT ON COLUMN public.datasets.deposition_date IS 'Date when a dataset is initially received by the Data Portal.';
COMMENT ON COLUMN public.datasets.release_date IS 'Date when a dataset is made available on the Data Portal.';
COMMENT ON COLUMN public.datasets.last_modified_date IS 'Date when a released dataset is last modified.';
COMMENT ON COLUMN public.datasets.related_database_entries IS 'If a CryoET dataset is also deposited into another database, enter the database identifier here (e.g. EMPIAR-11445). Use a comma to separate multiple identifiers.';
COMMENT ON COLUMN public.datasets.related_database_links IS 'If a CryoET dataset is also deposited into another database, e.g. EMPAIR, enter the database identifier here (e.g.https://www.ebi.ac.uk/empiar/EMPIAR-12345/).  Use a comma to separate multiple links.';
COMMENT ON COLUMN public.datasets.dataset_publications IS 'DOIs for publications that describe the dataset. Use a comma to separate multiple DOIs.';
COMMENT ON COLUMN public.datasets.dataset_citations IS 'DOIs for publications that cite the dataset. Use a comma to separate multiple DOIs.';
COMMENT ON COLUMN public.datasets.sample_type IS 'Type of samples used in a CryoET study. (cell, tissue, organism, intact organelle, in-vitro mixture, in-silico synthetic data, other)';
COMMENT ON COLUMN public.datasets.organism_name IS 'Name of the organism from which a biological sample used in a CryoET study is derived from, e.g. homo sapiens';
COMMENT ON COLUMN public.datasets.organism_taxid IS 'NCBI taxonomy identifier for the organism, e.g. 9606';
COMMENT ON COLUMN public.datasets.tissue_name IS 'Name of the tissue from which a biological sample used in a CryoET study is derived from.';
COMMENT ON COLUMN public.datasets.tissue_id IS 'UBERON identifier for the tissue';
COMMENT ON COLUMN public.datasets.cell_name IS 'Name of the cell from which a biological sample used in a CryoET study is derived from.';
COMMENT ON COLUMN public.datasets.cell_type_id IS 'Cell Ontology identifier for the cell type';
COMMENT ON COLUMN public.datasets.cell_strain_name IS 'Cell line or strain for the sample.';
COMMENT ON COLUMN public.datasets.cell_strain_id IS 'NCBI Identifier for the cell line or strain';
COMMENT ON COLUMN public.datasets.sample_preparation IS 'Describe how the sample was prepared.';
COMMENT ON COLUMN public.datasets.grid_preparation IS 'Describe Cryo-ET grid preparation.';
COMMENT ON COLUMN public.datasets.other_setup IS 'Describe other setup not covered by sample preparation or grid preparation that may make this dataset unique in  the same publication';
COMMENT ON COLUMN public.datasets.s3_prefix IS 'The S3 public bucket path where this dataset is contained';
COMMENT ON COLUMN public.datasets.https_prefix IS 'The https directory path where this dataset is contained';
CREATE TABLE public.runs (
    id integer NOT NULL,
    dataset_id integer NOT NULL,
    name character varying NOT NULL,
    s3_prefix character varying NOT NULL,
    https_prefix character varying NOT NULL
);
COMMENT ON TABLE public.runs IS 'Data related to an experiment run';
COMMENT ON COLUMN public.runs.id IS 'Numeric identifier (May change!)';
COMMENT ON COLUMN public.runs.dataset_id IS 'Reference to the dataset this run is a part of';
COMMENT ON COLUMN public.runs.name IS 'Short name for the tilt series';
COMMENT ON COLUMN public.runs.s3_prefix IS 'The S3 public bucket path where this dataset is contained';
COMMENT ON COLUMN public.runs.https_prefix IS 'The https directory path where this dataset is contained';
CREATE SEQUENCE public.runs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.runs_id_seq OWNED BY public.runs.id;
CREATE TABLE public.tiltseries (
    id integer NOT NULL,
    run_id integer NOT NULL,
    s3_mrc_bin1 character varying NOT NULL,
    s3_mrc_bin2 character varying NOT NULL,
    s3_mrc_bin4 character varying NOT NULL,
    s3_omezarr_dir character varying NOT NULL,
    https_mrc_bin1 character varying NOT NULL,
    https_mrc_bin2 character varying NOT NULL,
    https_mrc_bin4 character varying NOT NULL,
    https_omezarr_dir character varying NOT NULL,
    s3_collection_metadata character varying,
    https_collection_metadata character varying,
    s3_angle_list character varying NOT NULL,
    https_angle_list character varying NOT NULL,
    s3_alignment_file character varying NOT NULL,
    https_alignment_file character varying NOT NULL,
    acceleration_voltage integer NOT NULL,
    spherical_aberration_constant numeric NOT NULL,
    microscope_manufacturer character varying NOT NULL,
    microscope_model character varying NOT NULL,
    microscope_energy_filter character varying NOT NULL,
    microscope_phase_plate character varying,
    microscope_image_corrector character varying,
    microscope_additional_info character varying,
    camera_manufacturer character varying NOT NULL,
    camera_model character varying NOT NULL,
    tilt_min numeric NOT NULL,
    tilt_max numeric NOT NULL,
    tilt_range numeric NOT NULL,
    tilt_step numeric NOT NULL,
    tilting_scheme character varying NOT NULL,
    tilt_axis numeric NOT NULL,
    total_flux numeric NOT NULL,
    data_acquisition_software character varying NOT NULL,
    related_empiar_entry character varying,
    binning_from_frames numeric NOT NULL,
    tilt_series_quality integer NOT NULL
);
COMMENT ON TABLE public.tiltseries IS 'Tilt Series Metadata';
COMMENT ON COLUMN public.tiltseries.acceleration_voltage IS 'Electron Microscope Accelerator voltage in volts';
COMMENT ON COLUMN public.tiltseries.spherical_aberration_constant IS 'Spherical Aberration Constant of the objective lens in millimeters';
COMMENT ON COLUMN public.tiltseries.microscope_manufacturer IS 'Name of the microscope manufacturer';
COMMENT ON COLUMN public.tiltseries.microscope_model IS 'Microscope model name';
COMMENT ON COLUMN public.tiltseries.microscope_energy_filter IS 'Energy filter setup used';
COMMENT ON COLUMN public.tiltseries.microscope_phase_plate IS 'Phase plate configuration';
COMMENT ON COLUMN public.tiltseries.microscope_image_corrector IS 'Image corrector setup';
COMMENT ON COLUMN public.tiltseries.microscope_additional_info IS 'Other microscope optical setup information, in addition to energy filter, phase plate and image corrector';
COMMENT ON COLUMN public.tiltseries.camera_manufacturer IS 'Name of the camera manufacturer';
COMMENT ON COLUMN public.tiltseries.camera_model IS 'Camera model name';
COMMENT ON COLUMN public.tiltseries.tilt_min IS 'Minimal tilt angle in degrees';
COMMENT ON COLUMN public.tiltseries.tilt_max IS 'Maximal tilt angle in degrees';
COMMENT ON COLUMN public.tiltseries.tilt_range IS 'The difference between tilt_min and tilt_max';
COMMENT ON COLUMN public.tiltseries.tilting_scheme IS 'The order of stage tilting during acquisition of the data';
COMMENT ON COLUMN public.tiltseries.tilt_axis IS 'Rotation angle in degrees';
COMMENT ON COLUMN public.tiltseries.total_flux IS 'Number of Electrons reaching the specimen in a square Angstrom area for the entire tilt series';
COMMENT ON COLUMN public.tiltseries.data_acquisition_software IS 'Software used to collect data';
COMMENT ON COLUMN public.tiltseries.related_empiar_entry IS 'If a tilt series is deposited into EMPIAR, enter the EMPIAR dataset identifier';
COMMENT ON COLUMN public.tiltseries.binning_from_frames IS 'Describes the binning factor from frames to tilt series file';
COMMENT ON COLUMN public.tiltseries.tilt_series_quality IS 'Author assessment of tilt series quality within the dataset (1-5, 5 is best)';
CREATE SEQUENCE public.tiltseries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.tiltseries_id_seq OWNED BY public.tiltseries.id;
CREATE TABLE public.tomogram_voxel_spacings (
    id integer NOT NULL,
    run_id integer NOT NULL,
    voxel_spacing numeric NOT NULL,
    s3_prefix character varying,
    https_prefix character varying
);
COMMENT ON TABLE public.tomogram_voxel_spacings IS 'The tomograms for each run are grouped by their voxel spacing';
CREATE SEQUENCE public.tomogram_voxel_spacing_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.tomogram_voxel_spacing_id_seq OWNED BY public.tomogram_voxel_spacings.id;
CREATE TABLE public.tomograms (
    id integer NOT NULL,
    name character varying NOT NULL,
    size_x integer NOT NULL,
    size_y integer NOT NULL,
    size_z integer NOT NULL,
    voxel_spacing numeric NOT NULL,
    fiducial_alignment_status character varying NOT NULL,
    reconstruction_method character varying NOT NULL,
    reconstruction_software character varying NOT NULL,
    processing character varying NOT NULL,
    processing_software character varying,
    tomogram_version character varying NOT NULL,
    is_canonical boolean,
    s3_omezarr_dir character varying NOT NULL,
    https_omezarr_dir character varying NOT NULL,
    s3_mrc_scale0 character varying NOT NULL,
    s3_mrc_scale1 character varying NOT NULL,
    s3_mrc_scale2 character varying NOT NULL,
    https_mrc_scale0 character varying NOT NULL,
    https_mrc_scale1 character varying NOT NULL,
    https_mrc_scale2 character varying NOT NULL,
    scale0_dimensions character varying NOT NULL,
    scale1_dimensions character varying NOT NULL,
    scale2_dimensions character varying NOT NULL,
    ctf_corrected boolean,
    tomogram_voxel_spacing_id integer
);
COMMENT ON TABLE public.tomograms IS 'information about the tomograms in the CryoET Data Portal';
COMMENT ON COLUMN public.tomograms.id IS 'Numeric identifier for this tomogram (this may change!)';
COMMENT ON COLUMN public.tomograms.name IS 'Short name for this tomogram';
COMMENT ON COLUMN public.tomograms.size_x IS 'Number of pixels in the 3D data fast axis';
COMMENT ON COLUMN public.tomograms.size_y IS 'Number of pixels in the 3D data medium axis';
COMMENT ON COLUMN public.tomograms.size_z IS 'Number of pixels in the 3D data slow axis.  This is the image projection direction at zero stage tilt';
COMMENT ON COLUMN public.tomograms.voxel_spacing IS 'Voxel spacing equal in all three axes in angstroms';
COMMENT ON COLUMN public.tomograms.fiducial_alignment_status IS 'Fiducial Alignment status: True = aligned with fiducial False = aligned without fiducial';
COMMENT ON COLUMN public.tomograms.reconstruction_method IS 'Describe reconstruction method (Weighted backprojection, SART, SIRT)';
COMMENT ON COLUMN public.tomograms.reconstruction_software IS 'Name of software used for reconstruction';
COMMENT ON COLUMN public.tomograms.processing IS 'Describe additional processing used to derive the tomogram';
COMMENT ON COLUMN public.tomograms.processing_software IS 'Processing software used to derive the tomogram';
COMMENT ON COLUMN public.tomograms.tomogram_version IS 'Version of tomogram using the same software and post-processing. Version of tomogram using the same software and post-processing. This will be presented as the latest version';
COMMENT ON COLUMN public.tomograms.is_canonical IS 'Is this tomogram considered the canonical tomogram for the run experiment? True=Yes';
COMMENT ON COLUMN public.tomograms.s3_omezarr_dir IS 'S3 path to the this multiscale omezarr tomogram';
COMMENT ON COLUMN public.tomograms.https_omezarr_dir IS 'HTTPS path to the this multiscale omezarr tomogram';
COMMENT ON COLUMN public.tomograms.s3_mrc_scale0 IS 'S3 path to this tomogram in MRC format (no scaling)';
COMMENT ON COLUMN public.tomograms.s3_mrc_scale1 IS 'S3 path to this tomogram in MRC format (downscaled to 50%)';
COMMENT ON COLUMN public.tomograms.s3_mrc_scale2 IS 'S3 path to this tomogram in MRC format (downscaled to 25%)';
COMMENT ON COLUMN public.tomograms.https_mrc_scale0 IS 'https path to this tomogram in MRC format (no scaling)';
COMMENT ON COLUMN public.tomograms.https_mrc_scale1 IS 'https path to this tomogram in MRC format (downscaled to 50%)';
COMMENT ON COLUMN public.tomograms.https_mrc_scale2 IS 'https path to this tomogram in MRC format (downscaled to 25%)';
COMMENT ON COLUMN public.tomograms.scale0_dimensions IS 'comma separated x,y,z dimensions of the unscaled tomogram';
COMMENT ON COLUMN public.tomograms.scale1_dimensions IS 'comma separated x,y,z dimensions of the scale1 tomogram';
COMMENT ON COLUMN public.tomograms.scale2_dimensions IS 'comma separated x,y,z dimensions of the scale2 tomogram';
CREATE SEQUENCE public.tomograms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.tomograms_id_seq OWNED BY public.tomograms.id;
ALTER TABLE ONLY public.annotation_authors ALTER COLUMN id SET DEFAULT nextval('public.annotation_authors_id_seq'::regclass);
ALTER TABLE ONLY public.annotations ALTER COLUMN id SET DEFAULT nextval('public.annotations_id_seq'::regclass);
ALTER TABLE ONLY public.dataset_authors ALTER COLUMN id SET DEFAULT nextval('public.dataset_authors_id_seq'::regclass);
ALTER TABLE ONLY public.dataset_funding ALTER COLUMN id SET DEFAULT nextval('public.dataset_funding_id_seq'::regclass);
ALTER TABLE ONLY public.runs ALTER COLUMN id SET DEFAULT nextval('public.runs_id_seq'::regclass);
ALTER TABLE ONLY public.tiltseries ALTER COLUMN id SET DEFAULT nextval('public.tiltseries_id_seq'::regclass);
ALTER TABLE ONLY public.tomogram_voxel_spacings ALTER COLUMN id SET DEFAULT nextval('public.tomogram_voxel_spacing_id_seq'::regclass);
ALTER TABLE ONLY public.tomograms ALTER COLUMN id SET DEFAULT nextval('public.tomograms_id_seq'::regclass);
ALTER TABLE ONLY public.annotation_authors
    ADD CONSTRAINT annotation_authors_annotation_id_name_key UNIQUE (annotation_id, name);
ALTER TABLE ONLY public.annotation_authors
    ADD CONSTRAINT annotation_authors_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.annotations
    ADD CONSTRAINT annotations_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.dataset_authors
    ADD CONSTRAINT dataset_authors_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.dataset_funding
    ADD CONSTRAINT dataset_funding_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.datasets
    ADD CONSTRAINT datasets_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.runs
    ADD CONSTRAINT runs_dataset_id_name_key UNIQUE (dataset_id, name);
ALTER TABLE ONLY public.runs
    ADD CONSTRAINT runs_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.tiltseries
    ADD CONSTRAINT tiltseries_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.tomogram_voxel_spacings
    ADD CONSTRAINT tomogram_voxel_spacing_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.tomograms
    ADD CONSTRAINT tomograms_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.annotation_authors
    ADD CONSTRAINT annotation_authors_annotation_id_fkey FOREIGN KEY (annotation_id) REFERENCES public.annotations(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
ALTER TABLE ONLY public.annotations
    ADD CONSTRAINT annotations_tomogram_voxel_spacing_id_fkey FOREIGN KEY (tomogram_voxel_spacing_id) REFERENCES public.tomogram_voxel_spacings(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
ALTER TABLE ONLY public.dataset_authors
    ADD CONSTRAINT dataset_authors_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES public.datasets(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
ALTER TABLE ONLY public.dataset_funding
    ADD CONSTRAINT dataset_funding_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES public.datasets(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
ALTER TABLE ONLY public.runs
    ADD CONSTRAINT runs_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES public.datasets(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
ALTER TABLE ONLY public.tiltseries
    ADD CONSTRAINT tiltseries_run_id_fkey FOREIGN KEY (run_id) REFERENCES public.runs(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
ALTER TABLE ONLY public.tomogram_voxel_spacings
    ADD CONSTRAINT tomogram_voxel_spacing_run_id_fkey FOREIGN KEY (run_id) REFERENCES public.runs(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
ALTER TABLE ONLY public.tomograms
    ADD CONSTRAINT tomograms_tomogram_voxel_spacing_id_fkey FOREIGN KEY (tomogram_voxel_spacing_id) REFERENCES public.tomogram_voxel_spacings(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
