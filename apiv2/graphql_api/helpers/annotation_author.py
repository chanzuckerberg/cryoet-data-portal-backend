"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

from typing import TYPE_CHECKING, Annotated, Any, Optional

import graphql_api.helpers.annotation as annotation_helper
import strawberry

if TYPE_CHECKING:
    from graphql_api.helpers.annotation import AnnotationGroupByOptions
else:
    AnnotationGroupByOptions = "AnnotationGroupByOptions"


"""
Define groupby options for AnnotationAuthor type.
These are only used in aggregate queries.
"""


@strawberry.type
class AnnotationAuthorGroupByOptions:
    annotation: Optional[Annotated["AnnotationGroupByOptions", strawberry.lazy("graphql_api.helpers.annotation")]] = (
        None
    )
    id: Optional[int] = None
    author_list_order: Optional[int] = None
    orcid: Optional[str] = None
    kaggle_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    affiliation_name: Optional[str] = None
    affiliation_address: Optional[str] = None
    affiliation_identifier: Optional[str] = None
    corresponding_author_status: Optional[bool] = None
    primary_author_status: Optional[bool] = None


def build_annotation_author_groupby_output(
    group_object: Optional[AnnotationAuthorGroupByOptions],
    keys: list[str],
    value: Any,
) -> AnnotationAuthorGroupByOptions:
    """
    Given a list of (potentially nested) fields representing the key of a groupby query and the value,
    build the proper groupby object.
    """
    if not group_object:
        group_object = AnnotationAuthorGroupByOptions()

    key = keys.pop(0)
    match key:
        case "annotation":
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
        case _:
            pass
    setattr(group_object, key, value)
    return group_object
