"""
Fixtures for API tests
"""

import json
import os
import typing
from typing import Optional
from platformics.graphql_api.core.error_handler import HandleErrors

import boto3
import pytest
import pytest_asyncio
from platformics.security.authorization import Principal
from fastapi import FastAPI
from httpx import AsyncClient
from moto import mock_s3
from mypy_boto3_s3.client import S3Client
from platformics.graphql_api.core.deps import (
    get_auth_principal,
    get_db_session,
    get_engine,
    get_s3_client,
    require_auth_principal,
)
from platformics.graphql_api.setup import get_app
from platformics.database.connect import AsyncDB, SyncDB, init_async_db, init_sync_db
from platformics.database.models.base import Base
from platformics.test_infra.factories.base import FileFactory, SessionStorage
from pytest_postgresql import factories
from pytest_postgresql.executor_noop import NoopExecutor
from pytest_postgresql.janitor import DatabaseJanitor
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from platformics.settings import APISettings
from platformics.graphql_api.setup import get_strawberry_config
from graphql_api.mutations import Mutation
from graphql_api.queries import Query
import strawberry

__all__ = [
    "gql_client",
    "moto_client",
    "GQLTestClient",
    "SessionStorage",
    "FileFactory",
]  # needed by tests


test_db: NoopExecutor = factories.postgresql_noproc(
    host=os.getenv("PLATFORMICS_DATABASE_HOST"), password=os.getenv("PLATFORMICS_DATABASE_PASSWORD")
)  # type: ignore


def get_db_uri(
    protocol: typing.Optional[str],
    db_user: typing.Optional[str],
    db_pass: typing.Optional[str],
    db_host: typing.Optional[str],
    db_port: typing.Optional[int],
    db_name: typing.Optional[str],
) -> str:
    """
    Utility function to generate database URI
    """
    db_uri = f"{protocol}://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    return db_uri


@pytest.fixture()
def sync_db(test_db: NoopExecutor) -> typing.Generator[SyncDB, None, None]:
    """
    Fixture to create a synchronous database connection
    """
    pg_host = test_db.host
    pg_port = test_db.port
    pg_user = test_db.user
    pg_password = test_db.password
    pg_db = test_db.dbname

    with DatabaseJanitor(pg_user, pg_host, pg_port, pg_db, test_db.version, pg_password):
        db: SyncDB = init_sync_db(
            get_db_uri(
                "postgresql+psycopg",
                db_host=pg_host,
                db_port=pg_port,
                db_user=pg_user,
                db_pass=pg_password,
                db_name=pg_db,
            )
        )
        Base.metadata.create_all(db.engine)
        yield db


@pytest_asyncio.fixture()
async def async_db(sync_db: SyncDB, test_db: NoopExecutor) -> typing.AsyncGenerator[AsyncDB, None]:
    """
    Fixture to create an asynchronous database connection
    """
    pg_host = test_db.host
    pg_port = test_db.port
    pg_user = test_db.user
    pg_password = test_db.password
    pg_db = test_db.dbname

    db = init_async_db(
        get_db_uri(
            "postgresql+asyncpg",  # "postgresql+asyncpg
            db_host=pg_host,
            db_port=pg_port,
            db_user=pg_user,
            db_pass=pg_password,
            db_name=pg_db,
        )
    )
    yield db


# When importing `gql_client`, it will use the `http_client` below, which uses the test schema
@pytest_asyncio.fixture()
async def http_client(api_test_schema: FastAPI) -> AsyncClient:
    return AsyncClient(app=api_test_schema, base_url="http://test-codegen")


class GQLTestClient:
    def __init__(self, http_client: AsyncClient):
        self.http_client = http_client

    async def query(
        self,
        query: str,
        user_id: Optional[int] = None,
        member_projects: Optional[list[int]] = None,
        owner_projects: Optional[list[int]] = None,
        viewer_projects: Optional[list[int]] = None,
        service_identity: Optional[str] = None,
    ) -> dict[str, typing.Any]:
        """
        Utility function for making GQL HTTP queries with authorization info.
        """
        if not user_id:
            user_id = 111
        if not owner_projects:
            owner_projects = []
        if not member_projects:
            member_projects = []
        if not viewer_projects:
            viewer_projects = []
        gql_headers = {
            "content-type": "application/json",
            "accept": "application/json",
            "user_id": str(user_id),
            "member_projects": json.dumps(member_projects),
            "owner_projects": json.dumps(owner_projects),
            "viewer_projects": json.dumps(viewer_projects),
            "service_identity": service_identity or "",
        }
        result = await self.http_client.post("/graphql", json={"query": query}, headers=gql_headers)
        return result.json()


@pytest_asyncio.fixture()
async def moto_client() -> typing.AsyncGenerator[S3Client, None]:
    """
    Create S3 Moto client.
    """
    mocks3 = mock_s3()
    mocks3.start()
    res = boto3.resource("s3")
    res.create_bucket(Bucket="local-bucket")
    res.create_bucket(Bucket="remote-bucket")
    yield boto3.client("s3")
    mocks3.stop()


async def patched_s3_client() -> typing.AsyncGenerator[S3Client, None]:
    yield boto3.client("s3")


@pytest_asyncio.fixture()
async def gql_client(http_client: AsyncClient) -> GQLTestClient:
    """
    Create a GQL client.
    """
    client = GQLTestClient(http_client)
    return client


async def patched_authprincipal(request: Request) -> Principal:
    """
    Create a Principal object from request headers.
    """
    user_id = request.headers.get("user_id")
    if not user_id:
        raise Exception("user_id not found in request headers")
    principal = Principal(
        user_id,
        roles=["user"],
        attr={
            "user_id": int(user_id),
            "member_projects": json.loads(request.headers.get("member_projects", "[]")),
            "owner_projects": json.loads(request.headers.get("owner_projects", "[]")),
            "viewer_projects": json.loads(request.headers.get("viewer_projects", "[]")),
            "service_identity": request.headers.get("service_identity"),
        },
    )
    return principal


def overwrite_api(api: FastAPI, async_db: AsyncDB) -> None:
    """
    Utility function for overwriting API dependencies with test versions.
    """

    async def patched_session() -> typing.AsyncGenerator[AsyncSession, None]:
        session = async_db.session()
        try:
            yield session
        finally:
            await session.close()

    api.dependency_overrides[get_engine] = lambda: async_db
    api.dependency_overrides[get_db_session] = patched_session
    api.dependency_overrides[require_auth_principal] = patched_authprincipal
    api.dependency_overrides[get_auth_principal] = patched_authprincipal
    api.dependency_overrides[get_s3_client] = patched_s3_client


def raise_exception() -> str:
    raise Exception("Unexpected error")


# Subclass Query with an additional field to test Exception handling.
@strawberry.type
class MyQuery(Query):
    @strawberry.field
    def uncaught_exception(self) -> str:
        # Trigger an AttributeException
        return self.kaboom  # type: ignore


@pytest_asyncio.fixture()
async def api_test_schema(async_db: AsyncDB) -> FastAPI:
    """
    Create an API instance using the real schema.
    """
    settings = APISettings.model_validate({})  # Workaround for https://github.com/pydantic/pydantic/issues/3753
    strawberry_config = get_strawberry_config()
    schema = strawberry.Schema(query=MyQuery, mutation=Mutation, config=strawberry_config, extensions=[HandleErrors()])
    api = get_app(settings, schema)
    overwrite_api(api, async_db)
    return api
