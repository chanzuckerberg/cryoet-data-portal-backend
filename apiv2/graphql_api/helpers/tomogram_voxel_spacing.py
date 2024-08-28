"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

from typing import Any, Optional, TYPE_CHECKING
import strawberry
import datetime
import uuid
from graphql_api.helpers.run import RunGroupByOptions, build_run_groupby_output

if TYPE_CHECKING:
    from api.types.run import Run
else:
    Run = "Run"


"""
Define groupby options for TomogramVoxelSpacing type.
These are only used in aggregate queries.
"""


@strawberry.type
class TomogramVoxelSpacingGroupByOptions:
    run: Optional[RunGroupByOptions] = None
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
        case _:
            pass
    setattr(group_object, key, value)
    return group_object
