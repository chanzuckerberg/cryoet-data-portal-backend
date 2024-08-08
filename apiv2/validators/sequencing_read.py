"""
Pydantic validator for SequencingRead

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/validators/class_name.py.j2 instead.
"""

# ruff: noqa: E501 Line too long


from support.enums import SequencingProtocol, SequencingTechnology, NucleicAcid

import typing
import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated


class SequencingReadCreateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    sample_id: Annotated[uuid.UUID | None, Field()]
    protocol: Annotated[SequencingProtocol, Field()]
    technology: Annotated[SequencingTechnology, Field()]
    nucleic_acid: Annotated[NucleicAcid, Field()]
    primer_file_id: Annotated[uuid.UUID | None, Field()]
    contig_id: Annotated[uuid.UUID | None, Field()]
    producing_run_id: Annotated[uuid.UUID | None, Field()]
    collection_id: Annotated[
        int,
        Field(
            ge=0,
        ),
    ]
    deleted_at: Annotated[datetime.datetime | None, Field()]


class SequencingReadUpdateInputValidator(BaseModel):
    # Pydantic stuff
    model_config = ConfigDict(from_attributes=True)
    sample_id: Annotated[uuid.UUID | None, Field()]
    protocol: Annotated[SequencingProtocol | None, Field()]
    technology: Annotated[SequencingTechnology | None, Field()]
    nucleic_acid: Annotated[NucleicAcid | None, Field()]
    primer_file_id: Annotated[uuid.UUID | None, Field()]
    collection_id: Annotated[
        int | None,
        Field(
            ge=0,
        ),
    ]
    deleted_at: Annotated[datetime.datetime | None, Field()]