"""
GraphQL type for AnnotationFile

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
from graphql_api.helpers.annotation_file import AnnotationFileGroupByOptions, build_annotation_file_groupby_output
from sqlalchemy import inspect
from sqlalchemy.engine.row import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.types import Info
from support.enums import annotation_file_source_enum
from support.limit_offset import LimitOffsetClause
from typing_extensions import TypedDict
from validators.annotation_file import AnnotationFileCreateInputValidator, AnnotationFileUpdateInputValidator

from platformics.graphql_api.core.deps import get_authz_client, get_db_session, is_system_user, require_auth_principal
from platformics.graphql_api.core.errors import PlatformicsError
from platformics.graphql_api.core.query_builder import get_aggregate_db_rows, get_db_rows
from platformics.graphql_api.core.query_input_types import (
    BoolComparators,
    EnumComparators,
    IntComparators,
    StrComparators,
    aggregator_map,
    orderBy,
)
from platformics.graphql_api.core.relay_interface import EntityInterface
from platformics.graphql_api.core.strawberry_extensions import DependencyExtension
from platformics.security.authorization import AuthzAction, AuthzClient, Principal

E = typing.TypeVar("E")
T = typing.TypeVar("T")

if TYPE_CHECKING:
    from graphql_api.types.alignment import (
        Alignment,
        AlignmentAggregateWhereClause,
        AlignmentOrderByClause,
        AlignmentWhereClause,
    )
    from graphql_api.types.annotation_shape import (
        AnnotationShape,
        AnnotationShapeAggregateWhereClause,
        AnnotationShapeOrderByClause,
        AnnotationShapeWhereClause,
    )
    from graphql_api.types.tomogram_voxel_spacing import (
        TomogramVoxelSpacing,
        TomogramVoxelSpacingAggregateWhereClause,
        TomogramVoxelSpacingOrderByClause,
        TomogramVoxelSpacingWhereClause,
    )

    pass
else:
    AlignmentWhereClause = "AlignmentWhereClause"
    AlignmentAggregateWhereClause = "AlignmentAggregateWhereClause"
    Alignment = "Alignment"
    AlignmentOrderByClause = "AlignmentOrderByClause"
    AnnotationShapeWhereClause = "AnnotationShapeWhereClause"
    AnnotationShapeAggregateWhereClause = "AnnotationShapeAggregateWhereClause"
    AnnotationShape = "AnnotationShape"
    AnnotationShapeOrderByClause = "AnnotationShapeOrderByClause"
    TomogramVoxelSpacingWhereClause = "TomogramVoxelSpacingWhereClause"
    TomogramVoxelSpacingAggregateWhereClause = "TomogramVoxelSpacingAggregateWhereClause"
    TomogramVoxelSpacing = "TomogramVoxelSpacing"
    TomogramVoxelSpacingOrderByClause = "TomogramVoxelSpacingOrderByClause"
    pass


"""
------------------------------------------------------------------------------
Dataloaders
------------------------------------------------------------------------------
These are batching functions for loading related objects to avoid N+1 queries.
"""


@strawberry.field
async def load_alignment_rows(
    root: "AnnotationFile",
    info: Info,
    where: Annotated["AlignmentWhereClause", strawberry.lazy("graphql_api.types.alignment")] | None = None,
    order_by: Optional[list[Annotated["AlignmentOrderByClause", strawberry.lazy("graphql_api.types.alignment")]]] = [],
) -> Optional[Annotated["Alignment", strawberry.lazy("graphql_api.types.alignment")]]:
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.AnnotationFile)
    relationship = mapper.relationships["alignment"]
    return await dataloader.loader_for(relationship, where, order_by).load(root.alignment_id)  # type:ignore


@strawberry.field
async def load_annotation_shape_rows(
    root: "AnnotationFile",
    info: Info,
    where: Annotated["AnnotationShapeWhereClause", strawberry.lazy("graphql_api.types.annotation_shape")] | None = None,
    order_by: Optional[
        list[Annotated["AnnotationShapeOrderByClause", strawberry.lazy("graphql_api.types.annotation_shape")]]
    ] = [],
) -> Optional[Annotated["AnnotationShape", strawberry.lazy("graphql_api.types.annotation_shape")]]:
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.AnnotationFile)
    relationship = mapper.relationships["annotation_shape"]
    return await dataloader.loader_for(relationship, where, order_by).load(root.annotation_shape_id)  # type:ignore


@strawberry.field
async def load_tomogram_voxel_spacing_rows(
    root: "AnnotationFile",
    info: Info,
    where: (
        Annotated["TomogramVoxelSpacingWhereClause", strawberry.lazy("graphql_api.types.tomogram_voxel_spacing")] | None
    ) = None,
    order_by: Optional[
        list[
            Annotated["TomogramVoxelSpacingOrderByClause", strawberry.lazy("graphql_api.types.tomogram_voxel_spacing")]
        ]
    ] = [],
) -> Optional[Annotated["TomogramVoxelSpacing", strawberry.lazy("graphql_api.types.tomogram_voxel_spacing")]]:
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.AnnotationFile)
    relationship = mapper.relationships["tomogram_voxel_spacing"]
    return await dataloader.loader_for(relationship, where, order_by).load(
        root.tomogram_voxel_spacing_id,
    )  # type:ignore


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
class AnnotationFileWhereClauseMutations(TypedDict):
    id: IntComparators | None


"""
Supported WHERE clause attributes
"""


@strawberry.input
class AnnotationFileWhereClause(TypedDict):
    alignment: Optional[Annotated["AlignmentWhereClause", strawberry.lazy("graphql_api.types.alignment")]] | None
    alignment_id: Optional[IntComparators] | None
    annotation_shape: (
        Optional[Annotated["AnnotationShapeWhereClause", strawberry.lazy("graphql_api.types.annotation_shape")]] | None
    )
    annotation_shape_id: Optional[IntComparators] | None
    tomogram_voxel_spacing: (
        Optional[
            Annotated["TomogramVoxelSpacingWhereClause", strawberry.lazy("graphql_api.types.tomogram_voxel_spacing")]
        ]
        | None
    )
    tomogram_voxel_spacing_id: Optional[IntComparators] | None
    format: Optional[StrComparators] | None
    s3_path: Optional[StrComparators] | None
    file_size: Optional[IntComparators] | None
    https_path: Optional[StrComparators] | None
    is_visualization_default: Optional[BoolComparators] | None
    source: Optional[EnumComparators[annotation_file_source_enum]] | None
    id: Optional[IntComparators] | None


"""
Supported ORDER BY clause attributes
"""


@strawberry.input
class AnnotationFileOrderByClause(TypedDict):
    alignment: Optional[Annotated["AlignmentOrderByClause", strawberry.lazy("graphql_api.types.alignment")]] | None
    annotation_shape: (
        Optional[Annotated["AnnotationShapeOrderByClause", strawberry.lazy("graphql_api.types.annotation_shape")]]
        | None
    )
    tomogram_voxel_spacing: (
        Optional[
            Annotated["TomogramVoxelSpacingOrderByClause", strawberry.lazy("graphql_api.types.tomogram_voxel_spacing")]
        ]
        | None
    )
    format: Optional[orderBy] | None
    s3_path: Optional[orderBy] | None
    file_size: Optional[orderBy] | None
    https_path: Optional[orderBy] | None
    is_visualization_default: Optional[orderBy] | None
    source: Optional[orderBy] | None
    id: Optional[orderBy] | None


"""
Define AnnotationFile type
"""


@strawberry.type(description="Metadata for files associated with an annotation")
class AnnotationFile(EntityInterface):
    alignment: Optional[Annotated["Alignment", strawberry.lazy("graphql_api.types.alignment")]] = (
        load_alignment_rows
    )  # type:ignore
    alignment_id: Optional[int]
    annotation_shape: Optional[Annotated["AnnotationShape", strawberry.lazy("graphql_api.types.annotation_shape")]] = (
        load_annotation_shape_rows
    )  # type:ignore
    annotation_shape_id: Optional[int]
    tomogram_voxel_spacing: Optional[
        Annotated["TomogramVoxelSpacing", strawberry.lazy("graphql_api.types.tomogram_voxel_spacing")]
    ] = load_tomogram_voxel_spacing_rows  # type:ignore
    tomogram_voxel_spacing_id: Optional[int]
    format: str = strawberry.field(description="File format for this file")
    s3_path: str = strawberry.field(description="s3 path of the annotation file")
    file_size: Optional[int] = strawberry.field(description="Size of the file in bytes", default=None)
    https_path: str = strawberry.field(description="HTTPS path for this annotation file")
    is_visualization_default: Optional[bool] = strawberry.field(
        description="Data curator’s subjective choice of default annotation to display in visualization for an object",
        default=None,
    )
    source: Optional[annotation_file_source_enum] = strawberry.field(
        description="The source type for the annotation file (dataset_author, community, or portal_standard)",
        default=None,
    )
    id: int = strawberry.field(description="Numeric identifier (May change!)")


"""
We need to add this to each Queryable type so that strawberry will accept either our
Strawberry type *or* a SQLAlchemy model instance as a valid response class from a resolver
"""
AnnotationFile.__strawberry_definition__.is_type_of = (  # type: ignore
    lambda obj, info: type(obj) == db.AnnotationFile or type(obj) == AnnotationFile
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
class AnnotationFileNumericalColumns:
    file_size: Optional[int] = None
    id: Optional[int] = None


"""
Define columns that support min/max aggregations
"""


@strawberry.type
class AnnotationFileMinMaxColumns:
    format: Optional[str] = None
    s3_path: Optional[str] = None
    file_size: Optional[int] = None
    https_path: Optional[str] = None
    id: Optional[int] = None


"""
Define enum of all columns to support count and count(distinct) aggregations
"""


@strawberry.enum
class AnnotationFileCountColumns(enum.Enum):
    format = "format"
    s3Path = "s3_path"
    fileSize = "file_size"
    httpsPath = "https_path"
    isVisualizationDefault = "is_visualization_default"
    source = "source"
    id = "id"


"""
Support *filtering* on aggregates and related aggregates
"""


@strawberry.input
class AnnotationFileAggregateWhereClauseCount(TypedDict):
    arguments: Optional["AnnotationFileCountColumns"] | None
    distinct: Optional[bool] | None
    filter: Optional[AnnotationFileWhereClause] | None
    predicate: Optional[IntComparators] | None


@strawberry.input
class AnnotationFileAggregateWhereClause(TypedDict):
    count: AnnotationFileAggregateWhereClauseCount


"""
All supported aggregation functions
"""


@strawberry.type
class AnnotationFileAggregateFunctions:
    # This is a hack to accept "distinct" and "columns" as arguments to "count"
    @strawberry.field
    def count(
        self, distinct: Optional[bool] = False, columns: Optional[AnnotationFileCountColumns] = None,
    ) -> Optional[int]:
        # Count gets set with the proper value in the resolver, so we just return it here
        return self.count  # type: ignore

    sum: Optional[AnnotationFileNumericalColumns] = None
    avg: Optional[AnnotationFileNumericalColumns] = None
    stddev: Optional[AnnotationFileNumericalColumns] = None
    variance: Optional[AnnotationFileNumericalColumns] = None
    min: Optional[AnnotationFileMinMaxColumns] = None
    max: Optional[AnnotationFileMinMaxColumns] = None
    groupBy: Optional[AnnotationFileGroupByOptions] = None


"""
Wrapper around AnnotationFileAggregateFunctions
"""


@strawberry.type
class AnnotationFileAggregate:
    aggregate: Optional[list[AnnotationFileAggregateFunctions]] = None


"""
------------------------------------------------------------------------------
Mutation types
------------------------------------------------------------------------------
"""


@strawberry.input()
class AnnotationFileCreateInput:
    alignment_id: Optional[strawberry.ID] = strawberry.field(description="Tiltseries Alignment", default=None)
    annotation_shape_id: Optional[strawberry.ID] = strawberry.field(
        description="Shapes associated with an annotation", default=None,
    )
    tomogram_voxel_spacing_id: Optional[strawberry.ID] = strawberry.field(
        description="Voxel spacing that this annotation file is associated with", default=None,
    )
    format: str = strawberry.field(description="File format for this file")
    s3_path: str = strawberry.field(description="s3 path of the annotation file")
    file_size: Optional[int] = strawberry.field(description="Size of the file in bytes", default=None)
    https_path: str = strawberry.field(description="HTTPS path for this annotation file")
    is_visualization_default: Optional[bool] = strawberry.field(
        description="Data curator’s subjective choice of default annotation to display in visualization for an object",
        default=None,
    )
    source: Optional[annotation_file_source_enum] = strawberry.field(
        description="The source type for the annotation file (dataset_author, community, or portal_standard)",
        default=None,
    )
    id: int = strawberry.field(description="Numeric identifier (May change!)")


@strawberry.input()
class AnnotationFileUpdateInput:
    alignment_id: Optional[strawberry.ID] = strawberry.field(description="Tiltseries Alignment", default=None)
    annotation_shape_id: Optional[strawberry.ID] = strawberry.field(
        description="Shapes associated with an annotation", default=None,
    )
    tomogram_voxel_spacing_id: Optional[strawberry.ID] = strawberry.field(
        description="Voxel spacing that this annotation file is associated with", default=None,
    )
    format: Optional[str] = strawberry.field(description="File format for this file")
    s3_path: Optional[str] = strawberry.field(description="s3 path of the annotation file")
    file_size: Optional[int] = strawberry.field(description="Size of the file in bytes", default=None)
    https_path: Optional[str] = strawberry.field(description="HTTPS path for this annotation file")
    is_visualization_default: Optional[bool] = strawberry.field(
        description="Data curator’s subjective choice of default annotation to display in visualization for an object",
        default=None,
    )
    source: Optional[annotation_file_source_enum] = strawberry.field(
        description="The source type for the annotation file (dataset_author, community, or portal_standard)",
        default=None,
    )
    id: Optional[int] = strawberry.field(description="Numeric identifier (May change!)")


"""
------------------------------------------------------------------------------
Utilities
------------------------------------------------------------------------------
"""


@strawberry.field(extensions=[DependencyExtension()])
async def resolve_annotation_files(
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    where: Optional[AnnotationFileWhereClause] = None,
    order_by: Optional[list[AnnotationFileOrderByClause]] = [],
    limit_offset: Optional[LimitOffsetClause] = None,
) -> typing.Sequence[AnnotationFile]:
    """
    Resolve AnnotationFile objects. Used for queries (see graphql_api/queries.py).
    """
    limit = limit_offset["limit"] if limit_offset and "limit" in limit_offset else None
    offset = limit_offset["offset"] if limit_offset and "offset" in limit_offset else None
    if offset and not limit:
        raise PlatformicsError("Cannot use offset without limit")
    return await get_db_rows(db.AnnotationFile, session, authz_client, principal, where, order_by, AuthzAction.VIEW, limit, offset)  # type: ignore


def format_annotation_file_aggregate_output(
    query_results: Sequence[RowMapping] | RowMapping,
) -> AnnotationFileAggregate:
    """
    Given a row from the DB containing the results of an aggregate query,
    format the results using the proper GraphQL types.
    """
    aggregate = []
    if type(query_results) is not list:
        query_results = [query_results]  # type: ignore
    for row in query_results:
        aggregate.append(format_annotation_file_aggregate_row(row))
    return AnnotationFileAggregate(aggregate=aggregate)


def format_annotation_file_aggregate_row(row: RowMapping) -> AnnotationFileAggregateFunctions:
    """
    Given a single row from the DB containing the results of an aggregate query,
    format the results using the proper GraphQL types.
    """
    output = AnnotationFileAggregateFunctions()
    for key, value in row.items():
        # Key is either an aggregate function or a groupby key
        group_keys = key.split(".")
        aggregate = key.split("_", 1)
        if aggregate[0] not in aggregator_map.keys():
            # Turn list of groupby keys into nested objects
            if not output.groupBy:
                output.groupBy = AnnotationFileGroupByOptions()
            group = build_annotation_file_groupby_output(output.groupBy, group_keys, value)
            output.groupBy = group
        else:
            aggregate_name = aggregate[0]
            if aggregate_name == "count":
                output.count = value
            else:
                aggregator_fn, col_name = aggregate[0], aggregate[1]
                if not getattr(output, aggregator_fn):
                    if aggregate_name in ["min", "max"]:
                        setattr(output, aggregator_fn, AnnotationFileMinMaxColumns())
                    else:
                        setattr(output, aggregator_fn, AnnotationFileNumericalColumns())
                setattr(getattr(output, aggregator_fn), col_name, value)
    return output


@strawberry.field(extensions=[DependencyExtension()])
async def resolve_annotation_files_aggregate(
    info: Info,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    where: Optional[AnnotationFileWhereClause] = None,
    # TODO: add support for groupby, limit/offset
) -> AnnotationFileAggregate:
    """
    Aggregate values for AnnotationFile objects. Used for queries (see graphql_api/queries.py).
    """
    # Get the selected aggregate functions and columns to operate on, and groupby options if any were provided.
    # TODO: not sure why selected_fields is a list
    selections = info.selected_fields[0].selections[0].selections
    aggregate_selections = [selection for selection in selections if selection.name != "groupBy"]
    groupby_selections = [selection for selection in selections if selection.name == "groupBy"]
    groupby_selections = groupby_selections[0].selections if groupby_selections else []

    if not aggregate_selections:
        raise PlatformicsError("No aggregate functions selected")

    rows = await get_aggregate_db_rows(db.AnnotationFile, session, authz_client, principal, where, aggregate_selections, [], groupby_selections)  # type: ignore
    aggregate_output = format_annotation_file_aggregate_output(rows)
    return aggregate_output


@strawberry.mutation(extensions=[DependencyExtension()])
async def create_annotation_file(
    input: AnnotationFileCreateInput,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    is_system_user: bool = Depends(is_system_user),
) -> db.AnnotationFile:
    """
    Create a new AnnotationFile object. Used for mutations (see graphql_api/mutations.py).
    """
    validated = AnnotationFileCreateInputValidator(**input.__dict__)
    params = validated.model_dump()

    # Validate that the user can read all of the entities they're linking to.

    # Validate that the user can read all of the entities they're linking to.
    # Check that alignment relationship is accessible.
    if validated.alignment_id:
        alignment = await get_db_rows(
            db.Alignment,
            session,
            authz_client,
            principal,
            {"id": {"_eq": validated.alignment_id}},
            [],
            AuthzAction.VIEW,
        )
        if not alignment:
            raise PlatformicsError("Unauthorized: alignment does not exist")
    # Check that annotation_shape relationship is accessible.
    if validated.annotation_shape_id:
        annotation_shape = await get_db_rows(
            db.AnnotationShape,
            session,
            authz_client,
            principal,
            {"id": {"_eq": validated.annotation_shape_id}},
            [],
            AuthzAction.VIEW,
        )
        if not annotation_shape:
            raise PlatformicsError("Unauthorized: annotation_shape does not exist")
    # Check that tomogram_voxel_spacing relationship is accessible.
    if validated.tomogram_voxel_spacing_id:
        tomogram_voxel_spacing = await get_db_rows(
            db.TomogramVoxelSpacing,
            session,
            authz_client,
            principal,
            {"id": {"_eq": validated.tomogram_voxel_spacing_id}},
            [],
            AuthzAction.VIEW,
        )
        if not tomogram_voxel_spacing:
            raise PlatformicsError("Unauthorized: tomogram_voxel_spacing does not exist")

    # Save to DB
    params["owner_user_id"] = int(principal.id)
    new_entity = db.AnnotationFile(**params)

    # Are we actually allowed to create this entity?
    if not authz_client.can_create(new_entity, principal):
        raise PlatformicsError("Unauthorized: Cannot create entity")

    session.add(new_entity)
    await session.commit()
    return new_entity


@strawberry.mutation(extensions=[DependencyExtension()])
async def update_annotation_file(
    input: AnnotationFileUpdateInput,
    where: AnnotationFileWhereClauseMutations,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    is_system_user: bool = Depends(is_system_user),
) -> Sequence[db.AnnotationFile]:
    """
    Update AnnotationFile objects. Used for mutations (see graphql_api/mutations.py).
    """
    validated = AnnotationFileUpdateInputValidator(**input.__dict__)
    params = validated.model_dump()

    # Need at least one thing to update
    num_params = len([x for x in params if params[x] is not None])
    if num_params == 0:
        raise PlatformicsError("No fields to update")

    # Validate that the user can read all of the entities they're linking to.
    # Check that alignment relationship is accessible.
    if validated.alignment_id:
        alignment = await get_db_rows(
            db.Alignment,
            session,
            authz_client,
            principal,
            {"id": {"_eq": validated.alignment_id}},
            [],
            AuthzAction.VIEW,
        )
        if not alignment:
            raise PlatformicsError("Unauthorized: alignment does not exist")
        params["alignment"] = alignment[0]
        del params["alignment_id"]
    # Check that annotation_shape relationship is accessible.
    if validated.annotation_shape_id:
        annotation_shape = await get_db_rows(
            db.AnnotationShape,
            session,
            authz_client,
            principal,
            {"id": {"_eq": validated.annotation_shape_id}},
            [],
            AuthzAction.VIEW,
        )
        if not annotation_shape:
            raise PlatformicsError("Unauthorized: annotation_shape does not exist")
        params["annotation_shape"] = annotation_shape[0]
        del params["annotation_shape_id"]
    # Check that tomogram_voxel_spacing relationship is accessible.
    if validated.tomogram_voxel_spacing_id:
        tomogram_voxel_spacing = await get_db_rows(
            db.TomogramVoxelSpacing,
            session,
            authz_client,
            principal,
            {"id": {"_eq": validated.tomogram_voxel_spacing_id}},
            [],
            AuthzAction.VIEW,
        )
        if not tomogram_voxel_spacing:
            raise PlatformicsError("Unauthorized: tomogram_voxel_spacing does not exist")
        params["tomogram_voxel_spacing"] = tomogram_voxel_spacing[0]
        del params["tomogram_voxel_spacing_id"]

    # Fetch entities for update, if we have access to them
    entities = await get_db_rows(db.AnnotationFile, session, authz_client, principal, where, [], AuthzAction.UPDATE)
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
async def delete_annotation_file(
    where: AnnotationFileWhereClauseMutations,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
) -> Sequence[db.AnnotationFile]:
    """
    Delete AnnotationFile objects. Used for mutations (see graphql_api/mutations.py).
    """
    # Fetch entities for deletion, if we have access to them
    entities = await get_db_rows(db.AnnotationFile, session, authz_client, principal, where, [], AuthzAction.DELETE)
    if len(entities) == 0:
        raise PlatformicsError("Unauthorized: Cannot delete entities")

    # Update DB
    for entity in entities:
        await session.delete(entity)
    await session.commit()
    return entities
