"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

from typing import TYPE_CHECKING, Any, Optional

import strawberry
from graphql_api.helpers.run import RunGroupByOptions, build_run_groupby_output

if TYPE_CHECKING:
    from api.types.run import Run
else:
    Run = "Run"


"""
Define groupby options for FrameAcquisitionFile type.
These are only used in aggregate queries.
"""


@strawberry.type
class FrameAcquisitionFileGroupByOptions:
    run: Optional[RunGroupByOptions] = None
    s3_mdoc_path: Optional[str] = None
    https_mdoc_path: Optional[str] = None
    id: Optional[int] = None


def build_frame_acquisition_file_groupby_output(
    group_object: Optional[FrameAcquisitionFileGroupByOptions],
    keys: list[str],
    value: Any,
) -> FrameAcquisitionFileGroupByOptions:
    """
    Given a list of (potentially nested) fields representing the key of a groupby query and the value,
    build the proper groupby object.
    """
    if not group_object:
        group_object = FrameAcquisitionFileGroupByOptions()

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
