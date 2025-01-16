"""
Launch the GraphQL server.
"""

import os
from typing import Union

import strawberry
import uvicorn
from graphql_api.mutations import Mutation
from graphql_api.queries import Query
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from platformics.database.connect import AsyncDB, init_async_db
from platformics.graphql_api.core.deps import (
    get_auth_principal,
    get_engine,
)
from platformics.graphql_api.core.error_handler import HandleErrors
from platformics.graphql_api.setup import get_app, get_strawberry_config
from platformics.security.authorization import Principal
from platformics.settings import APISettings

# This is needed because GraphQL does not support 64 bit integers
# https://strawberry.rocks/docs/types/scalars#bigint-64-bit-integers
BigInt = strawberry.scalar(
    Union[int, str],  # type: ignore
    serialize=lambda v: int(v),
    parse_value=lambda v: str(v),
    description="BigInt field",
)


settings = APISettings.model_validate({})  # Workaround for https://github.com/pydantic/pydantic/issues/3753
schema = strawberry.Schema(query=Query, mutation=Mutation, config=get_strawberry_config(), extensions=[HandleErrors()],     scalar_overrides={int: BigInt},
)


# Create and run app
app = get_app(settings, schema)

engine = init_async_db(settings.DB_URI, echo=settings.DB_ECHO, pool_size=5, max_overflow=5)
app.state.engine = engine


def get_allowed_origins() -> list[str] | None:
    if origins := os.getenv("CRYOET_CORS_ALLOWED_ORIGINS"):
        return [item.strip() for item in origins.split(",")]
    return []


def get_allowed_origin_regex() -> str | None:
    if os.getenv("CRYOET_CORS_ALLOWED_ORIGINS"):
        return None
    # Use env var by default but fall back to localhost
    return os.getenv("CRYOET_CORS_ALLOWED_REGEXES", r"http://localhost:\d+")


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_origin_regex=get_allowed_origin_regex(),
    allow_headers=["Content-Type"],
    allow_credentials=True,
    max_age=600,
    allow_methods=["*"],
)


def override_auth_principal():
    # Create an anonymous auth scope if we don't have a logged in user!
    return Principal(
        "anonymous",
        roles=["user"],
        attr={
            "user_id": 0,
            "owner_projects": [],
            "member_projects": [],
            "service_identity": [],
            "viewer_projects": [],
        },
    )


def override_get_engine(request: Request) -> AsyncDB:
    return request.app.state.engine


app.dependency_overrides[get_engine] = override_get_engine
app.dependency_overrides[get_auth_principal] = override_auth_principal

if __name__ == "__main__":
    config = uvicorn.Config("main:app", host="0.0.0.0", port=9008, log_level="info")
    server = uvicorn.Server(config)
    server.run()
