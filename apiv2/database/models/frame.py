"""
SQLAlchemy database model for Frame

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/database/models/class_name.py.j2 instead.
"""

from typing import TYPE_CHECKING

from platformics.database.models.base import Base
from platformics.database.models.file import File
from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from database.models.deposition import Deposition
    from database.models.per_section_parameters import PerSectionParameters
    from database.models.run import Run
    from platformics.database.models.file import File

    ...
else:
    File = "File"
    Deposition = "Deposition"
    PerSectionParameters = "PerSectionParameters"
    Run = "Run"
    ...


class Frame(Base):
    __tablename__ = "frame"
    __mapper_args__ = {"polymorphic_identity": __tablename__, "polymorphic_load": "inline"}

    deposition_id: Mapped[int] = mapped_column(Integer, ForeignKey("deposition.id"), nullable=True, index=True)
    deposition: Mapped["Deposition"] = relationship(
        "Deposition",
        foreign_keys=deposition_id,
        back_populates="frames",
    )
    per_section_parameters: Mapped[list[PerSectionParameters]] = relationship(
        "PerSectionParameters",
        back_populates="frame",
        uselist=True,
        foreign_keys="PerSectionParameters.frame_id",
    )
    run_id: Mapped[int] = mapped_column(Integer, ForeignKey("run.id"), nullable=True, index=True)
    run: Mapped["Run"] = relationship(
        "Run",
        foreign_keys=run_id,
        back_populates="frames",
    )
    raw_angle: Mapped[float] = mapped_column(Float, nullable=False)
    acquisition_order: Mapped[int] = mapped_column(Integer, nullable=True)
    dose: Mapped[float] = mapped_column(Float, nullable=False)
    is_gain_corrected: Mapped[bool] = mapped_column(Boolean, nullable=True)
    s3_gain_file: Mapped[str] = mapped_column(String, nullable=True)
    https_gain_file: Mapped[str] = mapped_column(String, nullable=True)
    s3_prefix: Mapped[str] = mapped_column(String, nullable=False)
    https_prefix: Mapped[str] = mapped_column(String, nullable=False)
    id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, autoincrement=True, primary_key=True)