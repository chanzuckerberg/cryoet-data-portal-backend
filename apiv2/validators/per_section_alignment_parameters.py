"""
Pydantic validator for PerSectionAlignmentParameters

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/validators/class_name.py.j2 instead.
"""

# ruff: noqa: E501 Line too long

import typing
import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated


class PerSectionAlignmentParametersCreateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    alignment_id: Annotated[uuid.UUID, Field()]
    z_index: Annotated[
        int,
        Field(
            ge=0,
        ),
    ]
    x_offset: Annotated[float | None, Field()]
    y_offset: Annotated[float | None, Field()]
    volume_x_rotation: Annotated[float | None, Field()]
    in_plane_rotation: Annotated[list[list[float]] | None, Field()]
    tilt_angle: Annotated[float | None, Field()]
    id: Annotated[int, Field()]


class PerSectionAlignmentParametersUpdateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    alignment_id: Annotated[uuid.UUID | None, Field()]
    z_index: Annotated[
        int | None,
        Field(
            ge=0,
        ),
    ]
    x_offset: Annotated[float | None, Field()]
    y_offset: Annotated[float | None, Field()]
    volume_x_rotation: Annotated[float | None, Field()]
    in_plane_rotation: Annotated[list[list[float]] | None, Field()]
    tilt_angle: Annotated[float | None, Field()]
    id: Annotated[int | None, Field()]
