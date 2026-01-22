from __future__ import annotations

import re
import sys
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Any, ClassVar, Literal, Optional, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    conlist,
    field_validator,
    model_serializer,
)


metamodel_version = "None"
version = "1.1.0"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias=True,
        validate_by_name=True,
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
        arbitrary_types_allowed=True,
        use_enum_values=True,
        strict=False,
    )

    @model_serializer(mode="wrap", when_used="unless-none")
    def treat_empty_lists_as_none(
        self, handler: SerializerFunctionWrapHandler, info: SerializationInfo
    ) -> dict[str, Any]:
        if info.exclude_none:
            _instance = self.model_copy()
            for field, field_info in type(_instance).model_fields.items():
                if getattr(_instance, field) == [] and not (field_info.is_required()):
                    setattr(_instance, field, None)
        else:
            _instance = self
        return handler(_instance, info)


class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
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
        "default_prefix": "cdp-meta",
        "default_range": "Any",
        "id": "metadata",
        "imports": ["linkml:types"],
        "name": "cdp-meta",
        "prefixes": {
            "CL": {"prefix_prefix": "CL", "prefix_reference": "http://purl.obolibrary.org/obo/CL_"},
            "GO": {"prefix_prefix": "GO", "prefix_reference": "http://purl.obolibrary.org/obo/GO_"},
            "ORCID": {"prefix_prefix": "ORCID", "prefix_reference": "https://orcid.org/"},
            "ROR": {"prefix_prefix": "ROR", "prefix_reference": "https://ror.org/"},
            "UBERON": {"prefix_prefix": "UBERON", "prefix_reference": "http://purl.obolibrary.org/obo/UBERON_"},
            "cdp-meta": {"prefix_prefix": "cdp-meta", "prefix_reference": "metadata"},
            "linkml": {"prefix_prefix": "linkml", "prefix_reference": "https://w3id.org/linkml/"},
        },
        "source_file": "core/v2.0.0/codegen/metadata_materialized.yaml",
        "types": {
            "BTO_ID": {
                "base": "str",
                "description": "A BRENDA Tissue Ontology identifier",
                "from_schema": "metadata",
                "name": "BTO_ID",
                "pattern": "^BTO:[0-9]{7}$",
            },
            "CC_ID": {
                "base": "str",
                "description": "A Cell Culture Collection identifier",
                "from_schema": "metadata",
                "name": "CC_ID",
                "pattern": "^CC-[0-9]{4}$",
            },
            "CHEBI_ID": {
                "base": "str",
                "description": "A Chemical Entities of Biological " "Interest ontology identifier",
                "from_schema": "metadata",
                "name": "CHEBI_ID",
                "pattern": "^CHEBI:[0-9]+$",
            },
            "CL_ID": {
                "base": "str",
                "description": "A Cell Ontology identifier",
                "from_schema": "metadata",
                "name": "CL_ID",
                "pattern": "^CL:[0-9]{7}$",
            },
            "CVCL_ID": {
                "base": "str",
                "description": "A Cellosaurus identifier",
                "from_schema": "metadata",
                "name": "CVCL_ID",
                "pattern": "^CVCL_[A-Z0-9]{4,}$",
            },
            "DOI": {
                "base": "str",
                "description": "A Digital Object Identifier",
                "from_schema": "metadata",
                "name": "DOI",
                "pattern": "^(doi:)?10\\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+$",
            },
            "DOI_LIST": {
                "base": "str",
                "description": "A list of Digital Object Identifiers",
                "from_schema": "metadata",
                "name": "DOI_LIST",
                "pattern": "^(doi:)?10\\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+(\\s*,\\s*(doi:)?10\\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)*$",
            },
            "EFO_ID": {
                "base": "str",
                "description": "An Experimental Factor Ontology " "identifier",
                "from_schema": "metadata",
                "name": "EFO_ID",
                "pattern": "^EFO:[0-9]{7}$",
            },
            "EMDB_ID": {
                "base": "str",
                "description": "An Electron Microscopy Data Bank " "identifier",
                "from_schema": "metadata",
                "name": "EMDB_ID",
                "pattern": "^EMD-[0-9]{4,5}$",
            },
            "EMPIAR_EMDB_DOI_PDB_LIST": {
                "base": "str",
                "description": "A list of EMPIAR, " "EMDB, DOI, and PDB " "identifiers",
                "from_schema": "metadata",
                "name": "EMPIAR_EMDB_DOI_PDB_LIST",
                "pattern": "^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|(doi:)?10\\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+|PDB-[0-9a-zA-Z]{4,8})(\\s*,\\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|(doi:)?10\\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+|PDB-[0-9a-zA-Z]{4,8}))*$",
            },
            "EMPIAR_EMDB_PDB_LIST": {
                "base": "str",
                "description": "A list of EMPIAR, EMDB, " "and PDB identifiers",
                "from_schema": "metadata",
                "name": "EMPIAR_EMDB_PDB_LIST",
                "pattern": "^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|PDB-[0-9a-zA-Z]{4,8})(\\s*,\\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|PDB-[0-9a-zA-Z]{4,8}))*$",
            },
            "EMPIAR_ID": {
                "base": "str",
                "description": "An Electron Microscopy Public Image " "Archive identifier",
                "from_schema": "metadata",
                "name": "EMPIAR_ID",
                "pattern": "^EMPIAR-[0-9]+$",
            },
            "FBBT_ID": {
                "base": "str",
                "description": "A drosophila anatomy ontology " "identifier",
                "from_schema": "metadata",
                "name": "FBBT_ID",
                "pattern": "FBbt:[0-9]{8}$",
            },
            "FBDV_ID": {
                "base": "str",
                "description": "A drosophila developmental stage " "ontology identifier",
                "from_schema": "metadata",
                "name": "FBDV_ID",
                "pattern": "FBdv:[0-9]{8}$",
            },
            "FloatFormattedString": {
                "base": "str",
                "description": "A formatted string that " "represents a floating " "point number.",
                "from_schema": "metadata",
                "name": "FloatFormattedString",
                "pattern": "^float[ " "]*\\{[a-zA-Z0-9_-]+\\}[ ]*$",
            },
            "GO_ID": {
                "base": "str",
                "description": "A Gene Ontology identifier",
                "from_schema": "metadata",
                "name": "GO_ID",
                "pattern": "^GO:[0-9]{7}$",
            },
            "HSAPDV_ID": {
                "base": "str",
                "description": "A human developmental phenotype " "ontology identifier",
                "from_schema": "metadata",
                "name": "HSAPDV_ID",
                "pattern": "HsapDv:[0-9]{7}$",
            },
            "IntegerFormattedString": {
                "base": "str",
                "description": "A formatted string that " "represents an integer.",
                "from_schema": "metadata",
                "name": "IntegerFormattedString",
                "pattern": "^int[ " "]*\\{[a-zA-Z0-9_-]+\\}[ ]*$",
            },
            "MMUSDV_ID": {
                "base": "str",
                "description": "A mouse developmental stage ontology " "identifier",
                "from_schema": "metadata",
                "name": "MMUSDV_ID",
                "pattern": "MmusDv:[0-9]{7}$",
            },
            "MONDO_ID": {
                "base": "str",
                "description": "An identifier of type MONDO",
                "from_schema": "metadata",
                "name": "MONDO_ID",
                "pattern": "^MONDO:[0-9]{7}$",
            },
            "NCBI_TAXON_ID": {
                "base": "str",
                "description": "A NCBI Taxonomy identifier",
                "from_schema": "metadata",
                "name": "NCBI_TAXON_ID",
                "pattern": "^NCBITaxon:[0-9]+$",
            },
            "ONTOLOGY_ID": {
                "base": "str",
                "description": "An ontology identifier",
                "from_schema": "metadata",
                "name": "ONTOLOGY_ID",
                "pattern": "^[a-zA-Z]+:[0-9]+$",
            },
            "ORCID": {
                "base": "str",
                "description": "A unique, persistent identifier for " "researchers, provided by ORCID.",
                "from_schema": "metadata",
                "name": "ORCID",
                "pattern": "[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$",
            },
            "PATO_ID": {
                "base": "str",
                "description": "An identifier of type PATO",
                "from_schema": "metadata",
                "name": "PATO_ID",
                "pattern": "^PATO:[0-9]{7}$",
            },
            "PDB_ID": {
                "base": "str",
                "description": "A Protein Data Bank identifier",
                "from_schema": "metadata",
                "name": "PDB_ID",
                "pattern": "^PDB-[0-9a-zA-Z]{4,8}$",
            },
            "StringFormattedString": {
                "base": "str",
                "description": "A formatted string " "(variable) that " "represents a string.",
                "from_schema": "metadata",
                "name": "StringFormattedString",
                "pattern": "^[ ]*\\{[a-zA-Z0-9_-]+\\}[ " "]*$",
            },
            "UBERON_ID": {
                "base": "str",
                "description": "An UBERON identifier",
                "from_schema": "metadata",
                "name": "UBERON_ID",
                "pattern": "^UBERON:[0-9]{7}$",
            },
            "UNIPROT_ID": {
                "base": "str",
                "description": "A UniProt identifier",
                "from_schema": "metadata",
                "name": "UNIPROT_ID",
                "pattern": "^UniProtKB:[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}$",
            },
            "UNKNOWN_LITERAL": {
                "base": "str",
                "description": "A placeholder for an unknown " "value.",
                "from_schema": "metadata",
                "name": "UNKNOWN_LITERAL",
                "pattern": "^unknown$",
            },
            "URLorS3URI": {
                "base": "str",
                "description": "A URL or S3 URI",
                "from_schema": "metadata",
                "name": "URLorS3URI",
                "pattern": "^(((https?|s3)://)|cryoetportal-rawdatasets-dev).*$",
            },
            "VersionString": {
                "base": "float",
                "description": "A version number (only major, " "minor versions)",
                "from_schema": "metadata",
                "minimum_value": 0,
                "name": "VersionString",
            },
            "WBBT_ID": {
                "base": "str",
                "description": "A WormBase anatomy ontology identifier",
                "from_schema": "metadata",
                "name": "WBBT_ID",
                "pattern": "WBbt:[0-9]{7}$",
            },
            "WORMBASE_DEVELOPMENT_ID": {
                "base": "str",
                "description": "A WormBase " "developmental stage " "identifier",
                "from_schema": "metadata",
                "name": "WORMBASE_DEVELOPMENT_ID",
                "pattern": "WBls:[0-9]{7}$",
            },
            "WORMBASE_STRAIN_ID": {
                "base": "str",
                "description": "A WormBase strain identifier",
                "from_schema": "metadata",
                "name": "WORMBASE_STRAIN_ID",
                "pattern": "WBStrain[0-9]{8}$",
            },
            "ZFA_ID": {
                "base": "str",
                "description": "A zebrafish anatomy ontology identifier",
                "from_schema": "metadata",
                "name": "ZFA_ID",
                "pattern": "ZFA:[0-9]{7}$",
            },
            "ZFS_ID": {
                "base": "str",
                "description": "A zebrafish developmental stage ontology " "identifier",
                "from_schema": "metadata",
                "name": "ZFS_ID",
                "pattern": "ZFS:[0-9]{7}$",
            },
            "boolean": {
                "base": "Bool",
                "description": "A binary (true or false) value",
                "exact_mappings": ["schema:Boolean"],
                "from_schema": "metadata",
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
                "from_schema": "metadata",
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
                "from_schema": "metadata",
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
                "from_schema": "metadata",
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
                "from_schema": "metadata",
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
                "from_schema": "metadata",
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
                "from_schema": "metadata",
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
                "from_schema": "metadata",
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
                "from_schema": "metadata",
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
                "from_schema": "metadata",
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
                "from_schema": "metadata",
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
                "from_schema": "metadata",
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
                "from_schema": "metadata",
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
                "from_schema": "metadata",
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
                "from_schema": "metadata",
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
                "from_schema": "metadata",
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
                "from_schema": "metadata",
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
                "from_schema": "metadata",
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
                "from_schema": "metadata",
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


class AlignmentTypeEnum(str, Enum):
    """
    Type of alignment
    """

    LOCAL = "LOCAL"
    """
    per-section non-rigid alignment available
    """
    GLOBAL = "GLOBAL"
    """
    only per-section rigid alignment available
    """


class AlignmentFormatEnum(str, Enum):
    """
    Used to determine what alignment alogrithm to use.
    """

    IMOD = "IMOD"
    """
    formats (xf, tlt, com)
    """
    ARETOMO3 = "ARETOMO3"
    """
    formats (aln)
    """


class AlignmentMethodTypeEnum(str, Enum):
    """
    Used to determine how the alignment was done.
    """

    fiducial_based = "fiducial_based"
    """
    alignment was done based on fiducial markers
    """
    patch_tracking = "patch_tracking"
    """
    alignment was done based on patch tracking
    """
    projection_matching = "projection_matching"
    """
    alignment was done based on image projection
    """
    undefined = "undefined"
    """
    how alignment was done is unknown
    """


class AnnotationFileSourceEnum(str, Enum):
    """
    How the annotation file was acquired
    """

    dataset_author = "dataset_author"
    """
    Annotation submitted by dataset author
    """
    community = "community"
    """
    Annotation submitted by community member
    """
    portal_standard = "portal_standard"
    """
    Annotation submitted by portal standardization
    """


class AnnotationMethodTypeEnum(str, Enum):
    """
    Describes how the annotations were generated.
    """

    manual = "manual"
    """
    Annotations were generated manually.
    """
    automated = "automated"
    """
    Annotations were generated using automated tools or algorithms without supervision.
    """
    hybrid = "hybrid"
    """
    Annotations were generated using a combination of automated and manual methods.
    """
    simulated = "simulated"
    """
    Annotations were generated by simulation tools or algorithms.
    """


class AnnotationFileShapeTypeEnum(str, Enum):
    """
    Describes the shape of the annotation
    """

    SegmentationMask = "SegmentationMask"
    """
    A binary mask volume
    """
    OrientedPoint = "OrientedPoint"
    """
    A series of coordinates and an orientation
    """
    Point = "Point"
    """
    A series of coordinates
    """
    InstanceSegmentation = "InstanceSegmentation"
    """
    A volume with labels for multiple instances
    """


class PointAnnotationFileFormatEnum(str, Enum):
    """
    Describes the format of the point annotation file
    """

    csv = "csv"
    csv_with_header = "csv_with_header"
    tsv = "tsv"
    mod = "mod"
    relion3_star = "relion3_star"
    relion4_star = "relion4_star"
    tomoman_relion_star = "tomoman_relion_star"
    copick = "copick"


class OrientedPointAnnotationFileFormatEnum(str, Enum):
    """
    Describes the format of the oriented point annotation file
    """

    mod = "mod"
    relion3_star = "relion3_star"
    relion4_star = "relion4_star"
    tomoman_relion_star = "tomoman_relion_star"
    copick = "copick"
    stopgap_star = "stopgap_star"


class InstanceSegmentationAnnotationFileFormatEnum(str, Enum):
    """
    Describes the format of an instance segmentation annotation file
    """

    tardis = "tardis"
    copick = "copick"


class VolumeAnnotationFileFormatEnum(str, Enum):
    """
    Describes the format of a volume (semantic / semantic segmentation) annotation file
    """

    mrc = "mrc"
    zarr = "zarr"


class TriangularMeshAnnotationFileFormatEnum(str, Enum):
    """
    Describes the format of a triangular mesh annotation file
    """

    obj = "obj"
    stl = "stl"
    vtk = "vtk"
    glb = "glb"


class TriangularMeshAnnotationGroupFileFormatEnum(str, Enum):
    """
    Describes the format of a triangular mesh group annotation file
    """

    hff = "hff"


class AnnotationMethodLinkTypeEnum(str, Enum):
    """
    Describes the type of link associated to the annotation method.
    """

    documentation = "documentation"
    """
    Links to the documentation related to the method.
    """
    models_weights = "models_weights"
    """
    Links to the weights that the models used for generating annotations were trained with.
    """
    other = "other"
    """
    Link to resources that does not fit in the other categories.
    """
    source_code = "source_code"
    """
    Links to the source code of the method.
    """
    website = "website"
    """
    Links to a website of the method or tool used to generate the annotation.
    """


class CtfFormatEnum(str, Enum):
    """
    Used to determine what ctf parser to use.
    """

    CTFFIND = "CTFFIND"
    """
    The file has ctffind schema
    """
    Gctf = "Gctf"
    """
    The file has Gctf schema
    """
    IMOD = "IMOD"
    """
    The file has IMOD schema
    """


class DepositionTypesEnum(str, Enum):
    """
    Types of data a deposition has
    """

    annotation = "annotation"
    """
    The deposition comprises of new annotations for existing datasets
    """
    dataset = "dataset"
    """
    The deposition comprises of new dataset(s).
    """
    tomogram = "tomogram"
    """
    The deposition comprises of new tomograms for existing datasets
    """


class SampleTypeEnum(str, Enum):
    """
    Type of sample imaged in a CryoET study.
    """

    cell_line = "cell_line"
    """
    Tomographic data of immortalized cells or immortalized cell sections
    """
    in_silico = "in_silico"
    """
    Simulated tomographic data.
    """
    in_vitro = "in_vitro"
    """
    Tomographic data of in vitro reconstituted systems or mixtures of proteins.
    """
    organelle = "organelle"
    """
    Tomographic data of purified organelles.
    """
    organism = "organism"
    """
    Tomographic data of sections through multicellular organisms.
    """
    organoid = "organoid"
    """
    Tomographic data of organoid-derived samples.
    """
    other = "other"
    """
    Other type of sample.
    """
    primary_cell_culture = "primary_cell_culture"
    """
    Tomographic data of whole primary cells or primary cell sections.
    """
    tissue = "tissue"
    """
    Tomographic data of tissue sections.
    """
    virus = "virus"
    """
    Tomographic data of purified viruses or VLPs.
    """


class TiltseriesCameraAcquireModeEnum(str, Enum):
    """
    Camera acquisition mode
    """

    counting = "counting"
    """
    Counting mode
    """
    superresolution = "superresolution"
    """
    Super-resolution mode
    """
    linear = "linear"
    """
    Linear mode
    """
    cds = "cds"
    """
    Correlated double sampling mode
    """


class TiltseriesCameraManufacturerEnum(str, Enum):
    """
    Camera manufacturer
    """

    Gatan = "Gatan"
    """
    Gatan Inc.
    """
    FEI = "FEI"
    """
    FEI Company
    """
    TFS = "TFS"
    """
    Thermo Fisher Scientific
    """
    simulated = "simulated"
    """
    Simulated data
    """


class TiltseriesCameraModelFeiTfsEnum(str, Enum):
    """
    Camera model for FEI / TFS cameras
    """

    FALCON_IV = "FALCON IV"
    """
    FALCON IV
    """
    FALCON_4i = "FALCON 4i"
    """
    FALCON 4i
    """


class TiltseriesCameraModelGatanEnum(str, Enum):
    """
    Camera model for Gatan cameras
    """

    K2 = "K2"
    """
    K2
    """
    K2_SUMMIT = "K2 SUMMIT"
    """
    K2 SUMMIT
    """
    K3 = "K3"
    """
    K3
    """
    K3_BIOQUANTUM = "K3 BIOQUANTUM"
    """
    K3 BIOQUANTUM
    """
    UltraCam = "UltraCam"
    """
    UltraCam
    """
    UltraScan = "UltraScan"
    """
    UltraScan
    """


class TiltseriesCameraModelSimulatedEnum(str, Enum):
    """
    Camera model for simulated cameras
    """

    simulated = "simulated"
    """
    Simulated camera model
    """


class TiltseriesMicroscopeManufacturerEnum(str, Enum):
    """
    Microscope manufacturer
    """

    FEI = "FEI"
    """
    FEI Company
    """
    TFS = "TFS"
    """
    Thermo Fisher Scientific
    """
    JEOL = "JEOL"
    """
    JEOL Ltd.
    """
    SIMULATED = "SIMULATED"
    """
    Simulated data
    """


class FiducialAlignmentStatusEnum(str, Enum):
    """
    Fiducial Alignment method
    """

    FIDUCIAL = "FIDUCIAL"
    """
    Alignment computed based on fiducial markers
    """
    NON_FIDUCIAL = "NON_FIDUCIAL"
    """
    Alignment computed without fiducial markers
    """


class TomogramProcessingEnum(str, Enum):
    """
    Tomogram processing method
    """

    denoised = "denoised"
    """
    Tomogram was denoised
    """
    filtered = "filtered"
    """
    Tomogram was filtered
    """
    raw = "raw"
    """
    Tomogram was not processed
    """


class TomogramReconstructionMethodEnum(str, Enum):
    """
    Tomogram reconstruction method
    """

    SART = "SART"
    """
    Simultaneous Algebraic Reconstruction Technique
    """
    Fourier_Space = "Fourier Space"
    """
    Fourier space reconstruction
    """
    SIRT = "SIRT"
    """
    Simultaneous Iterative Reconstruction Technique
    """
    WBP = "WBP"
    """
    Weighted Back-Projection
    """
    Unknown = "Unknown"
    """
    Unknown reconstruction method
    """


class TomogramTypeEnum(str, Enum):
    """
    Tomogram type
    """

    CANONICAL = "CANONICAL"
    """
    Canonical tomogram (basis geometry for all annotations)
    """
    UNKNOWN = "UNKNOWN"
    """
    Tomogram's was not submitted by the dataset author
    """


class PicturePath(ConfiguredBaseModel):
    """
    A set of paths to representative images of a piece of data.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    snapshot: Optional[str] = Field(
        default=None,
        description="""Path to the dataset preview image relative to the dataset directory root.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["PicturePath", "MetadataPicturePath"],
                "exact_mappings": ["cdp-common:snapshot"],
                "recommended": True,
            }
        },
    )
    thumbnail: Optional[str] = Field(
        default=None,
        description="""Path to the thumbnail of preview image relative to the dataset directory root.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["PicturePath", "MetadataPicturePath"],
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
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid snapshot format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid snapshot format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("thumbnail")
    def pattern_thumbnail(cls, v):
        pattern = re.compile(r"^(((https?|s3)://)|cryoetportal-rawdatasets-dev).*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid thumbnail format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid thumbnail format: {v}"
            raise ValueError(err_msg)
        return v


class MetadataPicturePath(ConfiguredBaseModel):
    """
    A set of paths to representative images of a piece of data for metadata files.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    snapshot: Optional[str] = Field(
        default=None,
        description="""Relative path (non-URL/URI) to the dataset preview image relative to the dataset directory root.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["PicturePath", "MetadataPicturePath"],
                "exact_mappings": ["cdp-common:metadata_snapshot"],
                "recommended": True,
            }
        },
    )
    thumbnail: Optional[str] = Field(
        default=None,
        description="""Relative path (non-URL/URI) to the thumbnail of preview image relative to the dataset directory root.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["PicturePath", "MetadataPicturePath"],
                "exact_mappings": ["cdp-common:metadata_thumbnail"],
                "recommended": True,
            }
        },
    )


class FundingDetails(ConfiguredBaseModel):
    """
    A funding source for a scientific data entity (base for JSON and DB representation).
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    funding_agency_name: Optional[str] = Field(
        default=None,
        description="""The name of the funding source.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["FundingDetails"],
                "exact_mappings": ["cdp-common:funding_agency_name"],
                "recommended": True,
            }
        },
    )
    grant_id: Optional[str] = Field(
        default=None,
        description="""Grant identifier provided by the funding agency""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["FundingDetails"],
                "exact_mappings": ["cdp-common:funding_grant_id"],
                "recommended": True,
            }
        },
    )


class DateStampedEntity(ConfiguredBaseModel):
    """
    An entity with associated deposition, release and last modified dates.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    dates: DateStamp = Field(
        default=...,
        description="""A set of dates at which a data item was deposited, published and last modified.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["DateStampedEntity", "Tomogram", "Dataset", "Deposition", "Annotation"]}
        },
    )


class AuthoredEntity(ConfiguredBaseModel):
    """
    An entity with associated authors.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    authors: list[Author] = Field(
        default=...,
        description="""Author of a scientific data entity.""",
        min_length=1,
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AuthoredEntity", "Dataset", "Deposition", "Tomogram", "Annotation"],
                "list_elements_ordered": True,
            }
        },
    )


class FundedEntity(ConfiguredBaseModel):
    """
    An entity with associated funding sources.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    funding: Optional[list[FundingDetails]] = Field(
        default=[],
        description="""A funding source for a scientific data entity (base for JSON and DB representation).""",
        json_schema_extra={
            "linkml_meta": {
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

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata", "mixin": True})

    cross_references: Optional[CrossReferences] = Field(
        default=None,
        description="""A set of cross-references to other databases and publications.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["CrossReferencedEntity", "Tomogram", "Dataset", "Deposition"]}
        },
    )


class PicturedEntity(ConfiguredBaseModel):
    """
    An entity with associated preview images.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    key_photos: PicturePath = Field(
        default=...,
        description="""A set of paths to representative images of a piece of data.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["PicturedEntity", "PicturedMetadataEntity"]}},
    )


class PicturedMetadataEntity(ConfiguredBaseModel):
    """
    An entity with associated preview images for metadata files.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    key_photos: MetadataPicturePath = Field(
        default=...,
        description="""A set of paths to representative images of a piece of data for metadata files.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["PicturedEntity", "PicturedMetadataEntity"]}},
    )


class Assay(ConfiguredBaseModel):
    """
    The assay that was used to create the dataset.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    name: str = Field(
        default=...,
        description="""Name of the assay component.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "Assay",
                    "DevelopmentStageDetails",
                    "Disease",
                    "OrganismDetails",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                    "AnnotationTriangularMeshGroupFile",
                    "AuthorMixin",
                    "Author",
                ],
                "exact_mappings": ["cdp-common:assay_name"],
            }
        },
    )
    id: Optional[str] = Field(
        default=None,
        description="""EFO ontology identifier for the type of assay performed in a CryoET dataset""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "Assay",
                    "DevelopmentStageDetails",
                    "Disease",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                ],
                "exact_mappings": ["cdp-common:assay_id"],
                "recommended": True,
            }
        },
    )

    @field_validator("id")
    def pattern_id(cls, v):
        pattern = re.compile(r"^EFO:[0-9]{7}$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v


class DevelopmentStageDetails(ConfiguredBaseModel):
    """
    The development stage of the patients or organisms from which assayed biosamples were derived.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    name: Optional[str] = Field(
        default=None,
        description="""Name of the developmental stage component.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "Assay",
                    "DevelopmentStageDetails",
                    "Disease",
                    "OrganismDetails",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                    "AnnotationTriangularMeshGroupFile",
                    "AuthorMixin",
                    "Author",
                ],
                "exact_mappings": ["cdp-common:development_stage_name"],
                "recommended": True,
            }
        },
    )
    id: Optional[str] = Field(
        default=None,
        description="""The ontology identifier for the developmental stage component.""",
        json_schema_extra={
            "linkml_meta": {
                "any_of": [
                    {"range": "UNKNOWN_LITERAL"},
                    {"range": "WORMBASE_DEVELOPMENT_ID"},
                    {"range": "UBERON_ID"},
                    {"range": "HSAPDV_ID"},
                    {"range": "MMUSDV_ID"},
                    {"range": "ZFS_ID"},
                    {"range": "FBDV_ID"},
                ],
                "domain_of": [
                    "Assay",
                    "DevelopmentStageDetails",
                    "Disease",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                ],
                "exact_mappings": ["cdp-common:development_stage_id"],
                "recommended": True,
            }
        },
    )

    @field_validator("id")
    def pattern_id(cls, v):
        pattern = re.compile(
            r"(^unknown$)|(WBls:[0-9]{7}$)|(^UBERON:[0-9]{7}$)|(HsapDv:[0-9]{7}$)|(MmusDv:[0-9]{7}$)|(ZFS:[0-9]{7}$)|(FBdv:[0-9]{8}$)"
        )
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v


class Disease(ConfiguredBaseModel):
    """
    The disease or condition of the patients from which assayed biosamples were derived.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    name: Optional[str] = Field(
        default=None,
        description="""Name of the disease.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "Assay",
                    "DevelopmentStageDetails",
                    "Disease",
                    "OrganismDetails",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                    "AnnotationTriangularMeshGroupFile",
                    "AuthorMixin",
                    "Author",
                ],
                "exact_mappings": ["cdp-common:disease_name"],
                "recommended": True,
            }
        },
    )
    id: Optional[str] = Field(
        default=None,
        description="""The ontology identifier for the disease component.""",
        json_schema_extra={
            "linkml_meta": {
                "any_of": [{"range": "MONDO_ID"}, {"range": "PATO_ID"}],
                "domain_of": [
                    "Assay",
                    "DevelopmentStageDetails",
                    "Disease",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                ],
                "exact_mappings": ["cdp-common:disease_id"],
                "recommended": True,
            }
        },
    )

    @field_validator("id")
    def pattern_id(cls, v):
        pattern = re.compile(r"(^MONDO:[0-9]{7}$)|(^PATO:[0-9]{7}$)")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v


class OrganismDetails(ConfiguredBaseModel):
    """
    The species from which the sample was derived.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    name: str = Field(
        default=...,
        description="""Name of the organism from which a biological sample used in a CryoET study is derived from, e.g. homo sapiens.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "Assay",
                    "DevelopmentStageDetails",
                    "Disease",
                    "OrganismDetails",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                    "AnnotationTriangularMeshGroupFile",
                    "AuthorMixin",
                    "Author",
                ],
                "exact_mappings": ["cdp-common:organism_name"],
            }
        },
    )
    taxonomy_id: Optional[int] = Field(
        default=None,
        description="""NCBI taxonomy identifier for the organism, e.g. 9606""",
        ge=1,
        json_schema_extra={
            "linkml_meta": {
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
        default=...,
        description="""Name of the tissue from which a biological sample used in a CryoET study is derived from.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "Assay",
                    "DevelopmentStageDetails",
                    "Disease",
                    "OrganismDetails",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                    "AnnotationTriangularMeshGroupFile",
                    "AuthorMixin",
                    "Author",
                ],
                "exact_mappings": ["cdp-common:tissue_name"],
            }
        },
    )
    id: Optional[str] = Field(
        default=None,
        description="""The ontology identifier for the tissue.""",
        json_schema_extra={
            "linkml_meta": {
                "any_of": [
                    {"range": "BTO_ID"},
                    {"range": "CL_ID"},
                    {"range": "WBBT_ID"},
                    {"range": "ZFA_ID"},
                    {"range": "FBBT_ID"},
                    {"range": "UBERON_ID"},
                ],
                "domain_of": [
                    "Assay",
                    "DevelopmentStageDetails",
                    "Disease",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                ],
                "exact_mappings": ["cdp-common:tissue_id"],
                "recommended": True,
            }
        },
    )

    @field_validator("id")
    def pattern_id(cls, v):
        pattern = re.compile(
            r"(^BTO:[0-9]{7}$)|(^CL:[0-9]{7}$)|(WBbt:[0-9]{7}$)|(ZFA:[0-9]{7}$)|(FBbt:[0-9]{8}$)|(^UBERON:[0-9]{7}$)"
        )
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v


class CellType(ConfiguredBaseModel):
    """
    The cell type from which the sample was derived.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    name: str = Field(
        default=...,
        description="""Name of the cell type from which a biological sample used in a CryoET study is derived from.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "Assay",
                    "DevelopmentStageDetails",
                    "Disease",
                    "OrganismDetails",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                    "AnnotationTriangularMeshGroupFile",
                    "AuthorMixin",
                    "Author",
                ],
                "exact_mappings": ["cdp-common:cell_name"],
            }
        },
    )
    id: Optional[str] = Field(
        default=None,
        description="""The ontology identifier for the cell type.""",
        json_schema_extra={
            "linkml_meta": {
                "any_of": [
                    {"range": "CL_ID"},
                    {"range": "WBBT_ID"},
                    {"range": "ZFA_ID"},
                    {"range": "FBBT_ID"},
                    {"range": "UBERON_ID"},
                ],
                "domain_of": [
                    "Assay",
                    "DevelopmentStageDetails",
                    "Disease",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                ],
                "exact_mappings": ["cdp-common:cell_type_id"],
                "recommended": True,
            }
        },
    )

    @field_validator("id")
    def pattern_id(cls, v):
        pattern = re.compile(r"(^CL:[0-9]{7}$)|(WBbt:[0-9]{7}$)|(ZFA:[0-9]{7}$)|(FBbt:[0-9]{8}$)|(^UBERON:[0-9]{7}$)")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v


class CellStrain(ConfiguredBaseModel):
    """
    The strain or cell line from which the sample was derived.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    name: str = Field(
        default=...,
        description="""Cell line or strain for the sample.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "Assay",
                    "DevelopmentStageDetails",
                    "Disease",
                    "OrganismDetails",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                    "AnnotationTriangularMeshGroupFile",
                    "AuthorMixin",
                    "Author",
                ],
                "exact_mappings": ["cdp-common:cell_strain_name"],
            }
        },
    )
    id: Optional[str] = Field(
        default=None,
        description="""The ontology identifier for the cell strain.""",
        json_schema_extra={
            "linkml_meta": {
                "any_of": [
                    {"range": "WORMBASE_STRAIN_ID"},
                    {"range": "NCBI_TAXON_ID"},
                    {"range": "CVCL_ID"},
                    {"range": "CC_ID"},
                ],
                "domain_of": [
                    "Assay",
                    "DevelopmentStageDetails",
                    "Disease",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                ],
                "exact_mappings": ["cdp-common:cell_strain_id"],
                "recommended": True,
            }
        },
    )

    @field_validator("id")
    def pattern_id(cls, v):
        pattern = re.compile(r"(WBStrain[0-9]{8}$)|(^NCBITaxon:[0-9]+$)|(^CVCL_[A-Z0-9]{4,}$)|(^CC-[0-9]{4}$)")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v


class CellComponent(ConfiguredBaseModel):
    """
    The cellular component from which the sample was derived.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    name: str = Field(
        default=...,
        description="""Name of the cellular component.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "Assay",
                    "DevelopmentStageDetails",
                    "Disease",
                    "OrganismDetails",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                    "AnnotationTriangularMeshGroupFile",
                    "AuthorMixin",
                    "Author",
                ],
                "exact_mappings": ["cdp-common:cell_component_name"],
            }
        },
    )
    id: Optional[str] = Field(
        default=None,
        description="""The GO identifier for the cellular component.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "Assay",
                    "DevelopmentStageDetails",
                    "Disease",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                ],
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
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v


class ExperimentMetadata(ConfiguredBaseModel):
    """
    Metadata describing sample and sample preparation methods used in a cryoET dataset.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    sample_type: SampleTypeEnum = Field(
        default=...,
        description="""Type of sample imaged in a CryoET study.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["ExperimentMetadata", "Dataset"],
                "exact_mappings": ["cdp-common:preparation_sample_type"],
            }
        },
    )
    sample_preparation: Optional[str] = Field(
        default=None,
        description="""Describes how the sample was prepared.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["ExperimentMetadata", "Dataset"],
                "exact_mappings": ["cdp-common:sample_preparation"],
                "recommended": True,
            }
        },
    )
    grid_preparation: Optional[str] = Field(
        default=None,
        description="""Describes Cryo-ET grid preparation.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["ExperimentMetadata", "Dataset"],
                "exact_mappings": ["cdp-common:grid_preparation"],
                "recommended": True,
            }
        },
    )
    other_setup: Optional[str] = Field(
        default=None,
        description="""Describes other setup not covered by sample preparation or grid preparation that may make this dataset unique in the same publication.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["ExperimentMetadata", "Dataset"],
                "exact_mappings": ["cdp-common:preparation_other_setup"],
                "recommended": True,
            }
        },
    )
    organism: Optional[OrganismDetails] = Field(
        default=None,
        description="""The species from which the sample was derived.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ExperimentMetadata", "Dataset"]}},
    )
    tissue: Optional[TissueDetails] = Field(
        default=None,
        description="""The type of tissue from which the sample was derived.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ExperimentMetadata", "Dataset"]}},
    )
    cell_type: Optional[CellType] = Field(
        default=None,
        description="""The cell type from which the sample was derived.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ExperimentMetadata", "Dataset"]}},
    )
    cell_strain: Optional[CellStrain] = Field(
        default=None,
        description="""The strain or cell line from which the sample was derived.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ExperimentMetadata", "Dataset"]}},
    )
    cell_component: Optional[CellComponent] = Field(
        default=None,
        description="""The cellular component from which the sample was derived.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ExperimentMetadata", "Dataset"]}},
    )
    assay: Assay = Field(
        default=...,
        description="""The assay that was used to create the dataset.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ExperimentMetadata", "Dataset"]}},
    )
    development_stage: DevelopmentStageDetails = Field(
        default=...,
        description="""The development stage of the patients or organisms from which assayed biosamples were derived.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ExperimentMetadata", "Dataset"]}},
    )
    disease: Disease = Field(
        default=...,
        description="""The disease or condition of the patients from which assayed biosamples were derived.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ExperimentMetadata", "Dataset"]}},
    )

    @field_validator("sample_type")
    def pattern_sample_type(cls, v):
        pattern = re.compile(
            r"(^cell_line$)|(^in_silico$)|(^in_vitro$)|(^organelle$)|(^organism$)|(^organoid$)|(^other$)|(^primary_cell_culture$)|(^tissue$)|(^virus$)"
        )
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid sample_type format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid sample_type format: {v}"
            raise ValueError(err_msg)
        return v


class Dataset(ExperimentMetadata, CrossReferencedEntity, FundedEntity, AuthoredEntity, DateStampedEntity):
    """
    High-level description of a cryoET dataset.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "metadata",
            "mixins": [
                "DateStampedEntity",
                "AuthoredEntity",
                "FundedEntity",
                "CrossReferencedEntity",
                "ExperimentMetadata",
            ],
        }
    )

    dataset_identifier: int = Field(
        default=...,
        description="""An identifier for a CryoET dataset, assigned by the Data Portal. Used to identify the dataset as the directory name in data tree.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["Dataset"], "exact_mappings": ["cdp-common:dataset_identifier"]}
        },
    )
    dataset_title: str = Field(
        default=...,
        description="""Title of a CryoET dataset.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Dataset"], "exact_mappings": ["cdp-common:dataset_title"]}},
    )
    dataset_description: str = Field(
        default=...,
        description="""A short description of a CryoET dataset, similar to an abstract for a journal article or dataset.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["Dataset"], "exact_mappings": ["cdp-common:dataset_description"]}
        },
    )
    dates: DateStamp = Field(
        default=...,
        description="""A set of dates at which a data item was deposited, published and last modified.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["DateStampedEntity", "Tomogram", "Dataset", "Deposition", "Annotation"]}
        },
    )
    authors: list[Author] = Field(
        default=...,
        description="""Author of a scientific data entity.""",
        min_length=1,
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AuthoredEntity", "Dataset", "Deposition", "Tomogram", "Annotation"],
                "list_elements_ordered": True,
            }
        },
    )
    funding: Optional[list[FundingDetails]] = Field(
        default=[],
        description="""A funding source for a scientific data entity (base for JSON and DB representation).""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["FundedEntity", "Dataset"],
                "list_elements_ordered": True,
                "recommended": True,
            }
        },
    )
    cross_references: Optional[CrossReferences] = Field(
        default=None,
        description="""A set of cross-references to other databases and publications.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["CrossReferencedEntity", "Tomogram", "Dataset", "Deposition"]}
        },
    )
    sample_type: SampleTypeEnum = Field(
        default=...,
        description="""Type of sample imaged in a CryoET study.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["ExperimentMetadata", "Dataset"],
                "exact_mappings": ["cdp-common:preparation_sample_type"],
            }
        },
    )
    sample_preparation: Optional[str] = Field(
        default=None,
        description="""Describes how the sample was prepared.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["ExperimentMetadata", "Dataset"],
                "exact_mappings": ["cdp-common:sample_preparation"],
                "recommended": True,
            }
        },
    )
    grid_preparation: Optional[str] = Field(
        default=None,
        description="""Describes Cryo-ET grid preparation.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["ExperimentMetadata", "Dataset"],
                "exact_mappings": ["cdp-common:grid_preparation"],
                "recommended": True,
            }
        },
    )
    other_setup: Optional[str] = Field(
        default=None,
        description="""Describes other setup not covered by sample preparation or grid preparation that may make this dataset unique in the same publication.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["ExperimentMetadata", "Dataset"],
                "exact_mappings": ["cdp-common:preparation_other_setup"],
                "recommended": True,
            }
        },
    )
    organism: Optional[OrganismDetails] = Field(
        default=None,
        description="""The species from which the sample was derived.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ExperimentMetadata", "Dataset"]}},
    )
    tissue: Optional[TissueDetails] = Field(
        default=None,
        description="""The type of tissue from which the sample was derived.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ExperimentMetadata", "Dataset"]}},
    )
    cell_type: Optional[CellType] = Field(
        default=None,
        description="""The cell type from which the sample was derived.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ExperimentMetadata", "Dataset"]}},
    )
    cell_strain: Optional[CellStrain] = Field(
        default=None,
        description="""The strain or cell line from which the sample was derived.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ExperimentMetadata", "Dataset"]}},
    )
    cell_component: Optional[CellComponent] = Field(
        default=None,
        description="""The cellular component from which the sample was derived.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ExperimentMetadata", "Dataset"]}},
    )
    assay: Assay = Field(
        default=...,
        description="""The assay that was used to create the dataset.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ExperimentMetadata", "Dataset"]}},
    )
    development_stage: DevelopmentStageDetails = Field(
        default=...,
        description="""The development stage of the patients or organisms from which assayed biosamples were derived.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ExperimentMetadata", "Dataset"]}},
    )
    disease: Disease = Field(
        default=...,
        description="""The disease or condition of the patients from which assayed biosamples were derived.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ExperimentMetadata", "Dataset"]}},
    )

    @field_validator("sample_type")
    def pattern_sample_type(cls, v):
        pattern = re.compile(
            r"(^cell_line$)|(^in_silico$)|(^in_vitro$)|(^organelle$)|(^organism$)|(^organoid$)|(^other$)|(^primary_cell_culture$)|(^tissue$)|(^virus$)"
        )
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid sample_type format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid sample_type format: {v}"
            raise ValueError(err_msg)
        return v


class Deposition(CrossReferencedEntity, AuthoredEntity, DateStampedEntity):
    """
    Metadata describing a deposition.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "metadata", "mixins": ["DateStampedEntity", "AuthoredEntity", "CrossReferencedEntity"]}
    )

    deposition_description: str = Field(
        default=...,
        description="""A short description of the deposition, similar to an abstract for a journal article or dataset.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["Deposition"], "exact_mappings": ["cdp-common:deposition_description"]}
        },
    )
    deposition_identifier: int = Field(
        default=...,
        description="""An identifier for a CryoET deposition, assigned by the Data Portal. Used to identify the deposition the entity is a part of.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["Deposition"], "exact_mappings": ["cdp-common:deposition_identifier"]}
        },
    )
    deposition_title: str = Field(
        default=...,
        description="""Title of a CryoET deposition.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["Deposition"], "exact_mappings": ["cdp-common:deposition_title"]}
        },
    )
    deposition_types: list[DepositionTypesEnum] = Field(
        default=...,
        description="""Type of data in the deposition (e.g. dataset, annotation, tomogram)""",
        min_length=1,
        json_schema_extra={
            "linkml_meta": {"domain_of": ["Deposition"], "exact_mappings": ["cdp-common:deposition_types"]}
        },
    )
    tag: Optional[str] = Field(
        default=None,
        description="""A string to categorize this deposition (i.e \"competitionML2024Winners\")""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Deposition"], "exact_mappings": ["cdp-common:tag"]}},
    )
    dates: DateStamp = Field(
        default=...,
        description="""A set of dates at which a data item was deposited, published and last modified.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["DateStampedEntity", "Tomogram", "Dataset", "Deposition", "Annotation"]}
        },
    )
    authors: list[Author] = Field(
        default=...,
        description="""Author of a scientific data entity.""",
        min_length=1,
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AuthoredEntity", "Dataset", "Deposition", "Tomogram", "Annotation"],
                "list_elements_ordered": True,
            }
        },
    )
    cross_references: Optional[CrossReferences] = Field(
        default=None,
        description="""A set of cross-references to other databases and publications.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["CrossReferencedEntity", "Tomogram", "Dataset", "Deposition"]}
        },
    )

    @field_validator("deposition_types")
    def pattern_deposition_types(cls, v):
        pattern = re.compile(r"(^annotation$)|(^dataset$)|(^tomogram$)")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid deposition_types format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid deposition_types format: {v}"
            raise ValueError(err_msg)
        return v


class CameraDetails(ConfiguredBaseModel):
    """
    The camera used to collect the tilt series.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    acquire_mode: Optional[Union[TiltseriesCameraAcquireModeEnum, str]] = Field(
        default=None,
        description="""Camera acquisition mode""",
        json_schema_extra={
            "linkml_meta": {
                "any_of": [{"range": "StringFormattedString"}, {"range": "tiltseries_camera_acquire_mode_enum"}],
                "domain_of": ["CameraDetails"],
                "exact_mappings": ["cdp-common:tiltseries_camera_acquire_mode"],
            }
        },
    )
    manufacturer: TiltseriesCameraManufacturerEnum = Field(
        default=...,
        description="""Name of the camera manufacturer""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["CameraDetails", "MicroscopeDetails"],
                "exact_mappings": ["cdp-common:tiltseries_camera_manufacturer"],
            }
        },
    )
    model: Union[
        TiltseriesCameraModelFeiTfsEnum, TiltseriesCameraModelGatanEnum, TiltseriesCameraModelSimulatedEnum, str
    ] = Field(
        default=...,
        description="""Camera model name""",
        json_schema_extra={
            "linkml_meta": {
                "any_of": [
                    {"range": "StringFormattedString"},
                    {"range": "tiltseries_camera_model_fei_tfs_enum"},
                    {"range": "tiltseries_camera_model_gatan_enum"},
                    {"range": "tiltseries_camera_model_simulated_enum"},
                ],
                "domain_of": ["CameraDetails", "MicroscopeDetails"],
                "exact_mappings": ["cdp-common:tiltseries_camera_model"],
            }
        },
    )

    @field_validator("acquire_mode")
    def pattern_acquire_mode(cls, v):
        pattern = re.compile(r"(^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$)|((^counting$)|(^superresolution$)|(^linear$)|(^cds$))")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid acquire_mode format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid acquire_mode format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("manufacturer")
    def pattern_manufacturer(cls, v):
        pattern = re.compile(r"(^Gatan$)|(^FEI$)|(^TFS$)|(^simulated$)")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid manufacturer format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid manufacturer format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("model")
    def pattern_model(cls, v):
        pattern = re.compile(
            r"(^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$)|((^FALCON IV$)|(^FALCON 4i$))|((^K2$)|(^K2 SUMMIT$)|(^K3$)|(^K3 BIOQUANTUM$)|(^UltraCam$)|(^UltraScan$))|(^simulated$)"
        )
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid model format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid model format: {v}"
            raise ValueError(err_msg)
        return v


class MicroscopeDetails(ConfiguredBaseModel):
    """
    The microscope used to collect the tilt series.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    additional_info: Optional[str] = Field(
        default=None,
        description="""Other microscope optical setup information, in addition to energy filter, phase plate and image corrector""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["MicroscopeDetails"],
                "exact_mappings": ["cdp-common:tiltseries_microscope_additional_info"],
            }
        },
    )
    manufacturer: Union[TiltseriesMicroscopeManufacturerEnum, str] = Field(
        default=...,
        description="""Name of the microscope manufacturer""",
        json_schema_extra={
            "linkml_meta": {
                "any_of": [
                    {
                        "description": "Name of the microscope manufacturer",
                        "exact_mappings": ["cdp-common:tiltseries_microscope_manufacturer"],
                        "range": "tiltseries_microscope_manufacturer_enum",
                        "required": True,
                    },
                    {"range": "StringFormattedString"},
                ],
                "domain_of": ["CameraDetails", "MicroscopeDetails"],
            }
        },
    )
    model: str = Field(
        default=...,
        description="""Microscope model name""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["CameraDetails", "MicroscopeDetails"],
                "exact_mappings": ["cdp-common:tiltseries_microscope_model"],
            }
        },
    )

    @field_validator("manufacturer")
    def pattern_manufacturer(cls, v):
        pattern = re.compile(r"(^FEI$)|(^TFS$)|(^JEOL$)|(^SIMULATED$)|(^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$)")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid manufacturer format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid manufacturer format: {v}"
            raise ValueError(err_msg)
        return v


class MicroscopeOpticalSetup(ConfiguredBaseModel):
    """
    The optical setup of the microscope used to collect the tilt series.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    energy_filter: str = Field(
        default=...,
        description="""Energy filter setup used""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["MicroscopeOpticalSetup"],
                "exact_mappings": ["cdp-common:tiltseries_microscope_energy_filter"],
            }
        },
    )
    phase_plate: Optional[str] = Field(
        default=None,
        description="""Phase plate configuration""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["MicroscopeOpticalSetup"],
                "exact_mappings": ["cdp-common:tiltseries_microscope_phase_plate"],
            }
        },
    )
    image_corrector: Optional[str] = Field(
        default=None,
        description="""Image corrector setup""",
        json_schema_extra={
            "linkml_meta": {
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
        default=...,
        description="""Minimal tilt angle in degrees""",
        ge=-90,
        le=90,
        json_schema_extra={
            "linkml_meta": {
                "any_of": [
                    {
                        "description": "Minimal tilt angle in degrees",
                        "exact_mappings": ["cdp-common:tiltseries_tilt_min"],
                        "maximum_value": 90,
                        "minimum_value": -90,
                        "range": "float",
                        "required": True,
                        "unit": {"descriptive_name": "degrees", "symbol": "°"},
                    },
                    {"range": "FloatFormattedString"},
                ],
                "domain_of": ["TiltRange"],
                "unit": {"descriptive_name": "degrees", "symbol": "°"},
            }
        },
    )
    max: Union[float, str] = Field(
        default=...,
        description="""Maximal tilt angle in degrees""",
        ge=-90,
        le=90,
        json_schema_extra={
            "linkml_meta": {
                "any_of": [
                    {
                        "description": "Maximal tilt angle in degrees",
                        "exact_mappings": ["cdp-common:tiltseries_tilt_max"],
                        "maximum_value": 90,
                        "minimum_value": -90,
                        "range": "float",
                        "required": True,
                        "unit": {"descriptive_name": "degrees", "symbol": "°"},
                    },
                    {"range": "FloatFormattedString"},
                ],
                "domain_of": ["TiltRange"],
                "unit": {"descriptive_name": "degrees", "symbol": "°"},
            }
        },
    )

    @field_validator("min")
    def pattern_min(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid min format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid min format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("max")
    def pattern_max(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid max format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid max format: {v}"
            raise ValueError(err_msg)
        return v


class PerSectionParameter(ConfiguredBaseModel):
    """
    Parameters for a section of a tilt series.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    z_index: int = Field(
        default=...,
        description="""z-index of the frame in the tiltseries""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["PerSectionParameter", "PerSectionAlignmentParameters"],
                "exact_mappings": ["cdp-common:per_section_z_index"],
            }
        },
    )
    frame_acquisition_order: int = Field(
        default=...,
        description="""The 0-based index of this movie stack in the order of acquisition.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["PerSectionParameter"],
                "exact_mappings": ["cdp-common:frames_acquisition_order"],
            }
        },
    )
    raw_angle: Optional[float] = Field(
        default=None,
        description="""Nominal angle of the tilt series section.""",
        ge=-90,
        le=90,
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["PerSectionParameter"],
                "exact_mappings": ["cdp-common:per_section_nominal_tilt_angle"],
                "unit": {"descriptive_name": "degrees", "symbol": "°"},
            }
        },
    )
    astigmatic_angle: Optional[float] = Field(
        default=None,
        description="""Angle of astigmatism.""",
        ge=-180,
        le=180,
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["PerSectionParameter"],
                "exact_mappings": ["cdp-common:per_section_astigmatic_angle"],
                "unit": {"descriptive_name": "degrees", "symbol": "°"},
            }
        },
    )
    minor_defocus: Optional[float] = Field(
        default=None,
        description="""Minor axis defocus amount, underfocus is positive.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["PerSectionParameter"],
                "exact_mappings": ["cdp-common:per_section_minor_defocus"],
                "unit": {"descriptive_name": "angstrom", "symbol": "Å"},
            }
        },
    )
    major_defocus: Optional[float] = Field(
        default=None,
        description="""Major axis defocus amount, underfocus is positive.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["PerSectionParameter"],
                "exact_mappings": ["cdp-common:per_section_major_defocus"],
                "unit": {"descriptive_name": "angstrom", "symbol": "Å"},
            }
        },
    )
    max_resolution: Optional[float] = Field(
        default=None,
        description="""Maximum resolution of the CTF fit for this section.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["PerSectionParameter"],
                "exact_mappings": ["cdp-common:per_section_max_resolution"],
                "unit": {"descriptive_name": "angstrom", "symbol": "Å"},
            }
        },
    )
    phase_shift: Optional[float] = Field(
        default=None,
        description="""Phase shift measured for this section.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["PerSectionParameter"],
                "exact_mappings": ["cdp-common:per_section_phase_shift"],
                "unit": {"descriptive_name": "radians", "symbol": "rad"},
            }
        },
    )
    cross_correlation: Optional[float] = Field(
        default=None,
        description="""CTF fit cross correlation value for this section.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["PerSectionParameter"],
                "exact_mappings": ["cdp-common:per_section_cross_correlation"],
            }
        },
    )


class TiltSeriesSize(ConfiguredBaseModel):
    """
    The size of a tiltseries in sctions/pixels in each dimension.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    x: int = Field(
        default=...,
        description="""Number of pixels in the 2D data fast axis""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["TiltSeriesSize", "TomogramSize", "TomogramOffset", "AlignmentSize", "AlignmentOffset"],
                "unit": {"descriptive_name": "pixels", "symbol": "px"},
            }
        },
    )
    y: int = Field(
        default=...,
        description="""Number of pixels in the 2D data medium axis""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["TiltSeriesSize", "TomogramSize", "TomogramOffset", "AlignmentSize", "AlignmentOffset"],
                "unit": {"descriptive_name": "pixels", "symbol": "px"},
            }
        },
    )
    z: int = Field(
        default=...,
        description="""Number of sections in the 2D stack.""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["TiltSeriesSize", "TomogramSize", "TomogramOffset", "AlignmentSize", "AlignmentOffset"],
                "unit": {"descriptive_name": "sections"},
            }
        },
    )


class TiltSeries(ConfiguredBaseModel):
    """
    Metadata describing a tilt series.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    acceleration_voltage: float = Field(
        default=...,
        description="""Electron Microscope Accelerator voltage in volts""",
        ge=20000,
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["TiltSeries"],
                "exact_mappings": ["cdp-common:tiltseries_acceleration_voltage"],
                "unit": {"descriptive_name": "volts", "symbol": "V"},
            }
        },
    )
    aligned_tiltseries_binning: Optional[Union[float, str]] = Field(
        default=None,
        description="""Binning factor of the aligned tilt series""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "any_of": [
                    {
                        "description": "Binning factor of the aligned tilt series",
                        "exact_mappings": ["cdp-common:tiltseries_aligned_tiltseries_binning"],
                        "minimum_value": 0,
                        "range": "float",
                    },
                    {"range": "FloatFormattedString"},
                ],
                "domain_of": ["TiltSeries"],
            }
        },
    )
    binning_from_frames: Optional[Union[float, str]] = Field(
        default=None,
        description="""Describes the binning factor from frames to tilt series file""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "any_of": [
                    {
                        "description": "Describes the binning factor from frames to tilt " "series file",
                        "exact_mappings": ["cdp-common:tiltseries_binning_from_frames"],
                        "minimum_value": 0,
                        "range": "float",
                    },
                    {"range": "FloatFormattedString"},
                ],
                "domain_of": ["TiltSeries"],
            }
        },
    )
    camera: CameraDetails = Field(
        default=...,
        description="""The camera used to collect the tilt series.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["TiltSeries"]}},
    )
    data_acquisition_software: str = Field(
        default=...,
        description="""Software used to collect data""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["TiltSeries"],
                "exact_mappings": ["cdp-common:tiltseries_data_acquisition_software"],
            }
        },
    )
    frames_count: Optional[int] = Field(
        default=None,
        description="""Number of frames associated with this tiltseries""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["TiltSeries"], "exact_mappings": ["cdp-common:tiltseries_frames_count"]}
        },
    )
    is_aligned: bool = Field(
        default=...,
        description="""Whether this tilt series is aligned""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["TiltSeries"], "exact_mappings": ["cdp-common:tiltseries_is_aligned"]}
        },
    )
    microscope: MicroscopeDetails = Field(
        default=...,
        description="""The microscope used to collect the tilt series.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["TiltSeries"]}},
    )
    microscope_optical_setup: MicroscopeOpticalSetup = Field(
        default=...,
        description="""The optical setup of the microscope used to collect the tilt series.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["TiltSeries"]}},
    )
    related_empiar_entry: Optional[str] = Field(
        default=None,
        description="""If a tilt series is deposited into EMPIAR, enter the EMPIAR dataset identifier""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["TiltSeries"],
                "exact_mappings": ["cdp-common:tiltseries_related_empiar_entry"],
            }
        },
    )
    spherical_aberration_constant: Union[float, str] = Field(
        default=...,
        description="""Spherical Aberration Constant of the objective lens in millimeters""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "any_of": [
                    {
                        "description": "Spherical Aberration Constant of the objective " "lens in millimeters",
                        "exact_mappings": ["cdp-common:tiltseries_spherical_aberration_constant"],
                        "minimum_value": 0,
                        "range": "float",
                        "required": True,
                        "unit": {"descriptive_name": "millimeters", "symbol": "mm"},
                    },
                    {"range": "FloatFormattedString"},
                ],
                "domain_of": ["TiltSeries"],
                "unit": {"descriptive_name": "millimeters", "symbol": "mm"},
            }
        },
    )
    tilt_alignment_software: Optional[str] = Field(
        default=None,
        description="""Software used for tilt alignment""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["TiltSeries"],
                "exact_mappings": ["cdp-common:tiltseries_tilt_alignment_software"],
            }
        },
    )
    tilt_axis: Union[float, str] = Field(
        default=...,
        description="""Rotation angle in degrees""",
        ge=-360,
        le=360,
        json_schema_extra={
            "linkml_meta": {
                "any_of": [
                    {
                        "description": "Rotation angle in degrees",
                        "exact_mappings": ["cdp-common:tiltseries_tilt_axis"],
                        "maximum_value": 360,
                        "minimum_value": -360,
                        "range": "float",
                        "required": True,
                        "unit": {"descriptive_name": "degrees", "symbol": "°"},
                    },
                    {"range": "FloatFormattedString"},
                ],
                "domain_of": ["TiltSeries"],
                "unit": {"descriptive_name": "degrees", "symbol": "°"},
            }
        },
    )
    tilt_range: TiltRange = Field(
        default=...,
        description="""The range of tilt angles in the tilt series.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["TiltSeries"]}},
    )
    tilt_series_quality: Union[int, str] = Field(
        default=...,
        description="""Author assessment of tilt series quality within the dataset (1-5, 5 is best)""",
        ge=1,
        le=5,
        json_schema_extra={
            "linkml_meta": {
                "any_of": [
                    {
                        "description": "Author assessment of tilt series quality within "
                        "the dataset (1-5, 5 is best)",
                        "exact_mappings": ["cdp-common:tiltseries_tilt_series_quality"],
                        "maximum_value": 5,
                        "minimum_value": 1,
                        "range": "integer",
                        "required": True,
                    },
                    {"range": "IntegerFormattedString"},
                ],
                "domain_of": ["TiltSeries"],
            }
        },
    )
    tilt_step: Union[float, str] = Field(
        default=...,
        description="""Tilt step in degrees""",
        ge=0,
        le=90,
        json_schema_extra={
            "linkml_meta": {
                "any_of": [
                    {
                        "description": "Tilt step in degrees",
                        "exact_mappings": ["cdp-common:tiltseries_tilt_step"],
                        "maximum_value": 90,
                        "minimum_value": 0,
                        "range": "float",
                        "required": True,
                        "unit": {"descriptive_name": "degrees", "symbol": "°"},
                    },
                    {"range": "FloatFormattedString"},
                ],
                "domain_of": ["TiltSeries"],
                "unit": {"descriptive_name": "degrees", "symbol": "°"},
            }
        },
    )
    tilting_scheme: str = Field(
        default=...,
        description="""The order of stage tilting during acquisition of the data""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["TiltSeries"], "exact_mappings": ["cdp-common:tiltseries_tilting_scheme"]}
        },
    )
    total_flux: Union[float, str] = Field(
        default=...,
        description="""Number of Electrons reaching the specimen in a square Angstrom area for the entire tilt series""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "any_of": [
                    {
                        "description": "Number of Electrons reaching the specimen in a "
                        "square Angstrom area for the entire tilt series",
                        "exact_mappings": ["cdp-common:tiltseries_total_flux"],
                        "minimum_value": 0,
                        "range": "float",
                        "required": True,
                        "unit": {"descriptive_name": "electrons per square Angstrom", "symbol": "e^-/Å^2"},
                    },
                    {"range": "FloatFormattedString"},
                ],
                "domain_of": ["TiltSeries"],
                "unit": {"descriptive_name": "electrons per square Angstrom", "symbol": "e^-/Å^2"},
            }
        },
    )
    pixel_spacing: Union[float, str] = Field(
        default=...,
        description="""Pixel spacing for the tilt series""",
        ge=0.001,
        json_schema_extra={
            "linkml_meta": {
                "any_of": [
                    {
                        "description": "Pixel spacing for the tilt series",
                        "exact_mappings": ["cdp-common:tiltseries_pixel_spacing"],
                        "minimum_value": 0.001,
                        "range": "float",
                        "required": True,
                        "unit": {"descriptive_name": "Angstroms per pixel", "symbol": "Å/px"},
                    },
                    {"range": "FloatFormattedString"},
                ],
                "domain_of": ["TiltSeries"],
                "unit": {"descriptive_name": "Angstroms per pixel", "symbol": "Å/px"},
            }
        },
    )

    @field_validator("aligned_tiltseries_binning")
    def pattern_aligned_tiltseries_binning(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid aligned_tiltseries_binning format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid aligned_tiltseries_binning format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("binning_from_frames")
    def pattern_binning_from_frames(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid binning_from_frames format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid binning_from_frames format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("related_empiar_entry")
    def pattern_related_empiar_entry(cls, v):
        pattern = re.compile(r"^EMPIAR-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid related_empiar_entry format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid related_empiar_entry format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("spherical_aberration_constant")
    def pattern_spherical_aberration_constant(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid spherical_aberration_constant format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid spherical_aberration_constant format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("tilt_axis")
    def pattern_tilt_axis(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid tilt_axis format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid tilt_axis format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("tilt_series_quality")
    def pattern_tilt_series_quality(cls, v):
        pattern = re.compile(r"^int[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid tilt_series_quality format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid tilt_series_quality format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("tilt_step")
    def pattern_tilt_step(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid tilt_step format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid tilt_step format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("total_flux")
    def pattern_total_flux(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid total_flux format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid total_flux format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("pixel_spacing")
    def pattern_pixel_spacing(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid pixel_spacing format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid pixel_spacing format: {v}"
            raise ValueError(err_msg)
        return v


class TomogramSize(ConfiguredBaseModel):
    """
    The size of a tomogram in voxels in each dimension.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    x: int = Field(
        default=...,
        description="""Number of pixels in the 3D data fast axis""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["TiltSeriesSize", "TomogramSize", "TomogramOffset", "AlignmentSize", "AlignmentOffset"],
                "unit": {"descriptive_name": "pixels", "symbol": "px"},
            }
        },
    )
    y: int = Field(
        default=...,
        description="""Number of pixels in the 3D data medium axis""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["TiltSeriesSize", "TomogramSize", "TomogramOffset", "AlignmentSize", "AlignmentOffset"],
                "unit": {"descriptive_name": "pixels", "symbol": "px"},
            }
        },
    )
    z: int = Field(
        default=...,
        description="""Number of pixels in the 3D data slow axis.  This is the image projection direction at zero stage tilt""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["TiltSeriesSize", "TomogramSize", "TomogramOffset", "AlignmentSize", "AlignmentOffset"],
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
        default=...,
        description="""x offset data relative to the canonical tomogram in pixels""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["TiltSeriesSize", "TomogramSize", "TomogramOffset", "AlignmentSize", "AlignmentOffset"],
                "unit": {"descriptive_name": "pixels", "symbol": "px"},
            }
        },
    )
    y: int = Field(
        default=...,
        description="""y offset data relative to the canonical tomogram in pixels""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["TiltSeriesSize", "TomogramSize", "TomogramOffset", "AlignmentSize", "AlignmentOffset"],
                "unit": {"descriptive_name": "pixels", "symbol": "px"},
            }
        },
    )
    z: int = Field(
        default=...,
        description="""z offset data relative to the canonical tomogram in pixels""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["TiltSeriesSize", "TomogramSize", "TomogramOffset", "AlignmentSize", "AlignmentOffset"],
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
        default=...,
        description="""Voxel spacing equal in all three axes in angstroms""",
        ge=0.001,
        json_schema_extra={
            "linkml_meta": {
                "any_of": [
                    {
                        "description": "Voxel spacing equal in all three axes in " "angstroms",
                        "exact_mappings": ["cdp-common:tomogram_voxel_spacing"],
                        "minimum_value": 0.001,
                        "range": "float",
                        "required": True,
                        "unit": {"descriptive_name": "Angstroms per voxel", "symbol": "Å/voxel"},
                    },
                    {"range": "FloatFormattedString"},
                ],
                "domain_of": ["Tomogram"],
                "unit": {"descriptive_name": "Angstroms per voxel", "symbol": "Å/voxel"},
            }
        },
    )
    fiducial_alignment_status: Union[FiducialAlignmentStatusEnum, str] = Field(
        default=...,
        description="""Whether the tomographic alignment was computed based on fiducial markers.""",
        json_schema_extra={
            "linkml_meta": {
                "any_of": [
                    {
                        "description": "Whether the tomographic alignment was computed " "based on fiducial markers.",
                        "exact_mappings": ["cdp-common:tomogram_fiducial_alignment_status"],
                        "range": "fiducial_alignment_status_enum",
                        "required": True,
                    },
                    {"range": "StringFormattedString"},
                ],
                "domain_of": ["Tomogram"],
            }
        },
    )
    ctf_corrected: Optional[bool] = Field(
        default=None,
        description="""Whether this tomogram is CTF corrected""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["Tomogram"],
                "exact_mappings": ["cdp-common:tomogram_ctf_corrected"],
                "recommended": True,
            }
        },
    )
    align_software: Optional[str] = Field(
        default=None,
        description="""Software used for alignment""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["Tomogram"], "exact_mappings": ["cdp-common:tomogram_align_software"]}
        },
    )
    reconstruction_method: Union[TomogramReconstructionMethodEnum, str] = Field(
        default=...,
        description="""Describe reconstruction method (WBP, SART, SIRT)""",
        json_schema_extra={
            "linkml_meta": {
                "any_of": [
                    {
                        "description": "Describe reconstruction method (WBP, SART, SIRT)",
                        "exact_mappings": ["cdp-common:tomogram_reconstruction_method"],
                        "range": "tomogram_reconstruction_method_enum",
                        "required": True,
                    },
                    {"range": "StringFormattedString"},
                ],
                "domain_of": ["Tomogram"],
            }
        },
    )
    reconstruction_software: str = Field(
        default=...,
        description="""Name of software used for reconstruction""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["Tomogram"],
                "exact_mappings": ["cdp-common:tomogram_reconstruction_software"],
            }
        },
    )
    processing: TomogramProcessingEnum = Field(
        default=...,
        description="""Describe additional processing used to derive the tomogram""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["Tomogram"], "exact_mappings": ["cdp-common:tomogram_processing"]}
        },
    )
    processing_software: Optional[str] = Field(
        default=None,
        description="""Processing software used to derive the tomogram""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["Tomogram"],
                "exact_mappings": ["cdp-common:tomogram_processing_software"],
                "recommended": True,
            }
        },
    )
    tomogram_version: float = Field(
        default=...,
        description="""Version of tomogram""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["Tomogram"], "exact_mappings": ["cdp-common:tomogram_version"]}
        },
    )
    affine_transformation_matrix: Optional[
        conlist(min_length=4, max_length=4, item_type=conlist(min_length=4, max_length=4, item_type=float))
    ] = Field(
        default=None,
        description="""The flip or rotation transformation of this author submitted tomogram is indicated here""",
        json_schema_extra={
            "linkml_meta": {
                "array": {
                    "dimensions": [{"exact_cardinality": 4}, {"exact_cardinality": 4}],
                    "exact_number_dimensions": 2,
                },
                "domain_of": ["Tomogram", "Alignment"],
            }
        },
    )
    size: Optional[TomogramSize] = Field(
        default=None,
        description="""The size of a tomogram in voxels in each dimension.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Tomogram"]}},
    )
    offset: TomogramOffset = Field(
        default=...,
        description="""The offset of a tomogram in voxels in each dimension relative to the canonical tomogram.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Tomogram"]}},
    )
    is_visualization_default: bool = Field(
        default=...,
        description="""Whether the tomogram is the default for visualization.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "Tomogram",
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ]
            }
        },
    )
    cross_references: Optional[CrossReferences] = Field(
        default=None,
        description="""A set of cross-references to other databases and publications.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["CrossReferencedEntity", "Tomogram", "Dataset", "Deposition"]}
        },
    )
    dates: DateStamp = Field(
        default=...,
        description="""A set of dates at which a data item was deposited, published and last modified.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["DateStampedEntity", "Tomogram", "Dataset", "Deposition", "Annotation"]}
        },
    )
    authors: list[Author] = Field(
        default=...,
        description="""Author of a scientific data entity.""",
        min_length=1,
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AuthoredEntity", "Dataset", "Deposition", "Tomogram", "Annotation"],
                "list_elements_ordered": True,
            }
        },
    )

    @field_validator("voxel_spacing")
    def pattern_voxel_spacing(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid voxel_spacing format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid voxel_spacing format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("fiducial_alignment_status")
    def pattern_fiducial_alignment_status(cls, v):
        pattern = re.compile(r"(^FIDUCIAL$)|(^NON_FIDUCIAL$)|(^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$)")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid fiducial_alignment_status format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid fiducial_alignment_status format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("reconstruction_method")
    def pattern_reconstruction_method(cls, v):
        pattern = re.compile(r"(^SART$)|(^Fourier Space$)|(^SIRT$)|(^WBP$)|(^Unknown$)|(^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$)")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid reconstruction_method format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid reconstruction_method format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("processing")
    def pattern_processing(cls, v):
        pattern = re.compile(r"(^denoised$)|(^filtered$)|(^raw$)")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid processing format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid processing format: {v}"
            raise ValueError(err_msg)
        return v


class AnnotationConfidence(ConfiguredBaseModel):
    """
    Metadata describing the confidence of an annotation.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    precision: Optional[float] = Field(
        default=None,
        description="""Describe the confidence level of the annotation. Precision is defined as the % of annotation objects being true positive""",
        ge=0,
        le=100,
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AnnotationConfidence"],
                "exact_mappings": ["cdp-common:annotation_confidence_precision"],
                "unit": {"descriptive_name": "percentage", "symbol": "%"},
            }
        },
    )
    recall: Optional[float] = Field(
        default=None,
        description="""Describe the confidence level of the annotation. Recall is defined as the % of true positives being annotated correctly""",
        ge=0,
        le=100,
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AnnotationConfidence"],
                "exact_mappings": ["cdp-common:annotation_confidence_recall"],
                "unit": {"descriptive_name": "percentage", "symbol": "%"},
            }
        },
    )
    ground_truth_used: Optional[str] = Field(
        default=None,
        description="""Annotation filename used as ground truth for precision and recall""",
        json_schema_extra={
            "linkml_meta": {
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
        default=...,
        description="""Ontology identifier for the annotation object.""",
        json_schema_extra={
            "linkml_meta": {
                "any_of": [{"range": "GO_ID"}, {"range": "UNIPROT_ID"}, {"range": "UBERON_ID"}, {"range": "CHEBI_ID"}],
                "domain_of": [
                    "Assay",
                    "DevelopmentStageDetails",
                    "Disease",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                ],
                "exact_mappings": ["cdp-common:annotation_object_id"],
            }
        },
    )
    name: str = Field(
        default=...,
        description="""Name of the object being annotated (e.g. ribosome, nuclear pore complex, actin filament, membrane)""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "Assay",
                    "DevelopmentStageDetails",
                    "Disease",
                    "OrganismDetails",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                    "AnnotationTriangularMeshGroupFile",
                    "AuthorMixin",
                    "Author",
                ],
                "exact_mappings": ["cdp-common:annotation_object_name"],
            }
        },
    )
    description: Optional[str] = Field(
        default=None,
        description="""A textual description of the annotation object, can be a longer description to include additional information not covered by the Annotation object name and state.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AnnotationObject"],
                "exact_mappings": ["cdp-common:annotation_object_description"],
            }
        },
    )
    state: Optional[str] = Field(
        default=None,
        description="""Molecule state annotated (e.g. open, closed)""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["AnnotationObject"], "exact_mappings": ["cdp-common:annotation_object_state"]}
        },
    )

    @field_validator("id")
    def pattern_id(cls, v):
        pattern = re.compile(
            r"(^GO:[0-9]{7}$)|(^UniProtKB:[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}$)|(^UBERON:[0-9]{7}$)|(^CHEBI:[0-9]+$)"
        )
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v


class AnnotationMethodLinks(ConfiguredBaseModel):
    """
    A set of links to models, source code, documentation, etc referenced by annotation the method
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    link: str = Field(
        default=...,
        description="""URL to the annotation method reference""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AnnotationMethodLinks"],
                "exact_mappings": ["cdp-common:annotation_method_link"],
            }
        },
    )
    link_type: AnnotationMethodLinkTypeEnum = Field(
        default=...,
        description="""Type of link (e.g. model, source code, documentation)""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AnnotationMethodLinks"],
                "exact_mappings": ["cdp-common:annotation_method_link_type"],
            }
        },
    )
    custom_name: Optional[str] = Field(
        default=None,
        description="""user readable name of the resource""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AnnotationMethodLinks"],
                "exact_mappings": ["cdp-common:annotation_method_link_custom_name"],
                "recommended": True,
            }
        },
    )

    @field_validator("link_type")
    def pattern_link_type(cls, v):
        pattern = re.compile(r"(^documentation$)|(^models_weights$)|(^other$)|(^source_code$)|(^website$)")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid link_type format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid link_type format: {v}"
            raise ValueError(err_msg)
        return v


class AnnotationSourceFile(ConfiguredBaseModel):
    """
    File and sourcing data for an annotation. Represents an entry in annotation.sources.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    glob_string: Optional[str] = Field(
        default=None,
        description="""Glob string to match annotation files in the dataset. Required if annotation_source_file_glob_strings is not provided.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_glob_string"],
            }
        },
    )
    glob_strings: Optional[list[str]] = Field(
        default=[],
        description="""Glob strings to match annotation files in the dataset. Required if annotation_source_file_glob_string is not provided.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_glob_strings"],
            }
        },
    )
    is_visualization_default: Optional[bool] = Field(
        default=False,
        description="""This annotation will be rendered in neuroglancer by default.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "Tomogram",
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_is_visualization_default"],
                "ifabsent": "False",
            }
        },
    )
    is_portal_standard: Optional[bool] = Field(
        default=False,
        description="""Whether the annotation source is a portal standard.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "Alignment",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_is_portal_standard"],
                "ifabsent": "False",
            }
        },
    )


class AnnotationOrientedPointFile(AnnotationSourceFile):
    """
    File and sourcing data for an oriented point annotation. Annotation that identifies points along with orientation in the volume.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"aliases": ["OrientedPoint"], "from_schema": "metadata"})

    file_format: Optional[OrientedPointAnnotationFileFormatEnum] = Field(
        default=None,
        description="""The format of the oriented point annotation file.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:oriented_point_annotation_file_format"],
            }
        },
    )
    binning: Optional[float] = Field(
        default=1,
        description="""The binning factor for a point / oriented point / instance segmentation annotation file.""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
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
        default=None,
        description="""The filter value for an oriented point / instance segmentation annotation file.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationOrientedPointFile",
                    "AnnotationPointFile",
                    "IdentifiedObjectList",
                    "AnnotationInstanceSegmentationFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_filter_value"],
            }
        },
    )
    order: Optional[str] = Field(
        default="xyz",
        description="""The order of axes for an oriented point / instance segmentation annotation file.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AnnotationOrientedPointFile", "AnnotationInstanceSegmentationFile"],
                "exact_mappings": ["cdp-common:annotation_source_file_order"],
                "ifabsent": "string(xyz)",
            }
        },
    )
    mesh_source_path: Optional[str] = Field(
        default=None,
        description="""The path to the mesh source file associated with an oriented point file.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AnnotationOrientedPointFile", "AnnotationInstanceSegmentationFile"],
                "exact_mappings": ["cdp-common:annotation_source_file_mesh_source_path"],
            }
        },
    )
    glob_string: Optional[str] = Field(
        default=None,
        description="""Glob string to match annotation files in the dataset. Required if annotation_source_file_glob_strings is not provided.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_glob_string"],
            }
        },
    )
    glob_strings: Optional[list[str]] = Field(
        default=[],
        description="""Glob strings to match annotation files in the dataset. Required if annotation_source_file_glob_string is not provided.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_glob_strings"],
            }
        },
    )
    is_visualization_default: Optional[bool] = Field(
        default=False,
        description="""This annotation will be rendered in neuroglancer by default.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "Tomogram",
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_is_visualization_default"],
                "ifabsent": "False",
            }
        },
    )
    is_portal_standard: Optional[bool] = Field(
        default=False,
        description="""Whether the annotation source is a portal standard.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "Alignment",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_is_portal_standard"],
                "ifabsent": "False",
            }
        },
    )

    @field_validator("file_format")
    def pattern_file_format(cls, v):
        pattern = re.compile(
            r"(^mod$)|(^relion3_star$)|(^relion4_star$)|(^tomoman_relion_star$)|(^copick$)|(^stopgap_star$)"
        )
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid file_format format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid file_format format: {v}"
            raise ValueError(err_msg)
        return v


class AnnotationInstanceSegmentationFile(AnnotationOrientedPointFile):
    """
    File and sourcing data for an instance segmentation annotation. Annotation that identifies individual instances of object shapes.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"aliases": ["InstanceSegmentation"], "from_schema": "metadata"})

    file_format: Optional[InstanceSegmentationAnnotationFileFormatEnum] = Field(
        default=None,
        description="""The format of the instance segmentation annotation file.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:instance_segmentation_annotation_file_format"],
            }
        },
    )
    binning: Optional[float] = Field(
        default=1,
        description="""The binning factor for a point / oriented point / instance segmentation annotation file.""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
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
        default=None,
        description="""The filter value for an oriented point / instance segmentation annotation file.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationOrientedPointFile",
                    "AnnotationPointFile",
                    "IdentifiedObjectList",
                    "AnnotationInstanceSegmentationFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_filter_value"],
            }
        },
    )
    order: Optional[str] = Field(
        default="xyz",
        description="""The order of axes for an oriented point / instance segmentation annotation file.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AnnotationOrientedPointFile", "AnnotationInstanceSegmentationFile"],
                "exact_mappings": ["cdp-common:annotation_source_file_order"],
                "ifabsent": "string(xyz)",
            }
        },
    )
    mesh_source_path: Optional[str] = Field(
        default=None,
        description="""The path to the mesh source file associated with an oriented point file.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AnnotationOrientedPointFile", "AnnotationInstanceSegmentationFile"],
                "exact_mappings": ["cdp-common:annotation_source_file_mesh_source_path"],
            }
        },
    )
    glob_string: Optional[str] = Field(
        default=None,
        description="""Glob string to match annotation files in the dataset. Required if annotation_source_file_glob_strings is not provided.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_glob_string"],
            }
        },
    )
    glob_strings: Optional[list[str]] = Field(
        default=[],
        description="""Glob strings to match annotation files in the dataset. Required if annotation_source_file_glob_string is not provided.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_glob_strings"],
            }
        },
    )
    is_visualization_default: Optional[bool] = Field(
        default=False,
        description="""This annotation will be rendered in neuroglancer by default.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "Tomogram",
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_is_visualization_default"],
                "ifabsent": "False",
            }
        },
    )
    is_portal_standard: Optional[bool] = Field(
        default=False,
        description="""Whether the annotation source is a portal standard.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "Alignment",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_is_portal_standard"],
                "ifabsent": "False",
            }
        },
    )

    @field_validator("file_format")
    def pattern_file_format(cls, v):
        pattern = re.compile(r"(^tardis$)|(^copick$)")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid file_format format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid file_format format: {v}"
            raise ValueError(err_msg)
        return v


class AnnotationPointFile(AnnotationSourceFile):
    """
    File and sourcing data for a point annotation. Annotation that identifies points in the volume.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"aliases": ["Point"], "from_schema": "metadata"})

    file_format: Optional[PointAnnotationFileFormatEnum] = Field(
        default=None,
        description="""The format of the point annotation file.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:point_annotation_file_format"],
            }
        },
    )
    binning: Optional[float] = Field(
        default=1,
        description="""The binning factor for a point / oriented point / instance segmentation annotation file.""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
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
        default="xyz",
        description="""The columns used in a point annotation file.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AnnotationPointFile"],
                "exact_mappings": ["cdp-common:annotation_source_file_columns"],
                "ifabsent": "string(xyz)",
            }
        },
    )
    delimiter: Optional[str] = Field(
        default=",",
        description="""The delimiter used in a point annotation file.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AnnotationPointFile"],
                "exact_mappings": ["cdp-common:annotation_source_file_delimiter"],
                "ifabsent": "string(,)",
            }
        },
    )
    filter_value: Optional[str] = Field(
        default=None,
        description="""The filter value for an oriented point / instance segmentation annotation file.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationOrientedPointFile",
                    "AnnotationPointFile",
                    "IdentifiedObjectList",
                    "AnnotationInstanceSegmentationFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_filter_value"],
            }
        },
    )
    glob_string: Optional[str] = Field(
        default=None,
        description="""Glob string to match annotation files in the dataset. Required if annotation_source_file_glob_strings is not provided.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_glob_string"],
            }
        },
    )
    glob_strings: Optional[list[str]] = Field(
        default=[],
        description="""Glob strings to match annotation files in the dataset. Required if annotation_source_file_glob_string is not provided.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_glob_strings"],
            }
        },
    )
    is_visualization_default: Optional[bool] = Field(
        default=False,
        description="""This annotation will be rendered in neuroglancer by default.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "Tomogram",
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_is_visualization_default"],
                "ifabsent": "False",
            }
        },
    )
    is_portal_standard: Optional[bool] = Field(
        default=False,
        description="""Whether the annotation source is a portal standard.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "Alignment",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_is_portal_standard"],
                "ifabsent": "False",
            }
        },
    )

    @field_validator("file_format")
    def pattern_file_format(cls, v):
        pattern = re.compile(
            r"(^csv$)|(^csv_with_header$)|(^tsv$)|(^mod$)|(^relion3_star$)|(^relion4_star$)|(^tomoman_relion_star$)|(^copick$)"
        )
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid file_format format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid file_format format: {v}"
            raise ValueError(err_msg)
        return v


class AnnotationSegmentationMaskFile(AnnotationSourceFile):
    """
    File and sourcing data for a segmentation mask annotation. Annotation that identifies an object.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"aliases": ["SegmentationMask"], "from_schema": "metadata"})

    file_format: Optional[VolumeAnnotationFileFormatEnum] = Field(
        default=None,
        description="""The format of the volume annotation file.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:volume_annotation_file_format"],
            }
        },
    )
    glob_string: Optional[str] = Field(
        default=None,
        description="""Glob string to match annotation files in the dataset. Required if annotation_source_file_glob_strings is not provided.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_glob_string"],
            }
        },
    )
    glob_strings: Optional[list[str]] = Field(
        default=[],
        description="""Glob strings to match annotation files in the dataset. Required if annotation_source_file_glob_string is not provided.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_glob_strings"],
            }
        },
    )
    is_visualization_default: Optional[bool] = Field(
        default=False,
        description="""This annotation will be rendered in neuroglancer by default.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "Tomogram",
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_is_visualization_default"],
                "ifabsent": "False",
            }
        },
    )
    is_portal_standard: Optional[bool] = Field(
        default=False,
        description="""Whether the annotation source is a portal standard.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "Alignment",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_is_portal_standard"],
                "ifabsent": "False",
            }
        },
    )

    @field_validator("file_format")
    def pattern_file_format(cls, v):
        pattern = re.compile(r"(^mrc$)|(^zarr$)")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid file_format format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid file_format format: {v}"
            raise ValueError(err_msg)
        return v


class AnnotationSemanticSegmentationMaskFile(AnnotationSourceFile):
    """
    File and sourcing data for a semantic segmentation mask annotation. Annotation that identifies classes of objects.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"aliases": ["SemanticSegmentationMask"], "from_schema": "metadata"})

    file_format: Optional[VolumeAnnotationFileFormatEnum] = Field(
        default=None,
        description="""The format of the volume annotation file.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:volume_annotation_file_format"],
            }
        },
    )
    mask_label: Optional[int] = Field(
        default=1,
        description="""The mask label for a semantic segmentation mask annotation file.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AnnotationSemanticSegmentationMaskFile"],
                "exact_mappings": ["cdp-common:annotation_source_file_mask_label"],
                "ifabsent": "int(1)",
            }
        },
    )
    rescale: Optional[bool] = Field(
        default=False,
        description="""Whether the annotation file needs to be rescaled.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AnnotationSemanticSegmentationMaskFile"],
                "exact_mappings": ["cdp-common:annotation_source_file_rescale"],
                "ifabsent": "False",
            }
        },
    )
    threshold: Optional[float] = Field(
        default=None,
        description="""The threshold for a segmentation mask annotation file.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AnnotationSemanticSegmentationMaskFile"],
                "exact_mappings": ["cdp-common:annotation_source_file_threshold"],
            }
        },
    )
    glob_string: Optional[str] = Field(
        default=None,
        description="""Glob string to match annotation files in the dataset. Required if annotation_source_file_glob_strings is not provided.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_glob_string"],
            }
        },
    )
    glob_strings: Optional[list[str]] = Field(
        default=[],
        description="""Glob strings to match annotation files in the dataset. Required if annotation_source_file_glob_string is not provided.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_glob_strings"],
            }
        },
    )
    is_visualization_default: Optional[bool] = Field(
        default=False,
        description="""This annotation will be rendered in neuroglancer by default.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "Tomogram",
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_is_visualization_default"],
                "ifabsent": "False",
            }
        },
    )
    is_portal_standard: Optional[bool] = Field(
        default=False,
        description="""Whether the annotation source is a portal standard.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "Alignment",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_is_portal_standard"],
                "ifabsent": "False",
            }
        },
    )

    @field_validator("file_format")
    def pattern_file_format(cls, v):
        pattern = re.compile(r"(^mrc$)|(^zarr$)")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid file_format format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid file_format format: {v}"
            raise ValueError(err_msg)
        return v


class AnnotationTriangularMeshFile(AnnotationSourceFile):
    """
    File and sourcing data for a triangular mesh annotation. Annotation that identifies an object.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"aliases": ["TriangularMesh"], "from_schema": "metadata"})

    file_format: Optional[TriangularMeshAnnotationFileFormatEnum] = Field(
        default=None,
        description="""The format of the triangular mesh annotation file.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:triangular_mesh_annotation_file_format"],
            }
        },
    )
    scale_factor: Optional[float] = Field(
        default=1,
        description="""The scale factor for a mesh annotation file.""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AnnotationTriangularMeshFile", "AnnotationTriangularMeshGroupFile"],
                "exact_mappings": ["cdp-common:annotation_source_file_scale_factor"],
                "ifabsent": "float(1)",
            }
        },
    )
    glob_string: Optional[str] = Field(
        default=None,
        description="""Glob string to match annotation files in the dataset. Required if annotation_source_file_glob_strings is not provided.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_glob_string"],
            }
        },
    )
    glob_strings: Optional[list[str]] = Field(
        default=[],
        description="""Glob strings to match annotation files in the dataset. Required if annotation_source_file_glob_string is not provided.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_glob_strings"],
            }
        },
    )
    is_visualization_default: Optional[bool] = Field(
        default=False,
        description="""This annotation will be rendered in neuroglancer by default.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "Tomogram",
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_is_visualization_default"],
                "ifabsent": "False",
            }
        },
    )
    is_portal_standard: Optional[bool] = Field(
        default=False,
        description="""Whether the annotation source is a portal standard.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "Alignment",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_is_portal_standard"],
                "ifabsent": "False",
            }
        },
    )

    @field_validator("file_format")
    def pattern_file_format(cls, v):
        pattern = re.compile(r"(^obj$)|(^stl$)|(^vtk$)|(^glb$)")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid file_format format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid file_format format: {v}"
            raise ValueError(err_msg)
        return v


class AnnotationTriangularMeshGroupFile(AnnotationSourceFile):
    """
    File and sourcing data containing one or more triangular mesh annotations.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"aliases": ["TriangularMeshGroup"], "from_schema": "metadata"})

    file_format: Optional[TriangularMeshAnnotationGroupFileFormatEnum] = Field(
        default=None,
        description="""The format of the triangular mesh annotation group file.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:triangular_mesh_annotation_group_file_format"],
            }
        },
    )
    scale_factor: Optional[float] = Field(
        default=1,
        description="""The scale factor for a mesh annotation file.""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AnnotationTriangularMeshFile", "AnnotationTriangularMeshGroupFile"],
                "exact_mappings": ["cdp-common:annotation_source_file_scale_factor"],
                "ifabsent": "float(1)",
            }
        },
    )
    name: Optional[str] = Field(
        default=None,
        description="""The name that identifies to a single annotation mesh among multiple meshes.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "Assay",
                    "DevelopmentStageDetails",
                    "Disease",
                    "OrganismDetails",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                    "AnnotationTriangularMeshGroupFile",
                    "AuthorMixin",
                    "Author",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_mesh_name"],
            }
        },
    )
    glob_string: Optional[str] = Field(
        default=None,
        description="""Glob string to match annotation files in the dataset. Required if annotation_source_file_glob_strings is not provided.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_glob_string"],
            }
        },
    )
    glob_strings: Optional[list[str]] = Field(
        default=[],
        description="""Glob strings to match annotation files in the dataset. Required if annotation_source_file_glob_string is not provided.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_glob_strings"],
            }
        },
    )
    is_visualization_default: Optional[bool] = Field(
        default=False,
        description="""This annotation will be rendered in neuroglancer by default.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "Tomogram",
                    "AnnotationSourceFile",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_is_visualization_default"],
                "ifabsent": "False",
            }
        },
    )
    is_portal_standard: Optional[bool] = Field(
        default=False,
        description="""Whether the annotation source is a portal standard.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "Alignment",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ],
                "exact_mappings": ["cdp-common:annotation_source_file_is_portal_standard"],
                "ifabsent": "False",
            }
        },
    )

    @field_validator("file_format")
    def pattern_file_format(cls, v):
        pattern = re.compile(r"^hff$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid file_format format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid file_format format: {v}"
            raise ValueError(err_msg)
        return v


class IdentifiedObject(ConfiguredBaseModel):
    """
    Metadata describing an identified object.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    object_id: str = Field(
        default=...,
        description="""Gene Ontology Cellular Component identifier or UniProtKB accession for the identified object.""",
        json_schema_extra={
            "linkml_meta": {
                "any_of": [{"range": "GO_ID"}, {"range": "UNIPROT_ID"}],
                "domain_of": ["IdentifiedObject"],
                "exact_mappings": ["cdp-common:identified_object_id"],
            }
        },
    )
    object_name: str = Field(
        default=...,
        description="""Name of the object that was identified (e.g. ribosome, nuclear pore complex, actin filament, membrane)""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["IdentifiedObject"], "exact_mappings": ["cdp-common:identified_object_name"]}
        },
    )
    object_description: Optional[str] = Field(
        default=None,
        description="""A textual description of the identified object, can be a longer description to include additional information not covered by the identified object name and state.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["IdentifiedObject"],
                "exact_mappings": ["cdp-common:identified_object_description"],
            }
        },
    )
    object_state: Optional[str] = Field(
        default=None,
        description="""Molecule state identified (e.g. open, closed)""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["IdentifiedObject"], "exact_mappings": ["cdp-common:identified_object_state"]}
        },
    )

    @field_validator("object_id")
    def pattern_object_id(cls, v):
        pattern = re.compile(
            r"(^GO:[0-9]{7}$)|(^UniProtKB:[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}$)"
        )
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid object_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid object_id format: {v}"
            raise ValueError(err_msg)
        return v


class IdentifiedObjectList(ConfiguredBaseModel):
    """
    Metadata for a list of identified objects.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    filter_value: Optional[str] = Field(
        default=None,
        description="""Filter value for the identified object, used to filter the list of identified objects by run name.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationOrientedPointFile",
                    "AnnotationPointFile",
                    "IdentifiedObjectList",
                    "AnnotationInstanceSegmentationFile",
                ],
                "exact_mappings": ["cdp-common:identified_object_filter_value"],
            }
        },
    )


class Annotation(AuthoredEntity, DateStampedEntity):
    """
    Metadata describing an annotation.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "metadata", "mixins": ["DateStampedEntity", "AuthoredEntity"]}
    )

    annotation_method: str = Field(
        default=...,
        description="""Describe how the annotation is made (e.g. Manual, crYoLO, Positive Unlabeled Learning, template matching)""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["Annotation"], "exact_mappings": ["cdp-common:annotation_method"]}
        },
    )
    annotation_object: AnnotationObject = Field(
        default=...,
        description="""Metadata describing the object being annotated.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Annotation"]}},
    )
    annotation_publications: Optional[str] = Field(
        default=None,
        description="""List of publication IDs (EMPIAR, EMDB, DOI, PDB) that describe this annotation method. Comma separated.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["Annotation"], "exact_mappings": ["cdp-common:annotation_publications"]}
        },
    )
    annotation_software: Optional[str] = Field(
        default=None,
        description="""Software used for generating this annotation""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["Annotation"],
                "exact_mappings": ["cdp-common:annotation_software"],
                "recommended": True,
            }
        },
    )
    confidence: Optional[AnnotationConfidence] = Field(
        default=None,
        description="""Metadata describing the confidence of an annotation.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Annotation"]}},
    )
    files: Optional[list[AnnotationSourceFile]] = Field(
        default=[],
        description="""File and sourcing data for an annotation. Represents an entry in annotation.sources.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Annotation"], "list_elements_ordered": True}},
    )
    ground_truth_status: Optional[bool] = Field(
        default=False,
        description="""Whether an annotation is considered ground truth, as determined by the annotator.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["Annotation"],
                "exact_mappings": ["cdp-common:annotation_ground_truth_status"],
                "ifabsent": "False",
                "recommended": True,
            }
        },
    )
    is_curator_recommended: Optional[bool] = Field(
        default=False,
        description="""This annotation is recommended by the curator to be preferred for this object type.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["Annotation"],
                "exact_mappings": ["cdp-common:annotation_is_curator_recommended"],
                "ifabsent": "False",
            }
        },
    )
    method_type: AnnotationMethodTypeEnum = Field(
        default=...,
        description="""Classification of the annotation method based on supervision.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["Annotation", "Alignment"],
                "exact_mappings": ["cdp-common:annotation_method_type"],
            }
        },
    )
    method_links: Optional[list[AnnotationMethodLinks]] = Field(
        default=[],
        description="""A set of links to models, source code, documentation, etc referenced by annotation the method""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Annotation"]}},
    )
    object_count: Optional[int] = Field(
        default=None,
        description="""Number of objects identified""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["Annotation"], "exact_mappings": ["cdp-common:annotation_object_count"]}
        },
    )
    version: Optional[float] = Field(
        default=None,
        description="""Version of annotation.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["Annotation"], "exact_mappings": ["cdp-common:annotation_version"]}
        },
    )
    dates: DateStamp = Field(
        default=...,
        description="""A set of dates at which a data item was deposited, published and last modified.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["DateStampedEntity", "Tomogram", "Dataset", "Deposition", "Annotation"]}
        },
    )
    authors: list[Author] = Field(
        default=...,
        description="""Author of a scientific data entity.""",
        min_length=1,
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AuthoredEntity", "Dataset", "Deposition", "Tomogram", "Annotation"],
                "list_elements_ordered": True,
            }
        },
    )

    @field_validator("annotation_publications")
    def pattern_annotation_publications(cls, v):
        pattern = re.compile(
            r"^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+|PDB-[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+|PDB-[0-9a-zA-Z]{4,8}))*$"
        )
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid annotation_publications format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid annotation_publications format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("method_type")
    def pattern_method_type(cls, v):
        pattern = re.compile(r"(^manual$)|(^automated$)|(^hybrid$)|(^simulated$)")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid method_type format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid method_type format: {v}"
            raise ValueError(err_msg)
        return v


class AlignmentSize(ConfiguredBaseModel):
    """
    The size of an alignment in voxels in each dimension.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    x: Union[float, str] = Field(
        default=...,
        description="""X dimension of the reconstruction volume in angstrom""",
        json_schema_extra={
            "linkml_meta": {
                "any_of": [{"range": "float"}, {"range": "FloatFormattedString"}],
                "domain_of": ["TiltSeriesSize", "TomogramSize", "TomogramOffset", "AlignmentSize", "AlignmentOffset"],
                "unit": {"descriptive_name": "Angstrom", "symbol": "Å"},
            }
        },
    )
    y: Union[float, str] = Field(
        default=...,
        description="""Y dimension of the reconstruction volume in angstrom""",
        json_schema_extra={
            "linkml_meta": {
                "any_of": [{"range": "float"}, {"range": "FloatFormattedString"}],
                "domain_of": ["TiltSeriesSize", "TomogramSize", "TomogramOffset", "AlignmentSize", "AlignmentOffset"],
                "unit": {"descriptive_name": "Angstrom", "symbol": "Å"},
            }
        },
    )
    z: Union[float, str] = Field(
        default=...,
        description="""Z dimension of the reconstruction volume in angstrom""",
        json_schema_extra={
            "linkml_meta": {
                "any_of": [{"range": "float"}, {"range": "FloatFormattedString"}],
                "domain_of": ["TiltSeriesSize", "TomogramSize", "TomogramOffset", "AlignmentSize", "AlignmentOffset"],
                "unit": {"descriptive_name": "Angstrom", "symbol": "Å"},
            }
        },
    )

    @field_validator("x")
    def pattern_x(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid x format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid x format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("y")
    def pattern_y(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid y format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid y format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("z")
    def pattern_z(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid z format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid z format: {v}"
            raise ValueError(err_msg)
        return v


class AlignmentOffset(ConfiguredBaseModel):
    """
    The offset of a alignment in voxels in each dimension relative to the canonical tomogram.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    x: Union[float, str] = Field(
        default=...,
        description="""X shift of the reconstruction volume in angstrom""",
        json_schema_extra={
            "linkml_meta": {
                "any_of": [{"range": "float"}, {"range": "FloatFormattedString"}],
                "domain_of": ["TiltSeriesSize", "TomogramSize", "TomogramOffset", "AlignmentSize", "AlignmentOffset"],
                "unit": {"descriptive_name": "Angstrom", "symbol": "Å"},
            }
        },
    )
    y: Union[float, str] = Field(
        default=...,
        description="""Y shift of the reconstruction volume in angstrom""",
        json_schema_extra={
            "linkml_meta": {
                "any_of": [{"range": "float"}, {"range": "FloatFormattedString"}],
                "domain_of": ["TiltSeriesSize", "TomogramSize", "TomogramOffset", "AlignmentSize", "AlignmentOffset"],
                "unit": {"descriptive_name": "Angstrom", "symbol": "Å"},
            }
        },
    )
    z: Union[float, str] = Field(
        default=...,
        description="""Z shift of the reconstruction volume in angstrom""",
        json_schema_extra={
            "linkml_meta": {
                "any_of": [{"range": "float"}, {"range": "FloatFormattedString"}],
                "domain_of": ["TiltSeriesSize", "TomogramSize", "TomogramOffset", "AlignmentSize", "AlignmentOffset"],
                "unit": {"descriptive_name": "Angstrom", "symbol": "Å"},
            }
        },
    )

    @field_validator("x")
    def pattern_x(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid x format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid x format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("y")
    def pattern_y(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid y format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid y format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("z")
    def pattern_z(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid z format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid z format: {v}"
            raise ValueError(err_msg)
        return v


class PerSectionAlignmentParameters(ConfiguredBaseModel):
    """
    Alignment parameters for one section of a tilt series.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    z_index: int = Field(
        default=...,
        description="""z-index of the frame in the tiltseries""",
        ge=0,
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["PerSectionParameter", "PerSectionAlignmentParameters"],
                "exact_mappings": ["cdp-common:per_section_z_index"],
            }
        },
    )
    tilt_angle: Optional[float] = Field(
        default=None,
        description="""Tilt angle of the projection in degrees""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["PerSectionAlignmentParameters"],
                "exact_mappings": ["cdp-common:per_section_alignment_tilt_angle"],
                "unit": {"descriptive_name": "degrees", "symbol": "°"},
            }
        },
    )
    volume_x_rotation: Optional[float] = Field(
        default=None,
        description="""Additional X rotation of the reconstruction volume in degrees""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["PerSectionAlignmentParameters"],
                "exact_mappings": ["cdp-common:alignment_volume_x_rotation"],
                "unit": {"descriptive_name": "degrees", "symbol": "°"},
            }
        },
    )
    in_plane_rotation: Optional[
        conlist(min_length=2, max_length=2, item_type=conlist(min_length=2, max_length=2, item_type=float))
    ] = Field(
        default=None,
        description="""In-plane rotation of the projection as a rotation matrix.""",
        json_schema_extra={
            "linkml_meta": {
                "array": {
                    "dimensions": [{"exact_cardinality": 2}, {"exact_cardinality": 2}],
                    "exact_number_dimensions": 2,
                },
                "domain_of": ["PerSectionAlignmentParameters"],
            }
        },
    )
    x_offset: Optional[float] = Field(
        default=None,
        description="""In-plane X-shift of the projection in angstrom""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["PerSectionAlignmentParameters"],
                "exact_mappings": ["cdp-common:per_section_alignment_x_offset"],
                "unit": {"descriptive_name": "Angstrom", "symbol": "Å"},
            }
        },
    )
    y_offset: Optional[float] = Field(
        default=None,
        description="""In-plane Y-shift of the projection in angstrom""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["PerSectionAlignmentParameters"],
                "exact_mappings": ["cdp-common:per_section_alignment_y_offset"],
                "unit": {"descriptive_name": "Angstrom", "symbol": "Å"},
            }
        },
    )
    beam_tilt: Optional[float] = Field(
        default=None,
        description="""Beam tilt during projection in degrees""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["PerSectionAlignmentParameters"],
                "exact_mappings": ["cdp-common:per_section_alignment_beam_tilt"],
                "unit": {"descriptive_name": "degrees", "symbol": "°"},
            }
        },
    )


class Alignment(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    alignment_type: Optional[AlignmentTypeEnum] = Field(
        default=None,
        description="""The type of alignment.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Alignment"]}},
    )
    volume_offset: Optional[AlignmentOffset] = Field(
        default=None,
        description="""The offset of a alignment in voxels in each dimension relative to the canonical tomogram.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Alignment"]}},
    )
    volume_dimension: Optional[AlignmentSize] = Field(
        default=None,
        description="""The size of an alignment in voxels in each dimension.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Alignment"]}},
    )
    x_rotation_offset: Optional[Union[int, str]] = Field(
        default=None,
        description="""The x rotation offset relative to the tomogram.""",
        json_schema_extra={
            "linkml_meta": {
                "any_of": [{"range": "integer"}, {"range": "IntegerFormattedString"}],
                "domain_of": ["Alignment"],
            }
        },
    )
    tilt_offset: Optional[float] = Field(
        default=None,
        description="""The tilt offset relative to the tomogram.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Alignment"]}},
    )
    affine_transformation_matrix: Optional[
        conlist(min_length=4, max_length=4, item_type=conlist(min_length=4, max_length=4, item_type=float))
    ] = Field(
        default=None,
        description="""The flip or rotation transformation of this author submitted tomogram is indicated here. The default value if not present, is an identity matrix.""",
        json_schema_extra={
            "linkml_meta": {
                "array": {
                    "dimensions": [{"exact_cardinality": 4}, {"exact_cardinality": 4}],
                    "exact_number_dimensions": 2,
                },
                "domain_of": ["Tomogram", "Alignment"],
            }
        },
    )
    is_portal_standard: Optional[bool] = Field(
        default=None,
        description="""Whether the alignment is standardized for the portal.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AnnotationSourceFile",
                    "Alignment",
                    "AnnotationOrientedPointFile",
                    "AnnotationInstanceSegmentationFile",
                    "AnnotationPointFile",
                    "AnnotationSegmentationMaskFile",
                    "AnnotationSemanticSegmentationMaskFile",
                    "AnnotationTriangularMeshFile",
                    "AnnotationTriangularMeshGroupFile",
                ]
            }
        },
    )
    format: AlignmentFormatEnum = Field(
        default=...,
        description="""The format of the alignment.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Alignment", "Ctf"]}},
    )
    method_type: Optional[AlignmentMethodTypeEnum] = Field(
        default=None,
        description="""The alignment method type.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Annotation", "Alignment"]}},
    )

    @field_validator("alignment_type")
    def pattern_alignment_type(cls, v):
        pattern = re.compile(r"(^LOCAL$)|(^GLOBAL$)")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid alignment_type format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid alignment_type format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("x_rotation_offset")
    def pattern_x_rotation_offset(cls, v):
        pattern = re.compile(r"^int[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid x_rotation_offset format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid x_rotation_offset format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("format")
    def pattern_format(cls, v):
        pattern = re.compile(r"(^IMOD$)|(^ARETOMO3$)")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid format format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid format format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("method_type")
    def pattern_method_type(cls, v):
        pattern = re.compile(r"(^fiducial_based$)|(^patch_tracking$)|(^projection_matching$)|(^undefined$)")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid method_type format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid method_type format: {v}"
            raise ValueError(err_msg)
        return v


class Frame(ConfiguredBaseModel):
    """
    A frame entity.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    dose_rate: Union[float, str] = Field(
        default=...,
        description="""The dose exposure for a given frame.""",
        json_schema_extra={
            "linkml_meta": {"any_of": [{"range": "float"}, {"range": "FloatFormattedString"}], "domain_of": ["Frame"]}
        },
    )
    is_gain_corrected: Optional[bool] = Field(
        default=None,
        description="""Is the frame gain corrected""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Frame"]}},
    )

    @field_validator("dose_rate")
    def pattern_dose_rate(cls, v):
        pattern = re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid dose_rate format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid dose_rate format: {v}"
            raise ValueError(err_msg)
        return v


class Ctf(ConfiguredBaseModel):
    """
    A ctf entity.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata"})

    format: CtfFormatEnum = Field(
        default=...,
        description="""The format of the ctf file.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Alignment", "Ctf"]}},
    )

    @field_validator("format")
    def pattern_format(cls, v):
        pattern = re.compile(r"(^CTFFIND$)|(^Gctf$)|(^IMOD$)")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid format format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid format format: {v}"
            raise ValueError(err_msg)
        return v


class DateStampedEntityMixin(ConfiguredBaseModel):
    """
    A set of dates at which a data item was deposited, published and last modified.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata", "mixin": True})

    deposition_date: date = Field(
        default=...,
        description="""The date a data item was received by the cryoET data portal.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["DateStampedEntityMixin", "DateStamp"],
                "exact_mappings": ["cdp-common:deposition_date"],
            }
        },
    )
    release_date: date = Field(
        default=...,
        description="""The date a data item was received by the cryoET data portal.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["DateStampedEntityMixin", "DateStamp"],
                "exact_mappings": ["cdp-common:release_date"],
            }
        },
    )
    last_modified_date: date = Field(
        default=...,
        description="""The date a piece of data was last modified on the cryoET data portal.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["DateStampedEntityMixin", "DateStamp"],
                "exact_mappings": ["cdp-common:last_modified_date"],
            }
        },
    )


class DateStamp(DateStampedEntityMixin):
    """
    A set of dates at which a data item was deposited, published and last modified.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata", "mixins": ["DateStampedEntityMixin"]})

    deposition_date: date = Field(
        default=...,
        description="""The date a data item was received by the cryoET data portal.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["DateStampedEntityMixin", "DateStamp"],
                "exact_mappings": ["cdp-common:deposition_date"],
            }
        },
    )
    release_date: date = Field(
        default=...,
        description="""The date a data item was received by the cryoET data portal.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["DateStampedEntityMixin", "DateStamp"],
                "exact_mappings": ["cdp-common:release_date"],
            }
        },
    )
    last_modified_date: date = Field(
        default=...,
        description="""The date a piece of data was last modified on the cryoET data portal.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["DateStampedEntityMixin", "DateStamp"],
                "exact_mappings": ["cdp-common:last_modified_date"],
            }
        },
    )


class CrossReferencesMixin(ConfiguredBaseModel):
    """
    A set of cross-references to other databases and publications.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata", "mixin": True})

    publications: Optional[str] = Field(
        default=None,
        description="""Comma-separated list of DOIs for publications associated with the dataset.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["CrossReferencesMixin", "CrossReferences"], "recommended": True}
        },
    )
    related_database_entries: Optional[str] = Field(
        default=None,
        description="""Comma-separated list of related database entries for the dataset.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["CrossReferencesMixin", "CrossReferences"], "recommended": True}
        },
    )
    related_database_links: Optional[str] = Field(
        default=None,
        description="""Comma-separated list of related database links for the dataset.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["CrossReferencesMixin", "CrossReferences"]}},
    )
    dataset_citations: Optional[str] = Field(
        default=None,
        description="""Comma-separated list of DOIs for publications citing the dataset.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["CrossReferencesMixin", "CrossReferences"]}},
    )

    @field_validator("publications")
    def pattern_publications(cls, v):
        pattern = re.compile(
            r"(^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+(\s*,\s*(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)*$)|(^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+(\s*,\s*(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)*$)"
        )
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid publications format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid publications format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("related_database_entries")
    def pattern_related_database_entries(cls, v):
        pattern = re.compile(
            r"(^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|PDB-[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|PDB-[0-9a-zA-Z]{4,8}))*$)|(^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|PDB-[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|PDB-[0-9a-zA-Z]{4,8}))*$)"
        )
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid related_database_entries format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid related_database_entries format: {v}"
            raise ValueError(err_msg)
        return v


class CrossReferences(CrossReferencesMixin):
    """
    A set of cross-references to other databases and publications.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata", "mixins": ["CrossReferencesMixin"]})

    publications: Optional[str] = Field(
        default=None,
        description="""Comma-separated list of DOIs for publications associated with the dataset.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["CrossReferencesMixin", "CrossReferences"], "recommended": True}
        },
    )
    related_database_entries: Optional[str] = Field(
        default=None,
        description="""Comma-separated list of related database entries for the dataset.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["CrossReferencesMixin", "CrossReferences"], "recommended": True}
        },
    )
    related_database_links: Optional[str] = Field(
        default=None,
        description="""Comma-separated list of related database links for the dataset.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["CrossReferencesMixin", "CrossReferences"]}},
    )
    dataset_citations: Optional[str] = Field(
        default=None,
        description="""Comma-separated list of DOIs for publications citing the dataset.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["CrossReferencesMixin", "CrossReferences"]}},
    )

    @field_validator("publications")
    def pattern_publications(cls, v):
        pattern = re.compile(
            r"(^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+(\s*,\s*(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)*$)|(^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+(\s*,\s*(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)*$)"
        )
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid publications format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid publications format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator("related_database_entries")
    def pattern_related_database_entries(cls, v):
        pattern = re.compile(
            r"(^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|PDB-[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|PDB-[0-9a-zA-Z]{4,8}))*$)|(^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|PDB-[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|PDB-[0-9a-zA-Z]{4,8}))*$)"
        )
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid related_database_entries format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid related_database_entries format: {v}"
            raise ValueError(err_msg)
        return v


class AuthorMixin(ConfiguredBaseModel):
    """
    An entity with author data
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata", "mixin": True})

    name: str = Field(
        default=...,
        description="""The full name of the author.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AuthorMixin",
                    "Assay",
                    "DevelopmentStageDetails",
                    "Disease",
                    "OrganismDetails",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                    "AnnotationTriangularMeshGroupFile",
                    "Author",
                ],
                "exact_mappings": ["cdp-common:author_name"],
            }
        },
    )
    email: Optional[str] = Field(
        default=None,
        description="""The email address of the author.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["AuthorMixin", "Author"], "exact_mappings": ["cdp-common:author_email"]}
        },
    )
    affiliation_name: Optional[str] = Field(
        default=None,
        description="""The name of the author's affiliation.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AuthorMixin", "Author"],
                "exact_mappings": ["cdp-common:author_affiliation_name"],
            }
        },
    )
    affiliation_address: Optional[str] = Field(
        default=None,
        description="""The address of the author's affiliation.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AuthorMixin", "Author"],
                "exact_mappings": ["cdp-common:author_affiliation_address"],
            }
        },
    )
    affiliation_identifier: Optional[str] = Field(
        default=None,
        description="""A Research Organization Registry (ROR) identifier.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AuthorMixin", "Author"],
                "exact_mappings": ["cdp-common:author_affiliation_identifier"],
                "recommended": True,
            }
        },
    )
    corresponding_author_status: Optional[bool] = Field(
        default=False,
        description="""Whether the author is a corresponding author.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AuthorMixin", "Author"],
                "exact_mappings": ["cdp-common:author_corresponding_author_status"],
                "ifabsent": "False",
            }
        },
    )
    primary_author_status: Optional[bool] = Field(
        default=False,
        description="""Whether the author is a primary author.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AuthorMixin", "Author"],
                "exact_mappings": ["cdp-common:author_primary_author_status"],
                "ifabsent": "False",
            }
        },
    )
    kaggle_id: Optional[str] = Field(
        default=None,
        description="""Identifying string for the author's kaggle profile (found after 'kaggle.com/').""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["AuthorMixin", "Author"], "exact_mappings": ["cdp-common:kaggle_id"]}
        },
    )


class Author(AuthorMixin):
    """
    Author of a scientific data entity.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "metadata", "mixins": ["AuthorMixin"]})

    ORCID: Optional[str] = Field(
        default=None,
        description="""The ORCID identifier for the author.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["Author"], "exact_mappings": ["cdp-common:author_orcid"], "recommended": True}
        },
    )
    kaggle_id: Optional[str] = Field(
        default=None,
        description="""Identifying string for the author's kaggle profile (found after 'kaggle.com/').""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["Author", "AuthorMixin"], "exact_mappings": ["cdp-common:kaggle_id"]}
        },
    )
    name: str = Field(
        default=...,
        description="""The full name of the author.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": [
                    "AuthorMixin",
                    "Assay",
                    "DevelopmentStageDetails",
                    "Disease",
                    "OrganismDetails",
                    "TissueDetails",
                    "CellType",
                    "CellStrain",
                    "CellComponent",
                    "AnnotationObject",
                    "AnnotationTriangularMeshGroupFile",
                    "Author",
                ],
                "exact_mappings": ["cdp-common:author_name"],
            }
        },
    )
    email: Optional[str] = Field(
        default=None,
        description="""The email address of the author.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["AuthorMixin", "Author"], "exact_mappings": ["cdp-common:author_email"]}
        },
    )
    affiliation_name: Optional[str] = Field(
        default=None,
        description="""The name of the author's affiliation.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AuthorMixin", "Author"],
                "exact_mappings": ["cdp-common:author_affiliation_name"],
            }
        },
    )
    affiliation_address: Optional[str] = Field(
        default=None,
        description="""The address of the author's affiliation.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AuthorMixin", "Author"],
                "exact_mappings": ["cdp-common:author_affiliation_address"],
            }
        },
    )
    affiliation_identifier: Optional[str] = Field(
        default=None,
        description="""A Research Organization Registry (ROR) identifier.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AuthorMixin", "Author"],
                "exact_mappings": ["cdp-common:author_affiliation_identifier"],
                "recommended": True,
            }
        },
    )
    corresponding_author_status: Optional[bool] = Field(
        default=False,
        description="""Whether the author is a corresponding author.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AuthorMixin", "Author"],
                "exact_mappings": ["cdp-common:author_corresponding_author_status"],
                "ifabsent": "False",
            }
        },
    )
    primary_author_status: Optional[bool] = Field(
        default=False,
        description="""Whether the author is a primary author.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["AuthorMixin", "Author"],
                "exact_mappings": ["cdp-common:author_primary_author_status"],
                "ifabsent": "False",
            }
        },
    )

    @field_validator("ORCID")
    def pattern_ORCID(cls, v):
        pattern = re.compile(r"[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid ORCID format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid ORCID format: {v}"
            raise ValueError(err_msg)
        return v


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
PicturePath.model_rebuild()
MetadataPicturePath.model_rebuild()
FundingDetails.model_rebuild()
DateStampedEntity.model_rebuild()
AuthoredEntity.model_rebuild()
FundedEntity.model_rebuild()
CrossReferencedEntity.model_rebuild()
PicturedEntity.model_rebuild()
PicturedMetadataEntity.model_rebuild()
Assay.model_rebuild()
DevelopmentStageDetails.model_rebuild()
Disease.model_rebuild()
OrganismDetails.model_rebuild()
TissueDetails.model_rebuild()
CellType.model_rebuild()
CellStrain.model_rebuild()
CellComponent.model_rebuild()
ExperimentMetadata.model_rebuild()
Dataset.model_rebuild()
Deposition.model_rebuild()
CameraDetails.model_rebuild()
MicroscopeDetails.model_rebuild()
MicroscopeOpticalSetup.model_rebuild()
TiltRange.model_rebuild()
PerSectionParameter.model_rebuild()
TiltSeriesSize.model_rebuild()
TiltSeries.model_rebuild()
TomogramSize.model_rebuild()
TomogramOffset.model_rebuild()
Tomogram.model_rebuild()
AnnotationConfidence.model_rebuild()
AnnotationObject.model_rebuild()
AnnotationMethodLinks.model_rebuild()
AnnotationSourceFile.model_rebuild()
AnnotationOrientedPointFile.model_rebuild()
AnnotationInstanceSegmentationFile.model_rebuild()
AnnotationPointFile.model_rebuild()
AnnotationSegmentationMaskFile.model_rebuild()
AnnotationSemanticSegmentationMaskFile.model_rebuild()
AnnotationTriangularMeshFile.model_rebuild()
AnnotationTriangularMeshGroupFile.model_rebuild()
IdentifiedObject.model_rebuild()
IdentifiedObjectList.model_rebuild()
Annotation.model_rebuild()
AlignmentSize.model_rebuild()
AlignmentOffset.model_rebuild()
PerSectionAlignmentParameters.model_rebuild()
Alignment.model_rebuild()
Frame.model_rebuild()
Ctf.model_rebuild()
DateStampedEntityMixin.model_rebuild()
DateStamp.model_rebuild()
CrossReferencesMixin.model_rebuild()
CrossReferences.model_rebuild()
AuthorMixin.model_rebuild()
Author.model_rebuild()
