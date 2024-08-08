"""
SQLAlchemy database model for AnnotationShape

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
from support.enums import annotation_file_shape_type_enum
from platformics.database.models.file import File

if TYPE_CHECKING:
    from platformics.database.models.file import File
    from database.models.annotation import Annotation
    from database.models.annotation_file import AnnotationFile

    ...
else:
    File = "File"
    Annotation = "Annotation"
    AnnotationFile = "AnnotationFile"
    ...


class AnnotationShape(Base):
    __tablename__ = "annotation_shape"
    __mapper_args__ = {"polymorphic_identity": __tablename__, "polymorphic_load": "inline"}

    annotation_id: Mapped[int] = mapped_column(Integer, ForeignKey("annotation.id"), nullable=True, index=True)
    annotation: Mapped["Annotation"] = relationship(
        "Annotation",
        foreign_keys=annotation_id,
        back_populates="annotation_shapes",
    )
    annotation_files: Mapped[list[AnnotationFile]] = relationship(
        "AnnotationFile",
        back_populates="annotation_shape",
        uselist=True,
        foreign_keys="AnnotationFile.annotation_shape_id",
    )
    shape_type: Mapped[annotation_file_shape_type_enum] = mapped_column(
        Enum(annotation_file_shape_type_enum, native_enum=False), nullable=True
    )
    id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, autoincrement=True, primary_key=True)