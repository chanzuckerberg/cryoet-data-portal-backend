"""
Pydantic validator for TomogramVoxelSpacing

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/validators/class_name.py.j2 instead.
"""

# ruff: noqa: E501 Line too long


import typing
import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated


class TomogramVoxelSpacingCreateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    run_id: Annotated[uuid.UUID | None, Field()]
    voxel_spacing: Annotated[
        float,
        Field(
            ge=0.001,
        ),
    ]
    s3_prefix: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    https_prefix: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    id: Annotated[int, Field()]


class TomogramVoxelSpacingUpdateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    run_id: Annotated[uuid.UUID | None, Field()]
    voxel_spacing: Annotated[
        float | None,
        Field(
            ge=0.001,
        ),
    ]
    s3_prefix: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    https_prefix: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    id: Annotated[int | None, Field()]