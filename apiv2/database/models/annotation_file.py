"""
Auto-generated by running `make codegen`. Do not edit!
Make changes to the template platformics/codegen/templates/database/models/class_name.py.j2 instead.

SQLAlchemy database model for AnnotationFile
"""

from typing import TYPE_CHECKING

from platformics.database.models.base import Base
from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from support.enums import annotation_file_source_enum

if TYPE_CHECKING:
    from database.models.alignment import Alignment
    from database.models.annotation_shape import AnnotationShape
    from database.models.tomogram_voxel_spacing import TomogramVoxelSpacing

    ...
else:
    Alignment = "Alignment"
    AnnotationShape = "AnnotationShape"
    TomogramVoxelSpacing = "TomogramVoxelSpacing"
    ...


class AnnotationFile(Base):
    __tablename__ = "annotation_file"
    __mapper_args__ = {"polymorphic_identity": __tablename__, "polymorphic_load": "inline"}

    alignment_id: Mapped[int] = mapped_column(Integer, ForeignKey("alignment.id"), nullable=True, index=True)
    alignment: Mapped["Alignment"] = relationship(
        "Alignment",
        foreign_keys=alignment_id,
        back_populates="annotation_files",
    )
    annotation_shape_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("annotation_shape.id"), nullable=True, index=True,
    )
    annotation_shape: Mapped["AnnotationShape"] = relationship(
        "AnnotationShape",
        foreign_keys=annotation_shape_id,
        back_populates="annotation_files",
    )
    tomogram_voxel_spacing_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tomogram_voxel_spacing.id"), nullable=True, index=True,
    )
    tomogram_voxel_spacing: Mapped["TomogramVoxelSpacing"] = relationship(
        "TomogramVoxelSpacing",
        foreign_keys=tomogram_voxel_spacing_id,
        back_populates="annotation_files",
    )
    format: Mapped[str] = mapped_column(String, nullable=False)
    s3_path: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[float] = mapped_column(Float, nullable=True)
    https_path: Mapped[str] = mapped_column(String, nullable=False)
    is_visualization_default: Mapped[bool] = mapped_column(Boolean, nullable=True)
    source: Mapped[annotation_file_source_enum] = mapped_column(
        Enum(annotation_file_source_enum, native_enum=False), nullable=True,
    )
    id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, autoincrement=True, primary_key=True)
