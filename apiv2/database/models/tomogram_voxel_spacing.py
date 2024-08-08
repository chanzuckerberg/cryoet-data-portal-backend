"""
SQLAlchemy database model for TomogramVoxelSpacing

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
    from database.models.annotation_file import AnnotationFile
    from database.models.run import Run
    from database.models.tomogram import Tomogram

    ...
else:
    File = "File"
    AnnotationFile = "AnnotationFile"
    Run = "Run"
    Tomogram = "Tomogram"
    ...


class TomogramVoxelSpacing(Base):
    __tablename__ = "tomogram_voxel_spacing"
    __mapper_args__ = {"polymorphic_identity": __tablename__, "polymorphic_load": "inline"}

    annotation_files: Mapped[list[AnnotationFile]] = relationship(
        "AnnotationFile",
        back_populates="tomogram_voxel_spacing",
        uselist=True,
        foreign_keys="AnnotationFile.tomogram_voxel_spacing_id",
    )
    run_id: Mapped[int] = mapped_column(Integer, ForeignKey("run.id"), nullable=True, index=True)
    run: Mapped["Run"] = relationship(
        "Run",
        foreign_keys=run_id,
        back_populates="tomogram_voxel_spacings",
    )
    tomograms: Mapped[list[Tomogram]] = relationship(
        "Tomogram",
        back_populates="tomogram_voxel_spacing",
        uselist=True,
        foreign_keys="Tomogram.tomogram_voxel_spacing_id",
    )
    voxel_spacing: Mapped[float] = mapped_column(Float, nullable=False)
    s3_prefix: Mapped[str] = mapped_column(String, nullable=False)
    https_prefix: Mapped[str] = mapped_column(String, nullable=False)
    id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, autoincrement=True, primary_key=True)