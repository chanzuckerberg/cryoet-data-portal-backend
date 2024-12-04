"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

from typing import TYPE_CHECKING, Annotated, Any, Optional

import graphql_api.helpers.annotation_file as annotation_file_helper
import graphql_api.helpers.run as run_helper
import graphql_api.helpers.tomogram as tomogram_helper
import strawberry

if TYPE_CHECKING:
    from graphql_api.helpers.annotation_file import AnnotationFileGroupByOptions
    from graphql_api.helpers.run import RunGroupByOptions
    from graphql_api.helpers.tomogram import TomogramGroupByOptions
else:
    AnnotationFileGroupByOptions = "AnnotationFileGroupByOptions"
    RunGroupByOptions = "RunGroupByOptions"
    TomogramGroupByOptions = "TomogramGroupByOptions"


"""
Define groupby options for TomogramVoxelSpacing type.
These are only used in aggregate queries.
"""


@strawberry.type
class TomogramVoxelSpacingGroupByOptions:
    annotation_files: Optional[
        Annotated["AnnotationFileGroupByOptions", strawberry.lazy("graphql_api.helpers.annotation_file")]
    ] = None
    run: Optional[Annotated["RunGroupByOptions", strawberry.lazy("graphql_api.helpers.run")]] = None
    tomograms: Optional[Annotated["TomogramGroupByOptions", strawberry.lazy("graphql_api.helpers.tomogram")]] = None
    voxel_spacing: Optional[float] = None
    s3_prefix: Optional[str] = None
    https_prefix: Optional[str] = None
    id: Optional[int] = None


def build_tomogram_voxel_spacing_groupby_output(
    group_object: Optional[TomogramVoxelSpacingGroupByOptions],
    keys: list[str],
    value: Any,
) -> TomogramVoxelSpacingGroupByOptions:
    """
    Given a list of (potentially nested) fields representing the key of a groupby query and the value,
    build the proper groupby object.
    """
    if not group_object:
        group_object = TomogramVoxelSpacingGroupByOptions()

    key = keys.pop(0)
    match key:
        case "annotation_files":
            if getattr(group_object, key):
                value = annotation_file_helper.build_annotation_file_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = annotation_file_helper.build_annotation_file_groupby_output(
                    None,
                    keys,
                    value,
                )
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
        case _:
            pass
    setattr(group_object, key, value)
    return group_object
