import typing

import boto3
from botocore.client import Config
from fastapi import Depends
from mypy_boto3_s3.client import S3Client
from mypy_boto3_sts.client import STSClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from platformics.database.connect import AsyncDB, init_async_db
from platformics.graphql_api.core.error_handler import PlatformicsError
from platformics.security.authorization import AuthzClient, Principal, hydrate_auth_principal
from platformics.settings import APISettings


def get_settings(request: Request) -> APISettings:
    """Get the settings object from the app state"""
    return request.app.state.settings


async def get_engine(
    settings: APISettings = Depends(get_settings),
) -> typing.AsyncGenerator[AsyncDB, None]:
    """Wrap resolvers in a DB engine"""
    engine = init_async_db(settings.DB_URI, echo=settings.DB_ECHO)
    try:
        yield engine
    finally:
        pass


async def get_db_session(
    engine: AsyncDB = Depends(get_engine),
) -> typing.AsyncGenerator[AsyncSession, None]:
    """Wrap resolvers in a sqlalchemy-compatible db session"""
    session = engine.session()
    try:
        yield session
    finally:
        await session.close()  # type: ignore


def get_authz_client(settings: APISettings = Depends(get_settings)) -> AuthzClient:
    return AuthzClient(settings=settings)


def get_user_token(request: Request) -> typing.Optional[str]:
    auth_header = request.headers.get("authorization")
    parts = []
    if auth_header:
        parts = auth_header.split()
    if not auth_header or len(parts) != 2:
        return None
    if parts[0].lower() != "bearer":
        return None

    return parts[1]


def get_auth_principal(
    request: Request,
    settings: APISettings = Depends(get_settings),
    user_token: typing.Optional[str] = Depends(get_user_token),
) -> typing.Optional[Principal]:
    try:
        principal = hydrate_auth_principal(settings, user_token)
    except:
        raise PlatformicsError("Unauthorized")
    return principal


def require_auth_principal(
    principal: typing.Optional[Principal] = Depends(get_auth_principal),
) -> Principal:
    if not principal:
        raise PlatformicsError("Unauthorized")
    return principal


def is_system_user(principal: Principal = Depends(require_auth_principal)) -> bool:
    if principal.attr.get("service_identity"):
        return True
    return False


def require_system_user(principal: Principal = Depends(require_auth_principal)) -> None:
    if principal.attr.get("service_identity"):
        return None
    raise PlatformicsError("Unauthorized")


def get_s3_client(
    settings: APISettings = Depends(get_settings),
) -> S3Client:
    return boto3.client(
        "s3",
        region_name=settings.AWS_REGION,
        endpoint_url=settings.BOTO_ENDPOINT_URL,
        config=Config(signature_version="s3v4"),
    )


def get_sts_client(
    settings: APISettings = Depends(get_settings),
) -> STSClient:
    return boto3.client("sts", region_name=settings.AWS_REGION, endpoint_url=settings.BOTO_ENDPOINT_URL)
