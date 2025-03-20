"""
SQLAlchemy database model for Dataset

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/database/models/class_name.py.j2 instead.
"""




import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from support.enums import sample_type_enum

from platformics.database.models.base import Base
from platformics.database.models.file import File

if TYPE_CHECKING:
    from database.models.dataset_author import DatasetAuthor
    from database.models.dataset_funding import DatasetFunding
    from database.models.deposition import Deposition
    from database.models.run import Run

    from platformics.database.models.file import File
    ...
else:
    File = "File"
    Deposition = "Deposition"
    DatasetFunding = "DatasetFunding"
    DatasetAuthor = "DatasetAuthor"
    Run = "Run"
    ...


class Dataset(Base):
    __tablename__ = "dataset"
    __mapper_args__ = {"polymorphic_identity": __tablename__,"polymorphic_load": "inline"}




    deposition_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("deposition.id"),
        nullable=False, index=True,
    )
    deposition: Mapped["Deposition"] = relationship(
        "Deposition",
        foreign_keys=deposition_id,
        back_populates="datasets",

    )
    funding_sources: Mapped[
        list[DatasetFunding]
    ] = relationship(
        "DatasetFunding",
        back_populates="dataset",
        uselist=True,
        foreign_keys="DatasetFunding.dataset_id",
        cascade="all, delete-orphan",
    )
    authors: Mapped[
        list[DatasetAuthor]
    ] = relationship(
        "DatasetAuthor",
        back_populates="dataset",
        uselist=True,
        foreign_keys="DatasetAuthor.dataset_id",
        cascade="all, delete-orphan",
    )
    runs: Mapped[
        list[Run]
    ] = relationship(
        "Run",
        back_populates="dataset",
        uselist=True,
        foreign_keys="Run.dataset_id",
        cascade="all, delete-orphan",
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    organism_name: Mapped[str] = mapped_column(String, nullable=True)
    organism_taxid: Mapped[int] = mapped_column(Integer, nullable=True)
    tissue_name: Mapped[str] = mapped_column(String, nullable=True)
    tissue_id: Mapped[str] = mapped_column(String, nullable=True)
    cell_name: Mapped[str] = mapped_column(String, nullable=True)
    cell_type_id: Mapped[str] = mapped_column(String, nullable=True)
    cell_strain_name: Mapped[str] = mapped_column(String, nullable=True)
    cell_strain_id: Mapped[str] = mapped_column(String, nullable=True)
    sample_type: Mapped[sample_type_enum] = mapped_column(Enum(sample_type_enum, native_enum=False), nullable=True)
    sample_preparation: Mapped[str] = mapped_column(String, nullable=True)
    grid_preparation: Mapped[str] = mapped_column(String, nullable=True)
    other_setup: Mapped[str] = mapped_column(String, nullable=True)
    key_photo_url: Mapped[str] = mapped_column(String, nullable=True)
    key_photo_thumbnail_url: Mapped[str] = mapped_column(String, nullable=True)
    cell_component_name: Mapped[str] = mapped_column(String, nullable=True)
    cell_component_id: Mapped[str] = mapped_column(String, nullable=True)
    deposition_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    release_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_modified_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    dataset_publications: Mapped[str] = mapped_column(String, nullable=True)
    related_database_entries: Mapped[str] = mapped_column(String, nullable=True)
    s3_prefix: Mapped[str] = mapped_column(String, nullable=False)
    https_prefix: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[float] = mapped_column(Float, nullable=True)
    id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, primary_key=True)
