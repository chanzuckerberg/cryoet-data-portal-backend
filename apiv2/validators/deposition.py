"""
Pydantic validator for Deposition

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/validators/class_name.py.j2 instead.
"""

# ruff: noqa: E501 Line too long

import datetime

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated


class DepositionCreateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    title: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    description: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    tag: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    deposition_publications: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
            pattern=r"(^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+(\s*,\s*(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)*$)|(^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+(\s*,\s*(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)*$)",
        ),
    ]
    related_database_entries: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
            pattern=r"(^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8}))*$)|(^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8}))*$)",
        ),
    ]
    deposition_date: Annotated[datetime.datetime, Field()]
    release_date: Annotated[datetime.datetime, Field()]
    last_modified_date: Annotated[datetime.datetime, Field()]
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
    id: Annotated[int, Field()]


class DepositionUpdateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    title: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    description: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    tag: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    deposition_publications: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
            pattern=r"(^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+(\s*,\s*(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)*$)|(^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+(\s*,\s*(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+)*$)",
        ),
    ]
    related_database_entries: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
            pattern=r"(^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8}))*$)|(^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8}))*$)",
        ),
    ]
    deposition_date: Annotated[datetime.datetime | None, Field()]
    release_date: Annotated[datetime.datetime | None, Field()]
    last_modified_date: Annotated[datetime.datetime | None, Field()]
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
    id: Annotated[int | None, Field()]
