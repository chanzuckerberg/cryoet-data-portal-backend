"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

from typing import TYPE_CHECKING, Any, Optional

import strawberry
from graphql_api.helpers.deposition import DepositionGroupByOptions, build_deposition_groupby_output
from support.enums import deposition_types_enum

if TYPE_CHECKING:
    from api.types.deposition import Deposition
else:
    Deposition = "Deposition"


"""
Define groupby options for DepositionType type.
These are only used in aggregate queries.
"""


@strawberry.type
class DepositionTypeGroupByOptions:
    deposition: Optional[DepositionGroupByOptions] = None
    type: Optional[deposition_types_enum] = None
    id: Optional[int] = None


def build_deposition_type_groupby_output(
    group_object: Optional[DepositionTypeGroupByOptions],
    keys: list[str],
    value: Any,
) -> DepositionTypeGroupByOptions:
    """
    Given a list of (potentially nested) fields representing the key of a groupby query and the value,
    build the proper groupby object.
    """
    if not group_object:
        group_object = DepositionTypeGroupByOptions()

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
        case _:
            pass
    setattr(group_object, key, value)
    return group_object
