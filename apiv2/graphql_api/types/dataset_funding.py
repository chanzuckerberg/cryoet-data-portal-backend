"""
GraphQL type for DatasetFunding

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
from graphql_api.helpers.dataset_funding import DatasetFundingGroupByOptions, build_dataset_funding_groupby_output
from sqlalchemy import inspect
from sqlalchemy.engine.row import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.types import Info
from support.limit_offset import LimitOffsetClause
from typing_extensions import TypedDict
from validators.dataset_funding import DatasetFundingCreateInputValidator, DatasetFundingUpdateInputValidator

from platformics.graphql_api.core.deps import get_authz_client, get_db_session, is_system_user, require_auth_principal
from platformics.graphql_api.core.errors import PlatformicsError
from platformics.graphql_api.core.query_builder import get_aggregate_db_rows, get_db_rows
from platformics.graphql_api.core.query_input_types import (
    IntComparators,
    StrComparators,
    aggregator_map,
    orderBy,
)
from platformics.graphql_api.core.relay_interface import EntityInterface
from platformics.graphql_api.core.strawberry_extensions import DependencyExtension
from platformics.graphql_api.core.strawberry_helpers import get_aggregate_selections
from platformics.security.authorization import AuthzAction, AuthzClient, Principal

E = typing.TypeVar("E")
T = typing.TypeVar("T")

if TYPE_CHECKING:
    from graphql_api.types.dataset import Dataset, DatasetAggregateWhereClause, DatasetOrderByClause, DatasetWhereClause

    pass
else:
    DatasetWhereClause = "DatasetWhereClause"
    DatasetAggregateWhereClause = "DatasetAggregateWhereClause"
    Dataset = "Dataset"
    DatasetOrderByClause = "DatasetOrderByClause"
    pass


"""
------------------------------------------------------------------------------
Dataloaders
------------------------------------------------------------------------------
These are batching functions for loading related objects to avoid N+1 queries.
"""


@strawberry.field
async def load_dataset_rows(
    root: "DatasetFunding",
    info: Info,
    where: Annotated["DatasetWhereClause", strawberry.lazy("graphql_api.types.dataset")] | None = None,
    order_by: Optional[list[Annotated["DatasetOrderByClause", strawberry.lazy("graphql_api.types.dataset")]]] = [],
) -> Optional[Annotated["Dataset", strawberry.lazy("graphql_api.types.dataset")]]:
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.DatasetFunding)
    relationship = mapper.relationships["dataset"]
    return await dataloader.loader_for(relationship, where, order_by).load(root.dataset_id)  # type:ignore


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
class DatasetFundingWhereClauseMutations(TypedDict):
    id: IntComparators | None


"""
Supported WHERE clause attributes
"""


@strawberry.input
class DatasetFundingWhereClause(TypedDict):
    dataset: Optional[Annotated["DatasetWhereClause", strawberry.lazy("graphql_api.types.dataset")]] | None
    dataset_id: Optional[IntComparators] | None
    funding_agency_name: Optional[StrComparators] | None
    grant_id: Optional[StrComparators] | None
    id: Optional[IntComparators] | None


"""
Supported ORDER BY clause attributes
"""


@strawberry.input
class DatasetFundingOrderByClause(TypedDict):
    dataset: Optional[Annotated["DatasetOrderByClause", strawberry.lazy("graphql_api.types.dataset")]] | None
    funding_agency_name: Optional[orderBy] | None
    grant_id: Optional[orderBy] | None
    id: Optional[orderBy] | None


"""
Define DatasetFunding type
"""


@strawberry.type(description="Metadata for a dataset's funding sources")
class DatasetFunding(EntityInterface):
    dataset: Optional[Annotated["Dataset", strawberry.lazy("graphql_api.types.dataset")]] = (
        load_dataset_rows
    )  # type:ignore
    dataset_id: Optional[int]
    funding_agency_name: Optional[str] = strawberry.field(description="Name of the funding agency.", default=None)
    grant_id: Optional[str] = strawberry.field(
        description="Grant identifier provided by the funding agency.", default=None,
    )
    id: int = strawberry.field(description="Numeric identifier (May change!)")


"""
We need to add this to each Queryable type so that strawberry will accept either our
Strawberry type *or* a SQLAlchemy model instance as a valid response class from a resolver
"""
DatasetFunding.__strawberry_definition__.is_type_of = (  # type: ignore
    lambda obj, info: type(obj) == db.DatasetFunding or type(obj) == DatasetFunding
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
class DatasetFundingNumericalColumns:
    id: Optional[int] = None


"""
Define columns that support min/max aggregations
"""


@strawberry.type
class DatasetFundingMinMaxColumns:
    funding_agency_name: Optional[str] = None
    grant_id: Optional[str] = None
    id: Optional[int] = None


"""
Define enum of all columns to support count and count(distinct) aggregations
"""


@strawberry.enum
class DatasetFundingCountColumns(enum.Enum):
    fundingAgencyName = "funding_agency_name"
    grantId = "grant_id"
    id = "id"


"""
Support *filtering* on aggregates and related aggregates
"""


@strawberry.input
class DatasetFundingAggregateWhereClauseCount(TypedDict):
    arguments: Optional["DatasetFundingCountColumns"] | None
    distinct: Optional[bool] | None
    filter: Optional[DatasetFundingWhereClause] | None
    predicate: Optional[IntComparators] | None


@strawberry.input
class DatasetFundingAggregateWhereClause(TypedDict):
    count: DatasetFundingAggregateWhereClauseCount


"""
All supported aggregation functions
"""


@strawberry.type
class DatasetFundingAggregateFunctions:
    # This is a hack to accept "distinct" and "columns" as arguments to "count"
    @strawberry.field
    def count(
        self, distinct: Optional[bool] = False, columns: Optional[DatasetFundingCountColumns] = None,
    ) -> Optional[int]:
        # Count gets set with the proper value in the resolver, so we just return it here
        return self.count  # type: ignore

    sum: Optional[DatasetFundingNumericalColumns] = None
    avg: Optional[DatasetFundingNumericalColumns] = None
    stddev: Optional[DatasetFundingNumericalColumns] = None
    variance: Optional[DatasetFundingNumericalColumns] = None
    min: Optional[DatasetFundingMinMaxColumns] = None
    max: Optional[DatasetFundingMinMaxColumns] = None
    groupBy: Optional[DatasetFundingGroupByOptions] = None


"""
Wrapper around DatasetFundingAggregateFunctions
"""


@strawberry.type
class DatasetFundingAggregate:
    aggregate: Optional[list[DatasetFundingAggregateFunctions]] = None


"""
------------------------------------------------------------------------------
Mutation types
------------------------------------------------------------------------------
"""


@strawberry.input()
class DatasetFundingCreateInput:
    dataset_id: Optional[strawberry.ID] = strawberry.field(
        description="The dataset this dataset funding is a part of", default=None,
    )
    funding_agency_name: Optional[str] = strawberry.field(description="Name of the funding agency.", default=None)
    grant_id: Optional[str] = strawberry.field(
        description="Grant identifier provided by the funding agency.", default=None,
    )
    id: int = strawberry.field(description="Numeric identifier (May change!)")


@strawberry.input()
class DatasetFundingUpdateInput:
    dataset_id: Optional[strawberry.ID] = strawberry.field(
        description="The dataset this dataset funding is a part of", default=None,
    )
    funding_agency_name: Optional[str] = strawberry.field(description="Name of the funding agency.", default=None)
    grant_id: Optional[str] = strawberry.field(
        description="Grant identifier provided by the funding agency.", default=None,
    )
    id: Optional[int] = strawberry.field(description="Numeric identifier (May change!)")


"""
------------------------------------------------------------------------------
Utilities
------------------------------------------------------------------------------
"""


@strawberry.field(extensions=[DependencyExtension()])
async def resolve_dataset_funding(
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    where: Optional[DatasetFundingWhereClause] = None,
    order_by: Optional[list[DatasetFundingOrderByClause]] = [],
    limit_offset: Optional[LimitOffsetClause] = None,
) -> typing.Sequence[DatasetFunding]:
    """
    Resolve DatasetFunding objects. Used for queries (see graphql_api/queries.py).
    """
    limit = limit_offset["limit"] if limit_offset and "limit" in limit_offset else None
    offset = limit_offset["offset"] if limit_offset and "offset" in limit_offset else None
    if offset and not limit:
        raise PlatformicsError("Cannot use offset without limit")
    return await get_db_rows(db.DatasetFunding, session, authz_client, principal, where, order_by, AuthzAction.VIEW, limit, offset)  # type: ignore


def format_dataset_funding_aggregate_output(
    query_results: Sequence[RowMapping] | RowMapping,
) -> DatasetFundingAggregate:
    """
    Given a row from the DB containing the results of an aggregate query,
    format the results using the proper GraphQL types.
    """
    aggregate = []
    if type(query_results) is not list:
        query_results = [query_results]  # type: ignore
    for row in query_results:
        aggregate.append(format_dataset_funding_aggregate_row(row))
    return DatasetFundingAggregate(aggregate=aggregate)


def format_dataset_funding_aggregate_row(row: RowMapping) -> DatasetFundingAggregateFunctions:
    """
    Given a single row from the DB containing the results of an aggregate query,
    format the results using the proper GraphQL types.
    """
    output = DatasetFundingAggregateFunctions()
    for key, value in row.items():
        # Key is either an aggregate function or a groupby key
        group_keys = key.split(".")
        aggregate = key.split("_", 1)
        if aggregate[0] not in aggregator_map.keys():
            # Turn list of groupby keys into nested objects
            if not output.groupBy:
                output.groupBy = DatasetFundingGroupByOptions()
            group = build_dataset_funding_groupby_output(output.groupBy, group_keys, value)
            output.groupBy = group
        else:
            aggregate_name = aggregate[0]
            if aggregate_name == "count":
                output.count = value
            else:
                aggregator_fn, col_name = aggregate[0], aggregate[1]
                if not getattr(output, aggregator_fn):
                    if aggregate_name in ["min", "max"]:
                        setattr(output, aggregator_fn, DatasetFundingMinMaxColumns())
                    else:
                        setattr(output, aggregator_fn, DatasetFundingNumericalColumns())
                setattr(getattr(output, aggregator_fn), col_name, value)
    return output


@strawberry.field(extensions=[DependencyExtension()])
async def resolve_dataset_funding_aggregate(
    info: Info,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    where: Optional[DatasetFundingWhereClause] = None,
    # TODO: add support for groupby, limit/offset
) -> DatasetFundingAggregate:
    """
    Aggregate values for DatasetFunding objects. Used for queries (see graphql_api/queries.py).
    """
    # Get the selected aggregate functions and columns to operate on, and groupby options if any were provided.
    # TODO: not sure why selected_fields is a list
    aggregate_selections, groupby_selections = get_aggregate_selections(info.selected_fields)

    if not aggregate_selections:
        raise PlatformicsError("No aggregate functions selected")

    rows = await get_aggregate_db_rows(db.DatasetFunding, session, authz_client, principal, where, aggregate_selections, [], groupby_selections)  # type: ignore
    aggregate_output = format_dataset_funding_aggregate_output(rows)
    return aggregate_output


@strawberry.mutation(extensions=[DependencyExtension()])
async def create_dataset_funding(
    input: DatasetFundingCreateInput,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    is_system_user: bool = Depends(is_system_user),
) -> db.DatasetFunding:
    """
    Create a new DatasetFunding object. Used for mutations (see graphql_api/mutations.py).
    """
    validated = DatasetFundingCreateInputValidator(**input.__dict__)
    params = validated.model_dump()

    # Validate that the user can read all of the entities they're linking to.

    # Validate that the user can read all of the entities they're linking to.
    # Check that dataset relationship is accessible.
    if validated.dataset_id:
        dataset = await get_db_rows(
            db.Dataset, session, authz_client, principal, {"id": {"_eq": validated.dataset_id}}, [], AuthzAction.VIEW,
        )
        if not dataset:
            raise PlatformicsError("Unauthorized: dataset does not exist")

    # Save to DB
    params["owner_user_id"] = int(principal.id)
    new_entity = db.DatasetFunding(**params)

    # Are we actually allowed to create this entity?
    if not authz_client.can_create(new_entity, principal):
        raise PlatformicsError("Unauthorized: Cannot create entity")

    session.add(new_entity)
    await session.commit()
    return new_entity


@strawberry.mutation(extensions=[DependencyExtension()])
async def update_dataset_funding(
    input: DatasetFundingUpdateInput,
    where: DatasetFundingWhereClauseMutations,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    is_system_user: bool = Depends(is_system_user),
) -> Sequence[db.DatasetFunding]:
    """
    Update DatasetFunding objects. Used for mutations (see graphql_api/mutations.py).
    """
    validated = DatasetFundingUpdateInputValidator(**input.__dict__)
    params = validated.model_dump()

    # Need at least one thing to update
    num_params = len([x for x in params if params[x] is not None])
    if num_params == 0:
        raise PlatformicsError("No fields to update")

    # Validate that the user can read all of the entities they're linking to.
    # Check that dataset relationship is accessible.
    if validated.dataset_id:
        dataset = await get_db_rows(
            db.Dataset, session, authz_client, principal, {"id": {"_eq": validated.dataset_id}}, [], AuthzAction.VIEW,
        )
        if not dataset:
            raise PlatformicsError("Unauthorized: dataset does not exist")
        params["dataset"] = dataset[0]
        del params["dataset_id"]

    # Fetch entities for update, if we have access to them
    entities = await get_db_rows(db.DatasetFunding, session, authz_client, principal, where, [], AuthzAction.UPDATE)
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
async def delete_dataset_funding(
    where: DatasetFundingWhereClauseMutations,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
) -> Sequence[db.DatasetFunding]:
    """
    Delete DatasetFunding objects. Used for mutations (see graphql_api/mutations.py).
    """
    # Fetch entities for deletion, if we have access to them
    entities = await get_db_rows(db.DatasetFunding, session, authz_client, principal, where, [], AuthzAction.DELETE)
    if len(entities) == 0:
        raise PlatformicsError("Unauthorized: Cannot delete entities")

    # Update DB
    for entity in entities:
        await session.delete(entity)
    await session.commit()
    return entities
