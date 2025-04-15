"""
Auto-generated by running `make codegen`. Do not edit!
Make changes to the template platformics/codegen/templates/validators/class_name.py.j2 instead.

Pydantic validator for GainFile
"""

# ruff: noqa: E501 Line too long


import uuid

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated


class GainFileCreateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    run_id: Annotated[uuid.UUID, Field()]
    s3_file_path: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    https_file_path: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    id: Annotated[int, Field()]


class GainFileUpdateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    run_id: Annotated[uuid.UUID | None, Field()] = None
    s3_file_path: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    https_file_path: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ] = None
    id: Annotated[int | None, Field()] = None
