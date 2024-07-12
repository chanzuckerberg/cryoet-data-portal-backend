from __future__ import annotations
from datetime import datetime, date
from enum import Enum

from decimal import Decimal
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel as BaseModel, ConfigDict, Field, field_validator
import re
import sys

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


metamodel_version = "None"
version = "1.1.0"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
        arbitrary_types_allowed=True,
        use_enum_values=True,
    )

    pass


class SampleTypeEnum(str, Enum):
    """
    Type of sample imaged in a CryoET study.
    """

    # Tomographic data of whole cells or cell sections.
    cell = "cell"
    # Tomographic data of tissue sections.
    tissue = "tissue"
    # Tomographic data of sections through multicellular organisms.
    organism = "organism"
    # Tomographic data of purified organelles.
    organelle = "organelle"
    # Tomographic data of purified viruses or VLPs.
    virus = "virus"
    # Tomographic data of in vitro reconstituted systems or mixtures of proteins.
    in_vitro = "in_vitro"
    # Simulated tomographic data.
    in_silico = "in_silico"
    # Other type of sample.
    other = "other"


class FiducialAlignmentStatusEnum(str, Enum):
    """
    Fiducial Alignment method
    """

    # Alignment computed based on fiducial markers
    FIDUCIAL = "FIDUCIAL"
    # Alignment computed without fiducial markers
    NON_FIDUCIAL = "NON_FIDUCIAL"


class TomogramTypeEnum(str, Enum):
    """
    Tomogram type
    """

    # Canonical tomogram (basis geometry for all annotations)
    CANONICAL = "CANONICAL"


class AnnotationMethodTypeEnum(str, Enum):
    """
    Describes how the annotations were generated.
    """

    # Annotations were generated manually.
    manual = "manual"
    # Annotations were generated semi-automatically.
    automated = "automated"
    # Annotations were generated automatically.
    hybrid = "hybrid"


class PicturePath(ConfiguredBaseModel):
    """
    A set of paths to representative images of a piece of data.
    """

    snapshot: Any = Field(..., description="""A placeholder for any type of data.""")
    thumbnail: Any = Field(..., description="""A placeholder for any type of data.""")


class Author(ConfiguredBaseModel):
    """
    Author of a scientific data entity.
    """

    name: str = Field(..., description="""The full name of the author.""")
    email: Optional[str] = Field(None, description="""The email address of the author.""")
    affiliation_name: Optional[str] = Field(None, description="""The name of the author's affiliation.""")
    affiliation_address: Optional[str] = Field(None, description="""The address of the author's affiliation.""")
    affiliation_identifier: Optional[str] = Field(
        None, description="""A Research Organization Registry (ROR) identifier."""
    )
    corresponding_author_status: Optional[bool] = Field(
        False, description="""Whether the author is a corresponding author."""
    )
    primary_author_status: Optional[bool] = Field(False, description="""Whether the author is a primary author.""")
    ORCID: Optional[str] = Field(
        None, description="""A unique, persistent identifier for researchers, provided by ORCID."""
    )

    @field_validator("affiliation_identifier")
    def pattern_affiliation_identifier(cls, v):
        pattern = re.compile(r"^0[a-hj-km-np-tv-z|0-9]{6}[0-9]{2}$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid affiliation_identifier format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid affiliation_identifier format: {v}")
        return v

    @field_validator("ORCID")
    def pattern_ORCID(cls, v):
        pattern = re.compile(r"[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid ORCID format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid ORCID format: {v}")
        return v


class FundingDetails(ConfiguredBaseModel):
    """
    A funding source for a scientific data entity (base for JSON and DB representation).
    """

    funding_agency_name: Optional[str] = Field(None, description="""The name of the funding source.""")
    grant_id: Optional[str] = Field(None, description="""Grant identifier provided by the funding agency""")


class DateStamp(ConfiguredBaseModel):
    """
    A set of dates at which a data item was deposited, published and last modified.
    """

    deposition_date: date = Field(..., description="""The date a data item was received by the cryoET data portal.""")
    release_date: date = Field(..., description="""The date a data item was received by the cryoET data portal.""")
    last_modified_date: date = Field(
        ..., description="""The date a piece of data was last modified on the cryoET data portal."""
    )


class DatestampedEntity(ConfiguredBaseModel):
    """
    An entity with associated deposition, release and last modified dates.
    """

    dates: DateStamp = Field(
        ..., description="""A set of dates at which a data item was deposited, published and last modified."""
    )


class AuthoredEntity(ConfiguredBaseModel):
    """
    An entity with associated authors.
    """

    authors: List[Author] = Field(default_factory=list, description="""Author of a scientific data entity.""")


class FundedEntity(ConfiguredBaseModel):
    """
    An entity with associated funding sources.
    """

    funding: Optional[List[FundingDetails]] = Field(
        default_factory=list,
        description="""A funding source for a scientific data entity (base for JSON and DB representation).""",
    )


class CrossReferencedEntity(ConfiguredBaseModel):
    """
    An entity with associated cross-references to other databases and publications.
    """

    cross_references: Optional[CrossReferences] = Field(
        None, description="""A set of cross-references to other databases and publications."""
    )


class PicturedEntity(ConfiguredBaseModel):
    """
    An entity with associated preview images.
    """

    key_photos: PicturePath = Field(..., description="""A set of paths to representative images of a piece of data.""")


class OrganismDetails(ConfiguredBaseModel):
    """
    The species from which the sample was derived.
    """

    name: str = Field(
        ...,
        description="""Name of the organism from which a biological sample used in a CryoET study is derived from, e.g. homo sapiens.""",
    )
    taxonomy_id: Optional[int] = Field(
        None, description="""NCBI taxonomy identifier for the organism, e.g. 9606""", ge=1
    )


class TissueDetails(ConfiguredBaseModel):
    """
    The type of tissue from which the sample was derived.
    """

    name: str = Field(
        ..., description="""Name of the tissue from which a biological sample used in a CryoET study is derived from."""
    )
    id: Optional[str] = Field(None, description="""The UBERON identifier for the tissue.""")


class CellType(ConfiguredBaseModel):
    """
    The cell type from which the sample was derived.
    """

    name: str = Field(
        ...,
        description="""Name of the cell type from which a biological sample used in a CryoET study is derived from.""",
    )
    id: Optional[str] = Field(None, description="""Cell Ontology identifier for the cell type""")


class CellStrain(ConfiguredBaseModel):
    """
    The strain or cell line from which the sample was derived.
    """

    name: str = Field(..., description="""Cell line or strain for the sample.""")
    id: Optional[str] = Field(None, description="""Link to more information about the cell strain.""")


class CellComponent(ConfiguredBaseModel):
    """
    The cellular component from which the sample was derived.
    """

    name: str = Field(..., description="""Name of the cellular component.""")
    id: Optional[str] = Field(None, description="""The GO identifier for the cellular component.""")


class ExperimentalMetadata(ConfiguredBaseModel):
    """
    Metadata describing sample and sample preparation methods used in a cryoET dataset.
    """

    sample_type: SampleTypeEnum = Field(..., description="""Type of sample imaged in a CryoET study.""")
    sample_preparation: Optional[str] = Field(None, description="""Describes how the sample was prepared.""")
    grid_preparation: Optional[str] = Field(None, description="""Describes Cryo-ET grid preparation.""")
    other_setup: Optional[str] = Field(
        None,
        description="""Describes other setup not covered by sample preparation or grid preparation that may make this dataset unique in the same publication.""",
    )
    organism: Optional[OrganismDetails] = Field(None, description="""The species from which the sample was derived.""")
    tissue: Optional[TissueDetails] = Field(
        None, description="""The type of tissue from which the sample was derived."""
    )
    cell_type: Optional[CellType] = Field(None, description="""The cell type from which the sample was derived.""")
    cell_strain: Optional[CellStrain] = Field(
        None, description="""The strain or cell line from which the sample was derived."""
    )
    cell_component: Optional[CellComponent] = Field(
        None, description="""The cellular component from which the sample was derived."""
    )


class Dataset(ExperimentalMetadata, CrossReferencedEntity, FundedEntity, AuthoredEntity, DatestampedEntity):
    """
    High-level description of a cryoET dataset.
    """

    dataset_identifier: int = Field(
        ...,
        description="""An identifier for a CryoET dataset, assigned by the Data Portal. Used to identify the dataset as the directory name in data tree.""",
    )
    dataset_title: str = Field(..., description="""Title of a CryoET dataset.""")
    dataset_description: str = Field(
        ...,
        description="""A short description of a CryoET dataset, similar to an abstract for a journal article or dataset.""",
    )
    dates: DateStamp = Field(
        ..., description="""A set of dates at which a data item was deposited, published and last modified."""
    )
    authors: List[Author] = Field(default_factory=list, description="""Author of a scientific data entity.""")
    funding: Optional[List[FundingDetails]] = Field(
        default_factory=list,
        description="""A funding source for a scientific data entity (base for JSON and DB representation).""",
    )
    cross_references: Optional[CrossReferences] = Field(
        None, description="""A set of cross-references to other databases and publications."""
    )
    sample_type: SampleTypeEnum = Field(..., description="""Type of sample imaged in a CryoET study.""")
    sample_preparation: Optional[str] = Field(None, description="""Describes how the sample was prepared.""")
    grid_preparation: Optional[str] = Field(None, description="""Describes Cryo-ET grid preparation.""")
    other_setup: Optional[str] = Field(
        None,
        description="""Describes other setup not covered by sample preparation or grid preparation that may make this dataset unique in the same publication.""",
    )
    organism: Optional[OrganismDetails] = Field(None, description="""The species from which the sample was derived.""")
    tissue: Optional[TissueDetails] = Field(
        None, description="""The type of tissue from which the sample was derived."""
    )
    cell_type: Optional[CellType] = Field(None, description="""The cell type from which the sample was derived.""")
    cell_strain: Optional[CellStrain] = Field(
        None, description="""The strain or cell line from which the sample was derived."""
    )
    cell_component: Optional[CellComponent] = Field(
        None, description="""The cellular component from which the sample was derived."""
    )


class CameraDetails(ConfiguredBaseModel):
    """
    The camera used to collect the tilt series.
    """

    acquire_mode: Optional[str] = Field(None, description="""Camera acquisition mode""")
    manufacturer: str = Field(..., description="""Name of the camera manufacturer""")
    model: str = Field(..., description="""Camera model name""")


class MicroscopeDetails(ConfiguredBaseModel):
    """
    The microscope used to collect the tilt series.
    """

    manufacturer: str = Field(..., description="""Name of the microscope manufacturer""")
    model: str = Field(..., description="""Microscope model name""")


class MicroscopeOpticalSetup(ConfiguredBaseModel):
    """
    The optical setup of the microscope used to collect the tilt series.
    """

    energy_filter: str = Field(..., description="""Energy filter setup used""")
    phase_plate: Optional[str] = Field(None, description="""Phase plate configuration""")
    image_corrector: Optional[str] = Field(None, description="""Image corrector setup""")


class TiltRange(ConfiguredBaseModel):
    """
    The range of tilt angles in the tilt series.
    """

    min: float = Field(..., description="""Minimal tilt angle in degrees""")
    max: float = Field(..., description="""Maximal tilt angle in degrees""")


class TiltSeries(ConfiguredBaseModel):
    """
    Metadata describing a tilt series.
    """

    acceleration_voltage: int = Field(..., description="""Electron Microscope Accelerator voltage in volts""", ge=0)
    aligned_tiltseries_binning: Optional[int] = Field(1, description="""Binning factor of the aligned tilt series""")
    binning_from_frames: Optional[float] = Field(
        None, description="""Describes the binning factor from frames to tilt series file"""
    )
    camera: CameraDetails = Field(..., description="""The camera used to collect the tilt series.""")
    data_acquisition_software: str = Field(..., description="""Software used to collect data""")
    frames_count: Optional[int] = Field(None, description="""Number of frames associated with this tiltseries""")
    is_aligned: bool = Field(..., description="""Whether this tilt series is aligned""")
    microscope: MicroscopeDetails = Field(..., description="""The microscope used to collect the tilt series.""")
    microscope_additional_info: Optional[str] = Field(
        None,
        description="""Other microscope optical setup information, in addition to energy filter, phase plate and image corrector""",
    )
    microscope_optical_setup: MicroscopeOpticalSetup = Field(
        ..., description="""The optical setup of the microscope used to collect the tilt series."""
    )
    related_empiar_entry: Optional[str] = Field(
        None, description="""If a tilt series is deposited into EMPIAR, enter the EMPIAR dataset identifier"""
    )
    spherical_aberration_constant: float = Field(
        ..., description="""Spherical Aberration Constant of the objective lens in millimeters"""
    )
    tilt_alignment_software: Optional[str] = Field(None, description="""Software used for tilt alignment""")
    tilt_axis: float = Field(..., description="""Rotation angle in degrees""")
    tilt_range: TiltRange = Field(..., description="""The range of tilt angles in the tilt series.""")
    tilt_series_quality: int = Field(
        ..., description="""Author assessment of tilt series quality within the dataset (1-5, 5 is best)""", ge=1, le=5
    )
    tilt_step: float = Field(..., description="""Tilt step in degrees""")
    tilting_scheme: str = Field(..., description="""The order of stage tilting during acquisition of the data""")
    total_flux: float = Field(
        ...,
        description="""Number of Electrons reaching the specimen in a square Angstrom area for the entire tilt series""",
    )
    pixel_spacing: float = Field(..., description="""Pixel spacing for the tilt series""", ge=0)


class TomogramSize(ConfiguredBaseModel):
    """
    The size of a tomogram in voxels in each dimension.
    """

    x: int = Field(..., description="""Number of pixels in the 3D data fast axis""")
    y: int = Field(..., description="""Number of pixels in the 3D data medium axis""")
    z: int = Field(
        ...,
        description="""Number of pixels in the 3D data slow axis.  This is the image projection direction at zero stage tilt""",
    )


class TomogramOffset(ConfiguredBaseModel):
    """
    The offset of a tomogram in voxels in each dimension relative to the canonical tomogram.
    """

    x: int = Field(..., description="""x offset data relative to the canonical tomogram in pixels""")
    y: int = Field(..., description="""y offset data relative to the canonical tomogram in pixels""")
    z: int = Field(..., description="""z offset data relative to the canonical tomogram in pixels""")


class Tomogram(AuthoredEntity):
    """
    Metadata describing a tomogram.
    """

    voxel_spacing: float = Field(..., description="""Voxel spacing equal in all three axes in angstroms""")
    fiducial_alignment_status: FiducialAlignmentStatusEnum = Field(
        ..., description="""Whether the tomographic alignment was computed based on fiducial markers."""
    )
    ctf_corrected: Optional[bool] = Field(None, description="""Whether this tomogram is CTF corrected""")
    align_software: Optional[str] = Field(None, description="""Software used for alignment""")
    reconstruction_method: str = Field(
        ..., description="""Describe reconstruction method (Weighted back-projection, SART, SIRT)"""
    )
    reconstruction_software: str = Field(..., description="""Name of software used for reconstruction""")
    processing: str = Field(..., description="""Describe additional processing used to derive the tomogram""")
    processing_software: Optional[str] = Field(None, description="""Processing software used to derive the tomogram""")
    tomogram_version: float = Field(..., description="""Version of tomogram""")
    affine_transformation_matrix: Optional[Any] = Field(None, description="""A placeholder for any type of data.""")
    size: Optional[TomogramSize] = Field(None, description="""The size of a tomogram in voxels in each dimension.""")
    offset: TomogramOffset = Field(
        ..., description="""The offset of a tomogram in voxels in each dimension relative to the canonical tomogram."""
    )
    authors: List[Author] = Field(default_factory=list, description="""Author of a scientific data entity.""")


class AnnotationConfidence(ConfiguredBaseModel):
    """
    Metadata describing the confidence of an annotation.
    """

    precision: Optional[float] = Field(
        None,
        description="""Describe the confidence level of the annotation. Precision is defined as the % of annotation objects being true positive""",
        ge=0,
        le=100,
    )
    recall: Optional[float] = Field(
        None,
        description="""Describe the confidence level of the annotation. Recall is defined as the % of true positives being annotated correctly""",
        ge=0,
        le=100,
    )
    ground_truth_used: Optional[str] = Field(
        None, description="""Annotation filename used as ground truth for precision and recall"""
    )


class AnnotationObject(ConfiguredBaseModel):
    """
    Metadata describing the object being annotated.
    """

    id: str = Field(..., description="""Gene Ontology Cellular Component identifier for the annotation object""")
    name: str = Field(
        ...,
        description="""Name of the object being annotated (e.g. ribosome, nuclear pore complex, actin filament, membrane)""",
    )
    description: Optional[str] = Field(
        None,
        description="""A textual description of the annotation object, can be a longer description to include additional information not covered by the Annotation object name and state.""",
    )
    state: Optional[str] = Field(None, description="""Molecule state annotated (e.g. open, closed)""")


class AnnotationSourceFile(ConfiguredBaseModel):
    """
    File and sourcing data for an annotation. Represents an entry in annotation.sources.
    """

    file_format: str = Field(..., description="""File format for this file""")
    glob_string: str = Field(..., description="""Glob string to match annotation files in the dataset.""")
    is_visualization_default: Optional[bool] = Field(
        False, description="""This annotation will be rendered in neuroglancer by default."""
    )


class AnnotationOrientedPointFile(AnnotationSourceFile):
    """
    File and sourcing data for an oriented point annotation. Annotation that identifies points along with orientation in the volume.
    """

    binning: Optional[int] = Field(
        1, description="""The binning factor for a point / oriented point / instance segmentation annotation file."""
    )
    filter_value: Optional[str] = Field(
        None, description="""The filter value for an oriented point / instance segmentation annotation file."""
    )
    order: Optional[str] = Field(
        "xyz", description="""The order of axes for an oriented point / instance segmentation annotation file."""
    )
    file_format: str = Field(..., description="""File format for this file""")
    glob_string: str = Field(..., description="""Glob string to match annotation files in the dataset.""")
    is_visualization_default: Optional[bool] = Field(
        False, description="""This annotation will be rendered in neuroglancer by default."""
    )


class AnnotationInstanceSegmentationFile(AnnotationOrientedPointFile):
    """
    File and sourcing data for an instance segmentation annotation. Annotation that identifies individual instances of object shapes.
    """

    binning: Optional[int] = Field(
        1, description="""The binning factor for a point / oriented point / instance segmentation annotation file."""
    )
    filter_value: Optional[str] = Field(
        None, description="""The filter value for an oriented point / instance segmentation annotation file."""
    )
    order: Optional[str] = Field(
        "xyz", description="""The order of axes for an oriented point / instance segmentation annotation file."""
    )
    file_format: str = Field(..., description="""File format for this file""")
    glob_string: str = Field(..., description="""Glob string to match annotation files in the dataset.""")
    is_visualization_default: Optional[bool] = Field(
        False, description="""This annotation will be rendered in neuroglancer by default."""
    )


class AnnotationPointFile(AnnotationSourceFile):
    """
    File and sourcing data for a point annotation. Annotation that identifies points in the volume.
    """

    binning: Optional[int] = Field(
        1, description="""The binning factor for a point / oriented point / instance segmentation annotation file."""
    )
    columns: Optional[str] = Field("xyz", description="""The columns used in a point annotation file.""")
    delimiter: Optional[str] = Field(",", description="""The delimiter used in a point annotation file.""")
    file_format: str = Field(..., description="""File format for this file""")
    glob_string: str = Field(..., description="""Glob string to match annotation files in the dataset.""")
    is_visualization_default: Optional[bool] = Field(
        False, description="""This annotation will be rendered in neuroglancer by default."""
    )


class AnnotationSegmentationMaskFile(AnnotationSourceFile):
    """
    File and sourcing data for a segmentation mask annotation. Annotation that identifies an object.
    """

    file_format: str = Field(..., description="""File format for this file""")
    glob_string: str = Field(..., description="""Glob string to match annotation files in the dataset.""")
    is_visualization_default: Optional[bool] = Field(
        False, description="""This annotation will be rendered in neuroglancer by default."""
    )


class AnnotationSemanticSegmentationMaskFile(AnnotationSourceFile):
    """
    File and sourcing data for a semantic segmentation mask annotation. Annotation that identifies classes of objects.
    """

    mask_label: Optional[int] = Field(
        1, description="""The mask label for a semantic segmentation mask annotation file."""
    )
    file_format: str = Field(..., description="""File format for this file""")
    glob_string: str = Field(..., description="""Glob string to match annotation files in the dataset.""")
    is_visualization_default: Optional[bool] = Field(
        False, description="""This annotation will be rendered in neuroglancer by default."""
    )


class Annotation(AuthoredEntity, DatestampedEntity):
    """
    Metadata describing an annotation.
    """

    annotation_method: str = Field(
        ...,
        description="""Describe how the annotation is made (e.g. Manual, crYoLO, Positive Unlabeled Learning, template matching)""",
    )
    annotation_object: AnnotationObject = Field(..., description="""Metadata describing the object being annotated.""")
    annotation_publications: Optional[str] = Field(
        None, description="""DOIs for publications that describe the dataset. Use a comma to separate multiple DOIs."""
    )
    annotation_software: Optional[str] = Field(None, description="""Software used for generating this annotation""")
    confidence: Optional[AnnotationConfidence] = Field(
        None, description="""Metadata describing the confidence of an annotation."""
    )
    files: Optional[List[AnnotationSourceFile]] = Field(
        default_factory=list,
        description="""File and sourcing data for an annotation. Represents an entry in annotation.sources.""",
    )
    ground_truth_status: Optional[bool] = Field(
        False, description="""Whether an annotation is considered ground truth, as determined by the annotator."""
    )
    is_curator_recommended: Optional[bool] = Field(
        False, description="""This annotation is recommended by the curator to be preferred for this object type."""
    )
    method_type: AnnotationMethodTypeEnum = Field(
        ..., description="""Classification of the annotation method based on supervision."""
    )
    object_count: Optional[int] = Field(None, description="""Number of objects identified""")
    version: Optional[float] = Field(None, description="""Version of annotation.""")
    dates: DateStamp = Field(
        ..., description="""A set of dates at which a data item was deposited, published and last modified."""
    )
    authors: List[Author] = Field(default_factory=list, description="""Author of a scientific data entity.""")


class CrossReferences(ConfiguredBaseModel):
    """
    A set of cross-references to other databases and publications.
    """

    dataset_publications: Optional[str] = Field(
        None, description="""Comma-separated list of DOIs for publications associated with the dataset."""
    )
    related_database_entries: Optional[str] = Field(
        None, description="""Comma-separated list of related database entries for the dataset."""
    )
    related_database_links: Optional[str] = Field(
        None, description="""Comma-separated list of related database links for the dataset."""
    )
    dataset_citations: Optional[str] = Field(
        None, description="""Comma-separated list of DOIs for publications citing the dataset."""
    )


class GeneralGlob(ConfiguredBaseModel):
    """
    An abstracted glob class for destination and source globs.
    """

    list_glob: str = Field(..., description="""The glob for the file.""")
    match_regex: Optional[str] = Field(".*", description="""The regex for the file.""")
    name_regex: Optional[str] = Field("(.*)", description="""The regex for the name of the file.""")


class DestinationGlob(GeneralGlob):
    """
    A glob class for finding files in the output / destination directory.
    """

    list_glob: str = Field(..., description="""The glob for the file.""")
    match_regex: Optional[str] = Field(".*", description="""The regex for the file.""")
    name_regex: Optional[str] = Field("(.*)", description="""The regex for the name of the file.""")


class SourceGlob(GeneralGlob):
    """
    A glob class for finding files in the source directory.
    """

    list_glob: str = Field(..., description="""The glob for the file.""")
    match_regex: Optional[str] = Field(".*", description="""The regex for the file.""")
    name_regex: Optional[str] = Field("(.*)", description="""The regex for the name of the file.""")


class SourceMultiGlob(ConfiguredBaseModel):
    """
    A glob class for finding files in the source directory (with multiple globs).
    """

    list_globs: List[str] = Field(default_factory=list, description="""The globs for the file.""")


class DefaultSource(ConfiguredBaseModel):
    """
    A generalized source class with glob finders.
    """

    destination_glob: Optional[DestinationGlob] = Field(
        None, description="""The glob object for the destination file."""
    )
    source_glob: Optional[SourceGlob] = Field(None, description="""The glob object for the source file.""")
    source_multi_glob: Optional[SourceMultiGlob] = Field(
        None, description="""The glob object for the source file (with multiple globs)."""
    )


class SourceParentFiltersEntity(ConfiguredBaseModel):
    """
    Used as a mixin with root-level classes that contain sources that can have parent filters.
    """

    parent_filters: Optional[SourceParentFilters] = Field(None, description="""Filters for the parent of a source.""")


class SourceParentFilters(ConfiguredBaseModel):
    """
    Filters for the parent of a source.
    """

    include: Optional[SourceParent] = Field(None, description="""Include files for the parent of a source (regexes).""")
    exclude: Optional[SourceParent] = Field(None, description="""Exclude files for the parent of a source (regexes).""")


class SourceParent(ConfiguredBaseModel):
    """
    A filter for a parent class of a source. For a given attribute, it can only be used if the current class is a subclass of the attribute.
    """

    annotation: Optional[List[str]] = Field(default_factory=list, description="""Include or exclude annotations.""")
    dataset: Optional[List[str]] = Field(default_factory=list, description="""Include or exclude datasets.""")
    run: Optional[List[str]] = Field(default_factory=list, description="""Include or exclude runs.""")
    tomogram: Optional[List[str]] = Field(default_factory=list, description="""Include or exclude tomograms.""")
    voxel_spacing: Optional[List[str]] = Field(
        default_factory=list, description="""Include or exclude voxel spacings."""
    )


class DefaultLiteralEntity(ConfiguredBaseModel):
    """
    Used as a mixin with root-level classes that contain sources that have literals.
    """

    literal: Optional[DefaultLiteral] = Field(None, description="""A literal class with a value attribute.""")


class DefaultLiteral(ConfiguredBaseModel):
    """
    A literal class with a value attribute.
    """

    value: List[Any] = Field(default_factory=list, description="""The value for the literal.""")


class AnnotationEntity(ConfiguredBaseModel):
    """
    An annotation entity.
    """

    metadata: Annotation = Field(..., description="""The metadata for the annotation.""")
    sources: List[AnnotationSource] = Field(default_factory=list, description="""The sources for the annotation.""")


class AnnotationSource(ConfiguredBaseModel):
    """
    An annotation source.
    """

    InstanceSegmentation: Optional[AnnotationInstanceSegmentationFile] = Field(
        None, description="""The instance segmentation annotation source."""
    )
    OrientedPoint: Optional[AnnotationOrientedPointFile] = Field(
        None, description="""The oriented point annotation source."""
    )
    Point: Optional[AnnotationPointFile] = Field(None, description="""The point annotation source.""")
    SegmentationMask: Optional[AnnotationSegmentationMaskFile] = Field(
        None, description="""The segmentation mask annotation source."""
    )
    SemanticSegmentationMask: Optional[AnnotationSemanticSegmentationMaskFile] = Field(
        None, description="""The semantic segmentation mask annotation source."""
    )
    parent_filters: Optional[SourceParentFilters] = Field(None, description="""Filters for the parent of a source.""")


class DatasetEntity(ConfiguredBaseModel):
    """
    A dataset entity.
    """

    metadata: Dataset = Field(...)
    sources: List[DatasetSource] = Field(default_factory=list)


class DatasetSource(DefaultLiteralEntity, DefaultSource):
    """
    A dataset source.
    """

    destination_glob: Optional[DestinationGlob] = Field(
        None, description="""The glob object for the destination file."""
    )
    source_glob: Optional[SourceGlob] = Field(None, description="""The glob object for the source file.""")
    source_multi_glob: Optional[SourceMultiGlob] = Field(
        None, description="""The glob object for the source file (with multiple globs)."""
    )
    literal: Optional[DefaultLiteral] = Field(None, description="""A literal class with a value attribute.""")


class DatasetKeyPhotoEntity(ConfiguredBaseModel):
    """
    A dataset key photo entity.
    """

    sources: List[DatasetKeyPhotoSource] = Field(default_factory=list)


class DatasetKeyPhotoSource(SourceParentFiltersEntity):
    """
    A dataset key photo source.
    """

    literal: Optional[DatasetKeyPhotoLiteral] = Field(None, description="""A literal for a dataset key photo.""")
    parent_filters: Optional[SourceParentFilters] = Field(None, description="""Filters for the parent of a source.""")


class DatasetKeyPhotoLiteral(ConfiguredBaseModel):
    """
    A literal for a dataset key photo.
    """

    value: PicturePath = Field(..., description="""The value for the dataset key photo literal.""")


class FrameEntity(ConfiguredBaseModel):
    """
    A frame entity.
    """

    sources: List[FrameSource] = Field(default_factory=list)


class FrameSource(DefaultLiteralEntity, SourceParentFiltersEntity, DefaultSource):
    """
    A frame source.
    """

    destination_glob: Optional[DestinationGlob] = Field(
        None, description="""The glob object for the destination file."""
    )
    source_glob: Optional[SourceGlob] = Field(None, description="""The glob object for the source file.""")
    source_multi_glob: Optional[SourceMultiGlob] = Field(
        None, description="""The glob object for the source file (with multiple globs)."""
    )
    literal: Optional[DefaultLiteral] = Field(None, description="""A literal class with a value attribute.""")
    parent_filters: Optional[SourceParentFilters] = Field(None, description="""Filters for the parent of a source.""")


class GainEntity(ConfiguredBaseModel):
    """
    A gain entity.
    """

    sources: List[GainSource] = Field(default_factory=list)


class GainSource(DefaultLiteralEntity, SourceParentFiltersEntity, DefaultSource):
    """
    A gain source.
    """

    destination_glob: Optional[DestinationGlob] = Field(
        None, description="""The glob object for the destination file."""
    )
    source_glob: Optional[SourceGlob] = Field(None, description="""The glob object for the source file.""")
    source_multi_glob: Optional[SourceMultiGlob] = Field(
        None, description="""The glob object for the source file (with multiple globs)."""
    )
    literal: Optional[DefaultLiteral] = Field(None, description="""A literal class with a value attribute.""")
    parent_filters: Optional[SourceParentFilters] = Field(None, description="""Filters for the parent of a source.""")


class KeyImageEntity(ConfiguredBaseModel):
    """
    A key image entity.
    """

    sources: List[KeyImageSource] = Field(default_factory=list)


class KeyImageSource(DefaultLiteralEntity, SourceParentFiltersEntity, DefaultSource):
    """
    A key image source.
    """

    destination_glob: Optional[DestinationGlob] = Field(
        None, description="""The glob object for the destination file."""
    )
    source_glob: Optional[SourceGlob] = Field(None, description="""The glob object for the source file.""")
    source_multi_glob: Optional[SourceMultiGlob] = Field(
        None, description="""The glob object for the source file (with multiple globs)."""
    )
    literal: Optional[DefaultLiteral] = Field(None, description="""A literal class with a value attribute.""")
    parent_filters: Optional[SourceParentFilters] = Field(None, description="""Filters for the parent of a source.""")


class RawTiltEntity(ConfiguredBaseModel):
    """
    A raw tilt entity.
    """

    sources: List[RawTiltSource] = Field(default_factory=list)


class RawTiltSource(DefaultLiteralEntity, SourceParentFiltersEntity, DefaultSource):
    """
    A raw tilt source.
    """

    destination_glob: Optional[DestinationGlob] = Field(
        None, description="""The glob object for the destination file."""
    )
    source_glob: Optional[SourceGlob] = Field(None, description="""The glob object for the source file.""")
    source_multi_glob: Optional[SourceMultiGlob] = Field(
        None, description="""The glob object for the source file (with multiple globs)."""
    )
    literal: Optional[DefaultLiteral] = Field(None, description="""A literal class with a value attribute.""")
    parent_filters: Optional[SourceParentFilters] = Field(None, description="""Filters for the parent of a source.""")


class RunEntity(ConfiguredBaseModel):
    """
    A run entity.
    """

    sources: List[RunSource] = Field(default_factory=list)


class RunSource(DefaultLiteralEntity, SourceParentFiltersEntity, DefaultSource):
    """
    A run source.
    """

    destination_glob: Optional[DestinationGlob] = Field(
        None, description="""The glob object for the destination file."""
    )
    source_glob: Optional[SourceGlob] = Field(None, description="""The glob object for the source file.""")
    source_multi_glob: Optional[SourceMultiGlob] = Field(
        None, description="""The glob object for the source file (with multiple globs)."""
    )
    literal: Optional[DefaultLiteral] = Field(None, description="""A literal class with a value attribute.""")
    parent_filters: Optional[SourceParentFilters] = Field(None, description="""Filters for the parent of a source.""")


class StandardizationConfig(ConfiguredBaseModel):
    """
    A standardization configuration.
    """

    deposition_id: int = Field(..., description="""The deposition ID.""")
    run_data_map_file: Optional[str] = Field(None, description="""The run data map file.""")
    run_to_frame_map_csv: Optional[str] = Field(None, description="""The run to frame map CSV.""")
    run_to_tomo_map_csv: Optional[str] = Field(None, description="""The run to tomogram map CSV.""")
    run_to_ts_map_csv: Optional[str] = Field(None, description="""The run to tilt series map CSV.""")
    source_prefix: str = Field(..., description="""The source prefix of the input files.""")


class TiltSeriesEntity(ConfiguredBaseModel):
    """
    A tilt series entity.
    """

    metadata: TiltSeries = Field(...)
    sources: List[TiltSeriesSource] = Field(default_factory=list)


class TiltSeriesSource(DefaultLiteralEntity, SourceParentFiltersEntity, DefaultSource):
    """
    A tilt series source.
    """

    destination_glob: Optional[DestinationGlob] = Field(
        None, description="""The glob object for the destination file."""
    )
    source_glob: Optional[SourceGlob] = Field(None, description="""The glob object for the source file.""")
    source_multi_glob: Optional[SourceMultiGlob] = Field(
        None, description="""The glob object for the source file (with multiple globs)."""
    )
    literal: Optional[DefaultLiteral] = Field(None, description="""A literal class with a value attribute.""")
    parent_filters: Optional[SourceParentFilters] = Field(None, description="""Filters for the parent of a source.""")


class TomogramEntity(ConfiguredBaseModel):
    """
    A tomogram entity.
    """

    metadata: Tomogram = Field(...)
    sources: List[TomogramSource] = Field(default_factory=list)


class TomogramSource(DefaultLiteralEntity, SourceParentFiltersEntity, DefaultSource):
    """
    A tomogram source.
    """

    destination_glob: Optional[DestinationGlob] = Field(
        None, description="""The glob object for the destination file."""
    )
    source_glob: Optional[SourceGlob] = Field(None, description="""The glob object for the source file.""")
    source_multi_glob: Optional[SourceMultiGlob] = Field(
        None, description="""The glob object for the source file (with multiple globs)."""
    )
    literal: Optional[DefaultLiteral] = Field(None, description="""A literal class with a value attribute.""")
    parent_filters: Optional[SourceParentFilters] = Field(None, description="""Filters for the parent of a source.""")


class VoxelSpacingEntity(ConfiguredBaseModel):
    """
    A voxel spacing entity.
    """

    sources: List[VoxelSpacingSource] = Field(default_factory=list)


class VoxelSpacingSource(SourceParentFiltersEntity):
    """
    A voxel spacing source.
    """

    destination_glob: Optional[DestinationGlob] = Field(
        None, description="""The glob object for the destination file."""
    )
    source_glob: Optional[SourceGlob] = Field(None, description="""The glob object for the source file.""")
    literal: Optional[VoxelSpacingLiteral] = Field(None)
    tomogram_header: Optional[TomogramHeader] = Field(None, description="""The header for the voxel spacing.""")
    parent_filters: Optional[SourceParentFilters] = Field(None, description="""Filters for the parent of a source.""")


class VoxelSpacingLiteral(ConfiguredBaseModel):
    """
    A literal for a voxel spacing.
    """

    value: List[float] = Field(default_factory=list, description="""The value for the voxel spacing literal.""")


class TomogramHeader(ConfiguredBaseModel):
    """
    A tomogram header, a unique source attribute for voxel spacing.
    """

    list_glob: str = Field(..., description="""The glob for the tomogram header file.""")
    match_regex: Optional[str] = Field(".*", description="""The regex for the tomogram header file.""")
    header_key: Optional[str] = Field("voxel_size", description="""The key in the header file for the voxel spacing.""")


class Container(ConfiguredBaseModel):
    """
    Class that models the dataset config.
    """

    annotations: Optional[List[AnnotationEntity]] = Field(
        default_factory=list, description="""Annotations for the dataset."""
    )
    dataset_keyphotos: Optional[List[DatasetKeyPhotoEntity]] = Field(
        default_factory=list, description="""Key photos for the dataset."""
    )
    datasets: List[DatasetEntity] = Field(default_factory=list, description="""Datasets for the dataset.""")
    frames: Optional[List[FrameEntity]] = Field(default_factory=list, description="""Frames for the dataset.""")
    gains: Optional[List[GainEntity]] = Field(default_factory=list, description="""Gains for the dataset.""")
    key_images: Optional[List[KeyImageEntity]] = Field(
        default_factory=list, description="""Key images for the dataset."""
    )
    rawtilts: Optional[List[RawTiltEntity]] = Field(default_factory=list, description="""Raw tilts for the dataset.""")
    runs: Optional[List[RunEntity]] = Field(default_factory=list, description="""Runs for the dataset.""")
    standardization_config: StandardizationConfig = Field(
        ..., description="""Standardization config for the dataset."""
    )
    tiltseries: Optional[List[TiltSeriesEntity]] = Field(
        default_factory=list, description="""Tilt series for the dataset."""
    )
    tomograms: Optional[List[TomogramEntity]] = Field(
        default_factory=list, description="""Tomograms for the dataset."""
    )
    voxel_spacings: List[VoxelSpacingEntity] = Field(
        default_factory=list, description="""Voxel spacings for the dataset."""
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
PicturePath.model_rebuild()
Author.model_rebuild()
FundingDetails.model_rebuild()
DateStamp.model_rebuild()
DatestampedEntity.model_rebuild()
AuthoredEntity.model_rebuild()
FundedEntity.model_rebuild()
CrossReferencedEntity.model_rebuild()
PicturedEntity.model_rebuild()
OrganismDetails.model_rebuild()
TissueDetails.model_rebuild()
CellType.model_rebuild()
CellStrain.model_rebuild()
CellComponent.model_rebuild()
ExperimentalMetadata.model_rebuild()
Dataset.model_rebuild()
CameraDetails.model_rebuild()
MicroscopeDetails.model_rebuild()
MicroscopeOpticalSetup.model_rebuild()
TiltRange.model_rebuild()
TiltSeries.model_rebuild()
TomogramSize.model_rebuild()
TomogramOffset.model_rebuild()
Tomogram.model_rebuild()
AnnotationConfidence.model_rebuild()
AnnotationObject.model_rebuild()
AnnotationSourceFile.model_rebuild()
AnnotationOrientedPointFile.model_rebuild()
AnnotationInstanceSegmentationFile.model_rebuild()
AnnotationPointFile.model_rebuild()
AnnotationSegmentationMaskFile.model_rebuild()
AnnotationSemanticSegmentationMaskFile.model_rebuild()
Annotation.model_rebuild()
CrossReferences.model_rebuild()
GeneralGlob.model_rebuild()
DestinationGlob.model_rebuild()
SourceGlob.model_rebuild()
SourceMultiGlob.model_rebuild()
DefaultSource.model_rebuild()
SourceParentFiltersEntity.model_rebuild()
SourceParentFilters.model_rebuild()
SourceParent.model_rebuild()
DefaultLiteralEntity.model_rebuild()
DefaultLiteral.model_rebuild()
AnnotationEntity.model_rebuild()
AnnotationSource.model_rebuild()
DatasetEntity.model_rebuild()
DatasetSource.model_rebuild()
DatasetKeyPhotoEntity.model_rebuild()
DatasetKeyPhotoSource.model_rebuild()
DatasetKeyPhotoLiteral.model_rebuild()
FrameEntity.model_rebuild()
FrameSource.model_rebuild()
GainEntity.model_rebuild()
GainSource.model_rebuild()
KeyImageEntity.model_rebuild()
KeyImageSource.model_rebuild()
RawTiltEntity.model_rebuild()
RawTiltSource.model_rebuild()
RunEntity.model_rebuild()
RunSource.model_rebuild()
StandardizationConfig.model_rebuild()
TiltSeriesEntity.model_rebuild()
TiltSeriesSource.model_rebuild()
TomogramEntity.model_rebuild()
TomogramSource.model_rebuild()
VoxelSpacingEntity.model_rebuild()
VoxelSpacingSource.model_rebuild()
VoxelSpacingLiteral.model_rebuild()
TomogramHeader.model_rebuild()
Container.model_rebuild()
