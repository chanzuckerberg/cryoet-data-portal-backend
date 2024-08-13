"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

from typing import TYPE_CHECKING, Any, Optional

import strawberry
from graphql_api.helpers.alignment import AlignmentGroupByOptions, build_alignment_groupby_output
from graphql_api.helpers.annotation_shape import AnnotationShapeGroupByOptions, build_annotation_shape_groupby_output
from graphql_api.helpers.tomogram_voxel_spacing import (
    TomogramVoxelSpacingGroupByOptions,
    build_tomogram_voxel_spacing_groupby_output,
)
from support.enums import annotation_file_source_enum

if TYPE_CHECKING:
    from api.types.alignment import Alignment
else:
    Alignment = "Alignment"
if TYPE_CHECKING:
    from api.types.annotation_shape import AnnotationShape
else:
    AnnotationShape = "AnnotationShape"
if TYPE_CHECKING:
    from api.types.tomogram_voxel_spacing import TomogramVoxelSpacing
else:
    TomogramVoxelSpacing = "TomogramVoxelSpacing"


"""
Define groupby options for AnnotationFile type.
These are only used in aggregate queries.
"""


@strawberry.type
class AnnotationFileGroupByOptions:
    alignment: Optional[AlignmentGroupByOptions] = None
    annotation_shape: Optional[AnnotationShapeGroupByOptions] = None
    tomogram_voxel_spacing: Optional[TomogramVoxelSpacingGroupByOptions] = None
    format: Optional[str] = None
    s3_path: Optional[str] = None
    https_path: Optional[str] = None
    is_visualization_default: Optional[bool] = None
    source: Optional[annotation_file_source_enum] = None
    id: Optional[int] = None


def build_annotation_file_groupby_output(
    group_object: Optional[AnnotationFileGroupByOptions],
    keys: list[str],
    value: Any,
) -> AnnotationFileGroupByOptions:
    """
    Given a list of (potentially nested) fields representing the key of a groupby query and the value,
    build the proper groupby object.
    """
    if not group_object:
        group_object = AnnotationFileGroupByOptions()

    key = keys.pop(0)
    match key:
        case "alignment":
            if getattr(group_object, key):
                value = build_alignment_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = build_alignment_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "annotation_shape":
            if getattr(group_object, key):
                value = build_annotation_shape_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = build_annotation_shape_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "tomogram_voxel_spacing":
            if getattr(group_object, key):
                value = build_tomogram_voxel_spacing_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = build_tomogram_voxel_spacing_groupby_output(
                    None,
                    keys,
                    value,
                )
        case _:
            pass
    setattr(group_object, key, value)
    return group_object
