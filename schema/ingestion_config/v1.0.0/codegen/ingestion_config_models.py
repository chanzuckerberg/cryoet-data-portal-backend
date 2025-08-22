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
    ClassVar,
    List,
    Literal,
    Dict,
    Optional,
    Union
)
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator,
    conlist
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




class LinkMLMeta(RootModel):
    root: Dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'cdp-ingestion-config/',
     'description': 'Schema for ingestion configs',
     'id': 'cdp-ingestion-config',
     'imports': ['linkml:types',
                 '../../../core/v2.0.0/codegen/metadata_materialized',
                 '../../../core/v2.0.0/common'],
     'name': 'cdp-ingestion-config',
     'prefixes': {'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'}},
     'source_file': 'ingestion_config/v1.0.0/codegen/ingestion_config_models_materialized.yaml',
     'types': {'BTO_ID': {'base': 'str',
                          'description': 'A BRENDA Tissue Ontology identifier',
                          'from_schema': 'cdp-ingestion-config',
                          'name': 'BTO_ID',
                          'pattern': '^BTO:[0-9]{7}$'},
               'CC_ID': {'base': 'str',
                         'description': 'A Cell Culture Collection identifier',
                         'from_schema': 'cdp-ingestion-config',
                         'name': 'CC_ID',
                         'pattern': '^CC-[0-9]{4}$'},
               'CL_ID': {'base': 'str',
                         'description': 'A Cell Ontology identifier',
                         'from_schema': 'cdp-ingestion-config',
                         'name': 'CL_ID',
                         'pattern': '^CL:[0-9]{7}$'},
               'CVCL_ID': {'base': 'str',
                           'description': 'A Cellosaurus identifier',
                           'from_schema': 'cdp-ingestion-config',
                           'name': 'CVCL_ID',
                           'pattern': '^CVCL_[A-Z0-9]{4,}$'},
               'DOI': {'base': 'str',
                       'description': 'A Digital Object Identifier',
                       'from_schema': 'cdp-ingestion-config',
                       'name': 'DOI',
                       'pattern': '^(doi:)?10\\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+$'},
               'DOI_LIST': {'base': 'str',
                            'description': 'A list of Digital Object Identifiers',
                            'from_schema': 'cdp-ingestion-config',
                            'name': 'DOI_LIST',
                            'pattern': '^(doi:)?10\\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+(\\s*,\\s*(doi:)?10\\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)*$'},
               'EFO_ID': {'base': 'str',
                          'description': 'An Experimental Factor Ontology '
                                         'identifier',
                          'from_schema': 'cdp-ingestion-config',
                          'name': 'EFO_ID',
                          'pattern': '^EFO:[0-9]{7}$'},
               'EMDB_ID': {'base': 'str',
                           'description': 'An Electron Microscopy Data Bank '
                                          'identifier',
                           'from_schema': 'cdp-ingestion-config',
                           'name': 'EMDB_ID',
                           'pattern': '^EMD-[0-9]{4,5}$'},
               'EMPIAR_EMDB_DOI_PDB_LIST': {'base': 'str',
                                            'description': 'A list of EMPIAR, '
                                                           'EMDB, DOI, and PDB '
                                                           'identifiers',
                                            'from_schema': 'cdp-ingestion-config',
                                            'name': 'EMPIAR_EMDB_DOI_PDB_LIST',
                                            'pattern': '^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|(doi:)?10\\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+|PDB-[0-9a-zA-Z]{4,8})(\\s*,\\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|(doi:)?10\\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+|PDB-[0-9a-zA-Z]{4,8}))*$'},
               'EMPIAR_EMDB_PDB_LIST': {'base': 'str',
                                        'description': 'A list of EMPIAR, EMDB, '
                                                       'and PDB identifiers',
                                        'from_schema': 'cdp-ingestion-config',
                                        'name': 'EMPIAR_EMDB_PDB_LIST',
                                        'pattern': '^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|PDB-[0-9a-zA-Z]{4,8})(\\s*,\\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|PDB-[0-9a-zA-Z]{4,8}))*$'},
               'EMPIAR_ID': {'base': 'str',
                             'description': 'An Electron Microscopy Public Image '
                                            'Archive identifier',
                             'from_schema': 'cdp-ingestion-config',
                             'name': 'EMPIAR_ID',
                             'pattern': '^EMPIAR-[0-9]+$'},
               'FloatFormattedString': {'base': 'str',
                                        'description': 'A formatted string that '
                                                       'represents a floating '
                                                       'point number.',
                                        'from_schema': 'cdp-ingestion-config',
                                        'name': 'FloatFormattedString',
                                        'pattern': '^float[ '
                                                   ']*\\{[a-zA-Z0-9_-]+\\}[ ]*$'},
               'GO_ID': {'base': 'str',
                         'description': 'A Gene Ontology identifier',
                         'from_schema': 'cdp-ingestion-config',
                         'name': 'GO_ID',
                         'pattern': '^GO:[0-9]{7}$'},
               'HSAPDV_ID': {'base': 'str',
                             'description': 'A Human Developmental Phenotype '
                                            'Ontology identifier',
                             'from_schema': 'cdp-ingestion-config',
                             'name': 'HSAPDV_ID',
                             'pattern': 'HsapDv:[0-9]{7}$'},
               'IntegerFormattedString': {'base': 'str',
                                          'description': 'A formatted string that '
                                                         'represents an integer.',
                                          'from_schema': 'cdp-ingestion-config',
                                          'name': 'IntegerFormattedString',
                                          'pattern': '^int[ '
                                                     ']*\\{[a-zA-Z0-9_-]+\\}[ ]*$'},
               'MONDO_ID': {'base': 'str',
                            'description': 'An identifier of type MONDO',
                            'from_schema': 'cdp-ingestion-config',
                            'name': 'MONDO_ID',
                            'pattern': '^MONDO:[0-9]{7}$'},
               'NCBI_TAXON_ID': {'base': 'str',
                                 'description': 'A NCBI Taxonomy identifier',
                                 'from_schema': 'cdp-ingestion-config',
                                 'name': 'NCBI_TAXON_ID',
                                 'pattern': '^NCBITaxon:[0-9]+$'},
               'ONTOLOGY_ID': {'base': 'str',
                               'description': 'An ontology identifier',
                               'from_schema': 'cdp-ingestion-config',
                               'name': 'ONTOLOGY_ID',
                               'pattern': '^[a-zA-Z]+:[0-9]+$'},
               'ORCID': {'base': 'str',
                         'description': 'A unique, persistent identifier for '
                                        'researchers, provided by ORCID.',
                         'from_schema': 'cdp-ingestion-config',
                         'name': 'ORCID',
                         'pattern': '[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$'},
               'PATO_ID': {'base': 'str',
                           'description': 'An identifier of type PATO',
                           'from_schema': 'cdp-ingestion-config',
                           'name': 'PATO_ID',
                           'pattern': '^PATO:[0-9]{7}$'},
               'PDB_ID': {'base': 'str',
                          'description': 'A Protein Data Bank identifier',
                          'from_schema': 'cdp-ingestion-config',
                          'name': 'PDB_ID',
                          'pattern': '^PDB-[0-9a-zA-Z]{4,8}$'},
               'StringFormattedString': {'base': 'str',
                                         'description': 'A formatted string '
                                                        '(variable) that '
                                                        'represents a string.',
                                         'from_schema': 'cdp-ingestion-config',
                                         'name': 'StringFormattedString',
                                         'pattern': '^[ ]*\\{[a-zA-Z0-9_-]+\\}[ '
                                                    ']*$'},
               'UBERON_ID': {'base': 'str',
                             'description': 'An UBERON identifier',
                             'from_schema': 'cdp-ingestion-config',
                             'name': 'UBERON_ID',
                             'pattern': '^UBERON:[0-9]{7}$'},
               'UNIPROT_ID': {'base': 'str',
                              'description': 'A UniProt identifier',
                              'from_schema': 'cdp-ingestion-config',
                              'name': 'UNIPROT_ID',
                              'pattern': '^UniProtKB:[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}$'},
               'UNKNOWN_LITERAL': {'base': 'str',
                                   'description': 'A placeholder for an unknown '
                                                  'value.',
                                   'from_schema': 'cdp-ingestion-config',
                                   'name': 'UNKNOWN_LITERAL',
                                   'pattern': '^unknown$'},
               'URLorS3URI': {'base': 'str',
                              'description': 'A URL or S3 URI',
                              'from_schema': 'cdp-ingestion-config',
                              'name': 'URLorS3URI',
                              'pattern': '^(((https?|s3)://)|cryoetportal-rawdatasets-dev).*$'},
               'VersionString': {'base': 'float',
                                 'description': 'A version number (only major, '
                                                'minor versions)',
                                 'from_schema': 'cdp-ingestion-config',
                                 'minimum_value': 0,
                                 'name': 'VersionString'},
               'WORMBASE_DEVELOPMENT_ID': {'base': 'str',
                                           'description': 'A WormBase identifier',
                                           'from_schema': 'cdp-ingestion-config',
                                           'name': 'WORMBASE_DEVELOPMENT_ID',
                                           'pattern': 'WBls:[0-9]{7}$'},
               'WORMBASE_STRAIN_ID': {'base': 'str',
                                      'description': 'A WormBase strain identifier',
                                      'from_schema': 'cdp-ingestion-config',
                                      'name': 'WORMBASE_STRAIN_ID',
                                      'pattern': 'WBStrain[0-9]{8}$'},
               'WORMBASE_TISSUE_ID': {'base': 'str',
                                      'description': 'A WormBase tissue identifier',
                                      'from_schema': 'cdp-ingestion-config',
                                      'name': 'WORMBASE_TISSUE_ID',
                                      'pattern': 'WBbt:[0-9]{7}$'},
               'boolean': {'base': 'Bool',
                           'description': 'A binary (true or false) value',
                           'exact_mappings': ['schema:Boolean'],
                           'from_schema': 'cdp-ingestion-config',
                           'name': 'boolean',
                           'notes': ['If you are authoring schemas in LinkML YAML, '
                                     'the type is referenced with the lower case '
                                     '"boolean".'],
                           'repr': 'bool',
                           'uri': 'xsd:boolean'},
               'curie': {'base': 'Curie',
                         'comments': ['in RDF serializations this MUST be expanded '
                                      'to a URI',
                                      'in non-RDF serializations MAY be serialized '
                                      'as the compact representation'],
                         'conforms_to': 'https://www.w3.org/TR/curie/',
                         'description': 'a compact URI',
                         'from_schema': 'cdp-ingestion-config',
                         'name': 'curie',
                         'notes': ['If you are authoring schemas in LinkML YAML, '
                                   'the type is referenced with the lower case '
                                   '"curie".'],
                         'repr': 'str',
                         'uri': 'xsd:string'},
               'date': {'base': 'XSDDate',
                        'description': 'a date (year, month and day) in an '
                                       'idealized calendar',
                        'exact_mappings': ['schema:Date'],
                        'from_schema': 'cdp-ingestion-config',
                        'name': 'date',
                        'notes': ["URI is dateTime because OWL reasoners don't "
                                  'work with straight date or time',
                                  'If you are authoring schemas in LinkML YAML, '
                                  'the type is referenced with the lower case '
                                  '"date".'],
                        'repr': 'str',
                        'uri': 'xsd:date'},
               'date_or_datetime': {'base': 'str',
                                    'description': 'Either a date or a datetime',
                                    'from_schema': 'cdp-ingestion-config',
                                    'name': 'date_or_datetime',
                                    'notes': ['If you are authoring schemas in '
                                              'LinkML YAML, the type is referenced '
                                              'with the lower case '
                                              '"date_or_datetime".'],
                                    'repr': 'str',
                                    'uri': 'linkml:DateOrDatetime'},
               'datetime': {'base': 'XSDDateTime',
                            'description': 'The combination of a date and time',
                            'exact_mappings': ['schema:DateTime'],
                            'from_schema': 'cdp-ingestion-config',
                            'name': 'datetime',
                            'notes': ['If you are authoring schemas in LinkML '
                                      'YAML, the type is referenced with the lower '
                                      'case "datetime".'],
                            'repr': 'str',
                            'uri': 'xsd:dateTime'},
               'decimal': {'base': 'Decimal',
                           'broad_mappings': ['schema:Number'],
                           'description': 'A real number with arbitrary precision '
                                          'that conforms to the xsd:decimal '
                                          'specification',
                           'from_schema': 'cdp-ingestion-config',
                           'name': 'decimal',
                           'notes': ['If you are authoring schemas in LinkML YAML, '
                                     'the type is referenced with the lower case '
                                     '"decimal".'],
                           'uri': 'xsd:decimal'},
               'double': {'base': 'float',
                          'close_mappings': ['schema:Float'],
                          'description': 'A real number that conforms to the '
                                         'xsd:double specification',
                          'from_schema': 'cdp-ingestion-config',
                          'name': 'double',
                          'notes': ['If you are authoring schemas in LinkML YAML, '
                                    'the type is referenced with the lower case '
                                    '"double".'],
                          'uri': 'xsd:double'},
               'float': {'base': 'float',
                         'description': 'A real number that conforms to the '
                                        'xsd:float specification',
                         'exact_mappings': ['schema:Float'],
                         'from_schema': 'cdp-ingestion-config',
                         'name': 'float',
                         'notes': ['If you are authoring schemas in LinkML YAML, '
                                   'the type is referenced with the lower case '
                                   '"float".'],
                         'uri': 'xsd:float'},
               'integer': {'base': 'int',
                           'description': 'An integer',
                           'exact_mappings': ['schema:Integer'],
                           'from_schema': 'cdp-ingestion-config',
                           'name': 'integer',
                           'notes': ['If you are authoring schemas in LinkML YAML, '
                                     'the type is referenced with the lower case '
                                     '"integer".'],
                           'uri': 'xsd:integer'},
               'jsonpath': {'base': 'str',
                            'conforms_to': 'https://www.ietf.org/archive/id/draft-goessner-dispatch-jsonpath-00.html',
                            'description': 'A string encoding a JSON Path. The '
                                           'value of the string MUST conform to '
                                           'JSON Point syntax and SHOULD '
                                           'dereference to zero or more valid '
                                           'objects within the current instance '
                                           'document when encoded in tree form.',
                            'from_schema': 'cdp-ingestion-config',
                            'name': 'jsonpath',
                            'notes': ['If you are authoring schemas in LinkML '
                                      'YAML, the type is referenced with the lower '
                                      'case "jsonpath".'],
                            'repr': 'str',
                            'uri': 'xsd:string'},
               'jsonpointer': {'base': 'str',
                               'conforms_to': 'https://datatracker.ietf.org/doc/html/rfc6901',
                               'description': 'A string encoding a JSON Pointer. '
                                              'The value of the string MUST '
                                              'conform to JSON Point syntax and '
                                              'SHOULD dereference to a valid '
                                              'object within the current instance '
                                              'document when encoded in tree form.',
                               'from_schema': 'cdp-ingestion-config',
                               'name': 'jsonpointer',
                               'notes': ['If you are authoring schemas in LinkML '
                                         'YAML, the type is referenced with the '
                                         'lower case "jsonpointer".'],
                               'repr': 'str',
                               'uri': 'xsd:string'},
               'ncname': {'base': 'NCName',
                          'description': 'Prefix part of CURIE',
                          'from_schema': 'cdp-ingestion-config',
                          'name': 'ncname',
                          'notes': ['If you are authoring schemas in LinkML YAML, '
                                    'the type is referenced with the lower case '
                                    '"ncname".'],
                          'repr': 'str',
                          'uri': 'xsd:string'},
               'nodeidentifier': {'base': 'NodeIdentifier',
                                  'description': 'A URI, CURIE or BNODE that '
                                                 'represents a node in a model.',
                                  'from_schema': 'cdp-ingestion-config',
                                  'name': 'nodeidentifier',
                                  'notes': ['If you are authoring schemas in '
                                            'LinkML YAML, the type is referenced '
                                            'with the lower case '
                                            '"nodeidentifier".'],
                                  'repr': 'str',
                                  'uri': 'shex:nonLiteral'},
               'objectidentifier': {'base': 'ElementIdentifier',
                                    'comments': ['Used for inheritance and type '
                                                 'checking'],
                                    'description': 'A URI or CURIE that represents '
                                                   'an object in the model.',
                                    'from_schema': 'cdp-ingestion-config',
                                    'name': 'objectidentifier',
                                    'notes': ['If you are authoring schemas in '
                                              'LinkML YAML, the type is referenced '
                                              'with the lower case '
                                              '"objectidentifier".'],
                                    'repr': 'str',
                                    'uri': 'shex:iri'},
               'sparqlpath': {'base': 'str',
                              'conforms_to': 'https://www.w3.org/TR/sparql11-query/#propertypaths',
                              'description': 'A string encoding a SPARQL Property '
                                             'Path. The value of the string MUST '
                                             'conform to SPARQL syntax and SHOULD '
                                             'dereference to zero or more valid '
                                             'objects within the current instance '
                                             'document when encoded as RDF.',
                              'from_schema': 'cdp-ingestion-config',
                              'name': 'sparqlpath',
                              'notes': ['If you are authoring schemas in LinkML '
                                        'YAML, the type is referenced with the '
                                        'lower case "sparqlpath".'],
                              'repr': 'str',
                              'uri': 'xsd:string'},
               'string': {'base': 'str',
                          'description': 'A character string',
                          'exact_mappings': ['schema:Text'],
                          'from_schema': 'cdp-ingestion-config',
                          'name': 'string',
                          'notes': ['In RDF serializations, a slot with range of '
                                    'string is treated as a literal or type '
                                    'xsd:string.   If you are authoring schemas in '
                                    'LinkML YAML, the type is referenced with the '
                                    'lower case "string".'],
                          'uri': 'xsd:string'},
               'time': {'base': 'XSDTime',
                        'description': 'A time object represents a (local) time of '
                                       'day, independent of any particular day',
                        'exact_mappings': ['schema:Time'],
                        'from_schema': 'cdp-ingestion-config',
                        'name': 'time',
                        'notes': ['URI is dateTime because OWL reasoners do not '
                                  'work with straight date or time',
                                  'If you are authoring schemas in LinkML YAML, '
                                  'the type is referenced with the lower case '
                                  '"time".'],
                        'repr': 'str',
                        'uri': 'xsd:time'},
               'uri': {'base': 'URI',
                       'close_mappings': ['schema:URL'],
                       'comments': ['in RDF serializations a slot with range of '
                                    'uri is treated as a literal or type '
                                    'xsd:anyURI unless it is an identifier or a '
                                    'reference to an identifier, in which case it '
                                    'is translated directly to a node'],
                       'conforms_to': 'https://www.ietf.org/rfc/rfc3987.txt',
                       'description': 'a complete URI',
                       'from_schema': 'cdp-ingestion-config',
                       'name': 'uri',
                       'notes': ['If you are authoring schemas in LinkML YAML, the '
                                 'type is referenced with the lower case "uri".'],
                       'repr': 'str',
                       'uri': 'xsd:anyURI'},
               'uriorcurie': {'base': 'URIorCURIE',
                              'description': 'a URI or a CURIE',
                              'from_schema': 'cdp-ingestion-config',
                              'name': 'uriorcurie',
                              'notes': ['If you are authoring schemas in LinkML '
                                        'YAML, the type is referenced with the '
                                        'lower case "uriorcurie".'],
                              'repr': 'str',
                              'uri': 'xsd:anyURI'}}} )

class AlignmentTypeEnum(str, Enum):
    """
    Type of alignment
    """
    # per-section non-rigid alignment available
    LOCAL = "LOCAL"
    # only per-section rigid alignment available
    GLOBAL = "GLOBAL"


class AlignmentFormatEnum(str, Enum):
    """
    Used to determine what alignment alogrithm to use.
    """
    # formats (xf, tlt, com)
    IMOD = "IMOD"
    # formats (aln)
    ARETOMO3 = "ARETOMO3"


class AlignmentMethodTypeEnum(str, Enum):
    """
    Used to determine how the alignment was done.
    """
    # alignment was done based on fiducial markers
    fiducial_based = "fiducial_based"
    # alignment was done based on patch tracking
    patch_tracking = "patch_tracking"
    # alignment was done based on image projection
    projection_matching = "projection_matching"
    # how alignment was done is unknown
    undefined = "undefined"


class AnnotationFileSourceEnum(str, Enum):
    """
    How the annotation file was acquired
    """
    # Annotation submitted by dataset author
    dataset_author = "dataset_author"
    # Annotation submitted by community member
    community = "community"
    # Annotation submitted by portal standardization
    portal_standard = "portal_standard"


class AnnotationMethodTypeEnum(str, Enum):
    """
    Describes how the annotations were generated.
    """
    # Annotations were generated manually.
    manual = "manual"
    # Annotations were generated using automated tools or algorithms without supervision.
    automated = "automated"
    # Annotations were generated using a combination of automated and manual methods.
    hybrid = "hybrid"
    # Annotations were generated by simulation tools or algorithms.
    simulated = "simulated"


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


class AnnotationFileFormatEnum(str, Enum):
    """
    Describes the format of the annotation file
    """
    # MRC format
    mrc = "mrc"
    # OMEZARR format
    zarr = "zarr"
    # NDJSON format
    ndjson = "ndjson"
    # GLB format
    glb = "glb"


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


class CtfFormatEnum(str, Enum):
    """
    Used to determine what ctf parser to use.
    """
    # The file has ctffind schema
    CTFFIND = "CTFFIND"


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
    # Tomographic data of immortalized cells or immortalized cell sections
    cell_line = "cell_line"
    # Simulated tomographic data.
    in_silico = "in_silico"
    # Tomographic data of in vitro reconstituted systems or mixtures of proteins.
    in_vitro = "in_vitro"
    # Tomographic data of purified organelles.
    organelle = "organelle"
    # Tomographic data of sections through multicellular organisms.
    organism = "organism"
    # Tomographic data of organoid-derived samples.
    organoid = "organoid"
    # Other type of sample.
    other = "other"
    # Tomographic data of whole primary cells or primary cell sections.
    primary_cell_culture = "primary_cell_culture"
    # Tomographic data of tissue sections.
    tissue = "tissue"
    # Tomographic data of purified viruses or VLPs.
    virus = "virus"


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


class TiltseriesCameraManufacturerEnum(str, Enum):
    """
    Camera manufacturer
    """
    # Gatan Inc.
    Gatan = "Gatan"
    # FEI Company
    FEI = "FEI"
    # Thermo Fisher Scientific
    TFS = "TFS"
    # Simulated data
    simulated = "simulated"


class TiltseriesMicroscopeManufacturerEnum(str, Enum):
    """
    Microscope manufacturer
    """
    # FEI Company
    FEI = "FEI"
    # Thermo Fisher Scientific
    TFS = "TFS"
    # JEOL Ltd.
    JEOL = "JEOL"
    # Simulated data
    SIMULATED = "SIMULATED"


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


class TomogramReconstructionMethodEnum(str, Enum):
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
    # Tomogram's was not submitted by the dataset author
    UNKNOWN = "UNKNOWN"



class PicturePath(ConfiguredBaseModel):
    """
    A set of paths to representative images of a piece of data.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    snapshot: Optional[str] = Field(None, description="""Path to the dataset preview image relative to the dataset directory root.""", json_schema_extra = { "linkml_meta": {'alias': 'snapshot',
         'domain_of': ['PicturePath', 'MetadataPicturePath'],
         'exact_mappings': ['cdp-common:snapshot'],
         'recommended': True} })
    thumbnail: Optional[str] = Field(None, description="""Path to the thumbnail of preview image relative to the dataset directory root.""", json_schema_extra = { "linkml_meta": {'alias': 'thumbnail',
         'domain_of': ['PicturePath', 'MetadataPicturePath'],
         'exact_mappings': ['cdp-common:thumbnail'],
         'recommended': True} })

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


class MetadataPicturePath(ConfiguredBaseModel):
    """
    A set of paths to representative images of a piece of data for metadata files.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    snapshot: Optional[str] = Field(None, description="""Relative path (non-URL/URI) to the dataset preview image relative to the dataset directory root.""", json_schema_extra = { "linkml_meta": {'alias': 'snapshot',
         'domain_of': ['PicturePath', 'MetadataPicturePath'],
         'exact_mappings': ['cdp-common:metadata_snapshot'],
         'recommended': True} })
    thumbnail: Optional[str] = Field(None, description="""Relative path (non-URL/URI) to the thumbnail of preview image relative to the dataset directory root.""", json_schema_extra = { "linkml_meta": {'alias': 'thumbnail',
         'domain_of': ['PicturePath', 'MetadataPicturePath'],
         'exact_mappings': ['cdp-common:metadata_thumbnail'],
         'recommended': True} })


class FundingDetails(ConfiguredBaseModel):
    """
    A funding source for a scientific data entity (base for JSON and DB representation).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    funding_agency_name: Optional[str] = Field(None, description="""The name of the funding source.""", json_schema_extra = { "linkml_meta": {'alias': 'funding_agency_name',
         'domain_of': ['FundingDetails'],
         'exact_mappings': ['cdp-common:funding_agency_name'],
         'recommended': True} })
    grant_id: Optional[str] = Field(None, description="""Grant identifier provided by the funding agency""", json_schema_extra = { "linkml_meta": {'alias': 'grant_id',
         'domain_of': ['FundingDetails'],
         'exact_mappings': ['cdp-common:funding_grant_id'],
         'recommended': True} })


class DateStampedEntity(ConfiguredBaseModel):
    """
    An entity with associated deposition, release and last modified dates.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    dates: DateStamp = Field(..., description="""A set of dates at which a data item was deposited, published and last modified.""", json_schema_extra = { "linkml_meta": {'alias': 'dates',
         'domain_of': ['DateStampedEntity',
                       'Tomogram',
                       'Dataset',
                       'Deposition',
                       'Annotation']} })


class AuthoredEntity(ConfiguredBaseModel):
    """
    An entity with associated authors.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    authors: List[Author] = Field(..., description="""Author of a scientific data entity.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'authors',
         'domain_of': ['AuthoredEntity',
                       'Dataset',
                       'Deposition',
                       'Tomogram',
                       'Annotation'],
         'list_elements_ordered': True} })


class FundedEntity(ConfiguredBaseModel):
    """
    An entity with associated funding sources.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    funding: Optional[List[FundingDetails]] = Field(None, description="""A funding source for a scientific data entity (base for JSON and DB representation).""", json_schema_extra = { "linkml_meta": {'alias': 'funding',
         'domain_of': ['FundedEntity', 'Dataset'],
         'list_elements_ordered': True,
         'recommended': True} })


class CrossReferencedEntity(ConfiguredBaseModel):
    """
    An entity with associated cross-references to other databases and publications.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata', 'mixin': True})

    cross_references: Optional[CrossReferences] = Field(None, description="""A set of cross-references to other databases and publications.""", json_schema_extra = { "linkml_meta": {'alias': 'cross_references',
         'domain_of': ['CrossReferencedEntity', 'Tomogram', 'Dataset', 'Deposition']} })


class PicturedEntity(ConfiguredBaseModel):
    """
    An entity with associated preview images.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    key_photos: PicturePath = Field(..., description="""A set of paths to representative images of a piece of data.""", json_schema_extra = { "linkml_meta": {'alias': 'key_photos',
         'domain_of': ['PicturedEntity', 'PicturedMetadataEntity']} })


class PicturedMetadataEntity(ConfiguredBaseModel):
    """
    An entity with associated preview images for metadata files.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    key_photos: MetadataPicturePath = Field(..., description="""A set of paths to representative images of a piece of data for metadata files.""", json_schema_extra = { "linkml_meta": {'alias': 'key_photos',
         'domain_of': ['PicturedEntity', 'PicturedMetadataEntity']} })


class Assay(ConfiguredBaseModel):
    """
    The assay that was used to create the dataset.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    name: str = Field(..., description="""Name of the assay component.""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Assay',
                       'DevelopmentStageDetails',
                       'Disease',
                       'OrganismDetails',
                       'TissueDetails',
                       'CellType',
                       'CellStrain',
                       'CellComponent',
                       'AnnotationObject',
                       'AnnotationTriangularMeshGroupFile',
                       'AuthorMixin',
                       'Author'],
         'exact_mappings': ['cdp-common:assay_name']} })
    id: Optional[str] = Field(None, description="""The EFO identifier for the cellular component.""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Assay',
                       'DevelopmentStageDetails',
                       'Disease',
                       'TissueDetails',
                       'CellType',
                       'CellStrain',
                       'CellComponent',
                       'AnnotationObject'],
         'exact_mappings': ['cdp-common:assay_id'],
         'recommended': True} })

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^EFO:[0-9]{7}$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid id format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid id format: {v}")
        return v


class DevelopmentStageDetails(ConfiguredBaseModel):
    """
    The development stage of the patients or organisms from which assayed biosamples were derived.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    name: Optional[str] = Field(None, description="""Name of the developmental stage component.""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Assay',
                       'DevelopmentStageDetails',
                       'Disease',
                       'OrganismDetails',
                       'TissueDetails',
                       'CellType',
                       'CellStrain',
                       'CellComponent',
                       'AnnotationObject',
                       'AnnotationTriangularMeshGroupFile',
                       'AuthorMixin',
                       'Author'],
         'exact_mappings': ['cdp-common:development_stage_name'],
         'recommended': True} })
    id: Optional[str] = Field(None, description="""A placeholder for any type of data.""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'any_of': [{'range': 'UNKNOWN_LITERAL'},
                    {'range': 'WORMBASE_DEVELOPMENT_ID'},
                    {'range': 'UBERON_ID'},
                    {'range': 'HSAPDV_ID'}],
         'domain_of': ['Assay',
                       'DevelopmentStageDetails',
                       'Disease',
                       'TissueDetails',
                       'CellType',
                       'CellStrain',
                       'CellComponent',
                       'AnnotationObject'],
         'exact_mappings': ['cdp-common:development_stage_id'],
         'recommended': True} })

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"(^unknown$)|(WBls:[0-9]{7}$)|(^UBERON:[0-9]{7}$)|(HsapDv:[0-9]{7}$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid id format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid id format: {v}")
        return v


class Disease(ConfiguredBaseModel):
    """
    The disease or condition of the patients from which assayed biosamples were derived.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    name: Optional[str] = Field(None, description="""Name of the disease.""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Assay',
                       'DevelopmentStageDetails',
                       'Disease',
                       'OrganismDetails',
                       'TissueDetails',
                       'CellType',
                       'CellStrain',
                       'CellComponent',
                       'AnnotationObject',
                       'AnnotationTriangularMeshGroupFile',
                       'AuthorMixin',
                       'Author'],
         'exact_mappings': ['cdp-common:disease_name'],
         'recommended': True} })
    id: Optional[str] = Field(None, description="""A placeholder for any type of data.""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'any_of': [{'range': 'MONDO_ID'}, {'range': 'PATO_ID'}],
         'domain_of': ['Assay',
                       'DevelopmentStageDetails',
                       'Disease',
                       'TissueDetails',
                       'CellType',
                       'CellStrain',
                       'CellComponent',
                       'AnnotationObject'],
         'exact_mappings': ['cdp-common:disease_id'],
         'recommended': True} })

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"(^MONDO:[0-9]{7}$)|(^PATO:[0-9]{7}$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid id format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid id format: {v}")
        return v


class OrganismDetails(ConfiguredBaseModel):
    """
    The species from which the sample was derived.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    name: str = Field(..., description="""Name of the organism from which a biological sample used in a CryoET study is derived from, e.g. homo sapiens.""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Assay',
                       'DevelopmentStageDetails',
                       'Disease',
                       'OrganismDetails',
                       'TissueDetails',
                       'CellType',
                       'CellStrain',
                       'CellComponent',
                       'AnnotationObject',
                       'AnnotationTriangularMeshGroupFile',
                       'AuthorMixin',
                       'Author'],
         'exact_mappings': ['cdp-common:organism_name']} })
    taxonomy_id: Optional[int] = Field(None, description="""NCBI taxonomy identifier for the organism, e.g. 9606""", ge=1, json_schema_extra = { "linkml_meta": {'alias': 'taxonomy_id',
         'domain_of': ['OrganismDetails'],
         'exact_mappings': ['cdp-common:organism_taxid'],
         'recommended': True} })


class TissueDetails(ConfiguredBaseModel):
    """
    The type of tissue from which the sample was derived.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    name: str = Field(..., description="""Name of the tissue from which a biological sample used in a CryoET study is derived from.""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Assay',
                       'DevelopmentStageDetails',
                       'Disease',
                       'OrganismDetails',
                       'TissueDetails',
                       'CellType',
                       'CellStrain',
                       'CellComponent',
                       'AnnotationObject',
                       'AnnotationTriangularMeshGroupFile',
                       'AuthorMixin',
                       'Author'],
         'exact_mappings': ['cdp-common:tissue_name']} })
    id: Optional[str] = Field(None, description="""A placeholder for any type of data.""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'any_of': [{'range': 'CL_ID'},
                    {'range': 'WORMBASE_TISSUE_ID'},
                    {'range': 'UBERON_ID'}],
         'domain_of': ['Assay',
                       'DevelopmentStageDetails',
                       'Disease',
                       'TissueDetails',
                       'CellType',
                       'CellStrain',
                       'CellComponent',
                       'AnnotationObject'],
         'exact_mappings': ['cdp-common:tissue_id'],
         'recommended': True} })

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"(^CL:[0-9]{7}$)|(WBbt:[0-9]{7}$)|(^UBERON:[0-9]{7}$)")
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
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    name: str = Field(..., description="""Name of the cell type from which a biological sample used in a CryoET study is derived from.""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Assay',
                       'DevelopmentStageDetails',
                       'Disease',
                       'OrganismDetails',
                       'TissueDetails',
                       'CellType',
                       'CellStrain',
                       'CellComponent',
                       'AnnotationObject',
                       'AnnotationTriangularMeshGroupFile',
                       'AuthorMixin',
                       'Author'],
         'exact_mappings': ['cdp-common:cell_name']} })
    id: Optional[str] = Field(None, description="""A placeholder for any type of data.""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'any_of': [{'range': 'CL_ID'}, {'range': 'UBERON_ID'}],
         'domain_of': ['Assay',
                       'DevelopmentStageDetails',
                       'Disease',
                       'TissueDetails',
                       'CellType',
                       'CellStrain',
                       'CellComponent',
                       'AnnotationObject'],
         'exact_mappings': ['cdp-common:cell_type_id'],
         'recommended': True} })

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"(^CL:[0-9]{7}$)|(^UBERON:[0-9]{7}$)")
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
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    name: str = Field(..., description="""Cell line or strain for the sample.""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Assay',
                       'DevelopmentStageDetails',
                       'Disease',
                       'OrganismDetails',
                       'TissueDetails',
                       'CellType',
                       'CellStrain',
                       'CellComponent',
                       'AnnotationObject',
                       'AnnotationTriangularMeshGroupFile',
                       'AuthorMixin',
                       'Author'],
         'exact_mappings': ['cdp-common:cell_strain_name']} })
    id: Optional[str] = Field(None, description="""A placeholder for any type of data.""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'any_of': [{'range': 'WORMBASE_STRAIN_ID'},
                    {'range': 'NCBI_TAXON_ID'},
                    {'range': 'CVCL_ID'},
                    {'range': 'CC_ID'}],
         'domain_of': ['Assay',
                       'DevelopmentStageDetails',
                       'Disease',
                       'TissueDetails',
                       'CellType',
                       'CellStrain',
                       'CellComponent',
                       'AnnotationObject'],
         'exact_mappings': ['cdp-common:cell_strain_id'],
         'recommended': True} })

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"(WBStrain[0-9]{8}$)|(^NCBITaxon:[0-9]+$)|(^CVCL_[A-Z0-9]{4,}$)|(^CC-[0-9]{4}$)")
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
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    name: str = Field(..., description="""Name of the cellular component.""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Assay',
                       'DevelopmentStageDetails',
                       'Disease',
                       'OrganismDetails',
                       'TissueDetails',
                       'CellType',
                       'CellStrain',
                       'CellComponent',
                       'AnnotationObject',
                       'AnnotationTriangularMeshGroupFile',
                       'AuthorMixin',
                       'Author'],
         'exact_mappings': ['cdp-common:cell_component_name']} })
    id: Optional[str] = Field(None, description="""The GO identifier for the cellular component.""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Assay',
                       'DevelopmentStageDetails',
                       'Disease',
                       'TissueDetails',
                       'CellType',
                       'CellStrain',
                       'CellComponent',
                       'AnnotationObject'],
         'exact_mappings': ['cdp-common:cell_component_id'],
         'recommended': True} })

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


class ExperimentMetadata(ConfiguredBaseModel):
    """
    Metadata describing sample and sample preparation methods used in a cryoET dataset.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    sample_type: SampleTypeEnum = Field(..., description="""Type of sample imaged in a CryoET study.""", json_schema_extra = { "linkml_meta": {'alias': 'sample_type',
         'domain_of': ['ExperimentMetadata', 'Dataset'],
         'exact_mappings': ['cdp-common:preparation_sample_type']} })
    sample_preparation: Optional[str] = Field(None, description="""Describes how the sample was prepared.""", json_schema_extra = { "linkml_meta": {'alias': 'sample_preparation',
         'domain_of': ['ExperimentMetadata', 'Dataset'],
         'exact_mappings': ['cdp-common:sample_preparation'],
         'recommended': True} })
    grid_preparation: Optional[str] = Field(None, description="""Describes Cryo-ET grid preparation.""", json_schema_extra = { "linkml_meta": {'alias': 'grid_preparation',
         'domain_of': ['ExperimentMetadata', 'Dataset'],
         'exact_mappings': ['cdp-common:grid_preparation'],
         'recommended': True} })
    other_setup: Optional[str] = Field(None, description="""Describes other setup not covered by sample preparation or grid preparation that may make this dataset unique in the same publication.""", json_schema_extra = { "linkml_meta": {'alias': 'other_setup',
         'domain_of': ['ExperimentMetadata', 'Dataset'],
         'exact_mappings': ['cdp-common:preparation_other_setup'],
         'recommended': True} })
    organism: Optional[OrganismDetails] = Field(None, description="""The species from which the sample was derived.""", json_schema_extra = { "linkml_meta": {'alias': 'organism', 'domain_of': ['ExperimentMetadata', 'Dataset']} })
    tissue: Optional[TissueDetails] = Field(None, description="""The type of tissue from which the sample was derived.""", json_schema_extra = { "linkml_meta": {'alias': 'tissue', 'domain_of': ['ExperimentMetadata', 'Dataset']} })
    cell_type: Optional[CellType] = Field(None, description="""The cell type from which the sample was derived.""", json_schema_extra = { "linkml_meta": {'alias': 'cell_type', 'domain_of': ['ExperimentMetadata', 'Dataset']} })
    cell_strain: Optional[CellStrain] = Field(None, description="""The strain or cell line from which the sample was derived.""", json_schema_extra = { "linkml_meta": {'alias': 'cell_strain', 'domain_of': ['ExperimentMetadata', 'Dataset']} })
    cell_component: Optional[CellComponent] = Field(None, description="""The cellular component from which the sample was derived.""", json_schema_extra = { "linkml_meta": {'alias': 'cell_component', 'domain_of': ['ExperimentMetadata', 'Dataset']} })
    assay: Assay = Field(..., description="""The assay that was used to create the dataset.""", json_schema_extra = { "linkml_meta": {'alias': 'assay', 'domain_of': ['ExperimentMetadata', 'Dataset']} })
    development_stage: DevelopmentStageDetails = Field(..., description="""The development stage of the patients or organisms from which assayed biosamples were derived.""", json_schema_extra = { "linkml_meta": {'alias': 'development_stage', 'domain_of': ['ExperimentMetadata', 'Dataset']} })
    disease: Disease = Field(..., description="""The disease or condition of the patients from which assayed biosamples were derived.""", json_schema_extra = { "linkml_meta": {'alias': 'disease', 'domain_of': ['ExperimentMetadata', 'Dataset']} })

    @field_validator('sample_type')
    def pattern_sample_type(cls, v):
        pattern=re.compile(r"(^cell_line$)|(^in_silico$)|(^in_vitro$)|(^organelle$)|(^organism$)|(^organoid$)|(^other$)|(^primary_cell_culture$)|(^tissue$)|(^virus$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid sample_type format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid sample_type format: {v}")
        return v


class Dataset(ExperimentMetadata, CrossReferencedEntity, FundedEntity, AuthoredEntity, DateStampedEntity):
    """
    High-level description of a cryoET dataset.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata',
         'mixins': ['DateStampedEntity',
                    'AuthoredEntity',
                    'FundedEntity',
                    'CrossReferencedEntity',
                    'ExperimentMetadata']})

    dataset_identifier: int = Field(..., description="""An identifier for a CryoET dataset, assigned by the Data Portal. Used to identify the dataset as the directory name in data tree.""", json_schema_extra = { "linkml_meta": {'alias': 'dataset_identifier',
         'domain_of': ['Dataset'],
         'exact_mappings': ['cdp-common:dataset_identifier']} })
    dataset_title: str = Field(..., description="""Title of a CryoET dataset.""", json_schema_extra = { "linkml_meta": {'alias': 'dataset_title',
         'domain_of': ['Dataset'],
         'exact_mappings': ['cdp-common:dataset_title']} })
    dataset_description: str = Field(..., description="""A short description of a CryoET dataset, similar to an abstract for a journal article or dataset.""", json_schema_extra = { "linkml_meta": {'alias': 'dataset_description',
         'domain_of': ['Dataset'],
         'exact_mappings': ['cdp-common:dataset_description']} })
    dates: DateStamp = Field(..., description="""A set of dates at which a data item was deposited, published and last modified.""", json_schema_extra = { "linkml_meta": {'alias': 'dates',
         'domain_of': ['DateStampedEntity',
                       'Tomogram',
                       'Dataset',
                       'Deposition',
                       'Annotation']} })
    authors: List[Author] = Field(..., description="""Author of a scientific data entity.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'authors',
         'domain_of': ['AuthoredEntity',
                       'Dataset',
                       'Deposition',
                       'Tomogram',
                       'Annotation'],
         'list_elements_ordered': True} })
    funding: Optional[List[FundingDetails]] = Field(None, description="""A funding source for a scientific data entity (base for JSON and DB representation).""", json_schema_extra = { "linkml_meta": {'alias': 'funding',
         'domain_of': ['FundedEntity', 'Dataset'],
         'list_elements_ordered': True,
         'recommended': True} })
    cross_references: Optional[CrossReferences] = Field(None, description="""A set of cross-references to other databases and publications.""", json_schema_extra = { "linkml_meta": {'alias': 'cross_references',
         'domain_of': ['CrossReferencedEntity', 'Tomogram', 'Dataset', 'Deposition']} })
    sample_type: SampleTypeEnum = Field(..., description="""Type of sample imaged in a CryoET study.""", json_schema_extra = { "linkml_meta": {'alias': 'sample_type',
         'domain_of': ['ExperimentMetadata', 'Dataset'],
         'exact_mappings': ['cdp-common:preparation_sample_type']} })
    sample_preparation: Optional[str] = Field(None, description="""Describes how the sample was prepared.""", json_schema_extra = { "linkml_meta": {'alias': 'sample_preparation',
         'domain_of': ['ExperimentMetadata', 'Dataset'],
         'exact_mappings': ['cdp-common:sample_preparation'],
         'recommended': True} })
    grid_preparation: Optional[str] = Field(None, description="""Describes Cryo-ET grid preparation.""", json_schema_extra = { "linkml_meta": {'alias': 'grid_preparation',
         'domain_of': ['ExperimentMetadata', 'Dataset'],
         'exact_mappings': ['cdp-common:grid_preparation'],
         'recommended': True} })
    other_setup: Optional[str] = Field(None, description="""Describes other setup not covered by sample preparation or grid preparation that may make this dataset unique in the same publication.""", json_schema_extra = { "linkml_meta": {'alias': 'other_setup',
         'domain_of': ['ExperimentMetadata', 'Dataset'],
         'exact_mappings': ['cdp-common:preparation_other_setup'],
         'recommended': True} })
    organism: Optional[OrganismDetails] = Field(None, description="""The species from which the sample was derived.""", json_schema_extra = { "linkml_meta": {'alias': 'organism', 'domain_of': ['ExperimentMetadata', 'Dataset']} })
    tissue: Optional[TissueDetails] = Field(None, description="""The type of tissue from which the sample was derived.""", json_schema_extra = { "linkml_meta": {'alias': 'tissue', 'domain_of': ['ExperimentMetadata', 'Dataset']} })
    cell_type: Optional[CellType] = Field(None, description="""The cell type from which the sample was derived.""", json_schema_extra = { "linkml_meta": {'alias': 'cell_type', 'domain_of': ['ExperimentMetadata', 'Dataset']} })
    cell_strain: Optional[CellStrain] = Field(None, description="""The strain or cell line from which the sample was derived.""", json_schema_extra = { "linkml_meta": {'alias': 'cell_strain', 'domain_of': ['ExperimentMetadata', 'Dataset']} })
    cell_component: Optional[CellComponent] = Field(None, description="""The cellular component from which the sample was derived.""", json_schema_extra = { "linkml_meta": {'alias': 'cell_component', 'domain_of': ['ExperimentMetadata', 'Dataset']} })
    assay: Assay = Field(..., description="""The assay that was used to create the dataset.""", json_schema_extra = { "linkml_meta": {'alias': 'assay', 'domain_of': ['ExperimentMetadata', 'Dataset']} })
    development_stage: DevelopmentStageDetails = Field(..., description="""The development stage of the patients or organisms from which assayed biosamples were derived.""", json_schema_extra = { "linkml_meta": {'alias': 'development_stage', 'domain_of': ['ExperimentMetadata', 'Dataset']} })
    disease: Disease = Field(..., description="""The disease or condition of the patients from which assayed biosamples were derived.""", json_schema_extra = { "linkml_meta": {'alias': 'disease', 'domain_of': ['ExperimentMetadata', 'Dataset']} })

    @field_validator('sample_type')
    def pattern_sample_type(cls, v):
        pattern=re.compile(r"(^cell_line$)|(^in_silico$)|(^in_vitro$)|(^organelle$)|(^organism$)|(^organoid$)|(^other$)|(^primary_cell_culture$)|(^tissue$)|(^virus$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid sample_type format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid sample_type format: {v}")
        return v


class Deposition(CrossReferencedEntity, AuthoredEntity, DateStampedEntity):
    """
    Metadata describing a deposition.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata',
         'mixins': ['DateStampedEntity', 'AuthoredEntity', 'CrossReferencedEntity']})

    deposition_description: str = Field(..., description="""A short description of the deposition, similar to an abstract for a journal article or dataset.""", json_schema_extra = { "linkml_meta": {'alias': 'deposition_description',
         'domain_of': ['Deposition'],
         'exact_mappings': ['cdp-common:deposition_description']} })
    deposition_identifier: int = Field(..., description="""An identifier for a CryoET deposition, assigned by the Data Portal. Used to identify the deposition the entity is a part of.""", json_schema_extra = { "linkml_meta": {'alias': 'deposition_identifier',
         'domain_of': ['Deposition'],
         'exact_mappings': ['cdp-common:deposition_identifier']} })
    deposition_title: str = Field(..., description="""Title of a CryoET deposition.""", json_schema_extra = { "linkml_meta": {'alias': 'deposition_title',
         'domain_of': ['Deposition'],
         'exact_mappings': ['cdp-common:deposition_title']} })
    deposition_types: List[DepositionTypesEnum] = Field(..., description="""Type of data in the deposition (e.g. dataset, annotation, tomogram)""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'deposition_types',
         'domain_of': ['Deposition'],
         'exact_mappings': ['cdp-common:deposition_types']} })
    tag: Optional[str] = Field(None, description="""A string to categorize this deposition (i.e \"competitionML2024Winners\")""", json_schema_extra = { "linkml_meta": {'alias': 'tag',
         'domain_of': ['Deposition'],
         'exact_mappings': ['cdp-common:tag']} })
    dates: DateStamp = Field(..., description="""A set of dates at which a data item was deposited, published and last modified.""", json_schema_extra = { "linkml_meta": {'alias': 'dates',
         'domain_of': ['DateStampedEntity',
                       'Tomogram',
                       'Dataset',
                       'Deposition',
                       'Annotation']} })
    authors: List[Author] = Field(..., description="""Author of a scientific data entity.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'authors',
         'domain_of': ['AuthoredEntity',
                       'Dataset',
                       'Deposition',
                       'Tomogram',
                       'Annotation'],
         'list_elements_ordered': True} })
    cross_references: Optional[CrossReferences] = Field(None, description="""A set of cross-references to other databases and publications.""", json_schema_extra = { "linkml_meta": {'alias': 'cross_references',
         'domain_of': ['CrossReferencedEntity', 'Tomogram', 'Dataset', 'Deposition']} })

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
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    acquire_mode: Optional[Union[TiltseriesCameraAcquireModeEnum, str]] = Field(None, description="""A placeholder for any type of data.""", json_schema_extra = { "linkml_meta": {'alias': 'acquire_mode',
         'any_of': [{'range': 'StringFormattedString'},
                    {'range': 'tiltseries_camera_acquire_mode_enum'}],
         'domain_of': ['CameraDetails'],
         'exact_mappings': ['cdp-common:tiltseries_camera_acquire_mode']} })
    manufacturer: TiltseriesCameraManufacturerEnum = Field(..., description="""Name of the camera manufacturer""", json_schema_extra = { "linkml_meta": {'alias': 'manufacturer',
         'domain_of': ['CameraDetails', 'MicroscopeDetails'],
         'exact_mappings': ['cdp-common:tiltseries_camera_manufacturer']} })
    model: str = Field(..., description="""Camera model name""", json_schema_extra = { "linkml_meta": {'alias': 'model',
         'domain_of': ['CameraDetails', 'MicroscopeDetails'],
         'exact_mappings': ['cdp-common:tiltseries_camera_model']} })

    @field_validator('acquire_mode')
    def pattern_acquire_mode(cls, v):
        pattern=re.compile(r"(^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$)|((^counting$)|(^superresolution$)|(^linear$)|(^cds$))")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid acquire_mode format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid acquire_mode format: {v}")
        return v

    @field_validator('manufacturer')
    def pattern_manufacturer(cls, v):
        pattern=re.compile(r"(^Gatan$)|(^FEI$)|(^TFS$)|(^simulated$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid manufacturer format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid manufacturer format: {v}")
        return v


class MicroscopeDetails(ConfiguredBaseModel):
    """
    The microscope used to collect the tilt series.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    additional_info: Optional[str] = Field(None, description="""Other microscope optical setup information, in addition to energy filter, phase plate and image corrector""", json_schema_extra = { "linkml_meta": {'alias': 'additional_info',
         'domain_of': ['MicroscopeDetails'],
         'exact_mappings': ['cdp-common:tiltseries_microscope_additional_info']} })
    manufacturer: Union[TiltseriesMicroscopeManufacturerEnum, str] = Field(..., description="""A placeholder for any type of data.""", json_schema_extra = { "linkml_meta": {'alias': 'manufacturer',
         'any_of': [{'description': 'Name of the microscope manufacturer',
                     'exact_mappings': ['cdp-common:tiltseries_microscope_manufacturer'],
                     'range': 'tiltseries_microscope_manufacturer_enum',
                     'required': True},
                    {'range': 'StringFormattedString'}],
         'domain_of': ['CameraDetails', 'MicroscopeDetails']} })
    model: str = Field(..., description="""Microscope model name""", json_schema_extra = { "linkml_meta": {'alias': 'model',
         'domain_of': ['CameraDetails', 'MicroscopeDetails'],
         'exact_mappings': ['cdp-common:tiltseries_microscope_model']} })

    @field_validator('manufacturer')
    def pattern_manufacturer(cls, v):
        pattern=re.compile(r"(^FEI$)|(^TFS$)|(^JEOL$)|(^SIMULATED$)|(^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$)")
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
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    energy_filter: str = Field(..., description="""Energy filter setup used""", json_schema_extra = { "linkml_meta": {'alias': 'energy_filter',
         'domain_of': ['MicroscopeOpticalSetup'],
         'exact_mappings': ['cdp-common:tiltseries_microscope_energy_filter']} })
    phase_plate: Optional[str] = Field(None, description="""Phase plate configuration""", json_schema_extra = { "linkml_meta": {'alias': 'phase_plate',
         'domain_of': ['MicroscopeOpticalSetup'],
         'exact_mappings': ['cdp-common:tiltseries_microscope_phase_plate']} })
    image_corrector: Optional[str] = Field(None, description="""Image corrector setup""", json_schema_extra = { "linkml_meta": {'alias': 'image_corrector',
         'domain_of': ['MicroscopeOpticalSetup'],
         'exact_mappings': ['cdp-common:tiltseries_microscope_image_corrector']} })


class TiltRange(ConfiguredBaseModel):
    """
    The range of tilt angles in the tilt series.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    min: Union[float, str] = Field(..., description="""A placeholder for any type of data.""", ge=-90, le=90, json_schema_extra = { "linkml_meta": {'alias': 'min',
         'any_of': [{'description': 'Minimal tilt angle in degrees',
                     'exact_mappings': ['cdp-common:tiltseries_tilt_min'],
                     'maximum_value': 90,
                     'minimum_value': -90,
                     'range': 'float',
                     'required': True,
                     'unit': {'descriptive_name': 'degrees', 'symbol': '°'}},
                    {'range': 'FloatFormattedString'}],
         'domain_of': ['TiltRange'],
         'unit': {'descriptive_name': 'degrees', 'symbol': '°'}} })
    max: Union[float, str] = Field(..., description="""A placeholder for any type of data.""", ge=-90, le=90, json_schema_extra = { "linkml_meta": {'alias': 'max',
         'any_of': [{'description': 'Maximal tilt angle in degrees',
                     'exact_mappings': ['cdp-common:tiltseries_tilt_max'],
                     'maximum_value': 90,
                     'minimum_value': -90,
                     'range': 'float',
                     'required': True,
                     'unit': {'descriptive_name': 'degrees', 'symbol': '°'}},
                    {'range': 'FloatFormattedString'}],
         'domain_of': ['TiltRange'],
         'unit': {'descriptive_name': 'degrees', 'symbol': '°'}} })

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


class PerSectionParameter(ConfiguredBaseModel):
    """
    Parameters for a section of a tilt series.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    z_index: int = Field(..., description="""z-index of the frame in the tiltseries""", ge=0, json_schema_extra = { "linkml_meta": {'alias': 'z_index',
         'domain_of': ['PerSectionParameter', 'PerSectionAlignmentParameters'],
         'exact_mappings': ['cdp-common:per_section_z_index']} })
    frame_acquisition_order: int = Field(..., description="""The 0-based index of this movie stack in the order of acquisition.""", json_schema_extra = { "linkml_meta": {'alias': 'frame_acquisition_order',
         'domain_of': ['PerSectionParameter'],
         'exact_mappings': ['cdp-common:frames_acquisition_order']} })
    raw_angle: Optional[float] = Field(None, description="""Nominal angle of the tilt series section.""", ge=-90, le=90, json_schema_extra = { "linkml_meta": {'alias': 'raw_angle',
         'domain_of': ['PerSectionParameter'],
         'exact_mappings': ['cdp-common:per_section_nominal_tilt_angle'],
         'unit': {'descriptive_name': 'degrees', 'symbol': '°'}} })
    astigmatic_angle: Optional[float] = Field(None, description="""Angle of astigmatism.""", ge=-180, le=180, json_schema_extra = { "linkml_meta": {'alias': 'astigmatic_angle',
         'domain_of': ['PerSectionParameter'],
         'exact_mappings': ['cdp-common:per_section_astigmatic_angle'],
         'unit': {'descriptive_name': 'degrees', 'symbol': '°'}} })
    minor_defocus: Optional[float] = Field(None, description="""Minor axis defocus amount, underfocus is positive.""", json_schema_extra = { "linkml_meta": {'alias': 'minor_defocus',
         'domain_of': ['PerSectionParameter'],
         'exact_mappings': ['cdp-common:per_section_minor_defocus'],
         'unit': {'descriptive_name': 'angstrom', 'symbol': 'Å'}} })
    major_defocus: Optional[float] = Field(None, description="""Major axis defocus amount, underfocus is positive.""", json_schema_extra = { "linkml_meta": {'alias': 'major_defocus',
         'domain_of': ['PerSectionParameter'],
         'exact_mappings': ['cdp-common:per_section_major_defocus'],
         'unit': {'descriptive_name': 'angstrom', 'symbol': 'Å'}} })
    max_resolution: Optional[float] = Field(None, description="""Maximum resolution of the CTF fit for this section.""", json_schema_extra = { "linkml_meta": {'alias': 'max_resolution',
         'domain_of': ['PerSectionParameter'],
         'exact_mappings': ['cdp-common:per_section_max_resolution'],
         'unit': {'descriptive_name': 'angstrom', 'symbol': 'Å'}} })
    phase_shift: Optional[float] = Field(None, description="""Phase shift measured for this section.""", json_schema_extra = { "linkml_meta": {'alias': 'phase_shift',
         'domain_of': ['PerSectionParameter'],
         'exact_mappings': ['cdp-common:per_section_phase_shift'],
         'unit': {'descriptive_name': 'radians', 'symbol': 'rad'}} })
    cross_correlation: Optional[float] = Field(None, description="""CTF fit cross correlation value for this section.""", json_schema_extra = { "linkml_meta": {'alias': 'cross_correlation',
         'domain_of': ['PerSectionParameter'],
         'exact_mappings': ['cdp-common:per_section_cross_correlation']} })


class TiltSeriesSize(ConfiguredBaseModel):
    """
    The size of a tiltseries in sctions/pixels in each dimension.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    x: int = Field(..., description="""Number of pixels in the 2D data fast axis""", ge=0, json_schema_extra = { "linkml_meta": {'alias': 'x',
         'domain_of': ['TiltSeriesSize',
                       'TomogramSize',
                       'TomogramOffset',
                       'AlignmentSize',
                       'AlignmentOffset'],
         'unit': {'descriptive_name': 'pixels', 'symbol': 'px'}} })
    y: int = Field(..., description="""Number of pixels in the 2D data medium axis""", ge=0, json_schema_extra = { "linkml_meta": {'alias': 'y',
         'domain_of': ['TiltSeriesSize',
                       'TomogramSize',
                       'TomogramOffset',
                       'AlignmentSize',
                       'AlignmentOffset'],
         'unit': {'descriptive_name': 'pixels', 'symbol': 'px'}} })
    z: int = Field(..., description="""Number of sections in the 2D stack.""", ge=0, json_schema_extra = { "linkml_meta": {'alias': 'z',
         'domain_of': ['TiltSeriesSize',
                       'TomogramSize',
                       'TomogramOffset',
                       'AlignmentSize',
                       'AlignmentOffset'],
         'unit': {'descriptive_name': 'sections'}} })


class TiltSeries(ConfiguredBaseModel):
    """
    Metadata describing a tilt series.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    acceleration_voltage: float = Field(..., description="""Electron Microscope Accelerator voltage in volts""", ge=20000, json_schema_extra = { "linkml_meta": {'alias': 'acceleration_voltage',
         'domain_of': ['TiltSeries'],
         'exact_mappings': ['cdp-common:tiltseries_acceleration_voltage'],
         'unit': {'descriptive_name': 'volts', 'symbol': 'V'}} })
    aligned_tiltseries_binning: Optional[Union[float, str]] = Field(1.0, description="""A placeholder for any type of data.""", ge=0, json_schema_extra = { "linkml_meta": {'alias': 'aligned_tiltseries_binning',
         'any_of': [{'description': 'Binning factor of the aligned tilt series',
                     'exact_mappings': ['cdp-common:tiltseries_aligned_tiltseries_binning'],
                     'minimum_value': 0,
                     'range': 'float'},
                    {'range': 'FloatFormattedString'}],
         'domain_of': ['TiltSeries'],
         'ifabsent': 'float(1)'} })
    binning_from_frames: Optional[Union[float, str]] = Field(1.0, description="""A placeholder for any type of data.""", ge=0, json_schema_extra = { "linkml_meta": {'alias': 'binning_from_frames',
         'any_of': [{'description': 'Describes the binning factor from frames to tilt '
                                    'series file',
                     'exact_mappings': ['cdp-common:tiltseries_binning_from_frames'],
                     'minimum_value': 0,
                     'range': 'float'},
                    {'range': 'FloatFormattedString'}],
         'domain_of': ['TiltSeries'],
         'ifabsent': 'float(1)'} })
    camera: CameraDetails = Field(..., description="""The camera used to collect the tilt series.""", json_schema_extra = { "linkml_meta": {'alias': 'camera', 'domain_of': ['TiltSeries']} })
    data_acquisition_software: str = Field(..., description="""Software used to collect data""", json_schema_extra = { "linkml_meta": {'alias': 'data_acquisition_software',
         'domain_of': ['TiltSeries'],
         'exact_mappings': ['cdp-common:tiltseries_data_acquisition_software']} })
    frames_count: Optional[int] = Field(None, description="""Number of frames associated with this tiltseries""", json_schema_extra = { "linkml_meta": {'alias': 'frames_count',
         'domain_of': ['TiltSeries'],
         'exact_mappings': ['cdp-common:tiltseries_frames_count']} })
    is_aligned: bool = Field(..., description="""Whether this tilt series is aligned""", json_schema_extra = { "linkml_meta": {'alias': 'is_aligned',
         'domain_of': ['TiltSeries'],
         'exact_mappings': ['cdp-common:tiltseries_is_aligned']} })
    microscope: MicroscopeDetails = Field(..., description="""The microscope used to collect the tilt series.""", json_schema_extra = { "linkml_meta": {'alias': 'microscope', 'domain_of': ['TiltSeries']} })
    microscope_optical_setup: MicroscopeOpticalSetup = Field(..., description="""The optical setup of the microscope used to collect the tilt series.""", json_schema_extra = { "linkml_meta": {'alias': 'microscope_optical_setup', 'domain_of': ['TiltSeries']} })
    related_empiar_entry: Optional[str] = Field(None, description="""If a tilt series is deposited into EMPIAR, enter the EMPIAR dataset identifier""", json_schema_extra = { "linkml_meta": {'alias': 'related_empiar_entry',
         'domain_of': ['TiltSeries'],
         'exact_mappings': ['cdp-common:tiltseries_related_empiar_entry']} })
    spherical_aberration_constant: Union[float, str] = Field(..., description="""A placeholder for any type of data.""", ge=0, json_schema_extra = { "linkml_meta": {'alias': 'spherical_aberration_constant',
         'any_of': [{'description': 'Spherical Aberration Constant of the objective '
                                    'lens in millimeters',
                     'exact_mappings': ['cdp-common:tiltseries_spherical_aberration_constant'],
                     'minimum_value': 0,
                     'range': 'float',
                     'required': True,
                     'unit': {'descriptive_name': 'millimeters', 'symbol': 'mm'}},
                    {'range': 'FloatFormattedString'}],
         'domain_of': ['TiltSeries'],
         'unit': {'descriptive_name': 'millimeters', 'symbol': 'mm'}} })
    tilt_alignment_software: Optional[str] = Field(None, description="""Software used for tilt alignment""", json_schema_extra = { "linkml_meta": {'alias': 'tilt_alignment_software',
         'domain_of': ['TiltSeries'],
         'exact_mappings': ['cdp-common:tiltseries_tilt_alignment_software']} })
    tilt_axis: Union[float, str] = Field(..., description="""A placeholder for any type of data.""", ge=-360, le=360, json_schema_extra = { "linkml_meta": {'alias': 'tilt_axis',
         'any_of': [{'description': 'Rotation angle in degrees',
                     'exact_mappings': ['cdp-common:tiltseries_tilt_axis'],
                     'maximum_value': 360,
                     'minimum_value': -360,
                     'range': 'float',
                     'required': True,
                     'unit': {'descriptive_name': 'degrees', 'symbol': '°'}},
                    {'range': 'FloatFormattedString'}],
         'domain_of': ['TiltSeries'],
         'unit': {'descriptive_name': 'degrees', 'symbol': '°'}} })
    tilt_range: TiltRange = Field(..., description="""The range of tilt angles in the tilt series.""", json_schema_extra = { "linkml_meta": {'alias': 'tilt_range', 'domain_of': ['TiltSeries']} })
    tilt_series_quality: Union[int, str] = Field(..., description="""A placeholder for any type of data.""", ge=1, le=5, json_schema_extra = { "linkml_meta": {'alias': 'tilt_series_quality',
         'any_of': [{'description': 'Author assessment of tilt series quality within '
                                    'the dataset (1-5, 5 is best)',
                     'exact_mappings': ['cdp-common:tiltseries_tilt_series_quality'],
                     'maximum_value': 5,
                     'minimum_value': 1,
                     'range': 'integer',
                     'required': True},
                    {'range': 'IntegerFormattedString'}],
         'domain_of': ['TiltSeries']} })
    tilt_step: Union[float, str] = Field(..., description="""A placeholder for any type of data.""", ge=0, le=90, json_schema_extra = { "linkml_meta": {'alias': 'tilt_step',
         'any_of': [{'description': 'Tilt step in degrees',
                     'exact_mappings': ['cdp-common:tiltseries_tilt_step'],
                     'maximum_value': 90,
                     'minimum_value': 0,
                     'range': 'float',
                     'required': True,
                     'unit': {'descriptive_name': 'degrees', 'symbol': '°'}},
                    {'range': 'FloatFormattedString'}],
         'domain_of': ['TiltSeries'],
         'unit': {'descriptive_name': 'degrees', 'symbol': '°'}} })
    tilting_scheme: str = Field(..., description="""The order of stage tilting during acquisition of the data""", json_schema_extra = { "linkml_meta": {'alias': 'tilting_scheme',
         'domain_of': ['TiltSeries'],
         'exact_mappings': ['cdp-common:tiltseries_tilting_scheme']} })
    total_flux: Union[float, str] = Field(..., description="""A placeholder for any type of data.""", ge=0, json_schema_extra = { "linkml_meta": {'alias': 'total_flux',
         'any_of': [{'description': 'Number of Electrons reaching the specimen in a '
                                    'square Angstrom area for the entire tilt series',
                     'exact_mappings': ['cdp-common:tiltseries_total_flux'],
                     'minimum_value': 0,
                     'range': 'float',
                     'required': True,
                     'unit': {'descriptive_name': 'electrons per square Angstrom',
                              'symbol': 'e^-/Å^2'}},
                    {'range': 'FloatFormattedString'}],
         'domain_of': ['TiltSeries'],
         'unit': {'descriptive_name': 'electrons per square Angstrom',
                  'symbol': 'e^-/Å^2'}} })
    pixel_spacing: Union[float, str] = Field(..., description="""A placeholder for any type of data.""", ge=0.001, json_schema_extra = { "linkml_meta": {'alias': 'pixel_spacing',
         'any_of': [{'description': 'Pixel spacing for the tilt series',
                     'exact_mappings': ['cdp-common:tiltseries_pixel_spacing'],
                     'minimum_value': 0.001,
                     'range': 'float',
                     'required': True,
                     'unit': {'descriptive_name': 'Angstroms per pixel',
                              'symbol': 'Å/px'}},
                    {'range': 'FloatFormattedString'}],
         'domain_of': ['TiltSeries'],
         'unit': {'descriptive_name': 'Angstroms per pixel', 'symbol': 'Å/px'}} })

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
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    x: int = Field(..., description="""Number of pixels in the 3D data fast axis""", ge=0, json_schema_extra = { "linkml_meta": {'alias': 'x',
         'domain_of': ['TiltSeriesSize',
                       'TomogramSize',
                       'TomogramOffset',
                       'AlignmentSize',
                       'AlignmentOffset'],
         'unit': {'descriptive_name': 'pixels', 'symbol': 'px'}} })
    y: int = Field(..., description="""Number of pixels in the 3D data medium axis""", ge=0, json_schema_extra = { "linkml_meta": {'alias': 'y',
         'domain_of': ['TiltSeriesSize',
                       'TomogramSize',
                       'TomogramOffset',
                       'AlignmentSize',
                       'AlignmentOffset'],
         'unit': {'descriptive_name': 'pixels', 'symbol': 'px'}} })
    z: int = Field(..., description="""Number of pixels in the 3D data slow axis.  This is the image projection direction at zero stage tilt""", ge=0, json_schema_extra = { "linkml_meta": {'alias': 'z',
         'domain_of': ['TiltSeriesSize',
                       'TomogramSize',
                       'TomogramOffset',
                       'AlignmentSize',
                       'AlignmentOffset'],
         'unit': {'descriptive_name': 'pixels', 'symbol': 'px'}} })


class TomogramOffset(ConfiguredBaseModel):
    """
    The offset of a tomogram in voxels in each dimension relative to the canonical tomogram.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    x: int = Field(..., description="""x offset data relative to the canonical tomogram in pixels""", json_schema_extra = { "linkml_meta": {'alias': 'x',
         'domain_of': ['TiltSeriesSize',
                       'TomogramSize',
                       'TomogramOffset',
                       'AlignmentSize',
                       'AlignmentOffset'],
         'unit': {'descriptive_name': 'pixels', 'symbol': 'px'}} })
    y: int = Field(..., description="""y offset data relative to the canonical tomogram in pixels""", json_schema_extra = { "linkml_meta": {'alias': 'y',
         'domain_of': ['TiltSeriesSize',
                       'TomogramSize',
                       'TomogramOffset',
                       'AlignmentSize',
                       'AlignmentOffset'],
         'unit': {'descriptive_name': 'pixels', 'symbol': 'px'}} })
    z: int = Field(..., description="""z offset data relative to the canonical tomogram in pixels""", json_schema_extra = { "linkml_meta": {'alias': 'z',
         'domain_of': ['TiltSeriesSize',
                       'TomogramSize',
                       'TomogramOffset',
                       'AlignmentSize',
                       'AlignmentOffset'],
         'unit': {'descriptive_name': 'pixels', 'symbol': 'px'}} })


class Tomogram(AuthoredEntity):
    """
    Metadata describing a tomogram.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata', 'mixins': ['AuthoredEntity']})

    voxel_spacing: Union[float, str] = Field(..., description="""A placeholder for any type of data.""", ge=0.001, json_schema_extra = { "linkml_meta": {'alias': 'voxel_spacing',
         'any_of': [{'description': 'Voxel spacing equal in all three axes in '
                                    'angstroms',
                     'exact_mappings': ['cdp-common:tomogram_voxel_spacing'],
                     'minimum_value': 0.001,
                     'range': 'float',
                     'required': True,
                     'unit': {'descriptive_name': 'Angstroms per voxel',
                              'symbol': 'Å/voxel'}},
                    {'range': 'FloatFormattedString'}],
         'domain_of': ['Tomogram',
                       'AnnotationParent',
                       'KeyImageParent',
                       'TomogramParent'],
         'unit': {'descriptive_name': 'Angstroms per voxel', 'symbol': 'Å/voxel'}} })
    fiducial_alignment_status: Union[FiducialAlignmentStatusEnum, str] = Field(..., description="""A placeholder for any type of data.""", json_schema_extra = { "linkml_meta": {'alias': 'fiducial_alignment_status',
         'any_of': [{'description': 'Whether the tomographic alignment was computed '
                                    'based on fiducial markers.',
                     'exact_mappings': ['cdp-common:tomogram_fiducial_alignment_status'],
                     'range': 'fiducial_alignment_status_enum',
                     'required': True},
                    {'range': 'StringFormattedString'}],
         'domain_of': ['Tomogram']} })
    ctf_corrected: Optional[bool] = Field(None, description="""Whether this tomogram is CTF corrected""", json_schema_extra = { "linkml_meta": {'alias': 'ctf_corrected',
         'domain_of': ['Tomogram'],
         'exact_mappings': ['cdp-common:tomogram_ctf_corrected'],
         'recommended': True} })
    align_software: Optional[str] = Field(None, description="""Software used for alignment""", json_schema_extra = { "linkml_meta": {'alias': 'align_software',
         'domain_of': ['Tomogram'],
         'exact_mappings': ['cdp-common:tomogram_align_software']} })
    reconstruction_method: Union[TomogramReconstructionMethodEnum, str] = Field(..., description="""A placeholder for any type of data.""", json_schema_extra = { "linkml_meta": {'alias': 'reconstruction_method',
         'any_of': [{'description': 'Describe reconstruction method (WBP, SART, SIRT)',
                     'exact_mappings': ['cdp-common:tomogram_reconstruction_method'],
                     'range': 'tomogram_reconstruction_method_enum',
                     'required': True},
                    {'range': 'StringFormattedString'}],
         'domain_of': ['Tomogram']} })
    reconstruction_software: str = Field(..., description="""Name of software used for reconstruction""", json_schema_extra = { "linkml_meta": {'alias': 'reconstruction_software',
         'domain_of': ['Tomogram'],
         'exact_mappings': ['cdp-common:tomogram_reconstruction_software']} })
    processing: TomogramProcessingEnum = Field(..., description="""Describe additional processing used to derive the tomogram""", json_schema_extra = { "linkml_meta": {'alias': 'processing',
         'domain_of': ['Tomogram'],
         'exact_mappings': ['cdp-common:tomogram_processing']} })
    processing_software: Optional[str] = Field(None, description="""Processing software used to derive the tomogram""", json_schema_extra = { "linkml_meta": {'alias': 'processing_software',
         'domain_of': ['Tomogram'],
         'exact_mappings': ['cdp-common:tomogram_processing_software'],
         'recommended': True} })
    tomogram_version: float = Field(..., description="""Version of tomogram""", json_schema_extra = { "linkml_meta": {'alias': 'tomogram_version',
         'domain_of': ['Tomogram'],
         'exact_mappings': ['cdp-common:tomogram_version']} })
    affine_transformation_matrix: Optional[conlist(min_length=4, max_length=4, item_type=conlist(min_length=4, max_length=4, item_type=float))] = Field(None, description="""The flip or rotation transformation of this author submitted tomogram is indicated here""", json_schema_extra = { "linkml_meta": {'alias': 'affine_transformation_matrix',
         'array': {'dimensions': [{'exact_cardinality': 4}, {'exact_cardinality': 4}],
                   'exact_number_dimensions': 2},
         'domain_of': ['Tomogram', 'Alignment']} })
    size: Optional[TomogramSize] = Field(None, description="""The size of a tomogram in voxels in each dimension.""", json_schema_extra = { "linkml_meta": {'alias': 'size', 'domain_of': ['Tomogram']} })
    offset: TomogramOffset = Field(..., description="""The offset of a tomogram in voxels in each dimension relative to the canonical tomogram.""", json_schema_extra = { "linkml_meta": {'alias': 'offset', 'domain_of': ['Tomogram']} })
    is_visualization_default: bool = Field(True, description="""Whether the tomogram is the default for visualization.""", json_schema_extra = { "linkml_meta": {'alias': 'is_visualization_default',
         'domain_of': ['Tomogram',
                       'AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'ifabsent': 'True'} })
    cross_references: Optional[CrossReferences] = Field(None, description="""A set of cross-references to other databases and publications.""", json_schema_extra = { "linkml_meta": {'alias': 'cross_references',
         'domain_of': ['CrossReferencedEntity', 'Tomogram', 'Dataset', 'Deposition']} })
    dates: DateStamp = Field(..., description="""A set of dates at which a data item was deposited, published and last modified.""", json_schema_extra = { "linkml_meta": {'alias': 'dates',
         'domain_of': ['DateStampedEntity',
                       'Tomogram',
                       'Dataset',
                       'Deposition',
                       'Annotation']} })
    authors: List[Author] = Field(..., description="""Author of a scientific data entity.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'authors',
         'domain_of': ['AuthoredEntity',
                       'Dataset',
                       'Deposition',
                       'Tomogram',
                       'Annotation'],
         'list_elements_ordered': True} })

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
        pattern=re.compile(r"(^SART$)|(^Fourier Space$)|(^SIRT$)|(^WBP$)|(^Unknown$)|(^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$)")
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
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    precision: Optional[float] = Field(None, description="""Describe the confidence level of the annotation. Precision is defined as the % of annotation objects being true positive""", ge=0, le=100, json_schema_extra = { "linkml_meta": {'alias': 'precision',
         'domain_of': ['AnnotationConfidence'],
         'exact_mappings': ['cdp-common:annotation_confidence_precision'],
         'unit': {'descriptive_name': 'percentage', 'symbol': '%'}} })
    recall: Optional[float] = Field(None, description="""Describe the confidence level of the annotation. Recall is defined as the % of true positives being annotated correctly""", ge=0, le=100, json_schema_extra = { "linkml_meta": {'alias': 'recall',
         'domain_of': ['AnnotationConfidence'],
         'exact_mappings': ['cdp-common:annotation_confidence_recall'],
         'unit': {'descriptive_name': 'percentage', 'symbol': '%'}} })
    ground_truth_used: Optional[str] = Field(None, description="""Annotation filename used as ground truth for precision and recall""", json_schema_extra = { "linkml_meta": {'alias': 'ground_truth_used',
         'domain_of': ['AnnotationConfidence'],
         'exact_mappings': ['cdp-common:annotation_ground_truth_used']} })


class AnnotationObject(ConfiguredBaseModel):
    """
    Metadata describing the object being annotated.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    id: str = Field(..., description="""A placeholder for any type of data.""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'any_of': [{'range': 'GO_ID'}, {'range': 'UNIPROT_ID'}],
         'domain_of': ['Assay',
                       'DevelopmentStageDetails',
                       'Disease',
                       'TissueDetails',
                       'CellType',
                       'CellStrain',
                       'CellComponent',
                       'AnnotationObject'],
         'exact_mappings': ['cdp-common:annotation_object_id']} })
    name: str = Field(..., description="""Name of the object being annotated (e.g. ribosome, nuclear pore complex, actin filament, membrane)""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Assay',
                       'DevelopmentStageDetails',
                       'Disease',
                       'OrganismDetails',
                       'TissueDetails',
                       'CellType',
                       'CellStrain',
                       'CellComponent',
                       'AnnotationObject',
                       'AnnotationTriangularMeshGroupFile',
                       'AuthorMixin',
                       'Author'],
         'exact_mappings': ['cdp-common:annotation_object_name']} })
    description: Optional[str] = Field(None, description="""A textual description of the annotation object, can be a longer description to include additional information not covered by the Annotation object name and state.""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['AnnotationObject'],
         'exact_mappings': ['cdp-common:annotation_object_description']} })
    state: Optional[str] = Field(None, description="""Molecule state annotated (e.g. open, closed)""", json_schema_extra = { "linkml_meta": {'alias': 'state',
         'domain_of': ['AnnotationObject'],
         'exact_mappings': ['cdp-common:annotation_object_state']} })

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"(^GO:[0-9]{7}$)|(^UniProtKB:[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid id format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid id format: {v}")
        return v


class AnnotationMethodLinks(ConfiguredBaseModel):
    """
    A set of links to models, source code, documentation, etc referenced by annotation the method
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    link: str = Field(..., description="""URL to the annotation method reference""", json_schema_extra = { "linkml_meta": {'alias': 'link',
         'domain_of': ['AnnotationMethodLinks'],
         'exact_mappings': ['cdp-common:annotation_method_link']} })
    link_type: AnnotationMethodLinkTypeEnum = Field(..., description="""Type of link (e.g. model, source code, documentation)""", json_schema_extra = { "linkml_meta": {'alias': 'link_type',
         'domain_of': ['AnnotationMethodLinks'],
         'exact_mappings': ['cdp-common:annotation_method_link_type']} })
    custom_name: Optional[str] = Field(None, description="""user readable name of the resource""", json_schema_extra = { "linkml_meta": {'alias': 'custom_name',
         'domain_of': ['AnnotationMethodLinks'],
         'exact_mappings': ['cdp-common:annotation_method_link_custom_name'],
         'recommended': True} })

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


class AnnotationSourceFile(ConfiguredBaseModel):
    """
    File and sourcing data for an annotation. Represents an entry in annotation.sources.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    file_format: str = Field(..., description="""File format for this file""", json_schema_extra = { "linkml_meta": {'alias': 'file_format',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_format']} })
    glob_string: Optional[str] = Field(None, description="""Glob string to match annotation files in the dataset. Required if annotation_source_file_glob_strings is not provided.""", json_schema_extra = { "linkml_meta": {'alias': 'glob_string',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_glob_string']} })
    glob_strings: Optional[List[str]] = Field(None, description="""Glob strings to match annotation files in the dataset. Required if annotation_source_file_glob_string is not provided.""", json_schema_extra = { "linkml_meta": {'alias': 'glob_strings',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_glob_strings']} })
    is_visualization_default: Optional[bool] = Field(False, description="""This annotation will be rendered in neuroglancer by default.""", json_schema_extra = { "linkml_meta": {'alias': 'is_visualization_default',
         'domain_of': ['Tomogram',
                       'AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_is_visualization_default'],
         'ifabsent': 'False'} })
    is_portal_standard: Optional[bool] = Field(False, description="""Whether the annotation source is a portal standard.""", json_schema_extra = { "linkml_meta": {'alias': 'is_portal_standard',
         'domain_of': ['AnnotationSourceFile',
                       'Alignment',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_is_portal_standard'],
         'ifabsent': 'False'} })


class AnnotationOrientedPointFile(AnnotationSourceFile):
    """
    File and sourcing data for an oriented point annotation. Annotation that identifies points along with orientation in the volume.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'aliases': ['OrientedPoint'], 'from_schema': 'metadata'})

    binning: Optional[float] = Field(1.0, description="""The binning factor for a point / oriented point / instance segmentation annotation file.""", ge=0, json_schema_extra = { "linkml_meta": {'alias': 'binning',
         'domain_of': ['AnnotationOrientedPointFile',
                       'AnnotationPointFile',
                       'AnnotationInstanceSegmentationFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_binning'],
         'ifabsent': 'float(1)'} })
    filter_value: Optional[str] = Field(None, description="""The filter value for an oriented point / instance segmentation annotation file.""", json_schema_extra = { "linkml_meta": {'alias': 'filter_value',
         'domain_of': ['AnnotationOrientedPointFile',
                       'AnnotationPointFile',
                       'IdentifiedObjectList',
                       'AnnotationInstanceSegmentationFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_filter_value']} })
    order: Optional[str] = Field("xyz", description="""The order of axes for an oriented point / instance segmentation annotation file.""", json_schema_extra = { "linkml_meta": {'alias': 'order',
         'domain_of': ['AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_order'],
         'ifabsent': 'string(xyz)'} })
    mesh_source_path: Optional[str] = Field(None, description="""The path to the mesh source file associated with an oriented point file.""", json_schema_extra = { "linkml_meta": {'alias': 'mesh_source_path',
         'domain_of': ['AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_mesh_source_path']} })
    file_format: str = Field(..., description="""File format for this file""", json_schema_extra = { "linkml_meta": {'alias': 'file_format',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_format']} })
    glob_string: Optional[str] = Field(None, description="""Glob string to match annotation files in the dataset. Required if annotation_source_file_glob_strings is not provided.""", json_schema_extra = { "linkml_meta": {'alias': 'glob_string',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_glob_string']} })
    glob_strings: Optional[List[str]] = Field(None, description="""Glob strings to match annotation files in the dataset. Required if annotation_source_file_glob_string is not provided.""", json_schema_extra = { "linkml_meta": {'alias': 'glob_strings',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_glob_strings']} })
    is_visualization_default: Optional[bool] = Field(False, description="""This annotation will be rendered in neuroglancer by default.""", json_schema_extra = { "linkml_meta": {'alias': 'is_visualization_default',
         'domain_of': ['Tomogram',
                       'AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_is_visualization_default'],
         'ifabsent': 'False'} })
    is_portal_standard: Optional[bool] = Field(False, description="""Whether the annotation source is a portal standard.""", json_schema_extra = { "linkml_meta": {'alias': 'is_portal_standard',
         'domain_of': ['AnnotationSourceFile',
                       'Alignment',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_is_portal_standard'],
         'ifabsent': 'False'} })


class AnnotationInstanceSegmentationFile(AnnotationOrientedPointFile):
    """
    File and sourcing data for an instance segmentation annotation. Annotation that identifies individual instances of object shapes.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'aliases': ['InstanceSegmentation'], 'from_schema': 'metadata'})

    binning: Optional[float] = Field(1.0, description="""The binning factor for a point / oriented point / instance segmentation annotation file.""", ge=0, json_schema_extra = { "linkml_meta": {'alias': 'binning',
         'domain_of': ['AnnotationOrientedPointFile',
                       'AnnotationPointFile',
                       'AnnotationInstanceSegmentationFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_binning'],
         'ifabsent': 'float(1)'} })
    filter_value: Optional[str] = Field(None, description="""The filter value for an oriented point / instance segmentation annotation file.""", json_schema_extra = { "linkml_meta": {'alias': 'filter_value',
         'domain_of': ['AnnotationOrientedPointFile',
                       'AnnotationPointFile',
                       'IdentifiedObjectList',
                       'AnnotationInstanceSegmentationFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_filter_value']} })
    order: Optional[str] = Field("xyz", description="""The order of axes for an oriented point / instance segmentation annotation file.""", json_schema_extra = { "linkml_meta": {'alias': 'order',
         'domain_of': ['AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_order'],
         'ifabsent': 'string(xyz)'} })
    mesh_source_path: Optional[str] = Field(None, description="""The path to the mesh source file associated with an oriented point file.""", json_schema_extra = { "linkml_meta": {'alias': 'mesh_source_path',
         'domain_of': ['AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_mesh_source_path']} })
    file_format: str = Field(..., description="""File format for this file""", json_schema_extra = { "linkml_meta": {'alias': 'file_format',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_format']} })
    glob_string: Optional[str] = Field(None, description="""Glob string to match annotation files in the dataset. Required if annotation_source_file_glob_strings is not provided.""", json_schema_extra = { "linkml_meta": {'alias': 'glob_string',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_glob_string']} })
    glob_strings: Optional[List[str]] = Field(None, description="""Glob strings to match annotation files in the dataset. Required if annotation_source_file_glob_string is not provided.""", json_schema_extra = { "linkml_meta": {'alias': 'glob_strings',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_glob_strings']} })
    is_visualization_default: Optional[bool] = Field(False, description="""This annotation will be rendered in neuroglancer by default.""", json_schema_extra = { "linkml_meta": {'alias': 'is_visualization_default',
         'domain_of': ['Tomogram',
                       'AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_is_visualization_default'],
         'ifabsent': 'False'} })
    is_portal_standard: Optional[bool] = Field(False, description="""Whether the annotation source is a portal standard.""", json_schema_extra = { "linkml_meta": {'alias': 'is_portal_standard',
         'domain_of': ['AnnotationSourceFile',
                       'Alignment',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_is_portal_standard'],
         'ifabsent': 'False'} })


class AnnotationPointFile(AnnotationSourceFile):
    """
    File and sourcing data for a point annotation. Annotation that identifies points in the volume.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'aliases': ['Point'], 'from_schema': 'metadata'})

    binning: Optional[float] = Field(1.0, description="""The binning factor for a point / oriented point / instance segmentation annotation file.""", ge=0, json_schema_extra = { "linkml_meta": {'alias': 'binning',
         'domain_of': ['AnnotationOrientedPointFile',
                       'AnnotationPointFile',
                       'AnnotationInstanceSegmentationFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_binning'],
         'ifabsent': 'float(1)'} })
    columns: Optional[str] = Field("xyz", description="""The columns used in a point annotation file.""", json_schema_extra = { "linkml_meta": {'alias': 'columns',
         'domain_of': ['AnnotationPointFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_columns'],
         'ifabsent': 'string(xyz)'} })
    delimiter: Optional[str] = Field(",", description="""The delimiter used in a point annotation file.""", json_schema_extra = { "linkml_meta": {'alias': 'delimiter',
         'domain_of': ['AnnotationPointFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_delimiter'],
         'ifabsent': 'string(,)'} })
    filter_value: Optional[str] = Field(None, description="""The filter value for an oriented point / instance segmentation annotation file.""", json_schema_extra = { "linkml_meta": {'alias': 'filter_value',
         'domain_of': ['AnnotationOrientedPointFile',
                       'AnnotationPointFile',
                       'IdentifiedObjectList',
                       'AnnotationInstanceSegmentationFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_filter_value']} })
    file_format: str = Field(..., description="""File format for this file""", json_schema_extra = { "linkml_meta": {'alias': 'file_format',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_format']} })
    glob_string: Optional[str] = Field(None, description="""Glob string to match annotation files in the dataset. Required if annotation_source_file_glob_strings is not provided.""", json_schema_extra = { "linkml_meta": {'alias': 'glob_string',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_glob_string']} })
    glob_strings: Optional[List[str]] = Field(None, description="""Glob strings to match annotation files in the dataset. Required if annotation_source_file_glob_string is not provided.""", json_schema_extra = { "linkml_meta": {'alias': 'glob_strings',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_glob_strings']} })
    is_visualization_default: Optional[bool] = Field(False, description="""This annotation will be rendered in neuroglancer by default.""", json_schema_extra = { "linkml_meta": {'alias': 'is_visualization_default',
         'domain_of': ['Tomogram',
                       'AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_is_visualization_default'],
         'ifabsent': 'False'} })
    is_portal_standard: Optional[bool] = Field(False, description="""Whether the annotation source is a portal standard.""", json_schema_extra = { "linkml_meta": {'alias': 'is_portal_standard',
         'domain_of': ['AnnotationSourceFile',
                       'Alignment',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_is_portal_standard'],
         'ifabsent': 'False'} })


class AnnotationSegmentationMaskFile(AnnotationSourceFile):
    """
    File and sourcing data for a segmentation mask annotation. Annotation that identifies an object.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'aliases': ['SegmentationMask'], 'from_schema': 'metadata'})

    file_format: str = Field(..., description="""File format for this file""", json_schema_extra = { "linkml_meta": {'alias': 'file_format',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_format']} })
    glob_string: Optional[str] = Field(None, description="""Glob string to match annotation files in the dataset. Required if annotation_source_file_glob_strings is not provided.""", json_schema_extra = { "linkml_meta": {'alias': 'glob_string',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_glob_string']} })
    glob_strings: Optional[List[str]] = Field(None, description="""Glob strings to match annotation files in the dataset. Required if annotation_source_file_glob_string is not provided.""", json_schema_extra = { "linkml_meta": {'alias': 'glob_strings',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_glob_strings']} })
    is_visualization_default: Optional[bool] = Field(False, description="""This annotation will be rendered in neuroglancer by default.""", json_schema_extra = { "linkml_meta": {'alias': 'is_visualization_default',
         'domain_of': ['Tomogram',
                       'AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_is_visualization_default'],
         'ifabsent': 'False'} })
    is_portal_standard: Optional[bool] = Field(False, description="""Whether the annotation source is a portal standard.""", json_schema_extra = { "linkml_meta": {'alias': 'is_portal_standard',
         'domain_of': ['AnnotationSourceFile',
                       'Alignment',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_is_portal_standard'],
         'ifabsent': 'False'} })


class AnnotationSemanticSegmentationMaskFile(AnnotationSourceFile):
    """
    File and sourcing data for a semantic segmentation mask annotation. Annotation that identifies classes of objects.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'aliases': ['SemanticSegmentationMask'], 'from_schema': 'metadata'})

    mask_label: Optional[int] = Field(1, description="""The mask label for a semantic segmentation mask annotation file.""", json_schema_extra = { "linkml_meta": {'alias': 'mask_label',
         'domain_of': ['AnnotationSemanticSegmentationMaskFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_mask_label'],
         'ifabsent': 'int(1)'} })
    rescale: Optional[bool] = Field(False, description="""Whether the annotation file needs to be rescaled.""", json_schema_extra = { "linkml_meta": {'alias': 'rescale',
         'domain_of': ['AnnotationSemanticSegmentationMaskFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_rescale'],
         'ifabsent': 'False'} })
    threshold: Optional[float] = Field(None, description="""The threshold for a segmentation mask annotation file.""", json_schema_extra = { "linkml_meta": {'alias': 'threshold',
         'domain_of': ['AnnotationSemanticSegmentationMaskFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_threshold']} })
    file_format: str = Field(..., description="""File format for this file""", json_schema_extra = { "linkml_meta": {'alias': 'file_format',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_format']} })
    glob_string: Optional[str] = Field(None, description="""Glob string to match annotation files in the dataset. Required if annotation_source_file_glob_strings is not provided.""", json_schema_extra = { "linkml_meta": {'alias': 'glob_string',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_glob_string']} })
    glob_strings: Optional[List[str]] = Field(None, description="""Glob strings to match annotation files in the dataset. Required if annotation_source_file_glob_string is not provided.""", json_schema_extra = { "linkml_meta": {'alias': 'glob_strings',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_glob_strings']} })
    is_visualization_default: Optional[bool] = Field(False, description="""This annotation will be rendered in neuroglancer by default.""", json_schema_extra = { "linkml_meta": {'alias': 'is_visualization_default',
         'domain_of': ['Tomogram',
                       'AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_is_visualization_default'],
         'ifabsent': 'False'} })
    is_portal_standard: Optional[bool] = Field(False, description="""Whether the annotation source is a portal standard.""", json_schema_extra = { "linkml_meta": {'alias': 'is_portal_standard',
         'domain_of': ['AnnotationSourceFile',
                       'Alignment',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_is_portal_standard'],
         'ifabsent': 'False'} })


class AnnotationTriangularMeshFile(AnnotationSourceFile):
    """
    File and sourcing data for a triangular mesh annotation. Annotation that identifies an object.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'aliases': ['TriangularMesh'], 'from_schema': 'metadata'})

    scale_factor: Optional[float] = Field(1.0, description="""The scale factor for a mesh annotation file.""", ge=0, json_schema_extra = { "linkml_meta": {'alias': 'scale_factor',
         'domain_of': ['AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_scale_factor'],
         'ifabsent': 'float(1)'} })
    file_format: str = Field(..., description="""File format for this file""", json_schema_extra = { "linkml_meta": {'alias': 'file_format',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_format']} })
    glob_string: Optional[str] = Field(None, description="""Glob string to match annotation files in the dataset. Required if annotation_source_file_glob_strings is not provided.""", json_schema_extra = { "linkml_meta": {'alias': 'glob_string',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_glob_string']} })
    glob_strings: Optional[List[str]] = Field(None, description="""Glob strings to match annotation files in the dataset. Required if annotation_source_file_glob_string is not provided.""", json_schema_extra = { "linkml_meta": {'alias': 'glob_strings',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_glob_strings']} })
    is_visualization_default: Optional[bool] = Field(False, description="""This annotation will be rendered in neuroglancer by default.""", json_schema_extra = { "linkml_meta": {'alias': 'is_visualization_default',
         'domain_of': ['Tomogram',
                       'AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_is_visualization_default'],
         'ifabsent': 'False'} })
    is_portal_standard: Optional[bool] = Field(False, description="""Whether the annotation source is a portal standard.""", json_schema_extra = { "linkml_meta": {'alias': 'is_portal_standard',
         'domain_of': ['AnnotationSourceFile',
                       'Alignment',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_is_portal_standard'],
         'ifabsent': 'False'} })


class AnnotationTriangularMeshGroupFile(AnnotationSourceFile):
    """
    File and sourcing data containing one or more triangular mesh annotations.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'aliases': ['TriangularMeshGroup'], 'from_schema': 'metadata'})

    scale_factor: Optional[float] = Field(1.0, description="""The scale factor for a mesh annotation file.""", ge=0, json_schema_extra = { "linkml_meta": {'alias': 'scale_factor',
         'domain_of': ['AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_scale_factor'],
         'ifabsent': 'float(1)'} })
    name: Optional[str] = Field(None, description="""The name that identifies to a single annotation mesh among multiple meshes.""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Assay',
                       'DevelopmentStageDetails',
                       'Disease',
                       'OrganismDetails',
                       'TissueDetails',
                       'CellType',
                       'CellStrain',
                       'CellComponent',
                       'AnnotationObject',
                       'AnnotationTriangularMeshGroupFile',
                       'AuthorMixin',
                       'Author'],
         'exact_mappings': ['cdp-common:annotation_source_file_mesh_name']} })
    file_format: str = Field(..., description="""File format for this file""", json_schema_extra = { "linkml_meta": {'alias': 'file_format',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_format']} })
    glob_string: Optional[str] = Field(None, description="""Glob string to match annotation files in the dataset. Required if annotation_source_file_glob_strings is not provided.""", json_schema_extra = { "linkml_meta": {'alias': 'glob_string',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_glob_string']} })
    glob_strings: Optional[List[str]] = Field(None, description="""Glob strings to match annotation files in the dataset. Required if annotation_source_file_glob_string is not provided.""", json_schema_extra = { "linkml_meta": {'alias': 'glob_strings',
         'domain_of': ['AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_glob_strings']} })
    is_visualization_default: Optional[bool] = Field(False, description="""This annotation will be rendered in neuroglancer by default.""", json_schema_extra = { "linkml_meta": {'alias': 'is_visualization_default',
         'domain_of': ['Tomogram',
                       'AnnotationSourceFile',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_is_visualization_default'],
         'ifabsent': 'False'} })
    is_portal_standard: Optional[bool] = Field(False, description="""Whether the annotation source is a portal standard.""", json_schema_extra = { "linkml_meta": {'alias': 'is_portal_standard',
         'domain_of': ['AnnotationSourceFile',
                       'Alignment',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:annotation_source_file_is_portal_standard'],
         'ifabsent': 'False'} })


class IdentifiedObject(ConfiguredBaseModel):
    """
    Metadata describing an identified object.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    object_id: str = Field(..., description="""A placeholder for any type of data.""", json_schema_extra = { "linkml_meta": {'alias': 'object_id',
         'any_of': [{'range': 'GO_ID'}, {'range': 'UNIPROT_ID'}],
         'domain_of': ['IdentifiedObject'],
         'exact_mappings': ['cdp-common:identified_object_id']} })
    object_name: str = Field(..., description="""Name of the object that was identified (e.g. ribosome, nuclear pore complex, actin filament, membrane)""", json_schema_extra = { "linkml_meta": {'alias': 'object_name',
         'domain_of': ['IdentifiedObject'],
         'exact_mappings': ['cdp-common:identified_object_name']} })
    object_description: Optional[str] = Field(None, description="""A textual description of the identified object, can be a longer description to include additional information not covered by the identified object name and state.""", json_schema_extra = { "linkml_meta": {'alias': 'object_description',
         'domain_of': ['IdentifiedObject'],
         'exact_mappings': ['cdp-common:identified_object_description']} })
    object_state: Optional[str] = Field(None, description="""Molecule state identified (e.g. open, closed)""", json_schema_extra = { "linkml_meta": {'alias': 'object_state',
         'domain_of': ['IdentifiedObject'],
         'exact_mappings': ['cdp-common:identified_object_state']} })

    @field_validator('object_id')
    def pattern_object_id(cls, v):
        pattern=re.compile(r"(^GO:[0-9]{7}$)|(^UniProtKB:[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid object_id format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid object_id format: {v}")
        return v


class IdentifiedObjectList(ConfiguredBaseModel):
    """
    Metadata for a list of identified objects.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    filter_value: Optional[str] = Field(None, description="""Filter value for the identified object, used to filter the list of identified objects by run name.""", json_schema_extra = { "linkml_meta": {'alias': 'filter_value',
         'domain_of': ['AnnotationOrientedPointFile',
                       'AnnotationPointFile',
                       'IdentifiedObjectList',
                       'AnnotationInstanceSegmentationFile'],
         'exact_mappings': ['cdp-common:identified_object_filter_value']} })


class Annotation(AuthoredEntity, DateStampedEntity):
    """
    Metadata describing an annotation.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata', 'mixins': ['DateStampedEntity', 'AuthoredEntity']})

    annotation_method: str = Field(..., description="""Describe how the annotation is made (e.g. Manual, crYoLO, Positive Unlabeled Learning, template matching)""", json_schema_extra = { "linkml_meta": {'alias': 'annotation_method',
         'domain_of': ['Annotation'],
         'exact_mappings': ['cdp-common:annotation_method']} })
    annotation_object: AnnotationObject = Field(..., description="""Metadata describing the object being annotated.""", json_schema_extra = { "linkml_meta": {'alias': 'annotation_object', 'domain_of': ['Annotation']} })
    annotation_publications: Optional[str] = Field(None, description="""List of publication IDs (EMPIAR, EMDB, DOI, PDB) that describe this annotation method. Comma separated.""", json_schema_extra = { "linkml_meta": {'alias': 'annotation_publications',
         'domain_of': ['Annotation'],
         'exact_mappings': ['cdp-common:annotation_publications']} })
    annotation_software: Optional[str] = Field(None, description="""Software used for generating this annotation""", json_schema_extra = { "linkml_meta": {'alias': 'annotation_software',
         'domain_of': ['Annotation'],
         'exact_mappings': ['cdp-common:annotation_software'],
         'recommended': True} })
    confidence: Optional[AnnotationConfidence] = Field(None, description="""Metadata describing the confidence of an annotation.""", json_schema_extra = { "linkml_meta": {'alias': 'confidence', 'domain_of': ['Annotation']} })
    files: Optional[List[AnnotationSourceFile]] = Field(None, description="""File and sourcing data for an annotation. Represents an entry in annotation.sources.""", json_schema_extra = { "linkml_meta": {'alias': 'files', 'domain_of': ['Annotation'], 'list_elements_ordered': True} })
    ground_truth_status: Optional[bool] = Field(False, description="""Whether an annotation is considered ground truth, as determined by the annotator.""", json_schema_extra = { "linkml_meta": {'alias': 'ground_truth_status',
         'domain_of': ['Annotation'],
         'exact_mappings': ['cdp-common:annotation_ground_truth_status'],
         'ifabsent': 'False',
         'recommended': True} })
    is_curator_recommended: Optional[bool] = Field(False, description="""This annotation is recommended by the curator to be preferred for this object type.""", json_schema_extra = { "linkml_meta": {'alias': 'is_curator_recommended',
         'domain_of': ['Annotation'],
         'exact_mappings': ['cdp-common:annotation_is_curator_recommended'],
         'ifabsent': 'False'} })
    method_type: AnnotationMethodTypeEnum = Field(..., description="""Classification of the annotation method based on supervision.""", json_schema_extra = { "linkml_meta": {'alias': 'method_type',
         'domain_of': ['Annotation', 'Alignment'],
         'exact_mappings': ['cdp-common:annotation_method_type']} })
    method_links: Optional[List[AnnotationMethodLinks]] = Field(None, description="""A set of links to models, source code, documentation, etc referenced by annotation the method""", json_schema_extra = { "linkml_meta": {'alias': 'method_links', 'domain_of': ['Annotation']} })
    object_count: Optional[int] = Field(None, description="""Number of objects identified""", json_schema_extra = { "linkml_meta": {'alias': 'object_count',
         'domain_of': ['Annotation'],
         'exact_mappings': ['cdp-common:annotation_object_count']} })
    version: Optional[float] = Field(None, description="""Version of annotation.""", json_schema_extra = { "linkml_meta": {'alias': 'version',
         'domain_of': ['Annotation', 'Container'],
         'exact_mappings': ['cdp-common:annotation_version']} })
    dates: DateStamp = Field(..., description="""A set of dates at which a data item was deposited, published and last modified.""", json_schema_extra = { "linkml_meta": {'alias': 'dates',
         'domain_of': ['DateStampedEntity',
                       'Tomogram',
                       'Dataset',
                       'Deposition',
                       'Annotation']} })
    authors: List[Author] = Field(..., description="""Author of a scientific data entity.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'authors',
         'domain_of': ['AuthoredEntity',
                       'Dataset',
                       'Deposition',
                       'Tomogram',
                       'Annotation'],
         'list_elements_ordered': True} })

    @field_validator('annotation_publications')
    def pattern_annotation_publications(cls, v):
        pattern=re.compile(r"^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+|PDB-[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+|PDB-[0-9a-zA-Z]{4,8}))*$")
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
        pattern=re.compile(r"(^manual$)|(^automated$)|(^hybrid$)|(^simulated$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid method_type format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid method_type format: {v}")
        return v


class AlignmentSize(ConfiguredBaseModel):
    """
    The size of an alignment in voxels in each dimension.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    x: Union[float, str] = Field(..., description="""A placeholder for any type of data.""", json_schema_extra = { "linkml_meta": {'alias': 'x',
         'any_of': [{'range': 'float'}, {'range': 'FloatFormattedString'}],
         'domain_of': ['TiltSeriesSize',
                       'TomogramSize',
                       'TomogramOffset',
                       'AlignmentSize',
                       'AlignmentOffset'],
         'unit': {'descriptive_name': 'Angstrom', 'symbol': 'Å'}} })
    y: Union[float, str] = Field(..., description="""A placeholder for any type of data.""", json_schema_extra = { "linkml_meta": {'alias': 'y',
         'any_of': [{'range': 'float'}, {'range': 'FloatFormattedString'}],
         'domain_of': ['TiltSeriesSize',
                       'TomogramSize',
                       'TomogramOffset',
                       'AlignmentSize',
                       'AlignmentOffset'],
         'unit': {'descriptive_name': 'Angstrom', 'symbol': 'Å'}} })
    z: Union[float, str] = Field(..., description="""A placeholder for any type of data.""", json_schema_extra = { "linkml_meta": {'alias': 'z',
         'any_of': [{'range': 'float'}, {'range': 'FloatFormattedString'}],
         'domain_of': ['TiltSeriesSize',
                       'TomogramSize',
                       'TomogramOffset',
                       'AlignmentSize',
                       'AlignmentOffset'],
         'unit': {'descriptive_name': 'Angstrom', 'symbol': 'Å'}} })

    @field_validator('x')
    def pattern_x(cls, v):
        pattern=re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid x format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid x format: {v}")
        return v

    @field_validator('y')
    def pattern_y(cls, v):
        pattern=re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid y format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid y format: {v}")
        return v

    @field_validator('z')
    def pattern_z(cls, v):
        pattern=re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid z format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid z format: {v}")
        return v


class AlignmentOffset(ConfiguredBaseModel):
    """
    The offset of a alignment in voxels in each dimension relative to the canonical tomogram.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    x: Union[float, str] = Field(0.0, description="""A placeholder for any type of data.""", json_schema_extra = { "linkml_meta": {'alias': 'x',
         'any_of': [{'range': 'float'}, {'range': 'FloatFormattedString'}],
         'domain_of': ['TiltSeriesSize',
                       'TomogramSize',
                       'TomogramOffset',
                       'AlignmentSize',
                       'AlignmentOffset'],
         'ifabsent': 'float(0)',
         'unit': {'descriptive_name': 'Angstrom', 'symbol': 'Å'}} })
    y: Union[float, str] = Field(0.0, description="""A placeholder for any type of data.""", json_schema_extra = { "linkml_meta": {'alias': 'y',
         'any_of': [{'range': 'float'}, {'range': 'FloatFormattedString'}],
         'domain_of': ['TiltSeriesSize',
                       'TomogramSize',
                       'TomogramOffset',
                       'AlignmentSize',
                       'AlignmentOffset'],
         'ifabsent': 'float(0)',
         'unit': {'descriptive_name': 'Angstrom', 'symbol': 'Å'}} })
    z: Union[float, str] = Field(0.0, description="""A placeholder for any type of data.""", json_schema_extra = { "linkml_meta": {'alias': 'z',
         'any_of': [{'range': 'float'}, {'range': 'FloatFormattedString'}],
         'domain_of': ['TiltSeriesSize',
                       'TomogramSize',
                       'TomogramOffset',
                       'AlignmentSize',
                       'AlignmentOffset'],
         'ifabsent': 'float(0)',
         'unit': {'descriptive_name': 'Angstrom', 'symbol': 'Å'}} })

    @field_validator('x')
    def pattern_x(cls, v):
        pattern=re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid x format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid x format: {v}")
        return v

    @field_validator('y')
    def pattern_y(cls, v):
        pattern=re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid y format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid y format: {v}")
        return v

    @field_validator('z')
    def pattern_z(cls, v):
        pattern=re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid z format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid z format: {v}")
        return v


class PerSectionAlignmentParameters(ConfiguredBaseModel):
    """
    Alignment parameters for one section of a tilt series.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    z_index: int = Field(..., description="""z-index of the frame in the tiltseries""", ge=0, json_schema_extra = { "linkml_meta": {'alias': 'z_index',
         'domain_of': ['PerSectionParameter', 'PerSectionAlignmentParameters'],
         'exact_mappings': ['cdp-common:per_section_z_index']} })
    tilt_angle: Optional[float] = Field(None, description="""Tilt angle of the projection in degrees""", json_schema_extra = { "linkml_meta": {'alias': 'tilt_angle',
         'domain_of': ['PerSectionAlignmentParameters'],
         'exact_mappings': ['cdp-common:per_section_alignment_tilt_angle'],
         'unit': {'descriptive_name': 'degrees', 'symbol': '°'}} })
    volume_x_rotation: Optional[float] = Field(None, description="""Additional X rotation of the reconstruction volume in degrees""", json_schema_extra = { "linkml_meta": {'alias': 'volume_x_rotation',
         'domain_of': ['PerSectionAlignmentParameters'],
         'exact_mappings': ['cdp-common:alignment_volume_x_rotation'],
         'unit': {'descriptive_name': 'degrees', 'symbol': '°'}} })
    in_plane_rotation: Optional[conlist(min_length=2, max_length=2, item_type=conlist(min_length=2, max_length=2, item_type=float))] = Field(None, description="""In-plane rotation of the projection as a rotation matrix.""", json_schema_extra = { "linkml_meta": {'alias': 'in_plane_rotation',
         'array': {'dimensions': [{'exact_cardinality': 2}, {'exact_cardinality': 2}],
                   'exact_number_dimensions': 2},
         'domain_of': ['PerSectionAlignmentParameters']} })
    x_offset: Optional[float] = Field(None, description="""In-plane X-shift of the projection in angstrom""", json_schema_extra = { "linkml_meta": {'alias': 'x_offset',
         'domain_of': ['PerSectionAlignmentParameters'],
         'exact_mappings': ['cdp-common:per_section_alignment_x_offset'],
         'unit': {'descriptive_name': 'Angstrom', 'symbol': 'Å'}} })
    y_offset: Optional[float] = Field(None, description="""In-plane Y-shift of the projection in angstrom""", json_schema_extra = { "linkml_meta": {'alias': 'y_offset',
         'domain_of': ['PerSectionAlignmentParameters'],
         'exact_mappings': ['cdp-common:per_section_alignment_y_offset'],
         'unit': {'descriptive_name': 'Angstrom', 'symbol': 'Å'}} })
    beam_tilt: Optional[float] = Field(None, description="""Beam tilt during projection in degrees""", json_schema_extra = { "linkml_meta": {'alias': 'beam_tilt',
         'domain_of': ['PerSectionAlignmentParameters'],
         'exact_mappings': ['cdp-common:per_section_alignment_beam_tilt'],
         'unit': {'descriptive_name': 'degrees', 'symbol': '°'}} })


class Alignment(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    alignment_type: Optional[AlignmentTypeEnum] = Field(None, description="""The type of alignment.""", json_schema_extra = { "linkml_meta": {'alias': 'alignment_type', 'domain_of': ['Alignment']} })
    volume_offset: Optional[AlignmentOffset] = Field(None, description="""The offset of a alignment in voxels in each dimension relative to the canonical tomogram.""", json_schema_extra = { "linkml_meta": {'alias': 'volume_offset', 'domain_of': ['Alignment']} })
    volume_dimension: Optional[AlignmentSize] = Field(None, description="""The size of an alignment in voxels in each dimension.""", json_schema_extra = { "linkml_meta": {'alias': 'volume_dimension', 'domain_of': ['Alignment']} })
    x_rotation_offset: Optional[Union[int, str]] = Field(0, description="""A placeholder for any type of data.""", json_schema_extra = { "linkml_meta": {'alias': 'x_rotation_offset',
         'any_of': [{'range': 'integer'}, {'range': 'IntegerFormattedString'}],
         'domain_of': ['Alignment'],
         'ifabsent': 'int(0)'} })
    tilt_offset: Optional[float] = Field(0.0, description="""The tilt offset relative to the tomogram.""", json_schema_extra = { "linkml_meta": {'alias': 'tilt_offset', 'domain_of': ['Alignment'], 'ifabsent': 'float(0.0)'} })
    affine_transformation_matrix: Optional[conlist(min_length=4, max_length=4, item_type=conlist(min_length=4, max_length=4, item_type=float))] = Field(None, description="""The flip or rotation transformation of this author submitted tomogram is indicated here. The default value if not present, is an identity matrix.""", json_schema_extra = { "linkml_meta": {'alias': 'affine_transformation_matrix',
         'array': {'dimensions': [{'exact_cardinality': 4}, {'exact_cardinality': 4}],
                   'exact_number_dimensions': 2},
         'domain_of': ['Tomogram', 'Alignment']} })
    is_portal_standard: Optional[bool] = Field(False, description="""Whether the alignment is standardized for the portal.""", json_schema_extra = { "linkml_meta": {'alias': 'is_portal_standard',
         'domain_of': ['AnnotationSourceFile',
                       'Alignment',
                       'AnnotationOrientedPointFile',
                       'AnnotationInstanceSegmentationFile',
                       'AnnotationPointFile',
                       'AnnotationSegmentationMaskFile',
                       'AnnotationSemanticSegmentationMaskFile',
                       'AnnotationTriangularMeshFile',
                       'AnnotationTriangularMeshGroupFile'],
         'ifabsent': 'False'} })
    format: AlignmentFormatEnum = Field(..., description="""The format of the alignment.""", json_schema_extra = { "linkml_meta": {'alias': 'format', 'domain_of': ['Alignment', 'Ctf']} })
    method_type: Optional[AlignmentMethodTypeEnum] = Field(None, description="""The alignment method type.""", json_schema_extra = { "linkml_meta": {'alias': 'method_type', 'domain_of': ['Annotation', 'Alignment']} })

    @field_validator('alignment_type')
    def pattern_alignment_type(cls, v):
        pattern=re.compile(r"(^LOCAL$)|(^GLOBAL$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid alignment_type format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid alignment_type format: {v}")
        return v

    @field_validator('x_rotation_offset')
    def pattern_x_rotation_offset(cls, v):
        pattern=re.compile(r"^int[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid x_rotation_offset format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid x_rotation_offset format: {v}")
        return v

    @field_validator('format')
    def pattern_format(cls, v):
        pattern=re.compile(r"(^IMOD$)|(^ARETOMO3$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid format format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid format format: {v}")
        return v

    @field_validator('method_type')
    def pattern_method_type(cls, v):
        pattern=re.compile(r"(^fiducial_based$)|(^patch_tracking$)|(^projection_matching$)|(^undefined$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid method_type format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid method_type format: {v}")
        return v


class Frame(ConfiguredBaseModel):
    """
    A frame entity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    dose_rate: Union[float, str] = Field(..., description="""A placeholder for any type of data.""", json_schema_extra = { "linkml_meta": {'alias': 'dose_rate',
         'any_of': [{'range': 'float'}, {'range': 'FloatFormattedString'}],
         'domain_of': ['Frame']} })
    is_gain_corrected: Optional[bool] = Field(None, description="""Is the frame gain corrected""", json_schema_extra = { "linkml_meta": {'alias': 'is_gain_corrected', 'domain_of': ['Frame']} })

    @field_validator('dose_rate')
    def pattern_dose_rate(cls, v):
        pattern=re.compile(r"^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid dose_rate format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid dose_rate format: {v}")
        return v


class Ctf(ConfiguredBaseModel):
    """
    A ctf entity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata'})

    format: CtfFormatEnum = Field(..., description="""The format of the ctf file.""", json_schema_extra = { "linkml_meta": {'alias': 'format', 'domain_of': ['Alignment', 'Ctf']} })

    @field_validator('format')
    def pattern_format(cls, v):
        pattern=re.compile(r"^CTFFIND$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid format format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid format format: {v}")
        return v


class DateStampedEntityMixin(ConfiguredBaseModel):
    """
    A set of dates at which a data item was deposited, published and last modified.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config', 'mixin': True})

    deposition_date: date = Field(..., description="""The date a data item was received by the cryoET data portal.""", json_schema_extra = { "linkml_meta": {'alias': 'deposition_date',
         'domain_of': ['DateStampedEntityMixin', 'DateStamp'],
         'exact_mappings': ['cdp-common:deposition_date']} })
    release_date: date = Field(..., description="""The date a data item was received by the cryoET data portal.""", json_schema_extra = { "linkml_meta": {'alias': 'release_date',
         'domain_of': ['DateStampedEntityMixin', 'DateStamp'],
         'exact_mappings': ['cdp-common:release_date']} })
    last_modified_date: date = Field(..., description="""The date a piece of data was last modified on the cryoET data portal.""", json_schema_extra = { "linkml_meta": {'alias': 'last_modified_date',
         'domain_of': ['DateStampedEntityMixin', 'DateStamp'],
         'exact_mappings': ['cdp-common:last_modified_date']} })


class DateStamp(DateStampedEntityMixin):
    """
    A set of dates at which a data item was deposited, published and last modified.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata', 'mixins': ['DateStampedEntityMixin']})

    deposition_date: date = Field(..., description="""The date a data item was received by the cryoET data portal.""", json_schema_extra = { "linkml_meta": {'alias': 'deposition_date',
         'domain_of': ['DateStampedEntityMixin', 'DateStamp'],
         'exact_mappings': ['cdp-common:deposition_date']} })
    release_date: date = Field(..., description="""The date a data item was received by the cryoET data portal.""", json_schema_extra = { "linkml_meta": {'alias': 'release_date',
         'domain_of': ['DateStampedEntityMixin', 'DateStamp'],
         'exact_mappings': ['cdp-common:release_date']} })
    last_modified_date: date = Field(..., description="""The date a piece of data was last modified on the cryoET data portal.""", json_schema_extra = { "linkml_meta": {'alias': 'last_modified_date',
         'domain_of': ['DateStampedEntityMixin', 'DateStamp'],
         'exact_mappings': ['cdp-common:last_modified_date']} })


class CrossReferencesMixin(ConfiguredBaseModel):
    """
    A set of cross-references to other databases and publications.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config', 'mixin': True})

    publications: Optional[str] = Field(None, description="""Comma-separated list of DOIs for publications associated with the dataset.""", json_schema_extra = { "linkml_meta": {'alias': 'publications',
         'domain_of': ['CrossReferencesMixin', 'CrossReferences'],
         'recommended': True} })
    related_database_entries: Optional[str] = Field(None, description="""Comma-separated list of related database entries for the dataset.""", json_schema_extra = { "linkml_meta": {'alias': 'related_database_entries',
         'domain_of': ['CrossReferencesMixin', 'CrossReferences'],
         'recommended': True} })
    related_database_links: Optional[str] = Field(None, description="""Comma-separated list of related database links for the dataset.""", json_schema_extra = { "linkml_meta": {'alias': 'related_database_links',
         'domain_of': ['CrossReferencesMixin', 'CrossReferences']} })
    dataset_citations: Optional[str] = Field(None, description="""Comma-separated list of DOIs for publications citing the dataset.""", json_schema_extra = { "linkml_meta": {'alias': 'dataset_citations',
         'domain_of': ['CrossReferencesMixin', 'CrossReferences']} })

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
        pattern=re.compile(r"(^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|PDB-[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|PDB-[0-9a-zA-Z]{4,8}))*$)|(^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|PDB-[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|PDB-[0-9a-zA-Z]{4,8}))*$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid related_database_entries format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid related_database_entries format: {v}")
        return v


class CrossReferences(CrossReferencesMixin):
    """
    A set of cross-references to other databases and publications.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata', 'mixins': ['CrossReferencesMixin']})

    publications: Optional[str] = Field(None, description="""Comma-separated list of DOIs for publications associated with the dataset.""", json_schema_extra = { "linkml_meta": {'alias': 'publications',
         'domain_of': ['CrossReferencesMixin', 'CrossReferences'],
         'recommended': True} })
    related_database_entries: Optional[str] = Field(None, description="""Comma-separated list of related database entries for the dataset.""", json_schema_extra = { "linkml_meta": {'alias': 'related_database_entries',
         'domain_of': ['CrossReferencesMixin', 'CrossReferences'],
         'recommended': True} })
    related_database_links: Optional[str] = Field(None, description="""Comma-separated list of related database links for the dataset.""", json_schema_extra = { "linkml_meta": {'alias': 'related_database_links',
         'domain_of': ['CrossReferencesMixin', 'CrossReferences']} })
    dataset_citations: Optional[str] = Field(None, description="""Comma-separated list of DOIs for publications citing the dataset.""", json_schema_extra = { "linkml_meta": {'alias': 'dataset_citations',
         'domain_of': ['CrossReferencesMixin', 'CrossReferences']} })

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
        pattern=re.compile(r"(^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|PDB-[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|PDB-[0-9a-zA-Z]{4,8}))*$)|(^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|PDB-[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|PDB-[0-9a-zA-Z]{4,8}))*$)")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid related_database_entries format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid related_database_entries format: {v}")
        return v


class AuthorMixin(ConfiguredBaseModel):
    """
    An entity with author data
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config', 'mixin': True})

    name: str = Field(..., description="""The full name of the author.""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['AuthorMixin',
                       'Author',
                       'Assay',
                       'DevelopmentStageDetails',
                       'Disease',
                       'OrganismDetails',
                       'TissueDetails',
                       'CellType',
                       'CellStrain',
                       'CellComponent',
                       'AnnotationObject',
                       'AnnotationTriangularMeshGroupFile'],
         'exact_mappings': ['cdp-common:author_name']} })
    email: Optional[str] = Field(None, description="""The email address of the author.""", json_schema_extra = { "linkml_meta": {'alias': 'email',
         'domain_of': ['AuthorMixin', 'Author'],
         'exact_mappings': ['cdp-common:author_email']} })
    affiliation_name: Optional[str] = Field(None, description="""The name of the author's affiliation.""", json_schema_extra = { "linkml_meta": {'alias': 'affiliation_name',
         'domain_of': ['AuthorMixin', 'Author'],
         'exact_mappings': ['cdp-common:author_affiliation_name']} })
    affiliation_address: Optional[str] = Field(None, description="""The address of the author's affiliation.""", json_schema_extra = { "linkml_meta": {'alias': 'affiliation_address',
         'domain_of': ['AuthorMixin', 'Author'],
         'exact_mappings': ['cdp-common:author_affiliation_address']} })
    affiliation_identifier: Optional[str] = Field(None, description="""A Research Organization Registry (ROR) identifier.""", json_schema_extra = { "linkml_meta": {'alias': 'affiliation_identifier',
         'domain_of': ['AuthorMixin', 'Author'],
         'exact_mappings': ['cdp-common:author_affiliation_identifier'],
         'recommended': True} })
    corresponding_author_status: Optional[bool] = Field(False, description="""Whether the author is a corresponding author.""", json_schema_extra = { "linkml_meta": {'alias': 'corresponding_author_status',
         'domain_of': ['AuthorMixin', 'Author'],
         'exact_mappings': ['cdp-common:author_corresponding_author_status'],
         'ifabsent': 'False'} })
    primary_author_status: Optional[bool] = Field(False, description="""Whether the author is a primary author.""", json_schema_extra = { "linkml_meta": {'alias': 'primary_author_status',
         'domain_of': ['AuthorMixin', 'Author'],
         'exact_mappings': ['cdp-common:author_primary_author_status'],
         'ifabsent': 'False'} })
    kaggle_id: Optional[str] = Field(None, description="""Identifying string for the author's kaggle profile (found after 'kaggle.com/').""", json_schema_extra = { "linkml_meta": {'alias': 'kaggle_id',
         'domain_of': ['AuthorMixin', 'Author'],
         'exact_mappings': ['cdp-common:kaggle_id']} })


class Author(AuthorMixin):
    """
    Author of a scientific data entity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'metadata', 'mixins': ['AuthorMixin']})

    ORCID: Optional[str] = Field(None, description="""The ORCID identifier for the author.""", json_schema_extra = { "linkml_meta": {'alias': 'ORCID',
         'domain_of': ['Author'],
         'exact_mappings': ['cdp-common:author_orcid'],
         'recommended': True} })
    kaggle_id: Optional[str] = Field(None, description="""Identifying string for the author's kaggle profile (found after 'kaggle.com/').""", json_schema_extra = { "linkml_meta": {'alias': 'kaggle_id',
         'domain_of': ['Author', 'AuthorMixin'],
         'exact_mappings': ['cdp-common:kaggle_id']} })
    name: str = Field(..., description="""The full name of the author.""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['AuthorMixin',
                       'Assay',
                       'DevelopmentStageDetails',
                       'Disease',
                       'OrganismDetails',
                       'TissueDetails',
                       'CellType',
                       'CellStrain',
                       'CellComponent',
                       'AnnotationObject',
                       'AnnotationTriangularMeshGroupFile',
                       'Author'],
         'exact_mappings': ['cdp-common:author_name']} })
    email: Optional[str] = Field(None, description="""The email address of the author.""", json_schema_extra = { "linkml_meta": {'alias': 'email',
         'domain_of': ['AuthorMixin', 'Author'],
         'exact_mappings': ['cdp-common:author_email']} })
    affiliation_name: Optional[str] = Field(None, description="""The name of the author's affiliation.""", json_schema_extra = { "linkml_meta": {'alias': 'affiliation_name',
         'domain_of': ['AuthorMixin', 'Author'],
         'exact_mappings': ['cdp-common:author_affiliation_name']} })
    affiliation_address: Optional[str] = Field(None, description="""The address of the author's affiliation.""", json_schema_extra = { "linkml_meta": {'alias': 'affiliation_address',
         'domain_of': ['AuthorMixin', 'Author'],
         'exact_mappings': ['cdp-common:author_affiliation_address']} })
    affiliation_identifier: Optional[str] = Field(None, description="""A Research Organization Registry (ROR) identifier.""", json_schema_extra = { "linkml_meta": {'alias': 'affiliation_identifier',
         'domain_of': ['AuthorMixin', 'Author'],
         'exact_mappings': ['cdp-common:author_affiliation_identifier'],
         'recommended': True} })
    corresponding_author_status: Optional[bool] = Field(False, description="""Whether the author is a corresponding author.""", json_schema_extra = { "linkml_meta": {'alias': 'corresponding_author_status',
         'domain_of': ['AuthorMixin', 'Author'],
         'exact_mappings': ['cdp-common:author_corresponding_author_status'],
         'ifabsent': 'False'} })
    primary_author_status: Optional[bool] = Field(False, description="""Whether the author is a primary author.""", json_schema_extra = { "linkml_meta": {'alias': 'primary_author_status',
         'domain_of': ['AuthorMixin', 'Author'],
         'exact_mappings': ['cdp-common:author_primary_author_status'],
         'ifabsent': 'False'} })

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


class Container(ConfiguredBaseModel):
    """
    Class that models the ingestion config file.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config', 'tree_root': True})

    alignments: Optional[List[AlignmentEntity]] = Field(None, description="""An alignment entity.""", json_schema_extra = { "linkml_meta": {'alias': 'alignments', 'domain_of': ['Container']} })
    annotations: Optional[List[AnnotationEntity]] = Field(None, description="""An annotation entity.""", json_schema_extra = { "linkml_meta": {'alias': 'annotations', 'domain_of': ['Container']} })
    collection_metadata: Optional[List[CollectionMetadataEntity]] = Field(None, description="""A collection_metadata entity.""", json_schema_extra = { "linkml_meta": {'alias': 'collection_metadata', 'domain_of': ['Container']} })
    ctfs: Optional[List[CtfEntity]] = Field(None, description="""A ctf entity.""", json_schema_extra = { "linkml_meta": {'alias': 'ctfs', 'domain_of': ['Container']} })
    dataset_keyphotos: Optional[List[DatasetKeyPhotoEntity]] = Field(None, description="""A dataset key photo entity.""", json_schema_extra = { "linkml_meta": {'alias': 'dataset_keyphotos', 'domain_of': ['Container']} })
    datasets: List[DatasetEntity] = Field(..., description="""A dataset entity.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'datasets', 'domain_of': ['Container']} })
    deposition_keyphotos: Optional[List[DepositionKeyPhotoEntity]] = Field(None, description="""A deposition key photo entity.""", json_schema_extra = { "linkml_meta": {'alias': 'deposition_keyphotos', 'domain_of': ['Container']} })
    depositions: List[DepositionEntity] = Field(..., description="""A deposition entity.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'depositions', 'domain_of': ['Container']} })
    frames: Optional[List[FrameEntity]] = Field(None, description="""A frame entity.""", json_schema_extra = { "linkml_meta": {'alias': 'frames', 'domain_of': ['Container']} })
    gains: Optional[List[GainEntity]] = Field(None, description="""A gain entity.""", json_schema_extra = { "linkml_meta": {'alias': 'gains', 'domain_of': ['Container']} })
    identified_objects: Optional[List[IdentifiedObjectEntity]] = Field(None, description="""An identified object entity.""", json_schema_extra = { "linkml_meta": {'alias': 'identified_objects', 'domain_of': ['Container']} })
    key_images: Optional[List[KeyImageEntity]] = Field(None, description="""A key image entity.""", json_schema_extra = { "linkml_meta": {'alias': 'key_images', 'domain_of': ['Container']} })
    rawtilts: Optional[List[RawTiltEntity]] = Field(None, description="""A raw tilt entity.""", json_schema_extra = { "linkml_meta": {'alias': 'rawtilts', 'domain_of': ['Container']} })
    runs: List[RunEntity] = Field(..., description="""A run entity.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'runs', 'domain_of': ['Container']} })
    standardization_config: StandardizationConfig = Field(..., description="""A standardization configuration.""", json_schema_extra = { "linkml_meta": {'alias': 'standardization_config', 'domain_of': ['Container']} })
    tiltseries: Optional[List[TiltSeriesEntity]] = Field(None, description="""A tilt series entity.""", json_schema_extra = { "linkml_meta": {'alias': 'tiltseries', 'domain_of': ['Container']} })
    tomograms: Optional[List[TomogramEntity]] = Field(None, description="""A tomogram entity.""", json_schema_extra = { "linkml_meta": {'alias': 'tomograms', 'domain_of': ['Container']} })
    version: str = Field(..., description="""The version of the ingestion config.""", json_schema_extra = { "linkml_meta": {'alias': 'version', 'domain_of': ['Annotation', 'Container']} })
    voxel_spacings: List[VoxelSpacingEntity] = Field(..., description="""A voxel spacing entity.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'voxel_spacings', 'domain_of': ['Container']} })


class GeneralGlob(ConfiguredBaseModel):
    """
    An abstracted glob class for destination and source globs.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True, 'from_schema': 'cdp-ingestion-config'})

    list_glob: str = Field(..., description="""The glob for the file.""", json_schema_extra = { "linkml_meta": {'alias': 'list_glob',
         'domain_of': ['GeneralGlob',
                       'TomogramHeader',
                       'DestinationGlob',
                       'SourceGlob']} })
    match_regex: Optional[str] = Field(".*", description="""The regex for the file.""", json_schema_extra = { "linkml_meta": {'alias': 'match_regex',
         'domain_of': ['GeneralGlob',
                       'TomogramHeader',
                       'DestinationGlob',
                       'SourceGlob'],
         'ifabsent': 'string(.*)'} })
    name_regex: Optional[str] = Field("(.*)", description="""The regex for the name of the file.""", json_schema_extra = { "linkml_meta": {'alias': 'name_regex',
         'domain_of': ['GeneralGlob', 'DestinationGlob', 'SourceGlob'],
         'ifabsent': 'string((.*))'} })


class DestinationGlob(GeneralGlob):
    """
    A glob class for finding files in the output / destination directory.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    list_glob: str = Field(..., description="""The glob for the file.""", json_schema_extra = { "linkml_meta": {'alias': 'list_glob',
         'domain_of': ['GeneralGlob',
                       'TomogramHeader',
                       'DestinationGlob',
                       'SourceGlob']} })
    match_regex: Optional[str] = Field(".*", description="""The regex for the file.""", json_schema_extra = { "linkml_meta": {'alias': 'match_regex',
         'domain_of': ['GeneralGlob',
                       'TomogramHeader',
                       'DestinationGlob',
                       'SourceGlob'],
         'ifabsent': 'string(.*)'} })
    name_regex: Optional[str] = Field("(.*)", description="""The regex for the name of the file.""", json_schema_extra = { "linkml_meta": {'alias': 'name_regex',
         'domain_of': ['GeneralGlob', 'DestinationGlob', 'SourceGlob'],
         'ifabsent': 'string((.*))'} })


class SourceGlob(GeneralGlob):
    """
    A glob class for finding files in the source directory.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    list_glob: str = Field(..., description="""The glob for the file.""", json_schema_extra = { "linkml_meta": {'alias': 'list_glob',
         'domain_of': ['GeneralGlob',
                       'TomogramHeader',
                       'DestinationGlob',
                       'SourceGlob']} })
    match_regex: Optional[str] = Field(".*", description="""The regex for the file.""", json_schema_extra = { "linkml_meta": {'alias': 'match_regex',
         'domain_of': ['GeneralGlob',
                       'TomogramHeader',
                       'DestinationGlob',
                       'SourceGlob'],
         'ifabsent': 'string(.*)'} })
    name_regex: Optional[str] = Field("(.*)", description="""The regex for the name of the file.""", json_schema_extra = { "linkml_meta": {'alias': 'name_regex',
         'domain_of': ['GeneralGlob', 'DestinationGlob', 'SourceGlob'],
         'ifabsent': 'string((.*))'} })


class SourceMultiGlob(ConfiguredBaseModel):
    """
    A glob class for finding files in the source directory (with multiple globs).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    list_globs: List[str] = Field(..., description="""The globs for the file.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'list_globs', 'domain_of': ['SourceMultiGlob']} })


class DefaultSource(ConfiguredBaseModel):
    """
    A default source class that all source classes inherit from.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    exclude: Optional[List[str]] = Field(None, description="""Exclude files from the source that match (regexes).""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class StandardSource(DefaultSource):
    """
    A generalized source class with glob finders. Inherited by a majority of source classes.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    destination_glob: Optional[DestinationGlob] = Field(None, description="""A glob class for finding files in the output / destination directory.""", json_schema_extra = { "linkml_meta": {'alias': 'destination_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_glob: Optional[SourceGlob] = Field(None, description="""A glob class for finding files in the source directory.""", json_schema_extra = { "linkml_meta": {'alias': 'source_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_multi_glob: Optional[SourceMultiGlob] = Field(None, description="""A glob class for finding files in the source directory (with multiple globs).""", json_schema_extra = { "linkml_meta": {'alias': 'source_multi_glob',
         'domain_of': ['StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    literal: Optional[StandardLiteral] = Field(None, description="""A literal class with a value attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'literal',
         'domain_of': ['StandardSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DepositionSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    exclude: Optional[List[str]] = Field(None, description="""Exclude files from the source that match (regexes).""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class StandardLiteral(ConfiguredBaseModel):
    """
    A literal class with a value attribute.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    value: List[Any] = Field(..., description="""A placeholder for any type of data.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'value',
         'domain_of': ['StandardLiteral',
                       'KeyPhotoLiteral',
                       'DestinationMetadataFilterKeyPair',
                       'VoxelSpacingLiteral']} })


class KeyPhotoLiteral(ConfiguredBaseModel):
    """
    A literal for a key photo.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    value: PicturePath = Field(..., description="""A set of paths to representative images of a piece of data.""", json_schema_extra = { "linkml_meta": {'alias': 'value',
         'domain_of': ['StandardLiteral',
                       'KeyPhotoLiteral',
                       'DestinationMetadataFilterKeyPair',
                       'VoxelSpacingLiteral']} })


class DestinationMetadataFilterKeyPair(ConfiguredBaseModel):
    """
    A key value pair for a destination metadata filter.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    key: List[str] = Field(..., description="""The path of the key for the filter in the metadata file.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'key', 'domain_of': ['DestinationMetadataFilterKeyPair']} })
    value: Any = Field(..., description="""A placeholder for any type of data.""", json_schema_extra = { "linkml_meta": {'alias': 'value',
         'domain_of': ['StandardLiteral',
                       'KeyPhotoLiteral',
                       'DestinationMetadataFilterKeyPair',
                       'VoxelSpacingLiteral']} })


class DestinationMetadataFilter(ConfiguredBaseModel):
    """
    A finder class for to filter destination metadata by certain criteria.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    filters: List[DestinationMetadataFilterKeyPair] = Field(..., description="""A key value pair for a destination metadata filter.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'filters', 'domain_of': ['DestinationMetadataFilter']} })


class ReferencedSource(StandardSource):
    """
    A Inherited by a majority of source classes.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    destination_filter: Optional[DestinationMetadataFilter] = Field(None, description="""A finder class for to filter destination metadata by certain criteria.""", json_schema_extra = { "linkml_meta": {'alias': 'destination_filter',
         'domain_of': ['ReferencedSource', 'TiltSeriesSource', 'TomogramSource']} })
    destination_glob: Optional[DestinationGlob] = Field(None, description="""A glob class for finding files in the output / destination directory.""", json_schema_extra = { "linkml_meta": {'alias': 'destination_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_glob: Optional[SourceGlob] = Field(None, description="""A glob class for finding files in the source directory.""", json_schema_extra = { "linkml_meta": {'alias': 'source_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_multi_glob: Optional[SourceMultiGlob] = Field(None, description="""A glob class for finding files in the source directory (with multiple globs).""", json_schema_extra = { "linkml_meta": {'alias': 'source_multi_glob',
         'domain_of': ['StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    literal: Optional[StandardLiteral] = Field(None, description="""A literal class with a value attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'literal',
         'domain_of': ['StandardSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DepositionSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    exclude: Optional[List[str]] = Field(None, description="""Exclude files from the source that match (regexes).""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class AlignmentEntity(ConfiguredBaseModel):
    """
    An alignment entity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    metadata: Optional[Alignment] = Field(None, description="""The metadata for the alignment.""", json_schema_extra = { "linkml_meta": {'alias': 'metadata',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DepositionEntity',
                       'FrameEntity',
                       'IdentifiedObjectEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity']} })
    sources: Optional[List[AlignmentSource]] = Field(None, description="""An alignment source.""", json_schema_extra = { "linkml_meta": {'alias': 'sources',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CollectionMetadataEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DatasetKeyPhotoEntity',
                       'DepositionEntity',
                       'DepositionKeyPhotoEntity',
                       'FrameEntity',
                       'GainEntity',
                       'IdentifiedObjectEntity',
                       'KeyImageEntity',
                       'RawTiltEntity',
                       'RunEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity',
                       'VoxelSpacingEntity']} })


class AlignmentSource(StandardSource):
    """
    An alignment source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    parent_filters: Optional[AlignmentParentFilters] = Field(None, description="""Types of parent filters for an alignment source.""", json_schema_extra = { "linkml_meta": {'alias': 'parent_filters',
         'domain_of': ['AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })
    destination_glob: Optional[DestinationGlob] = Field(None, description="""A glob class for finding files in the output / destination directory.""", json_schema_extra = { "linkml_meta": {'alias': 'destination_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_glob: Optional[SourceGlob] = Field(None, description="""A glob class for finding files in the source directory.""", json_schema_extra = { "linkml_meta": {'alias': 'source_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_multi_glob: Optional[SourceMultiGlob] = Field(None, description="""A glob class for finding files in the source directory (with multiple globs).""", json_schema_extra = { "linkml_meta": {'alias': 'source_multi_glob',
         'domain_of': ['StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    literal: Optional[StandardLiteral] = Field(None, description="""A literal class with a value attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'literal',
         'domain_of': ['StandardSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DepositionSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    exclude: Optional[List[str]] = Field(None, description="""Exclude files from the source that match (regexes).""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class AlignmentParentFilters(ConfiguredBaseModel):
    """
    Types of parent filters for an alignment source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    include: Optional[AlignmentParent] = Field(None, description="""A filter for a parent class of an alignment source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'include',
         'domain_of': ['AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters']} })
    exclude: Optional[AlignmentParent] = Field(None, description="""A filter for a parent class of an alignment source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class AlignmentParent(ConfiguredBaseModel):
    """
    A filter for a parent class of an alignment source. For a given attribute, it can only be used if the current class is a subclass of the attribute.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    dataset: Optional[List[str]] = Field(None, description="""Include or exclude datasets for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'dataset',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    deposition: Optional[List[str]] = Field(None, description="""Include or exclude depositions for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'deposition',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'DatasetParent',
                       'DatasetKeyPhotoParent',
                       'DepositionKeyPhotoParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    run: Optional[List[str]] = Field(None, description="""Include or exclude runs for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'run',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })


class AnnotationEntity(ConfiguredBaseModel):
    """
    An annotation entity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    metadata: Annotation = Field(..., description="""Metadata describing an annotation.""", json_schema_extra = { "linkml_meta": {'alias': 'metadata',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DepositionEntity',
                       'FrameEntity',
                       'IdentifiedObjectEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity']} })
    sources: List[AnnotationSource] = Field(..., description="""An annotation source.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'sources',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CollectionMetadataEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DatasetKeyPhotoEntity',
                       'DepositionEntity',
                       'DepositionKeyPhotoEntity',
                       'FrameEntity',
                       'GainEntity',
                       'IdentifiedObjectEntity',
                       'KeyImageEntity',
                       'RawTiltEntity',
                       'RunEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity',
                       'VoxelSpacingEntity']} })


class AnnotationSource(DefaultSource):
    """
    An annotation source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    InstanceSegmentation: Optional[AnnotationInstanceSegmentationFile] = Field(None, description="""File and sourcing data for an instance segmentation annotation. Annotation that identifies individual instances of object shapes.""", json_schema_extra = { "linkml_meta": {'alias': 'InstanceSegmentation', 'domain_of': ['AnnotationSource']} })
    OrientedPoint: Optional[AnnotationOrientedPointFile] = Field(None, description="""File and sourcing data for an oriented point annotation. Annotation that identifies points along with orientation in the volume.""", json_schema_extra = { "linkml_meta": {'alias': 'OrientedPoint', 'domain_of': ['AnnotationSource']} })
    Point: Optional[AnnotationPointFile] = Field(None, description="""File and sourcing data for a point annotation. Annotation that identifies points in the volume.""", json_schema_extra = { "linkml_meta": {'alias': 'Point', 'domain_of': ['AnnotationSource']} })
    SegmentationMask: Optional[AnnotationSegmentationMaskFile] = Field(None, description="""File and sourcing data for a segmentation mask annotation. Annotation that identifies an object.""", json_schema_extra = { "linkml_meta": {'alias': 'SegmentationMask', 'domain_of': ['AnnotationSource']} })
    SemanticSegmentationMask: Optional[AnnotationSemanticSegmentationMaskFile] = Field(None, description="""File and sourcing data for a semantic segmentation mask annotation. Annotation that identifies classes of objects.""", json_schema_extra = { "linkml_meta": {'alias': 'SemanticSegmentationMask', 'domain_of': ['AnnotationSource']} })
    TriangularMesh: Optional[AnnotationTriangularMeshFile] = Field(None, description="""File and sourcing data for a triangular mesh annotation. Annotation that identifies an object.""", json_schema_extra = { "linkml_meta": {'alias': 'TriangularMesh', 'domain_of': ['AnnotationSource']} })
    TriangularMeshGroup: Optional[AnnotationTriangularMeshGroupFile] = Field(None, description="""File and sourcing data containing one or more triangular mesh annotations.""", json_schema_extra = { "linkml_meta": {'alias': 'TriangularMeshGroup', 'domain_of': ['AnnotationSource']} })
    parent_filters: Optional[AnnotationParentFilters] = Field(None, description="""Filters for the parent of an annotation source.""", json_schema_extra = { "linkml_meta": {'alias': 'parent_filters',
         'domain_of': ['AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })
    exclude: Optional[List[str]] = Field(None, description="""Exclude files from the source that match (regexes).""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class AnnotationParentFilters(ConfiguredBaseModel):
    """
    Filters for the parent of an annotation source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    include: Optional[AnnotationParent] = Field(None, description="""A filter for a parent class of an annotation source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'include',
         'domain_of': ['AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters']} })
    exclude: Optional[AnnotationParent] = Field(None, description="""A filter for a parent class of an annotation source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class AnnotationParent(ConfiguredBaseModel):
    """
    A filter for a parent class of an annotation source. For a given attribute, it can only be used if the current class is a subclass of the attribute.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    dataset: Optional[List[str]] = Field(None, description="""Include or exclude datasets for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'dataset',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    deposition: Optional[List[str]] = Field(None, description="""Include or exclude depositions for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'deposition',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'DatasetParent',
                       'DatasetKeyPhotoParent',
                       'DepositionKeyPhotoParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    run: Optional[List[str]] = Field(None, description="""Include or exclude runs for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'run',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    voxel_spacing: Optional[List[str]] = Field(None, description="""Include or exclude voxel spacings for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'voxel_spacing',
         'domain_of': ['Tomogram',
                       'AnnotationParent',
                       'KeyImageParent',
                       'TomogramParent']} })


class CollectionMetadataEntity(ConfiguredBaseModel):
    """
    A collection_metadata entity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    sources: List[CollectionMetadataSource] = Field(..., description="""A collection_metadata source.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'sources',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CollectionMetadataEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DatasetKeyPhotoEntity',
                       'DepositionEntity',
                       'DepositionKeyPhotoEntity',
                       'FrameEntity',
                       'GainEntity',
                       'IdentifiedObjectEntity',
                       'KeyImageEntity',
                       'RawTiltEntity',
                       'RunEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity',
                       'VoxelSpacingEntity']} })


class CollectionMetadataSource(StandardSource):
    """
    A collection_metadata source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    parent_filters: Optional[CollectionMetadataParentFilters] = Field(None, description="""Types of parent filters for a collection_metadata source.""", json_schema_extra = { "linkml_meta": {'alias': 'parent_filters',
         'domain_of': ['AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })
    destination_glob: Optional[DestinationGlob] = Field(None, description="""A glob class for finding files in the output / destination directory.""", json_schema_extra = { "linkml_meta": {'alias': 'destination_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_glob: Optional[SourceGlob] = Field(None, description="""A glob class for finding files in the source directory.""", json_schema_extra = { "linkml_meta": {'alias': 'source_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_multi_glob: Optional[SourceMultiGlob] = Field(None, description="""A glob class for finding files in the source directory (with multiple globs).""", json_schema_extra = { "linkml_meta": {'alias': 'source_multi_glob',
         'domain_of': ['StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    literal: Optional[StandardLiteral] = Field(None, description="""A literal class with a value attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'literal',
         'domain_of': ['StandardSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DepositionSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    exclude: Optional[List[str]] = Field(None, description="""Exclude files from the source that match (regexes).""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class CollectionMetadataParentFilters(ConfiguredBaseModel):
    """
    Types of parent filters for a collection_metadata source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    include: Optional[CollectionMetadataParent] = Field(None, description="""A filter for a parent class of a collection_metadata source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'include',
         'domain_of': ['AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters']} })
    exclude: Optional[CollectionMetadataParent] = Field(None, description="""A filter for a parent class of a collection_metadata source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class CollectionMetadataParent(ConfiguredBaseModel):
    """
    A filter for a parent class of a collection_metadata source. For a given attribute, it can only be used if the current class is a subclass of the attribute.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    dataset: Optional[List[str]] = Field(None, description="""Include or exclude datasets for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'dataset',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    deposition: Optional[List[str]] = Field(None, description="""Include or exclude depositions for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'deposition',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'DatasetParent',
                       'DatasetKeyPhotoParent',
                       'DepositionKeyPhotoParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    run: Optional[List[str]] = Field(None, description="""Include or exclude runs for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'run',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })


class CtfEntity(ConfiguredBaseModel):
    """
    A ctf entity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    metadata: Optional[Ctf] = Field(None, description="""A ctf entity.""", json_schema_extra = { "linkml_meta": {'alias': 'metadata',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DepositionEntity',
                       'FrameEntity',
                       'IdentifiedObjectEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity']} })
    sources: List[CtfSource] = Field(..., description="""A ctf source.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'sources',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CollectionMetadataEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DatasetKeyPhotoEntity',
                       'DepositionEntity',
                       'DepositionKeyPhotoEntity',
                       'FrameEntity',
                       'GainEntity',
                       'IdentifiedObjectEntity',
                       'KeyImageEntity',
                       'RawTiltEntity',
                       'RunEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity',
                       'VoxelSpacingEntity']} })


class CtfSource(StandardSource):
    """
    A ctf source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    parent_filters: Optional[CtfParentFilters] = Field(None, description="""Types of parent filters for a ctf source.""", json_schema_extra = { "linkml_meta": {'alias': 'parent_filters',
         'domain_of': ['AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })
    destination_glob: Optional[DestinationGlob] = Field(None, description="""A glob class for finding files in the output / destination directory.""", json_schema_extra = { "linkml_meta": {'alias': 'destination_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_glob: Optional[SourceGlob] = Field(None, description="""A glob class for finding files in the source directory.""", json_schema_extra = { "linkml_meta": {'alias': 'source_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_multi_glob: Optional[SourceMultiGlob] = Field(None, description="""A glob class for finding files in the source directory (with multiple globs).""", json_schema_extra = { "linkml_meta": {'alias': 'source_multi_glob',
         'domain_of': ['StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    literal: Optional[StandardLiteral] = Field(None, description="""A literal class with a value attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'literal',
         'domain_of': ['StandardSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DepositionSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    exclude: Optional[List[str]] = Field(None, description="""Exclude files from the source that match (regexes).""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class CtfParentFilters(ConfiguredBaseModel):
    """
    Types of parent filters for a ctf source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    include: Optional[CtfParent] = Field(None, description="""A filter for a parent class of a ctf source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'include',
         'domain_of': ['AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters']} })
    exclude: Optional[CtfParent] = Field(None, description="""A filter for a parent class of a ctf source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class CtfParent(ConfiguredBaseModel):
    """
    A filter for a parent class of a ctf source. For a given attribute, it can only be used if the current class is a subclass of the attribute.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    dataset: Optional[List[str]] = Field(None, description="""Include or exclude datasets for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'dataset',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    deposition: Optional[List[str]] = Field(None, description="""Include or exclude depositions for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'deposition',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'DatasetParent',
                       'DatasetKeyPhotoParent',
                       'DepositionKeyPhotoParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    run: Optional[List[str]] = Field(None, description="""Include or exclude runs for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'run',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })


class DatasetEntity(ConfiguredBaseModel):
    """
    A dataset entity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    metadata: Optional[Dataset] = Field(None, description="""High-level description of a cryoET dataset.""", json_schema_extra = { "linkml_meta": {'alias': 'metadata',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DepositionEntity',
                       'FrameEntity',
                       'IdentifiedObjectEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity']} })
    sources: List[DatasetSource] = Field(..., description="""A dataset source.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'sources',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CollectionMetadataEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DatasetKeyPhotoEntity',
                       'DepositionEntity',
                       'DepositionKeyPhotoEntity',
                       'FrameEntity',
                       'GainEntity',
                       'IdentifiedObjectEntity',
                       'KeyImageEntity',
                       'RawTiltEntity',
                       'RunEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity',
                       'VoxelSpacingEntity']} })


class DatasetSource(StandardSource):
    """
    A dataset source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    parent_filters: Optional[DatasetParentFilters] = Field(None, description="""Types of parent filters for a dataset source.""", json_schema_extra = { "linkml_meta": {'alias': 'parent_filters',
         'domain_of': ['AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })
    destination_glob: Optional[DestinationGlob] = Field(None, description="""A glob class for finding files in the output / destination directory.""", json_schema_extra = { "linkml_meta": {'alias': 'destination_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_glob: Optional[SourceGlob] = Field(None, description="""A glob class for finding files in the source directory.""", json_schema_extra = { "linkml_meta": {'alias': 'source_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_multi_glob: Optional[SourceMultiGlob] = Field(None, description="""A glob class for finding files in the source directory (with multiple globs).""", json_schema_extra = { "linkml_meta": {'alias': 'source_multi_glob',
         'domain_of': ['StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    literal: Optional[StandardLiteral] = Field(None, description="""A literal class with a value attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'literal',
         'domain_of': ['StandardSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DepositionSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    exclude: Optional[List[str]] = Field(None, description="""Exclude files from the source that match (regexes).""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class DatasetParentFilters(ConfiguredBaseModel):
    """
    Types of parent filters for a dataset source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    include: Optional[DatasetParent] = Field(None, description="""A filter for a parent class of a dataset source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'include',
         'domain_of': ['AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters']} })
    exclude: Optional[DatasetParent] = Field(None, description="""A filter for a parent class of a dataset source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class DatasetParent(ConfiguredBaseModel):
    """
    A filter for a parent class of a dataset source. For a given attribute, it can only be used if the current class is a subclass of the attribute.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    deposition: Optional[List[str]] = Field(None, description="""Include or exclude depositions for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'deposition',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'DatasetParent',
                       'DatasetKeyPhotoParent',
                       'DepositionKeyPhotoParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })


class DatasetKeyPhotoEntity(ConfiguredBaseModel):
    """
    A dataset key photo entity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    sources: List[DatasetKeyPhotoSource] = Field(..., description="""A key photo source.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'sources',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CollectionMetadataEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DatasetKeyPhotoEntity',
                       'DepositionEntity',
                       'DepositionKeyPhotoEntity',
                       'FrameEntity',
                       'GainEntity',
                       'IdentifiedObjectEntity',
                       'KeyImageEntity',
                       'RawTiltEntity',
                       'RunEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity',
                       'VoxelSpacingEntity']} })


class DatasetKeyPhotoSource(StandardSource):
    """
    A key photo source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    literal: Optional[KeyPhotoLiteral] = Field(None, description="""A literal for a key photo.""", json_schema_extra = { "linkml_meta": {'alias': 'literal',
         'domain_of': ['StandardSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DepositionSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    parent_filters: Optional[DatasetKeyPhotoParentFilters] = Field(None, description="""Types of parent filters for a key photo source.""", json_schema_extra = { "linkml_meta": {'alias': 'parent_filters',
         'domain_of': ['AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })
    destination_glob: Optional[DestinationGlob] = Field(None, description="""A glob class for finding files in the output / destination directory.""", json_schema_extra = { "linkml_meta": {'alias': 'destination_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_glob: Optional[SourceGlob] = Field(None, description="""A glob class for finding files in the source directory.""", json_schema_extra = { "linkml_meta": {'alias': 'source_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_multi_glob: Optional[SourceMultiGlob] = Field(None, description="""A glob class for finding files in the source directory (with multiple globs).""", json_schema_extra = { "linkml_meta": {'alias': 'source_multi_glob',
         'domain_of': ['StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    exclude: Optional[List[str]] = Field(None, description="""Exclude files from the source that match (regexes).""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class DatasetKeyPhotoParentFilters(ConfiguredBaseModel):
    """
    Types of parent filters for a key photo source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    include: Optional[DatasetKeyPhotoParent] = Field(None, description="""A filter for a parent class of a key photo source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'include',
         'domain_of': ['AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters']} })
    exclude: Optional[DatasetKeyPhotoParent] = Field(None, description="""A filter for a parent class of a key photo source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class DatasetKeyPhotoParent(ConfiguredBaseModel):
    """
    A filter for a parent class of a key photo source. For a given attribute, it can only be used if the current class is a subclass of the attribute.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    deposition: Optional[List[str]] = Field(None, description="""Include or exclude depositions for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'deposition',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'DatasetParent',
                       'DatasetKeyPhotoParent',
                       'DepositionKeyPhotoParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })


class DepositionEntity(ConfiguredBaseModel):
    """
    A deposition entity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    metadata: Optional[Deposition] = Field(None, description="""Metadata describing a deposition.""", json_schema_extra = { "linkml_meta": {'alias': 'metadata',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DepositionEntity',
                       'FrameEntity',
                       'IdentifiedObjectEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity']} })
    sources: List[DepositionSource] = Field(..., description="""A deposition source.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'sources',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CollectionMetadataEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DatasetKeyPhotoEntity',
                       'DepositionEntity',
                       'DepositionKeyPhotoEntity',
                       'FrameEntity',
                       'GainEntity',
                       'IdentifiedObjectEntity',
                       'KeyImageEntity',
                       'RawTiltEntity',
                       'RunEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity',
                       'VoxelSpacingEntity']} })


class DepositionSource(StandardSource):
    """
    A deposition source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    destination_glob: Optional[DestinationGlob] = Field(None, description="""A glob class for finding files in the output / destination directory.""", json_schema_extra = { "linkml_meta": {'alias': 'destination_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_glob: Optional[SourceGlob] = Field(None, description="""A glob class for finding files in the source directory.""", json_schema_extra = { "linkml_meta": {'alias': 'source_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_multi_glob: Optional[SourceMultiGlob] = Field(None, description="""A glob class for finding files in the source directory (with multiple globs).""", json_schema_extra = { "linkml_meta": {'alias': 'source_multi_glob',
         'domain_of': ['StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    literal: Optional[StandardLiteral] = Field(None, description="""A literal class with a value attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'literal',
         'domain_of': ['StandardSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DepositionSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    exclude: Optional[List[str]] = Field(None, description="""Exclude files from the source that match (regexes).""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class DepositionKeyPhotoEntity(ConfiguredBaseModel):
    """
    A deposition key photo entity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    sources: List[DepositionKeyPhotoSource] = Field(..., description="""A key photo source.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'sources',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CollectionMetadataEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DatasetKeyPhotoEntity',
                       'DepositionEntity',
                       'DepositionKeyPhotoEntity',
                       'FrameEntity',
                       'GainEntity',
                       'IdentifiedObjectEntity',
                       'KeyImageEntity',
                       'RawTiltEntity',
                       'RunEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity',
                       'VoxelSpacingEntity']} })


class DepositionKeyPhotoSource(StandardSource):
    """
    A key photo source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    literal: Optional[KeyPhotoLiteral] = Field(None, description="""A literal for a key photo.""", json_schema_extra = { "linkml_meta": {'alias': 'literal',
         'domain_of': ['StandardSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DepositionSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    parent_filters: Optional[DepositionKeyPhotoParentFilters] = Field(None, description="""Types of parent filters for a key photo source.""", json_schema_extra = { "linkml_meta": {'alias': 'parent_filters',
         'domain_of': ['AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })
    destination_glob: Optional[DestinationGlob] = Field(None, description="""A glob class for finding files in the output / destination directory.""", json_schema_extra = { "linkml_meta": {'alias': 'destination_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_glob: Optional[SourceGlob] = Field(None, description="""A glob class for finding files in the source directory.""", json_schema_extra = { "linkml_meta": {'alias': 'source_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_multi_glob: Optional[SourceMultiGlob] = Field(None, description="""A glob class for finding files in the source directory (with multiple globs).""", json_schema_extra = { "linkml_meta": {'alias': 'source_multi_glob',
         'domain_of': ['StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    exclude: Optional[List[str]] = Field(None, description="""Exclude files from the source that match (regexes).""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class DepositionKeyPhotoParentFilters(ConfiguredBaseModel):
    """
    Types of parent filters for a key photo source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    include: Optional[DepositionKeyPhotoParent] = Field(None, description="""A filter for a parent class of a key photo source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'include',
         'domain_of': ['AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters']} })
    exclude: Optional[DepositionKeyPhotoParent] = Field(None, description="""A filter for a parent class of a key photo source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class DepositionKeyPhotoParent(ConfiguredBaseModel):
    """
    A filter for a parent class of a key photo source. For a given attribute, it can only be used if the current class is a subclass of the attribute.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    deposition: Optional[List[str]] = Field(None, description="""Include or exclude depositions for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'deposition',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'DatasetParent',
                       'DatasetKeyPhotoParent',
                       'DepositionKeyPhotoParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })


class FrameEntity(ConfiguredBaseModel):
    """
    A frame entity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    sources: Optional[List[FrameSource]] = Field(None, description="""A frame source.""", json_schema_extra = { "linkml_meta": {'alias': 'sources',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CollectionMetadataEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DatasetKeyPhotoEntity',
                       'DepositionEntity',
                       'DepositionKeyPhotoEntity',
                       'FrameEntity',
                       'GainEntity',
                       'IdentifiedObjectEntity',
                       'KeyImageEntity',
                       'RawTiltEntity',
                       'RunEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity',
                       'VoxelSpacingEntity']} })
    metadata: Optional[Frame] = Field(None, description="""A frame entity.""", json_schema_extra = { "linkml_meta": {'alias': 'metadata',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DepositionEntity',
                       'FrameEntity',
                       'IdentifiedObjectEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity']} })


class FrameSource(StandardSource):
    """
    A frame source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    parent_filters: Optional[FrameParentFilters] = Field(None, description="""Types of parent filters for a frame source.""", json_schema_extra = { "linkml_meta": {'alias': 'parent_filters',
         'domain_of': ['AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })
    destination_glob: Optional[DestinationGlob] = Field(None, description="""A glob class for finding files in the output / destination directory.""", json_schema_extra = { "linkml_meta": {'alias': 'destination_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_glob: Optional[SourceGlob] = Field(None, description="""A glob class for finding files in the source directory.""", json_schema_extra = { "linkml_meta": {'alias': 'source_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_multi_glob: Optional[SourceMultiGlob] = Field(None, description="""A glob class for finding files in the source directory (with multiple globs).""", json_schema_extra = { "linkml_meta": {'alias': 'source_multi_glob',
         'domain_of': ['StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    literal: Optional[StandardLiteral] = Field(None, description="""A literal class with a value attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'literal',
         'domain_of': ['StandardSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DepositionSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    exclude: Optional[List[str]] = Field(None, description="""Exclude files from the source that match (regexes).""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class FrameParentFilters(ConfiguredBaseModel):
    """
    Types of parent filters for a frame source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    include: Optional[FrameParent] = Field(None, description="""A filter for a parent class of a frame source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'include',
         'domain_of': ['AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters']} })
    exclude: Optional[FrameParent] = Field(None, description="""A filter for a parent class of a frame source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class FrameParent(ConfiguredBaseModel):
    """
    A filter for a parent class of a frame source. For a given attribute, it can only be used if the current class is a subclass of the attribute.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    dataset: Optional[List[str]] = Field(None, description="""Include or exclude datasets for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'dataset',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    deposition: Optional[List[str]] = Field(None, description="""Include or exclude depositions for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'deposition',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'DatasetParent',
                       'DatasetKeyPhotoParent',
                       'DepositionKeyPhotoParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    run: Optional[List[str]] = Field(None, description="""Include or exclude runs for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'run',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })


class GainEntity(ConfiguredBaseModel):
    """
    A gain entity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    sources: List[GainSource] = Field(..., description="""A gain source.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'sources',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CollectionMetadataEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DatasetKeyPhotoEntity',
                       'DepositionEntity',
                       'DepositionKeyPhotoEntity',
                       'FrameEntity',
                       'GainEntity',
                       'IdentifiedObjectEntity',
                       'KeyImageEntity',
                       'RawTiltEntity',
                       'RunEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity',
                       'VoxelSpacingEntity']} })


class GainSource(StandardSource):
    """
    A gain source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    parent_filters: Optional[GainParentFilters] = Field(None, description="""Types of parent filters for a gain source.""", json_schema_extra = { "linkml_meta": {'alias': 'parent_filters',
         'domain_of': ['AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })
    destination_glob: Optional[DestinationGlob] = Field(None, description="""A glob class for finding files in the output / destination directory.""", json_schema_extra = { "linkml_meta": {'alias': 'destination_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_glob: Optional[SourceGlob] = Field(None, description="""A glob class for finding files in the source directory.""", json_schema_extra = { "linkml_meta": {'alias': 'source_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_multi_glob: Optional[SourceMultiGlob] = Field(None, description="""A glob class for finding files in the source directory (with multiple globs).""", json_schema_extra = { "linkml_meta": {'alias': 'source_multi_glob',
         'domain_of': ['StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    literal: Optional[StandardLiteral] = Field(None, description="""A literal class with a value attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'literal',
         'domain_of': ['StandardSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DepositionSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    exclude: Optional[List[str]] = Field(None, description="""Exclude files from the source that match (regexes).""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class GainParentFilters(ConfiguredBaseModel):
    """
    Types of parent filters for a gain source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    include: Optional[GainParent] = Field(None, description="""A filter for a parent class of a gain source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'include',
         'domain_of': ['AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters']} })
    exclude: Optional[GainParent] = Field(None, description="""A filter for a parent class of a gain source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class GainParent(ConfiguredBaseModel):
    """
    A filter for a parent class of a gain source. For a given attribute, it can only be used if the current class is a subclass of the attribute.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    dataset: Optional[List[str]] = Field(None, description="""Include or exclude datasets for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'dataset',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    deposition: Optional[List[str]] = Field(None, description="""Include or exclude depositions for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'deposition',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'DatasetParent',
                       'DatasetKeyPhotoParent',
                       'DepositionKeyPhotoParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    run: Optional[List[str]] = Field(None, description="""Include or exclude runs for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'run',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })


class IdentifiedObjectEntity(ConfiguredBaseModel):
    """
    An identified object entity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    metadata: Optional[IdentifiedObjectList] = Field(None, description="""Metadata for a list of identified objects.""", json_schema_extra = { "linkml_meta": {'alias': 'metadata',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DepositionEntity',
                       'FrameEntity',
                       'IdentifiedObjectEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity']} })
    sources: List[StandardSource] = Field(..., description="""A generalized source class with glob finders. Inherited by a majority of source classes.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'sources',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CollectionMetadataEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DatasetKeyPhotoEntity',
                       'DepositionEntity',
                       'DepositionKeyPhotoEntity',
                       'FrameEntity',
                       'GainEntity',
                       'IdentifiedObjectEntity',
                       'KeyImageEntity',
                       'RawTiltEntity',
                       'RunEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity',
                       'VoxelSpacingEntity']} })


class KeyImageEntity(ConfiguredBaseModel):
    """
    A key image entity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    sources: List[KeyImageSource] = Field(..., description="""A key image source.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'sources',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CollectionMetadataEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DatasetKeyPhotoEntity',
                       'DepositionEntity',
                       'DepositionKeyPhotoEntity',
                       'FrameEntity',
                       'GainEntity',
                       'IdentifiedObjectEntity',
                       'KeyImageEntity',
                       'RawTiltEntity',
                       'RunEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity',
                       'VoxelSpacingEntity']} })


class KeyImageSource(StandardSource):
    """
    A key image source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    parent_filters: Optional[KeyImageParentFilters] = Field(None, description="""Types of parent filters for a key image source.""", json_schema_extra = { "linkml_meta": {'alias': 'parent_filters',
         'domain_of': ['AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })
    destination_glob: Optional[DestinationGlob] = Field(None, description="""A glob class for finding files in the output / destination directory.""", json_schema_extra = { "linkml_meta": {'alias': 'destination_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_glob: Optional[SourceGlob] = Field(None, description="""A glob class for finding files in the source directory.""", json_schema_extra = { "linkml_meta": {'alias': 'source_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_multi_glob: Optional[SourceMultiGlob] = Field(None, description="""A glob class for finding files in the source directory (with multiple globs).""", json_schema_extra = { "linkml_meta": {'alias': 'source_multi_glob',
         'domain_of': ['StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    literal: Optional[StandardLiteral] = Field(None, description="""A literal class with a value attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'literal',
         'domain_of': ['StandardSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DepositionSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    exclude: Optional[List[str]] = Field(None, description="""Exclude files from the source that match (regexes).""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class KeyImageParentFilters(ConfiguredBaseModel):
    """
    Types of parent filters for a key image source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    include: Optional[KeyImageParent] = Field(None, description="""A filter for a parent class of a key image source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'include',
         'domain_of': ['AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters']} })
    exclude: Optional[KeyImageParent] = Field(None, description="""A filter for a parent class of a key image source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class KeyImageParent(ConfiguredBaseModel):
    """
    A filter for a parent class of a key image source. For a given attribute, it can only be used if the current class is a subclass of the attribute.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    dataset: Optional[List[str]] = Field(None, description="""Include or exclude datasets for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'dataset',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    deposition: Optional[List[str]] = Field(None, description="""Include or exclude depositions for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'deposition',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'DatasetParent',
                       'DatasetKeyPhotoParent',
                       'DepositionKeyPhotoParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    run: Optional[List[str]] = Field(None, description="""Include or exclude runs for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'run',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    tomogram: Optional[List[str]] = Field(None, description="""Include or exclude tomograms for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'tomogram', 'domain_of': ['KeyImageParent']} })
    voxel_spacing: Optional[List[str]] = Field(None, description="""Include or exclude voxel spacings for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'voxel_spacing',
         'domain_of': ['Tomogram',
                       'AnnotationParent',
                       'KeyImageParent',
                       'TomogramParent']} })


class RawTiltEntity(ConfiguredBaseModel):
    """
    A raw tilt entity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    sources: List[RawTiltSource] = Field(..., description="""A raw tilt source.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'sources',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CollectionMetadataEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DatasetKeyPhotoEntity',
                       'DepositionEntity',
                       'DepositionKeyPhotoEntity',
                       'FrameEntity',
                       'GainEntity',
                       'IdentifiedObjectEntity',
                       'KeyImageEntity',
                       'RawTiltEntity',
                       'RunEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity',
                       'VoxelSpacingEntity']} })


class RawTiltSource(StandardSource):
    """
    A raw tilt source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    parent_filters: Optional[RawTiltParentFilters] = Field(None, description="""Types of parent filters for a raw tilt source.""", json_schema_extra = { "linkml_meta": {'alias': 'parent_filters',
         'domain_of': ['AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })
    destination_glob: Optional[DestinationGlob] = Field(None, description="""A glob class for finding files in the output / destination directory.""", json_schema_extra = { "linkml_meta": {'alias': 'destination_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_glob: Optional[SourceGlob] = Field(None, description="""A glob class for finding files in the source directory.""", json_schema_extra = { "linkml_meta": {'alias': 'source_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_multi_glob: Optional[SourceMultiGlob] = Field(None, description="""A glob class for finding files in the source directory (with multiple globs).""", json_schema_extra = { "linkml_meta": {'alias': 'source_multi_glob',
         'domain_of': ['StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    literal: Optional[StandardLiteral] = Field(None, description="""A literal class with a value attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'literal',
         'domain_of': ['StandardSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DepositionSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    exclude: Optional[List[str]] = Field(None, description="""Exclude files from the source that match (regexes).""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class RawTiltParentFilters(ConfiguredBaseModel):
    """
    Types of parent filters for a raw tilt source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    include: Optional[RawTiltParent] = Field(None, description="""A filter for a parent class of a raw tilt source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'include',
         'domain_of': ['AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters']} })
    exclude: Optional[RawTiltParent] = Field(None, description="""A filter for a parent class of a raw tilt source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class RawTiltParent(ConfiguredBaseModel):
    """
    A filter for a parent class of a raw tilt source. For a given attribute, it can only be used if the current class is a subclass of the attribute.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    dataset: Optional[List[str]] = Field(None, description="""Include or exclude datasets for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'dataset',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    deposition: Optional[List[str]] = Field(None, description="""Include or exclude depositions for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'deposition',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'DatasetParent',
                       'DatasetKeyPhotoParent',
                       'DepositionKeyPhotoParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    run: Optional[List[str]] = Field(None, description="""Include or exclude runs for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'run',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })


class RunEntity(ConfiguredBaseModel):
    """
    A run entity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    sources: List[RunSource] = Field(..., description="""A run source.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'sources',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CollectionMetadataEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DatasetKeyPhotoEntity',
                       'DepositionEntity',
                       'DepositionKeyPhotoEntity',
                       'FrameEntity',
                       'GainEntity',
                       'IdentifiedObjectEntity',
                       'KeyImageEntity',
                       'RawTiltEntity',
                       'RunEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity',
                       'VoxelSpacingEntity']} })


class RunSource(StandardSource):
    """
    A run source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    parent_filters: Optional[RunParentFilters] = Field(None, description="""Types of parent filters for a run source.""", json_schema_extra = { "linkml_meta": {'alias': 'parent_filters',
         'domain_of': ['AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })
    destination_glob: Optional[DestinationGlob] = Field(None, description="""A glob class for finding files in the output / destination directory.""", json_schema_extra = { "linkml_meta": {'alias': 'destination_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_glob: Optional[SourceGlob] = Field(None, description="""A glob class for finding files in the source directory.""", json_schema_extra = { "linkml_meta": {'alias': 'source_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_multi_glob: Optional[SourceMultiGlob] = Field(None, description="""A glob class for finding files in the source directory (with multiple globs).""", json_schema_extra = { "linkml_meta": {'alias': 'source_multi_glob',
         'domain_of': ['StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    literal: Optional[StandardLiteral] = Field(None, description="""A literal class with a value attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'literal',
         'domain_of': ['StandardSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DepositionSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    exclude: Optional[List[str]] = Field(None, description="""Exclude files from the source that match (regexes).""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class RunParentFilters(ConfiguredBaseModel):
    """
    Types of parent filters for a run source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    include: Optional[RunParent] = Field(None, description="""A filter for a parent class of a run source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'include',
         'domain_of': ['AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters']} })
    exclude: Optional[RunParent] = Field(None, description="""A filter for a parent class of a run source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class RunParent(ConfiguredBaseModel):
    """
    A filter for a parent class of a run source. For a given attribute, it can only be used if the current class is a subclass of the attribute.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    dataset: Optional[List[str]] = Field(None, description="""Include or exclude datasets for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'dataset',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    deposition: Optional[List[str]] = Field(None, description="""Include or exclude depositions for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'deposition',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'DatasetParent',
                       'DatasetKeyPhotoParent',
                       'DepositionKeyPhotoParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })


class StandardizationConfig(ConfiguredBaseModel):
    """
    A standardization configuration.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    deposition_id: int = Field(..., description="""The deposition ID.""", json_schema_extra = { "linkml_meta": {'alias': 'deposition_id', 'domain_of': ['StandardizationConfig']} })
    run_data_map_file: Optional[str] = Field(None, description="""The run data map file.""", json_schema_extra = { "linkml_meta": {'alias': 'run_data_map_file', 'domain_of': ['StandardizationConfig']} })
    run_to_frame_map_csv: Optional[str] = Field(None, description="""The run to frame map CSV.""", json_schema_extra = { "linkml_meta": {'alias': 'run_to_frame_map_csv', 'domain_of': ['StandardizationConfig']} })
    run_to_tomo_map_csv: Optional[str] = Field(None, description="""The run to tomogram map CSV.""", json_schema_extra = { "linkml_meta": {'alias': 'run_to_tomo_map_csv', 'domain_of': ['StandardizationConfig']} })
    run_to_ts_map_csv: Optional[str] = Field(None, description="""The run to tilt series map CSV.""", json_schema_extra = { "linkml_meta": {'alias': 'run_to_ts_map_csv', 'domain_of': ['StandardizationConfig']} })
    source_prefix: str = Field(..., description="""The source prefix of the input files.""", json_schema_extra = { "linkml_meta": {'alias': 'source_prefix', 'domain_of': ['StandardizationConfig']} })


class TiltSeriesEntity(ConfiguredBaseModel):
    """
    A tilt series entity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    metadata: Optional[TiltSeries] = Field(None, description="""Metadata describing a tilt series.""", json_schema_extra = { "linkml_meta": {'alias': 'metadata',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DepositionEntity',
                       'FrameEntity',
                       'IdentifiedObjectEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity']} })
    sources: List[TiltSeriesSource] = Field(..., description="""A tilt series source.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'sources',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CollectionMetadataEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DatasetKeyPhotoEntity',
                       'DepositionEntity',
                       'DepositionKeyPhotoEntity',
                       'FrameEntity',
                       'GainEntity',
                       'IdentifiedObjectEntity',
                       'KeyImageEntity',
                       'RawTiltEntity',
                       'RunEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity',
                       'VoxelSpacingEntity']} })


class TiltSeriesSource(ReferencedSource):
    """
    A tilt series source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    parent_filters: Optional[TiltSeriesParentFilters] = Field(None, description="""Types of parent filters for a tilt series source.""", json_schema_extra = { "linkml_meta": {'alias': 'parent_filters',
         'domain_of': ['AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })
    destination_filter: Optional[DestinationMetadataFilter] = Field(None, description="""A finder class for to filter destination metadata by certain criteria.""", json_schema_extra = { "linkml_meta": {'alias': 'destination_filter',
         'domain_of': ['ReferencedSource', 'TiltSeriesSource', 'TomogramSource']} })
    destination_glob: Optional[DestinationGlob] = Field(None, description="""A glob class for finding files in the output / destination directory.""", json_schema_extra = { "linkml_meta": {'alias': 'destination_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_glob: Optional[SourceGlob] = Field(None, description="""A glob class for finding files in the source directory.""", json_schema_extra = { "linkml_meta": {'alias': 'source_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_multi_glob: Optional[SourceMultiGlob] = Field(None, description="""A glob class for finding files in the source directory (with multiple globs).""", json_schema_extra = { "linkml_meta": {'alias': 'source_multi_glob',
         'domain_of': ['StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    literal: Optional[StandardLiteral] = Field(None, description="""A literal class with a value attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'literal',
         'domain_of': ['StandardSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DepositionSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    exclude: Optional[List[str]] = Field(None, description="""Exclude files from the source that match (regexes).""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class TiltSeriesParentFilters(ConfiguredBaseModel):
    """
    Types of parent filters for a tilt series source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    include: Optional[TiltSeriesParent] = Field(None, description="""A filter for a parent class of a tilt series source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'include',
         'domain_of': ['AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters']} })
    exclude: Optional[TiltSeriesParent] = Field(None, description="""A filter for a parent class of a tilt series source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class TiltSeriesParent(ConfiguredBaseModel):
    """
    A filter for a parent class of a tilt series source. For a given attribute, it can only be used if the current class is a subclass of the attribute.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    dataset: Optional[List[str]] = Field(None, description="""Include or exclude datasets for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'dataset',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    deposition: Optional[List[str]] = Field(None, description="""Include or exclude depositions for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'deposition',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'DatasetParent',
                       'DatasetKeyPhotoParent',
                       'DepositionKeyPhotoParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    run: Optional[List[str]] = Field(None, description="""Include or exclude runs for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'run',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })


class TomogramEntity(ConfiguredBaseModel):
    """
    A tomogram entity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    metadata: Optional[Tomogram] = Field(None, description="""Metadata describing a tomogram.""", json_schema_extra = { "linkml_meta": {'alias': 'metadata',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DepositionEntity',
                       'FrameEntity',
                       'IdentifiedObjectEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity']} })
    sources: List[TomogramSource] = Field(..., description="""A tomogram source.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'sources',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CollectionMetadataEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DatasetKeyPhotoEntity',
                       'DepositionEntity',
                       'DepositionKeyPhotoEntity',
                       'FrameEntity',
                       'GainEntity',
                       'IdentifiedObjectEntity',
                       'KeyImageEntity',
                       'RawTiltEntity',
                       'RunEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity',
                       'VoxelSpacingEntity']} })


class TomogramSource(ReferencedSource):
    """
    A tomogram source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    parent_filters: Optional[TomogramParentFilters] = Field(None, description="""Types of parent filters for a tomogram source.""", json_schema_extra = { "linkml_meta": {'alias': 'parent_filters',
         'domain_of': ['AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })
    destination_filter: Optional[DestinationMetadataFilter] = Field(None, description="""A finder class for to filter destination metadata by certain criteria.""", json_schema_extra = { "linkml_meta": {'alias': 'destination_filter',
         'domain_of': ['ReferencedSource', 'TiltSeriesSource', 'TomogramSource']} })
    destination_glob: Optional[DestinationGlob] = Field(None, description="""A glob class for finding files in the output / destination directory.""", json_schema_extra = { "linkml_meta": {'alias': 'destination_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_glob: Optional[SourceGlob] = Field(None, description="""A glob class for finding files in the source directory.""", json_schema_extra = { "linkml_meta": {'alias': 'source_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_multi_glob: Optional[SourceMultiGlob] = Field(None, description="""A glob class for finding files in the source directory (with multiple globs).""", json_schema_extra = { "linkml_meta": {'alias': 'source_multi_glob',
         'domain_of': ['StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    literal: Optional[StandardLiteral] = Field(None, description="""A literal class with a value attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'literal',
         'domain_of': ['StandardSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DepositionSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    exclude: Optional[List[str]] = Field(None, description="""Exclude files from the source that match (regexes).""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class TomogramParentFilters(ConfiguredBaseModel):
    """
    Types of parent filters for a tomogram source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    include: Optional[TomogramParent] = Field(None, description="""A filter for a parent class of a tomogram source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'include',
         'domain_of': ['AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters']} })
    exclude: Optional[TomogramParent] = Field(None, description="""A filter for a parent class of a tomogram source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class TomogramParent(ConfiguredBaseModel):
    """
    A filter for a parent class of a tomogram source. For a given attribute, it can only be used if the current class is a subclass of the attribute.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    dataset: Optional[List[str]] = Field(None, description="""Include or exclude datasets for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'dataset',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    deposition: Optional[List[str]] = Field(None, description="""Include or exclude depositions for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'deposition',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'DatasetParent',
                       'DatasetKeyPhotoParent',
                       'DepositionKeyPhotoParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    run: Optional[List[str]] = Field(None, description="""Include or exclude runs for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'run',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    voxel_spacing: Optional[List[str]] = Field(None, description="""Include or exclude voxel spacings for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'voxel_spacing',
         'domain_of': ['Tomogram',
                       'AnnotationParent',
                       'KeyImageParent',
                       'TomogramParent']} })


class VoxelSpacingEntity(ConfiguredBaseModel):
    """
    A voxel spacing entity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    sources: List[VoxelSpacingSource] = Field(..., description="""A voxel spacing source.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'sources',
         'domain_of': ['AlignmentEntity',
                       'AnnotationEntity',
                       'CollectionMetadataEntity',
                       'CtfEntity',
                       'DatasetEntity',
                       'DatasetKeyPhotoEntity',
                       'DepositionEntity',
                       'DepositionKeyPhotoEntity',
                       'FrameEntity',
                       'GainEntity',
                       'IdentifiedObjectEntity',
                       'KeyImageEntity',
                       'RawTiltEntity',
                       'RunEntity',
                       'TiltSeriesEntity',
                       'TomogramEntity',
                       'VoxelSpacingEntity']} })


class VoxelSpacingSource(DefaultSource):
    """
    A voxel spacing source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    destination_glob: Optional[DestinationGlob] = Field(None, description="""A glob class for finding files in the output / destination directory.""", json_schema_extra = { "linkml_meta": {'alias': 'destination_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    source_glob: Optional[SourceGlob] = Field(None, description="""A glob class for finding files in the source directory.""", json_schema_extra = { "linkml_meta": {'alias': 'source_glob',
         'domain_of': ['StandardSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    literal: Optional[VoxelSpacingLiteral] = Field(None, description="""A literal for a voxel spacing.""", json_schema_extra = { "linkml_meta": {'alias': 'literal',
         'domain_of': ['StandardSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'VoxelSpacingSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DepositionSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource']} })
    tomogram_header: Optional[TomogramHeader] = Field(None, description="""A tomogram header, a unique source attribute for voxel spacing.""", json_schema_extra = { "linkml_meta": {'alias': 'tomogram_header', 'domain_of': ['VoxelSpacingSource']} })
    parent_filters: Optional[VoxelSpacingParentFilters] = Field(None, description="""Types of parent filters for a voxel spacing source.""", json_schema_extra = { "linkml_meta": {'alias': 'parent_filters',
         'domain_of': ['AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })
    exclude: Optional[List[str]] = Field(None, description="""Exclude files from the source that match (regexes).""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class VoxelSpacingParentFilters(ConfiguredBaseModel):
    """
    Types of parent filters for a voxel spacing source.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    include: Optional[VoxelSpacingParent] = Field(None, description="""A filter for a parent class of a voxel spacing source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'include',
         'domain_of': ['AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters']} })
    exclude: Optional[VoxelSpacingParent] = Field(None, description="""A filter for a parent class of a voxel spacing source. For a given attribute, it can only be used if the current class is a subclass of the attribute.""", json_schema_extra = { "linkml_meta": {'alias': 'exclude',
         'domain_of': ['DefaultSource',
                       'AlignmentParentFilters',
                       'AnnotationParentFilters',
                       'CollectionMetadataParentFilters',
                       'CtfParentFilters',
                       'DatasetParentFilters',
                       'DatasetKeyPhotoParentFilters',
                       'DepositionKeyPhotoParentFilters',
                       'FrameParentFilters',
                       'GainParentFilters',
                       'KeyImageParentFilters',
                       'RawTiltParentFilters',
                       'RunParentFilters',
                       'TiltSeriesParentFilters',
                       'TomogramParentFilters',
                       'VoxelSpacingParentFilters',
                       'StandardSource',
                       'ReferencedSource',
                       'AlignmentSource',
                       'AnnotationSource',
                       'CollectionMetadataSource',
                       'CtfSource',
                       'DatasetSource',
                       'DatasetKeyPhotoSource',
                       'DepositionSource',
                       'DepositionKeyPhotoSource',
                       'FrameSource',
                       'GainSource',
                       'KeyImageSource',
                       'RawTiltSource',
                       'RunSource',
                       'TiltSeriesSource',
                       'TomogramSource',
                       'VoxelSpacingSource']} })


class VoxelSpacingParent(ConfiguredBaseModel):
    """
    A filter for a parent class of a voxel spacing source. For a given attribute, it can only be used if the current class is a subclass of the attribute.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    dataset: Optional[List[str]] = Field(None, description="""Include or exclude datasets for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'dataset',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    deposition: Optional[List[str]] = Field(None, description="""Include or exclude depositions for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'deposition',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'DatasetParent',
                       'DatasetKeyPhotoParent',
                       'DepositionKeyPhotoParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'RunParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })
    run: Optional[List[str]] = Field(None, description="""Include or exclude runs for a source.""", json_schema_extra = { "linkml_meta": {'alias': 'run',
         'domain_of': ['AlignmentParent',
                       'AnnotationParent',
                       'CollectionMetadataParent',
                       'CtfParent',
                       'FrameParent',
                       'GainParent',
                       'KeyImageParent',
                       'RawTiltParent',
                       'TiltSeriesParent',
                       'TomogramParent',
                       'VoxelSpacingParent']} })


class VoxelSpacingLiteral(ConfiguredBaseModel):
    """
    A literal for a voxel spacing.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    value: List[float] = Field(..., description="""The value for the voxel spacing literal.""", min_length=1, json_schema_extra = { "linkml_meta": {'alias': 'value',
         'domain_of': ['StandardLiteral',
                       'KeyPhotoLiteral',
                       'DestinationMetadataFilterKeyPair',
                       'VoxelSpacingLiteral']} })


class TomogramHeader(ConfiguredBaseModel):
    """
    A tomogram header, a unique source attribute for voxel spacing.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cdp-ingestion-config'})

    list_glob: str = Field(..., description="""The glob for the tomogram header file.""", json_schema_extra = { "linkml_meta": {'alias': 'list_glob',
         'domain_of': ['GeneralGlob',
                       'TomogramHeader',
                       'DestinationGlob',
                       'SourceGlob']} })
    match_regex: Optional[str] = Field(".*", description="""The regex for the tomogram header file.""", json_schema_extra = { "linkml_meta": {'alias': 'match_regex',
         'domain_of': ['GeneralGlob',
                       'TomogramHeader',
                       'DestinationGlob',
                       'SourceGlob'],
         'ifabsent': 'string(.*)'} })
    header_key: Optional[str] = Field("voxel_size", description="""The key in the header file for the voxel spacing.""", json_schema_extra = { "linkml_meta": {'alias': 'header_key',
         'domain_of': ['TomogramHeader'],
         'ifabsent': 'string(voxel_size)'} })


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
Assay.model_rebuild()
DevelopmentStageDetails.model_rebuild()
Disease.model_rebuild()
PicturedMetadataEntity.model_rebuild()
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
Container.model_rebuild()
GeneralGlob.model_rebuild()
DestinationGlob.model_rebuild()
SourceGlob.model_rebuild()
SourceMultiGlob.model_rebuild()
DefaultSource.model_rebuild()
StandardSource.model_rebuild()
StandardLiteral.model_rebuild()
KeyPhotoLiteral.model_rebuild()
DestinationMetadataFilterKeyPair.model_rebuild()
DestinationMetadataFilter.model_rebuild()
ReferencedSource.model_rebuild()
AlignmentEntity.model_rebuild()
AlignmentSource.model_rebuild()
AlignmentParentFilters.model_rebuild()
AlignmentParent.model_rebuild()
AnnotationEntity.model_rebuild()
AnnotationSource.model_rebuild()
AnnotationParentFilters.model_rebuild()
AnnotationParent.model_rebuild()
CollectionMetadataEntity.model_rebuild()
CollectionMetadataSource.model_rebuild()
CollectionMetadataParentFilters.model_rebuild()
CollectionMetadataParent.model_rebuild()
CtfEntity.model_rebuild()
CtfSource.model_rebuild()
CtfParentFilters.model_rebuild()
CtfParent.model_rebuild()
DatasetEntity.model_rebuild()
DatasetSource.model_rebuild()
DatasetParentFilters.model_rebuild()
DatasetParent.model_rebuild()
DatasetKeyPhotoEntity.model_rebuild()
DatasetKeyPhotoSource.model_rebuild()
DatasetKeyPhotoParentFilters.model_rebuild()
DatasetKeyPhotoParent.model_rebuild()
DepositionEntity.model_rebuild()
DepositionSource.model_rebuild()
DepositionKeyPhotoEntity.model_rebuild()
DepositionKeyPhotoSource.model_rebuild()
DepositionKeyPhotoParentFilters.model_rebuild()
DepositionKeyPhotoParent.model_rebuild()
FrameEntity.model_rebuild()
FrameSource.model_rebuild()
FrameParentFilters.model_rebuild()
FrameParent.model_rebuild()
GainEntity.model_rebuild()
GainSource.model_rebuild()
GainParentFilters.model_rebuild()
GainParent.model_rebuild()
IdentifiedObjectEntity.model_rebuild()
KeyImageEntity.model_rebuild()
KeyImageSource.model_rebuild()
KeyImageParentFilters.model_rebuild()
KeyImageParent.model_rebuild()
RawTiltEntity.model_rebuild()
RawTiltSource.model_rebuild()
RawTiltParentFilters.model_rebuild()
RawTiltParent.model_rebuild()
RunEntity.model_rebuild()
RunSource.model_rebuild()
RunParentFilters.model_rebuild()
RunParent.model_rebuild()
StandardizationConfig.model_rebuild()
TiltSeriesEntity.model_rebuild()
TiltSeriesSource.model_rebuild()
TiltSeriesParentFilters.model_rebuild()
TiltSeriesParent.model_rebuild()
TomogramEntity.model_rebuild()
TomogramSource.model_rebuild()
TomogramParentFilters.model_rebuild()
TomogramParent.model_rebuild()
VoxelSpacingEntity.model_rebuild()
VoxelSpacingSource.model_rebuild()
VoxelSpacingParentFilters.model_rebuild()
VoxelSpacingParent.model_rebuild()
VoxelSpacingLiteral.model_rebuild()
TomogramHeader.model_rebuild()
