"""
Auto-generated by running `make codegen`. Do not edit!
Make changes to the template platformics/codegen/templates/database/models/class_name.py.j2 instead.

SQLAlchemy database model for DatasetAuthor
"""

from typing import TYPE_CHECKING

from platformics.database.models.base import Base
from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from database.models.dataset import Dataset

    ...
else:
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
    id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, autoincrement=True, primary_key=True)
    author_list_order: Mapped[int] = mapped_column(Integer, nullable=False)
    orcid: Mapped[str] = mapped_column(String, nullable=True)
    kaggle_id: Mapped[str] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=True)
    affiliation_name: Mapped[str] = mapped_column(String, nullable=True)
    affiliation_address: Mapped[str] = mapped_column(String, nullable=True)
    affiliation_identifier: Mapped[str] = mapped_column(String, nullable=True)
    corresponding_author_status: Mapped[bool] = mapped_column(Boolean, nullable=True)
    primary_author_status: Mapped[bool] = mapped_column(Boolean, nullable=True)
