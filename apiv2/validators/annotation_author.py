"""
Pydantic validator for AnnotationAuthor

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/validators/class_name.py.j2 instead.
"""

# ruff: noqa: E501 Line too long

import uuid

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated


class AnnotationAuthorCreateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    annotation_id: Annotated[uuid.UUID | None, Field()]
    id: Annotated[int, Field()]
    author_list_order: Annotated[int, Field()]
    orcid: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
            pattern=r"[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$",
        ),
    ]
    kaggle_id: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    name: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    email: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    affiliation_name: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    affiliation_address: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    affiliation_identifier: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    corresponding_author_status: Annotated[bool | None, Field()]
    primary_author_status: Annotated[bool | None, Field()]


class AnnotationAuthorUpdateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    annotation_id: Annotated[uuid.UUID | None, Field()]
    id: Annotated[int | None, Field()]
    author_list_order: Annotated[int | None, Field()]
    orcid: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
            pattern=r"[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$",
        ),
    ]
    kaggle_id: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    name: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    email: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    affiliation_name: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    affiliation_address: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    affiliation_identifier: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    corresponding_author_status: Annotated[bool | None, Field()]
    primary_author_status: Annotated[bool | None, Field()]
