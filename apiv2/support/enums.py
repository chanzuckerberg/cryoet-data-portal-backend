"""
GraphQL enums

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/support/enums.py.j2 instead.
"""

import enum

import strawberry


@strawberry.enum
class annotation_file_source_enum(enum.StrEnum):
    dataset_author = "dataset_author"
    community = "community"
    portal_standard = "portal_standard"


@strawberry.enum
class alignment_method_type_enum(enum.StrEnum):
    projection_matching = "projection_matching"
    patch_tracking = "patch_tracking"
    fiducial_based = "fiducial_based"


@strawberry.enum
class annotation_method_type_enum(enum.StrEnum):
    manual = "manual"
    automated = "automated"
    hybrid = "hybrid"
    simulated = "simulated"


@strawberry.enum
class annotation_file_shape_type_enum(enum.StrEnum):
    SegmentationMask = "SegmentationMask"
    OrientedPoint = "OrientedPoint"
    Point = "Point"
    InstanceSegmentation = "InstanceSegmentation"
    Mesh = "Mesh"


@strawberry.enum
class annotation_method_link_type_enum(enum.StrEnum):
    documentation = "documentation"
    models_weights = "models_weights"
    other = "other"
    source_code = "source_code"
    website = "website"


@strawberry.enum
class deposition_types_enum(enum.StrEnum):
    annotation = "annotation"
    dataset = "dataset"
    tomogram = "tomogram"


@strawberry.enum
class sample_type_enum(enum.StrEnum):
    cell = "cell"
    tissue = "tissue"
    organism = "organism"
    organelle = "organelle"
    virus = "virus"
    in_vitro = "in_vitro"
    in_silico = "in_silico"
    other = "other"


@strawberry.enum
class tiltseries_camera_acquire_mode_enum(enum.StrEnum):
    counting = "counting"
    superresolution = "superresolution"
    linear = "linear"
    cds = "cds"


@strawberry.enum
class tiltseries_microscope_manufacturer_enum(enum.StrEnum):
    FEI = "FEI"
    TFS = "TFS"
    JEOL = "JEOL"
    SIMULATED = "SIMULATED"


@strawberry.enum
class fiducial_alignment_status_enum(enum.StrEnum):
    FIDUCIAL = "FIDUCIAL"
    NON_FIDUCIAL = "NON_FIDUCIAL"


@strawberry.enum
class tomogram_processing_enum(enum.StrEnum):
    denoised = "denoised"
    filtered = "filtered"
    raw = "raw"
    filtered_odd = "filtered_odd"


@strawberry.enum
class tomogram_reconstruction_method_enum(enum.StrEnum):
    SART = "SART"
    Fourier_Space = "Fourier_Space"
    SIRT = "SIRT"
    WBP = "WBP"
    Unknown = "Unknown"


@strawberry.enum
class alignment_type_enum(enum.StrEnum):
    LOCAL = "LOCAL"
    GLOBAL = "GLOBAL"
