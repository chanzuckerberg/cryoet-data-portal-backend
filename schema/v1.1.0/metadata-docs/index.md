# cdp-meta



URI: metadata

Name: cdp-meta



## Classes

| Class | Description |
| --- | --- |
| [Annotation](Annotation.md) | Metadata describing an annotation. |
| [AnnotationConfidence](AnnotationConfidence.md) | Metadata describing the confidence of an annotation. |
| [AnnotationMethodLinks](AnnotationMethodLinks.md) | A set of links to models, sourcecode, documentation, etc referenced by annotation the method |
| [AnnotationObject](AnnotationObject.md) | Metadata describing the object being annotated. |
| [AnnotationSourceFile](AnnotationSourceFile.md) | File and sourcing data for an annotation. Represents an entry in annotation.sources. |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[AnnotationOrientedPointFile](AnnotationOrientedPointFile.md) | File and sourcing data for an oriented point annotation. Annotation that identifies points along with orientation in the volume. |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[AnnotationInstanceSegmentationFile](AnnotationInstanceSegmentationFile.md) | File and sourcing data for an instance segmentation annotation. Annotation that identifies individual instances of object shapes. |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[AnnotationPointFile](AnnotationPointFile.md) | File and sourcing data for a point annotation. Annotation that identifies points in the volume. |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[AnnotationSegmentationMaskFile](AnnotationSegmentationMaskFile.md) | File and sourcing data for a segmentation mask annotation. Annotation that identifies an object. |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[AnnotationSemanticSegmentationMaskFile](AnnotationSemanticSegmentationMaskFile.md) | File and sourcing data for a semantic segmentation mask annotation. Annotation that identifies classes of objects. |
| [Any](Any.md) | A placeholder for any type of data. |
| [Author](Author.md) | Author of a scientific data entity. |
| [AuthoredEntity](AuthoredEntity.md) | An entity with associated authors. |
| [CameraDetails](CameraDetails.md) | The camera used to collect the tilt series. |
| [CellComponent](CellComponent.md) | The cellular component from which the sample was derived. |
| [CellStrain](CellStrain.md) | The strain or cell line from which the sample was derived. |
| [CellType](CellType.md) | The cell type from which the sample was derived. |
| [CrossReferencedEntity](CrossReferencedEntity.md) | An entity with associated cross-references to other databases and publications. |
| [CrossReferences](CrossReferences.md) | A set of cross-references to other databases and publications. |
| [Dataset](Dataset.md) | High-level description of a cryoET dataset. |
| [DateStamp](DateStamp.md) | A set of dates at which a data item was deposited, published and last modified. |
| [DatestampedEntity](DatestampedEntity.md) | An entity with associated deposition, release and last modified dates. |
| [Deposition](Deposition.md) | Metadata describing a deposition. |
| [ExperimentMetadata](ExperimentMetadata.md) | Metadata describing sample and sample preparation methods used in a cryoET dataset. |
| [FundedEntity](FundedEntity.md) | An entity with associated funding sources. |
| [FundingDetails](FundingDetails.md) | A funding source for a scientific data entity (base for JSON and DB representation). |
| [MicroscopeDetails](MicroscopeDetails.md) | The microscope used to collect the tilt series. |
| [MicroscopeOpticalSetup](MicroscopeOpticalSetup.md) | The optical setup of the microscope used to collect the tilt series. |
| [OrganismDetails](OrganismDetails.md) | The species from which the sample was derived. |
| [PicturedEntity](PicturedEntity.md) | An entity with associated preview images. |
| [PicturePath](PicturePath.md) | A set of paths to representative images of a piece of data. |
| [TiltRange](TiltRange.md) | The range of tilt angles in the tilt series. |
| [TiltSeries](TiltSeries.md) | Metadata describing a tilt series. |
| [TissueDetails](TissueDetails.md) | The type of tissue from which the sample was derived. |
| [Tomogram](Tomogram.md) | Metadata describing a tomogram. |
| [TomogramOffset](TomogramOffset.md) | The offset of a tomogram in voxels in each dimension relative to the canonical tomogram. |
| [TomogramSize](TomogramSize.md) | The size of a tomogram in voxels in each dimension. |



## Slots

| Slot | Description |
| --- | --- |
| [acceleration_voltage](acceleration_voltage.md) | Electron Microscope Accelerator voltage in volts |
| [acquire_mode](acquire_mode.md) | Camera acquisition mode |
| [additional_info](additional_info.md) | Other microscope optical setup information, in addition to energy filter, pha... |
| [affiliation_address](affiliation_address.md) | The address of the author's affiliation |
| [affiliation_identifier](affiliation_identifier.md) | A Research Organization Registry (ROR) identifier |
| [affiliation_name](affiliation_name.md) | The name of the author's affiliation |
| [affine_transformation_matrix](affine_transformation_matrix.md) | The flip or rotation transformation of this author submitted tomogram is indi... |
| [align_software](align_software.md) | Software used for alignment |
| [aligned_tiltseries_binning](aligned_tiltseries_binning.md) | Binning factor of the aligned tilt series |
| [annotation_method](annotation_method.md) | Describe how the annotation is made (e |
| [annotation_object](annotation_object.md) | Metadata describing the object being annotated |
| [annotation_publications](annotation_publications.md) | List of publication IDs (EMPIAR, EMDB, DOI) that describe this annotation met... |
| [annotation_software](annotation_software.md) | Software used for generating this annotation |
| [authors](authors.md) | Author of a scientific data entity |
| [binning](binning.md) | The binning factor for a point / oriented point / instance segmentation annot... |
| [binning_from_frames](binning_from_frames.md) | Describes the binning factor from frames to tilt series file |
| [camera](camera.md) | The camera used to collect the tilt series |
| [cell_component](cell_component.md) | The cellular component from which the sample was derived |
| [cell_strain](cell_strain.md) | The strain or cell line from which the sample was derived |
| [cell_type](cell_type.md) | The cell type from which the sample was derived |
| [columns](columns.md) | The columns used in a point annotation file |
| [confidence](confidence.md) | Metadata describing the confidence of an annotation |
| [corresponding_author_status](corresponding_author_status.md) | Whether the author is a corresponding author |
| [cross_references](cross_references.md) | A set of cross-references to other databases and publications |
| [ctf_corrected](ctf_corrected.md) | Whether this tomogram is CTF corrected |
| [data_acquisition_software](data_acquisition_software.md) | Software used to collect data |
| [dataset_citations](dataset_citations.md) | Comma-separated list of DOIs for publications citing the dataset |
| [dataset_description](dataset_description.md) | A short description of a CryoET dataset, similar to an abstract for a journal... |
| [dataset_identifier](dataset_identifier.md) | An identifier for a CryoET dataset, assigned by the Data Portal |
| [dataset_title](dataset_title.md) | Title of a CryoET dataset |
| [dates](dates.md) | A set of dates at which a data item was deposited, published and last modifie... |
| [delimiter](delimiter.md) | The delimiter used in a point annotation file |
| [deposition_date](deposition_date.md) | The date a data item was received by the cryoET data portal |
| [deposition_description](deposition_description.md) | A short description of the deposition, similar to an abstract for a journal a... |
| [deposition_identifier](deposition_identifier.md) | An identifier for a CryoET deposition, assigned by the Data Portal |
| [deposition_title](deposition_title.md) | Title of a CryoET deposition |
| [deposition_types](deposition_types.md) | Type of data in the deposition (e |
| [description](description.md) | A textual description of the annotation object, can be a longer description t... |
| [email](email.md) | The email address of the author |
| [energy_filter](energy_filter.md) | Energy filter setup used |
| [fiducial_alignment_status](fiducial_alignment_status.md) | Whether the tomographic alignment was computed based on fiducial markers |
| [file_format](file_format.md) | File format for this file |
| [files](files.md) | File and sourcing data for an annotation |
| [filter_value](filter_value.md) | The filter value for an oriented point / instance segmentation annotation fil... |
| [frames_count](frames_count.md) | Number of frames associated with this tiltseries |
| [funding](funding.md) | A funding source for a scientific data entity (base for JSON and DB represent... |
| [funding_agency_name](funding_agency_name.md) | The name of the funding source |
| [glob_string](glob_string.md) | Glob string to match annotation files in the dataset |
| [glob_strings](glob_strings.md) | Glob strings to match annotation files in the dataset |
| [grant_id](grant_id.md) | Grant identifier provided by the funding agency |
| [grid_preparation](grid_preparation.md) | Describes Cryo-ET grid preparation |
| [ground_truth_status](ground_truth_status.md) | Whether an annotation is considered ground truth, as determined by the annota... |
| [ground_truth_used](ground_truth_used.md) | Annotation filename used as ground truth for precision and recall |
| [id](id.md) | The UBERON identifier for the tissue |
| [image_corrector](image_corrector.md) | Image corrector setup |
| [is_aligned](is_aligned.md) | Whether this tilt series is aligned |
| [is_curator_recommended](is_curator_recommended.md) | This annotation is recommended by the curator to be preferred for this object... |
| [is_visualization_default](is_visualization_default.md) | This annotation will be rendered in neuroglancer by default |
| [key_photos](key_photos.md) | A set of paths to representative images of a piece of data |
| [last_modified_date](last_modified_date.md) | The date a piece of data was last modified on the cryoET data portal |
| [link](link.md) | URL to the resource |
| [link_type](link_type.md) | Type of link (e |
| [manufacturer](manufacturer.md) | Name of the camera manufacturer |
| [mask_label](mask_label.md) | The mask label for a semantic segmentation mask annotation file |
| [max](max.md) | Maximal tilt angle in degrees |
| [method_type](method_type.md) | Classification of the annotation method based on supervision |
| [microscope](microscope.md) | The microscope used to collect the tilt series |
| [microscope_optical_setup](microscope_optical_setup.md) | The optical setup of the microscope used to collect the tilt series |
| [min](min.md) | Minimal tilt angle in degrees |
| [model](model.md) | Camera model name |
| [name](name.md) | The full name of the author |
| [object_count](object_count.md) | Number of objects identified |
| [offset](offset.md) | The offset of a tomogram in voxels in each dimension relative to the canonica... |
| [ORCID](ORCID.md) | The ORCID identifier for the author |
| [order](order.md) | The order of axes for an oriented point / instance segmentation annotation fi... |
| [organism](organism.md) | The species from which the sample was derived |
| [other_setup](other_setup.md) | Describes other setup not covered by sample preparation or grid preparation t... |
| [phase_plate](phase_plate.md) | Phase plate configuration |
| [pixel_spacing](pixel_spacing.md) | Pixel spacing for the tilt series |
| [precision](precision.md) | Describe the confidence level of the annotation |
| [primary_author_status](primary_author_status.md) | Whether the author is a primary author |
| [processing](processing.md) | Describe additional processing used to derive the tomogram |
| [processing_software](processing_software.md) | Processing software used to derive the tomogram |
| [publications](publications.md) | Comma-separated list of DOIs for publications associated with the dataset |
| [recall](recall.md) | Describe the confidence level of the annotation |
| [reconstruction_method](reconstruction_method.md) | Describe reconstruction method (WBP, SART, SIRT) |
| [reconstruction_software](reconstruction_software.md) | Name of software used for reconstruction |
| [related_database_entries](related_database_entries.md) | Comma-separated list of related database entries for the dataset |
| [related_database_links](related_database_links.md) | Comma-separated list of related database links for the dataset |
| [related_empiar_entry](related_empiar_entry.md) | If a tilt series is deposited into EMPIAR, enter the EMPIAR dataset identifie... |
| [release_date](release_date.md) | The date a data item was received by the cryoET data portal |
| [sample_preparation](sample_preparation.md) | Describes how the sample was prepared |
| [sample_type](sample_type.md) | Type of sample imaged in a CryoET study |
| [size](size.md) | The size of a tomogram in voxels in each dimension |
| [snapshot](snapshot.md) | Path to the dataset preview image relative to the dataset directory root |
| [spherical_aberration_constant](spherical_aberration_constant.md) | Spherical Aberration Constant of the objective lens in millimeters |
| [state](state.md) | Molecule state annotated (e |
| [taxonomy_id](taxonomy_id.md) | NCBI taxonomy identifier for the organism, e |
| [thumbnail](thumbnail.md) | Path to the thumbnail of preview image relative to the dataset directory root |
| [tilt_alignment_software](tilt_alignment_software.md) | Software used for tilt alignment |
| [tilt_axis](tilt_axis.md) | Rotation angle in degrees |
| [tilt_range](tilt_range.md) | The range of tilt angles in the tilt series |
| [tilt_series_quality](tilt_series_quality.md) | Author assessment of tilt series quality within the dataset (1-5, 5 is best) |
| [tilt_step](tilt_step.md) | Tilt step in degrees |
| [tilting_scheme](tilting_scheme.md) | The order of stage tilting during acquisition of the data |
| [tissue](tissue.md) | The type of tissue from which the sample was derived |
| [tomogram_version](tomogram_version.md) | Version of tomogram |
| [total_flux](total_flux.md) | Number of Electrons reaching the specimen in a square Angstrom area for the e... |
| [version](version.md) | Version of annotation |
| [voxel_spacing](voxel_spacing.md) | Voxel spacing equal in all three axes in angstroms |
| [x](x.md) | Number of pixels in the 3D data fast axis |
| [y](y.md) | Number of pixels in the 3D data medium axis |
| [z](z.md) | Number of pixels in the 3D data slow axis |


## Enumerations

| Enumeration | Description |
| --- | --- |
| [AnnotationMethodLinkTypeEnum](AnnotationMethodLinkTypeEnum.md) | Describes the type of link associated to the annotation method |
| [AnnotationMethodTypeEnum](AnnotationMethodTypeEnum.md) | Describes how the annotations were generated |
| [DepositionTypesEnum](DepositionTypesEnum.md) | Types of data a deposition has |
| [FiducialAlignmentStatusEnum](FiducialAlignmentStatusEnum.md) | Fiducial Alignment method |
| [SampleTypeEnum](SampleTypeEnum.md) | Type of sample imaged in a CryoET study |
| [TiltseriesCameraAcquireModeEnum](TiltseriesCameraAcquireModeEnum.md) | Camera acquisition mode |
| [TiltseriesMicroscopeManufacturerEnum](TiltseriesMicroscopeManufacturerEnum.md) | Microscope manufacturer |
| [TomogramProcessingEnum](TomogramProcessingEnum.md) | Tomogram processing method |
| [TomogramTypeEnum](TomogramTypeEnum.md) | Tomogram type |
| [TomogromReconstructionMethodEnum](TomogromReconstructionMethodEnum.md) | Tomogram reconstruction method |


## Types

| Type | Description |
| --- | --- |
| [Boolean](Boolean.md) | A binary (true or false) value |
| [BTOID](BTOID.md) | A BRENDA Tissue Ontology identifier |
| [CLID](CLID.md) | A Cell Ontology identifier |
| [Curie](Curie.md) | a compact URI |
| [Date](Date.md) | a date (year, month and day) in an idealized calendar |
| [DateOrDatetime](DateOrDatetime.md) | Either a date or a datetime |
| [Datetime](Datetime.md) | The combination of a date and time |
| [Decimal](Decimal.md) | A real number with arbitrary precision that conforms to the xsd:decimal speci... |
| [DOI](DOI.md) | A Digital Object Identifier |
| [DOILIST](DOILIST.md) | A list of Digital Object Identifiers |
| [Double](Double.md) | A real number that conforms to the xsd:double specification |
| [EMDBID](EMDBID.md) | An Electron Microscopy Data Bank identifier |
| [EMPIAREMDBDOIPDBLIST](EMPIAREMDBDOIPDBLIST.md) | A list of EMPIAR, EMDB, DOI, and PDB identifiers |
| [EMPIAREMDBPDBLIST](EMPIAREMDBPDBLIST.md) | A list of EMPIAR, EMDB, and PDB identifiers |
| [EMPIARID](EMPIARID.md) | An Electron Microscopy Public Image Archive identifier |
| [Float](Float.md) | A real number that conforms to the xsd:float specification |
| [FloatFormattedString](FloatFormattedString.md) | A formatted string that represents a floating point number |
| [GOID](GOID.md) | A Gene Ontology identifier |
| [Integer](Integer.md) | An integer |
| [IntegerFormattedString](IntegerFormattedString.md) | A formatted string that represents an integer |
| [Jsonpath](Jsonpath.md) | A string encoding a JSON Path |
| [Jsonpointer](Jsonpointer.md) | A string encoding a JSON Pointer |
| [Ncname](Ncname.md) | Prefix part of CURIE |
| [Nodeidentifier](Nodeidentifier.md) | A URI, CURIE or BNODE that represents a node in a model |
| [Objectidentifier](Objectidentifier.md) | A URI or CURIE that represents an object in the model |
| [ONTOLOGYID](ONTOLOGYID.md) | An ontology identifier |
| [ORCID](ORCID.md) | A unique, persistent identifier for researchers, provided by ORCID |
| [PDBID](PDBID.md) | A Protein Data Bank identifier |
| [Sparqlpath](Sparqlpath.md) | A string encoding a SPARQL Property Path |
| [String](String.md) | A character string |
| [StringFormattedString](StringFormattedString.md) | A formatted string (variable) that represents a string |
| [Time](Time.md) | A time object represents a (local) time of day, independent of any particular... |
| [Uri](Uri.md) | a complete URI |
| [Uriorcurie](Uriorcurie.md) | a URI or a CURIE |
| [URLorS3URI](URLorS3URI.md) | A URL or S3 URI |
| [VersionString](VersionString.md) | A version number (only major, minor versions) |


## Subsets

| Subset | Description |
| --- | --- |
