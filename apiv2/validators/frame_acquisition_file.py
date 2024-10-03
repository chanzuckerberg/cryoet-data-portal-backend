"""
Pydantic validator for FrameAcquisitionFile

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/validators/class_name.py.j2 instead.
"""

# ruff: noqa: E501 Line too long


import uuid

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated


class FrameAcquisitionFileCreateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    run_id: Annotated[uuid.UUID | None, Field()]
    s3_mdoc_path: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    https_mdoc_path: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    id: Annotated[int, Field()]


class FrameAcquisitionFileUpdateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    run_id: Annotated[uuid.UUID | None, Field()]
    s3_mdoc_path: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    https_mdoc_path: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    id: Annotated[int | None, Field()]
