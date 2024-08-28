"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

from typing import TYPE_CHECKING, Any, Optional

import strawberry
from graphql_api.helpers.tomogram import TomogramGroupByOptions, build_tomogram_groupby_output

if TYPE_CHECKING:
    from api.types.tomogram import Tomogram
else:
    Tomogram = "Tomogram"


"""
Define groupby options for TomogramAuthor type.
These are only used in aggregate queries.
"""


@strawberry.type
class TomogramAuthorGroupByOptions:
    tomogram: Optional[TomogramGroupByOptions] = None
    author_list_order: Optional[int] = None
    orcid: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    affiliation_name: Optional[str] = None
    affiliation_address: Optional[str] = None
    affiliation_identifier: Optional[str] = None
    corresponding_author_status: Optional[bool] = None
    primary_author_status: Optional[bool] = None
    id: Optional[int] = None


def build_tomogram_author_groupby_output(
    group_object: Optional[TomogramAuthorGroupByOptions],
    keys: list[str],
    value: Any,
) -> TomogramAuthorGroupByOptions:
    """
    Given a list of (potentially nested) fields representing the key of a groupby query and the value,
    build the proper groupby object.
    """
    if not group_object:
        group_object = TomogramAuthorGroupByOptions()

    key = keys.pop(0)
    match key:
        case "tomogram":
            if getattr(group_object, key):
                value = build_tomogram_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = build_tomogram_groupby_output(
                    None,
                    keys,
                    value,
                )
        case _:
            pass
    setattr(group_object, key, value)
    return group_object
