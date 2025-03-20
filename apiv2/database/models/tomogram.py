"""
SQLAlchemy database model for Tomogram

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
from support.enums import fiducial_alignment_status_enum, tomogram_reconstruction_method_enum, tomogram_processing_enum
from platformics.database.models.file import File

if TYPE_CHECKING:
    from platformics.database.models.file import File
    from database.models.alignment import Alignment
    from database.models.tomogram_author import TomogramAuthor
    from database.models.deposition import Deposition
    from database.models.run import Run
    from database.models.tomogram_voxel_spacing import TomogramVoxelSpacing

    ...
else:
    File = "File"
    Alignment = "Alignment"
    TomogramAuthor = "TomogramAuthor"
    Deposition = "Deposition"
    Run = "Run"
    TomogramVoxelSpacing = "TomogramVoxelSpacing"
    ...


class Tomogram(Base):
    __tablename__ = "tomogram"
    __mapper_args__ = {"polymorphic_identity": __tablename__, "polymorphic_load": "inline"}

    alignment_id: Mapped[int] = mapped_column(Integer, ForeignKey("alignment.id"), nullable=True, index=True)
    alignment: Mapped["Alignment"] = relationship(
        "Alignment",
        foreign_keys=alignment_id,
        back_populates="tomograms",
    )
    authors: Mapped[list[TomogramAuthor]] = relationship(
        "TomogramAuthor",
        back_populates="tomogram",
        uselist=True,
        foreign_keys="TomogramAuthor.tomogram_id",
        cascade="all, delete-orphan",
    )
    deposition_id: Mapped[int] = mapped_column(Integer, ForeignKey("deposition.id"), nullable=False, index=True)
    deposition: Mapped["Deposition"] = relationship(
        "Deposition",
        foreign_keys=deposition_id,
        back_populates="tomograms",
    )
    run_id: Mapped[int] = mapped_column(Integer, ForeignKey("run.id"), nullable=True, index=True)
    run: Mapped["Run"] = relationship(
        "Run",
        foreign_keys=run_id,
        back_populates="tomograms",
    )
    tomogram_voxel_spacing_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tomogram_voxel_spacing.id"), nullable=True, index=True
    )
    tomogram_voxel_spacing: Mapped["TomogramVoxelSpacing"] = relationship(
        "TomogramVoxelSpacing",
        foreign_keys=tomogram_voxel_spacing_id,
        back_populates="tomograms",
    )
    name: Mapped[str] = mapped_column(String, nullable=True)
    size_x: Mapped[int] = mapped_column(Integer, nullable=False)
    size_y: Mapped[int] = mapped_column(Integer, nullable=False)
    size_z: Mapped[int] = mapped_column(Integer, nullable=False)
    voxel_spacing: Mapped[float] = mapped_column(Float, nullable=False)
    fiducial_alignment_status: Mapped[fiducial_alignment_status_enum] = mapped_column(
        Enum(fiducial_alignment_status_enum, native_enum=False), nullable=False
    )
    reconstruction_method: Mapped[tomogram_reconstruction_method_enum] = mapped_column(
        Enum(tomogram_reconstruction_method_enum, native_enum=False), nullable=False
    )
    processing: Mapped[tomogram_processing_enum] = mapped_column(
        Enum(tomogram_processing_enum, native_enum=False), nullable=False
    )
    tomogram_version: Mapped[float] = mapped_column(Float, nullable=True)
    processing_software: Mapped[str] = mapped_column(String, nullable=True)
    reconstruction_software: Mapped[str] = mapped_column(String, nullable=False)
    is_portal_standard: Mapped[bool] = mapped_column(Boolean, nullable=True)
    is_author_submitted: Mapped[bool] = mapped_column(Boolean, nullable=True)
    is_visualization_default: Mapped[bool] = mapped_column(Boolean, nullable=True)
    s3_omezarr_dir: Mapped[str] = mapped_column(String, nullable=True)
    https_omezarr_dir: Mapped[str] = mapped_column(String, nullable=True)
    file_size_omezarr: Mapped[float] = mapped_column(Float, nullable=True)
    s3_mrc_file: Mapped[str] = mapped_column(String, nullable=True)
    https_mrc_file: Mapped[str] = mapped_column(String, nullable=True)
    file_size_mrc: Mapped[float] = mapped_column(Float, nullable=True)
    scale0_dimensions: Mapped[str] = mapped_column(String, nullable=True)
    scale1_dimensions: Mapped[str] = mapped_column(String, nullable=True)
    scale2_dimensions: Mapped[str] = mapped_column(String, nullable=True)
    ctf_corrected: Mapped[bool] = mapped_column(Boolean, nullable=True)
    offset_x: Mapped[int] = mapped_column(Integer, nullable=False)
    offset_y: Mapped[int] = mapped_column(Integer, nullable=False)
    offset_z: Mapped[int] = mapped_column(Integer, nullable=False)
    key_photo_url: Mapped[str] = mapped_column(String, nullable=True)
    key_photo_thumbnail_url: Mapped[str] = mapped_column(String, nullable=True)
    neuroglancer_config: Mapped[str] = mapped_column(String, nullable=True)
    publications: Mapped[str] = mapped_column(String, nullable=True)
    related_database_entries: Mapped[str] = mapped_column(String, nullable=True)
    id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, autoincrement=True, primary_key=True)
    deposition_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    release_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_modified_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)
