from __future__ import annotations 
from datetime import (
    datetime,
    date
)
from decimal import Decimal 
from enum import Enum 
import re
import sys
from typing import (
    Any,
    List,
    Literal,
    Dict,
    Optional,
    Union
)
from pydantic.version import VERSION  as PYDANTIC_VERSION 
if int(PYDANTIC_VERSION[0])>=2:
    from pydantic import (
        BaseModel,
        ConfigDict,
        Field,
        field_validator
    )
else:
    from pydantic import (
        BaseModel,
        Field,
        validator
    )

metamodel_version = "None"
version = "1.1.0"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
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


class AnnotationShapeEnum(str, Enum):
    """
    Annotation shape types available on the data portal.
    """
    # Annotation that identifies individual instances of object shapes.
    InstanceSegmentation = "InstanceSegmentation"
    # Annotation that identifies points in the volume.
    Point = "Point"
    # Annotation that identifies points along with orientation in the volume.
    OrientedPoint = "OrientedPoint"
    # Annotation that identifies an object.
    SegmentationMask = "SegmentationMask"
    # Annotation that identifies classes of objects.
    SemanticSegmentationMask = "SemanticSegmentationMask"


class PicturePath(ConfiguredBaseModel):
    """
    A set of paths to representative images of a piece of data.
    """
    snapshot: Optional[str] = Field(None, description="""Path to the dataset preview image relative to the dataset directory root.""")
    thumbnail: Optional[str] = Field(None, description="""Path to the thumbnail of preview image relative to the dataset directory root.""")


class Author(ConfiguredBaseModel):
    """
    Author of a scientific data entity.
    """
    name: Optional[str] = Field(None, description="""The full name of the author.""")
    email: Optional[str] = Field(None, description="""The email address of the author.""")
    affiliation_name: Optional[str] = Field(None, description="""The name of the author's affiliation.""")
    affiliation_address: Optional[str] = Field(None, description="""The address of the author's affiliation.""")
    affiliation_identifier: Optional[str] = Field(None, description="""A Research Organization Registry (ROR) identifier.""")
    is_corresponding: Optional[bool] = Field(None, description="""Whether the author is a corresponding author.""")
    primary_author_status: Optional[bool] = Field(None, description="""Whether the author is a primary author.""")
    ORCID: Optional[str] = Field(None, description="""A unique, persistent identifier for researchers, provided by ORCID.""")

    @field_validator('affiliation_identifier')
    def pattern_affiliation_identifier(cls, v):
        pattern=re.compile(r"^0[a-hj-km-np-tv-z|0-9]{6}[0-9]{2}$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid affiliation_identifier format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid affiliation_identifier format: {v}")
        return v

    @field_validator('ORCID')
    def pattern_ORCID(cls, v):
        pattern=re.compile(r"[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid ORCID format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid ORCID format: {v}")
        return v


class Annotator(ConfiguredBaseModel):
    """
    Annotator of a scientific data entity.
    """
    name: Optional[str] = Field(None)
    email: Optional[str] = Field(None)
    affiliation_name: Optional[str] = Field(None)
    affiliation_address: Optional[str] = Field(None)
    affiliation_identifier: Optional[str] = Field(None)
    is_corresponding: Optional[str] = Field(None)
    is_primary_annotator: Optional[bool] = Field(None, description="""Whether the author is a primary author.""")
    ORCID: Optional[str] = Field(None)


class Funding(ConfiguredBaseModel):
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
    last_modified_date: date = Field(..., description="""The date a piece of data was last modified on the cryoET data portal.""")


class DatestampedEntity(ConfiguredBaseModel):
    """
    An entity with associated deposition, release and last modified dates.
    """
    dates: DateStamp = Field(..., description="""A set of dates at which a data item was deposited, published and last modified.""")


class AuthoredEntity(ConfiguredBaseModel):
    """
    An entity with associated authors.
    """
    authors: List[Author] = Field(default_factory=list, description="""Author of a scientific data entity.""")


class AnnotatoredEntity(ConfiguredBaseModel):
    """
    An entity with associated annotation authors.
    """
    authors: List[Annotator] = Field(default_factory=list, description="""Annotator of a scientific data entity.""")


class FundedEntity(ConfiguredBaseModel):
    """
    An entity with associated funding sources.
    """
    funding: Optional[List[Funding]] = Field(default_factory=list, description="""A funding source for a scientific data entity (base for JSON and DB representation).""")


class CrossReferencedEntity(ConfiguredBaseModel):
    """
    An entity with associated cross-references to other databases and publications.
    """
    cross_references: Optional[CrossReferences] = Field(None, description="""A set of cross-references to other databases and publications.""")


class PicturedEntity(ConfiguredBaseModel):
    """
    An entity with associated preview images.
    """
    key_photos: PicturePath = Field(..., description="""A set of paths to representative images of a piece of data.""")


class Organism(ConfiguredBaseModel):
    """
    The species from which the sample was derived.
    """
    name: Optional[str] = Field(None)
    taxonomy_id: Optional[str] = Field(None, description="""NCBI taxonomy identifier for the organism, e.g. 9606""")


class Tissue(ConfiguredBaseModel):
    """
    The type of tissue from which the sample was derived.
    """
    name: Optional[str] = Field(None)
    id: Optional[str] = Field(None, description="""The UBERON identifier for the tissue.""")


class CellType(ConfiguredBaseModel):
    """
    The cell type from which the sample was derived.
    """
    name: Optional[str] = Field(None)
    id: Optional[str] = Field(None)


class CellStrain(ConfiguredBaseModel):
    """
    The strain or cell line from which the sample was derived.
    """
    name: Optional[str] = Field(None)
    id: Optional[str] = Field(None)


class CellComponent(ConfiguredBaseModel):
    """
    The cellular component from which the sample was derived.
    """
    name: Optional[str] = Field(None)
    id: Optional[str] = Field(None)


class ExperimentalMetadata(ConfiguredBaseModel):
    """
    Metadata describing sample and sample preparation methods used in a cryoET dataset.
    """
    sample_type: Optional[SampleTypeEnum] = Field(None, description="""Type of sample imaged in a CryoET study.""")
    sample_preparation: Optional[str] = Field(None, description="""Describes how the sample was prepared.""")
    grid_preparation: Optional[str] = Field(None, description="""Describes Cryo-ET grid preparation.""")
    other_setup: Optional[str] = Field(None, description="""Describes other setup not covered by sample preparation or grid preparation that may make this dataset unique in the same publication.""")
    organism: Optional[Organism] = Field(None, description="""The species from which the sample was derived.""")
    tissue: Optional[Tissue] = Field(None, description="""The type of tissue from which the sample was derived.""")
    cell_type: Optional[CellType] = Field(None, description="""The cell type from which the sample was derived.""")
    cell_strain: Optional[CellStrain] = Field(None, description="""The strain or cell line from which the sample was derived.""")
    cell_component: Optional[CellComponent] = Field(None, description="""The cellular component from which the sample was derived.""")


class Dataset(ExperimentalMetadata, CrossReferencedEntity, FundedEntity, AuthoredEntity, DatestampedEntity):
    """
    High-level description of a cryoET dataset.
    """
    dataset_identifier: Optional[int] = Field(None, description="""An identifier for a CryoET dataset, assigned by the Data Portal. Used to identify the dataset as the directory name in data tree.""")
    dataset_title: Optional[str] = Field(None, description="""Title of a CryoET dataset.""")
    dataset_description: Optional[str] = Field(None, description="""A short description of a CryoET dataset, similar to an abstract for a journal article or dataset.""")
    dates: DateStamp = Field(..., description="""A set of dates at which a data item was deposited, published and last modified.""")
    authors: List[Author] = Field(default_factory=list, description="""Author of a scientific data entity.""")
    funding: Optional[List[Funding]] = Field(default_factory=list, description="""A funding source for a scientific data entity (base for JSON and DB representation).""")
    cross_references: Optional[CrossReferences] = Field(None, description="""A set of cross-references to other databases and publications.""")
    sample_type: Optional[str] = Field(None, description="""Type of sample imaged in a CryoET study.""")
    sample_preparation: Optional[str] = Field(None, description="""Describes how the sample was prepared.""")
    grid_preparation: Optional[str] = Field(None, description="""Describes Cryo-ET grid preparation.""")
    other_setup: Optional[str] = Field(None, description="""Describes other setup not covered by sample preparation or grid preparation that may make this dataset unique in the same publication.""")
    organism: Optional[Organism] = Field(None, description="""The species from which the sample was derived.""")
    tissue: Optional[Tissue] = Field(None, description="""The type of tissue from which the sample was derived.""")
    cell_type: Optional[CellType] = Field(None, description="""The cell type from which the sample was derived.""")
    cell_strain: Optional[CellStrain] = Field(None, description="""The strain or cell line from which the sample was derived.""")
    cell_component: Optional[CellComponent] = Field(None, description="""The cellular component from which the sample was derived.""")


class Camera(ConfiguredBaseModel):
    """
    The camera used to collect the tilt series.
    """
    manufacturer: Optional[str] = Field(None, description="""Name of the camera manufacturer""")
    model: Optional[str] = Field(None, description="""Camera model name""")


class Microscope(ConfiguredBaseModel):
    """
    The microscope used to collect the tilt series.
    """
    manufacturer: Optional[str] = Field(None)
    model: Optional[str] = Field(None)


class MicroscopeOpticalSetup(ConfiguredBaseModel):
    """
    The optical setup of the microscope used to collect the tilt series.
    """
    energy_filter: Optional[str] = Field(None, description="""Energy filter setup used""")
    phase_plate: Optional[str] = Field(None, description="""Phase plate configuration""")
    image_corrector: Optional[str] = Field(None, description="""Image corrector setup""")


class TiltRange(ConfiguredBaseModel):
    """
    The range of tilt angles in the tilt series.
    """
    min: Optional[float] = Field(None, description="""Minimal tilt angle in degrees""")
    max: Optional[float] = Field(None, description="""Maximal tilt angle in degrees""")


class TiltSeries(ConfiguredBaseModel):
    """
    Metadata describing a tilt series.
    """
    acceleration_voltage: Optional[int] = Field(None, description="""Electron Microscope Accelerator voltage in volts""")
    spherical_aberration_constant: Optional[float] = Field(None, description="""Spherical Aberration Constant of the objective lens in millimeters""")
    microscope_additional_info: Optional[str] = Field(None, description="""Other microscope optical setup information, in addition to energy filter, phase plate and image corrector""")
    tilt_axis: Optional[float] = Field(None, description="""Rotation angle in degrees""")
    tilt_step: Optional[float] = Field(None, description="""Tilt step in degrees""")
    tilting_scheme: Optional[str] = Field(None, description="""The order of stage tilting during acquisition of the data""")
    total_flux: Optional[float] = Field(None, description="""Number of Electrons reaching the specimen in a square Angstrom area for the entire tilt series""")
    data_acquisition_software: Optional[str] = Field(None, description="""Software used to collect data""")
    binning_from_frames: Optional[float] = Field(None, description="""Describes the binning factor from frames to tilt series file""")
    tilt_series_quality: Optional[int] = Field(None, description="""Author assessment of tilt series quality within the dataset (1-5, 5 is best)""")
    pixel_spacing: Optional[float] = Field(None, description="""Pixel spacing for the tilt series""")
    aligned_tiltseries_binning: Optional[int] = Field(None, description="""Binning factor of the aligned tilt series""")
    frames_count: Optional[int] = Field(None, description="""Number of frames associated with this tiltseries""")
    camera: Optional[Camera] = Field(None, description="""The camera used to collect the tilt series.""")
    microscope: Optional[Microscope] = Field(None, description="""The microscope used to collect the tilt series.""")
    microscope_optical_setup: Optional[MicroscopeOpticalSetup] = Field(None, description="""The optical setup of the microscope used to collect the tilt series.""")
    tilt_range: Optional[TiltRange] = Field(None, description="""The range of tilt angles in the tilt series.""")


class TomogramSize(ConfiguredBaseModel):
    """
    The size of a tomogram in voxels in each dimension.
    """
    x: Optional[int] = Field(None, description="""Number of pixels in the 3D data fast axis""")
    y: Optional[int] = Field(None, description="""Number of pixels in the 3D data medium axis""")
    z: Optional[int] = Field(None, description="""Number of pixels in the 3D data slow axis.  This is the image projection direction at zero stage tilt""")


class TomogramOffset(ConfiguredBaseModel):
    """
    The offset of a tomogram in voxels in each dimension relative to the canonical tomogram.
    """
    x: Optional[int] = Field(None)
    y: Optional[int] = Field(None)
    z: Optional[int] = Field(None)


class Tomogram(AuthoredEntity):
    """
    Metadata describing a tomogram.
    """
    voxel_spacing: Optional[float] = Field(None, description="""Voxel spacing equal in all three axes in angstroms""")
    fiducial_alignment_status: Optional[FiducialAlignmentStatusEnum] = Field(None, description="""Whether the tomographic alignment was computed based on fiducial markers.""")
    ctf_corrected: Optional[bool] = Field(None, description="""Whether this tomogram is CTF corrected""")
    reconstruction_method: Optional[str] = Field(None, description="""Describe reconstruction method (Weighted back-projection, SART, SIRT)""")
    reconstruction_software: Optional[str] = Field(None, description="""Name of software used for reconstruction""")
    processing: Optional[str] = Field(None, description="""Describe additional processing used to derive the tomogram""")
    processing_software: Optional[str] = Field(None, description="""Processing software used to derive the tomogram""")
    tomogram_version: Optional[string] = Field(None, description="""Version of tomogram using the same software and post-processing. Version of tomogram using the same software and post-processing. This will be presented as the latest version""")
    affine_transformation_matrix: Optional[str] = Field(None, description="""The flip or rotation transformation of this author submitted tomogram is indicated here""")
    size: Optional[TomogramSize] = Field(None, description="""The size of a tomogram in voxels in each dimension.""")
    offset: Optional[TomogramOffset] = Field(None, description="""The offset of a tomogram in voxels in each dimension relative to the canonical tomogram.""")
    authors: List[Author] = Field(default_factory=list, description="""Author of a scientific data entity.""")


class AnnotationConfidence(ConfiguredBaseModel):
    """
    Metadata describing the confidence of an annotation.
    """
    precision: Optional[float] = Field(None, description="""Describe the confidence level of the annotation. Precision is defined as the % of annotation objects being true positive""")
    recall: Optional[float] = Field(None, description="""Describe the confidence level of the annotation. Recall is defined as the % of true positives being annotated correctly""")
    ground_truth_used: Optional[str] = Field(None, description="""Annotation filename used as ground truth for precision and recall""")


class AnnotationObject(ConfiguredBaseModel):
    """
    Metadata describing the object being annotated.
    """
    id: Optional[str] = Field(None)
    name: Optional[str] = Field(None)
    description: Optional[str] = Field(None, description="""A textual description of the annotation object, can be a longer description to include additional information not covered by the Annotation object name and state.""")
    state: Optional[str] = Field(None, description="""Molecule state annotated (e.g. open, closed)""")


class AnnotationSourceFile(ConfiguredBaseModel):
    """
    File and sourcing data for an annotation. Represents an entry in annotation.sources.
    """
    file_format: str = Field(..., description="""File format for this file""")
    glob_string: str = Field(..., description="""Glob string to match annotation files in the dataset.""")
    is_visualization_default: Optional[bool] = Field(None, description="""This annotation will be rendered in neuroglancer by default.""")


class AnnotationOrientedPointFile(AnnotationSourceFile):
    """
    File and sourcing data for an oriented point annotation.
    """
    binning: Optional[int] = Field(None, description="""The binning factor for a oriented point annotation file.""")
    filter_value: Optional[str] = Field(None, description="""The filter value for a oriented point annotation file.""")
    order: Optional[str] = Field(None, description="""The order of axes for a oriented point annotation file.""")
    file_format: str = Field(...)
    glob_string: str = Field(...)
    is_visualization_default: Optional[bool] = Field(None)


class AnnotationInstanceSegmentationFile(AnnotationOrientedPointFile):
    """
    File and sourcing data for an instance segmentation annotation.
    """
    binning: Optional[int] = Field(None)
    filter_value: Optional[str] = Field(None)
    order: Optional[str] = Field(None)
    file_format: str = Field(...)
    glob_string: str = Field(...)
    is_visualization_default: Optional[bool] = Field(None)


class AnnotationPointFile(AnnotationSourceFile):
    """
    File and sourcing data for a point annotation.
    """
    binning: Optional[int] = Field(None)
    columns: Optional[str] = Field(None, description="""The columns used in a point annotation file.""")
    delimiter: Optional[str] = Field(None, description="""The delimiter used in a oriented point annotation file.""")
    file_format: str = Field(...)
    glob_string: str = Field(...)
    is_visualization_default: Optional[bool] = Field(None)


class AnnotationSegmentationMaskFile(AnnotationSourceFile):
    """
    File and sourcing data for a segmentation mask annotation.
    """
    file_format: str = Field(...)
    glob_string: str = Field(...)
    is_visualization_default: Optional[bool] = Field(None)


class AnnotationSemanticSegmentationMaskFile(AnnotationSourceFile):
    """
    File and sourcing data for a semantic segmentation mask annotation.
    """
    mask_label: Optional[int] = Field(None, description="""The mask label for a semantic segmentation mask annotation file.""")
    file_format: str = Field(...)
    glob_string: str = Field(...)
    is_visualization_default: Optional[bool] = Field(None)


class Annotation(AnnotatoredEntity, DatestampedEntity):
    """
    Metadata describing an annotation.
    """
    annotation_method: Optional[str] = Field(None, description="""Describe how the annotation is made (e.g. Manual, crYoLO, Positive Unlabeled Learning, template matching)""")
    annotation_method_type: Optional[AnnotationMethodTypeEnum] = Field(None, description="""Classification of the annotation method based on supervision.""")
    annotation_publications: Optional[str] = Field(None, description="""DOIs for publications that describe the dataset. Use a comma to separate multiple DOIs.""")
    annotation_software: Optional[str] = Field(None, description="""Software used for generating this annotation""")
    ground_truth_status: Optional[bool] = Field(None, description="""Whether an annotation is considered ground truth, as determined by the annotator.""")
    object_count: Optional[int] = Field(None, description="""Number of objects identified""")
    is_curator_recommended: Optional[bool] = Field(None, description="""This annotation is recommended by the curator to be preferred for this object type.""")
    files: Optional[List[AnnotationSourceFile]] = Field(default_factory=list, description="""File and sourcing data for an annotation. Represents an entry in annotation.sources.""")
    confidence: Optional[AnnotationConfidence] = Field(None, description="""Metadata describing the confidence of an annotation.""")
    annotation_object: Optional[AnnotationObject] = Field(None, description="""Metadata describing the object being annotated.""")
    dates: DateStamp = Field(..., description="""A set of dates at which a data item was deposited, published and last modified.""")
    authors: List[Annotator] = Field(default_factory=list, description="""Annotator of a scientific data entity.""")


class CrossReferences(ConfiguredBaseModel):
    """
    A set of cross-references to other databases and publications.
    """
    dataset_publications: Optional[str] = Field(None, description="""Comma-separated list of DOIs for publications associated with the dataset.""")
    related_database_entries: Optional[str] = Field(None, description="""Comma-separated list of related database entries for the dataset.""")


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
PicturePath.model_rebuild()
Author.model_rebuild()
Annotator.model_rebuild()
Funding.model_rebuild()
DateStamp.model_rebuild()
DatestampedEntity.model_rebuild()
AuthoredEntity.model_rebuild()
AnnotatoredEntity.model_rebuild()
FundedEntity.model_rebuild()
CrossReferencedEntity.model_rebuild()
PicturedEntity.model_rebuild()
Organism.model_rebuild()
Tissue.model_rebuild()
CellType.model_rebuild()
CellStrain.model_rebuild()
CellComponent.model_rebuild()
ExperimentalMetadata.model_rebuild()
Dataset.model_rebuild()
Camera.model_rebuild()
Microscope.model_rebuild()
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

