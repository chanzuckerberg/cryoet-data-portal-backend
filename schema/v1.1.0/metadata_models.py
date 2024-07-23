from __future__ import annotations
from datetime import datetime, date
from enum import Enum

from decimal import Decimal
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel as BaseModel, ConfigDict,  Field, field_validator
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
        extra = 'forbid',
        arbitrary_types_allowed=True,
        use_enum_values = True)

    pass

        

class AnnotationMethodTypeEnum(str, Enum):
    """
    Describes how the annotations were generated.
    """
    # Annotations were generated manually.
    manual = "manual"
    # Annotations were generated automatically.
    automated = "automated"
    # Annotations were generated semi-automatically.
    hybrid = "hybrid"
    
    

class AnnotationFileShapeTypeEnum(str, Enum):
    """
    Describes the shape of the annotation
    """
    # A binary mask volume
    SegmentationMask = "SegmentationMask"
    # A series of coordinates and an orientation
    OrientedPoint = "OrientedPoint"
    # A series of coordinates
    Point = "Point"
    # A volume with labels for multiple instances
    InstanceSegmentation = "InstanceSegmentation"
    
    

class AnnotationMethodLinkTypeEnum(str, Enum):
    """
    Describes the type of link associated to the annotation method.
    """
    # Links to the documentation related to the method.
    documentation = "documentation"
    # Links to the weights that the models used for generating annotations were trained with.
    models_weights = "models_weights"
    # Link to resources that does not fit in the other categories.
    other = "other"
    # Links to the source code of the method.
    source_code = "source_code"
    # Links to a website of the method or tool used to generate the annotation.
    website = "website"
    
    

class DepositionTypesEnum(str, Enum):
    """
    Types of data a deposition has
    """
    # The deposition comprises of new annotations for existing datasets
    annotation = "annotation"
    # The deposition comprises of new dataset(s).
    dataset = "dataset"
    # The deposition comprises of new tomograms for existing datasets
    tomogram = "tomogram"
    
    

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
    
    

class TiltseriesCameraAcquireModeEnum(str, Enum):
    """
    Camera acquisition mode
    """
    # Counting mode
    counting = "counting"
    # Super-resolution mode
    superresolution = "superresolution"
    # Linear mode
    linear = "linear"
    # Correlated double sampling mode
    cds = "cds"
    
    

class MicroscopeManufacturerEnum(str, Enum):
    """
    Microscope manufacturer
    """
    # FEI Company
    FEI = "FEI"
    # Thermo Fisher Scientific
    TFS = "TFS"
    # JEOL Ltd.
    JEOL = "JEOL"
    
    

class FiducialAlignmentStatusEnum(str, Enum):
    """
    Fiducial Alignment method
    """
    # Alignment computed based on fiducial markers
    FIDUCIAL = "FIDUCIAL"
    # Alignment computed without fiducial markers
    NON_FIDUCIAL = "NON_FIDUCIAL"
    
    

class TomogramProcessingEnum(str, Enum):
    """
    Tomogram processing method
    """
    # Tomogram was denoised
    denoised = "denoised"
    # Tomogram was filtered
    filtered = "filtered"
    # Tomogram was not processed
    raw = "raw"
    
    

class TomogromReconstructionMethodEnum(str, Enum):
    """
    Tomogram reconstruction method
    """
    # Simultaneous Algebraic Reconstruction Technique
    SART = "SART"
    # Fourier space reconstruction
    Fourier_Space = "Fourier Space"
    # Simultaneous Iterative Reconstruction Technique
    SIRT = "SIRT"
    # Weighted Back-Projection
    WBP = "WBP"
    # Unknown reconstruction method
    Unknown = "Unknown"
    
    

class TomogramTypeEnum(str, Enum):
    """
    Tomogram type
    """
    # Canonical tomogram (basis geometry for all annotations)
    CANONICAL = "CANONICAL"
    
    

class PicturePath(ConfiguredBaseModel):
    """
    A set of paths to representative images of a piece of data.
    """
    snapshot: Optional[str] = Field(None, description="""Path to the dataset preview image relative to the dataset directory root.""")
    thumbnail: Optional[str] = Field(None, description="""Path to the thumbnail of preview image relative to the dataset directory root.""")
    
    
    @field_validator('snapshot')
    def pattern_snapshot(cls, v):
        pattern=re.compile(r"^(((https?|s3)://)|cryoetportal-rawdatasets-dev).*$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid snapshot format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid snapshot format: {v}")
        return v
    
    @field_validator('thumbnail')
    def pattern_thumbnail(cls, v):
        pattern=re.compile(r"^(((https?|s3)://)|cryoetportal-rawdatasets-dev).*$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid thumbnail format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid thumbnail format: {v}")
        return v
    

class Author(ConfiguredBaseModel):
    """
    Author of a scientific data entity.
    """
    name: str = Field(..., description="""The full name of the author.""")
    email: Optional[str] = Field(None, description="""The email address of the author.""")
    affiliation_name: Optional[str] = Field(None, description="""The name of the author's affiliation.""")
    affiliation_address: Optional[str] = Field(None, description="""The address of the author's affiliation.""")
    affiliation_identifier: Optional[str] = Field(None, description="""A Research Organization Registry (ROR) identifier.""")
    corresponding_author_status: Optional[bool] = Field(False, description="""Whether the author is a corresponding author.""")
    primary_author_status: Optional[bool] = Field(False, description="""Whether the author is a primary author.""")
    ORCID: Optional[str] = Field(None, description="""The ORCID identifier for the author.""")
    
    
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
    
    

class FundedEntity(ConfiguredBaseModel):
    """
    An entity with associated funding sources.
    """
    funding: Optional[List[FundingDetails]] = Field(default_factory=list, description="""A funding source for a scientific data entity (base for JSON and DB representation).""")
    
    

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
    
    

class OrganismDetails(ConfiguredBaseModel):
    """
    The species from which the sample was derived.
    """
    name: str = Field(..., description="""Name of the organism from which a biological sample used in a CryoET study is derived from, e.g. homo sapiens.""")
    taxonomy_id: Optional[int] = Field(None, description="""NCBI taxonomy identifier for the organism, e.g. 9606""", ge=1)
    
    

class TissueDetails(ConfiguredBaseModel):
    """
    The type of tissue from which the sample was derived.
    """
    name: str = Field(..., description="""Name of the tissue from which a biological sample used in a CryoET study is derived from.""")
    id: Optional[str] = Field(None, description="""The UBERON identifier for the tissue.""")
    
    
    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^BTO:[0-9]{7}$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid id format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid id format: {v}")
        return v
    

class CellType(ConfiguredBaseModel):
    """
    The cell type from which the sample was derived.
    """
    name: str = Field(..., description="""Name of the cell type from which a biological sample used in a CryoET study is derived from.""")
    id: Optional[str] = Field(None, description="""Cell Ontology identifier for the cell type""")
    
    
    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^CL:[0-9]{7}$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid id format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid id format: {v}")
        return v
    

class CellStrain(ConfiguredBaseModel):
    """
    The strain or cell line from which the sample was derived.
    """
    name: str = Field(..., description="""Cell line or strain for the sample.""")
    id: Optional[str] = Field(None, description="""Link to more information about the cell strain.""")
    
    
    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^[a-zA-Z]+:[0-9]+$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid id format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid id format: {v}")
        return v
    

class CellComponent(ConfiguredBaseModel):
    """
    The cellular component from which the sample was derived.
    """
    name: str = Field(..., description="""Name of the cellular component.""")
    id: Optional[str] = Field(None, description="""The GO identifier for the cellular component.""")
    
    
    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^GO:[0-9]{7}$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid id format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid id format: {v}")
        return v
    

class ExperimentalMetadata(ConfiguredBaseModel):
    """
    Metadata describing sample and sample preparation methods used in a cryoET dataset.
    """
    sample_type: SampleTypeEnum = Field(..., description="""Type of sample imaged in a CryoET study.""")
    sample_preparation: Optional[str] = Field(None, description="""Describes how the sample was prepared.""")
    grid_preparation: Optional[str] = Field(None, description="""Describes Cryo-ET grid preparation.""")
    other_setup: Optional[str] = Field(None, description="""Describes other setup not covered by sample preparation or grid preparation that may make this dataset unique in the same publication.""")
    organism: Optional[OrganismDetails] = Field(None, description="""The species from which the sample was derived.""")
    tissue: Optional[TissueDetails] = Field(None, description="""The type of tissue from which the sample was derived.""")
    cell_type: Optional[CellType] = Field(None, description="""The cell type from which the sample was derived.""")
    cell_strain: Optional[CellStrain] = Field(None, description="""The strain or cell line from which the sample was derived.""")
    cell_component: Optional[CellComponent] = Field(None, description="""The cellular component from which the sample was derived.""")
    
    
    @field_validator('sample_type')
    def pattern_sample_type(cls, v):
        pattern=re.compile(r"(^cell$)|(^tissue$)|(^organism$)|(^organelle$)|(^virus$)|(^in_vitro$)|(^in_silico$)|(^other$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid sample_type format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid sample_type format: {v}")
        return v
    

class Dataset(ExperimentalMetadata, CrossReferencedEntity, FundedEntity, AuthoredEntity, DatestampedEntity):
    """
    High-level description of a cryoET dataset.
    """
    dataset_identifier: int = Field(..., description="""An identifier for a CryoET dataset, assigned by the Data Portal. Used to identify the dataset as the directory name in data tree.""")
    dataset_title: str = Field(..., description="""Title of a CryoET dataset.""")
    dataset_description: str = Field(..., description="""A short description of a CryoET dataset, similar to an abstract for a journal article or dataset.""")
    dates: DateStamp = Field(..., description="""A set of dates at which a data item was deposited, published and last modified.""")
    authors: List[Author] = Field(default_factory=list, description="""Author of a scientific data entity.""")
    funding: Optional[List[FundingDetails]] = Field(default_factory=list, description="""A funding source for a scientific data entity (base for JSON and DB representation).""")
    cross_references: Optional[CrossReferences] = Field(None, description="""A set of cross-references to other databases and publications.""")
    sample_type: SampleTypeEnum = Field(..., description="""Type of sample imaged in a CryoET study.""")
    sample_preparation: Optional[str] = Field(None, description="""Describes how the sample was prepared.""")
    grid_preparation: Optional[str] = Field(None, description="""Describes Cryo-ET grid preparation.""")
    other_setup: Optional[str] = Field(None, description="""Describes other setup not covered by sample preparation or grid preparation that may make this dataset unique in the same publication.""")
    organism: Optional[OrganismDetails] = Field(None, description="""The species from which the sample was derived.""")
    tissue: Optional[TissueDetails] = Field(None, description="""The type of tissue from which the sample was derived.""")
    cell_type: Optional[CellType] = Field(None, description="""The cell type from which the sample was derived.""")
    cell_strain: Optional[CellStrain] = Field(None, description="""The strain or cell line from which the sample was derived.""")
    cell_component: Optional[CellComponent] = Field(None, description="""The cellular component from which the sample was derived.""")
    
    
    @field_validator('sample_type')
    def pattern_sample_type(cls, v):
        pattern=re.compile(r"(^cell$)|(^tissue$)|(^organism$)|(^organelle$)|(^virus$)|(^in_vitro$)|(^in_silico$)|(^other$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid sample_type format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid sample_type format: {v}")
        return v
    

class Deposition(CrossReferencedEntity, AuthoredEntity, DatestampedEntity):
    """
    Metadata describing a deposition.
    """
    deposition_description: str = Field(..., description="""A short description of the deposition, similar to an abstract for a journal article or dataset.""")
    deposition_identifier: int = Field(..., description="""An identifier for a CryoET deposition, assigned by the Data Portal. Used to identify the deposition the entity is a part of.""")
    deposition_title: str = Field(..., description="""Title of a CryoET deposition.""")
    deposition_types: List[DepositionTypesEnum] = Field(default_factory=list, description="""Type of data in the deposition (e.g. dataset, annotation, tomogram)""")
    dates: DateStamp = Field(..., description="""A set of dates at which a data item was deposited, published and last modified.""")
    authors: List[Author] = Field(default_factory=list, description="""Author of a scientific data entity.""")
    cross_references: Optional[CrossReferences] = Field(None, description="""A set of cross-references to other databases and publications.""")
    
    
    @field_validator('deposition_types')
    def pattern_deposition_types(cls, v):
        pattern=re.compile(r"(^annotation$)|(^dataset$)|(^tomogram$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid deposition_types format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid deposition_types format: {v}")
        return v
    

class CameraDetails(ConfiguredBaseModel):
    """
    The camera used to collect the tilt series.
    """
    acquire_mode: Optional[Union[TiltseriesCameraAcquireModeEnum, str]] = Field(None, description="""Camera acquisition mode""")
    manufacturer: str = Field(..., description="""Name of the camera manufacturer""")
    model: str = Field(..., description="""Camera model name""")
    
    
    @field_validator('acquire_mode')
    def pattern_acquire_mode(cls, v):
        pattern=re.compile(r"(^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$)|(^counting$)|(^superresolution$)|(^linear$)|(^cds$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid acquire_mode format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid acquire_mode format: {v}")
        return v
    

class MicroscopeDetails(ConfiguredBaseModel):
    """
    The microscope used to collect the tilt series.
    """
    additional_info: Optional[str] = Field(None, description="""Other microscope optical setup information, in addition to energy filter, phase plate and image corrector""")
    manufacturer: Union[MicroscopeManufacturerEnum, str] = Field(..., description="""Name of the microscope manufacturer""")
    model: str = Field(..., description="""Microscope model name""")
    
    
    @field_validator('manufacturer')
    def pattern_manufacturer(cls, v):
        pattern=re.compile(r"(^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$)|(^FEI$)|(^TFS$)|(^JEOL$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid manufacturer format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid manufacturer format: {v}")
        return v
    

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
    min: Union[float, str] = Field(..., description="""Minimal tilt angle in degrees""", ge=-90, le=90)
    max: Union[float, str] = Field(..., description="""Maximal tilt angle in degrees""", ge=-90, le=90)
    
    
    @field_validator('min')
    def pattern_min(cls, v):
        pattern=re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid min format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid min format: {v}")
        return v
    
    @field_validator('max')
    def pattern_max(cls, v):
        pattern=re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid max format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid max format: {v}")
        return v
    

class TiltSeries(ConfiguredBaseModel):
    """
    Metadata describing a tilt series.
    """
    acceleration_voltage: float = Field(..., description="""Electron Microscope Accelerator voltage in volts""", ge=20000)
    aligned_tiltseries_binning: Optional[Union[float, str]] = Field(1.0, description="""Binning factor of the aligned tilt series""", ge=0)
    binning_from_frames: Optional[Union[float, str]] = Field(1.0, description="""Describes the binning factor from frames to tilt series file""", ge=0)
    camera: CameraDetails = Field(..., description="""The camera used to collect the tilt series.""")
    data_acquisition_software: str = Field(..., description="""Software used to collect data""")
    frames_count: Optional[int] = Field(None, description="""Number of frames associated with this tiltseries""")
    is_aligned: bool = Field(..., description="""Whether this tilt series is aligned""")
    microscope: MicroscopeDetails = Field(..., description="""The microscope used to collect the tilt series.""")
    microscope_optical_setup: MicroscopeOpticalSetup = Field(..., description="""The optical setup of the microscope used to collect the tilt series.""")
    related_empiar_entry: Optional[str] = Field(None, description="""If a tilt series is deposited into EMPIAR, enter the EMPIAR dataset identifier""")
    spherical_aberration_constant: Union[float, str] = Field(..., description="""Spherical Aberration Constant of the objective lens in millimeters""", ge=0)
    tilt_alignment_software: Optional[str] = Field(None, description="""Software used for tilt alignment""")
    tilt_axis: Union[float, str] = Field(..., description="""Rotation angle in degrees""", ge=-360, le=360)
    tilt_range: TiltRange = Field(..., description="""The range of tilt angles in the tilt series.""")
    tilt_series_quality: Union[int, str] = Field(..., description="""Author assessment of tilt series quality within the dataset (1-5, 5 is best)""", ge=1, le=5)
    tilt_step: Union[float, str] = Field(..., description="""Tilt step in degrees""", ge=0, le=90)
    tilting_scheme: str = Field(..., description="""The order of stage tilting during acquisition of the data""")
    total_flux: Union[float, str] = Field(..., description="""Number of Electrons reaching the specimen in a square Angstrom area for the entire tilt series""", ge=0)
    pixel_spacing: Union[float, str] = Field(..., description="""Pixel spacing for the tilt series""", ge=0.001)
    
    
    @field_validator('aligned_tiltseries_binning')
    def pattern_aligned_tiltseries_binning(cls, v):
        pattern=re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid aligned_tiltseries_binning format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid aligned_tiltseries_binning format: {v}")
        return v
    
    @field_validator('binning_from_frames')
    def pattern_binning_from_frames(cls, v):
        pattern=re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid binning_from_frames format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid binning_from_frames format: {v}")
        return v
    
    @field_validator('related_empiar_entry')
    def pattern_related_empiar_entry(cls, v):
        pattern=re.compile(r"^EMPIAR-[0-9]+$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid related_empiar_entry format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid related_empiar_entry format: {v}")
        return v
    
    @field_validator('spherical_aberration_constant')
    def pattern_spherical_aberration_constant(cls, v):
        pattern=re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid spherical_aberration_constant format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid spherical_aberration_constant format: {v}")
        return v
    
    @field_validator('tilt_axis')
    def pattern_tilt_axis(cls, v):
        pattern=re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid tilt_axis format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid tilt_axis format: {v}")
        return v
    
    @field_validator('tilt_series_quality')
    def pattern_tilt_series_quality(cls, v):
        pattern=re.compile(r"^int[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid tilt_series_quality format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid tilt_series_quality format: {v}")
        return v
    
    @field_validator('tilt_step')
    def pattern_tilt_step(cls, v):
        pattern=re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid tilt_step format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid tilt_step format: {v}")
        return v
    
    @field_validator('total_flux')
    def pattern_total_flux(cls, v):
        pattern=re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid total_flux format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid total_flux format: {v}")
        return v
    
    @field_validator('pixel_spacing')
    def pattern_pixel_spacing(cls, v):
        pattern=re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid pixel_spacing format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid pixel_spacing format: {v}")
        return v
    

class TomogramSize(ConfiguredBaseModel):
    """
    The size of a tomogram in voxels in each dimension.
    """
    x: int = Field(..., description="""Number of pixels in the 3D data fast axis""", ge=0)
    y: int = Field(..., description="""Number of pixels in the 3D data medium axis""", ge=0)
    z: int = Field(..., description="""Number of pixels in the 3D data slow axis.  This is the image projection direction at zero stage tilt""", ge=0)
    
    

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
    voxel_spacing: Union[float, str] = Field(..., description="""Voxel spacing equal in all three axes in angstroms""", ge=0.001)
    fiducial_alignment_status: Union[FiducialAlignmentStatusEnum, str] = Field(..., description="""Whether the tomographic alignment was computed based on fiducial markers.""")
    ctf_corrected: Optional[bool] = Field(None, description="""Whether this tomogram is CTF corrected""")
    align_software: Optional[str] = Field(None, description="""Software used for alignment""")
    reconstruction_method: Union[TomogromReconstructionMethodEnum, str] = Field(..., description="""Describe reconstruction method (WBP, SART, SIRT)""")
    reconstruction_software: str = Field(..., description="""Name of software used for reconstruction""")
    processing: TomogramProcessingEnum = Field(..., description="""Describe additional processing used to derive the tomogram""")
    processing_software: Optional[str] = Field(None, description="""Processing software used to derive the tomogram""")
    tomogram_version: float = Field(..., description="""Version of tomogram""")
    affine_transformation_matrix: Optional[Any] = Field(None, description="""A placeholder for any type of data.""")
    size: Optional[TomogramSize] = Field(None, description="""The size of a tomogram in voxels in each dimension.""")
    offset: TomogramOffset = Field(..., description="""The offset of a tomogram in voxels in each dimension relative to the canonical tomogram.""")
    authors: List[Author] = Field(default_factory=list, description="""Author of a scientific data entity.""")
    
    
    @field_validator('voxel_spacing')
    def pattern_voxel_spacing(cls, v):
        pattern=re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid voxel_spacing format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid voxel_spacing format: {v}")
        return v
    
    @field_validator('fiducial_alignment_status')
    def pattern_fiducial_alignment_status(cls, v):
        pattern=re.compile(r"(^FIDUCIAL$)|(^NON_FIDUCIAL$)|(^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid fiducial_alignment_status format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid fiducial_alignment_status format: {v}")
        return v
    
    @field_validator('reconstruction_method')
    def pattern_reconstruction_method(cls, v):
        pattern=re.compile(r"(^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$)|(^SART$)|(^Fourier Space$)|(^SIRT$)|(^WBP$)|(^Unknown$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid reconstruction_method format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid reconstruction_method format: {v}")
        return v
    
    @field_validator('processing')
    def pattern_processing(cls, v):
        pattern=re.compile(r"(^denoised$)|(^filtered$)|(^raw$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid processing format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid processing format: {v}")
        return v
    

class AnnotationConfidence(ConfiguredBaseModel):
    """
    Metadata describing the confidence of an annotation.
    """
    precision: Optional[float] = Field(None, description="""Describe the confidence level of the annotation. Precision is defined as the % of annotation objects being true positive""", ge=0, le=100)
    recall: Optional[float] = Field(None, description="""Describe the confidence level of the annotation. Recall is defined as the % of true positives being annotated correctly""", ge=0, le=100)
    ground_truth_used: Optional[str] = Field(None, description="""Annotation filename used as ground truth for precision and recall""")
    
    

class AnnotationObject(ConfiguredBaseModel):
    """
    Metadata describing the object being annotated.
    """
    id: str = Field(..., description="""Gene Ontology Cellular Component identifier for the annotation object""")
    name: str = Field(..., description="""Name of the object being annotated (e.g. ribosome, nuclear pore complex, actin filament, membrane)""")
    description: Optional[str] = Field(None, description="""A textual description of the annotation object, can be a longer description to include additional information not covered by the Annotation object name and state.""")
    state: Optional[str] = Field(None, description="""Molecule state annotated (e.g. open, closed)""")
    
    
    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^GO:[0-9]{7}$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid id format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid id format: {v}")
        return v
    

class AnnotationSourceFile(ConfiguredBaseModel):
    """
    File and sourcing data for an annotation. Represents an entry in annotation.sources.
    """
    file_format: str = Field(..., description="""File format for this file""")
    glob_string: Optional[str] = Field(None, description="""Glob string to match annotation files in the dataset. Required if annotation_source_file_glob_strings is not provided.""")
    glob_strings: Optional[List[str]] = Field(default_factory=list, description="""Glob strings to match annotation files in the dataset. Required if annotation_source_file_glob_string is not provided.""")
    is_visualization_default: Optional[bool] = Field(False, description="""This annotation will be rendered in neuroglancer by default.""")
    
    

class AnnotationOrientedPointFile(AnnotationSourceFile):
    """
    File and sourcing data for an oriented point annotation. Annotation that identifies points along with orientation in the volume.
    """
    binning: Optional[float] = Field(1.0, description="""The binning factor for a point / oriented point / instance segmentation annotation file.""", ge=0)
    filter_value: Optional[str] = Field(None, description="""The filter value for an oriented point / instance segmentation annotation file.""")
    order: Optional[str] = Field("xyz", description="""The order of axes for an oriented point / instance segmentation annotation file.""")
    file_format: str = Field(..., description="""File format for this file""")
    glob_string: Optional[str] = Field(None, description="""Glob string to match annotation files in the dataset. Required if annotation_source_file_glob_strings is not provided.""")
    glob_strings: Optional[List[str]] = Field(default_factory=list, description="""Glob strings to match annotation files in the dataset. Required if annotation_source_file_glob_string is not provided.""")
    is_visualization_default: Optional[bool] = Field(False, description="""This annotation will be rendered in neuroglancer by default.""")
    
    

class AnnotationInstanceSegmentationFile(AnnotationOrientedPointFile):
    """
    File and sourcing data for an instance segmentation annotation. Annotation that identifies individual instances of object shapes.
    """
    binning: Optional[float] = Field(1.0, description="""The binning factor for a point / oriented point / instance segmentation annotation file.""", ge=0)
    filter_value: Optional[str] = Field(None, description="""The filter value for an oriented point / instance segmentation annotation file.""")
    order: Optional[str] = Field("xyz", description="""The order of axes for an oriented point / instance segmentation annotation file.""")
    file_format: str = Field(..., description="""File format for this file""")
    glob_string: Optional[str] = Field(None, description="""Glob string to match annotation files in the dataset. Required if annotation_source_file_glob_strings is not provided.""")
    glob_strings: Optional[List[str]] = Field(default_factory=list, description="""Glob strings to match annotation files in the dataset. Required if annotation_source_file_glob_string is not provided.""")
    is_visualization_default: Optional[bool] = Field(False, description="""This annotation will be rendered in neuroglancer by default.""")
    
    

class AnnotationPointFile(AnnotationSourceFile):
    """
    File and sourcing data for a point annotation. Annotation that identifies points in the volume.
    """
    binning: Optional[float] = Field(1.0, description="""The binning factor for a point / oriented point / instance segmentation annotation file.""", ge=0)
    columns: Optional[str] = Field("xyz", description="""The columns used in a point annotation file.""")
    delimiter: Optional[str] = Field(",", description="""The delimiter used in a point annotation file.""")
    file_format: str = Field(..., description="""File format for this file""")
    glob_string: Optional[str] = Field(None, description="""Glob string to match annotation files in the dataset. Required if annotation_source_file_glob_strings is not provided.""")
    glob_strings: Optional[List[str]] = Field(default_factory=list, description="""Glob strings to match annotation files in the dataset. Required if annotation_source_file_glob_string is not provided.""")
    is_visualization_default: Optional[bool] = Field(False, description="""This annotation will be rendered in neuroglancer by default.""")
    
    

class AnnotationSegmentationMaskFile(AnnotationSourceFile):
    """
    File and sourcing data for a segmentation mask annotation. Annotation that identifies an object.
    """
    file_format: str = Field(..., description="""File format for this file""")
    glob_string: Optional[str] = Field(None, description="""Glob string to match annotation files in the dataset. Required if annotation_source_file_glob_strings is not provided.""")
    glob_strings: Optional[List[str]] = Field(default_factory=list, description="""Glob strings to match annotation files in the dataset. Required if annotation_source_file_glob_string is not provided.""")
    is_visualization_default: Optional[bool] = Field(False, description="""This annotation will be rendered in neuroglancer by default.""")
    
    

class AnnotationSemanticSegmentationMaskFile(AnnotationSourceFile):
    """
    File and sourcing data for a semantic segmentation mask annotation. Annotation that identifies classes of objects.
    """
    mask_label: Optional[int] = Field(1, description="""The mask label for a semantic segmentation mask annotation file.""")
    file_format: str = Field(..., description="""File format for this file""")
    glob_string: Optional[str] = Field(None, description="""Glob string to match annotation files in the dataset. Required if annotation_source_file_glob_strings is not provided.""")
    glob_strings: Optional[List[str]] = Field(default_factory=list, description="""Glob strings to match annotation files in the dataset. Required if annotation_source_file_glob_string is not provided.""")
    is_visualization_default: Optional[bool] = Field(False, description="""This annotation will be rendered in neuroglancer by default.""")
    
    

class Annotation(AuthoredEntity, DatestampedEntity):
    """
    Metadata describing an annotation.
    """
    annotation_method: str = Field(..., description="""Describe how the annotation is made (e.g. Manual, crYoLO, Positive Unlabeled Learning, template matching)""")
    annotation_object: AnnotationObject = Field(..., description="""Metadata describing the object being annotated.""")
    annotation_publications: Optional[str] = Field(None, description="""List of publication IDs (EMPIAR, EMDB, DOI) that describe this annotation method. Comma separated.""")
    annotation_software: Optional[str] = Field(None, description="""Software used for generating this annotation""")
    confidence: Optional[AnnotationConfidence] = Field(None, description="""Metadata describing the confidence of an annotation.""")
    files: Optional[List[AnnotationSourceFile]] = Field(default_factory=list, description="""File and sourcing data for an annotation. Represents an entry in annotation.sources.""")
    ground_truth_status: Optional[bool] = Field(False, description="""Whether an annotation is considered ground truth, as determined by the annotator.""")
    is_curator_recommended: Optional[bool] = Field(False, description="""This annotation is recommended by the curator to be preferred for this object type.""")
    method_type: AnnotationMethodTypeEnum = Field(..., description="""Classification of the annotation method based on supervision.""")
    object_count: Optional[int] = Field(None, description="""Number of objects identified""")
    version: Optional[float] = Field(None, description="""Version of annotation.""")
    dates: DateStamp = Field(..., description="""A set of dates at which a data item was deposited, published and last modified.""")
    authors: List[Author] = Field(default_factory=list, description="""Author of a scientific data entity.""")
    
    
    @field_validator('annotation_publications')
    def pattern_annotation_publications(cls, v):
        pattern=re.compile(r"^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+|pdb[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+|pdb[0-9a-zA-Z]{4,8}))*$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid annotation_publications format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid annotation_publications format: {v}")
        return v
    
    @field_validator('method_type')
    def pattern_method_type(cls, v):
        pattern=re.compile(r"(^manual$)|(^automated$)|(^hybrid$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid method_type format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid method_type format: {v}")
        return v
    

class CrossReferences(ConfiguredBaseModel):
    """
    A set of cross-references to other databases and publications.
    """
    publications: Optional[str] = Field(None, description="""Comma-separated list of DOIs for publications associated with the dataset.""")
    related_database_entries: Optional[str] = Field(None, description="""Comma-separated list of related database entries for the dataset.""")
    related_database_links: Optional[str] = Field(None, description="""Comma-separated list of related database links for the dataset.""")
    dataset_citations: Optional[str] = Field(None, description="""Comma-separated list of DOIs for publications citing the dataset.""")
    
    
    @field_validator('publications')
    def pattern_publications(cls, v):
        pattern=re.compile(r"(^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+(\s*,\s*(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)*$)|(^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+(\s*,\s*(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)*$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid publications format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid publications format: {v}")
        return v
    
    @field_validator('related_database_entries')
    def pattern_related_database_entries(cls, v):
        pattern=re.compile(r"(^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8}))*$)|(^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8}))*$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid related_database_entries format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid related_database_entries format: {v}")
        return v
    

class AnnotationMethodLinks(ConfiguredBaseModel):
    """
    A set of links to models, sourcecode, documentation, etc referenced by annotation the method
    """
    link: str = Field(..., description="""URL to the resource""")
    link_type: AnnotationMethodLinkTypeEnum = Field(..., description="""Type of link (e.g. model, sourcecode, documentation)""")
    name: Optional[str] = Field(None, description="""user readable name of the resource""")
    
    
    @field_validator('link_type')
    def pattern_link_type(cls, v):
        pattern=re.compile(r"(^documentation$)|(^models_weights$)|(^other$)|(^source_code$)|(^website$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid link_type format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid link_type format: {v}")
        return v
    


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
Deposition.model_rebuild()
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
AnnotationMethodLinks.model_rebuild()

