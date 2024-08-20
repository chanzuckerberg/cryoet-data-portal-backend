"""
GraphQL type for Alignment

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
from graphql_api.helpers.alignment import AlignmentGroupByOptions, build_alignment_groupby_output
from graphql_api.types.annotation_file import AnnotationFileAggregate, format_annotation_file_aggregate_output
from graphql_api.types.per_section_alignment_parameters import (
    PerSectionAlignmentParametersAggregate,
    format_per_section_alignment_parameters_aggregate_output,
)
from graphql_api.types.tomogram import TomogramAggregate, format_tomogram_aggregate_output
from platformics.graphql_api.core.deps import get_authz_client, get_db_session, is_system_user, require_auth_principal
from platformics.graphql_api.core.errors import PlatformicsError
from platformics.graphql_api.core.query_builder import get_aggregate_db_rows, get_db_rows
from platformics.graphql_api.core.query_input_types import (
    EnumComparators,
    FloatComparators,
    IntComparators,
    StrComparators,
    aggregator_map,
    orderBy,
)
from platformics.graphql_api.core.relay_interface import EntityInterface
from platformics.graphql_api.core.strawberry_extensions import DependencyExtension
from platformics.security.authorization import AuthzAction, AuthzClient, Principal
from sqlalchemy import inspect
from sqlalchemy.engine.row import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry import relay
from strawberry.types import Info
from support.enums import alignment_type_enum
from support.limit_offset import LimitOffsetClause
from typing_extensions import TypedDict
from validators.alignment import AlignmentCreateInputValidator, AlignmentUpdateInputValidator

E = typing.TypeVar("E")
T = typing.TypeVar("T")

if TYPE_CHECKING:
    from graphql_api.types.annotation_file import AnnotationFile, AnnotationFileOrderByClause, AnnotationFileWhereClause
    from graphql_api.types.deposition import Deposition, DepositionOrderByClause, DepositionWhereClause
    from graphql_api.types.per_section_alignment_parameters import (
        PerSectionAlignmentParameters,
        PerSectionAlignmentParametersOrderByClause,
        PerSectionAlignmentParametersWhereClause,
    )
    from graphql_api.types.run import Run, RunOrderByClause, RunWhereClause
    from graphql_api.types.tiltseries import Tiltseries, TiltseriesOrderByClause, TiltseriesWhereClause
    from graphql_api.types.tomogram import Tomogram, TomogramOrderByClause, TomogramWhereClause

    pass
else:
    AnnotationFileWhereClause = "AnnotationFileWhereClause"
    AnnotationFile = "AnnotationFile"
    AnnotationFileOrderByClause = "AnnotationFileOrderByClause"
    PerSectionAlignmentParametersWhereClause = "PerSectionAlignmentParametersWhereClause"
    PerSectionAlignmentParameters = "PerSectionAlignmentParameters"
    PerSectionAlignmentParametersOrderByClause = "PerSectionAlignmentParametersOrderByClause"
    DepositionWhereClause = "DepositionWhereClause"
    Deposition = "Deposition"
    DepositionOrderByClause = "DepositionOrderByClause"
    TiltseriesWhereClause = "TiltseriesWhereClause"
    Tiltseries = "Tiltseries"
    TiltseriesOrderByClause = "TiltseriesOrderByClause"
    TomogramWhereClause = "TomogramWhereClause"
    Tomogram = "Tomogram"
    TomogramOrderByClause = "TomogramOrderByClause"
    RunWhereClause = "RunWhereClause"
    Run = "Run"
    RunOrderByClause = "RunOrderByClause"
    pass


"""
------------------------------------------------------------------------------
Dataloaders
------------------------------------------------------------------------------
These are batching functions for loading related objects to avoid N+1 queries.
"""


@relay.connection(
    relay.ListConnection[
        Annotated["AnnotationFile", strawberry.lazy("graphql_api.types.annotation_file")]
    ],  # type:ignore
)
async def load_annotation_file_rows(
    root: "Alignment",
    info: Info,
    where: Annotated["AnnotationFileWhereClause", strawberry.lazy("graphql_api.types.annotation_file")] | None = None,
    order_by: Optional[
        list[Annotated["AnnotationFileOrderByClause", strawberry.lazy("graphql_api.types.annotation_file")]]
    ] = [],
) -> Sequence[Annotated["AnnotationFile", strawberry.lazy("graphql_api.types.annotation_file")]]:
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Alignment)
    relationship = mapper.relationships["annotation_files"]
    return await dataloader.loader_for(relationship, where, order_by).load(root.id)  # type:ignore


@strawberry.field
async def load_annotation_file_aggregate_rows(
    root: "Alignment",
    info: Info,
    where: Annotated["AnnotationFileWhereClause", strawberry.lazy("graphql_api.types.annotation_file")] | None = None,
) -> Optional[Annotated["AnnotationFileAggregate", strawberry.lazy("graphql_api.types.annotation_file")]]:
    selections = info.selected_fields[0].selections[0].selections
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Alignment)
    relationship = mapper.relationships["annotation_files"]
    rows = await dataloader.aggregate_loader_for(relationship, where, selections).load(root.id)  # type:ignore
    aggregate_output = format_annotation_file_aggregate_output(rows)
    return aggregate_output


@relay.connection(
    relay.ListConnection[
        Annotated[
            "PerSectionAlignmentParameters",
            strawberry.lazy("graphql_api.types.per_section_alignment_parameters"),
        ]
    ],  # type:ignore
)
async def load_per_section_alignment_parameters_rows(
    root: "Alignment",
    info: Info,
    where: (
        Annotated[
            "PerSectionAlignmentParametersWhereClause",
            strawberry.lazy("graphql_api.types.per_section_alignment_parameters"),
        ]
        | None
    ) = None,
    order_by: Optional[
        list[
            Annotated[
                "PerSectionAlignmentParametersOrderByClause",
                strawberry.lazy("graphql_api.types.per_section_alignment_parameters"),
            ]
        ]
    ] = [],
) -> Sequence[
    Annotated["PerSectionAlignmentParameters", strawberry.lazy("graphql_api.types.per_section_alignment_parameters")]
]:
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Alignment)
    relationship = mapper.relationships["per_section_alignments"]
    return await dataloader.loader_for(relationship, where, order_by).load(root.id)  # type:ignore


@strawberry.field
async def load_per_section_alignment_parameters_aggregate_rows(
    root: "Alignment",
    info: Info,
    where: (
        Annotated[
            "PerSectionAlignmentParametersWhereClause",
            strawberry.lazy("graphql_api.types.per_section_alignment_parameters"),
        ]
        | None
    ) = None,
) -> Optional[
    Annotated[
        "PerSectionAlignmentParametersAggregate",
        strawberry.lazy("graphql_api.types.per_section_alignment_parameters"),
    ]
]:
    selections = info.selected_fields[0].selections[0].selections
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Alignment)
    relationship = mapper.relationships["per_section_alignments"]
    rows = await dataloader.aggregate_loader_for(relationship, where, selections).load(root.id)  # type:ignore
    aggregate_output = format_per_section_alignment_parameters_aggregate_output(rows)
    return aggregate_output


@strawberry.field
async def load_deposition_rows(
    root: "Alignment",
    info: Info,
    where: Annotated["DepositionWhereClause", strawberry.lazy("graphql_api.types.deposition")] | None = None,
    order_by: Optional[
        list[Annotated["DepositionOrderByClause", strawberry.lazy("graphql_api.types.deposition")]]
    ] = [],
) -> Optional[Annotated["Deposition", strawberry.lazy("graphql_api.types.deposition")]]:
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Alignment)
    relationship = mapper.relationships["deposition"]
    return await dataloader.loader_for(relationship, where, order_by).load(root.deposition_id)  # type:ignore


@strawberry.field
async def load_tiltseries_rows(
    root: "Alignment",
    info: Info,
    where: Annotated["TiltseriesWhereClause", strawberry.lazy("graphql_api.types.tiltseries")] | None = None,
    order_by: Optional[
        list[Annotated["TiltseriesOrderByClause", strawberry.lazy("graphql_api.types.tiltseries")]]
    ] = [],
) -> Optional[Annotated["Tiltseries", strawberry.lazy("graphql_api.types.tiltseries")]]:
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Alignment)
    relationship = mapper.relationships["tiltseries"]
    return await dataloader.loader_for(relationship, where, order_by).load(root.tiltseries_id)  # type:ignore


@relay.connection(
    relay.ListConnection[Annotated["Tomogram", strawberry.lazy("graphql_api.types.tomogram")]],  # type:ignore
)
async def load_tomogram_rows(
    root: "Alignment",
    info: Info,
    where: Annotated["TomogramWhereClause", strawberry.lazy("graphql_api.types.tomogram")] | None = None,
    order_by: Optional[list[Annotated["TomogramOrderByClause", strawberry.lazy("graphql_api.types.tomogram")]]] = [],
) -> Sequence[Annotated["Tomogram", strawberry.lazy("graphql_api.types.tomogram")]]:
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Alignment)
    relationship = mapper.relationships["tomograms"]
    return await dataloader.loader_for(relationship, where, order_by).load(root.id)  # type:ignore


@strawberry.field
async def load_tomogram_aggregate_rows(
    root: "Alignment",
    info: Info,
    where: Annotated["TomogramWhereClause", strawberry.lazy("graphql_api.types.tomogram")] | None = None,
) -> Optional[Annotated["TomogramAggregate", strawberry.lazy("graphql_api.types.tomogram")]]:
    selections = info.selected_fields[0].selections[0].selections
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Alignment)
    relationship = mapper.relationships["tomograms"]
    rows = await dataloader.aggregate_loader_for(relationship, where, selections).load(root.id)  # type:ignore
    aggregate_output = format_tomogram_aggregate_output(rows)
    return aggregate_output


@strawberry.field
async def load_run_rows(
    root: "Alignment",
    info: Info,
    where: Annotated["RunWhereClause", strawberry.lazy("graphql_api.types.run")] | None = None,
    order_by: Optional[list[Annotated["RunOrderByClause", strawberry.lazy("graphql_api.types.run")]]] = [],
) -> Optional[Annotated["Run", strawberry.lazy("graphql_api.types.run")]]:
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Alignment)
    relationship = mapper.relationships["run"]
    return await dataloader.loader_for(relationship, where, order_by).load(root.run_id)  # type:ignore


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
class AlignmentWhereClauseMutations(TypedDict):
    id: IntComparators | None


"""
Supported WHERE clause attributes
"""


@strawberry.input
class AlignmentWhereClause(TypedDict):
    annotation_files: (
        Optional[Annotated["AnnotationFileWhereClause", strawberry.lazy("graphql_api.types.annotation_file")]] | None
    )
    per_section_alignments: (
        Optional[
            Annotated[
                "PerSectionAlignmentParametersWhereClause",
                strawberry.lazy("graphql_api.types.per_section_alignment_parameters"),
            ]
        ]
        | None
    )
    deposition: Optional[Annotated["DepositionWhereClause", strawberry.lazy("graphql_api.types.deposition")]] | None
    tiltseries: Optional[Annotated["TiltseriesWhereClause", strawberry.lazy("graphql_api.types.tiltseries")]] | None
    tomograms: Optional[Annotated["TomogramWhereClause", strawberry.lazy("graphql_api.types.tomogram")]] | None
    run: Optional[Annotated["RunWhereClause", strawberry.lazy("graphql_api.types.run")]] | None
    alignment: Optional[StrComparators] | None
    alignment_type: Optional[EnumComparators[alignment_type_enum]] | None
    volume_x_dimension: Optional[FloatComparators] | None
    volume_y_dimension: Optional[FloatComparators] | None
    volume_z_dimension: Optional[FloatComparators] | None
    volume_x_offset: Optional[FloatComparators] | None
    volume_y_offset: Optional[FloatComparators] | None
    volume_z_offset: Optional[FloatComparators] | None
    volume_x_rotation: Optional[FloatComparators] | None
    tilt_offset: Optional[FloatComparators] | None
    local_alignment_file: Optional[StrComparators] | None
    id: Optional[IntComparators] | None


"""
Supported ORDER BY clause attributes
"""


@strawberry.input
class AlignmentOrderByClause(TypedDict):
    deposition: Optional[Annotated["DepositionOrderByClause", strawberry.lazy("graphql_api.types.deposition")]] | None
    tiltseries: Optional[Annotated["TiltseriesOrderByClause", strawberry.lazy("graphql_api.types.tiltseries")]] | None
    run: Optional[Annotated["RunOrderByClause", strawberry.lazy("graphql_api.types.run")]] | None
    alignment: Optional[orderBy] | None
    alignment_type: Optional[orderBy] | None
    volume_x_dimension: Optional[orderBy] | None
    volume_y_dimension: Optional[orderBy] | None
    volume_z_dimension: Optional[orderBy] | None
    volume_x_offset: Optional[orderBy] | None
    volume_y_offset: Optional[orderBy] | None
    volume_z_offset: Optional[orderBy] | None
    volume_x_rotation: Optional[orderBy] | None
    tilt_offset: Optional[orderBy] | None
    local_alignment_file: Optional[orderBy] | None
    id: Optional[orderBy] | None


"""
Define Alignment type
"""


@strawberry.type(description="Tiltseries Alignment")
class Alignment(EntityInterface):
    annotation_files: Sequence[Annotated["AnnotationFile", strawberry.lazy("graphql_api.types.annotation_file")]] = (
        load_annotation_file_rows
    )  # type:ignore
    annotation_files_aggregate: Optional[
        Annotated["AnnotationFileAggregate", strawberry.lazy("graphql_api.types.annotation_file")]
    ] = load_annotation_file_aggregate_rows  # type:ignore
    per_section_alignments: Sequence[
        Annotated[
            "PerSectionAlignmentParameters",
            strawberry.lazy("graphql_api.types.per_section_alignment_parameters"),
        ]
    ] = load_per_section_alignment_parameters_rows  # type:ignore
    per_section_alignments_aggregate: Optional[
        Annotated[
            "PerSectionAlignmentParametersAggregate",
            strawberry.lazy("graphql_api.types.per_section_alignment_parameters"),
        ]
    ] = load_per_section_alignment_parameters_aggregate_rows  # type:ignore
    deposition: Optional[Annotated["Deposition", strawberry.lazy("graphql_api.types.deposition")]] = (
        load_deposition_rows
    )  # type:ignore
    tiltseries: Optional[Annotated["Tiltseries", strawberry.lazy("graphql_api.types.tiltseries")]] = (
        load_tiltseries_rows
    )  # type:ignore
    tomograms: Sequence[Annotated["Tomogram", strawberry.lazy("graphql_api.types.tomogram")]] = (
        load_tomogram_rows
    )  # type:ignore
    tomograms_aggregate: Optional[Annotated["TomogramAggregate", strawberry.lazy("graphql_api.types.tomogram")]] = (
        load_tomogram_aggregate_rows
    )  # type:ignore
    run: Optional[Annotated["Run", strawberry.lazy("graphql_api.types.run")]] = load_run_rows  # type:ignore
    alignment: str = strawberry.field(description="Describe a tiltseries alignment")
    alignment_type: Optional[alignment_type_enum] = strawberry.field(
        description="Type of alignment included, i.e. is a non-rigid alignment included?",
        default=None,
    )
    volume_x_dimension: Optional[float] = strawberry.field(
        description="X dimension of the reconstruction volume in angstrom",
        default=None,
    )
    volume_y_dimension: Optional[float] = strawberry.field(
        description="Y dimension of the reconstruction volume in angstrom",
        default=None,
    )
    volume_z_dimension: Optional[float] = strawberry.field(
        description="Z dimension of the reconstruction volume in angstrom",
        default=None,
    )
    volume_x_offset: Optional[float] = strawberry.field(
        description="X shift of the reconstruction volume in angstrom",
        default=None,
    )
    volume_y_offset: Optional[float] = strawberry.field(
        description="Y shift of the reconstruction volume in angstrom",
        default=None,
    )
    volume_z_offset: Optional[float] = strawberry.field(
        description="Z shift of the reconstruction volume in angstrom",
        default=None,
    )
    volume_x_rotation: Optional[float] = strawberry.field(
        description="Additional X rotation of the reconstruction volume in degrees",
        default=None,
    )
    tilt_offset: Optional[float] = strawberry.field(description="Additional tilt offset in degrees", default=None)
    local_alignment_file: Optional[str] = strawberry.field(description="Path to the local alignment file", default=None)
    id: int = strawberry.field(description="An identifier to refer to a specific instance of this type")


"""
We need to add this to each Queryable type so that strawberry will accept either our
Strawberry type *or* a SQLAlchemy model instance as a valid response class from a resolver
"""
Alignment.__strawberry_definition__.is_type_of = (  # type: ignore
    lambda obj, info: type(obj) == db.Alignment or type(obj) == Alignment
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
class AlignmentNumericalColumns:
    volume_x_dimension: Optional[float] = None
    volume_y_dimension: Optional[float] = None
    volume_z_dimension: Optional[float] = None
    volume_x_offset: Optional[float] = None
    volume_y_offset: Optional[float] = None
    volume_z_offset: Optional[float] = None
    volume_x_rotation: Optional[float] = None
    tilt_offset: Optional[float] = None
    id: Optional[int] = None


"""
Define columns that support min/max aggregations
"""


@strawberry.type
class AlignmentMinMaxColumns:
    alignment: Optional[str] = None
    volume_x_dimension: Optional[float] = None
    volume_y_dimension: Optional[float] = None
    volume_z_dimension: Optional[float] = None
    volume_x_offset: Optional[float] = None
    volume_y_offset: Optional[float] = None
    volume_z_offset: Optional[float] = None
    volume_x_rotation: Optional[float] = None
    tilt_offset: Optional[float] = None
    local_alignment_file: Optional[str] = None
    id: Optional[int] = None


"""
Define enum of all columns to support count and count(distinct) aggregations
"""


@strawberry.enum
class AlignmentCountColumns(enum.Enum):
    annotationFiles = "annotation_files"
    perSectionAlignments = "per_section_alignments"
    deposition = "deposition"
    tiltseries = "tiltseries"
    tomograms = "tomograms"
    run = "run"
    alignment = "alignment"
    alignmentType = "alignment_type"
    volumeXDimension = "volume_x_dimension"
    volumeYDimension = "volume_y_dimension"
    volumeZDimension = "volume_z_dimension"
    volumeXOffset = "volume_x_offset"
    volumeYOffset = "volume_y_offset"
    volumeZOffset = "volume_z_offset"
    volumeXRotation = "volume_x_rotation"
    tiltOffset = "tilt_offset"
    localAlignmentFile = "local_alignment_file"
    id = "id"


"""
All supported aggregation functions
"""


@strawberry.type
class AlignmentAggregateFunctions:
    # This is a hack to accept "distinct" and "columns" as arguments to "count"
    @strawberry.field
    def count(self, distinct: Optional[bool] = False, columns: Optional[AlignmentCountColumns] = None) -> Optional[int]:
        # Count gets set with the proper value in the resolver, so we just return it here
        return self.count  # type: ignore

    sum: Optional[AlignmentNumericalColumns] = None
    avg: Optional[AlignmentNumericalColumns] = None
    stddev: Optional[AlignmentNumericalColumns] = None
    variance: Optional[AlignmentNumericalColumns] = None
    min: Optional[AlignmentMinMaxColumns] = None
    max: Optional[AlignmentMinMaxColumns] = None
    groupBy: Optional[AlignmentGroupByOptions] = None


"""
Wrapper around AlignmentAggregateFunctions
"""


@strawberry.type
class AlignmentAggregate:
    aggregate: Optional[list[AlignmentAggregateFunctions]] = None


"""
------------------------------------------------------------------------------
Mutation types
------------------------------------------------------------------------------
"""


@strawberry.input()
class AlignmentCreateInput:
    deposition_id: Optional[strawberry.ID] = strawberry.field(description=None, default=None)
    tiltseries_id: Optional[strawberry.ID] = strawberry.field(description=None, default=None)
    run_id: Optional[strawberry.ID] = strawberry.field(description=None, default=None)
    alignment: str = strawberry.field(description="Describe a tiltseries alignment")
    alignment_type: Optional[alignment_type_enum] = strawberry.field(
        description="Type of alignment included, i.e. is a non-rigid alignment included?",
        default=None,
    )
    volume_x_dimension: Optional[float] = strawberry.field(
        description="X dimension of the reconstruction volume in angstrom",
        default=None,
    )
    volume_y_dimension: Optional[float] = strawberry.field(
        description="Y dimension of the reconstruction volume in angstrom",
        default=None,
    )
    volume_z_dimension: Optional[float] = strawberry.field(
        description="Z dimension of the reconstruction volume in angstrom",
        default=None,
    )
    volume_x_offset: Optional[float] = strawberry.field(
        description="X shift of the reconstruction volume in angstrom",
        default=None,
    )
    volume_y_offset: Optional[float] = strawberry.field(
        description="Y shift of the reconstruction volume in angstrom",
        default=None,
    )
    volume_z_offset: Optional[float] = strawberry.field(
        description="Z shift of the reconstruction volume in angstrom",
        default=None,
    )
    volume_x_rotation: Optional[float] = strawberry.field(
        description="Additional X rotation of the reconstruction volume in degrees",
        default=None,
    )
    tilt_offset: Optional[float] = strawberry.field(description="Additional tilt offset in degrees", default=None)
    local_alignment_file: Optional[str] = strawberry.field(description="Path to the local alignment file", default=None)
    id: int = strawberry.field(description="An identifier to refer to a specific instance of this type")


@strawberry.input()
class AlignmentUpdateInput:
    deposition_id: Optional[strawberry.ID] = strawberry.field(description=None, default=None)
    tiltseries_id: Optional[strawberry.ID] = strawberry.field(description=None, default=None)
    run_id: Optional[strawberry.ID] = strawberry.field(description=None, default=None)
    alignment: Optional[str] = strawberry.field(description="Describe a tiltseries alignment")
    alignment_type: Optional[alignment_type_enum] = strawberry.field(
        description="Type of alignment included, i.e. is a non-rigid alignment included?",
        default=None,
    )
    volume_x_dimension: Optional[float] = strawberry.field(
        description="X dimension of the reconstruction volume in angstrom",
        default=None,
    )
    volume_y_dimension: Optional[float] = strawberry.field(
        description="Y dimension of the reconstruction volume in angstrom",
        default=None,
    )
    volume_z_dimension: Optional[float] = strawberry.field(
        description="Z dimension of the reconstruction volume in angstrom",
        default=None,
    )
    volume_x_offset: Optional[float] = strawberry.field(
        description="X shift of the reconstruction volume in angstrom",
        default=None,
    )
    volume_y_offset: Optional[float] = strawberry.field(
        description="Y shift of the reconstruction volume in angstrom",
        default=None,
    )
    volume_z_offset: Optional[float] = strawberry.field(
        description="Z shift of the reconstruction volume in angstrom",
        default=None,
    )
    volume_x_rotation: Optional[float] = strawberry.field(
        description="Additional X rotation of the reconstruction volume in degrees",
        default=None,
    )
    tilt_offset: Optional[float] = strawberry.field(description="Additional tilt offset in degrees", default=None)
    local_alignment_file: Optional[str] = strawberry.field(description="Path to the local alignment file", default=None)
    id: Optional[int] = strawberry.field(description="An identifier to refer to a specific instance of this type")


"""
------------------------------------------------------------------------------
Utilities
------------------------------------------------------------------------------
"""


@strawberry.field(extensions=[DependencyExtension()])
async def resolve_alignments(
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    where: Optional[AlignmentWhereClause] = None,
    order_by: Optional[list[AlignmentOrderByClause]] = [],
    limit_offset: Optional[LimitOffsetClause] = None,
) -> typing.Sequence[Alignment]:
    """
    Resolve Alignment objects. Used for queries (see graphql_api/queries.py).
    """
    limit = limit_offset["limit"] if limit_offset and "limit" in limit_offset else None
    offset = limit_offset["offset"] if limit_offset and "offset" in limit_offset else None
    if offset and not limit:
        raise PlatformicsError("Cannot use offset without limit")
    return await get_db_rows(db.Alignment, session, authz_client, principal, where, order_by, AuthzAction.VIEW, limit, offset)  # type: ignore


def format_alignment_aggregate_output(query_results: Sequence[RowMapping] | RowMapping) -> AlignmentAggregate:
    """
    Given a row from the DB containing the results of an aggregate query,
    format the results using the proper GraphQL types.
    """
    aggregate = []
    if type(query_results) is not list:
        query_results = [query_results]  # type: ignore
    for row in query_results:
        aggregate.append(format_alignment_aggregate_row(row))
    return AlignmentAggregate(aggregate=aggregate)


def format_alignment_aggregate_row(row: RowMapping) -> AlignmentAggregateFunctions:
    """
    Given a single row from the DB containing the results of an aggregate query,
    format the results using the proper GraphQL types.
    """
    output = AlignmentAggregateFunctions()
    for key, value in row.items():
        # Key is either an aggregate function or a groupby key
        group_keys = key.split(".")
        aggregate = key.split("_", 1)
        if aggregate[0] not in aggregator_map.keys():
            # Turn list of groupby keys into nested objects
            if not output.groupBy:
                output.groupBy = AlignmentGroupByOptions()
            group = build_alignment_groupby_output(output.groupBy, group_keys, value)
            output.groupBy = group
        else:
            aggregate_name = aggregate[0]
            if aggregate_name == "count":
                output.count = value
            else:
                aggregator_fn, col_name = aggregate[0], aggregate[1]
                if not getattr(output, aggregator_fn):
                    if aggregate_name in ["min", "max"]:
                        setattr(output, aggregator_fn, AlignmentMinMaxColumns())
                    else:
                        setattr(output, aggregator_fn, AlignmentNumericalColumns())
                setattr(getattr(output, aggregator_fn), col_name, value)
    return output


@strawberry.field(extensions=[DependencyExtension()])
async def resolve_alignments_aggregate(
    info: Info,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    where: Optional[AlignmentWhereClause] = None,
    # TODO: add support for groupby, limit/offset
) -> AlignmentAggregate:
    """
    Aggregate values for Alignment objects. Used for queries (see graphql_api/queries.py).
    """
    # Get the selected aggregate functions and columns to operate on, and groupby options if any were provided.
    # TODO: not sure why selected_fields is a list
    selections = info.selected_fields[0].selections[0].selections
    aggregate_selections = [selection for selection in selections if selection.name != "groupBy"]
    groupby_selections = [selection for selection in selections if selection.name == "groupBy"]
    groupby_selections = groupby_selections[0].selections if groupby_selections else []

    if not aggregate_selections:
        raise PlatformicsError("No aggregate functions selected")

    rows = await get_aggregate_db_rows(db.Alignment, session, authz_client, principal, where, aggregate_selections, [], groupby_selections)  # type: ignore
    aggregate_output = format_alignment_aggregate_output(rows)
    return aggregate_output


@strawberry.mutation(extensions=[DependencyExtension()])
async def create_alignment(
    input: AlignmentCreateInput,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    is_system_user: bool = Depends(is_system_user),
) -> db.Alignment:
    """
    Create a new Alignment object. Used for mutations (see graphql_api/mutations.py).
    """
    validated = AlignmentCreateInputValidator(**input.__dict__)
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
    # Check that run relationship is accessible.
    if validated.run_id:
        run = await get_db_rows(
            db.Run,
            session,
            authz_client,
            principal,
            {"id": {"_eq": validated.run_id}},
            [],
            AuthzAction.VIEW,
        )
        if not run:
            raise PlatformicsError("Unauthorized: run does not exist")

    # Save to DB
    params["owner_user_id"] = int(principal.id)
    new_entity = db.Alignment(**params)

    # Are we actually allowed to create this entity?
    if not authz_client.can_create(new_entity, principal):
        raise PlatformicsError("Unauthorized: Cannot create entity")

    session.add(new_entity)
    await session.commit()
    return new_entity


@strawberry.mutation(extensions=[DependencyExtension()])
async def update_alignment(
    input: AlignmentUpdateInput,
    where: AlignmentWhereClauseMutations,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    is_system_user: bool = Depends(is_system_user),
) -> Sequence[db.Alignment]:
    """
    Update Alignment objects. Used for mutations (see graphql_api/mutations.py).
    """
    validated = AlignmentUpdateInputValidator(**input.__dict__)
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
    # Check that run relationship is accessible.
    if validated.run_id:
        run = await get_db_rows(
            db.Run,
            session,
            authz_client,
            principal,
            {"id": {"_eq": validated.run_id}},
            [],
            AuthzAction.VIEW,
        )
        if not run:
            raise PlatformicsError("Unauthorized: run does not exist")
        params["run"] = run[0]
        del params["run_id"]

    # Fetch entities for update, if we have access to them
    entities = await get_db_rows(db.Alignment, session, authz_client, principal, where, [], AuthzAction.UPDATE)
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
async def delete_alignment(
    where: AlignmentWhereClauseMutations,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
) -> Sequence[db.Alignment]:
    """
    Delete Alignment objects. Used for mutations (see graphql_api/mutations.py).
    """
    # Fetch entities for deletion, if we have access to them
    entities = await get_db_rows(db.Alignment, session, authz_client, principal, where, [], AuthzAction.DELETE)
    if len(entities) == 0:
        raise PlatformicsError("Unauthorized: Cannot delete entities")

    # Update DB
    for entity in entities:
        await session.delete(entity)
    await session.commit()
    return entities