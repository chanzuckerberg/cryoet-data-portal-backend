"""
SQLAlchemy database model for AnnotationShape

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/database/models/class_name.py.j2 instead.
"""

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from support.enums import annotation_file_shape_type_enum

from platformics.database.models.base import Base
from platformics.database.models.file import File

if TYPE_CHECKING:
    from database.models.annotation import Annotation
    from database.models.annotation_file import AnnotationFile

    from platformics.database.models.file import File

    ...
else:
    File = "File"
    Annotation = "Annotation"
    AnnotationFile = "AnnotationFile"
    ...


class AnnotationShape(Base):
    __tablename__ = "annotation_shape"
    __mapper_args__ = {"polymorphic_identity": __tablename__, "polymorphic_load": "inline"}

    annotation_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("annotation.id"), nullable=True, index=True)
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
        cascade="all, delete-orphan",
    )
    shape_type: Mapped[annotation_file_shape_type_enum] = mapped_column(
        Enum(annotation_file_shape_type_enum, native_enum=False), nullable=True,
    )
    id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True, autoincrement=True, primary_key=True)
