from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import re
import sys
from typing import Any, ClassVar, List, Literal, Dict, Optional, Union
from pydantic.version import VERSION as PYDANTIC_VERSION

if int(PYDANTIC_VERSION[0]) >= 2:
    from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator
else:
    from pydantic import BaseModel, Field, validator

from pydantic import conlist

metamodel_version = "None"
version = "1.1.0"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
        arbitrary_types_allowed=True,
        use_enum_values=True,
        strict=False,
    )
    pass


class LinkMLMeta(RootModel):
    root: Dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key: str):
        return getattr(self.root, key)

    def __getitem__(self, key: str):
        return self.root[key]

    def __setitem__(self, key: str, value):
        self.root[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta(
    {
        "default_prefix": "cdp-dataset-config/",
        "description": "Schema for dataset configs",
        "id": "cdp-dataset-config",
        "imports": ["linkml:types", "./metadata_materialized", "./common"],
        "name": "cdp-dataset-config",
        "prefixes": {"linkml": {"prefix_prefix": "linkml", "prefix_reference": "https://w3id.org/linkml/"}},
        "source_file": "dataset_config_materialized.yaml",
        "types": {
            "BTO_ID": {
                "base": "str",
                "description": "A BRENDA Tissue Ontology identifier",
                "from_schema": "cdp-dataset-config",
                "name": "BTO_ID",
                "pattern": "^BTO:[0-9]{7}$",
            },
            "BooleanFormattedString": {
                "base": "str",
                "description": "A formatted string that " "represents a boolean.",
                "from_schema": "cdp-dataset-config",
                "name": "BooleanFormattedString",
                "pattern": "^[ ]*\\{[a-zA-Z0-9_-]+\\}[ " "]*$",
            },
            "CL_ID": {
                "base": "str",
                "description": "A Cell Ontology identifier",
                "from_schema": "cdp-dataset-config",
                "name": "CL_ID",
                "pattern": "^CL:[0-9]{7}$",
            },
            "DOI": {
                "base": "str",
                "description": "A Digital Object Identifier",
                "from_schema": "cdp-dataset-config",
                "name": "DOI",
                "pattern": "^(doi:)?10\\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+$",
            },
            "DOI_LIST": {
                "base": "str",
                "description": "A list of Digital Object Identifiers",
                "from_schema": "cdp-dataset-config",
                "name": "DOI_LIST",
                "pattern": "^(doi:)?10\\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+(\\s*,\\s*(doi:)?10\\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)*$",
            },
            "EMDB_ID": {
                "base": "str",
                "description": "An Electron Microscopy Data Bank " "identifier",
                "from_schema": "cdp-dataset-config",
                "name": "EMDB_ID",
                "pattern": "^EMD-[0-9]{4,5}$",
            },
            "EMPIAR_EMDB_LIST": {
                "base": "str",
                "description": "A list of EMPIAR and EMDB " "identifiers",
                "from_schema": "cdp-dataset-config",
                "name": "EMPIAR_EMDB_LIST",
                "pattern": "^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5})(\\s*,\\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}))*$",
            },
            "EMPIAR_ID": {
                "base": "str",
                "description": "An Electron Microscopy Public Image " "Archive identifier",
                "from_schema": "cdp-dataset-config",
                "name": "EMPIAR_ID",
                "pattern": "^EMPIAR-[0-9]{5}$",
            },
            "FloatFormattedString": {
                "base": "str",
                "description": "A formatted string that " "represents a floating " "point number.",
                "from_schema": "cdp-dataset-config",
                "name": "FloatFormattedString",
                "pattern": "^float[ " "]*\\{[a-zA-Z0-9_-]+\\}[ ]*$",
            },
            "GO_ID": {
                "base": "str",
                "description": "A Gene Ontology identifier",
                "from_schema": "cdp-dataset-config",
                "name": "GO_ID",
                "pattern": "^GO:[0-9]{7}$",
            },
            "IntegerFormattedString": {
                "base": "str",
                "description": "A formatted string that " "represents an integer.",
                "from_schema": "cdp-dataset-config",
                "name": "IntegerFormattedString",
                "pattern": "^int[ " "]*\\{[a-zA-Z0-9_-]+\\}[ ]*$",
            },
            "ONTOLOGY_ID": {
                "base": "str",
                "description": "An ontology identifier",
                "from_schema": "cdp-dataset-config",
                "name": "ONTOLOGY_ID",
                "pattern": "^[A-Z]+:[0-9]+$",
            },
            "ORCID": {
                "base": "str",
                "description": "A unique, persistent identifier for " "researchers, provided by ORCID.",
                "from_schema": "cdp-dataset-config",
                "name": "ORCID",
                "pattern": "[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$",
            },
            "StringFormattedString": {
                "base": "str",
                "description": "A formatted string " "(variable) that " "represents a string.",
                "from_schema": "cdp-dataset-config",
                "name": "StringFormattedString",
                "pattern": "^[ ]*\\{[a-zA-Z0-9_-]+\\}[ " "]*$",
            },
            "URLorS3URI": {
                "base": "str",
                "description": "A URL or S3 URI",
                "from_schema": "cdp-dataset-config",
                "name": "URLorS3URI",
                "pattern": "^(((https?|s3)://)|cryoetportal-rawdatasets-dev).*$",
            },
            "VersionString": {
                "base": "float",
                "description": "A version number (only major, " "minor versions)",
                "from_schema": "cdp-dataset-config",
                "minimum_value": 0,
                "name": "VersionString",
            },
            "boolean": {
                "base": "Bool",
                "description": "A binary (true or false) value",
                "exact_mappings": ["schema:Boolean"],
                "from_schema": "cdp-dataset-config",
                "name": "boolean",
                "notes": [
                    "If you are authoring schemas in LinkML YAML, "
                    "the type is referenced with the lower case "
                    '"boolean".'
                ],
                "repr": "bool",
                "uri": "xsd:boolean",
            },
            "curie": {
                "base": "Curie",
                "comments": [
                    "in RDF serializations this MUST be expanded " "to a URI",
                    "in non-RDF serializations MAY be serialized " "as the compact representation",
                ],
                "conforms_to": "https://www.w3.org/TR/curie/",
                "description": "a compact URI",
                "from_schema": "cdp-dataset-config",
                "name": "curie",
                "notes": [
                    "If you are authoring schemas in LinkML YAML, "
                    "the type is referenced with the lower case "
                    '"curie".'
                ],
                "repr": "str",
                "uri": "xsd:string",
            },
            "date": {
                "base": "XSDDate",
                "description": "a date (year, month and day) in an " "idealized calendar",
                "exact_mappings": ["schema:Date"],
                "from_schema": "cdp-dataset-config",
                "name": "date",
                "notes": [
                    "URI is dateTime because OWL reasoners don't " "work with straight date or time",
                    "If you are authoring schemas in LinkML YAML, "
                    "the type is referenced with the lower case "
                    '"date".',
                ],
                "repr": "str",
                "uri": "xsd:date",
            },
            "date_or_datetime": {
                "base": "str",
                "description": "Either a date or a datetime",
                "from_schema": "cdp-dataset-config",
                "name": "date_or_datetime",
                "notes": [
                    "If you are authoring schemas in "
                    "LinkML YAML, the type is referenced "
                    "with the lower case "
                    '"date_or_datetime".'
                ],
                "repr": "str",
                "uri": "linkml:DateOrDatetime",
            },
            "datetime": {
                "base": "XSDDateTime",
                "description": "The combination of a date and time",
                "exact_mappings": ["schema:DateTime"],
                "from_schema": "cdp-dataset-config",
                "name": "datetime",
                "notes": [
                    "If you are authoring schemas in LinkML "
                    "YAML, the type is referenced with the lower "
                    'case "datetime".'
                ],
                "repr": "str",
                "uri": "xsd:dateTime",
            },
            "decimal": {
                "base": "Decimal",
                "broad_mappings": ["schema:Number"],
                "description": "A real number with arbitrary precision "
                "that conforms to the xsd:decimal "
                "specification",
                "from_schema": "cdp-dataset-config",
                "name": "decimal",
                "notes": [
                    "If you are authoring schemas in LinkML YAML, "
                    "the type is referenced with the lower case "
                    '"decimal".'
                ],
                "uri": "xsd:decimal",
            },
            "double": {
                "base": "float",
                "close_mappings": ["schema:Float"],
                "description": "A real number that conforms to the " "xsd:double specification",
                "from_schema": "cdp-dataset-config",
                "name": "double",
                "notes": [
                    "If you are authoring schemas in LinkML YAML, "
                    "the type is referenced with the lower case "
                    '"double".'
                ],
                "uri": "xsd:double",
            },
            "float": {
                "base": "float",
                "description": "A real number that conforms to the " "xsd:float specification",
                "exact_mappings": ["schema:Float"],
                "from_schema": "cdp-dataset-config",
                "name": "float",
                "notes": [
                    "If you are authoring schemas in LinkML YAML, "
                    "the type is referenced with the lower case "
                    '"float".'
                ],
                "uri": "xsd:float",
            },
            "integer": {
                "base": "int",
                "description": "An integer",
                "exact_mappings": ["schema:Integer"],
                "from_schema": "cdp-dataset-config",
                "name": "integer",
                "notes": [
                    "If you are authoring schemas in LinkML YAML, "
                    "the type is referenced with the lower case "
                    '"integer".'
                ],
                "uri": "xsd:integer",
            },
            "jsonpath": {
                "base": "str",
                "conforms_to": "https://www.ietf.org/archive/id/draft-goessner-dispatch-jsonpath-00.html",
                "description": "A string encoding a JSON Path. The "
                "value of the string MUST conform to "
                "JSON Point syntax and SHOULD "
                "dereference to zero or more valid "
                "objects within the current instance "
                "document when encoded in tree form.",
                "from_schema": "cdp-dataset-config",
                "name": "jsonpath",
                "notes": [
                    "If you are authoring schemas in LinkML "
                    "YAML, the type is referenced with the lower "
                    'case "jsonpath".'
                ],
                "repr": "str",
                "uri": "xsd:string",
            },
            "jsonpointer": {
                "base": "str",
                "conforms_to": "https://datatracker.ietf.org/doc/html/rfc6901",
                "description": "A string encoding a JSON Pointer. "
                "The value of the string MUST "
                "conform to JSON Point syntax and "
                "SHOULD dereference to a valid "
                "object within the current instance "
                "document when encoded in tree form.",
                "from_schema": "cdp-dataset-config",
                "name": "jsonpointer",
                "notes": [
                    "If you are authoring schemas in LinkML "
                    "YAML, the type is referenced with the "
                    'lower case "jsonpointer".'
                ],
                "repr": "str",
                "uri": "xsd:string",
            },
            "ncname": {
                "base": "NCName",
                "description": "Prefix part of CURIE",
                "from_schema": "cdp-dataset-config",
                "name": "ncname",
                "notes": [
                    "If you are authoring schemas in LinkML YAML, "
                    "the type is referenced with the lower case "
                    '"ncname".'
                ],
                "repr": "str",
                "uri": "xsd:string",
            },
            "nodeidentifier": {
                "base": "NodeIdentifier",
                "description": "A URI, CURIE or BNODE that " "represents a node in a model.",
                "from_schema": "cdp-dataset-config",
                "name": "nodeidentifier",
                "notes": [
                    "If you are authoring schemas in "
                    "LinkML YAML, the type is referenced "
                    "with the lower case "
                    '"nodeidentifier".'
                ],
                "repr": "str",
                "uri": "shex:nonLiteral",
            },
            "objectidentifier": {
                "base": "ElementIdentifier",
                "comments": ["Used for inheritance and type " "checking"],
                "description": "A URI or CURIE that represents " "an object in the model.",
                "from_schema": "cdp-dataset-config",
                "name": "objectidentifier",
                "notes": [
                    "If you are authoring schemas in "
                    "LinkML YAML, the type is referenced "
                    "with the lower case "
                    '"objectidentifier".'
                ],
                "repr": "str",
                "uri": "shex:iri",
            },
            "sparqlpath": {
                "base": "str",
                "conforms_to": "https://www.w3.org/TR/sparql11-query/#propertypaths",
                "description": "A string encoding a SPARQL Property "
                "Path. The value of the string MUST "
                "conform to SPARQL syntax and SHOULD "
                "dereference to zero or more valid "
                "objects within the current instance "
                "document when encoded as RDF.",
                "from_schema": "cdp-dataset-config",
                "name": "sparqlpath",
                "notes": [
                    "If you are authoring schemas in LinkML "
                    "YAML, the type is referenced with the "
                    'lower case "sparqlpath".'
                ],
                "repr": "str",
                "uri": "xsd:string",
            },
            "string": {
                "base": "str",
                "description": "A character string",
                "exact_mappings": ["schema:Text"],
                "from_schema": "cdp-dataset-config",
                "name": "string",
                "notes": [
                    "In RDF serializations, a slot with range of "
                    "string is treated as a literal or type "
                    "xsd:string.   If you are authoring schemas in "
                    "LinkML YAML, the type is referenced with the "
                    'lower case "string".'
                ],
                "uri": "xsd:string",
            },
            "time": {
                "base": "XSDTime",
                "description": "A time object represents a (local) time of " "day, independent of any particular day",
                "exact_mappings": ["schema:Time"],
                "from_schema": "cdp-dataset-config",
                "name": "time",
                "notes": [
                    "URI is dateTime because OWL reasoners do not " "work with straight date or time",
                    "If you are authoring schemas in LinkML YAML, "
                    "the type is referenced with the lower case "
                    '"time".',
                ],
                "repr": "str",
                "uri": "xsd:time",
            },
            "uri": {
                "base": "URI",
                "close_mappings": ["schema:URL"],
                "comments": [
                    "in RDF serializations a slot with range of "
                    "uri is treated as a literal or type "
                    "xsd:anyURI unless it is an identifier or a "
                    "reference to an identifier, in which case it "
                    "is translated directly to a node"
                ],
                "conforms_to": "https://www.ietf.org/rfc/rfc3987.txt",
                "description": "a complete URI",
                "from_schema": "cdp-dataset-config",
                "name": "uri",
                "notes": [
                    "If you are authoring schemas in LinkML YAML, the " 'type is referenced with the lower case "uri".'
                ],
                "repr": "str",
                "uri": "xsd:anyURI",
            },
            "uriorcurie": {
                "base": "URIorCURIE",
                "description": "a URI or a CURIE",
                "from_schema": "cdp-dataset-config",
                "name": "uriorcurie",
                "notes": [
                    "If you are authoring schemas in LinkML "
                    "YAML, the type is referenced with the "
                    'lower case "uriorcurie".'
                ],
                "repr": "str",
                "uri": "xsd:anyURI",
            },
        },
    }
)


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
    datasets = "datasets"
    # The deposition comprises of new tomograms for existing datasets
    tomograms = "tomograms"


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
    FOURIER_SPACE = "FOURIER SPACE"
    # Simultaneous Iterative Reconstruction Technique
    SIRT = "SIRT"
    # Weighted Back-Projection
    WBP = "WBP"
    # Unknown reconstruction method
    UNKNOWN = "UNKNOWN"


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

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    snapshot: Optional[str] = Field(
        None,
        description="""Path to the dataset preview image relative to the dataset directory root.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "snapshot",
                "domain_of": ["PicturePath"],
                "exact_mappings": ["cdp-common:snapshot"],
                "recommended": True,
            }
        },
    )
    thumbnail: Optional[str] = Field(
        None,
        description="""Path to the thumbnail of preview image relative to the dataset directory root.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "thumbnail",
                "domain_of": ["PicturePath"],
                "exact_mappings": ["cdp-common:thumbnail"],
                "recommended": True,
            }
        },
    )

    @field_validator("snapshot")
    def pattern_snapshot(cls, v):
        pattern = re.compile(r"^(((https?|s3)://)|cryoetportal-rawdatasets-dev).*$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid snapshot format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid snapshot format: {v}")
        return v

    @field_validator("thumbnail")
    def pattern_thumbnail(cls, v):
        pattern = re.compile(r"^(((https?|s3)://)|cryoetportal-rawdatasets-dev).*$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid thumbnail format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid thumbnail format: {v}")
        return v


class Author(ConfiguredBaseModel):
    """
    Author of a scientific data entity.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    name: str = Field(
        ...,
        description="""The full name of the author.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": [
                    "Author",
                    "OrganismDetails",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                    "AnnotationMethodLinks",
                ],
                "exact_mappings": ["cdp-common:author_name"],
            }
        },
    )
    email: Optional[str] = Field(
        None,
        description="""The email address of the author.""",
        json_schema_extra={
            "linkml_meta": {"alias": "email", "domain_of": ["Author"], "exact_mappings": ["cdp-common:author_email"]}
        },
    )
    affiliation_name: Optional[str] = Field(
        None,
        description="""The name of the author's affiliation.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "affiliation_name",
                "domain_of": ["Author"],
                "exact_mappings": ["cdp-common:author_affiliation_name"],
            }
        },
    )
    affiliation_address: Optional[str] = Field(
        None,
        description="""The address of the author's affiliation.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "affiliation_address",
                "domain_of": ["Author"],
                "exact_mappings": ["cdp-common:author_affiliation_address"],
            }
        },
    )
    affiliation_identifier: Optional[str] = Field(
        None,
        description="""A Research Organization Registry (ROR) identifier.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "affiliation_identifier",
                "domain_of": ["Author"],
                "exact_mappings": ["cdp-common:affiliation_identifier"],
                "recommended": True,
            }
        },
    )
    corresponding_author_status: Optional[bool] = Field(
        False,
        description="""Whether the author is a corresponding author.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "corresponding_author_status",
                "domain_of": ["Author"],
                "exact_mappings": ["cdp-common:author_corresponding_author_status"],
                "ifabsent": "False",
            }
        },
    )
    primary_author_status: Optional[bool] = Field(
        False,
        description="""Whether the author is a primary author.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "primary_author_status",
                "domain_of": ["Author"],
                "exact_mappings": ["cdp-common:author_primary_author_status"],
                "ifabsent": "False",
            }
        },
    )
    ORCID: Optional[str] = Field(
        None,
        description="""The ORCID identifier for the author.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "ORCID",
                "domain_of": ["Author"],
                "exact_mappings": ["cdp-common:author_orcid"],
                "recommended": True,
            }
        },
    )

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

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    funding_agency_name: Optional[str] = Field(
        None,
        description="""The name of the funding source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "funding_agency_name",
                "domain_of": ["FundingDetails"],
                "exact_mappings": ["cdp-common:funding_agency_name"],
                "recommended": True,
            }
        },
    )
    grant_id: Optional[str] = Field(
        None,
        description="""Grant identifier provided by the funding agency""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "grant_id",
                "domain_of": ["FundingDetails"],
                "exact_mappings": ["cdp-common:funding_grant_id"],
                "recommended": True,
            }
        },
    )


class DateStamp(ConfiguredBaseModel):
    """
    A set of dates at which a data item was deposited, published and last modified.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    deposition_date: date = Field(
        ...,
        description="""The date a data item was received by the cryoET data portal.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "deposition_date",
                "domain_of": ["DateStamp"],
                "exact_mappings": ["cdp-common:deposition_date"],
            }
        },
    )
    release_date: date = Field(
        ...,
        description="""The date a data item was received by the cryoET data portal.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "release_date",
                "domain_of": ["DateStamp"],
                "exact_mappings": ["cdp-common:release_date"],
            }
        },
    )
    last_modified_date: date = Field(
        ...,
        description="""The date a piece of data was last modified on the cryoET data portal.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "last_modified_date",
                "domain_of": ["DateStamp"],
                "exact_mappings": ["cdp-common:last_modified_date"],
            }
        },
    )


class DatestampedEntity(ConfiguredBaseModel):
    """
    An entity with associated deposition, release and last modified dates.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"abstract": True, "from_schema": "metadata"})

    dates: DateStamp = Field(
        ...,
        description="""A set of dates at which a data item was deposited, published and last modified.""",
        json_schema_extra={
            "linkml_meta": {"alias": "dates", "domain_of": ["DatestampedEntity", "Dataset", "Annotation"]}
        },
    )


class AuthoredEntity(ConfiguredBaseModel):
    """
    An entity with associated authors.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"abstract": True, "from_schema": "metadata"})

    authors: List[Author] = Field(
        ...,
        description="""Author of a scientific data entity.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "authors",
                "domain_of": ["AuthoredEntity", "Dataset", "Tomogram", "Annotation"],
                "list_elements_ordered": True,
            }
        },
    )


class FundedEntity(ConfiguredBaseModel):
    """
    An entity with associated funding sources.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"abstract": True, "from_schema": "metadata"})

    funding: Optional[List[FundingDetails]] = Field(
        default_factory=list,
        description="""A funding source for a scientific data entity (base for JSON and DB representation).""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "funding",
                "domain_of": ["FundedEntity", "Dataset"],
                "list_elements_ordered": True,
                "recommended": True,
            }
        },
    )


class CrossReferencedEntity(ConfiguredBaseModel):
    """
    An entity with associated cross-references to other databases and publications.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"abstract": True, "from_schema": "metadata"})

    cross_references: Optional[CrossReferences] = Field(
        None,
        description="""A set of cross-references to other databases and publications.""",
        json_schema_extra={
            "linkml_meta": {"alias": "cross_references", "domain_of": ["CrossReferencedEntity", "Dataset"]}
        },
    )


class PicturedEntity(ConfiguredBaseModel):
    """
    An entity with associated preview images.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"abstract": True, "from_schema": "metadata"})

    key_photos: PicturePath = Field(
        ...,
        description="""A set of paths to representative images of a piece of data.""",
        json_schema_extra={"linkml_meta": {"alias": "key_photos", "domain_of": ["PicturedEntity"]}},
    )


class OrganismDetails(ConfiguredBaseModel):
    """
    The species from which the sample was derived.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    name: str = Field(
        ...,
        description="""Name of the organism from which a biological sample used in a CryoET study is derived from, e.g. homo sapiens.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": [
                    "Author",
                    "OrganismDetails",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                    "AnnotationMethodLinks",
                ],
                "exact_mappings": ["cdp-common:organism_name"],
            }
        },
    )
    taxonomy_id: Optional[int] = Field(
        None,
        description="""NCBI taxonomy identifier for the organism, e.g. 9606""",
        ge=1,
        json_schema_extra={
            "linkml_meta": {
                "alias": "taxonomy_id",
                "domain_of": ["OrganismDetails"],
                "exact_mappings": ["cdp-common:organism_taxid"],
                "recommended": True,
            }
        },
    )


class TissueDetails(ConfiguredBaseModel):
    """
    The type of tissue from which the sample was derived.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    name: str = Field(
        ...,
        description="""Name of the tissue from which a biological sample used in a CryoET study is derived from.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": [
                    "Author",
                    "OrganismDetails",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                    "AnnotationMethodLinks",
                ],
                "exact_mappings": ["cdp-common:tissue_name"],
            }
        },
    )
    id: Optional[str] = Field(
        None,
        description="""The UBERON identifier for the tissue.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "id",
                "domain_of": ["TissueDetails", "CellType", "CellStrain", "CellComponent", "AnnotationObject"],
                "exact_mappings": ["cdp-common:tissue_id"],
                "recommended": True,
            }
        },
    )

    @field_validator("id")
    def pattern_id(cls, v):
        pattern = re.compile(r"^BTO:[0-9]{7}$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid id format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid id format: {v}")
        return v


class CellType(ConfiguredBaseModel):
    """
    The cell type from which the sample was derived.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    name: str = Field(
        ...,
        description="""Name of the cell type from which a biological sample used in a CryoET study is derived from.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": [
                    "Author",
                    "OrganismDetails",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                    "AnnotationMethodLinks",
                ],
                "exact_mappings": ["cdp-common:cell_name"],
            }
        },
    )
    id: Optional[str] = Field(
        None,
        description="""Cell Ontology identifier for the cell type""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "id",
                "domain_of": ["TissueDetails", "CellType", "CellStrain", "CellComponent", "AnnotationObject"],
                "exact_mappings": ["cdp-common:cell_type_id"],
                "recommended": True,
            }
        },
    )

    @field_validator("id")
    def pattern_id(cls, v):
        pattern = re.compile(r"^CL:[0-9]{7}$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid id format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid id format: {v}")
        return v


class CellStrain(ConfiguredBaseModel):
    """
    The strain or cell line from which the sample was derived.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    name: str = Field(
        ...,
        description="""Cell line or strain for the sample.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": [
                    "Author",
                    "OrganismDetails",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                    "AnnotationMethodLinks",
                ],
                "exact_mappings": ["cdp-common:cell_strain_name"],
            }
        },
    )
    id: Optional[str] = Field(
        None,
        description="""Link to more information about the cell strain.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "id",
                "domain_of": ["TissueDetails", "CellType", "CellStrain", "CellComponent", "AnnotationObject"],
                "exact_mappings": ["cdp-common:cell_strain_id"],
                "recommended": True,
            }
        },
    )

    @field_validator("id")
    def pattern_id(cls, v):
        pattern = re.compile(r"^[A-Z]+:[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid id format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid id format: {v}")
        return v


class CellComponent(ConfiguredBaseModel):
    """
    The cellular component from which the sample was derived.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    name: str = Field(
        ...,
        description="""Name of the cellular component.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": [
                    "Author",
                    "OrganismDetails",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                    "AnnotationMethodLinks",
                ],
                "exact_mappings": ["cdp-common:cell_component_name"],
            }
        },
    )
    id: Optional[str] = Field(
        None,
        description="""The GO identifier for the cellular component.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "id",
                "domain_of": ["TissueDetails", "CellType", "CellStrain", "CellComponent", "AnnotationObject"],
                "exact_mappings": ["cdp-common:cell_component_id"],
                "recommended": True,
            }
        },
    )

    @field_validator("id")
    def pattern_id(cls, v):
        pattern = re.compile(r"^GO:[0-9]{7}$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid id format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid id format: {v}")
        return v


class ExperimentalMetadata(ConfiguredBaseModel):
    """
    Metadata describing sample and sample preparation methods used in a cryoET dataset.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"abstract": True, "from_schema": "metadata"})

    sample_type: SampleTypeEnum = Field(
        ...,
        description="""Type of sample imaged in a CryoET study.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "sample_type",
                "domain_of": ["ExperimentalMetadata", "Dataset"],
                "exact_mappings": ["cdp-common:preparation_sample_type"],
            }
        },
    )
    sample_preparation: Optional[str] = Field(
        None,
        description="""Describes how the sample was prepared.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "sample_preparation",
                "domain_of": ["ExperimentalMetadata", "Dataset"],
                "exact_mappings": ["cdp-common:sample_preparation"],
                "recommended": True,
            }
        },
    )
    grid_preparation: Optional[str] = Field(
        None,
        description="""Describes Cryo-ET grid preparation.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "grid_preparation",
                "domain_of": ["ExperimentalMetadata", "Dataset"],
                "exact_mappings": ["cdp-common:grid_preparation"],
                "recommended": True,
            }
        },
    )
    other_setup: Optional[str] = Field(
        None,
        description="""Describes other setup not covered by sample preparation or grid preparation that may make this dataset unique in the same publication.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "other_setup",
                "domain_of": ["ExperimentalMetadata", "Dataset"],
                "exact_mappings": ["cdp-common:preparation_other_setup"],
                "recommended": True,
            }
        },
    )
    organism: Optional[OrganismDetails] = Field(
        None,
        description="""The species from which the sample was derived.""",
        json_schema_extra={"linkml_meta": {"alias": "organism", "domain_of": ["ExperimentalMetadata", "Dataset"]}},
    )
    tissue: Optional[TissueDetails] = Field(
        None,
        description="""The type of tissue from which the sample was derived.""",
        json_schema_extra={"linkml_meta": {"alias": "tissue", "domain_of": ["ExperimentalMetadata", "Dataset"]}},
    )
    cell_type: Optional[CellType] = Field(
        None,
        description="""The cell type from which the sample was derived.""",
        json_schema_extra={"linkml_meta": {"alias": "cell_type", "domain_of": ["ExperimentalMetadata", "Dataset"]}},
    )
    cell_strain: Optional[CellStrain] = Field(
        None,
        description="""The strain or cell line from which the sample was derived.""",
        json_schema_extra={"linkml_meta": {"alias": "cell_strain", "domain_of": ["ExperimentalMetadata", "Dataset"]}},
    )
    cell_component: Optional[CellComponent] = Field(
        None,
        description="""The cellular component from which the sample was derived.""",
        json_schema_extra={
            "linkml_meta": {"alias": "cell_component", "domain_of": ["ExperimentalMetadata", "Dataset"]}
        },
    )

    @field_validator("sample_type")
    def pattern_sample_type(cls, v):
        pattern = re.compile(
            r"(^cell$)|(^tissue$)|(^organism$)|(^organelle$)|(^virus$)|(^in_vitro$)|(^in_silico$)|(^other$)"
        )
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid sample_type format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid sample_type format: {v}")
        return v


class Dataset(ExperimentalMetadata, CrossReferencedEntity, FundedEntity, AuthoredEntity, DatestampedEntity):
    """
    High-level description of a cryoET dataset.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "metadata",
            "mixins": [
                "DatestampedEntity",
                "AuthoredEntity",
                "FundedEntity",
                "CrossReferencedEntity",
                "ExperimentalMetadata",
            ],
        }
    )

    dataset_identifier: int = Field(
        ...,
        description="""An identifier for a CryoET dataset, assigned by the Data Portal. Used to identify the dataset as the directory name in data tree.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "dataset_identifier",
                "domain_of": ["Dataset"],
                "exact_mappings": ["cdp-common:dataset_identifier"],
            }
        },
    )
    dataset_title: str = Field(
        ...,
        description="""Title of a CryoET dataset.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "dataset_title",
                "domain_of": ["Dataset"],
                "exact_mappings": ["cdp-common:dataset_title"],
            }
        },
    )
    dataset_description: str = Field(
        ...,
        description="""A short description of a CryoET dataset, similar to an abstract for a journal article or dataset.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "dataset_description",
                "domain_of": ["Dataset"],
                "exact_mappings": ["cdp-common:dataset_description"],
            }
        },
    )
    dates: DateStamp = Field(
        ...,
        description="""A set of dates at which a data item was deposited, published and last modified.""",
        json_schema_extra={
            "linkml_meta": {"alias": "dates", "domain_of": ["DatestampedEntity", "Dataset", "Annotation"]}
        },
    )
    authors: List[Author] = Field(
        ...,
        description="""Author of a scientific data entity.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "authors",
                "domain_of": ["AuthoredEntity", "Dataset", "Tomogram", "Annotation"],
                "list_elements_ordered": True,
            }
        },
    )
    funding: Optional[List[FundingDetails]] = Field(
        default_factory=list,
        description="""A funding source for a scientific data entity (base for JSON and DB representation).""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "funding",
                "domain_of": ["FundedEntity", "Dataset"],
                "list_elements_ordered": True,
                "recommended": True,
            }
        },
    )
    cross_references: Optional[CrossReferences] = Field(
        None,
        description="""A set of cross-references to other databases and publications.""",
        json_schema_extra={
            "linkml_meta": {"alias": "cross_references", "domain_of": ["CrossReferencedEntity", "Dataset"]}
        },
    )
    sample_type: SampleTypeEnum = Field(
        ...,
        description="""Type of sample imaged in a CryoET study.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "sample_type",
                "domain_of": ["ExperimentalMetadata", "Dataset"],
                "exact_mappings": ["cdp-common:preparation_sample_type"],
            }
        },
    )
    sample_preparation: Optional[str] = Field(
        None,
        description="""Describes how the sample was prepared.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "sample_preparation",
                "domain_of": ["ExperimentalMetadata", "Dataset"],
                "exact_mappings": ["cdp-common:sample_preparation"],
                "recommended": True,
            }
        },
    )
    grid_preparation: Optional[str] = Field(
        None,
        description="""Describes Cryo-ET grid preparation.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "grid_preparation",
                "domain_of": ["ExperimentalMetadata", "Dataset"],
                "exact_mappings": ["cdp-common:grid_preparation"],
                "recommended": True,
            }
        },
    )
    other_setup: Optional[str] = Field(
        None,
        description="""Describes other setup not covered by sample preparation or grid preparation that may make this dataset unique in the same publication.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "other_setup",
                "domain_of": ["ExperimentalMetadata", "Dataset"],
                "exact_mappings": ["cdp-common:preparation_other_setup"],
                "recommended": True,
            }
        },
    )
    organism: Optional[OrganismDetails] = Field(
        None,
        description="""The species from which the sample was derived.""",
        json_schema_extra={"linkml_meta": {"alias": "organism", "domain_of": ["ExperimentalMetadata", "Dataset"]}},
    )
    tissue: Optional[TissueDetails] = Field(
        None,
        description="""The type of tissue from which the sample was derived.""",
        json_schema_extra={"linkml_meta": {"alias": "tissue", "domain_of": ["ExperimentalMetadata", "Dataset"]}},
    )
    cell_type: Optional[CellType] = Field(
        None,
        description="""The cell type from which the sample was derived.""",
        json_schema_extra={"linkml_meta": {"alias": "cell_type", "domain_of": ["ExperimentalMetadata", "Dataset"]}},
    )
    cell_strain: Optional[CellStrain] = Field(
        None,
        description="""The strain or cell line from which the sample was derived.""",
        json_schema_extra={"linkml_meta": {"alias": "cell_strain", "domain_of": ["ExperimentalMetadata", "Dataset"]}},
    )
    cell_component: Optional[CellComponent] = Field(
        None,
        description="""The cellular component from which the sample was derived.""",
        json_schema_extra={
            "linkml_meta": {"alias": "cell_component", "domain_of": ["ExperimentalMetadata", "Dataset"]}
        },
    )

    @field_validator("sample_type")
    def pattern_sample_type(cls, v):
        pattern = re.compile(
            r"(^cell$)|(^tissue$)|(^organism$)|(^organelle$)|(^virus$)|(^in_vitro$)|(^in_silico$)|(^other$)"
        )
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid sample_type format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid sample_type format: {v}")
        return v


class CameraDetails(ConfiguredBaseModel):
    """
    The camera used to collect the tilt series.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    acquire_mode: Optional[Union[TiltseriesCameraAcquireModeEnum, str]] = Field(
        None,
        description="""Camera acquisition mode""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "acquire_mode",
                "any_of": [{"range": "StringFormattedString"}, {"range": "tiltseries_camera_acquire_mode_enum"}],
                "domain_of": ["CameraDetails"],
                "exact_mappings": ["cdp-common:tiltseries_camera_acquire_mode"],
            }
        },
    )
    manufacturer: str = Field(
        ...,
        description="""Name of the camera manufacturer""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "manufacturer",
                "domain_of": ["CameraDetails", "MicroscopeDetails"],
                "exact_mappings": ["cdp-common:tiltseries_camera_manufacturer"],
            }
        },
    )
    model: str = Field(
        ...,
        description="""Camera model name""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "model",
                "domain_of": ["CameraDetails", "MicroscopeDetails"],
                "exact_mappings": ["cdp-common:tiltseries_camera_model"],
            }
        },
    )

    @field_validator("acquire_mode")
    def pattern_acquire_mode(cls, v):
        pattern = re.compile(r"(^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$)|(^counting$)|(^superresolution$)|(^linear$)|(^cds$)")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid acquire_mode format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid acquire_mode format: {v}")
        return v


class MicroscopeDetails(ConfiguredBaseModel):
    """
    The microscope used to collect the tilt series.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    additional_info: Optional[str] = Field(
        None,
        description="""Other microscope optical setup information, in addition to energy filter, phase plate and image corrector""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "additional_info",
                "domain_of": ["MicroscopeDetails"],
                "exact_mappings": ["cdp-common:tiltseries_microscope_additional_info"],
            }
        },
    )
    manufacturer: Union[MicroscopeManufacturerEnum, str] = Field(
        ...,
        description="""Name of the microscope manufacturer""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "manufacturer",
                "any_of": [{"range": "StringFormattedString"}, {"range": "microscope_manufacturer_enum"}],
                "domain_of": ["CameraDetails", "MicroscopeDetails"],
                "exact_mappings": ["cdp-common:tiltseries_microscope_manufacturer"],
            }
        },
    )
    model: str = Field(
        ...,
        description="""Microscope model name""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "model",
                "domain_of": ["CameraDetails", "MicroscopeDetails"],
                "exact_mappings": ["cdp-common:tiltseries_microscope_model"],
            }
        },
    )

    @field_validator("manufacturer")
    def pattern_manufacturer(cls, v):
        pattern = re.compile(r"(^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$)|(^FEI$)|(^TFS$)|(^JEOL$)")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid manufacturer format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid manufacturer format: {v}")
        return v


class MicroscopeOpticalSetup(ConfiguredBaseModel):
    """
    The optical setup of the microscope used to collect the tilt series.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    energy_filter: str = Field(
        ...,
        description="""Energy filter setup used""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "energy_filter",
                "domain_of": ["MicroscopeOpticalSetup"],
                "exact_mappings": ["cdp-common:tiltseries_microscope_energy_filter"],
            }
        },
    )
    phase_plate: Optional[str] = Field(
        None,
        description="""Phase plate configuration""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "phase_plate",
                "domain_of": ["MicroscopeOpticalSetup"],
                "exact_mappings": ["cdp-common:tiltseries_microscope_phase_plate"],
            }
        },
    )
    image_corrector: Optional[str] = Field(
        None,
        description="""Image corrector setup""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "image_corrector",
                "domain_of": ["MicroscopeOpticalSetup"],
                "exact_mappings": ["cdp-common:tiltseries_microscope_image_corrector"],
            }
        },
    )


class TiltRange(ConfiguredBaseModel):
    """
    The range of tilt angles in the tilt series.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    min: Union[float, str] = Field(
        ...,
        description="""Minimal tilt angle in degrees""",
        ge=-90,
        le=90,
        json_schema_extra={
            "linkml_meta": {
                "alias": "min",
                "any_of": [
                    {"maximum_value": 90, "minimum_value": -90, "range": "float"},
                    {"range": "FloatFormattedString"},
                ],
                "domain_of": ["TiltRange"],
                "exact_mappings": ["cdp-common:tiltseries_tilt_min"],
                "unit": {"descriptive_name": "degrees", "symbol": "°"},
            }
        },
    )
    max: Union[float, str] = Field(
        ...,
        description="""Maximal tilt angle in degrees""",
        ge=-90,
        le=90,
        json_schema_extra={
            "linkml_meta": {
                "alias": "max",
                "any_of": [
                    {"maximum_value": 90, "minimum_value": -90, "range": "float"},
                    {"range": "FloatFormattedString"},
                ],
                "domain_of": ["TiltRange"],
                "exact_mappings": ["cdp-common:tiltseries_tilt_max"],
                "unit": {"descriptive_name": "degrees", "symbol": "°"},
            }
        },
    )

    @field_validator("min")
    def pattern_min(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid min format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid min format: {v}")
        return v

    @field_validator("max")
    def pattern_max(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid max format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid max format: {v}")
        return v


class TiltSeries(ConfiguredBaseModel):
    """
    Metadata describing a tilt series.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    acceleration_voltage: float = Field(
        ...,
        description="""Electron Microscope Accelerator voltage in volts""",
        ge=20000,
        json_schema_extra={
            "linkml_meta": {
                "alias": "acceleration_voltage",
                "domain_of": ["TiltSeries"],
                "exact_mappings": ["cdp-common:tiltseries_acceleration_voltage"],
                "unit": {"descriptive_name": "volts", "symbol": "V"},
            }
        },
    )
    aligned_tiltseries_binning: Optional[Union[float, str]] = Field(
        1.0,
        description="""Binning factor of the aligned tilt series""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "alias": "aligned_tiltseries_binning",
                "any_of": [{"minimum_value": 0, "range": "float"}, {"range": "FloatFormattedString"}],
                "domain_of": ["TiltSeries"],
                "exact_mappings": ["cdp-common:tiltseries_aligned_tiltseries_binning"],
                "ifabsent": "float(1)",
            }
        },
    )
    binning_from_frames: Optional[Union[float, str]] = Field(
        1.0,
        description="""Describes the binning factor from frames to tilt series file""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "alias": "binning_from_frames",
                "any_of": [{"minimum_value": 0, "range": "float"}, {"range": "FloatFormattedString"}],
                "domain_of": ["TiltSeries"],
                "exact_mappings": ["cdp-common:tiltseries_binning_from_frames"],
                "ifabsent": "float(1)",
            }
        },
    )
    camera: CameraDetails = Field(
        ...,
        description="""The camera used to collect the tilt series.""",
        json_schema_extra={"linkml_meta": {"alias": "camera", "domain_of": ["TiltSeries"]}},
    )
    data_acquisition_software: str = Field(
        ...,
        description="""Software used to collect data""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "data_acquisition_software",
                "domain_of": ["TiltSeries"],
                "exact_mappings": ["cdp-common:tiltseries_data_acquisition_software"],
            }
        },
    )
    frames_count: Optional[int] = Field(
        None,
        description="""Number of frames associated with this tiltseries""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "frames_count",
                "domain_of": ["TiltSeries"],
                "exact_mappings": ["cdp-common:tiltseries_frames_count"],
            }
        },
    )
    is_aligned: bool = Field(
        ...,
        description="""Whether this tilt series is aligned""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "is_aligned",
                "domain_of": ["TiltSeries"],
                "exact_mappings": ["cdp-common:tiltseries_is_aligned"],
            }
        },
    )
    microscope: MicroscopeDetails = Field(
        ...,
        description="""The microscope used to collect the tilt series.""",
        json_schema_extra={"linkml_meta": {"alias": "microscope", "domain_of": ["TiltSeries"]}},
    )
    microscope_optical_setup: MicroscopeOpticalSetup = Field(
        ...,
        description="""The optical setup of the microscope used to collect the tilt series.""",
        json_schema_extra={"linkml_meta": {"alias": "microscope_optical_setup", "domain_of": ["TiltSeries"]}},
    )
    related_empiar_entry: Optional[str] = Field(
        None,
        description="""If a tilt series is deposited into EMPIAR, enter the EMPIAR dataset identifier""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "related_empiar_entry",
                "domain_of": ["TiltSeries"],
                "exact_mappings": ["cdp-common:tiltseries_related_empiar_entry"],
            }
        },
    )
    spherical_aberration_constant: Union[float, str] = Field(
        ...,
        description="""Spherical Aberration Constant of the objective lens in millimeters""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "alias": "spherical_aberration_constant",
                "any_of": [{"minimum_value": 0, "range": "float"}, {"range": "FloatFormattedString"}],
                "domain_of": ["TiltSeries"],
                "exact_mappings": ["cdp-common:tiltseries_spherical_aberration_constant"],
                "unit": {"descriptive_name": "millimeters", "symbol": "mm"},
            }
        },
    )
    tilt_alignment_software: Optional[str] = Field(
        None,
        description="""Software used for tilt alignment""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "tilt_alignment_software",
                "domain_of": ["TiltSeries"],
                "exact_mappings": ["cdp-common:tiltseries_tilt_alignment_software"],
            }
        },
    )
    tilt_axis: Union[float, str] = Field(
        ...,
        description="""Rotation angle in degrees""",
        ge=-360,
        le=360,
        json_schema_extra={
            "linkml_meta": {
                "alias": "tilt_axis",
                "any_of": [
                    {"maximum_value": 360, "minimum_value": -360, "range": "float"},
                    {"range": "FloatFormattedString"},
                ],
                "domain_of": ["TiltSeries"],
                "exact_mappings": ["cdp-common:tiltseries_tilt_axis"],
                "unit": {"descriptive_name": "degrees", "symbol": "°"},
            }
        },
    )
    tilt_range: TiltRange = Field(
        ...,
        description="""The range of tilt angles in the tilt series.""",
        json_schema_extra={"linkml_meta": {"alias": "tilt_range", "domain_of": ["TiltSeries"]}},
    )
    tilt_series_quality: Union[int, str] = Field(
        ...,
        description="""Author assessment of tilt series quality within the dataset (1-5, 5 is best)""",
        ge=1,
        le=5,
        json_schema_extra={
            "linkml_meta": {
                "alias": "tilt_series_quality",
                "any_of": [
                    {"maximum_value": 5, "minimum_value": 1, "range": "integer"},
                    {"range": "IntegerFormattedString"},
                ],
                "domain_of": ["TiltSeries"],
                "exact_mappings": ["cdp-common:tiltseries_tilt_series_quality"],
            }
        },
    )
    tilt_step: Union[float, str] = Field(
        ...,
        description="""Tilt step in degrees""",
        ge=0,
        le=90,
        json_schema_extra={
            "linkml_meta": {
                "alias": "tilt_step",
                "any_of": [
                    {"maximum_value": 90, "minimum_value": 0, "range": "float"},
                    {"range": "FloatFormattedString"},
                ],
                "domain_of": ["TiltSeries"],
                "exact_mappings": ["cdp-common:tiltseries_tilt_step"],
                "unit": {"descriptive_name": "degrees", "symbol": "°"},
            }
        },
    )
    tilting_scheme: str = Field(
        ...,
        description="""The order of stage tilting during acquisition of the data""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "tilting_scheme",
                "domain_of": ["TiltSeries"],
                "exact_mappings": ["cdp-common:tiltseries_tilting_scheme"],
            }
        },
    )
    total_flux: Union[float, str] = Field(
        ...,
        description="""Number of Electrons reaching the specimen in a square Angstrom area for the entire tilt series""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "alias": "total_flux",
                "any_of": [{"minimum_value": 0, "range": "float"}, {"range": "FloatFormattedString"}],
                "domain_of": ["TiltSeries"],
                "exact_mappings": ["cdp-common:tiltseries_total_flux"],
                "unit": {"descriptive_name": "electrons per square Angstrom", "symbol": "e^-/Å^2"},
            }
        },
    )
    pixel_spacing: Union[float, str] = Field(
        ...,
        description="""Pixel spacing for the tilt series""",
        ge=0.001,
        json_schema_extra={
            "linkml_meta": {
                "alias": "pixel_spacing",
                "any_of": [{"minimum_value": 0.001, "range": "float"}, {"range": "FloatFormattedString"}],
                "domain_of": ["TiltSeries"],
                "exact_mappings": ["cdp-common:tiltseries_pixel_spacing"],
                "unit": {"descriptive_name": "Angstroms per pixel", "symbol": "Å/px"},
            }
        },
    )

    @field_validator("aligned_tiltseries_binning")
    def pattern_aligned_tiltseries_binning(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid aligned_tiltseries_binning format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid aligned_tiltseries_binning format: {v}")
        return v

    @field_validator("binning_from_frames")
    def pattern_binning_from_frames(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid binning_from_frames format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid binning_from_frames format: {v}")
        return v

    @field_validator("related_empiar_entry")
    def pattern_related_empiar_entry(cls, v):
        pattern = re.compile(r"^EMPIAR-[0-9]{5}$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid related_empiar_entry format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid related_empiar_entry format: {v}")
        return v

    @field_validator("spherical_aberration_constant")
    def pattern_spherical_aberration_constant(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid spherical_aberration_constant format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid spherical_aberration_constant format: {v}")
        return v

    @field_validator("tilt_axis")
    def pattern_tilt_axis(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid tilt_axis format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid tilt_axis format: {v}")
        return v

    @field_validator("tilt_series_quality")
    def pattern_tilt_series_quality(cls, v):
        pattern = re.compile(r"^int[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid tilt_series_quality format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid tilt_series_quality format: {v}")
        return v

    @field_validator("tilt_step")
    def pattern_tilt_step(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid tilt_step format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid tilt_step format: {v}")
        return v

    @field_validator("total_flux")
    def pattern_total_flux(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid total_flux format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid total_flux format: {v}")
        return v

    @field_validator("pixel_spacing")
    def pattern_pixel_spacing(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid pixel_spacing format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid pixel_spacing format: {v}")
        return v


class TomogramSize(ConfiguredBaseModel):
    """
    The size of a tomogram in voxels in each dimension.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    x: int = Field(
        ...,
        description="""Number of pixels in the 3D data fast axis""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "alias": "x",
                "domain_of": ["TomogramSize", "TomogramOffset"],
                "unit": {"descriptive_name": "pixels", "symbol": "px"},
            }
        },
    )
    y: int = Field(
        ...,
        description="""Number of pixels in the 3D data medium axis""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "alias": "y",
                "domain_of": ["TomogramSize", "TomogramOffset"],
                "unit": {"descriptive_name": "pixels", "symbol": "px"},
            }
        },
    )
    z: int = Field(
        ...,
        description="""Number of pixels in the 3D data slow axis.  This is the image projection direction at zero stage tilt""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "alias": "z",
                "domain_of": ["TomogramSize", "TomogramOffset"],
                "unit": {"descriptive_name": "pixels", "symbol": "px"},
            }
        },
    )


class TomogramOffset(ConfiguredBaseModel):
    """
    The offset of a tomogram in voxels in each dimension relative to the canonical tomogram.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    x: int = Field(
        ...,
        description="""x offset data relative to the canonical tomogram in pixels""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "x",
                "domain_of": ["TomogramSize", "TomogramOffset"],
                "unit": {"descriptive_name": "pixels", "symbol": "px"},
            }
        },
    )
    y: int = Field(
        ...,
        description="""y offset data relative to the canonical tomogram in pixels""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "y",
                "domain_of": ["TomogramSize", "TomogramOffset"],
                "unit": {"descriptive_name": "pixels", "symbol": "px"},
            }
        },
    )
    z: int = Field(
        ...,
        description="""z offset data relative to the canonical tomogram in pixels""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "z",
                "domain_of": ["TomogramSize", "TomogramOffset"],
                "unit": {"descriptive_name": "pixels", "symbol": "px"},
            }
        },
    )


class Tomogram(AuthoredEntity):
    """
    Metadata describing a tomogram.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata", "mixins": ["AuthoredEntity"]})

    voxel_spacing: Union[float, str] = Field(
        ...,
        description="""Voxel spacing equal in all three axes in angstroms""",
        ge=0.001,
        json_schema_extra={
            "linkml_meta": {
                "alias": "voxel_spacing",
                "any_of": [{"minimum_value": 0.001, "range": "float"}, {"range": "FloatFormattedString"}],
                "domain_of": ["Tomogram", "SourceParent"],
                "exact_mappings": ["cdp-common:tomogram_voxel_spacing"],
                "unit": {"descriptive_name": "Angstroms per voxel", "symbol": "Å/voxel"},
            }
        },
    )
    fiducial_alignment_status: Union[FiducialAlignmentStatusEnum, str] = Field(
        ...,
        description="""Whether the tomographic alignment was computed based on fiducial markers.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "fiducial_alignment_status",
                "any_of": [
                    {"range": "fiducial_alignment_status_enum"},
                    {"pattern": "^[ ]*\\{[a-zA-Z0-9_-]+\\}[ ]*$", "range": "BooleanFormattedString"},
                ],
                "domain_of": ["Tomogram"],
                "exact_mappings": ["cdp-common:tomogram_fiducial_alignment_status"],
            }
        },
    )
    ctf_corrected: Optional[bool] = Field(
        None,
        description="""Whether this tomogram is CTF corrected""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "ctf_corrected",
                "domain_of": ["Tomogram"],
                "exact_mappings": ["cdp-common:tomogram_ctf_corrected"],
                "recommended": True,
            }
        },
    )
    align_software: Optional[str] = Field(
        None,
        description="""Software used for alignment""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "align_software",
                "domain_of": ["Tomogram"],
                "exact_mappings": ["cdp-common:tomogram_align_software"],
            }
        },
    )
    reconstruction_method: Union[TomogromReconstructionMethodEnum, str] = Field(
        ...,
        description="""Describe reconstruction method (WBP, SART, SIRT)""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "reconstruction_method",
                "any_of": [{"range": "StringFormattedString"}, {"range": "tomogrom_reconstruction_method_enum"}],
                "domain_of": ["Tomogram"],
                "exact_mappings": ["cdp-common:tomogram_reconstruction_method"],
            }
        },
    )
    reconstruction_software: str = Field(
        ...,
        description="""Name of software used for reconstruction""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "reconstruction_software",
                "domain_of": ["Tomogram"],
                "exact_mappings": ["cdp-common:tomogram_reconstruction_software"],
            }
        },
    )
    processing: TomogramProcessingEnum = Field(
        ...,
        description="""Describe additional processing used to derive the tomogram""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "processing",
                "domain_of": ["Tomogram"],
                "exact_mappings": ["cdp-common:tomogram_processing"],
            }
        },
    )
    processing_software: Optional[str] = Field(
        None,
        description="""Processing software used to derive the tomogram""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "processing_software",
                "domain_of": ["Tomogram"],
                "exact_mappings": ["cdp-common:tomogram_processing_software"],
                "recommended": True,
            }
        },
    )
    tomogram_version: float = Field(
        ...,
        description="""Version of tomogram""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "tomogram_version",
                "domain_of": ["Tomogram"],
                "exact_mappings": ["cdp-common:tomogram_version"],
            }
        },
    )
    affine_transformation_matrix: Optional[
        conlist(min_length=4, max_length=4, item_type=conlist(min_length=4, max_length=4, item_type=Any))
    ] = Field(
        None,
        description="""A placeholder for any type of data.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "affine_transformation_matrix",
                "array": {
                    "dimensions": [{"exact_cardinality": 4}, {"exact_cardinality": 4}],
                    "exact_number_dimensions": 2,
                },
                "domain_of": ["Tomogram"],
            }
        },
    )
    size: Optional[TomogramSize] = Field(
        None,
        description="""The size of a tomogram in voxels in each dimension.""",
        json_schema_extra={"linkml_meta": {"alias": "size", "domain_of": ["Tomogram"]}},
    )
    offset: TomogramOffset = Field(
        ...,
        description="""The offset of a tomogram in voxels in each dimension relative to the canonical tomogram.""",
        json_schema_extra={"linkml_meta": {"alias": "offset", "domain_of": ["Tomogram"]}},
    )
    authors: List[Author] = Field(
        ...,
        description="""Author of a scientific data entity.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "authors",
                "domain_of": ["AuthoredEntity", "Dataset", "Tomogram", "Annotation"],
                "list_elements_ordered": True,
            }
        },
    )

    @field_validator("voxel_spacing")
    def pattern_voxel_spacing(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid voxel_spacing format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid voxel_spacing format: {v}")
        return v

    @field_validator("fiducial_alignment_status")
    def pattern_fiducial_alignment_status(cls, v):
        pattern = re.compile(
            r"(^FIDUCIAL$)|(^NON_FIDUCIAL$)|(^FIDUCIAL$)|(^NON_FIDUCIAL$)|(^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$)"
        )
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid fiducial_alignment_status format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid fiducial_alignment_status format: {v}")
        return v

    @field_validator("reconstruction_method")
    def pattern_reconstruction_method(cls, v):
        pattern = re.compile(r"(^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$)|(^SART$)|(^FOURIER SPACE$)|(^SIRT$)|(^WBP$)|(^UNKNOWN$)")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid reconstruction_method format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid reconstruction_method format: {v}")
        return v

    @field_validator("processing")
    def pattern_processing(cls, v):
        pattern = re.compile(r"(^denoised$)|(^filtered$)|(^raw$)")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid processing format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid processing format: {v}")
        return v


class AnnotationConfidence(ConfiguredBaseModel):
    """
    Metadata describing the confidence of an annotation.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    precision: Optional[float] = Field(
        None,
        description="""Describe the confidence level of the annotation. Precision is defined as the % of annotation objects being true positive""",
        ge=0,
        le=100,
        json_schema_extra={
            "linkml_meta": {
                "alias": "precision",
                "domain_of": ["AnnotationConfidence"],
                "exact_mappings": ["cdp-common:annotation_confidence_precision"],
                "unit": {"descriptive_name": "percentage", "symbol": "%"},
            }
        },
    )
    recall: Optional[float] = Field(
        None,
        description="""Describe the confidence level of the annotation. Recall is defined as the % of true positives being annotated correctly""",
        ge=0,
        le=100,
        json_schema_extra={
            "linkml_meta": {
                "alias": "recall",
                "domain_of": ["AnnotationConfidence"],
                "exact_mappings": ["cdp-common:annotation_confidence_recall"],
                "unit": {"descriptive_name": "percentage", "symbol": "%"},
            }
        },
    )
    ground_truth_used: Optional[str] = Field(
        None,
        description="""Annotation filename used as ground truth for precision and recall""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "ground_truth_used",
                "domain_of": ["AnnotationConfidence"],
                "exact_mappings": ["cdp-common:annotation_ground_truth_used"],
            }
        },
    )


class AnnotationObject(ConfiguredBaseModel):
    """
    Metadata describing the object being annotated.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    id: str = Field(
        ...,
        description="""Gene Ontology Cellular Component identifier for the annotation object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "id",
                "domain_of": ["TissueDetails", "CellType", "CellStrain", "CellComponent", "AnnotationObject"],
                "exact_mappings": ["cdp-common:annotation_object_id"],
            }
        },
    )
    name: str = Field(
        ...,
        description="""Name of the object being annotated (e.g. ribosome, nuclear pore complex, actin filament, membrane)""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": [
                    "Author",
                    "OrganismDetails",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                    "AnnotationMethodLinks",
                ],
                "exact_mappings": ["cdp-common:annotation_object_name"],
            }
        },
    )
    description: Optional[str] = Field(
        None,
        description="""A textual description of the annotation object, can be a longer description to include additional information not covered by the Annotation object name and state.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "description",
                "domain_of": ["AnnotationObject"],
                "exact_mappings": ["cdp-common:annotation_object_description"],
            }
        },
    )
    state: Optional[str] = Field(
        None,
        description="""Molecule state annotated (e.g. open, closed)""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "state",
                "domain_of": ["AnnotationObject"],
                "exact_mappings": ["cdp-common:annotation_object_state"],
            }
        },
    )

    @field_validator("id")
    def pattern_id(cls, v):
        pattern = re.compile(r"^GO:[0-9]{7}$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid id format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid id format: {v}")
        return v


class AnnotationSourceFile(ConfiguredBaseModel):
    """
    File and sourcing data for an annotation. Represents an entry in annotation.sources.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    file_format: str = Field(
        ...,
        description="""File format for this file""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "file_format",
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_format"],
            }
        },
    )
    glob_string: str = Field(
        ...,
        description="""Glob string to match annotation files in the dataset.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "glob_string",
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_glob_string"],
            }
        },
    )
    is_visualization_default: Optional[bool] = Field(
        False,
        description="""This annotation will be rendered in neuroglancer by default.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "is_visualization_default",
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_is_visualization_default"],
                "ifabsent": "False",
            }
        },
    )


class AnnotationOrientedPointFile(AnnotationSourceFile):
    """
    File and sourcing data for an oriented point annotation. Annotation that identifies points along with orientation in the volume.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"aliases": ["OrientedPoint"], "from_schema": "metadata"})

    binning: Optional[float] = Field(
        1.0,
        description="""The binning factor for a point / oriented point / instance segmentation annotation file.""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "alias": "binning",
                "domain_of": [
                    "AnnotationOrientedPointFile",
                    "AnnotationPointFile",
                    "AnnotationInstanceSegmentationFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_binning"],
                "ifabsent": "float(1)",
            }
        },
    )
    filter_value: Optional[str] = Field(
        None,
        description="""The filter value for an oriented point / instance segmentation annotation file.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "filter_value",
                "domain_of": ["AnnotationOrientedPointFile", "AnnotationInstanceSegmentationFile"],
                "exact_mappings": ["cdp-common:annotation_source_file_filter_value"],
            }
        },
    )
    order: Optional[str] = Field(
        "xyz",
        description="""The order of axes for an oriented point / instance segmentation annotation file.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "order",
                "domain_of": ["AnnotationOrientedPointFile", "AnnotationInstanceSegmentationFile"],
                "exact_mappings": ["cdp-common:annotation_source_file_order"],
                "ifabsent": "string(xyz)",
            }
        },
    )
    file_format: str = Field(
        ...,
        description="""File format for this file""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "file_format",
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_format"],
            }
        },
    )
    glob_string: str = Field(
        ...,
        description="""Glob string to match annotation files in the dataset.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "glob_string",
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_glob_string"],
            }
        },
    )
    is_visualization_default: Optional[bool] = Field(
        False,
        description="""This annotation will be rendered in neuroglancer by default.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "is_visualization_default",
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_is_visualization_default"],
                "ifabsent": "False",
            }
        },
    )


class AnnotationInstanceSegmentationFile(AnnotationOrientedPointFile):
    """
    File and sourcing data for an instance segmentation annotation. Annotation that identifies individual instances of object shapes.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"aliases": ["InstanceSegmentation"], "from_schema": "metadata"})

    binning: Optional[float] = Field(
        1.0,
        description="""The binning factor for a point / oriented point / instance segmentation annotation file.""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "alias": "binning",
                "domain_of": [
                    "AnnotationOrientedPointFile",
                    "AnnotationPointFile",
                    "AnnotationInstanceSegmentationFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_binning"],
                "ifabsent": "float(1)",
            }
        },
    )
    filter_value: Optional[str] = Field(
        None,
        description="""The filter value for an oriented point / instance segmentation annotation file.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "filter_value",
                "domain_of": ["AnnotationOrientedPointFile", "AnnotationInstanceSegmentationFile"],
                "exact_mappings": ["cdp-common:annotation_source_file_filter_value"],
            }
        },
    )
    order: Optional[str] = Field(
        "xyz",
        description="""The order of axes for an oriented point / instance segmentation annotation file.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "order",
                "domain_of": ["AnnotationOrientedPointFile", "AnnotationInstanceSegmentationFile"],
                "exact_mappings": ["cdp-common:annotation_source_file_order"],
                "ifabsent": "string(xyz)",
            }
        },
    )
    file_format: str = Field(
        ...,
        description="""File format for this file""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "file_format",
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_format"],
            }
        },
    )
    glob_string: str = Field(
        ...,
        description="""Glob string to match annotation files in the dataset.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "glob_string",
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_glob_string"],
            }
        },
    )
    is_visualization_default: Optional[bool] = Field(
        False,
        description="""This annotation will be rendered in neuroglancer by default.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "is_visualization_default",
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_is_visualization_default"],
                "ifabsent": "False",
            }
        },
    )


class AnnotationPointFile(AnnotationSourceFile):
    """
    File and sourcing data for a point annotation. Annotation that identifies points in the volume.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"aliases": ["Point"], "from_schema": "metadata"})

    binning: Optional[float] = Field(
        1.0,
        description="""The binning factor for a point / oriented point / instance segmentation annotation file.""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "alias": "binning",
                "domain_of": [
                    "AnnotationOrientedPointFile",
                    "AnnotationPointFile",
                    "AnnotationInstanceSegmentationFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_binning"],
                "ifabsent": "float(1)",
            }
        },
    )
    columns: Optional[str] = Field(
        "xyz",
        description="""The columns used in a point annotation file.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "columns",
                "domain_of": ["AnnotationPointFile"],
                "exact_mappings": ["cdp-common:annotation_source_file_columns"],
                "ifabsent": "string(xyz)",
            }
        },
    )
    delimiter: Optional[str] = Field(
        ",",
        description="""The delimiter used in a point annotation file.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "delimiter",
                "domain_of": ["AnnotationPointFile"],
                "exact_mappings": ["cdp-common:annotation_source_file_delimiter"],
                "ifabsent": "string(,)",
            }
        },
    )
    file_format: str = Field(
        ...,
        description="""File format for this file""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "file_format",
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_format"],
            }
        },
    )
    glob_string: str = Field(
        ...,
        description="""Glob string to match annotation files in the dataset.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "glob_string",
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_glob_string"],
            }
        },
    )
    is_visualization_default: Optional[bool] = Field(
        False,
        description="""This annotation will be rendered in neuroglancer by default.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "is_visualization_default",
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_is_visualization_default"],
                "ifabsent": "False",
            }
        },
    )


class AnnotationSegmentationMaskFile(AnnotationSourceFile):
    """
    File and sourcing data for a segmentation mask annotation. Annotation that identifies an object.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"aliases": ["SegmentationMask"], "from_schema": "metadata"})

    file_format: str = Field(
        ...,
        description="""File format for this file""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "file_format",
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_format"],
            }
        },
    )
    glob_string: str = Field(
        ...,
        description="""Glob string to match annotation files in the dataset.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "glob_string",
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_glob_string"],
            }
        },
    )
    is_visualization_default: Optional[bool] = Field(
        False,
        description="""This annotation will be rendered in neuroglancer by default.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "is_visualization_default",
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_is_visualization_default"],
                "ifabsent": "False",
            }
        },
    )


class AnnotationSemanticSegmentationMaskFile(AnnotationSourceFile):
    """
    File and sourcing data for a semantic segmentation mask annotation. Annotation that identifies classes of objects.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"aliases": ["SemanticSegmentationMask"], "from_schema": "metadata"})

    mask_label: Optional[int] = Field(
        1,
        description="""The mask label for a semantic segmentation mask annotation file.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "mask_label",
                "domain_of": ["AnnotationSemanticSegmentationMaskFile"],
                "exact_mappings": ["cdp-common:annotation_source_file_mask_label"],
                "ifabsent": "int(1)",
            }
        },
    )
    file_format: str = Field(
        ...,
        description="""File format for this file""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "file_format",
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_format"],
            }
        },
    )
    glob_string: str = Field(
        ...,
        description="""Glob string to match annotation files in the dataset.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "glob_string",
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_glob_string"],
            }
        },
    )
    is_visualization_default: Optional[bool] = Field(
        False,
        description="""This annotation will be rendered in neuroglancer by default.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "is_visualization_default",
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_is_visualization_default"],
                "ifabsent": "False",
            }
        },
    )


class Annotation(AuthoredEntity, DatestampedEntity):
    """
    Metadata describing an annotation.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "metadata", "mixins": ["DatestampedEntity", "AuthoredEntity"]}
    )

    annotation_method: str = Field(
        ...,
        description="""Describe how the annotation is made (e.g. Manual, crYoLO, Positive Unlabeled Learning, template matching)""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "annotation_method",
                "domain_of": ["Annotation"],
                "exact_mappings": ["cdp-common:annotation_method"],
            }
        },
    )
    annotation_object: AnnotationObject = Field(
        ...,
        description="""Metadata describing the object being annotated.""",
        json_schema_extra={"linkml_meta": {"alias": "annotation_object", "domain_of": ["Annotation"]}},
    )
    annotation_publications: Optional[str] = Field(
        None,
        description="""DOIs for publications that describe the dataset. Use a comma to separate multiple DOIs.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "annotation_publications",
                "domain_of": ["Annotation"],
                "exact_mappings": ["cdp-common:annotation_publication"],
            }
        },
    )
    annotation_software: Optional[str] = Field(
        None,
        description="""Software used for generating this annotation""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "annotation_software",
                "domain_of": ["Annotation"],
                "exact_mappings": ["cdp-common:annotation_software"],
                "recommended": True,
            }
        },
    )
    confidence: Optional[AnnotationConfidence] = Field(
        None,
        description="""Metadata describing the confidence of an annotation.""",
        json_schema_extra={"linkml_meta": {"alias": "confidence", "domain_of": ["Annotation"]}},
    )
    files: Optional[List[AnnotationSourceFile]] = Field(
        default_factory=list,
        description="""File and sourcing data for an annotation. Represents an entry in annotation.sources.""",
        json_schema_extra={
            "linkml_meta": {"alias": "files", "domain_of": ["Annotation"], "list_elements_ordered": True}
        },
    )
    ground_truth_status: Optional[bool] = Field(
        False,
        description="""Whether an annotation is considered ground truth, as determined by the annotator.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "ground_truth_status",
                "domain_of": ["Annotation"],
                "exact_mappings": ["cdp-common:annotation_ground_truth_status"],
                "ifabsent": "False",
                "recommended": True,
            }
        },
    )
    is_curator_recommended: Optional[bool] = Field(
        False,
        description="""This annotation is recommended by the curator to be preferred for this object type.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "is_curator_recommended",
                "domain_of": ["Annotation"],
                "exact_mappings": ["cdp-common:annotation_is_curator_recommended"],
                "ifabsent": "False",
            }
        },
    )
    method_type: AnnotationMethodTypeEnum = Field(
        ...,
        description="""Classification of the annotation method based on supervision.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "method_type",
                "domain_of": ["Annotation"],
                "exact_mappings": ["cdp-common:annotation_method_type"],
            }
        },
    )
    object_count: Optional[int] = Field(
        None,
        description="""Number of objects identified""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "object_count",
                "domain_of": ["Annotation"],
                "exact_mappings": ["cdp-common:annotation_object_count"],
            }
        },
    )
    version: Optional[float] = Field(
        None,
        description="""Version of annotation.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "version",
                "domain_of": ["Annotation"],
                "exact_mappings": ["cdp-common:annotation_version"],
            }
        },
    )
    dates: DateStamp = Field(
        ...,
        description="""A set of dates at which a data item was deposited, published and last modified.""",
        json_schema_extra={
            "linkml_meta": {"alias": "dates", "domain_of": ["DatestampedEntity", "Dataset", "Annotation"]}
        },
    )
    authors: List[Author] = Field(
        ...,
        description="""Author of a scientific data entity.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "authors",
                "domain_of": ["AuthoredEntity", "Dataset", "Tomogram", "Annotation"],
                "list_elements_ordered": True,
            }
        },
    )

    @field_validator("method_type")
    def pattern_method_type(cls, v):
        pattern = re.compile(r"(^manual$)|(^automated$)|(^hybrid$)")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid method_type format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid method_type format: {v}")
        return v


class CrossReferences(ConfiguredBaseModel):
    """
    A set of cross-references to other databases and publications.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    dataset_publications: Optional[str] = Field(
        None,
        description="""Comma-separated list of DOIs for publications associated with the dataset.""",
        json_schema_extra={
            "linkml_meta": {"alias": "dataset_publications", "domain_of": ["CrossReferences"], "recommended": True}
        },
    )
    related_database_entries: Optional[str] = Field(
        None,
        description="""Comma-separated list of related database entries for the dataset.""",
        json_schema_extra={
            "linkml_meta": {"alias": "related_database_entries", "domain_of": ["CrossReferences"], "recommended": True}
        },
    )
    related_database_links: Optional[str] = Field(
        None,
        description="""Comma-separated list of related database links for the dataset.""",
        json_schema_extra={"linkml_meta": {"alias": "related_database_links", "domain_of": ["CrossReferences"]}},
    )
    dataset_citations: Optional[str] = Field(
        None,
        description="""Comma-separated list of DOIs for publications citing the dataset.""",
        json_schema_extra={"linkml_meta": {"alias": "dataset_citations", "domain_of": ["CrossReferences"]}},
    )

    @field_validator("dataset_publications")
    def pattern_dataset_publications(cls, v):
        pattern = re.compile(
            r"(^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+(\s*,\s*(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)*$)|(^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+(\s*,\s*(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)*$)"
        )
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid dataset_publications format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid dataset_publications format: {v}")
        return v

    @field_validator("related_database_entries")
    def pattern_related_database_entries(cls, v):
        pattern = re.compile(
            r"(^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}))*$)|(^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}))*$)"
        )
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid related_database_entries format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid related_database_entries format: {v}")
        return v


class AnnotationMethodLinks(ConfiguredBaseModel):
    """
    A set of links to models, sourcecode, documentation, etc referenced by annotation the method
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    link: str = Field(
        ...,
        description="""URL to the resource""",
        json_schema_extra={"linkml_meta": {"alias": "link", "domain_of": ["AnnotationMethodLinks"]}},
    )
    link_type: AnnotationMethodLinkTypeEnum = Field(
        ...,
        description="""Type of link (e.g. model, sourcecode, documentation)""",
        json_schema_extra={"linkml_meta": {"alias": "link_type", "domain_of": ["AnnotationMethodLinks"]}},
    )
    name: Optional[str] = Field(
        None,
        description="""user readable name of the resource""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": [
                    "AnnotationMethodLinks",
                    "Author",
                    "OrganismDetails",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                ],
                "recommended": True,
            }
        },
    )

    @field_validator("link_type")
    def pattern_link_type(cls, v):
        pattern = re.compile(r"(^documentation$)|(^models_weights$)|(^other$)|(^source_code$)|(^website$)")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid link_type format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid link_type format: {v}")
        return v


class Container(ConfiguredBaseModel):
    """
    Class that models the dataset config.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config", "tree_root": True})

    annotations: Optional[List[AnnotationEntity]] = Field(
        default_factory=list,
        description="""An annotation entity.""",
        json_schema_extra={"linkml_meta": {"alias": "annotations", "domain_of": ["Container"]}},
    )
    dataset_keyphotos: Optional[List[DatasetKeyPhotoEntity]] = Field(
        default_factory=list,
        description="""A dataset key photo entity.""",
        json_schema_extra={"linkml_meta": {"alias": "dataset_keyphotos", "domain_of": ["Container"]}},
    )
    datasets: List[DatasetEntity] = Field(
        ...,
        description="""A dataset entity.""",
        json_schema_extra={"linkml_meta": {"alias": "datasets", "domain_of": ["Container"]}},
    )
    frames: Optional[List[FrameEntity]] = Field(
        default_factory=list,
        description="""A frame entity.""",
        json_schema_extra={"linkml_meta": {"alias": "frames", "domain_of": ["Container"]}},
    )
    gains: Optional[List[GainEntity]] = Field(
        default_factory=list,
        description="""A gain entity.""",
        json_schema_extra={"linkml_meta": {"alias": "gains", "domain_of": ["Container"]}},
    )
    key_images: Optional[List[KeyImageEntity]] = Field(
        default_factory=list,
        description="""A key image entity.""",
        json_schema_extra={"linkml_meta": {"alias": "key_images", "domain_of": ["Container"]}},
    )
    rawtilts: Optional[List[RawTiltEntity]] = Field(
        default_factory=list,
        description="""A raw tilt entity.""",
        json_schema_extra={"linkml_meta": {"alias": "rawtilts", "domain_of": ["Container"]}},
    )
    runs: Optional[List[RunEntity]] = Field(
        default_factory=list,
        description="""A run entity.""",
        json_schema_extra={"linkml_meta": {"alias": "runs", "domain_of": ["Container"]}},
    )
    standardization_config: StandardizationConfig = Field(
        ...,
        description="""A standardization configuration.""",
        json_schema_extra={"linkml_meta": {"alias": "standardization_config", "domain_of": ["Container"]}},
    )
    tiltseries: Optional[List[TiltSeriesEntity]] = Field(
        default_factory=list,
        description="""A tilt series entity.""",
        json_schema_extra={"linkml_meta": {"alias": "tiltseries", "domain_of": ["Container"]}},
    )
    tomograms: Optional[List[TomogramEntity]] = Field(
        default_factory=list,
        description="""A tomogram entity.""",
        json_schema_extra={"linkml_meta": {"alias": "tomograms", "domain_of": ["Container"]}},
    )
    voxel_spacings: List[VoxelSpacingEntity] = Field(
        ...,
        description="""A voxel spacing entity.""",
        json_schema_extra={"linkml_meta": {"alias": "voxel_spacings", "domain_of": ["Container"]}},
    )


class GeneralGlob(ConfiguredBaseModel):
    """
    An abstracted glob class for destination and source globs.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"abstract": True, "from_schema": "cdp-dataset-config"})

    list_glob: str = Field(
        ...,
        description="""The glob for the file.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "list_glob",
                "domain_of": ["GeneralGlob", "TomogramHeader", "DestinationGlob", "SourceGlob"],
            }
        },
    )
    match_regex: Optional[str] = Field(
        ".*",
        description="""The regex for the file.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "match_regex",
                "domain_of": ["GeneralGlob", "TomogramHeader", "DestinationGlob", "SourceGlob"],
                "ifabsent": "string(.*)",
            }
        },
    )
    name_regex: Optional[str] = Field(
        "(.*)",
        description="""The regex for the name of the file.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "name_regex",
                "domain_of": ["GeneralGlob", "DestinationGlob", "SourceGlob"],
                "ifabsent": "string((.*))",
            }
        },
    )


class DestinationGlob(GeneralGlob):
    """
    A glob class for finding files in the output / destination directory.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    list_glob: str = Field(
        ...,
        description="""The glob for the file.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "list_glob",
                "domain_of": ["GeneralGlob", "TomogramHeader", "DestinationGlob", "SourceGlob"],
            }
        },
    )
    match_regex: Optional[str] = Field(
        ".*",
        description="""The regex for the file.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "match_regex",
                "domain_of": ["GeneralGlob", "TomogramHeader", "DestinationGlob", "SourceGlob"],
                "ifabsent": "string(.*)",
            }
        },
    )
    name_regex: Optional[str] = Field(
        "(.*)",
        description="""The regex for the name of the file.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "name_regex",
                "domain_of": ["GeneralGlob", "DestinationGlob", "SourceGlob"],
                "ifabsent": "string((.*))",
            }
        },
    )


class SourceGlob(GeneralGlob):
    """
    A glob class for finding files in the source directory.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    list_glob: str = Field(
        ...,
        description="""The glob for the file.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "list_glob",
                "domain_of": ["GeneralGlob", "TomogramHeader", "DestinationGlob", "SourceGlob"],
            }
        },
    )
    match_regex: Optional[str] = Field(
        ".*",
        description="""The regex for the file.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "match_regex",
                "domain_of": ["GeneralGlob", "TomogramHeader", "DestinationGlob", "SourceGlob"],
                "ifabsent": "string(.*)",
            }
        },
    )
    name_regex: Optional[str] = Field(
        "(.*)",
        description="""The regex for the name of the file.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "name_regex",
                "domain_of": ["GeneralGlob", "DestinationGlob", "SourceGlob"],
                "ifabsent": "string((.*))",
            }
        },
    )


class SourceMultiGlob(ConfiguredBaseModel):
    """
    A glob class for finding files in the source directory (with multiple globs).
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    list_globs: List[str] = Field(
        ...,
        description="""The globs for the file.""",
        json_schema_extra={"linkml_meta": {"alias": "list_globs", "domain_of": ["SourceMultiGlob"]}},
    )


class DefaultSource(ConfiguredBaseModel):
    """
    A generalized source class with glob finders.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    destination_glob: Optional[DestinationGlob] = Field(
        None,
        description="""A glob class for finding files in the output / destination directory.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "destination_glob",
                "domain_of": [
                    "DefaultSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    source_glob: Optional[SourceGlob] = Field(
        None,
        description="""A glob class for finding files in the source directory.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "source_glob",
                "domain_of": [
                    "DefaultSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    source_multi_glob: Optional[SourceMultiGlob] = Field(
        None,
        description="""A glob class for finding files in the source directory (with multiple globs).""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "source_multi_glob",
                "domain_of": [
                    "DefaultSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )


class SourceParentFiltersEntity(ConfiguredBaseModel):
    """
    Used as a mixin with root-level classes that contain sources that can have parent filters.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    parent_filters: Optional[SourceParentFilters] = Field(
        None,
        description="""Filters for the parent of a source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "parent_filters",
                "domain_of": [
                    "SourceParentFiltersEntity",
                    "AnnotationSource",
                    "DatasetKeyPhotoSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                    "VoxelSpacingSource",
                ],
            }
        },
    )


class SourceParentFilters(ConfiguredBaseModel):
    """
    Filters for the parent of a source.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    include: Optional[SourceParent] = Field(
        None,
        description="""A filter for a parent class of a source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""",
        json_schema_extra={"linkml_meta": {"alias": "include", "domain_of": ["SourceParentFilters"]}},
    )
    exclude: Optional[SourceParent] = Field(
        None,
        description="""A filter for a parent class of a source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""",
        json_schema_extra={"linkml_meta": {"alias": "exclude", "domain_of": ["SourceParentFilters"]}},
    )


class SourceParent(ConfiguredBaseModel):
    """
    A filter for a parent class of a source. For a given attribute, it can only be used if the current class is a subclass of the attribute.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    annotation: Optional[List[str]] = Field(
        default_factory=list,
        description="""Include or exclude annotations.""",
        json_schema_extra={"linkml_meta": {"alias": "annotation", "domain_of": ["SourceParent"]}},
    )
    dataset: Optional[List[str]] = Field(
        default_factory=list,
        description="""Include or exclude datasets.""",
        json_schema_extra={"linkml_meta": {"alias": "dataset", "domain_of": ["SourceParent"]}},
    )
    run: Optional[List[str]] = Field(
        default_factory=list,
        description="""Include or exclude runs.""",
        json_schema_extra={"linkml_meta": {"alias": "run", "domain_of": ["SourceParent"]}},
    )
    tomogram: Optional[List[str]] = Field(
        default_factory=list,
        description="""Include or exclude tomograms.""",
        json_schema_extra={"linkml_meta": {"alias": "tomogram", "domain_of": ["SourceParent"]}},
    )
    voxel_spacing: Optional[List[str]] = Field(
        default_factory=list,
        description="""Include or exclude voxel spacings.""",
        json_schema_extra={"linkml_meta": {"alias": "voxel_spacing", "domain_of": ["Tomogram", "SourceParent"]}},
    )


class DefaultLiteralEntity(ConfiguredBaseModel):
    """
    Used as a mixin with root-level classes that contain sources that have literals.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    literal: Optional[DefaultLiteral] = Field(
        None,
        description="""A literal class with a value attribute.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "literal",
                "domain_of": [
                    "DefaultLiteralEntity",
                    "DatasetKeyPhotoSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )


class DefaultLiteral(ConfiguredBaseModel):
    """
    A literal class with a value attribute.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    value: List[Any] = Field(
        ...,
        description="""A placeholder for any type of data.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "value",
                "domain_of": ["DefaultLiteral", "DatasetKeyPhotoLiteral", "VoxelSpacingLiteral"],
            }
        },
    )


class AnnotationEntity(ConfiguredBaseModel):
    """
    An annotation entity.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    metadata: Annotation = Field(
        ...,
        description="""Metadata describing an annotation.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "metadata",
                "domain_of": ["AnnotationEntity", "DatasetEntity", "TiltSeriesEntity", "TomogramEntity"],
            }
        },
    )
    sources: List[AnnotationSource] = Field(
        ...,
        description="""An annotation source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "sources",
                "domain_of": [
                    "AnnotationEntity",
                    "DatasetEntity",
                    "DatasetKeyPhotoEntity",
                    "FrameEntity",
                    "GainEntity",
                    "KeyImageEntity",
                    "RawTiltEntity",
                    "RunEntity",
                    "TiltSeriesEntity",
                    "TomogramEntity",
                    "VoxelSpacingEntity",
                ],
            }
        },
    )


class AnnotationSource(ConfiguredBaseModel):
    """
    An annotation source.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    InstanceSegmentation: Optional[AnnotationInstanceSegmentationFile] = Field(
        None,
        description="""File and sourcing data for an instance segmentation annotation. Annotation that identifies individual instances of object shapes.""",
        json_schema_extra={"linkml_meta": {"alias": "InstanceSegmentation", "domain_of": ["AnnotationSource"]}},
    )
    OrientedPoint: Optional[AnnotationOrientedPointFile] = Field(
        None,
        description="""File and sourcing data for an oriented point annotation. Annotation that identifies points along with orientation in the volume.""",
        json_schema_extra={"linkml_meta": {"alias": "OrientedPoint", "domain_of": ["AnnotationSource"]}},
    )
    Point: Optional[AnnotationPointFile] = Field(
        None,
        description="""File and sourcing data for a point annotation. Annotation that identifies points in the volume.""",
        json_schema_extra={"linkml_meta": {"alias": "Point", "domain_of": ["AnnotationSource"]}},
    )
    SegmentationMask: Optional[AnnotationSegmentationMaskFile] = Field(
        None,
        description="""File and sourcing data for a segmentation mask annotation. Annotation that identifies an object.""",
        json_schema_extra={"linkml_meta": {"alias": "SegmentationMask", "domain_of": ["AnnotationSource"]}},
    )
    SemanticSegmentationMask: Optional[AnnotationSemanticSegmentationMaskFile] = Field(
        None,
        description="""File and sourcing data for a semantic segmentation mask annotation. Annotation that identifies classes of objects.""",
        json_schema_extra={"linkml_meta": {"alias": "SemanticSegmentationMask", "domain_of": ["AnnotationSource"]}},
    )
    parent_filters: Optional[SourceParentFilters] = Field(
        None,
        description="""Filters for the parent of a source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "parent_filters",
                "domain_of": [
                    "SourceParentFiltersEntity",
                    "AnnotationSource",
                    "DatasetKeyPhotoSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                    "VoxelSpacingSource",
                ],
            }
        },
    )


class DatasetEntity(ConfiguredBaseModel):
    """
    A dataset entity.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    metadata: Dataset = Field(
        ...,
        description="""High-level description of a cryoET dataset.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "metadata",
                "domain_of": ["AnnotationEntity", "DatasetEntity", "TiltSeriesEntity", "TomogramEntity"],
            }
        },
    )
    sources: List[DatasetSource] = Field(
        ...,
        description="""A dataset source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "sources",
                "domain_of": [
                    "AnnotationEntity",
                    "DatasetEntity",
                    "DatasetKeyPhotoEntity",
                    "FrameEntity",
                    "GainEntity",
                    "KeyImageEntity",
                    "RawTiltEntity",
                    "RunEntity",
                    "TiltSeriesEntity",
                    "TomogramEntity",
                    "VoxelSpacingEntity",
                ],
            }
        },
    )


class DatasetSource(DefaultLiteralEntity, DefaultSource):
    """
    A dataset source.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "cdp-dataset-config", "mixins": ["DefaultSource", "DefaultLiteralEntity"]}
    )

    destination_glob: Optional[DestinationGlob] = Field(
        None,
        description="""A glob class for finding files in the output / destination directory.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "destination_glob",
                "domain_of": [
                    "DefaultSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    source_glob: Optional[SourceGlob] = Field(
        None,
        description="""A glob class for finding files in the source directory.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "source_glob",
                "domain_of": [
                    "DefaultSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    source_multi_glob: Optional[SourceMultiGlob] = Field(
        None,
        description="""A glob class for finding files in the source directory (with multiple globs).""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "source_multi_glob",
                "domain_of": [
                    "DefaultSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    literal: Optional[DefaultLiteral] = Field(
        None,
        description="""A literal class with a value attribute.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "literal",
                "domain_of": [
                    "DefaultLiteralEntity",
                    "DatasetKeyPhotoSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )


class DatasetKeyPhotoEntity(ConfiguredBaseModel):
    """
    A dataset key photo entity.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    sources: List[DatasetKeyPhotoSource] = Field(
        ...,
        description="""A dataset key photo source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "sources",
                "domain_of": [
                    "AnnotationEntity",
                    "DatasetEntity",
                    "DatasetKeyPhotoEntity",
                    "FrameEntity",
                    "GainEntity",
                    "KeyImageEntity",
                    "RawTiltEntity",
                    "RunEntity",
                    "TiltSeriesEntity",
                    "TomogramEntity",
                    "VoxelSpacingEntity",
                ],
            }
        },
    )


class DatasetKeyPhotoSource(SourceParentFiltersEntity):
    """
    A dataset key photo source.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "cdp-dataset-config", "mixins": ["SourceParentFiltersEntity"]}
    )

    literal: Optional[DatasetKeyPhotoLiteral] = Field(
        None,
        description="""A literal for a dataset key photo.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "literal",
                "domain_of": [
                    "DefaultLiteralEntity",
                    "DatasetKeyPhotoSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    parent_filters: Optional[SourceParentFilters] = Field(
        None,
        description="""Filters for the parent of a source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "parent_filters",
                "domain_of": [
                    "SourceParentFiltersEntity",
                    "AnnotationSource",
                    "DatasetKeyPhotoSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                    "VoxelSpacingSource",
                ],
            }
        },
    )


class DatasetKeyPhotoLiteral(ConfiguredBaseModel):
    """
    A literal for a dataset key photo.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    value: PicturePath = Field(
        ...,
        description="""A set of paths to representative images of a piece of data.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "value",
                "domain_of": ["DefaultLiteral", "DatasetKeyPhotoLiteral", "VoxelSpacingLiteral"],
            }
        },
    )


class FrameEntity(ConfiguredBaseModel):
    """
    A frame entity.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    sources: List[FrameSource] = Field(
        ...,
        description="""A frame source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "sources",
                "domain_of": [
                    "AnnotationEntity",
                    "DatasetEntity",
                    "DatasetKeyPhotoEntity",
                    "FrameEntity",
                    "GainEntity",
                    "KeyImageEntity",
                    "RawTiltEntity",
                    "RunEntity",
                    "TiltSeriesEntity",
                    "TomogramEntity",
                    "VoxelSpacingEntity",
                ],
            }
        },
    )


class FrameSource(DefaultLiteralEntity, SourceParentFiltersEntity, DefaultSource):
    """
    A frame source.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "cdp-dataset-config",
            "mixins": ["DefaultSource", "DefaultLiteralEntity", "SourceParentFiltersEntity"],
        }
    )

    destination_glob: Optional[DestinationGlob] = Field(
        None,
        description="""A glob class for finding files in the output / destination directory.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "destination_glob",
                "domain_of": [
                    "DefaultSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    source_glob: Optional[SourceGlob] = Field(
        None,
        description="""A glob class for finding files in the source directory.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "source_glob",
                "domain_of": [
                    "DefaultSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    source_multi_glob: Optional[SourceMultiGlob] = Field(
        None,
        description="""A glob class for finding files in the source directory (with multiple globs).""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "source_multi_glob",
                "domain_of": [
                    "DefaultSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    literal: Optional[DefaultLiteral] = Field(
        None,
        description="""A literal class with a value attribute.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "literal",
                "domain_of": [
                    "DefaultLiteralEntity",
                    "DatasetKeyPhotoSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    parent_filters: Optional[SourceParentFilters] = Field(
        None,
        description="""Filters for the parent of a source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "parent_filters",
                "domain_of": [
                    "SourceParentFiltersEntity",
                    "AnnotationSource",
                    "DatasetKeyPhotoSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                    "VoxelSpacingSource",
                ],
            }
        },
    )


class GainEntity(ConfiguredBaseModel):
    """
    A gain entity.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    sources: List[GainSource] = Field(
        ...,
        description="""A gain source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "sources",
                "domain_of": [
                    "AnnotationEntity",
                    "DatasetEntity",
                    "DatasetKeyPhotoEntity",
                    "FrameEntity",
                    "GainEntity",
                    "KeyImageEntity",
                    "RawTiltEntity",
                    "RunEntity",
                    "TiltSeriesEntity",
                    "TomogramEntity",
                    "VoxelSpacingEntity",
                ],
            }
        },
    )


class GainSource(DefaultLiteralEntity, SourceParentFiltersEntity, DefaultSource):
    """
    A gain source.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "cdp-dataset-config",
            "mixins": ["DefaultSource", "DefaultLiteralEntity", "SourceParentFiltersEntity"],
        }
    )

    destination_glob: Optional[DestinationGlob] = Field(
        None,
        description="""A glob class for finding files in the output / destination directory.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "destination_glob",
                "domain_of": [
                    "DefaultSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    source_glob: Optional[SourceGlob] = Field(
        None,
        description="""A glob class for finding files in the source directory.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "source_glob",
                "domain_of": [
                    "DefaultSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    source_multi_glob: Optional[SourceMultiGlob] = Field(
        None,
        description="""A glob class for finding files in the source directory (with multiple globs).""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "source_multi_glob",
                "domain_of": [
                    "DefaultSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    literal: Optional[DefaultLiteral] = Field(
        None,
        description="""A literal class with a value attribute.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "literal",
                "domain_of": [
                    "DefaultLiteralEntity",
                    "DatasetKeyPhotoSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    parent_filters: Optional[SourceParentFilters] = Field(
        None,
        description="""Filters for the parent of a source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "parent_filters",
                "domain_of": [
                    "SourceParentFiltersEntity",
                    "AnnotationSource",
                    "DatasetKeyPhotoSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                    "VoxelSpacingSource",
                ],
            }
        },
    )


class KeyImageEntity(ConfiguredBaseModel):
    """
    A key image entity.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    sources: List[KeyImageSource] = Field(
        ...,
        description="""A key image source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "sources",
                "domain_of": [
                    "AnnotationEntity",
                    "DatasetEntity",
                    "DatasetKeyPhotoEntity",
                    "FrameEntity",
                    "GainEntity",
                    "KeyImageEntity",
                    "RawTiltEntity",
                    "RunEntity",
                    "TiltSeriesEntity",
                    "TomogramEntity",
                    "VoxelSpacingEntity",
                ],
            }
        },
    )


class KeyImageSource(DefaultLiteralEntity, SourceParentFiltersEntity, DefaultSource):
    """
    A key image source.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "cdp-dataset-config",
            "mixins": ["DefaultSource", "DefaultLiteralEntity", "SourceParentFiltersEntity"],
        }
    )

    destination_glob: Optional[DestinationGlob] = Field(
        None,
        description="""A glob class for finding files in the output / destination directory.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "destination_glob",
                "domain_of": [
                    "DefaultSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    source_glob: Optional[SourceGlob] = Field(
        None,
        description="""A glob class for finding files in the source directory.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "source_glob",
                "domain_of": [
                    "DefaultSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    source_multi_glob: Optional[SourceMultiGlob] = Field(
        None,
        description="""A glob class for finding files in the source directory (with multiple globs).""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "source_multi_glob",
                "domain_of": [
                    "DefaultSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    literal: Optional[DefaultLiteral] = Field(
        None,
        description="""A literal class with a value attribute.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "literal",
                "domain_of": [
                    "DefaultLiteralEntity",
                    "DatasetKeyPhotoSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    parent_filters: Optional[SourceParentFilters] = Field(
        None,
        description="""Filters for the parent of a source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "parent_filters",
                "domain_of": [
                    "SourceParentFiltersEntity",
                    "AnnotationSource",
                    "DatasetKeyPhotoSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                    "VoxelSpacingSource",
                ],
            }
        },
    )


class RawTiltEntity(ConfiguredBaseModel):
    """
    A raw tilt entity.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    sources: List[RawTiltSource] = Field(
        ...,
        description="""A raw tilt source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "sources",
                "domain_of": [
                    "AnnotationEntity",
                    "DatasetEntity",
                    "DatasetKeyPhotoEntity",
                    "FrameEntity",
                    "GainEntity",
                    "KeyImageEntity",
                    "RawTiltEntity",
                    "RunEntity",
                    "TiltSeriesEntity",
                    "TomogramEntity",
                    "VoxelSpacingEntity",
                ],
            }
        },
    )


class RawTiltSource(DefaultLiteralEntity, SourceParentFiltersEntity, DefaultSource):
    """
    A raw tilt source.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "cdp-dataset-config",
            "mixins": ["DefaultSource", "DefaultLiteralEntity", "SourceParentFiltersEntity"],
        }
    )

    destination_glob: Optional[DestinationGlob] = Field(
        None,
        description="""A glob class for finding files in the output / destination directory.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "destination_glob",
                "domain_of": [
                    "DefaultSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    source_glob: Optional[SourceGlob] = Field(
        None,
        description="""A glob class for finding files in the source directory.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "source_glob",
                "domain_of": [
                    "DefaultSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    source_multi_glob: Optional[SourceMultiGlob] = Field(
        None,
        description="""A glob class for finding files in the source directory (with multiple globs).""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "source_multi_glob",
                "domain_of": [
                    "DefaultSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    literal: Optional[DefaultLiteral] = Field(
        None,
        description="""A literal class with a value attribute.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "literal",
                "domain_of": [
                    "DefaultLiteralEntity",
                    "DatasetKeyPhotoSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    parent_filters: Optional[SourceParentFilters] = Field(
        None,
        description="""Filters for the parent of a source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "parent_filters",
                "domain_of": [
                    "SourceParentFiltersEntity",
                    "AnnotationSource",
                    "DatasetKeyPhotoSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                    "VoxelSpacingSource",
                ],
            }
        },
    )


class RunEntity(ConfiguredBaseModel):
    """
    A run entity.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    sources: List[RunSource] = Field(
        ...,
        description="""A run source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "sources",
                "domain_of": [
                    "AnnotationEntity",
                    "DatasetEntity",
                    "DatasetKeyPhotoEntity",
                    "FrameEntity",
                    "GainEntity",
                    "KeyImageEntity",
                    "RawTiltEntity",
                    "RunEntity",
                    "TiltSeriesEntity",
                    "TomogramEntity",
                    "VoxelSpacingEntity",
                ],
            }
        },
    )


class RunSource(DefaultLiteralEntity, SourceParentFiltersEntity, DefaultSource):
    """
    A run source.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "cdp-dataset-config",
            "mixins": ["DefaultSource", "DefaultLiteralEntity", "SourceParentFiltersEntity"],
        }
    )

    destination_glob: Optional[DestinationGlob] = Field(
        None,
        description="""A glob class for finding files in the output / destination directory.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "destination_glob",
                "domain_of": [
                    "DefaultSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    source_glob: Optional[SourceGlob] = Field(
        None,
        description="""A glob class for finding files in the source directory.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "source_glob",
                "domain_of": [
                    "DefaultSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    source_multi_glob: Optional[SourceMultiGlob] = Field(
        None,
        description="""A glob class for finding files in the source directory (with multiple globs).""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "source_multi_glob",
                "domain_of": [
                    "DefaultSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    literal: Optional[DefaultLiteral] = Field(
        None,
        description="""A literal class with a value attribute.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "literal",
                "domain_of": [
                    "DefaultLiteralEntity",
                    "DatasetKeyPhotoSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    parent_filters: Optional[SourceParentFilters] = Field(
        None,
        description="""Filters for the parent of a source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "parent_filters",
                "domain_of": [
                    "SourceParentFiltersEntity",
                    "AnnotationSource",
                    "DatasetKeyPhotoSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                    "VoxelSpacingSource",
                ],
            }
        },
    )


class StandardizationConfig(ConfiguredBaseModel):
    """
    A standardization configuration.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    deposition_id: int = Field(
        ...,
        description="""The deposition ID.""",
        json_schema_extra={"linkml_meta": {"alias": "deposition_id", "domain_of": ["StandardizationConfig"]}},
    )
    run_data_map_file: Optional[str] = Field(
        None,
        description="""The run data map file.""",
        json_schema_extra={"linkml_meta": {"alias": "run_data_map_file", "domain_of": ["StandardizationConfig"]}},
    )
    run_to_frame_map_csv: Optional[str] = Field(
        None,
        description="""The run to frame map CSV.""",
        json_schema_extra={"linkml_meta": {"alias": "run_to_frame_map_csv", "domain_of": ["StandardizationConfig"]}},
    )
    run_to_tomo_map_csv: Optional[str] = Field(
        None,
        description="""The run to tomogram map CSV.""",
        json_schema_extra={"linkml_meta": {"alias": "run_to_tomo_map_csv", "domain_of": ["StandardizationConfig"]}},
    )
    run_to_ts_map_csv: Optional[str] = Field(
        None,
        description="""The run to tilt series map CSV.""",
        json_schema_extra={"linkml_meta": {"alias": "run_to_ts_map_csv", "domain_of": ["StandardizationConfig"]}},
    )
    source_prefix: str = Field(
        ...,
        description="""The source prefix of the input files.""",
        json_schema_extra={"linkml_meta": {"alias": "source_prefix", "domain_of": ["StandardizationConfig"]}},
    )


class TiltSeriesEntity(ConfiguredBaseModel):
    """
    A tilt series entity.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    metadata: TiltSeries = Field(
        ...,
        description="""Metadata describing a tilt series.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "metadata",
                "domain_of": ["AnnotationEntity", "DatasetEntity", "TiltSeriesEntity", "TomogramEntity"],
            }
        },
    )
    sources: List[TiltSeriesSource] = Field(
        ...,
        description="""A tilt series source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "sources",
                "domain_of": [
                    "AnnotationEntity",
                    "DatasetEntity",
                    "DatasetKeyPhotoEntity",
                    "FrameEntity",
                    "GainEntity",
                    "KeyImageEntity",
                    "RawTiltEntity",
                    "RunEntity",
                    "TiltSeriesEntity",
                    "TomogramEntity",
                    "VoxelSpacingEntity",
                ],
            }
        },
    )


class TiltSeriesSource(DefaultLiteralEntity, SourceParentFiltersEntity, DefaultSource):
    """
    A tilt series source.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "cdp-dataset-config",
            "mixins": ["DefaultSource", "DefaultLiteralEntity", "SourceParentFiltersEntity"],
        }
    )

    destination_glob: Optional[DestinationGlob] = Field(
        None,
        description="""A glob class for finding files in the output / destination directory.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "destination_glob",
                "domain_of": [
                    "DefaultSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    source_glob: Optional[SourceGlob] = Field(
        None,
        description="""A glob class for finding files in the source directory.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "source_glob",
                "domain_of": [
                    "DefaultSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    source_multi_glob: Optional[SourceMultiGlob] = Field(
        None,
        description="""A glob class for finding files in the source directory (with multiple globs).""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "source_multi_glob",
                "domain_of": [
                    "DefaultSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    literal: Optional[DefaultLiteral] = Field(
        None,
        description="""A literal class with a value attribute.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "literal",
                "domain_of": [
                    "DefaultLiteralEntity",
                    "DatasetKeyPhotoSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    parent_filters: Optional[SourceParentFilters] = Field(
        None,
        description="""Filters for the parent of a source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "parent_filters",
                "domain_of": [
                    "SourceParentFiltersEntity",
                    "AnnotationSource",
                    "DatasetKeyPhotoSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                    "VoxelSpacingSource",
                ],
            }
        },
    )


class TomogramEntity(ConfiguredBaseModel):
    """
    A tomogram entity.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    metadata: Tomogram = Field(
        ...,
        description="""Metadata describing a tomogram.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "metadata",
                "domain_of": ["AnnotationEntity", "DatasetEntity", "TiltSeriesEntity", "TomogramEntity"],
            }
        },
    )
    sources: List[TomogramSource] = Field(
        ...,
        description="""A tomogram source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "sources",
                "domain_of": [
                    "AnnotationEntity",
                    "DatasetEntity",
                    "DatasetKeyPhotoEntity",
                    "FrameEntity",
                    "GainEntity",
                    "KeyImageEntity",
                    "RawTiltEntity",
                    "RunEntity",
                    "TiltSeriesEntity",
                    "TomogramEntity",
                    "VoxelSpacingEntity",
                ],
            }
        },
    )


class TomogramSource(DefaultLiteralEntity, SourceParentFiltersEntity, DefaultSource):
    """
    A tomogram source.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "cdp-dataset-config",
            "mixins": ["DefaultSource", "DefaultLiteralEntity", "SourceParentFiltersEntity"],
        }
    )

    destination_glob: Optional[DestinationGlob] = Field(
        None,
        description="""A glob class for finding files in the output / destination directory.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "destination_glob",
                "domain_of": [
                    "DefaultSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    source_glob: Optional[SourceGlob] = Field(
        None,
        description="""A glob class for finding files in the source directory.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "source_glob",
                "domain_of": [
                    "DefaultSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    source_multi_glob: Optional[SourceMultiGlob] = Field(
        None,
        description="""A glob class for finding files in the source directory (with multiple globs).""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "source_multi_glob",
                "domain_of": [
                    "DefaultSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    literal: Optional[DefaultLiteral] = Field(
        None,
        description="""A literal class with a value attribute.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "literal",
                "domain_of": [
                    "DefaultLiteralEntity",
                    "DatasetKeyPhotoSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    parent_filters: Optional[SourceParentFilters] = Field(
        None,
        description="""Filters for the parent of a source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "parent_filters",
                "domain_of": [
                    "SourceParentFiltersEntity",
                    "AnnotationSource",
                    "DatasetKeyPhotoSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                    "VoxelSpacingSource",
                ],
            }
        },
    )


class VoxelSpacingEntity(ConfiguredBaseModel):
    """
    A voxel spacing entity.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    sources: List[VoxelSpacingSource] = Field(
        ...,
        description="""A voxel spacing source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "sources",
                "domain_of": [
                    "AnnotationEntity",
                    "DatasetEntity",
                    "DatasetKeyPhotoEntity",
                    "FrameEntity",
                    "GainEntity",
                    "KeyImageEntity",
                    "RawTiltEntity",
                    "RunEntity",
                    "TiltSeriesEntity",
                    "TomogramEntity",
                    "VoxelSpacingEntity",
                ],
            }
        },
    )


class VoxelSpacingSource(SourceParentFiltersEntity):
    """
    A voxel spacing source.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "cdp-dataset-config", "mixins": ["SourceParentFiltersEntity"]}
    )

    destination_glob: Optional[DestinationGlob] = Field(
        None,
        description="""A glob class for finding files in the output / destination directory.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "destination_glob",
                "domain_of": [
                    "DefaultSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    source_glob: Optional[SourceGlob] = Field(
        None,
        description="""A glob class for finding files in the source directory.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "source_glob",
                "domain_of": [
                    "DefaultSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    literal: Optional[VoxelSpacingLiteral] = Field(
        None,
        description="""A literal for a voxel spacing.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "literal",
                "domain_of": [
                    "DefaultLiteralEntity",
                    "DatasetKeyPhotoSource",
                    "VoxelSpacingSource",
                    "DatasetSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                ],
            }
        },
    )
    tomogram_header: Optional[TomogramHeader] = Field(
        None,
        description="""A tomogram header, a unique source attribute for voxel spacing.""",
        json_schema_extra={"linkml_meta": {"alias": "tomogram_header", "domain_of": ["VoxelSpacingSource"]}},
    )
    parent_filters: Optional[SourceParentFilters] = Field(
        None,
        description="""Filters for the parent of a source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "parent_filters",
                "domain_of": [
                    "SourceParentFiltersEntity",
                    "AnnotationSource",
                    "DatasetKeyPhotoSource",
                    "FrameSource",
                    "GainSource",
                    "KeyImageSource",
                    "RawTiltSource",
                    "RunSource",
                    "TiltSeriesSource",
                    "TomogramSource",
                    "VoxelSpacingSource",
                ],
            }
        },
    )


class VoxelSpacingLiteral(ConfiguredBaseModel):
    """
    A literal for a voxel spacing.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    value: List[float] = Field(
        ...,
        description="""The value for the voxel spacing literal.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "value",
                "domain_of": ["DefaultLiteral", "DatasetKeyPhotoLiteral", "VoxelSpacingLiteral"],
            }
        },
    )


class TomogramHeader(ConfiguredBaseModel):
    """
    A tomogram header, a unique source attribute for voxel spacing.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "cdp-dataset-config"})

    list_glob: str = Field(
        ...,
        description="""The glob for the tomogram header file.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "list_glob",
                "domain_of": ["GeneralGlob", "TomogramHeader", "DestinationGlob", "SourceGlob"],
            }
        },
    )
    match_regex: Optional[str] = Field(
        ".*",
        description="""The regex for the tomogram header file.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "match_regex",
                "domain_of": ["GeneralGlob", "TomogramHeader", "DestinationGlob", "SourceGlob"],
                "ifabsent": "string(.*)",
            }
        },
    )
    header_key: Optional[str] = Field(
        "voxel_size",
        description="""The key in the header file for the voxel spacing.""",
        json_schema_extra={
            "linkml_meta": {"alias": "header_key", "domain_of": ["TomogramHeader"], "ifabsent": "string(voxel_size)"}
        },
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
AnnotationMethodLinks.model_rebuild()
Container.model_rebuild()
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
