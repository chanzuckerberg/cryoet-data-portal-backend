# cdp-meta



URI: metadata

Name: cdp-meta



## Classes

| Class | Description |
| --- | --- |
| [Annotation](Annotation.md) | Metadata describing an annotation. |
| [AnnotationConfidence](AnnotationConfidence.md) | Metadata describing the confidence of an annotation. |
| [AnnotationObject](AnnotationObject.md) | Metadata describing the object being annotated. |
| [AnnotationSourceFile](AnnotationSourceFile.md) | File and sourcing data for an annotation. Represents an entry in annotation.sources. |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[AnnotationOrientedPointFile](AnnotationOrientedPointFile.md) | File and sourcing data for an oriented point annotation. |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[AnnotationInstanceSegmentationFile](AnnotationInstanceSegmentationFile.md) | File and sourcing data for an instance segmentation annotation. |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[AnnotationPointFile](AnnotationPointFile.md) | File and sourcing data for a point annotation. |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[AnnotationSegmentationMaskFile](AnnotationSegmentationMaskFile.md) | File and sourcing data for a segmentation mask annotation. |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[AnnotationSemanticSegmentationMaskFile](AnnotationSemanticSegmentationMaskFile.md) | File and sourcing data for a semantic segmentation mask annotation. |
| [Annotator](Annotator.md) | Annotator of a scientific data entity. |
| [AnnotatoredEntity](AnnotatoredEntity.md) | An entity with associated annotation authors. |
| [Any](Any.md) | None |
| [Author](Author.md) | Author of a scientific data entity. |
| [AuthoredEntity](AuthoredEntity.md) | An entity with associated authors. |
| [Camera](Camera.md) | The camera used to collect the tilt series. |
| [CellComponent](CellComponent.md) | The cellular component from which the sample was derived. |
| [CellStrain](CellStrain.md) | The strain or cell line from which the sample was derived. |
| [CellType](CellType.md) | The cell type from which the sample was derived. |
| [CrossReferencedEntity](CrossReferencedEntity.md) | An entity with associated cross-references to other databases and publications. |
| [CrossReferences](CrossReferences.md) | A set of cross-references to other databases and publications. |
| [Dataset](Dataset.md) | High-level description of a cryoET dataset. |
| [DateStamp](DateStamp.md) | A set of dates at which a data item was deposited, published and last modified. |
| [DatestampedEntity](DatestampedEntity.md) | An entity with associated deposition, release and last modified dates. |
| [ExperimentalMetadata](ExperimentalMetadata.md) | Metadata describing sample and sample preparation methods used in a cryoET dataset. |
| [FundedEntity](FundedEntity.md) | An entity with associated funding sources. |
| [Funding](Funding.md) | A funding source for a scientific data entity (base for JSON and DB representation). |
| [Microscope](Microscope.md) | The microscope used to collect the tilt series. |
| [MicroscopeOpticalSetup](MicroscopeOpticalSetup.md) | The optical setup of the microscope used to collect the tilt series. |
| [Organism](Organism.md) | The species from which the sample was derived. |
| [PicturedEntity](PicturedEntity.md) | An entity with associated preview images. |
| [PicturePath](PicturePath.md) | A set of paths to representative images of a piece of data. |
| [TiltRange](TiltRange.md) | The range of tilt angles in the tilt series. |
| [TiltSeries](TiltSeries.md) | Metadata describing a tilt series. |
| [Tissue](Tissue.md) | The type of tissue from which the sample was derived. |
| [Tomogram](Tomogram.md) | Metadata describing a tomogram. |
| [TomogramOffset](TomogramOffset.md) | The offset of a tomogram in voxels in each dimension relative to the canonical tomogram. |
| [TomogramSize](TomogramSize.md) | The size of a tomogram in voxels in each dimension. |



## Slots

| Slot | Description |
| --- | --- |
| [acceleration_voltage](acceleration_voltage.md) | Electron Microscope Accelerator voltage in volts |
| [affiliation_address](affiliation_address.md) | The address of the author's affiliation |
| [affiliation_identifier](affiliation_identifier.md) | A Research Organization Registry (ROR) identifier |
| [affiliation_name](affiliation_name.md) | The name of the author's affiliation |
| [affine_transformation_matrix](affine_transformation_matrix.md) | The flip or rotation transformation of this author submitted tomogram is indi... |
| [aligned_tiltseries_binning](aligned_tiltseries_binning.md) | Binning factor of the aligned tilt series |
| [annotation_method](annotation_method.md) | Describe how the annotation is made (e |
| [annotation_method_type](annotation_method_type.md) | Classification of the annotation method based on supervision |
| [annotation_object](annotation_object.md) | Metadata describing the object being annotated |
| [annotation_publications](annotation_publications.md) | DOIs for publications that describe the dataset |
| [annotation_software](annotation_software.md) | Software used for generating this annotation |
| [authors](authors.md) | Author of a scientific data entity |
| [binning](binning.md) | The binning factor for a oriented point annotation file |
| [binning_from_frames](binning_from_frames.md) | Describes the binning factor from frames to tilt series file |
| [camera](camera.md) | The camera used to collect the tilt series |
| [cell_component](cell_component.md) | The cellular component from which the sample was derived |
| [cell_strain](cell_strain.md) | The strain or cell line from which the sample was derived |
| [cell_type](cell_type.md) | The cell type from which the sample was derived |
| [columns](columns.md) | The columns used in a point annotation file |
| [confidence](confidence.md) | Metadata describing the confidence of an annotation |
| [cross_references](cross_references.md) | A set of cross-references to other databases and publications |
| [ctf_corrected](ctf_corrected.md) | Whether this tomogram is CTF corrected |
| [data_acquisition_software](data_acquisition_software.md) | Software used to collect data |
| [dataset_citations](dataset_citations.md) | Comma-separated list of DOIs for publications citing the dataset |
| [dataset_description](dataset_description.md) | A short description of a CryoET dataset, similar to an abstract for a journal... |
| [dataset_identifier](dataset_identifier.md) | An identifier for a CryoET dataset, assigned by the Data Portal |
| [dataset_publications](dataset_publications.md) | Comma-separated list of DOIs for publications associated with the dataset |
| [dataset_title](dataset_title.md) | Title of a CryoET dataset |
| [dates](dates.md) | A set of dates at which a data item was deposited, published and last modifie... |
| [delimiter](delimiter.md) | The delimiter used in a oriented point annotation file |
| [deposition_date](deposition_date.md) | The date a data item was received by the cryoET data portal |
| [description](description.md) | A textual description of the annotation object, can be a longer description t... |
| [email](email.md) | The email address of the author |
| [energy_filter](energy_filter.md) | Energy filter setup used |
| [fiducial_alignment_status](fiducial_alignment_status.md) | Whether the tomographic alignment was computed based on fiducial markers |
| [file_format](file_format.md) | File format for this file |
| [files](files.md) | File and sourcing data for an annotation |
| [filter_value](filter_value.md) | The filter value for a oriented point annotation file |
| [frames_count](frames_count.md) | Number of frames associated with this tiltseries |
| [funding](funding.md) | A funding source for a scientific data entity (base for JSON and DB represent... |
| [funding_agency_name](funding_agency_name.md) | The name of the funding source |
| [glob_string](glob_string.md) | Glob string to match annotation files in the dataset |
| [grant_id](grant_id.md) | Grant identifier provided by the funding agency |
| [grid_preparation](grid_preparation.md) | Describes Cryo-ET grid preparation |
| [ground_truth_status](ground_truth_status.md) | Whether an annotation is considered ground truth, as determined by the annota... |
| [ground_truth_used](ground_truth_used.md) | Annotation filename used as ground truth for precision and recall |
| [id](id.md) | The UBERON identifier for the tissue |
| [image_corrector](image_corrector.md) | Image corrector setup |
| [is_corresponding](is_corresponding.md) | Whether the author is a corresponding author |
| [is_curator_recommended](is_curator_recommended.md) | This annotation is recommended by the curator to be preferred for this object... |
| [is_primary_annotator](is_primary_annotator.md) | Whether the author is a primary author |
| [is_visualization_default](is_visualization_default.md) | This annotation will be rendered in neuroglancer by default |
| [key_photos](key_photos.md) | A set of paths to representative images of a piece of data |
| [last_modified_date](last_modified_date.md) | The date a piece of data was last modified on the cryoET data portal |
| [manufacturer](manufacturer.md) | Name of the camera manufacturer |
| [mask_label](mask_label.md) | The mask label for a semantic segmentation mask annotation file |
| [max](max.md) | Maximal tilt angle in degrees |
| [microscope](microscope.md) | The microscope used to collect the tilt series |
| [microscope_additional_info](microscope_additional_info.md) | Other microscope optical setup information, in addition to energy filter, pha... |
| [microscope_optical_setup](microscope_optical_setup.md) | The optical setup of the microscope used to collect the tilt series |
| [min](min.md) | Minimal tilt angle in degrees |
| [model](model.md) | Camera model name |
| [name](name.md) | The full name of the author |
| [object_count](object_count.md) | Number of objects identified |
| [offset](offset.md) | The offset of a tomogram in voxels in each dimension relative to the canonica... |
| [ORCID](ORCID.md) | A unique, persistent identifier for researchers, provided by ORCID |
| [order](order.md) | The order of axes for a oriented point annotation file |
| [organism](organism.md) | The species from which the sample was derived |
| [other_setup](other_setup.md) | Describes other setup not covered by sample preparation or grid preparation t... |
| [phase_plate](phase_plate.md) | Phase plate configuration |
| [pixel_spacing](pixel_spacing.md) | Pixel spacing for the tilt series |
| [precision](precision.md) | Describe the confidence level of the annotation |
| [primary_author_status](primary_author_status.md) | Whether the author is a primary author |
| [processing](processing.md) | Describe additional processing used to derive the tomogram |
| [processing_software](processing_software.md) | Processing software used to derive the tomogram |
| [recall](recall.md) | Describe the confidence level of the annotation |
| [reconstruction_method](reconstruction_method.md) | Describe reconstruction method (Weighted back-projection, SART, SIRT) |
| [reconstruction_software](reconstruction_software.md) | Name of software used for reconstruction |
| [related_database_entries](related_database_entries.md) | Comma-separated list of related database entries for the dataset |
| [related_database_links](related_database_links.md) | Comma-separated list of related database links for the dataset |
| [release_date](release_date.md) | The date a data item was received by the cryoET data portal |
| [sample_preparation](sample_preparation.md) | Describes how the sample was prepared |
| [sample_type](sample_type.md) | Type of sample imaged in a CryoET study |
| [size](size.md) | The size of a tomogram in voxels in each dimension |
| [snapshot](snapshot.md) | Path to the dataset preview image relative to the dataset directory root |
| [spherical_aberration_constant](spherical_aberration_constant.md) | Spherical Aberration Constant of the objective lens in millimeters |
| [state](state.md) | Molecule state annotated (e |
| [taxonomy_id](taxonomy_id.md) | NCBI taxonomy identifier for the organism, e |
| [thumbnail](thumbnail.md) | Path to the thumbnail of preview image relative to the dataset directory root |
| [tilt_axis](tilt_axis.md) | Rotation angle in degrees |
| [tilt_range](tilt_range.md) | The range of tilt angles in the tilt series |
| [tilt_series_quality](tilt_series_quality.md) | Author assessment of tilt series quality within the dataset (1-5, 5 is best) |
| [tilt_step](tilt_step.md) | Tilt step in degrees |
| [tilting_scheme](tilting_scheme.md) | The order of stage tilting during acquisition of the data |
| [tissue](tissue.md) | The type of tissue from which the sample was derived |
| [tomogram_version](tomogram_version.md) | Version of tomogram using the same software and post-processing |
| [total_flux](total_flux.md) | Number of Electrons reaching the specimen in a square Angstrom area for the e... |
| [voxel_spacing](voxel_spacing.md) | Voxel spacing equal in all three axes in angstroms |
| [x](x.md) | Number of pixels in the 3D data fast axis |
| [y](y.md) | Number of pixels in the 3D data medium axis |
| [z](z.md) | Number of pixels in the 3D data slow axis |


## Enumerations

| Enumeration | Description |
| --- | --- |
| [AnnotationMethodTypeEnum](AnnotationMethodTypeEnum.md) | Describes how the annotations were generated |
| [AnnotationShapeEnum](AnnotationShapeEnum.md) | Annotation shape types available on the data portal |
| [FiducialAlignmentStatusEnum](FiducialAlignmentStatusEnum.md) | Fiducial Alignment method |
| [SampleTypeEnum](SampleTypeEnum.md) | Type of sample imaged in a CryoET study |
| [TomogramTypeEnum](TomogramTypeEnum.md) | Tomogram type |


## Types

| Type | Description |
| --- | --- |


## Subsets

| Subset | Description |
| --- | --- |
