"""
SQLAlchemy database model for DatasetAuthor

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/database/models/class_name.py.j2 instead.
"""

import uuid
import uuid6
import datetime
from typing import TYPE_CHECKING

from platformics.database.models.base import Base
from sqlalchemy import ForeignKey, String, Float, Integer, Enum, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from platformics.database.models.file import File

if TYPE_CHECKING:
    from platformics.database.models.file import File
    from database.models.dataset import Dataset

    ...
else:
    File = "File"
    Dataset = "Dataset"
    ...


class DatasetAuthor(Base):
    __tablename__ = "dataset_author"
    __mapper_args__ = {"polymorphic_identity": __tablename__, "polymorphic_load": "inline"}

    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset.id"), nullable=True, index=True)
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        foreign_keys=dataset_id,
        back_populates="authors",
    )
    author_list_order: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=True)
    affiliation_name: Mapped[str] = mapped_column(String, nullable=True)
    affiliation_address: Mapped[str] = mapped_column(String, nullable=True)
    affiliation_identifier: Mapped[str] = mapped_column(String, nullable=True)
    corresponding_author_status: Mapped[bool] = mapped_column(Boolean, nullable=True)
    primary_author_status: Mapped[bool] = mapped_column(Boolean, nullable=True)
    orcid: Mapped[str] = mapped_column(String, nullable=True)
    id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, autoincrement=True, primary_key=True)