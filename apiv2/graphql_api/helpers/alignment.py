"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

from typing import Any, Optional, TYPE_CHECKING
import strawberry
import datetime
import uuid
from support.enums import alignment_type_enum
from graphql_api.helpers.deposition import DepositionGroupByOptions, build_deposition_groupby_output
from graphql_api.helpers.tiltseries import TiltseriesGroupByOptions, build_tiltseries_groupby_output
from graphql_api.helpers.run import RunGroupByOptions, build_run_groupby_output

if TYPE_CHECKING:
    from api.types.deposition import Deposition
else:
    Deposition = "Deposition"
if TYPE_CHECKING:
    from api.types.tiltseries import Tiltseries
else:
    Tiltseries = "Tiltseries"
if TYPE_CHECKING:
    from api.types.run import Run
else:
    Run = "Run"


"""
Define groupby options for Alignment type.
These are only used in aggregate queries.
"""


@strawberry.type
class AlignmentGroupByOptions:
    deposition: Optional[DepositionGroupByOptions] = None
    tiltseries: Optional[TiltseriesGroupByOptions] = None
    run: Optional[RunGroupByOptions] = None
    alignment: Optional[str] = None
    alignment_type: Optional[alignment_type_enum] = None
    volume_x_dimension: Optional[float] = None
    volume_y_dimension: Optional[float] = None
    volume_z_dimension: Optional[float] = None
    volume_x_offset: Optional[float] = None
    volume_y_offset: Optional[float] = None
    volume_z_offset: Optional[float] = None
    volume_x_rotation: Optional[float] = None
    tilt_offset: Optional[float] = None
    local_alignment_file: Optional[str] = None
    id: Optional[int] = None


def build_alignment_groupby_output(
    group_object: Optional[AlignmentGroupByOptions],
    keys: list[str],
    value: Any,
) -> AlignmentGroupByOptions:
    """
    Given a list of (potentially nested) fields representing the key of a groupby query and the value,
    build the proper groupby object.
    """
    if not group_object:
        group_object = AlignmentGroupByOptions()

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
