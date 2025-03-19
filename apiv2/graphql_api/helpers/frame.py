"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

from typing import TYPE_CHECKING, Annotated, Any, Optional

import graphql_api.helpers.deposition as deposition_helper
import graphql_api.helpers.per_section_parameters as per_section_parameters_helper
import graphql_api.helpers.run as run_helper
import strawberry

if TYPE_CHECKING:
    from graphql_api.helpers.deposition import DepositionGroupByOptions
    from graphql_api.helpers.per_section_parameters import PerSectionParametersGroupByOptions
    from graphql_api.helpers.run import RunGroupByOptions
else:
    DepositionGroupByOptions = "DepositionGroupByOptions"
    RunGroupByOptions = "RunGroupByOptions"
    PerSectionParametersGroupByOptions = "PerSectionParametersGroupByOptions"


"""
Define groupby options for Frame type.
These are only used in aggregate queries.
"""


@strawberry.type
class FrameGroupByOptions:
    deposition: Optional[Annotated["DepositionGroupByOptions", strawberry.lazy("graphql_api.helpers.deposition")]] = (
        None
    )
    run: Optional[Annotated["RunGroupByOptions", strawberry.lazy("graphql_api.helpers.run")]] = None
    acquisition_order: Optional[int] = None
    accumulated_dose: Optional[float] = None
    exposure_dose: Optional[float] = None
    is_gain_corrected: Optional[bool] = None
    per_section_parameters: Optional[
        Annotated["PerSectionParametersGroupByOptions", strawberry.lazy("graphql_api.helpers.per_section_parameters")]
    ] = None
    s3_frame_path: Optional[str] = None
    https_frame_path: Optional[str] = None
    file_size: Optional[float] = None
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
                value = deposition_helper.build_deposition_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = deposition_helper.build_deposition_groupby_output(
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
        case "per_section_parameters":
            if getattr(group_object, key):
                value = per_section_parameters_helper.build_per_section_parameters_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = per_section_parameters_helper.build_per_section_parameters_groupby_output(
                    None,
                    keys,
                    value,
                )
        case _:
            pass
    setattr(group_object, key, value)
    return group_object
