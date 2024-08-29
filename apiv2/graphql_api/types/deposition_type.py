"""
GraphQL type for DepositionType

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/types/class_name.py.j2 instead.
"""

# ruff: noqa: E501 Line too long


import datetime
import enum
import typing
from typing import TYPE_CHECKING, Annotated, Optional, Sequence

import database.models as db
import strawberry
from fastapi import Depends
from graphql_api.helpers.deposition_type import DepositionTypeGroupByOptions, build_deposition_type_groupby_output
from sqlalchemy import inspect
from sqlalchemy.engine.row import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.types import Info
from support.enums import deposition_types_enum
from support.limit_offset import LimitOffsetClause
from typing_extensions import TypedDict
from validators.deposition_type import DepositionTypeCreateInputValidator, DepositionTypeUpdateInputValidator

from platformics.graphql_api.core.deps import get_authz_client, get_db_session, is_system_user, require_auth_principal
from platformics.graphql_api.core.errors import PlatformicsError
from platformics.graphql_api.core.query_builder import get_aggregate_db_rows, get_db_rows
from platformics.graphql_api.core.query_input_types import (
    EnumComparators,
    IntComparators,
    aggregator_map,
    orderBy,
)
from platformics.graphql_api.core.relay_interface import EntityInterface
from platformics.graphql_api.core.strawberry_extensions import DependencyExtension
from platformics.security.authorization import AuthzAction, AuthzClient, Principal

E = typing.TypeVar("E")
T = typing.TypeVar("T")

if TYPE_CHECKING:
    from graphql_api.types.deposition import Deposition, DepositionOrderByClause, DepositionWhereClause

    pass
else:
    DepositionWhereClause = "DepositionWhereClause"
    Deposition = "Deposition"
    DepositionOrderByClause = "DepositionOrderByClause"
    pass


"""
------------------------------------------------------------------------------
Dataloaders
------------------------------------------------------------------------------
These are batching functions for loading related objects to avoid N+1 queries.
"""


@strawberry.field
async def load_deposition_rows(
    root: "DepositionType",
    info: Info,
    where: Annotated["DepositionWhereClause", strawberry.lazy("graphql_api.types.deposition")] | None = None,
    order_by: Optional[
        list[Annotated["DepositionOrderByClause", strawberry.lazy("graphql_api.types.deposition")]]
    ] = [],
) -> Optional[Annotated["Deposition", strawberry.lazy("graphql_api.types.deposition")]]:
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.DepositionType)
    relationship = mapper.relationships["deposition"]
    return await dataloader.loader_for(relationship, where, order_by).load(root.deposition_id)  # type:ignore


"""
------------------------------------------------------------------------------
Define Strawberry GQL types
------------------------------------------------------------------------------
"""


"""
Only let users specify IDs in WHERE clause when mutating data (for safety).
We can extend that list as we gather more use cases from the FE team.
"""


@strawberry.input
class DepositionTypeWhereClauseMutations(TypedDict):
    id: IntComparators | None


"""
Supported WHERE clause attributes
"""


@strawberry.input
class DepositionTypeWhereClause(TypedDict):
    deposition: Optional[Annotated["DepositionWhereClause", strawberry.lazy("graphql_api.types.deposition")]] | None
    type: Optional[EnumComparators[deposition_types_enum]] | None
    id: Optional[IntComparators] | None


"""
Supported ORDER BY clause attributes
"""


@strawberry.input
class DepositionTypeOrderByClause(TypedDict):
    deposition: Optional[Annotated["DepositionOrderByClause", strawberry.lazy("graphql_api.types.deposition")]] | None
    type: Optional[orderBy] | None
    id: Optional[orderBy] | None


"""
Define DepositionType type
"""


@strawberry.type(description=None)
class DepositionType(EntityInterface):
    deposition: Optional[Annotated["Deposition", strawberry.lazy("graphql_api.types.deposition")]] = (
        load_deposition_rows
    )  # type:ignore
    type: Optional[deposition_types_enum] = strawberry.field(description=None, default=None)
    id: int = strawberry.field(description="An identifier to refer to a specific instance of this type")


"""
We need to add this to each Queryable type so that strawberry will accept either our
Strawberry type *or* a SQLAlchemy model instance as a valid response class from a resolver
"""
DepositionType.__strawberry_definition__.is_type_of = (  # type: ignore
    lambda obj, info: type(obj) == db.DepositionType or type(obj) == DepositionType
)

"""
------------------------------------------------------------------------------
Aggregation types
------------------------------------------------------------------------------
"""
"""
Define columns that support numerical aggregations
"""


@strawberry.type
class DepositionTypeNumericalColumns:
    id: Optional[int] = None


"""
Define columns that support min/max aggregations
"""


@strawberry.type
class DepositionTypeMinMaxColumns:
    id: Optional[int] = None


"""
Define enum of all columns to support count and count(distinct) aggregations
"""


@strawberry.enum
class DepositionTypeCountColumns(enum.Enum):
    deposition = "deposition"
    type = "type"
    id = "id"


"""
All supported aggregation functions
"""


@strawberry.type
class DepositionTypeAggregateFunctions:
    # This is a hack to accept "distinct" and "columns" as arguments to "count"
    @strawberry.field
    def count(
        self, distinct: Optional[bool] = False, columns: Optional[DepositionTypeCountColumns] = None,
    ) -> Optional[int]:
        # Count gets set with the proper value in the resolver, so we just return it here
        return self.count  # type: ignore

    sum: Optional[DepositionTypeNumericalColumns] = None
    avg: Optional[DepositionTypeNumericalColumns] = None
    stddev: Optional[DepositionTypeNumericalColumns] = None
    variance: Optional[DepositionTypeNumericalColumns] = None
    min: Optional[DepositionTypeMinMaxColumns] = None
    max: Optional[DepositionTypeMinMaxColumns] = None
    groupBy: Optional[DepositionTypeGroupByOptions] = None


"""
Wrapper around DepositionTypeAggregateFunctions
"""


@strawberry.type
class DepositionTypeAggregate:
    aggregate: Optional[list[DepositionTypeAggregateFunctions]] = None


"""
------------------------------------------------------------------------------
Mutation types
------------------------------------------------------------------------------
"""


@strawberry.input()
class DepositionTypeCreateInput:
    deposition_id: Optional[strawberry.ID] = strawberry.field(description=None, default=None)
    type: Optional[deposition_types_enum] = strawberry.field(description=None, default=None)
    id: int = strawberry.field(description="An identifier to refer to a specific instance of this type")


@strawberry.input()
class DepositionTypeUpdateInput:
    deposition_id: Optional[strawberry.ID] = strawberry.field(description=None, default=None)
    type: Optional[deposition_types_enum] = strawberry.field(description=None, default=None)
    id: Optional[int] = strawberry.field(description="An identifier to refer to a specific instance of this type")


"""
------------------------------------------------------------------------------
Utilities
------------------------------------------------------------------------------
"""


@strawberry.field(extensions=[DependencyExtension()])
async def resolve_deposition_types(
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    where: Optional[DepositionTypeWhereClause] = None,
    order_by: Optional[list[DepositionTypeOrderByClause]] = [],
    limit_offset: Optional[LimitOffsetClause] = None,
) -> typing.Sequence[DepositionType]:
    """
    Resolve DepositionType objects. Used for queries (see graphql_api/queries.py).
    """
    limit = limit_offset["limit"] if limit_offset and "limit" in limit_offset else None
    offset = limit_offset["offset"] if limit_offset and "offset" in limit_offset else None
    if offset and not limit:
        raise PlatformicsError("Cannot use offset without limit")
    return await get_db_rows(db.DepositionType, session, authz_client, principal, where, order_by, AuthzAction.VIEW, limit, offset)  # type: ignore


def format_deposition_type_aggregate_output(
    query_results: Sequence[RowMapping] | RowMapping,
) -> DepositionTypeAggregate:
    """
    Given a row from the DB containing the results of an aggregate query,
    format the results using the proper GraphQL types.
    """
    aggregate = []
    if type(query_results) is not list:
        query_results = [query_results]  # type: ignore
    for row in query_results:
        aggregate.append(format_deposition_type_aggregate_row(row))
    return DepositionTypeAggregate(aggregate=aggregate)


def format_deposition_type_aggregate_row(row: RowMapping) -> DepositionTypeAggregateFunctions:
    """
    Given a single row from the DB containing the results of an aggregate query,
    format the results using the proper GraphQL types.
    """
    output = DepositionTypeAggregateFunctions()
    for key, value in row.items():
        # Key is either an aggregate function or a groupby key
        group_keys = key.split(".")
        aggregate = key.split("_", 1)
        if aggregate[0] not in aggregator_map.keys():
            # Turn list of groupby keys into nested objects
            if not output.groupBy:
                output.groupBy = DepositionTypeGroupByOptions()
            group = build_deposition_type_groupby_output(output.groupBy, group_keys, value)
            output.groupBy = group
        else:
            aggregate_name = aggregate[0]
            if aggregate_name == "count":
                output.count = value
            else:
                aggregator_fn, col_name = aggregate[0], aggregate[1]
                if not getattr(output, aggregator_fn):
                    if aggregate_name in ["min", "max"]:
                        setattr(output, aggregator_fn, DepositionTypeMinMaxColumns())
                    else:
                        setattr(output, aggregator_fn, DepositionTypeNumericalColumns())
                setattr(getattr(output, aggregator_fn), col_name, value)
    return output


@strawberry.field(extensions=[DependencyExtension()])
async def resolve_deposition_types_aggregate(
    info: Info,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    where: Optional[DepositionTypeWhereClause] = None,
    # TODO: add support for groupby, limit/offset
) -> DepositionTypeAggregate:
    """
    Aggregate values for DepositionType objects. Used for queries (see graphql_api/queries.py).
    """
    # Get the selected aggregate functions and columns to operate on, and groupby options if any were provided.
    # TODO: not sure why selected_fields is a list
    selections = info.selected_fields[0].selections[0].selections
    aggregate_selections = [selection for selection in selections if selection.name != "groupBy"]
    groupby_selections = [selection for selection in selections if selection.name == "groupBy"]
    groupby_selections = groupby_selections[0].selections if groupby_selections else []

    if not aggregate_selections:
        raise PlatformicsError("No aggregate functions selected")

    rows = await get_aggregate_db_rows(db.DepositionType, session, authz_client, principal, where, aggregate_selections, [], groupby_selections)  # type: ignore
    aggregate_output = format_deposition_type_aggregate_output(rows)
    return aggregate_output


@strawberry.mutation(extensions=[DependencyExtension()])
async def create_deposition_type(
    input: DepositionTypeCreateInput,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    is_system_user: bool = Depends(is_system_user),
) -> db.DepositionType:
    """
    Create a new DepositionType object. Used for mutations (see graphql_api/mutations.py).
    """
    validated = DepositionTypeCreateInputValidator(**input.__dict__)
    params = validated.model_dump()

    # Validate that the user can read all of the entities they're linking to.

    # Validate that the user can read all of the entities they're linking to.
    # Check that deposition relationship is accessible.
    if validated.deposition_id:
        deposition = await get_db_rows(
            db.Deposition,
            session,
            authz_client,
            principal,
            {"id": {"_eq": validated.deposition_id}},
            [],
            AuthzAction.VIEW,
        )
        if not deposition:
            raise PlatformicsError("Unauthorized: deposition does not exist")

    # Save to DB
    params["owner_user_id"] = int(principal.id)
    new_entity = db.DepositionType(**params)

    # Are we actually allowed to create this entity?
    if not authz_client.can_create(new_entity, principal):
        raise PlatformicsError("Unauthorized: Cannot create entity")

    session.add(new_entity)
    await session.commit()
    return new_entity


@strawberry.mutation(extensions=[DependencyExtension()])
async def update_deposition_type(
    input: DepositionTypeUpdateInput,
    where: DepositionTypeWhereClauseMutations,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    is_system_user: bool = Depends(is_system_user),
) -> Sequence[db.DepositionType]:
    """
    Update DepositionType objects. Used for mutations (see graphql_api/mutations.py).
    """
    validated = DepositionTypeUpdateInputValidator(**input.__dict__)
    params = validated.model_dump()

    # Need at least one thing to update
    num_params = len([x for x in params if params[x] is not None])
    if num_params == 0:
        raise PlatformicsError("No fields to update")

    # Validate that the user can read all of the entities they're linking to.
    # Check that deposition relationship is accessible.
    if validated.deposition_id:
        deposition = await get_db_rows(
            db.Deposition,
            session,
            authz_client,
            principal,
            {"id": {"_eq": validated.deposition_id}},
            [],
            AuthzAction.VIEW,
        )
        if not deposition:
            raise PlatformicsError("Unauthorized: deposition does not exist")
        params["deposition"] = deposition[0]
        del params["deposition_id"]

    # Fetch entities for update, if we have access to them
    entities = await get_db_rows(db.DepositionType, session, authz_client, principal, where, [], AuthzAction.UPDATE)
    if len(entities) == 0:
        raise PlatformicsError("Unauthorized: Cannot update entities")

    # Update DB
    updated_at = datetime.datetime.now()
    for entity in entities:
        entity.updated_at = updated_at
        for key in params:
            if params[key] is not None:
                setattr(entity, key, params[key])

    if not authz_client.can_update(entity, principal):
        raise PlatformicsError("Unauthorized: Cannot access new collection")

    await session.commit()
    return entities


@strawberry.mutation(extensions=[DependencyExtension()])
async def delete_deposition_type(
    where: DepositionTypeWhereClauseMutations,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
) -> Sequence[db.DepositionType]:
    """
    Delete DepositionType objects. Used for mutations (see graphql_api/mutations.py).
    """
    # Fetch entities for deletion, if we have access to them
    entities = await get_db_rows(db.DepositionType, session, authz_client, principal, where, [], AuthzAction.DELETE)
    if len(entities) == 0:
        raise PlatformicsError("Unauthorized: Cannot delete entities")

    # Update DB
    for entity in entities:
        await session.delete(entity)
    await session.commit()
    return entities
