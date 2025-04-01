"""
Auto-generated by running `make codegen`. Do not edit!
Make changes to the template platformics/codegen/templates/validators/class_name.py.j2 instead.

Pydantic validator for Tomogram
"""

# ruff: noqa: E501 Line too long


import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from support.enums import fiducial_alignment_status_enum, tomogram_processing_enum, tomogram_reconstruction_method_enum
from typing_extensions import Annotated


class TomogramCreateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    alignment_id: Annotated[uuid.UUID | None, Field()] = None
    deposition_id: Annotated[uuid.UUID, Field()]
    run_id: Annotated[uuid.UUID | None, Field()] = None
    tomogram_voxel_spacing_id: Annotated[uuid.UUID | None, Field()] = None
    name: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
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
    tomogram_version: Annotated[float | None, Field()] = None
    processing_software: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    reconstruction_software: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    is_portal_standard: Annotated[bool | None, Field()] = None
    is_author_submitted: Annotated[bool | None, Field()] = None
    is_visualization_default: Annotated[bool | None, Field()] = None
    s3_omezarr_dir: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    https_omezarr_dir: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    file_size_omezarr: Annotated[float | None, Field()] = None
    s3_mrc_file: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    https_mrc_file: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    file_size_mrc: Annotated[float | None, Field()] = None
    scale0_dimensions: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    scale1_dimensions: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    scale2_dimensions: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    ctf_corrected: Annotated[bool | None, Field()] = None
    offset_x: Annotated[int, Field()]
    offset_y: Annotated[int, Field()]
    offset_z: Annotated[int, Field()]
    key_photo_url: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    key_photo_thumbnail_url: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    neuroglancer_config: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    publications: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
            pattern=r"(^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+(\s*,\s*(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)*$)|(^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+(\s*,\s*(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)*$)",
        ),
    ] = None
    related_database_entries: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
            pattern=r"(^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8}))*$)|(^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8}))*$)",
        ),
    ] = None
    id: Annotated[int, Field()]
    deposition_date: Annotated[datetime.datetime | None, Field()] = None
    release_date: Annotated[datetime.datetime | None, Field()] = None
    last_modified_date: Annotated[datetime.datetime | None, Field()] = None


class TomogramUpdateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    alignment_id: Annotated[uuid.UUID | None, Field()] = None
    deposition_id: Annotated[uuid.UUID | None, Field()] = None
    run_id: Annotated[uuid.UUID | None, Field()] = None
    tomogram_voxel_spacing_id: Annotated[uuid.UUID | None, Field()] = None
    name: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    size_x: Annotated[
        int | None,
        Field(
            ge=0,
        ),
    ] = None
    size_y: Annotated[
        int | None,
        Field(
            ge=0,
        ),
    ] = None
    size_z: Annotated[
        int | None,
        Field(
            ge=0,
        ),
    ] = None
    voxel_spacing: Annotated[
        float | None,
        Field(
            ge=0.001,
        ),
    ] = None
    fiducial_alignment_status: Annotated[fiducial_alignment_status_enum | None, Field()] = None
    reconstruction_method: Annotated[tomogram_reconstruction_method_enum | None, Field()] = None
    processing: Annotated[tomogram_processing_enum | None, Field()] = None
    tomogram_version: Annotated[float | None, Field()] = None
    processing_software: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    reconstruction_software: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    is_portal_standard: Annotated[bool | None, Field()] = None
    is_author_submitted: Annotated[bool | None, Field()] = None
    is_visualization_default: Annotated[bool | None, Field()] = None
    s3_omezarr_dir: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    https_omezarr_dir: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    file_size_omezarr: Annotated[float | None, Field()] = None
    s3_mrc_file: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    https_mrc_file: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    file_size_mrc: Annotated[float | None, Field()] = None
    scale0_dimensions: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    scale1_dimensions: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    scale2_dimensions: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    ctf_corrected: Annotated[bool | None, Field()] = None
    offset_x: Annotated[int | None, Field()] = None
    offset_y: Annotated[int | None, Field()] = None
    offset_z: Annotated[int | None, Field()] = None
    key_photo_url: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    key_photo_thumbnail_url: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    neuroglancer_config: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    publications: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
            pattern=r"(^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+(\s*,\s*(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)*$)|(^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+(\s*,\s*(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)*$)",
        ),
    ] = None
    related_database_entries: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
            pattern=r"(^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8}))*$)|(^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8}))*$)",
        ),
    ] = None
    id: Annotated[int | None, Field()] = None
    deposition_date: Annotated[datetime.datetime | None, Field()] = None
    release_date: Annotated[datetime.datetime | None, Field()] = None
    last_modified_date: Annotated[datetime.datetime | None, Field()] = None
