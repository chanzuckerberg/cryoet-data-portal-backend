"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

from typing import TYPE_CHECKING, Annotated, Any, Optional

import graphql_api.helpers.alignment as alignment_helper
import strawberry

if TYPE_CHECKING:
    from graphql_api.helpers.alignment import AlignmentGroupByOptions
else:
    AlignmentGroupByOptions = "AlignmentGroupByOptions"


"""
Define groupby options for PerSectionAlignmentParameters type.
These are only used in aggregate queries.
"""


@strawberry.type
class PerSectionAlignmentParametersGroupByOptions:
    alignment: Optional[Annotated["AlignmentGroupByOptions", strawberry.lazy("graphql_api.helpers.alignment")]] = None
    z_index: Optional[int] = None
    x_offset: Optional[float] = None
    y_offset: Optional[float] = None
    volume_x_rotation: Optional[float] = None
    in_plane_rotation: Optional[list[list[float]]] = None
    tilt_angle: Optional[float] = None
    id: Optional[int] = None


def build_per_section_alignment_parameters_groupby_output(
    group_object: Optional[PerSectionAlignmentParametersGroupByOptions],
    keys: list[str],
    value: Any,
) -> PerSectionAlignmentParametersGroupByOptions:
    """
    Given a list of (potentially nested) fields representing the key of a groupby query and the value,
    build the proper groupby object.
    """
    if not group_object:
        group_object = PerSectionAlignmentParametersGroupByOptions()

    key = keys.pop(0)
    match key:
        case "alignment":
            if getattr(group_object, key):
                value = alignment_helper.build_alignment_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = alignment_helper.build_alignment_groupby_output(
                    None,
                    keys,
                    value,
                )
        case _:
            pass
    setattr(group_object, key, value)
    return group_object
