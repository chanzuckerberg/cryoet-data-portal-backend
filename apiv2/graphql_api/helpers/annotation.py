"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

import datetime
from typing import TYPE_CHECKING, Annotated, Any, Optional

import graphql_api.helpers.annotation_author as annotation_author_helper
import graphql_api.helpers.annotation_method_link as annotation_method_link_helper
import graphql_api.helpers.annotation_shape as annotation_shape_helper
import graphql_api.helpers.deposition as deposition_helper
import graphql_api.helpers.run as run_helper
import strawberry
from support.enums import annotation_method_type_enum

if TYPE_CHECKING:
    from graphql_api.helpers.annotation_author import AnnotationAuthorGroupByOptions
    from graphql_api.helpers.annotation_method_link import AnnotationMethodLinkGroupByOptions
    from graphql_api.helpers.annotation_shape import AnnotationShapeGroupByOptions
    from graphql_api.helpers.deposition import DepositionGroupByOptions
    from graphql_api.helpers.run import RunGroupByOptions
else:
    RunGroupByOptions = "RunGroupByOptions"
    AnnotationShapeGroupByOptions = "AnnotationShapeGroupByOptions"
    AnnotationMethodLinkGroupByOptions = "AnnotationMethodLinkGroupByOptions"
    AnnotationAuthorGroupByOptions = "AnnotationAuthorGroupByOptions"
    DepositionGroupByOptions = "DepositionGroupByOptions"


"""
Define groupby options for Annotation type.
These are only used in aggregate queries.
"""


@strawberry.type
class AnnotationGroupByOptions:
    run: Optional[Annotated["RunGroupByOptions", strawberry.lazy("graphql_api.helpers.run")]] = None
    annotation_shapes: Optional[
        Annotated["AnnotationShapeGroupByOptions", strawberry.lazy("graphql_api.helpers.annotation_shape")]
    ] = None
    method_links: Optional[
        Annotated["AnnotationMethodLinkGroupByOptions", strawberry.lazy("graphql_api.helpers.annotation_method_link")]
    ] = None
    authors: Optional[
        Annotated["AnnotationAuthorGroupByOptions", strawberry.lazy("graphql_api.helpers.annotation_author")]
    ] = None
    deposition: Optional[Annotated["DepositionGroupByOptions", strawberry.lazy("graphql_api.helpers.deposition")]] = (
        None
    )
    s3_metadata_path: Optional[str] = None
    https_metadata_path: Optional[str] = None
    annotation_publication: Optional[str] = None
    annotation_method: Optional[str] = None
    ground_truth_status: Optional[bool] = None
    object_id: Optional[str] = None
    object_name: Optional[str] = None
    object_description: Optional[str] = None
    object_state: Optional[str] = None
    object_count: Optional[int] = None
    confidence_precision: Optional[float] = None
    confidence_recall: Optional[float] = None
    ground_truth_used: Optional[str] = None
    annotation_software: Optional[str] = None
    is_curator_recommended: Optional[bool] = None
    method_type: Optional[annotation_method_type_enum] = None
    deposition_date: Optional[datetime.datetime] = None
    release_date: Optional[datetime.datetime] = None
    last_modified_date: Optional[datetime.datetime] = None
    id: Optional[int] = None


def build_annotation_groupby_output(
    group_object: Optional[AnnotationGroupByOptions],
    keys: list[str],
    value: Any,
) -> AnnotationGroupByOptions:
    """
    Given a list of (potentially nested) fields representing the key of a groupby query and the value,
    build the proper groupby object.
    """
    if not group_object:
        group_object = AnnotationGroupByOptions()

    key = keys.pop(0)
    match key:
        case "run":
            if getattr(group_object, key):
                value = run_helper.build_run_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = run_helper.build_run_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "annotation_shapes":
            if getattr(group_object, key):
                value = annotation_shape_helper.build_annotation_shape_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = annotation_shape_helper.build_annotation_shape_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "annotation_method_links":
            if getattr(group_object, key):
                value = annotation_method_link_helper.build_annotation_method_link_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = annotation_method_link_helper.build_annotation_method_link_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "annotation_authors":
            if getattr(group_object, key):
                value = annotation_author_helper.build_annotation_author_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = annotation_author_helper.build_annotation_author_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "deposition":
            if getattr(group_object, key):
                value = deposition_helper.build_deposition_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = deposition_helper.build_deposition_groupby_output(
                    None,
                    keys,
                    value,
                )
        case _:
            pass
    setattr(group_object, key, value)
    return group_object
