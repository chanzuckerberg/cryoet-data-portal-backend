"""
Pydantic validator for Tomogram

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/validators/class_name.py.j2 instead.
"""

# ruff: noqa: E501 Line too long


import uuid

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from support.enums import fiducial_alignment_status_enum, tomogram_processing_enum, tomogram_reconstruction_method_enum
from typing_extensions import Annotated


class TomogramCreateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    alignment_id: Annotated[uuid.UUID | None, Field()]
    deposition_id: Annotated[uuid.UUID | None, Field()]
    run_id: Annotated[uuid.UUID | None, Field()]
    tomogram_voxel_spacing_id: Annotated[uuid.UUID | None, Field()]
    name: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    size_x: Annotated[
        int,
        Field(
            ge=0,
        ),
    ]
    size_y: Annotated[
        int,
        Field(
            ge=0,
        ),
    ]
    size_z: Annotated[
        int,
        Field(
            ge=0,
        ),
    ]
    voxel_spacing: Annotated[
        float,
        Field(
            ge=0.001,
        ),
    ]
    fiducial_alignment_status: Annotated[fiducial_alignment_status_enum, Field()]
    reconstruction_method: Annotated[tomogram_reconstruction_method_enum, Field()]
    processing: Annotated[tomogram_processing_enum, Field()]
    tomogram_version: Annotated[float | None, Field()]
    processing_software: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    reconstruction_software: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    is_canonical: Annotated[bool | None, Field()]
    s3_omezarr_dir: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    https_omezarr_dir: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    s3_mrc_file: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    https_mrc_file: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    scale0_dimensions: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    scale1_dimensions: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    scale2_dimensions: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    ctf_corrected: Annotated[bool | None, Field()]
    offset_x: Annotated[int, Field()]
    offset_y: Annotated[int, Field()]
    offset_z: Annotated[int, Field()]
    key_photo_url: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    key_photo_thumbnail_url: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    neuroglancer_config: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    is_standardized: Annotated[bool, Field()]
    id: Annotated[int, Field()]


class TomogramUpdateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    alignment_id: Annotated[uuid.UUID | None, Field()]
    deposition_id: Annotated[uuid.UUID | None, Field()]
    run_id: Annotated[uuid.UUID | None, Field()]
    tomogram_voxel_spacing_id: Annotated[uuid.UUID | None, Field()]
    name: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    size_x: Annotated[
        int | None,
        Field(
            ge=0,
        ),
    ]
    size_y: Annotated[
        int | None,
        Field(
            ge=0,
        ),
    ]
    size_z: Annotated[
        int | None,
        Field(
            ge=0,
        ),
    ]
    voxel_spacing: Annotated[
        float | None,
        Field(
            ge=0.001,
        ),
    ]
    fiducial_alignment_status: Annotated[fiducial_alignment_status_enum | None, Field()]
    reconstruction_method: Annotated[tomogram_reconstruction_method_enum | None, Field()]
    processing: Annotated[tomogram_processing_enum | None, Field()]
    tomogram_version: Annotated[float | None, Field()]
    processing_software: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    reconstruction_software: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    is_canonical: Annotated[bool | None, Field()]
    s3_omezarr_dir: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    https_omezarr_dir: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    s3_mrc_file: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    https_mrc_file: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    scale0_dimensions: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    scale1_dimensions: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    scale2_dimensions: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    ctf_corrected: Annotated[bool | None, Field()]
    offset_x: Annotated[int | None, Field()]
    offset_y: Annotated[int | None, Field()]
    offset_z: Annotated[int | None, Field()]
    key_photo_url: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    key_photo_thumbnail_url: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    neuroglancer_config: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    is_standardized: Annotated[bool | None, Field()]
    id: Annotated[int | None, Field()]
