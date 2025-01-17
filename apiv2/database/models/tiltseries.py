"""
SQLAlchemy database model for Tiltseries

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/database/models/class_name.py.j2 instead.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from support.enums import tiltseries_microscope_manufacturer_enum

from platformics.database.models.base import Base
from platformics.database.models.file import File

if TYPE_CHECKING:
    from database.models.alignment import Alignment
    from database.models.deposition import Deposition
    from database.models.run import Run

    from platformics.database.models.file import File

    ...
else:
    File = "File"
    Alignment = "Alignment"
    Run = "Run"
    Deposition = "Deposition"
    ...


class Tiltseries(Base):
    __tablename__ = "tiltseries"
    __mapper_args__ = {"polymorphic_identity": __tablename__, "polymorphic_load": "inline"}

    alignments: Mapped[list[Alignment]] = relationship(
        "Alignment",
        back_populates="tiltseries",
        uselist=True,
        foreign_keys="Alignment.tiltseries_id",
        cascade="all, delete-orphan",
    )
    run_id: Mapped[int] = mapped_column(Integer, ForeignKey("run.id"), nullable=False, index=True)
    run: Mapped["Run"] = relationship(
        "Run",
        foreign_keys=run_id,
        back_populates="tiltseries",
    )
    deposition_id: Mapped[int] = mapped_column(Integer, ForeignKey("deposition.id"), nullable=True, index=True)
    deposition: Mapped["Deposition"] = relationship(
        "Deposition",
        foreign_keys=deposition_id,
        back_populates="tiltseries",
    )
    s3_omezarr_dir: Mapped[str] = mapped_column(String, nullable=True)
    s3_mrc_file: Mapped[str] = mapped_column(String, nullable=True)
    https_omezarr_dir: Mapped[str] = mapped_column(String, nullable=True)
    https_mrc_file: Mapped[str] = mapped_column(String, nullable=True)
    s3_angle_list: Mapped[str] = mapped_column(String, nullable=True)
    https_angle_list: Mapped[str] = mapped_column(String, nullable=True)
    acceleration_voltage: Mapped[int] = mapped_column(Integer, nullable=False)
    spherical_aberration_constant: Mapped[float] = mapped_column(Float, nullable=False)
    microscope_manufacturer: Mapped[tiltseries_microscope_manufacturer_enum] = mapped_column(
        Enum(tiltseries_microscope_manufacturer_enum, native_enum=False), nullable=False,
    )
    microscope_model: Mapped[str] = mapped_column(String, nullable=False)
    microscope_energy_filter: Mapped[str] = mapped_column(String, nullable=False)
    microscope_phase_plate: Mapped[str] = mapped_column(String, nullable=True)
    microscope_image_corrector: Mapped[str] = mapped_column(String, nullable=True)
    microscope_additional_info: Mapped[str] = mapped_column(String, nullable=True)
    camera_manufacturer: Mapped[str] = mapped_column(String, nullable=False)
    camera_model: Mapped[str] = mapped_column(String, nullable=False)
    tilt_min: Mapped[float] = mapped_column(Float, nullable=False)
    tilt_max: Mapped[float] = mapped_column(Float, nullable=False)
    tilt_range: Mapped[float] = mapped_column(Float, nullable=False)
    tilt_step: Mapped[float] = mapped_column(Float, nullable=False)
    tilting_scheme: Mapped[str] = mapped_column(String, nullable=False)
    tilt_axis: Mapped[float] = mapped_column(Float, nullable=False)
    total_flux: Mapped[float] = mapped_column(Float, nullable=False)
    data_acquisition_software: Mapped[str] = mapped_column(String, nullable=False)
    related_empiar_entry: Mapped[str] = mapped_column(String, nullable=True)
    binning_from_frames: Mapped[float] = mapped_column(Float, nullable=True)
    tilt_series_quality: Mapped[int] = mapped_column(Integer, nullable=False)
    is_aligned: Mapped[bool] = mapped_column(Boolean, nullable=False)
    pixel_spacing: Mapped[float] = mapped_column(Float, nullable=False)
    aligned_tiltseries_binning: Mapped[int] = mapped_column(Integer, nullable=True)
    size_x: Mapped[int] = mapped_column(Integer, nullable=True)
    size_y: Mapped[int] = mapped_column(Integer, nullable=True)
    size_z: Mapped[int] = mapped_column(Integer, nullable=True)
    id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, autoincrement=True, primary_key=True)
