"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""



from typing import TYPE_CHECKING, Annotated, Any, Optional

import graphql_api.helpers.frame as frame_helper
import graphql_api.helpers.run as run_helper
import graphql_api.helpers.tiltseries as tiltseries_helper
import strawberry

if TYPE_CHECKING:
    from graphql_api.helpers.frame import FrameGroupByOptions
    from graphql_api.helpers.run import RunGroupByOptions
    from graphql_api.helpers.tiltseries import TiltseriesGroupByOptions
else:
    FrameGroupByOptions = "FrameGroupByOptions"
    RunGroupByOptions = "RunGroupByOptions"
    TiltseriesGroupByOptions = "TiltseriesGroupByOptions"


"""
Define groupby options for PerSectionParameters type.
These are only used in aggregate queries.
"""

@strawberry.type
class PerSectionParametersGroupByOptions:
    astigmatic_angle: Optional[float] = None
    frame: Optional[Annotated["FrameGroupByOptions", strawberry.lazy("graphql_api.helpers.frame")]] = None
    major_defocus: Optional[float] = None
    max_resolution: Optional[float] = None
    minor_defocus: Optional[float] = None
    phase_shift: Optional[float] = None
    raw_angle: Optional[float] = None
    run: Optional[Annotated["RunGroupByOptions", strawberry.lazy("graphql_api.helpers.run")]] = None
    tiltseries: Optional[Annotated["TiltseriesGroupByOptions", strawberry.lazy("graphql_api.helpers.tiltseries")]] = None
    z_index: Optional[int] = None
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
                value = frame_helper.build_frame_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = frame_helper.build_frame_groupby_output(
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
        case "tiltseries":
            if getattr(group_object, key):
                value = tiltseries_helper.build_tiltseries_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = tiltseries_helper.build_tiltseries_groupby_output(
                    None,
                    keys,
                    value,
                )
        case _:
            pass
    setattr(group_object, key, value)
    return group_object
