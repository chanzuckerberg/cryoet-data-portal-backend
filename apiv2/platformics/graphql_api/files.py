"""
GraphQL types, queries, and mutations for files.
"""

import datetime
import json
import tempfile
import typing
import uuid
from dataclasses import dataclass

import sqlalchemy as sa
import strawberry
import uuid6
from fastapi import Depends
from mypy_boto3_s3.client import S3Client
from mypy_boto3_sts.client import STSClient
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from strawberry.scalars import JSON
from strawberry.types import Info
from typing_extensions import TypedDict

import platformics.database.models as db
from platformics.graphql_api.core.deps import (
    get_authz_client,
    get_db_session,
    get_s3_client,
    get_settings,
    get_sts_client,
    require_auth_principal,
    require_system_user,
)
from platformics.graphql_api.core.query_builder import get_db_rows
from platformics.graphql_api.core.query_input_types import (
    EnumComparators,
    IntComparators,
    StrComparators,
    UUIDComparators,
)
from platformics.graphql_api.core.strawberry_extensions import DependencyExtension
from platformics.security.authorization import AuthzAction, AuthzClient, Principal
from platformics.settings import APISettings
from platformics.support import sqlalchemy_helpers
from platformics.support.file_enums import FileAccessProtocol, FileStatus
from platformics.support.format_handlers import get_validator

FILE_TEMPORARY_PREFIX = "tmp"
FILE_CONCATENATION_MAX = 200
FILE_CONCATENATION_MAX_SIZE = 50e3  # SARS-CoV-2 genome is ~30kbp
FILE_CONCATENATION_PREFIX = f"{FILE_TEMPORARY_PREFIX}/concatenated-files"
FILE_CONTENTS_MAX_SIZE = 1e6  # 1MB
UPLOADS_PREFIX = "uploads"

# ------------------------------------------------------------------------------
# Utility types/inputs
# ------------------------------------------------------------------------------


@strawberry.type
@dataclass
class SignedURL:
    """
    Signed URLs for downloading a file from S3.
    """

    url: str
    protocol: str
    method: str
    expiration: int
    fields: typing.Optional[JSON] = None  # type: ignore


@strawberry.type
@dataclass
class MultipartUploadCredentials:
    """
    STS token for uploading a file to S3.
    """

    protocol: str
    namespace: str
    path: str
    access_key_id: str
    secret_access_key: str
    session_token: str
    expiration: str


# Define graphQL input types so we can pass a "file" JSON to mutations.
# Keep them separate so we can control which fields are required.
@strawberry.input()
class FileUpload:
    """
    GraphQL input type for uploading a file.
    """

    name: str
    file_format: str
    compression_type: typing.Optional[str] = None


@strawberry.input()
class FileCreate:
    """
    GraphQL input type for creating a File object based on an existing S3 file (no upload).
    """

    name: str
    file_format: str
    compression_type: typing.Optional[str] = None
    protocol: FileAccessProtocol
    namespace: str
    path: str


# ------------------------------------------------------------------------------
# Main types/inputs
# ------------------------------------------------------------------------------


@strawberry.type
class File:
    """
    GraphQL File type and fields.
    """

    id: strawberry.ID
    entity_id: strawberry.ID
    entity_field_name: str
    entity_class_name: str
    status: FileStatus
    protocol: FileAccessProtocol
    namespace: str
    path: str
    file_format: str
    compression_type: typing.Optional[int] = None
    size: typing.Optional[int] = None
    upload_error: typing.Optional[str] = None
    created_at: datetime.datetime
    updated_at: typing.Optional[datetime.datetime] = None

    @strawberry.field(extensions=[DependencyExtension()])
    def download_link(
        self,
        expiration: int = 3600,
        s3_client: S3Client = Depends(get_s3_client),
    ) -> typing.Optional[SignedURL]:
        """
        Generate a signed URL for downloading a file from S3.
        """
        if not self.path:  # type: ignore
            return None
        params = {"Bucket": self.namespace, "Key": self.path}
        url = s3_client.generate_presigned_url(ClientMethod="get_object", Params=params, ExpiresIn=expiration)
        return SignedURL(url=url, protocol="https", method="get", expiration=expiration)

    @strawberry.field(extensions=[DependencyExtension()])
    def contents(
        self,
        s3_client: S3Client = Depends(get_s3_client),
    ) -> str | None:
        """
        Utility function to get file contents of small files.
        """
        if not self.path or not self.size:
            return None
        if self.size > FILE_CONTENTS_MAX_SIZE:
            raise Exception(f"Cannot download files larger than {FILE_CONTENTS_MAX_SIZE} bytes")
        contents = s3_client.get_object(Bucket=self.namespace, Key=self.path)["Body"].read().decode("utf-8")
        return contents


@strawberry.type
class MultipartUploadResponse:
    """
    Return type for the uploadFile mutation.
    """

    credentials: MultipartUploadCredentials
    file: File


@strawberry.input
class FileWhereClause(TypedDict):
    """
    Supported where clause fields for the File type.
    """

    id: typing.Optional[UUIDComparators]
    entity_id: typing.Optional[UUIDComparators]
    entity_field_name: typing.Optional[StrComparators]
    entity_class_name: typing.Optional[StrComparators]
    status: typing.Optional[EnumComparators[FileStatus]]
    protocol: typing.Optional[StrComparators]
    namespace: typing.Optional[StrComparators]
    path: typing.Optional[StrComparators]
    file_format: typing.Optional[StrComparators]
    compression_type: typing.Optional[StrComparators]
    size: typing.Optional[IntComparators]


# ------------------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------------------


async def validate_file(
    file: db.File,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    s3_client: S3Client = Depends(get_s3_client),
) -> None:
    """
    Utility function to validate a file against its file format.
    """
    validator = get_validator(format=file.file_format)

    # Validate data
    try:
        validator(s3_client, file.namespace, file.path).validate()

        file_size = s3_client.head_object(Bucket=file.namespace, Key=file.path)["ContentLength"]
    except:  # noqa
        file.status = FileStatus.FAILED
    else:
        file.status = FileStatus.SUCCESS
        file.size = file_size

    file.updated_at = func.now()
    await session.commit()


def generate_multipart_upload_token(
    new_file: db.File,
    expiration: int = 3600,
    sts_client: STSClient = Depends(get_sts_client),
) -> MultipartUploadCredentials:
    """
    Utility function to generate an STS token for multipart upload.
    """
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowSampleUploads",
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:CreateMultipartUpload",
                    "s3:AbortMultipartUpload",
                    "s3:ListMultipartUploadParts",
                ],
                "Resource": f"arn:aws:s3:::{new_file.namespace}/{new_file.path}",
            },
        ],
    }

    # Generate an STS token to allow users to
    token_name = f"file-upload-token-{uuid6.uuid7()}"
    creds = sts_client.get_federation_token(Name=token_name, Policy=json.dumps(policy), DurationSeconds=expiration)

    return MultipartUploadCredentials(
        protocol="s3",
        namespace=new_file.namespace,
        path=new_file.path,
        access_key_id=creds["Credentials"]["AccessKeyId"],
        secret_access_key=creds["Credentials"]["SecretAccessKey"],
        session_token=creds["Credentials"]["SessionToken"],
        expiration=creds["Credentials"]["Expiration"].isoformat(),
    )


# ------------------------------------------------------------------------------
# Mutations
# ------------------------------------------------------------------------------


@strawberry.mutation(extensions=[DependencyExtension()])
async def mark_upload_complete(
    file_id: strawberry.ID,
    principal: Principal = Depends(require_auth_principal),
    authz_client: AuthzClient = Depends(get_authz_client),
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    s3_client: S3Client = Depends(get_s3_client),
) -> db.File:
    """
    Once a file is uploaded, the front-end should make a markUploadComplete mutation
    to mark the file as ready for pipeline analysis.
    """

    # Get the type of entity that the file is related to
    file_row = (await session.execute(sa.select(db.File).where(db.File.id == file_id))).scalars().one()
    entity_class = sqlalchemy_helpers.get_orm_class_by_name(file_row.entity_class_name)
    mapper = inspect(entity_class)

    # See if we actually have access to that file.
    query = authz_client.get_resource_query(
        principal,
        AuthzAction.UPDATE,
        db.File,
        mapper.relationships.get(file_row.entity_field_name),
    )
    query = query.filter(db.File.id == file_id)
    file = (await session.execute(query)).scalars().one()
    if not file:
        raise Exception("NOT FOUND!")  # TODO: How do we raise sane errors in our api?

    await validate_file(file, session, s3_client)
    return file


# Need to create separate mutations because they return different types.
# Strawberry is unhappy with a mutation returning a union type.
@strawberry.mutation(extensions=[DependencyExtension()])
async def create_file(
    info: Info,
    entity_id: strawberry.ID,
    entity_field_name: str,
    entity_class_name: str,
    file: FileCreate,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    s3_client: S3Client = Depends(get_s3_client),
    sts_client: STSClient = Depends(get_sts_client),
    settings: APISettings = Depends(get_settings),
) -> db.File:
    """
    Create a file object based on an existing S3 file (no upload).
    """
    # Since user can specify an arbitrary path, make sure only a system user can do this.
    require_system_user(principal)
    new_file = await create_or_upload_file(
        entity_id,
        entity_field_name,
        entity_class_name,
        file,
        -1,
        session,
        authz_client,
        principal,
        s3_client,
        sts_client,
        settings,
    )
    assert isinstance(new_file, db.File)  # reassure mypy that we're returning the right type
    return new_file


@strawberry.mutation(extensions=[DependencyExtension()])
async def upload_file(
    info: Info,
    entity_id: strawberry.ID,
    entity_field_name: str,
    entity_class_name: str,
    file: FileUpload,
    expiration: int = 3600,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    s3_client: S3Client = Depends(get_s3_client),
    sts_client: STSClient = Depends(get_sts_client),
    settings: APISettings = Depends(get_settings),
) -> MultipartUploadResponse:
    """
    Create a file object and generate an STS token for multipart upload.
    """
    response = await create_or_upload_file(
        entity_id,
        entity_field_name,
        entity_class_name,
        file,
        expiration,
        session,
        authz_client,
        principal,
        s3_client,
        sts_client,
        settings,
    )
    assert isinstance(response, MultipartUploadResponse)  # reassure mypy that we're returning the right type
    return response


async def create_or_upload_file(
    entity_id: strawberry.ID,
    entity_field_name: str,
    entity_class_name: str,
    file: FileCreate | FileUpload,
    expiration: int = 3600,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    s3_client: S3Client = Depends(get_s3_client),
    sts_client: STSClient = Depends(get_sts_client),
    settings: APISettings = Depends(get_settings),
) -> db.File | MultipartUploadResponse:
    """
    Utility function for creating a File object, whether for upload or for linking existing files.
    """
    # Basic validation
    if "/" in file.name:
        raise Exception("File name should not contain /")

    # Fetch the entity if have access to it
    entity_class = sqlalchemy_helpers.get_orm_class_by_name(entity_class_name)
    query = authz_client.get_resource_query(principal, AuthzAction.UPDATE, entity_class)
    _, pk_col = sqlalchemy_helpers.get_primary_key(entity_class)
    query = query.filter(pk_col == entity_id)
    entity = (await session.execute(query)).scalars().one()
    if not entity:
        raise Exception("Entity not found")

    # Does that entity type have a column for storing a file ID?
    entity_property_name = f"{entity_field_name}_id"
    if not hasattr(entity, entity_property_name):
        raise Exception(f"This entity does not have a corresponding file of type {entity_field_name}")

    # Unlink the File(s) currently connected to this entity (only commit to DB once add the new File below)
    query = authz_client.get_resource_query(principal, AuthzAction.UPDATE, db.File, entity_class)
    query = query.filter(db.File.entity_id == entity_id)
    query = query.filter(db.File.entity_field_name == entity_field_name)
    current_files = (await session.execute(query)).scalars().all()
    for current_file in current_files:
        current_file.entity_id = None

    # Set file parameters based on user inputs
    file_id = uuid6.uuid7()
    if isinstance(file, FileUpload):
        file_protocol = settings.DEFAULT_UPLOAD_PROTOCOL
        file_namespace = settings.DEFAULT_UPLOAD_BUCKET
        file_path = f"{settings.OUTPUT_S3_PREFIX}/{UPLOADS_PREFIX}/{file_id}/{file.name}"
    else:
        file_protocol = file.protocol  # type: ignore
        file_namespace = file.namespace
        file_path = file.path

    # Create a new file record
    new_file = db.File(
        id=file_id,
        entity_id=entity_id,
        entity_field_name=entity_field_name,
        entity_class_name=entity_class_name,
        protocol=file_protocol,
        namespace=file_namespace,
        path=file_path,
        file_format=file.file_format,
        compression_type=file.compression_type,
        status=FileStatus.PENDING,
    )
    # Save file to db first
    session.add(new_file)
    await session.commit()
    # Then update entity with file ID (if do both in one transaction, it will fail because of foreign key constraint)
    setattr(entity, entity_property_name, new_file.id)
    await session.commit()

    # If file already exists, validate it
    if isinstance(file, FileCreate):
        await validate_file(new_file, session, s3_client)
        return new_file

    # If new file, create an STS token for multipart upload
    else:
        return MultipartUploadResponse(
            file=new_file,  # type: ignore
            credentials=generate_multipart_upload_token(new_file, expiration, sts_client),
        )


@strawberry.mutation(extensions=[DependencyExtension()])
async def upload_temporary_file(
    expiration: int = 3600,
    principal: Principal = Depends(require_auth_principal),
    sts_client: STSClient = Depends(get_sts_client),
    settings: APISettings = Depends(get_settings),
) -> MultipartUploadResponse:
    """
    Generate upload tokens to upload files to S3 for temporary use (e.g. when export CGs to Nextclade, user can upload a
    tree file that is sent to Nextclade and then not used in the app later). Only system users can do this.
    """
    require_system_user(principal)
    # Create a File object in memory because that's what `generate_multipart_upload_token` expects
    # but this doesn't create a row in the File table.
    new_file = db.File(namespace=settings.DEFAULT_UPLOAD_BUCKET, path=f"{FILE_TEMPORARY_PREFIX}/{uuid6.uuid7()}")
    return MultipartUploadResponse(
        file=new_file,  # type: ignore
        credentials=generate_multipart_upload_token(new_file, expiration, sts_client),
    )


@strawberry.mutation(extensions=[DependencyExtension()])
async def concatenate_files(
    ids: typing.Sequence[uuid.UUID],
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    s3_client: S3Client = Depends(get_s3_client),
    settings: APISettings = Depends(get_settings),
) -> SignedURL:
    """
    Concatenate file contents synchronously (as opposed to the asynchronous bulk-download concatenate pipeline).
    Only use for small files e.g. for exporting small CG FASTAs to Nextclade, where input file IDs is an array of
    ConsensusGenome.sequence.id. We only support doing so on SARS-CoV-2 FASTAs (~30kbp genome)
    so it's ok to do synchronously.
    """
    if len(ids) > FILE_CONCATENATION_MAX:
        raise Exception(f"Cannot concatenate more than {FILE_CONCATENATION_MAX} files")

    # Get files in question if have access to them
    where = {"id": {"_in": ids}, "status": {"_eq": FileStatus.SUCCESS}}
    files = await get_db_rows(db.File, session, authz_client, principal, where, [])
    if len(files) < 2:
        raise Exception("Need at least 2 valid files to concatenate")
    for file in files:
        if file.size > FILE_CONCATENATION_MAX_SIZE:
            raise Exception("Cannot concatenate files larger than 1MB")

    # Concatenate files (tmp files are automatically deleted when closed)
    with tempfile.NamedTemporaryFile() as file_concatenated:
        with open(file_concatenated.name, "ab") as fp_concat:  # noqa: ASYNC101
            for file in files:
                # Download file locally and append it
                with tempfile.NamedTemporaryFile() as file_temp:
                    s3_client.download_file(file.namespace, file.path, file_temp.name)
                    with open(file_temp.name, "rb") as fp_temp:  # noqa: ASYNC101
                        fp_concat.write(fp_temp.read())
        # Upload to S3
        path = f"{FILE_CONCATENATION_PREFIX}/{uuid6.uuid7()}"
        s3_client.upload_file(file_concatenated.name, file.namespace, path)

    # Return signed URL
    expiration = 36000
    url = s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": settings.DEFAULT_UPLOAD_BUCKET, "Key": path},
        ExpiresIn=expiration,
    )
    return SignedURL(url=url, protocol="https", method="get", expiration=expiration)
