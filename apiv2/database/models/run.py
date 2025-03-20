"""
SQLAlchemy database model for Run

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
    from database.models.alignment import Alignment
    from database.models.annotation import Annotation
    from database.models.dataset import Dataset
    from database.models.frame import Frame
    from database.models.gain_file import GainFile
    from database.models.frame_acquisition_file import FrameAcquisitionFile
    from database.models.per_section_parameters import PerSectionParameters
    from database.models.tiltseries import Tiltseries
    from database.models.tomogram_voxel_spacing import TomogramVoxelSpacing
    from database.models.tomogram import Tomogram

    ...
else:
    File = "File"
    Alignment = "Alignment"
    Annotation = "Annotation"
    Dataset = "Dataset"
    Frame = "Frame"
    GainFile = "GainFile"
    FrameAcquisitionFile = "FrameAcquisitionFile"
    PerSectionParameters = "PerSectionParameters"
    Tiltseries = "Tiltseries"
    TomogramVoxelSpacing = "TomogramVoxelSpacing"
    Tomogram = "Tomogram"
    ...


class Run(Base):
    __tablename__ = "run"
    __mapper_args__ = {"polymorphic_identity": __tablename__, "polymorphic_load": "inline"}

    alignments: Mapped[list[Alignment]] = relationship(
        "Alignment", back_populates="run", uselist=True, foreign_keys="Alignment.run_id", cascade="all, delete-orphan"
    )
    annotations: Mapped[list[Annotation]] = relationship(
        "Annotation", back_populates="run", uselist=True, foreign_keys="Annotation.run_id", cascade="all, delete-orphan"
    )
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset.id"), nullable=False, index=True)
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        foreign_keys=dataset_id,
        back_populates="runs",
    )
    frames: Mapped[list[Frame]] = relationship(
        "Frame", back_populates="run", uselist=True, foreign_keys="Frame.run_id", cascade="all, delete-orphan"
    )
    gain_files: Mapped[list[GainFile]] = relationship(
        "GainFile", back_populates="run", uselist=True, foreign_keys="GainFile.run_id", cascade="all, delete-orphan"
    )
    frame_acquisition_files: Mapped[list[FrameAcquisitionFile]] = relationship(
        "FrameAcquisitionFile",
        back_populates="run",
        uselist=True,
        foreign_keys="FrameAcquisitionFile.run_id",
        cascade="all, delete-orphan",
    )
    per_section_parameters: Mapped[list[PerSectionParameters]] = relationship(
        "PerSectionParameters",
        back_populates="run",
        uselist=True,
        foreign_keys="PerSectionParameters.run_id",
        cascade="all, delete-orphan",
    )
    tiltseries: Mapped[list[Tiltseries]] = relationship(
        "Tiltseries", back_populates="run", uselist=True, foreign_keys="Tiltseries.run_id", cascade="all, delete-orphan"
    )
    tomogram_voxel_spacings: Mapped[list[TomogramVoxelSpacing]] = relationship(
        "TomogramVoxelSpacing",
        back_populates="run",
        uselist=True,
        foreign_keys="TomogramVoxelSpacing.run_id",
        cascade="all, delete-orphan",
    )
    tomograms: Mapped[list[Tomogram]] = relationship(
        "Tomogram", back_populates="run", uselist=True, foreign_keys="Tomogram.run_id", cascade="all, delete-orphan"
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    s3_prefix: Mapped[str] = mapped_column(String, nullable=False)
    https_prefix: Mapped[str] = mapped_column(String, nullable=False)
    id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, autoincrement=True, primary_key=True)
