"""
Auto-generated by running `make codegen`. Do not edit!
Make changes to the template platformics/codegen/templates/graphql_api/types/class_name.py.j2 instead.

GraphQL type for PerSectionParameters
"""

# ruff: noqa: E501 Line too long


import datetime
import enum
import typing
from typing import TYPE_CHECKING, Annotated, Optional, Sequence

import database.models as db
import strawberry
from fastapi import Depends
from graphql_api.helpers.per_section_parameters import (
    PerSectionParametersGroupByOptions,
    build_per_section_parameters_groupby_output,
)
from platformics.graphql_api.core.deps import get_authz_client, get_db_session, is_system_user, require_auth_principal
from platformics.graphql_api.core.errors import PlatformicsError
from platformics.graphql_api.core.query_builder import get_aggregate_db_rows, get_db_rows
from platformics.graphql_api.core.query_input_types import (
    FloatComparators,
    IntComparators,
    aggregator_map,
    orderBy,
)
from platformics.graphql_api.core.relay_interface import EntityInterface
from platformics.graphql_api.core.strawberry_extensions import DependencyExtension
from platformics.graphql_api.core.strawberry_helpers import get_aggregate_selections
from platformics.security.authorization import AuthzAction, AuthzClient, Principal
from sqlalchemy import inspect
from sqlalchemy.engine.row import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.types import Info
from support.limit_offset import LimitOffsetClause
from typing_extensions import TypedDict
from validators.per_section_parameters import (
    PerSectionParametersCreateInputValidator,
    PerSectionParametersUpdateInputValidator,
)

E = typing.TypeVar("E")
T = typing.TypeVar("T")

if TYPE_CHECKING:
    from graphql_api.types.frame import Frame, FrameAggregateWhereClause, FrameOrderByClause, FrameWhereClause
    from graphql_api.types.run import Run, RunAggregateWhereClause, RunOrderByClause, RunWhereClause
    from graphql_api.types.tiltseries import (
        Tiltseries,
        TiltseriesAggregateWhereClause,
        TiltseriesOrderByClause,
        TiltseriesWhereClause,
    )

    pass
else:
    FrameWhereClause = "FrameWhereClause"
    FrameAggregateWhereClause = "FrameAggregateWhereClause"
    Frame = "Frame"
    FrameOrderByClause = "FrameOrderByClause"
    RunWhereClause = "RunWhereClause"
    RunAggregateWhereClause = "RunAggregateWhereClause"
    Run = "Run"
    RunOrderByClause = "RunOrderByClause"
    TiltseriesWhereClause = "TiltseriesWhereClause"
    TiltseriesAggregateWhereClause = "TiltseriesAggregateWhereClause"
    Tiltseries = "Tiltseries"
    TiltseriesOrderByClause = "TiltseriesOrderByClause"
    pass


"""
------------------------------------------------------------------------------
Dataloaders
------------------------------------------------------------------------------
These are batching functions for loading related objects to avoid N+1 queries.
"""


@strawberry.field
async def load_frame_rows(
    root: "PerSectionParameters",
    info: Info,
    where: Annotated["FrameWhereClause", strawberry.lazy("graphql_api.types.frame")] | None = None,
    order_by: Optional[list[Annotated["FrameOrderByClause", strawberry.lazy("graphql_api.types.frame")]]] = [],
) -> Optional[Annotated["Frame", strawberry.lazy("graphql_api.types.frame")]]:
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.PerSectionParameters)
    relationship = mapper.relationships["frame"]
    return await dataloader.loader_for(relationship, where, order_by).load(root.frame_id)  # type:ignore


@strawberry.field
async def load_run_rows(
    root: "PerSectionParameters",
    info: Info,
    where: Annotated["RunWhereClause", strawberry.lazy("graphql_api.types.run")] | None = None,
    order_by: Optional[list[Annotated["RunOrderByClause", strawberry.lazy("graphql_api.types.run")]]] = [],
) -> Optional[Annotated["Run", strawberry.lazy("graphql_api.types.run")]]:
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.PerSectionParameters)
    relationship = mapper.relationships["run"]
    return await dataloader.loader_for(relationship, where, order_by).load(root.run_id)  # type:ignore


@strawberry.field
async def load_tiltseries_rows(
    root: "PerSectionParameters",
    info: Info,
    where: Annotated["TiltseriesWhereClause", strawberry.lazy("graphql_api.types.tiltseries")] | None = None,
    order_by: Optional[
        list[Annotated["TiltseriesOrderByClause", strawberry.lazy("graphql_api.types.tiltseries")]]
    ] = [],
) -> Optional[Annotated["Tiltseries", strawberry.lazy("graphql_api.types.tiltseries")]]:
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.PerSectionParameters)
    relationship = mapper.relationships["tiltseries"]
    return await dataloader.loader_for(relationship, where, order_by).load(root.tiltseries_id)  # type:ignore


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
class PerSectionParametersWhereClauseMutations(TypedDict):
    id: IntComparators | None


"""
Supported WHERE clause attributes
"""


@strawberry.input
class PerSectionParametersWhereClause(TypedDict):
    astigmatic_angle: Optional[FloatComparators] | None
    frame: Optional[Annotated["FrameWhereClause", strawberry.lazy("graphql_api.types.frame")]] | None
    frame_id: Optional[IntComparators] | None
    major_defocus: Optional[FloatComparators] | None
    max_resolution: Optional[FloatComparators] | None
    minor_defocus: Optional[FloatComparators] | None
    phase_shift: Optional[FloatComparators] | None
    raw_angle: Optional[FloatComparators] | None
    run: Optional[Annotated["RunWhereClause", strawberry.lazy("graphql_api.types.run")]] | None
    run_id: Optional[IntComparators] | None
    tiltseries: Optional[Annotated["TiltseriesWhereClause", strawberry.lazy("graphql_api.types.tiltseries")]] | None
    tiltseries_id: Optional[IntComparators] | None
    z_index: Optional[IntComparators] | None
    id: Optional[IntComparators] | None


"""
Supported ORDER BY clause attributes
"""


@strawberry.input
class PerSectionParametersOrderByClause(TypedDict):
    astigmatic_angle: Optional[orderBy] | None
    frame: Optional[Annotated["FrameOrderByClause", strawberry.lazy("graphql_api.types.frame")]] | None
    major_defocus: Optional[orderBy] | None
    max_resolution: Optional[orderBy] | None
    minor_defocus: Optional[orderBy] | None
    phase_shift: Optional[orderBy] | None
    raw_angle: Optional[orderBy] | None
    run: Optional[Annotated["RunOrderByClause", strawberry.lazy("graphql_api.types.run")]] | None
    tiltseries: Optional[Annotated["TiltseriesOrderByClause", strawberry.lazy("graphql_api.types.tiltseries")]] | None
    z_index: Optional[orderBy] | None
    id: Optional[orderBy] | None


"""
Define PerSectionParameters type
"""


@strawberry.type(description="Map individual Frames to a Tiltseries")
class PerSectionParameters(EntityInterface):
    astigmatic_angle: Optional[float] = strawberry.field(
        description="Angle (in degrees) from reciprocal space X axis to the major axis of defocus.", default=None,
    )
    frame: Optional[Annotated["Frame", strawberry.lazy("graphql_api.types.frame")]] = load_frame_rows  # type:ignore
    frame_id: int
    major_defocus: Optional[float] = strawberry.field(
        description="Defocus (major axis) estimated for this tilt image in Angstrom (underfocus has positive sign).",
        default=None,
    )
    max_resolution: Optional[float] = strawberry.field(description="Maximum resolution of the frame", default=None)
    minor_defocus: Optional[float] = strawberry.field(
        description="Defocus (minor axis) estimated for this tilt image in Angstrom (underfocus has positive sign).",
        default=None,
    )
    phase_shift: Optional[float] = strawberry.field(
        description="Phase shift estimated for this tilt image in degrees.", default=None,
    )
    raw_angle: float = strawberry.field(
        description="Nominal tilt angle for this tilt image reported by the microscope.",
    )
    run: Optional[Annotated["Run", strawberry.lazy("graphql_api.types.run")]] = load_run_rows  # type:ignore
    run_id: int
    tiltseries: Optional[Annotated["Tiltseries", strawberry.lazy("graphql_api.types.tiltseries")]] = (
        load_tiltseries_rows
    )  # type:ignore
    tiltseries_id: int
    z_index: int = strawberry.field(description="Index (0-based) of this tilt image in the tilt series stack.")
    id: int = strawberry.field(description="Numeric identifier (May change!)")


"""
We need to add this to each Queryable type so that strawberry will accept either our
Strawberry type *or* a SQLAlchemy model instance as a valid response class from a resolver
"""
PerSectionParameters.__strawberry_definition__.is_type_of = (  # type: ignore
    lambda obj, info: type(obj) == db.PerSectionParameters or type(obj) == PerSectionParameters
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
class PerSectionParametersNumericalColumns:
    astigmatic_angle: Optional[float] = None
    major_defocus: Optional[float] = None
    max_resolution: Optional[float] = None
    minor_defocus: Optional[float] = None
    phase_shift: Optional[float] = None
    raw_angle: Optional[float] = None
    z_index: Optional[int] = None
    id: Optional[int] = None


"""
Define columns that support min/max aggregations
"""


@strawberry.type
class PerSectionParametersMinMaxColumns:
    astigmatic_angle: Optional[float] = None
    major_defocus: Optional[float] = None
    max_resolution: Optional[float] = None
    minor_defocus: Optional[float] = None
    phase_shift: Optional[float] = None
    raw_angle: Optional[float] = None
    z_index: Optional[int] = None
    id: Optional[int] = None


"""
Define enum of all columns to support count and count(distinct) aggregations
"""


@strawberry.enum
class PerSectionParametersCountColumns(enum.Enum):
    astigmaticAngle = "astigmatic_angle"
    majorDefocus = "major_defocus"
    maxResolution = "max_resolution"
    minorDefocus = "minor_defocus"
    phaseShift = "phase_shift"
    rawAngle = "raw_angle"
    zIndex = "z_index"
    id = "id"


"""
Support *filtering* on aggregates and related aggregates
"""


@strawberry.input
class PerSectionParametersAggregateWhereClauseCount(TypedDict):
    arguments: Optional["PerSectionParametersCountColumns"] | None
    distinct: Optional[bool] | None
    filter: Optional[PerSectionParametersWhereClause] | None
    predicate: Optional[IntComparators] | None


@strawberry.input
class PerSectionParametersAggregateWhereClause(TypedDict):
    count: PerSectionParametersAggregateWhereClauseCount


"""
All supported aggregation functions
"""


@strawberry.type
class PerSectionParametersAggregateFunctions:
    # This is a hack to accept "distinct" and "columns" as arguments to "count"
    @strawberry.field
    def count(
        self, distinct: Optional[bool] = False, columns: Optional[PerSectionParametersCountColumns] = None,
    ) -> Optional[int]:
        # Count gets set with the proper value in the resolver, so we just return it here
        return self.count  # type: ignore

    sum: Optional[PerSectionParametersNumericalColumns] = None
    avg: Optional[PerSectionParametersNumericalColumns] = None
    stddev: Optional[PerSectionParametersNumericalColumns] = None
    variance: Optional[PerSectionParametersNumericalColumns] = None
    min: Optional[PerSectionParametersMinMaxColumns] = None
    max: Optional[PerSectionParametersMinMaxColumns] = None
    groupBy: Optional[PerSectionParametersGroupByOptions] = None


"""
Wrapper around PerSectionParametersAggregateFunctions
"""


@strawberry.type
class PerSectionParametersAggregate:
    aggregate: Optional[list[PerSectionParametersAggregateFunctions]] = None


"""
------------------------------------------------------------------------------
Mutation types
------------------------------------------------------------------------------
"""


@strawberry.input()
class PerSectionParametersCreateInput:
    astigmatic_angle: Optional[float] = strawberry.field(
        description="Angle (in degrees) from reciprocal space X axis to the major axis of defocus.", default=None,
    )
    frame_id: strawberry.ID = strawberry.field(description="Frame that this section is a part of")
    major_defocus: Optional[float] = strawberry.field(
        description="Defocus (major axis) estimated for this tilt image in Angstrom (underfocus has positive sign).",
        default=None,
    )
    max_resolution: Optional[float] = strawberry.field(description="Maximum resolution of the frame", default=None)
    minor_defocus: Optional[float] = strawberry.field(
        description="Defocus (minor axis) estimated for this tilt image in Angstrom (underfocus has positive sign).",
        default=None,
    )
    phase_shift: Optional[float] = strawberry.field(
        description="Phase shift estimated for this tilt image in degrees.", default=None,
    )
    raw_angle: float = strawberry.field(
        description="Nominal tilt angle for this tilt image reported by the microscope.",
    )
    run_id: strawberry.ID = strawberry.field(description="Run that this section is a part of")
    tiltseries_id: strawberry.ID = strawberry.field(description="Tiltseries that this section is a part of")
    z_index: int = strawberry.field(description="Index (0-based) of this tilt image in the tilt series stack.")
    id: int = strawberry.field(description="Numeric identifier (May change!)")


@strawberry.input()
class PerSectionParametersUpdateInput:
    astigmatic_angle: Optional[float] = strawberry.field(
        description="Angle (in degrees) from reciprocal space X axis to the major axis of defocus.", default=None,
    )
    frame_id: Optional[strawberry.ID] = strawberry.field(
        description="Frame that this section is a part of", default=None,
    )
    major_defocus: Optional[float] = strawberry.field(
        description="Defocus (major axis) estimated for this tilt image in Angstrom (underfocus has positive sign).",
        default=None,
    )
    max_resolution: Optional[float] = strawberry.field(description="Maximum resolution of the frame", default=None)
    minor_defocus: Optional[float] = strawberry.field(
        description="Defocus (minor axis) estimated for this tilt image in Angstrom (underfocus has positive sign).",
        default=None,
    )
    phase_shift: Optional[float] = strawberry.field(
        description="Phase shift estimated for this tilt image in degrees.", default=None,
    )
    raw_angle: Optional[float] = strawberry.field(
        description="Nominal tilt angle for this tilt image reported by the microscope.", default=None,
    )
    run_id: Optional[strawberry.ID] = strawberry.field(description="Run that this section is a part of", default=None)
    tiltseries_id: Optional[strawberry.ID] = strawberry.field(
        description="Tiltseries that this section is a part of", default=None,
    )
    z_index: Optional[int] = strawberry.field(
        description="Index (0-based) of this tilt image in the tilt series stack.", default=None,
    )
    id: Optional[int] = strawberry.field(description="Numeric identifier (May change!)", default=None)


"""
------------------------------------------------------------------------------
Utilities
------------------------------------------------------------------------------
"""


@strawberry.field(extensions=[DependencyExtension()])
async def resolve_per_section_parameters(
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    where: Optional[PerSectionParametersWhereClause] = None,
    order_by: Optional[list[PerSectionParametersOrderByClause]] = [],
    limit_offset: Optional[LimitOffsetClause] = None,
) -> typing.Sequence[PerSectionParameters]:
    """
    Resolve PerSectionParameters objects. Used for queries (see graphql_api/queries.py).
    """
    limit = limit_offset["limit"] if limit_offset and "limit" in limit_offset else None
    offset = limit_offset["offset"] if limit_offset and "offset" in limit_offset else None
    if offset and not limit:
        raise PlatformicsError("Cannot use offset without limit")
    return await get_db_rows(db.PerSectionParameters, session, authz_client, principal, where, order_by, AuthzAction.VIEW, limit, offset)  # type: ignore


def format_per_section_parameters_aggregate_output(
    query_results: Sequence[RowMapping] | RowMapping,
) -> PerSectionParametersAggregate:
    """
    Given a row from the DB containing the results of an aggregate query,
    format the results using the proper GraphQL types.
    """
    aggregate = []
    if type(query_results) is not list:
        query_results = [query_results]  # type: ignore
    for row in query_results:
        aggregate.append(format_per_section_parameters_aggregate_row(row))
    return PerSectionParametersAggregate(aggregate=aggregate)


def format_per_section_parameters_aggregate_row(row: RowMapping) -> PerSectionParametersAggregateFunctions:
    """
    Given a single row from the DB containing the results of an aggregate query,
    format the results using the proper GraphQL types.
    """
    output = PerSectionParametersAggregateFunctions()
    for key, value in row.items():
        # Key is either an aggregate function or a groupby key
        group_keys = key.split(".")
        aggregate = key.split("_", 1)
        if aggregate[0] not in aggregator_map.keys():
            # Turn list of groupby keys into nested objects
            if not output.groupBy:
                output.groupBy = PerSectionParametersGroupByOptions()
            group = build_per_section_parameters_groupby_output(output.groupBy, group_keys, value)
            output.groupBy = group
        else:
            aggregate_name = aggregate[0]
            if aggregate_name == "count":
                output.count = value
            else:
                aggregator_fn, col_name = aggregate[0], aggregate[1]
                if not getattr(output, aggregator_fn):
                    if aggregate_name in ["min", "max"]:
                        setattr(output, aggregator_fn, PerSectionParametersMinMaxColumns())
                    else:
                        setattr(output, aggregator_fn, PerSectionParametersNumericalColumns())
                setattr(getattr(output, aggregator_fn), col_name, value)
    return output


@strawberry.field(extensions=[DependencyExtension()])
async def resolve_per_section_parameters_aggregate(
    info: Info,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    where: Optional[PerSectionParametersWhereClause] = None,
    # TODO: add support for groupby, limit/offset
) -> PerSectionParametersAggregate:
    """
    Aggregate values for PerSectionParameters objects. Used for queries (see graphql_api/queries.py).
    """
    # Get the selected aggregate functions and columns to operate on, and groupby options if any were provided.
    # TODO: not sure why selected_fields is a list
    aggregate_selections, groupby_selections = get_aggregate_selections(info.selected_fields)

    if not aggregate_selections:
        raise PlatformicsError("No aggregate functions selected")

    rows = await get_aggregate_db_rows(db.PerSectionParameters, session, authz_client, principal, where, aggregate_selections, [], groupby_selections)  # type: ignore
    aggregate_output = format_per_section_parameters_aggregate_output(rows)
    return aggregate_output


@strawberry.mutation(extensions=[DependencyExtension()])
async def create_per_section_parameters(
    input: PerSectionParametersCreateInput,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    is_system_user: bool = Depends(is_system_user),
) -> db.PerSectionParameters:
    """
    Create a new PerSectionParameters object. Used for mutations (see graphql_api/mutations.py).
    """
    validated = PerSectionParametersCreateInputValidator(**input.__dict__)
    params = validated.model_dump()

    # Validate that the user can read all of the entities they're linking to.

    # Validate that the user can read all of the entities they're linking to.
    # Check that frame relationship is accessible.
    if validated.frame_id:
        frame = await get_db_rows(
            db.Frame, session, authz_client, principal, {"id": {"_eq": validated.frame_id}}, [], AuthzAction.VIEW,
        )
        if not frame:
            raise PlatformicsError("Unauthorized: frame does not exist")
    # Check that run relationship is accessible.
    if validated.run_id:
        run = await get_db_rows(
            db.Run, session, authz_client, principal, {"id": {"_eq": validated.run_id}}, [], AuthzAction.VIEW,
        )
        if not run:
            raise PlatformicsError("Unauthorized: run does not exist")
    # Check that tiltseries relationship is accessible.
    if validated.tiltseries_id:
        tiltseries = await get_db_rows(
            db.Tiltseries,
            session,
            authz_client,
            principal,
            {"id": {"_eq": validated.tiltseries_id}},
            [],
            AuthzAction.VIEW,
        )
        if not tiltseries:
            raise PlatformicsError("Unauthorized: tiltseries does not exist")

    # Save to DB
    params["owner_user_id"] = int(principal.id)
    new_entity = db.PerSectionParameters(**params)

    # Are we actually allowed to create this entity?
    if not authz_client.can_create(new_entity, principal):
        raise PlatformicsError("Unauthorized: Cannot create entity")

    session.add(new_entity)
    await session.commit()
    return new_entity


@strawberry.mutation(extensions=[DependencyExtension()])
async def update_per_section_parameters(
    input: PerSectionParametersUpdateInput,
    where: PerSectionParametersWhereClauseMutations,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    is_system_user: bool = Depends(is_system_user),
) -> Sequence[db.PerSectionParameters]:
    """
    Update PerSectionParameters objects. Used for mutations (see graphql_api/mutations.py).
    """
    validated = PerSectionParametersUpdateInputValidator(**input.__dict__)
    params = validated.model_dump()

    # Need at least one thing to update
    num_params = len([x for x in params if params[x] is not None])
    if num_params == 0:
        raise PlatformicsError("No fields to update")

    # Validate that the user can read all of the entities they're linking to.
    # Check that frame relationship is accessible.
    if validated.frame_id:
        frame = await get_db_rows(
            db.Frame, session, authz_client, principal, {"id": {"_eq": validated.frame_id}}, [], AuthzAction.VIEW,
        )
        if not frame:
            raise PlatformicsError("Unauthorized: frame does not exist")
        params["frame"] = frame[0]
        del params["frame_id"]
    # Check that run relationship is accessible.
    if validated.run_id:
        run = await get_db_rows(
            db.Run, session, authz_client, principal, {"id": {"_eq": validated.run_id}}, [], AuthzAction.VIEW,
        )
        if not run:
            raise PlatformicsError("Unauthorized: run does not exist")
        params["run"] = run[0]
        del params["run_id"]
    # Check that tiltseries relationship is accessible.
    if validated.tiltseries_id:
        tiltseries = await get_db_rows(
            db.Tiltseries,
            session,
            authz_client,
            principal,
            {"id": {"_eq": validated.tiltseries_id}},
            [],
            AuthzAction.VIEW,
        )
        if not tiltseries:
            raise PlatformicsError("Unauthorized: tiltseries does not exist")
        params["tiltseries"] = tiltseries[0]
        del params["tiltseries_id"]

    # Fetch entities for update, if we have access to them
    entities = await get_db_rows(
        db.PerSectionParameters, session, authz_client, principal, where, [], AuthzAction.UPDATE,
    )
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
async def delete_per_section_parameters(
    where: PerSectionParametersWhereClauseMutations,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
) -> Sequence[db.PerSectionParameters]:
    """
    Delete PerSectionParameters objects. Used for mutations (see graphql_api/mutations.py).
    """
    # Fetch entities for deletion, if we have access to them
    entities = await get_db_rows(
        db.PerSectionParameters, session, authz_client, principal, where, [], AuthzAction.DELETE,
    )
    if len(entities) == 0:
        raise PlatformicsError("Unauthorized: Cannot delete entities")

    # Update DB
    for entity in entities:
        await session.delete(entity)
    await session.commit()
    return entities
