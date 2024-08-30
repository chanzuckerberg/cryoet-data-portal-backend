"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

from typing import TYPE_CHECKING, Any, Optional

import strawberry
from graphql_api.helpers.frame import FrameGroupByOptions, build_frame_groupby_output
from graphql_api.helpers.tiltseries import TiltseriesGroupByOptions, build_tiltseries_groupby_output

if TYPE_CHECKING:
    from api.types.frame import Frame
else:
    Frame = "Frame"
if TYPE_CHECKING:
    from api.types.tiltseries import Tiltseries
else:
    Tiltseries = "Tiltseries"


"""
Define groupby options for PerSectionParameters type.
These are only used in aggregate queries.
"""


@strawberry.type
class PerSectionParametersGroupByOptions:
    frame: Optional[FrameGroupByOptions] = None
    tiltseries: Optional[TiltseriesGroupByOptions] = None
    z_index: Optional[int] = None
    defocus: Optional[float] = None
    astigmatism: Optional[float] = None
    astigmatic_angle: Optional[float] = None
    id: Optional[int] = None


def build_per_section_parameters_groupby_output(
    group_object: Optional[PerSectionParametersGroupByOptions],
    keys: list[str],
    value: Any,
) -> PerSectionParametersGroupByOptions:
    """
    Given a list of (potentially nested) fields representing the key of a groupby query and the value,
    build the proper groupby object.
    """
    if not group_object:
        group_object = PerSectionParametersGroupByOptions()

    key = keys.pop(0)
    match key:
        case "frame":
            if getattr(group_object, key):
                value = build_frame_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = build_frame_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "tiltseries":
            if getattr(group_object, key):
                value = build_tiltseries_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = build_tiltseries_groupby_output(
                    None,
                    keys,
                    value,
                )
        case _:
            pass
    setattr(group_object, key, value)
    return group_object
