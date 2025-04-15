"""
Auto-generated by running `make codegen`. Do not edit!
Make changes to the template platformics/codegen/templates/database/models/class_name.py.j2 instead.

SQLAlchemy database model for GainFile
"""

from typing import TYPE_CHECKING

from platformics.database.models.base import Base
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from database.models.run import Run

    ...
else:
    Run = "Run"
    ...


class GainFile(Base):
    __tablename__ = "gain_file"
    __mapper_args__ = {"polymorphic_identity": __tablename__, "polymorphic_load": "inline"}

    run_id: Mapped[int] = mapped_column(Integer, ForeignKey("run.id"), nullable=False, index=True)
    run: Mapped["Run"] = relationship(
        "Run",
        foreign_keys=run_id,
        back_populates="gain_files",
    )
    s3_file_path: Mapped[str] = mapped_column(String, nullable=False)
    https_file_path: Mapped[str] = mapped_column(String, nullable=False)
    id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, autoincrement=True, primary_key=True)
