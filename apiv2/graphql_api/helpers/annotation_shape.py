"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

from typing import Any, Optional, TYPE_CHECKING
import strawberry
import datetime
import uuid
from support.enums import annotation_file_shape_type_enum
from graphql_api.helpers.annotation import AnnotationGroupByOptions, build_annotation_groupby_output

if TYPE_CHECKING:
    from api.types.annotation import Annotation
else:
    Annotation = "Annotation"


"""
Define groupby options for AnnotationShape type.
These are only used in aggregate queries.
"""


@strawberry.type
class AnnotationShapeGroupByOptions:
    annotation: Optional[AnnotationGroupByOptions] = None
    shape_type: Optional[annotation_file_shape_type_enum] = None
    id: Optional[int] = None


def build_annotation_shape_groupby_output(
    group_object: Optional[AnnotationShapeGroupByOptions],
    keys: list[str],
    value: Any,
) -> AnnotationShapeGroupByOptions:
    """
    Given a list of (potentially nested) fields representing the key of a groupby query and the value,
    build the proper groupby object.
    """
    if not group_object:
        group_object = AnnotationShapeGroupByOptions()

    key = keys.pop(0)
    match key:
        case "annotation":
            if getattr(group_object, key):
                value = build_annotation_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = build_annotation_groupby_output(
                    None,
                    keys,
                    value,
                )
        case _:
            pass
    setattr(group_object, key, value)
    return group_object
