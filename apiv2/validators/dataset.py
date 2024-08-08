"""
Pydantic validator for Dataset

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/validators/class_name.py.j2 instead.
"""

# ruff: noqa: E501 Line too long


from support.enums import sample_type_enum

import typing
import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated


class DatasetCreateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    deposition_id: Annotated[uuid.UUID | None, Field()]
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
    organism_name: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    organism_taxid: Annotated[
        int | None,
        Field(
            ge=1,
        ),
    ]
    tissue_name: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    tissue_id: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
            pattern=r"^BTO:[0-9]{7}$",
        ),
    ]
    cell_name: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    cell_type_id: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
            pattern=r"^CL:[0-9]{7}$",
        ),
    ]
    cell_strain_name: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    cell_strain_id: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
            pattern=r"(WBStrain[0-9]{8}$)|(^[a-zA-Z]+:[0-9]+$)",
        ),
    ]
    sample_type: Annotated[sample_type_enum | None, Field()]
    sample_preparation: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    grid_preparation: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    other_setup: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
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
    cell_component_name: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    cell_component_id: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
            pattern=r"^GO:[0-9]{7}$",
        ),
    ]
    deposition_date: Annotated[datetime.datetime, Field()]
    release_date: Annotated[datetime.datetime, Field()]
    last_modified_date: Annotated[datetime.datetime, Field()]
    publications: Annotated[
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
    related_database_links: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    dataset_citations: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
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


class DatasetUpdateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    deposition_id: Annotated[uuid.UUID | None, Field()]
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
    organism_name: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    organism_taxid: Annotated[
        int | None,
        Field(
            ge=1,
        ),
    ]
    tissue_name: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    tissue_id: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
            pattern=r"^BTO:[0-9]{7}$",
        ),
    ]
    cell_name: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    cell_type_id: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
            pattern=r"^CL:[0-9]{7}$",
        ),
    ]
    cell_strain_name: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    cell_strain_id: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
            pattern=r"(WBStrain[0-9]{8}$)|(^[a-zA-Z]+:[0-9]+$)",
        ),
    ]
    sample_type: Annotated[sample_type_enum | None, Field()]
    sample_preparation: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    grid_preparation: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    other_setup: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
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
    cell_component_name: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    cell_component_id: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
            pattern=r"^GO:[0-9]{7}$",
        ),
    ]
    deposition_date: Annotated[datetime.datetime | None, Field()]
    release_date: Annotated[datetime.datetime | None, Field()]
    last_modified_date: Annotated[datetime.datetime | None, Field()]
    publications: Annotated[
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
    related_database_links: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
        ),
    ]
    dataset_citations: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
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