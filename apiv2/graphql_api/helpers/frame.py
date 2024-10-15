"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

from typing import TYPE_CHECKING, Any, Optional

import strawberry
from graphql_api.helpers.deposition import DepositionGroupByOptions, build_deposition_groupby_output
from graphql_api.helpers.run import RunGroupByOptions, build_run_groupby_output

if TYPE_CHECKING:
    from api.types.deposition import Deposition
else:
    Deposition = "Deposition"
if TYPE_CHECKING:
    from api.types.run import Run
else:
    Run = "Run"


"""
Define groupby options for Frame type.
These are only used in aggregate queries.
"""


@strawberry.type
class FrameGroupByOptions:
    deposition: Optional[DepositionGroupByOptions] = None
    run: Optional[RunGroupByOptions] = None
    raw_angle: Optional[float] = None
    acquisition_order: Optional[int] = None
    dose: Optional[float] = None
    is_gain_corrected: Optional[bool] = None
    s3_frame_path: Optional[str] = None
    https_frame_path: Optional[str] = None
    id: Optional[int] = None


def build_frame_groupby_output(
    group_object: Optional[FrameGroupByOptions],
    keys: list[str],
    value: Any,
) -> FrameGroupByOptions:
    """
    Given a list of (potentially nested) fields representing the key of a groupby query and the value,
    build the proper groupby object.
    """
    if not group_object:
        group_object = FrameGroupByOptions()

    key = keys.pop(0)
    match key:
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
