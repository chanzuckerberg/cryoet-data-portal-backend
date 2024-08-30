import datetime
import uuid
from typing import ClassVar

import uuid6
from mypy_boto3_s3.client import S3Client
from sqlalchemy import Column, DateTime, Enum, Integer, String, cast, event
from sqlalchemy.dialects.postgresql import UUID, VARCHAR
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapped, Mapper, mapped_column
from sqlalchemy.sql import func

from platformics.database.models.base import Base
from platformics.settings import APISettings
from platformics.support import sqlalchemy_helpers
from platformics.support.file_enums import FileAccessProtocol, FileStatus, FileUploadClient


class File(Base):
    __tablename__ = "file"
    _settings: ClassVar[APISettings | None] = None
    _s3_client: ClassVar[S3Client | None] = None

    @staticmethod
    def get_settings() -> APISettings:
        if not File._settings:
            raise Exception("Settings not defined in this environment")
        return File._settings

    @staticmethod
    def set_settings(settings: APISettings) -> None:
        File._settings = settings

    @staticmethod
    def get_s3_client() -> S3Client:
        if not File._s3_client:
            raise Exception("S3 client not defined in this environment")
        return File._s3_client

    @staticmethod
    def set_s3_client(s3_client: S3Client) -> None:
        File._s3_client = s3_client

    id: Column[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7)

    # TODO - the relationship between Entities and Files is currently being
    # configured in both directions: entities have {fieldname}_file_id fields,
    # *and* files have {entity_id, field_name, entity_table__name} fields to map
    # back to entities. This is necessary to support File objects inheriting the
    # access control properties of the Entity they're associated with.
    entity_id: Mapped[str] = mapped_column(String, nullable=False)
    entity_field_name: Mapped[str] = mapped_column(String, nullable=False)
    entity_class_name: Mapped[str] = mapped_column(String, nullable=False)

    # TODO: Changes here need to be reflected in graphql_api/files.py
    status: Mapped[FileStatus] = mapped_column(Enum(FileStatus, native_enum=False), nullable=False)
    protocol: Mapped[FileAccessProtocol] = mapped_column(Enum(FileAccessProtocol, native_enum=False), nullable=False)
    namespace: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)
    file_format: Mapped[str] = mapped_column(String, nullable=False)
    compression_type: Mapped[str] = mapped_column(String, nullable=True)
    size: Mapped[int] = mapped_column(Integer, nullable=True)
    upload_client: Mapped[FileUploadClient] = mapped_column(Enum(FileUploadClient, native_enum=False), nullable=True)
    upload_error: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)


@event.listens_for(File, "before_delete")
def before_delete(mapper: Mapper, connection: Connection, target: File) -> None:
    """
    Before deleting a File object, check whether we need to delete it from S3, and
    make sure to scrub the foreign keys in the Entity it's associated with.
    """
    table_files = target.__table__
    settings = File.get_settings()
    s3_client = File.get_s3_client()

    # If this file is managed by platformics, see if it needs to be deleted from S3
    if target.path.startswith(f"{settings.OUTPUT_S3_PREFIX}/") and target.protocol == FileAccessProtocol.s3:
        # Is this the last File object pointing to this path?
        files_pointing_to_same_path = connection.execute(
            table_files.select()
            .where(table_files.c.id != target.id)
            .where(table_files.c.protocol == target.protocol)
            .where(table_files.c.namespace == target.namespace)
            .where(table_files.c.path == target.path),
        )

        # If so, delete it from S3
        if len(list(files_pointing_to_same_path)) == 0:
            response = s3_client.delete_object(Bucket=target.namespace, Key=target.path)
            if response["ResponseMetadata"]["HTTPStatusCode"] != 204:
                raise Exception("Failed to delete file from S3")

    related_class = sqlalchemy_helpers.get_orm_class_by_name(target.entity_class_name)
    table_entity = related_class.__table__
    _, pk_col = sqlalchemy_helpers.get_primary_key(table_entity)

    # Finally, scrub the foreign keys in the related Entity
    values = {f"{target.entity_field_name}_id": None}
    # Modifying the target.entity directly does not save changes, we need to use `connection`
    connection.execute(
        table_entity.update().where(cast(pk_col, VARCHAR) == target.entity_id).values(**values),  # type: ignore
    )
