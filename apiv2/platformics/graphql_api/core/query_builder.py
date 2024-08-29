"""
Helper functions for working with the database.
"""

import typing
from collections import defaultdict
from typing import Any, Optional, Sequence, Tuple

import strcase
from sqlalchemy import ColumnElement, and_, distinct, inspect
from sqlalchemy.engine.row import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy.sql import Select
from typing_extensions import TypedDict

from platformics.database.models.base import Base
from platformics.graphql_api.core.errors import PlatformicsError
from platformics.graphql_api.core.query_input_types import aggregator_map, operator_map, orderBy
from platformics.security.authorization import AuthzAction, AuthzClient, Principal

E = typing.TypeVar("E")
T = typing.TypeVar("T")


def apply_order_by(field: str, direction: orderBy, query: Select) -> Select:
    match direction.value:
        case "asc":
            query = query.order_by(getattr(query.selected_columns, field).asc())
        case "asc_nulls_first":
            query = query.order_by(getattr(query.selected_columns, field).asc().nullsfirst())
        case "asc_nulls_last":
            query = query.order_by(getattr(query.selected_columns, field).asc().nullslast())
        case "desc":
            query = query.order_by(getattr(query.selected_columns, field).desc())
        case "desc_nulls_first":
            query = query.order_by(getattr(query.selected_columns, field).desc().nullsfirst())
        case "desc_nulls_last":
            query = query.order_by(getattr(query.selected_columns, field).desc().nullslast())
    return query


class IndexedOrderByClause(TypedDict):
    field: dict[str, orderBy] | dict[str, dict[str, Any]]
    index: int
    sort: orderBy


def convert_where_clauses_to_sql(
    principal: Principal,
    authz_client: AuthzClient,
    action: AuthzAction,
    query: Select,
    sa_model: Base,
    where_clause: dict[str, Any],
    order_by: Optional[list[IndexedOrderByClause]],
    group_by: Optional[ColumnElement[Any]] | Optional[list[Any]],
    depth: int,
) -> Tuple[Select, list[Any], list[Any]]:
    """
    Convert a query with a where clause clause to a SQLAlchemy query.
    If order_by is provided, also return a list of order_by fields that need to be applied.
    """

    # TODO, this may need to be adjusted, 5 just seemed like a reasonable starting point
    if depth >= 5:
        raise PlatformicsError("Max filter depth exceeded")
    depth += 1

    if not order_by:
        order_by = []
    if not where_clause:
        where_clause = {}
    if not group_by:
        group_by = []

    local_order_by = []  # Fields that we can sort by on the *current* class without having to deal with recursion
    local_where_clauses = {}  # Fields that we can filter on the *current* class without having to deal with recursion
    local_group_by = []  # Fields that we can group by on the *current* class without having to deal with recursion

    mapper = inspect(sa_model)

    # Create a dictionary with the keys as the related field/field names
    # The values are dict of {order_by: {"field": ..., "index": ...}, where: {...}, group_by: [...]}
    all_joins = defaultdict(dict)  # type: ignore
    for item in order_by:
        for col, v in item["field"].items():
            if col in mapper.relationships:  # type: ignore
                if not all_joins[col].get("order_by"):
                    all_joins[col]["order_by"] = []
                all_joins[col]["order_by"].append({"field": v, "index": item["index"]})
            else:
                local_order_by.append({"field": col, "sort": v, "index": item["index"]})
    for col, v in where_clause.items():
        if col in mapper.relationships:  # type: ignore
            all_joins[col]["where"] = v
        else:
            local_where_clauses[col] = v
    authz_client.modify_where_clause(principal, action, sa_model, local_where_clauses)
    for group in group_by:  # type: ignore
        col = strcase.to_snake(group.name)
        if col in mapper.relationships:  # type: ignore
            all_joins[col]["group_by"] = group.selections
        else:
            local_group_by.append(getattr(sa_model, col))

    # Add the local_group_by fields to the query
    for col in local_group_by:
        query = query.add_columns(col)  # type: ignore

    # Handle related fields
    for join_field, join_info in all_joins.items():
        relationship = mapper.relationships[join_field]  # type: ignore
        related_cls = relationship.mapper.entity
        secure_query = authz_client.get_resource_query(principal, action, related_cls)
        # Get the subquery, nested order_by fields, and nested group_by fields that need to be applied to the current query
        subquery, subquery_order_by, subquery_group_by = convert_where_clauses_to_sql(
            principal,
            authz_client,
            action,
            secure_query,
            related_cls,
            join_info.get("where"),  # type: ignore
            join_info.get("order_by"),
            join_info.get("group_by"),
            depth,
        )
        subquery = subquery.subquery()  # type: ignore
        query_alias = aliased(related_cls, subquery)  # type: ignore
        joincondition_a = [
            (getattr(sa_model, local.key) == getattr(query_alias, remote.key))
            for local, remote in relationship.local_remote_pairs
        ]
        query = query.join(query_alias, and_(*joincondition_a))
        # Add the subquery columns and subquery_order_by fields to the current query
        for aliased_field_num, item in enumerate(subquery_order_by):
            aliased_field_name = f"{join_field}_order_field_{aliased_field_num}"
            field_to_match = getattr(subquery.c, item["field"])  # type: ignore
            query = query.add_columns(field_to_match.label(aliased_field_name))
            local_order_by.append({"field": aliased_field_name, "sort": item["sort"], "index": item["index"]})

        # Add the subquery columns and subquery_group_by fields to the current query
        for item in subquery_group_by:
            # mypy is currently inferring the wrong type for `item` so we can silence it until we can fix it.
            field_name = item if isinstance(item, str) else item.key  # type: ignore[attr-defined]
            aliased_field_name = f"{join_field}.{field_name}"
            field_to_match = getattr(subquery.c, field_name)  # type: ignore
            query = query.add_columns(field_to_match.label(aliased_field_name))
            local_group_by.append(aliased_field_name)

    # Handle not-related fields
    for col, v in local_where_clauses.items():
        for comparator, value in v.items():  # type: ignore
            sa_comparator = operator_map[comparator]
            if sa_comparator == "IS_NULL":
                if value:
                    query = query.filter(getattr(sa_model, col).is_(None))
                else:
                    query = query.filter(getattr(sa_model, col).isnot(None))
            # For the variants of regexp_match, we pass in a dict with the comparator, should_negate, and flag
            elif isinstance(sa_comparator, dict):
                if sa_comparator["should_negate"]:
                    query = query.filter(
                        ~(getattr(getattr(sa_model, col), sa_comparator["comparator"])(value, sa_comparator["flag"])),
                    )
                else:
                    query = query.filter(
                        getattr(getattr(sa_model, col), sa_comparator["comparator"])(value, sa_comparator["flag"]),
                    )
            else:
                query = query.filter(getattr(getattr(sa_model, col), sa_comparator)(value))  # type: ignore

    return query, local_order_by, local_group_by


def get_db_query(
    model_cls: type[E],
    action: AuthzAction,
    authz_client: AuthzClient,
    principal: Principal,
    # TODO it would be nicer if we could have the WhereClause classes inherit from a BaseWhereClause
    # so that these type checks could be smarter, but TypedDict doesn't support type checks like that
    where: dict[str, Any],
    order_by: Optional[list[dict[str, Any]]] = None,
    relationship: Optional[Any] = None,
) -> Select:
    """
    Given a model class and a where clause, return a SQLAlchemy query that is limited
    based on the where clause, and which entities the user has access to.
    """
    query = authz_client.get_resource_query(principal, action, model_cls, relationship)
    # Add indices to the order_by fields so that we can preserve the order of the fields
    if order_by is None:
        order_by = []
    order_by = [IndexedOrderByClause({"field": x, "index": i}) for i, x in enumerate(order_by)]  # type: ignore
    query, order_by, _group_by = convert_where_clauses_to_sql(
        principal,
        authz_client,
        action,
        query,
        model_cls,  # type: ignore
        where,
        order_by,  # type: ignore
        [],
        0,
    )
    # Sort the order_by fields by their index so that we can apply them in the correct order
    order_by.sort(key=lambda x: x["index"])
    for item in order_by:
        query = apply_order_by(item["field"], item["sort"], query)
    return query


async def get_db_rows(
    model_cls: type[E],  # type: ignore
    session: AsyncSession,
    authz_client: AuthzClient,
    principal: Principal,
    where: Any,
    order_by: Optional[list[dict[str, Any]]] = None,
    action: AuthzAction = AuthzAction.VIEW,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> typing.Sequence[E]:
    """
    Retrieve rows from the database, filtered by the where clause and the user's permissions.
    """
    if order_by is None:
        order_by = []
    query = get_db_query(model_cls, action, authz_client, principal, where, order_by)
    if limit:
        query = query.limit(limit)
        if offset:
            query = query.offset(offset)
    result = await session.execute(query)
    return result.scalars().all()


def get_aggregate_db_query(
    model_cls: type[E],
    action: AuthzAction,
    authz_client: AuthzClient,
    principal: Principal,
    where: dict[str, Any],
    aggregate: Any,
    group_by: Optional[ColumnElement[Any]] | Optional[list[Any]] = None,
    depth: Optional[int] = None,
    remote: Optional[ColumnElement[Any]] = None,
) -> Tuple[Select, list[Any]]:
    """
    Given a model class, a where clause, and an aggregate clause,
    return a SQLAlchemy query that performs the aggregations, with results
    limited based on the where clause, and which entities the user has access to.
    """
    if not depth:
        depth = 0
    depth += 1
    # TODO, this may need to be adjusted, 5 just seemed like a reasonable starting point
    if depth >= 5:
        raise Exception("Max filter depth exceeded")
    query = authz_client.get_resource_query(principal, action, model_cls)
    # Deconstruct the aggregate dict and build mappings for the query
    aggregate_query_fields = []
    if remote is not None:
        aggregate_query_fields.append(remote)
    for aggregator in aggregate:
        agg_fn = aggregator_map[aggregator.name]
        if aggregator.name == "count":
            # If provided "distinct" or "columns" arguments, use them to construct the count query
            # Otherwise, default to counting the primary key
            col = model_cls.id
            count_fn = agg_fn(model_cls.id)  # type: ignore
            if aggregator.arguments:
                if colname := strcase.to_snake(aggregator.arguments.get("columns")):
                    col = getattr(model_cls, colname)
                if aggregator.arguments.get("distinct"):
                    count_fn = agg_fn(distinct(col))  # type: ignore
            aggregate_query_fields.append(count_fn.label("count"))
        else:
            for col in aggregator.selections:
                col_name = strcase.to_snake(col.name)
                aggregate_query_fields.append(
                    agg_fn(getattr(model_cls, col_name)).label(f"{aggregator.name}_{col_name}"),  # type: ignore
                )
    query = query.with_only_columns(*aggregate_query_fields)
    query, _order_by, group_by = convert_where_clauses_to_sql(
        principal,
        authz_client,
        action,
        query,
        model_cls,  # type: ignore
        where,
        [],
        group_by,
        depth,  # type: ignore
    )
    if remote is not None:
        query = query.group_by(remote)
    return query, group_by


async def get_aggregate_db_rows(
    model_cls: type[E],  # type: ignore
    session: AsyncSession,
    authz_client: AuthzClient,
    principal: Principal,
    where: Any,
    aggregate: Any,
    order_by: Optional[list[tuple[ColumnElement[Any], ...]]] = None,
    group_by: Optional[ColumnElement[Any]] | Optional[list[Any]] = None,
    action: AuthzAction = AuthzAction.VIEW,
) -> Sequence[RowMapping]:
    """
    Retrieve aggregate rows from the database, filtered by the where clause and the user's permissions.
    """
    query, group_by = get_aggregate_db_query(model_cls, action, authz_client, principal, where, aggregate, group_by)
    if group_by:
        query = query.group_by(*group_by)  # type: ignore
    result = await session.execute(query)
    return result.mappings().all()
