"""
Pydantic validator for PerSectionParameters

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/validators/class_name.py.j2 instead.
"""

# ruff: noqa: E501 Line too long


import uuid

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Annotated


class PerSectionParametersCreateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    frame_id: Annotated[uuid.UUID, Field()]
    tiltseries_id: Annotated[uuid.UUID, Field()]
    z_index: Annotated[
        int,
        Field(
            ge=0,
        ),
    ]
    defocus: Annotated[
        float | None,
        Field(
            ge=100,
            le=100,
        ),
    ]
    astigmatism: Annotated[float | None, Field()]
    astigmatic_angle: Annotated[
        float | None,
        Field(
            ge=-180,
            le=180,
        ),
    ]
    id: Annotated[int, Field()]


class PerSectionParametersUpdateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    frame_id: Annotated[uuid.UUID | None, Field()]
    tiltseries_id: Annotated[uuid.UUID | None, Field()]
    z_index: Annotated[
        int | None,
        Field(
            ge=0,
        ),
    ]
    defocus: Annotated[
        float | None,
        Field(
            ge=100,
            le=100,
        ),
    ]
    astigmatism: Annotated[float | None, Field()]
    astigmatic_angle: Annotated[
        float | None,
        Field(
            ge=-180,
            le=180,
        ),
    ]
    id: Annotated[int | None, Field()]
