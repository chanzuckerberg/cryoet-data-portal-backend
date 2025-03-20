"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

from typing import Any, Optional, TYPE_CHECKING, Annotated
import strawberry
import datetime
import uuid
import graphql_api.helpers.deposition_author as deposition_author_helper
import graphql_api.helpers.alignment as alignment_helper
import graphql_api.helpers.annotation as annotation_helper
import graphql_api.helpers.dataset as dataset_helper
import graphql_api.helpers.frame as frame_helper
import graphql_api.helpers.tiltseries as tiltseries_helper
import graphql_api.helpers.tomogram as tomogram_helper
import graphql_api.helpers.deposition_type as deposition_type_helper

if TYPE_CHECKING:
    from graphql_api.helpers.deposition_author import DepositionAuthorGroupByOptions
    from graphql_api.helpers.alignment import AlignmentGroupByOptions
    from graphql_api.helpers.annotation import AnnotationGroupByOptions
    from graphql_api.helpers.dataset import DatasetGroupByOptions
    from graphql_api.helpers.frame import FrameGroupByOptions
    from graphql_api.helpers.tiltseries import TiltseriesGroupByOptions
    from graphql_api.helpers.tomogram import TomogramGroupByOptions
    from graphql_api.helpers.deposition_type import DepositionTypeGroupByOptions
else:
    DepositionAuthorGroupByOptions = "DepositionAuthorGroupByOptions"
    AlignmentGroupByOptions = "AlignmentGroupByOptions"
    AnnotationGroupByOptions = "AnnotationGroupByOptions"
    DatasetGroupByOptions = "DatasetGroupByOptions"
    FrameGroupByOptions = "FrameGroupByOptions"
    TiltseriesGroupByOptions = "TiltseriesGroupByOptions"
    TomogramGroupByOptions = "TomogramGroupByOptions"
    DepositionTypeGroupByOptions = "DepositionTypeGroupByOptions"


"""
Define groupby options for Deposition type.
These are only used in aggregate queries.
"""


@strawberry.type
class DepositionGroupByOptions:
    authors: Optional[
        Annotated["DepositionAuthorGroupByOptions", strawberry.lazy("graphql_api.helpers.deposition_author")]
    ] = None
    alignments: Optional[Annotated["AlignmentGroupByOptions", strawberry.lazy("graphql_api.helpers.alignment")]] = None
    annotations: Optional[Annotated["AnnotationGroupByOptions", strawberry.lazy("graphql_api.helpers.annotation")]] = (
        None
    )
    datasets: Optional[Annotated["DatasetGroupByOptions", strawberry.lazy("graphql_api.helpers.dataset")]] = None
    frames: Optional[Annotated["FrameGroupByOptions", strawberry.lazy("graphql_api.helpers.frame")]] = None
    tiltseries: Optional[Annotated["TiltseriesGroupByOptions", strawberry.lazy("graphql_api.helpers.tiltseries")]] = (
        None
    )
    tomograms: Optional[Annotated["TomogramGroupByOptions", strawberry.lazy("graphql_api.helpers.tomogram")]] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tag: Optional[str] = None
    deposition_types: Optional[
        Annotated["DepositionTypeGroupByOptions", strawberry.lazy("graphql_api.helpers.deposition_type")]
    ] = None
    deposition_publications: Optional[str] = None
    related_database_entries: Optional[str] = None
    deposition_date: Optional[datetime.datetime] = None
    release_date: Optional[datetime.datetime] = None
    last_modified_date: Optional[datetime.datetime] = None
    key_photo_url: Optional[str] = None
    key_photo_thumbnail_url: Optional[str] = None
    id: Optional[int] = None


def build_deposition_groupby_output(
    group_object: Optional[DepositionGroupByOptions],
    keys: list[str],
    value: Any,
) -> DepositionGroupByOptions:
    """
    Given a list of (potentially nested) fields representing the key of a groupby query and the value,
    build the proper groupby object.
    """
    if not group_object:
        group_object = DepositionGroupByOptions()

    key = keys.pop(0)
    match key:
        case "authors":
            if getattr(group_object, key):
                value = deposition_author_helper.build_deposition_author_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = deposition_author_helper.build_deposition_author_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "alignments":
            if getattr(group_object, key):
                value = alignment_helper.build_alignment_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = alignment_helper.build_alignment_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "annotations":
            if getattr(group_object, key):
                value = annotation_helper.build_annotation_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = annotation_helper.build_annotation_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "datasets":
            if getattr(group_object, key):
                value = dataset_helper.build_dataset_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = dataset_helper.build_dataset_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "frames":
            if getattr(group_object, key):
                value = frame_helper.build_frame_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = frame_helper.build_frame_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "tiltseries":
            if getattr(group_object, key):
                value = tiltseries_helper.build_tiltseries_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = tiltseries_helper.build_tiltseries_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "tomograms":
            if getattr(group_object, key):
                value = tomogram_helper.build_tomogram_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = tomogram_helper.build_tomogram_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "deposition_types":
            if getattr(group_object, key):
                value = deposition_type_helper.build_deposition_type_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = deposition_type_helper.build_deposition_type_groupby_output(
                    None,
                    keys,
                    value,
                )
        case _:
            pass
    setattr(group_object, key, value)
    return group_object
