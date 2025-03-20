"""
GraphQL type for Deposition

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/types/class_name.py.j2 instead.
"""

# ruff: noqa: E501 Line too long

import typing
from typing import TYPE_CHECKING, Annotated, Any, Optional, Sequence, Callable, List

import platformics.database.models as base_db
from platformics.graphql_api.core.strawberry_helpers import get_aggregate_selections, get_nested_selected_fields
import database.models as db
import strawberry
import datetime
from platformics.graphql_api.core.query_builder import get_db_rows, get_aggregate_db_rows
from validators.deposition import DepositionCreateInputValidator
from validators.deposition import DepositionUpdateInputValidator
from graphql_api.helpers.deposition import DepositionGroupByOptions, build_deposition_groupby_output
from platformics.graphql_api.core.relay_interface import EntityInterface
from graphql_api.types.deposition_author import DepositionAuthorAggregate, format_deposition_author_aggregate_output
from graphql_api.types.alignment import AlignmentAggregate, format_alignment_aggregate_output
from graphql_api.types.annotation import AnnotationAggregate, format_annotation_aggregate_output
from graphql_api.types.dataset import DatasetAggregate, format_dataset_aggregate_output
from graphql_api.types.frame import FrameAggregate, format_frame_aggregate_output
from graphql_api.types.tiltseries import TiltseriesAggregate, format_tiltseries_aggregate_output
from graphql_api.types.tomogram import TomogramAggregate, format_tomogram_aggregate_output
from graphql_api.types.deposition_type import DepositionTypeAggregate, format_deposition_type_aggregate_output
from fastapi import Depends
from platformics.graphql_api.core.errors import PlatformicsError
from platformics.graphql_api.core.deps import get_authz_client, get_db_session, require_auth_principal, is_system_user
from platformics.graphql_api.core.query_input_types import (
    aggregator_map,
    orderBy,
    EnumComparators,
    DatetimeComparators,
    IntComparators,
    FloatComparators,
    StrComparators,
    UUIDComparators,
    BoolComparators,
)
from platformics.graphql_api.core.strawberry_extensions import DependencyExtension
from platformics.security.authorization import AuthzAction, AuthzClient, Principal
from sqlalchemy import inspect
from sqlalchemy.engine.row import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry import relay
from strawberry.types import Info
from support.limit_offset import LimitOffsetClause
from typing_extensions import TypedDict
import enum

E = typing.TypeVar("E")
T = typing.TypeVar("T")

if TYPE_CHECKING:
    from graphql_api.types.deposition_author import (
        DepositionAuthorOrderByClause,
        DepositionAuthorAggregateWhereClause,
        DepositionAuthorWhereClause,
        DepositionAuthor,
    )
    from graphql_api.types.alignment import (
        AlignmentOrderByClause,
        AlignmentAggregateWhereClause,
        AlignmentWhereClause,
        Alignment,
    )
    from graphql_api.types.annotation import (
        AnnotationOrderByClause,
        AnnotationAggregateWhereClause,
        AnnotationWhereClause,
        Annotation,
    )
    from graphql_api.types.dataset import DatasetOrderByClause, DatasetAggregateWhereClause, DatasetWhereClause, Dataset
    from graphql_api.types.frame import FrameOrderByClause, FrameAggregateWhereClause, FrameWhereClause, Frame
    from graphql_api.types.tiltseries import (
        TiltseriesOrderByClause,
        TiltseriesAggregateWhereClause,
        TiltseriesWhereClause,
        Tiltseries,
    )
    from graphql_api.types.tomogram import (
        TomogramOrderByClause,
        TomogramAggregateWhereClause,
        TomogramWhereClause,
        Tomogram,
    )
    from graphql_api.types.deposition_type import (
        DepositionTypeOrderByClause,
        DepositionTypeAggregateWhereClause,
        DepositionTypeWhereClause,
        DepositionType,
    )

    pass
else:
    DepositionAuthorWhereClause = "DepositionAuthorWhereClause"
    DepositionAuthorAggregateWhereClause = "DepositionAuthorAggregateWhereClause"
    DepositionAuthor = "DepositionAuthor"
    DepositionAuthorOrderByClause = "DepositionAuthorOrderByClause"
    AlignmentWhereClause = "AlignmentWhereClause"
    AlignmentAggregateWhereClause = "AlignmentAggregateWhereClause"
    Alignment = "Alignment"
    AlignmentOrderByClause = "AlignmentOrderByClause"
    AnnotationWhereClause = "AnnotationWhereClause"
    AnnotationAggregateWhereClause = "AnnotationAggregateWhereClause"
    Annotation = "Annotation"
    AnnotationOrderByClause = "AnnotationOrderByClause"
    DatasetWhereClause = "DatasetWhereClause"
    DatasetAggregateWhereClause = "DatasetAggregateWhereClause"
    Dataset = "Dataset"
    DatasetOrderByClause = "DatasetOrderByClause"
    FrameWhereClause = "FrameWhereClause"
    FrameAggregateWhereClause = "FrameAggregateWhereClause"
    Frame = "Frame"
    FrameOrderByClause = "FrameOrderByClause"
    TiltseriesWhereClause = "TiltseriesWhereClause"
    TiltseriesAggregateWhereClause = "TiltseriesAggregateWhereClause"
    Tiltseries = "Tiltseries"
    TiltseriesOrderByClause = "TiltseriesOrderByClause"
    TomogramWhereClause = "TomogramWhereClause"
    TomogramAggregateWhereClause = "TomogramAggregateWhereClause"
    Tomogram = "Tomogram"
    TomogramOrderByClause = "TomogramOrderByClause"
    DepositionTypeWhereClause = "DepositionTypeWhereClause"
    DepositionTypeAggregateWhereClause = "DepositionTypeAggregateWhereClause"
    DepositionType = "DepositionType"
    DepositionTypeOrderByClause = "DepositionTypeOrderByClause"
    pass


"""
------------------------------------------------------------------------------
Dataloaders
------------------------------------------------------------------------------
These are batching functions for loading related objects to avoid N+1 queries.
"""


@relay.connection(
    relay.ListConnection[Annotated["DepositionAuthor", strawberry.lazy("graphql_api.types.deposition_author")]]  # type:ignore
)
async def load_deposition_author_rows(
    root: "Deposition",
    info: Info,
    where: (
        Annotated["DepositionAuthorWhereClause", strawberry.lazy("graphql_api.types.deposition_author")] | None
    ) = None,
    order_by: Optional[
        list[Annotated["DepositionAuthorOrderByClause", strawberry.lazy("graphql_api.types.deposition_author")]]
    ] = [],
) -> Sequence[Annotated["DepositionAuthor", strawberry.lazy("graphql_api.types.deposition_author")]]:
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Deposition)
    relationship = mapper.relationships["authors"]
    return await dataloader.loader_for(relationship, where, order_by).load(root.id)  # type:ignore


@strawberry.field
async def load_deposition_author_aggregate_rows(
    root: "Deposition",
    info: Info,
    where: (
        Annotated["DepositionAuthorWhereClause", strawberry.lazy("graphql_api.types.deposition_author")] | None
    ) = None,
) -> Optional[Annotated["DepositionAuthorAggregate", strawberry.lazy("graphql_api.types.deposition_author")]]:
    selections = get_nested_selected_fields(info.selected_fields)
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Deposition)
    relationship = mapper.relationships["authors"]
    rows = await dataloader.aggregate_loader_for(relationship, where, selections).load(root.id)  # type:ignore
    aggregate_output = format_deposition_author_aggregate_output(rows)
    return aggregate_output


@relay.connection(
    relay.ListConnection[Annotated["Alignment", strawberry.lazy("graphql_api.types.alignment")]]  # type:ignore
)
async def load_alignment_rows(
    root: "Deposition",
    info: Info,
    where: Annotated["AlignmentWhereClause", strawberry.lazy("graphql_api.types.alignment")] | None = None,
    order_by: Optional[list[Annotated["AlignmentOrderByClause", strawberry.lazy("graphql_api.types.alignment")]]] = [],
) -> Sequence[Annotated["Alignment", strawberry.lazy("graphql_api.types.alignment")]]:
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Deposition)
    relationship = mapper.relationships["alignments"]
    return await dataloader.loader_for(relationship, where, order_by).load(root.id)  # type:ignore


@strawberry.field
async def load_alignment_aggregate_rows(
    root: "Deposition",
    info: Info,
    where: Annotated["AlignmentWhereClause", strawberry.lazy("graphql_api.types.alignment")] | None = None,
) -> Optional[Annotated["AlignmentAggregate", strawberry.lazy("graphql_api.types.alignment")]]:
    selections = get_nested_selected_fields(info.selected_fields)
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Deposition)
    relationship = mapper.relationships["alignments"]
    rows = await dataloader.aggregate_loader_for(relationship, where, selections).load(root.id)  # type:ignore
    aggregate_output = format_alignment_aggregate_output(rows)
    return aggregate_output


@relay.connection(
    relay.ListConnection[Annotated["Annotation", strawberry.lazy("graphql_api.types.annotation")]]  # type:ignore
)
async def load_annotation_rows(
    root: "Deposition",
    info: Info,
    where: Annotated["AnnotationWhereClause", strawberry.lazy("graphql_api.types.annotation")] | None = None,
    order_by: Optional[
        list[Annotated["AnnotationOrderByClause", strawberry.lazy("graphql_api.types.annotation")]]
    ] = [],
) -> Sequence[Annotated["Annotation", strawberry.lazy("graphql_api.types.annotation")]]:
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Deposition)
    relationship = mapper.relationships["annotations"]
    return await dataloader.loader_for(relationship, where, order_by).load(root.id)  # type:ignore


@strawberry.field
async def load_annotation_aggregate_rows(
    root: "Deposition",
    info: Info,
    where: Annotated["AnnotationWhereClause", strawberry.lazy("graphql_api.types.annotation")] | None = None,
) -> Optional[Annotated["AnnotationAggregate", strawberry.lazy("graphql_api.types.annotation")]]:
    selections = get_nested_selected_fields(info.selected_fields)
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Deposition)
    relationship = mapper.relationships["annotations"]
    rows = await dataloader.aggregate_loader_for(relationship, where, selections).load(root.id)  # type:ignore
    aggregate_output = format_annotation_aggregate_output(rows)
    return aggregate_output


@relay.connection(
    relay.ListConnection[Annotated["Dataset", strawberry.lazy("graphql_api.types.dataset")]]  # type:ignore
)
async def load_dataset_rows(
    root: "Deposition",
    info: Info,
    where: Annotated["DatasetWhereClause", strawberry.lazy("graphql_api.types.dataset")] | None = None,
    order_by: Optional[list[Annotated["DatasetOrderByClause", strawberry.lazy("graphql_api.types.dataset")]]] = [],
) -> Sequence[Annotated["Dataset", strawberry.lazy("graphql_api.types.dataset")]]:
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Deposition)
    relationship = mapper.relationships["datasets"]
    return await dataloader.loader_for(relationship, where, order_by).load(root.id)  # type:ignore


@strawberry.field
async def load_dataset_aggregate_rows(
    root: "Deposition",
    info: Info,
    where: Annotated["DatasetWhereClause", strawberry.lazy("graphql_api.types.dataset")] | None = None,
) -> Optional[Annotated["DatasetAggregate", strawberry.lazy("graphql_api.types.dataset")]]:
    selections = get_nested_selected_fields(info.selected_fields)
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Deposition)
    relationship = mapper.relationships["datasets"]
    rows = await dataloader.aggregate_loader_for(relationship, where, selections).load(root.id)  # type:ignore
    aggregate_output = format_dataset_aggregate_output(rows)
    return aggregate_output


@relay.connection(
    relay.ListConnection[Annotated["Frame", strawberry.lazy("graphql_api.types.frame")]]  # type:ignore
)
async def load_frame_rows(
    root: "Deposition",
    info: Info,
    where: Annotated["FrameWhereClause", strawberry.lazy("graphql_api.types.frame")] | None = None,
    order_by: Optional[list[Annotated["FrameOrderByClause", strawberry.lazy("graphql_api.types.frame")]]] = [],
) -> Sequence[Annotated["Frame", strawberry.lazy("graphql_api.types.frame")]]:
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Deposition)
    relationship = mapper.relationships["frames"]
    return await dataloader.loader_for(relationship, where, order_by).load(root.id)  # type:ignore


@strawberry.field
async def load_frame_aggregate_rows(
    root: "Deposition",
    info: Info,
    where: Annotated["FrameWhereClause", strawberry.lazy("graphql_api.types.frame")] | None = None,
) -> Optional[Annotated["FrameAggregate", strawberry.lazy("graphql_api.types.frame")]]:
    selections = get_nested_selected_fields(info.selected_fields)
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Deposition)
    relationship = mapper.relationships["frames"]
    rows = await dataloader.aggregate_loader_for(relationship, where, selections).load(root.id)  # type:ignore
    aggregate_output = format_frame_aggregate_output(rows)
    return aggregate_output


@relay.connection(
    relay.ListConnection[Annotated["Tiltseries", strawberry.lazy("graphql_api.types.tiltseries")]]  # type:ignore
)
async def load_tiltseries_rows(
    root: "Deposition",
    info: Info,
    where: Annotated["TiltseriesWhereClause", strawberry.lazy("graphql_api.types.tiltseries")] | None = None,
    order_by: Optional[
        list[Annotated["TiltseriesOrderByClause", strawberry.lazy("graphql_api.types.tiltseries")]]
    ] = [],
) -> Sequence[Annotated["Tiltseries", strawberry.lazy("graphql_api.types.tiltseries")]]:
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Deposition)
    relationship = mapper.relationships["tiltseries"]
    return await dataloader.loader_for(relationship, where, order_by).load(root.id)  # type:ignore


@strawberry.field
async def load_tiltseries_aggregate_rows(
    root: "Deposition",
    info: Info,
    where: Annotated["TiltseriesWhereClause", strawberry.lazy("graphql_api.types.tiltseries")] | None = None,
) -> Optional[Annotated["TiltseriesAggregate", strawberry.lazy("graphql_api.types.tiltseries")]]:
    selections = get_nested_selected_fields(info.selected_fields)
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Deposition)
    relationship = mapper.relationships["tiltseries"]
    rows = await dataloader.aggregate_loader_for(relationship, where, selections).load(root.id)  # type:ignore
    aggregate_output = format_tiltseries_aggregate_output(rows)
    return aggregate_output


@relay.connection(
    relay.ListConnection[Annotated["Tomogram", strawberry.lazy("graphql_api.types.tomogram")]]  # type:ignore
)
async def load_tomogram_rows(
    root: "Deposition",
    info: Info,
    where: Annotated["TomogramWhereClause", strawberry.lazy("graphql_api.types.tomogram")] | None = None,
    order_by: Optional[list[Annotated["TomogramOrderByClause", strawberry.lazy("graphql_api.types.tomogram")]]] = [],
) -> Sequence[Annotated["Tomogram", strawberry.lazy("graphql_api.types.tomogram")]]:
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Deposition)
    relationship = mapper.relationships["tomograms"]
    return await dataloader.loader_for(relationship, where, order_by).load(root.id)  # type:ignore


@strawberry.field
async def load_tomogram_aggregate_rows(
    root: "Deposition",
    info: Info,
    where: Annotated["TomogramWhereClause", strawberry.lazy("graphql_api.types.tomogram")] | None = None,
) -> Optional[Annotated["TomogramAggregate", strawberry.lazy("graphql_api.types.tomogram")]]:
    selections = get_nested_selected_fields(info.selected_fields)
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Deposition)
    relationship = mapper.relationships["tomograms"]
    rows = await dataloader.aggregate_loader_for(relationship, where, selections).load(root.id)  # type:ignore
    aggregate_output = format_tomogram_aggregate_output(rows)
    return aggregate_output


@relay.connection(
    relay.ListConnection[Annotated["DepositionType", strawberry.lazy("graphql_api.types.deposition_type")]]  # type:ignore
)
async def load_deposition_type_rows(
    root: "Deposition",
    info: Info,
    where: Annotated["DepositionTypeWhereClause", strawberry.lazy("graphql_api.types.deposition_type")] | None = None,
    order_by: Optional[
        list[Annotated["DepositionTypeOrderByClause", strawberry.lazy("graphql_api.types.deposition_type")]]
    ] = [],
) -> Sequence[Annotated["DepositionType", strawberry.lazy("graphql_api.types.deposition_type")]]:
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Deposition)
    relationship = mapper.relationships["deposition_types"]
    return await dataloader.loader_for(relationship, where, order_by).load(root.id)  # type:ignore


@strawberry.field
async def load_deposition_type_aggregate_rows(
    root: "Deposition",
    info: Info,
    where: Annotated["DepositionTypeWhereClause", strawberry.lazy("graphql_api.types.deposition_type")] | None = None,
) -> Optional[Annotated["DepositionTypeAggregate", strawberry.lazy("graphql_api.types.deposition_type")]]:
    selections = get_nested_selected_fields(info.selected_fields)
    dataloader = info.context["sqlalchemy_loader"]
    mapper = inspect(db.Deposition)
    relationship = mapper.relationships["deposition_types"]
    rows = await dataloader.aggregate_loader_for(relationship, where, selections).load(root.id)  # type:ignore
    aggregate_output = format_deposition_type_aggregate_output(rows)
    return aggregate_output


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
class DepositionWhereClauseMutations(TypedDict):
    id: IntComparators | None


"""
Supported WHERE clause attributes
"""


@strawberry.input
class DepositionWhereClause(TypedDict):
    authors: (
        Optional[Annotated["DepositionAuthorWhereClause", strawberry.lazy("graphql_api.types.deposition_author")]]
        | None
    )
    authors_aggregate: (
        Optional[
            Annotated["DepositionAuthorAggregateWhereClause", strawberry.lazy("graphql_api.types.deposition_author")]
        ]
        | None
    )
    alignments: Optional[Annotated["AlignmentWhereClause", strawberry.lazy("graphql_api.types.alignment")]] | None
    alignments_aggregate: (
        Optional[Annotated["AlignmentAggregateWhereClause", strawberry.lazy("graphql_api.types.alignment")]] | None
    )
    annotations: Optional[Annotated["AnnotationWhereClause", strawberry.lazy("graphql_api.types.annotation")]] | None
    annotations_aggregate: (
        Optional[Annotated["AnnotationAggregateWhereClause", strawberry.lazy("graphql_api.types.annotation")]] | None
    )
    datasets: Optional[Annotated["DatasetWhereClause", strawberry.lazy("graphql_api.types.dataset")]] | None
    datasets_aggregate: (
        Optional[Annotated["DatasetAggregateWhereClause", strawberry.lazy("graphql_api.types.dataset")]] | None
    )
    frames: Optional[Annotated["FrameWhereClause", strawberry.lazy("graphql_api.types.frame")]] | None
    frames_aggregate: (
        Optional[Annotated["FrameAggregateWhereClause", strawberry.lazy("graphql_api.types.frame")]] | None
    )
    tiltseries: Optional[Annotated["TiltseriesWhereClause", strawberry.lazy("graphql_api.types.tiltseries")]] | None
    tiltseries_aggregate: (
        Optional[Annotated["TiltseriesAggregateWhereClause", strawberry.lazy("graphql_api.types.tiltseries")]] | None
    )
    tomograms: Optional[Annotated["TomogramWhereClause", strawberry.lazy("graphql_api.types.tomogram")]] | None
    tomograms_aggregate: (
        Optional[Annotated["TomogramAggregateWhereClause", strawberry.lazy("graphql_api.types.tomogram")]] | None
    )
    title: Optional[StrComparators] | None
    description: Optional[StrComparators] | None
    tag: Optional[StrComparators] | None
    deposition_types: (
        Optional[Annotated["DepositionTypeWhereClause", strawberry.lazy("graphql_api.types.deposition_type")]] | None
    )
    deposition_types_aggregate: (
        Optional[Annotated["DepositionTypeAggregateWhereClause", strawberry.lazy("graphql_api.types.deposition_type")]]
        | None
    )
    deposition_publications: Optional[StrComparators] | None
    related_database_entries: Optional[StrComparators] | None
    deposition_date: Optional[DatetimeComparators] | None
    release_date: Optional[DatetimeComparators] | None
    last_modified_date: Optional[DatetimeComparators] | None
    key_photo_url: Optional[StrComparators] | None
    key_photo_thumbnail_url: Optional[StrComparators] | None
    id: Optional[IntComparators] | None


"""
Supported ORDER BY clause attributes
"""


@strawberry.input
class DepositionOrderByClause(TypedDict):
    title: Optional[orderBy] | None
    description: Optional[orderBy] | None
    tag: Optional[orderBy] | None
    deposition_publications: Optional[orderBy] | None
    related_database_entries: Optional[orderBy] | None
    deposition_date: Optional[orderBy] | None
    release_date: Optional[orderBy] | None
    last_modified_date: Optional[orderBy] | None
    key_photo_url: Optional[orderBy] | None
    key_photo_thumbnail_url: Optional[orderBy] | None
    id: Optional[orderBy] | None


"""
Define Deposition type
"""


@strawberry.type(description="Deposition metadata")
class Deposition(EntityInterface):
    authors: Sequence[Annotated["DepositionAuthor", strawberry.lazy("graphql_api.types.deposition_author")]] = (
        load_deposition_author_rows  # type:ignore
    )
    authors_aggregate: Optional[
        Annotated["DepositionAuthorAggregate", strawberry.lazy("graphql_api.types.deposition_author")]
    ] = load_deposition_author_aggregate_rows  # type:ignore
    alignments: Sequence[Annotated["Alignment", strawberry.lazy("graphql_api.types.alignment")]] = load_alignment_rows  # type:ignore
    alignments_aggregate: Optional[Annotated["AlignmentAggregate", strawberry.lazy("graphql_api.types.alignment")]] = (
        load_alignment_aggregate_rows  # type:ignore
    )
    annotations: Sequence[Annotated["Annotation", strawberry.lazy("graphql_api.types.annotation")]] = (
        load_annotation_rows  # type:ignore
    )
    annotations_aggregate: Optional[
        Annotated["AnnotationAggregate", strawberry.lazy("graphql_api.types.annotation")]
    ] = load_annotation_aggregate_rows  # type:ignore
    datasets: Sequence[Annotated["Dataset", strawberry.lazy("graphql_api.types.dataset")]] = load_dataset_rows  # type:ignore
    datasets_aggregate: Optional[Annotated["DatasetAggregate", strawberry.lazy("graphql_api.types.dataset")]] = (
        load_dataset_aggregate_rows  # type:ignore
    )
    frames: Sequence[Annotated["Frame", strawberry.lazy("graphql_api.types.frame")]] = load_frame_rows  # type:ignore
    frames_aggregate: Optional[Annotated["FrameAggregate", strawberry.lazy("graphql_api.types.frame")]] = (
        load_frame_aggregate_rows  # type:ignore
    )
    tiltseries: Sequence[Annotated["Tiltseries", strawberry.lazy("graphql_api.types.tiltseries")]] = (
        load_tiltseries_rows  # type:ignore
    )
    tiltseries_aggregate: Optional[
        Annotated["TiltseriesAggregate", strawberry.lazy("graphql_api.types.tiltseries")]
    ] = load_tiltseries_aggregate_rows  # type:ignore
    tomograms: Sequence[Annotated["Tomogram", strawberry.lazy("graphql_api.types.tomogram")]] = load_tomogram_rows  # type:ignore
    tomograms_aggregate: Optional[Annotated["TomogramAggregate", strawberry.lazy("graphql_api.types.tomogram")]] = (
        load_tomogram_aggregate_rows  # type:ignore
    )
    title: str = strawberry.field(description="Title for the deposition")
    description: str = strawberry.field(description="Description for the deposition")
    tag: Optional[str] = strawberry.field(description="Tag for the deposition - like ml competition", default=None)
    deposition_types: Sequence[Annotated["DepositionType", strawberry.lazy("graphql_api.types.deposition_type")]] = (
        load_deposition_type_rows  # type:ignore
    )
    deposition_types_aggregate: Optional[
        Annotated["DepositionTypeAggregate", strawberry.lazy("graphql_api.types.deposition_type")]
    ] = load_deposition_type_aggregate_rows  # type:ignore
    deposition_publications: Optional[str] = strawberry.field(
        description="The publications related to this deposition", default=None
    )
    related_database_entries: Optional[str] = strawberry.field(
        description="The related database entries to this deposition", default=None
    )
    deposition_date: datetime.datetime = strawberry.field(description="The date the deposition was deposited")
    release_date: datetime.datetime = strawberry.field(description="The date the deposition was released")
    last_modified_date: datetime.datetime = strawberry.field(description="The date the deposition was last modified")
    key_photo_url: Optional[str] = strawberry.field(description="URL for the deposition preview image.", default=None)
    key_photo_thumbnail_url: Optional[str] = strawberry.field(
        description="URL for the deposition thumbnail image.", default=None
    )
    id: int = strawberry.field(description="Numeric identifier (May change!)")


"""
We need to add this to each Queryable type so that strawberry will accept either our
Strawberry type *or* a SQLAlchemy model instance as a valid response class from a resolver
"""
Deposition.__strawberry_definition__.is_type_of = (  # type: ignore
    lambda obj, info: type(obj) == db.Deposition or type(obj) == Deposition
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
class DepositionNumericalColumns:
    id: Optional[int] = None


"""
Define columns that support min/max aggregations
"""


@strawberry.type
class DepositionMinMaxColumns:
    title: Optional[str] = None
    description: Optional[str] = None
    tag: Optional[str] = None
    deposition_publications: Optional[str] = None
    related_database_entries: Optional[str] = None
    deposition_date: Optional[datetime.datetime] = None
    release_date: Optional[datetime.datetime] = None
    last_modified_date: Optional[datetime.datetime] = None
    key_photo_url: Optional[str] = None
    key_photo_thumbnail_url: Optional[str] = None
    id: Optional[int] = None


"""
Define enum of all columns to support count and count(distinct) aggregations
"""


@strawberry.enum
class DepositionCountColumns(enum.Enum):
    title = "title"
    description = "description"
    tag = "tag"
    depositionPublications = "deposition_publications"
    relatedDatabaseEntries = "related_database_entries"
    depositionDate = "deposition_date"
    releaseDate = "release_date"
    lastModifiedDate = "last_modified_date"
    keyPhotoUrl = "key_photo_url"
    keyPhotoThumbnailUrl = "key_photo_thumbnail_url"
    id = "id"


"""
Support *filtering* on aggregates and related aggregates
"""


@strawberry.input
class DepositionAggregateWhereClauseCount(TypedDict):
    arguments: Optional["DepositionCountColumns"] | None
    distinct: Optional[bool] | None
    filter: Optional[DepositionWhereClause] | None
    predicate: Optional[IntComparators] | None


@strawberry.input
class DepositionAggregateWhereClause(TypedDict):
    count: DepositionAggregateWhereClauseCount


"""
All supported aggregation functions
"""


@strawberry.type
class DepositionAggregateFunctions:
    # This is a hack to accept "distinct" and "columns" as arguments to "count"
    @strawberry.field
    def count(
        self, distinct: Optional[bool] = False, columns: Optional[DepositionCountColumns] = None
    ) -> Optional[int]:
        # Count gets set with the proper value in the resolver, so we just return it here
        return self.count  # type: ignore

    sum: Optional[DepositionNumericalColumns] = None
    avg: Optional[DepositionNumericalColumns] = None
    stddev: Optional[DepositionNumericalColumns] = None
    variance: Optional[DepositionNumericalColumns] = None
    min: Optional[DepositionMinMaxColumns] = None
    max: Optional[DepositionMinMaxColumns] = None
    groupBy: Optional[DepositionGroupByOptions] = None


"""
Wrapper around DepositionAggregateFunctions
"""


@strawberry.type
class DepositionAggregate:
    aggregate: Optional[list[DepositionAggregateFunctions]] = None


"""
------------------------------------------------------------------------------
Mutation types
------------------------------------------------------------------------------
"""


@strawberry.input()
class DepositionCreateInput:
    title: str = strawberry.field(description="Title for the deposition")
    description: str = strawberry.field(description="Description for the deposition")
    tag: Optional[str] = strawberry.field(description="Tag for the deposition - like ml competition", default=None)
    deposition_publications: Optional[str] = strawberry.field(
        description="The publications related to this deposition", default=None
    )
    related_database_entries: Optional[str] = strawberry.field(
        description="The related database entries to this deposition", default=None
    )
    deposition_date: datetime.datetime = strawberry.field(description="The date the deposition was deposited")
    release_date: datetime.datetime = strawberry.field(description="The date the deposition was released")
    last_modified_date: datetime.datetime = strawberry.field(description="The date the deposition was last modified")
    key_photo_url: Optional[str] = strawberry.field(description="URL for the deposition preview image.", default=None)
    key_photo_thumbnail_url: Optional[str] = strawberry.field(
        description="URL for the deposition thumbnail image.", default=None
    )
    id: int = strawberry.field(description="Numeric identifier (May change!)")


@strawberry.input()
class DepositionUpdateInput:
    title: Optional[str] = strawberry.field(description="Title for the deposition")
    description: Optional[str] = strawberry.field(description="Description for the deposition")
    tag: Optional[str] = strawberry.field(description="Tag for the deposition - like ml competition", default=None)
    deposition_publications: Optional[str] = strawberry.field(
        description="The publications related to this deposition", default=None
    )
    related_database_entries: Optional[str] = strawberry.field(
        description="The related database entries to this deposition", default=None
    )
    deposition_date: Optional[datetime.datetime] = strawberry.field(description="The date the deposition was deposited")
    release_date: Optional[datetime.datetime] = strawberry.field(description="The date the deposition was released")
    last_modified_date: Optional[datetime.datetime] = strawberry.field(
        description="The date the deposition was last modified"
    )
    key_photo_url: Optional[str] = strawberry.field(description="URL for the deposition preview image.", default=None)
    key_photo_thumbnail_url: Optional[str] = strawberry.field(
        description="URL for the deposition thumbnail image.", default=None
    )
    id: Optional[int] = strawberry.field(description="Numeric identifier (May change!)")


"""
------------------------------------------------------------------------------
Utilities
------------------------------------------------------------------------------
"""


@strawberry.field(extensions=[DependencyExtension()])
async def resolve_depositions(
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    where: Optional[DepositionWhereClause] = None,
    order_by: Optional[list[DepositionOrderByClause]] = [],
    limit_offset: Optional[LimitOffsetClause] = None,
) -> typing.Sequence[Deposition]:
    """
    Resolve Deposition objects. Used for queries (see graphql_api/queries.py).
    """
    limit = limit_offset["limit"] if limit_offset and "limit" in limit_offset else None
    offset = limit_offset["offset"] if limit_offset and "offset" in limit_offset else None
    if offset and not limit:
        raise PlatformicsError("Cannot use offset without limit")
    return await get_db_rows(
        db.Deposition, session, authz_client, principal, where, order_by, AuthzAction.VIEW, limit, offset
    )  # type: ignore


def format_deposition_aggregate_output(query_results: Sequence[RowMapping] | RowMapping) -> DepositionAggregate:
    """
    Given a row from the DB containing the results of an aggregate query,
    format the results using the proper GraphQL types.
    """
    aggregate = []
    if not type(query_results) is list:
        query_results = [query_results]  # type: ignore
    for row in query_results:
        aggregate.append(format_deposition_aggregate_row(row))
    return DepositionAggregate(aggregate=aggregate)


def format_deposition_aggregate_row(row: RowMapping) -> DepositionAggregateFunctions:
    """
    Given a single row from the DB containing the results of an aggregate query,
    format the results using the proper GraphQL types.
    """
    output = DepositionAggregateFunctions()
    for key, value in row.items():
        # Key is either an aggregate function or a groupby key
        group_keys = key.split(".")
        aggregate = key.split("_", 1)
        if aggregate[0] not in aggregator_map.keys():
            # Turn list of groupby keys into nested objects
            if not getattr(output, "groupBy"):
                setattr(output, "groupBy", DepositionGroupByOptions())
            group = build_deposition_groupby_output(getattr(output, "groupBy"), group_keys, value)
            setattr(output, "groupBy", group)
        else:
            aggregate_name = aggregate[0]
            if aggregate_name == "count":
                output.count = value
            else:
                aggregator_fn, col_name = aggregate[0], aggregate[1]
                if not getattr(output, aggregator_fn):
                    if aggregate_name in ["min", "max"]:
                        setattr(output, aggregator_fn, DepositionMinMaxColumns())
                    else:
                        setattr(output, aggregator_fn, DepositionNumericalColumns())
                setattr(getattr(output, aggregator_fn), col_name, value)
    return output


@strawberry.field(extensions=[DependencyExtension()])
async def resolve_depositions_aggregate(
    info: Info,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    where: Optional[DepositionWhereClause] = None,
    # TODO: add support for groupby, limit/offset
) -> DepositionAggregate:
    """
    Aggregate values for Deposition objects. Used for queries (see graphql_api/queries.py).
    """
    # Get the selected aggregate functions and columns to operate on, and groupby options if any were provided.
    # TODO: not sure why selected_fields is a list
    aggregate_selections, groupby_selections = get_aggregate_selections(info.selected_fields)

    if not aggregate_selections:
        raise PlatformicsError("No aggregate functions selected")

    rows = await get_aggregate_db_rows(
        db.Deposition, session, authz_client, principal, where, aggregate_selections, [], groupby_selections
    )  # type: ignore
    aggregate_output = format_deposition_aggregate_output(rows)
    return aggregate_output


@strawberry.mutation(extensions=[DependencyExtension()])
async def create_deposition(
    input: DepositionCreateInput,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    is_system_user: bool = Depends(is_system_user),
) -> db.Deposition:
    """
    Create a new Deposition object. Used for mutations (see graphql_api/mutations.py).
    """
    validated = DepositionCreateInputValidator(**input.__dict__)
    params = validated.model_dump()

    # Validate that the user can read all of the entities they're linking to.

    # Validate that the user can read all of the entities they're linking to.

    # Save to DB
    params["owner_user_id"] = int(principal.id)
    new_entity = db.Deposition(**params)

    # Are we actually allowed to create this entity?
    if not authz_client.can_create(new_entity, principal):
        raise PlatformicsError("Unauthorized: Cannot create entity")

    session.add(new_entity)
    await session.commit()
    return new_entity


@strawberry.mutation(extensions=[DependencyExtension()])
async def update_deposition(
    input: DepositionUpdateInput,
    where: DepositionWhereClauseMutations,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
    is_system_user: bool = Depends(is_system_user),
) -> Sequence[db.Deposition]:
    """
    Update Deposition objects. Used for mutations (see graphql_api/mutations.py).
    """
    validated = DepositionUpdateInputValidator(**input.__dict__)
    params = validated.model_dump()

    # Need at least one thing to update
    num_params = len([x for x in params if params[x] is not None])
    if num_params == 0:
        raise PlatformicsError("No fields to update")

    # Validate that the user can read all of the entities they're linking to.

    # Fetch entities for update, if we have access to them
    entities = await get_db_rows(db.Deposition, session, authz_client, principal, where, [], AuthzAction.UPDATE)
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
async def delete_deposition(
    where: DepositionWhereClauseMutations,
    session: AsyncSession = Depends(get_db_session, use_cache=False),
    authz_client: AuthzClient = Depends(get_authz_client),
    principal: Principal = Depends(require_auth_principal),
) -> Sequence[db.Deposition]:
    """
    Delete Deposition objects. Used for mutations (see graphql_api/mutations.py).
    """
    # Fetch entities for deletion, if we have access to them
    entities = await get_db_rows(db.Deposition, session, authz_client, principal, where, [], AuthzAction.DELETE)
    if len(entities) == 0:
        raise PlatformicsError("Unauthorized: Cannot delete entities")

    # Update DB
    for entity in entities:
        await session.delete(entity)
    await session.commit()
    return entities
