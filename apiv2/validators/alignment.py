"""
Pydantic validator for Alignment

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/validators/class_name.py.j2 instead.
"""

# ruff: noqa: E501 Line too long

from support.enums import alignment_type_enum, alignment_method_type_enum

import typing
import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated


class AlignmentCreateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    deposition_id: Annotated[uuid.UUID | None, Field()]
    tiltseries_id: Annotated[uuid.UUID | None, Field()]
    run_id: Annotated[uuid.UUID | None, Field()]
    alignment_type: Annotated[alignment_type_enum | None, Field()]
    alignment_method: Annotated[alignment_method_type_enum | None, Field()]
    volume_x_dimension: Annotated[float | None, Field()]
    volume_y_dimension: Annotated[float | None, Field()]
    volume_z_dimension: Annotated[float | None, Field()]
    volume_x_offset: Annotated[float | None, Field()]
    volume_y_offset: Annotated[float | None, Field()]
    volume_z_offset: Annotated[float | None, Field()]
    x_rotation_offset: Annotated[float | None, Field()]
    tilt_offset: Annotated[float | None, Field()]
    affine_transformation_matrix: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    s3_alignment_metadata: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    https_alignment_metadata: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    is_portal_standard: Annotated[bool | None, Field()]
    id: Annotated[int, Field()]


class AlignmentUpdateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    deposition_id: Annotated[uuid.UUID | None, Field()]
    tiltseries_id: Annotated[uuid.UUID | None, Field()]
    run_id: Annotated[uuid.UUID | None, Field()]
    alignment_type: Annotated[alignment_type_enum | None, Field()]
    alignment_method: Annotated[alignment_method_type_enum | None, Field()]
    volume_x_dimension: Annotated[float | None, Field()]
    volume_y_dimension: Annotated[float | None, Field()]
    volume_z_dimension: Annotated[float | None, Field()]
    volume_x_offset: Annotated[float | None, Field()]
    volume_y_offset: Annotated[float | None, Field()]
    volume_z_offset: Annotated[float | None, Field()]
    x_rotation_offset: Annotated[float | None, Field()]
    tilt_offset: Annotated[float | None, Field()]
    affine_transformation_matrix: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    s3_alignment_metadata: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    https_alignment_metadata: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    is_portal_standard: Annotated[bool | None, Field()]
    id: Annotated[int | None, Field()]
