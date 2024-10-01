"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

import datetime
from typing import TYPE_CHECKING, Any, Optional

import strawberry
from graphql_api.helpers.deposition import DepositionGroupByOptions, build_deposition_groupby_output
from graphql_api.helpers.run import RunGroupByOptions, build_run_groupby_output
from support.enums import annotation_method_type_enum

if TYPE_CHECKING:
    from api.types.run import Run
else:
    Run = "Run"
if TYPE_CHECKING:
    from api.types.deposition import Deposition
else:
    Deposition = "Deposition"


"""
Define groupby options for Annotation type.
These are only used in aggregate queries.
"""


@strawberry.type
class AnnotationGroupByOptions:
    run: Optional[RunGroupByOptions] = None
    deposition: Optional[DepositionGroupByOptions] = None
    s3_metadata_path: Optional[str] = None
    https_metadata_path: Optional[str] = None
    annotation_publication: Optional[str] = None
    annotation_method: Optional[str] = None
    method_links: Optional[str] = None
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
                value = build_run_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = build_run_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "deposition":
            if getattr(group_object, key):
                value = build_deposition_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = build_deposition_groupby_output(
                    None,
                    keys,
                    value,
                )
        case _:
            pass
    setattr(group_object, key, value)
    return group_object
