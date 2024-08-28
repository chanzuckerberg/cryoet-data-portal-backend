"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

from typing import Any, Optional, TYPE_CHECKING
import strawberry
import datetime
import uuid


"""
Define groupby options for Deposition type.
These are only used in aggregate queries.
"""


@strawberry.type
class DepositionGroupByOptions:
    deposition_title: Optional[str] = None
    deposition_description: Optional[str] = None
    publications: Optional[str] = None
    related_database_entries: Optional[str] = None
    deposition_date: Optional[datetime.datetime] = None
    release_date: Optional[datetime.datetime] = None
    last_modified_date: Optional[datetime.datetime] = None
    id: Optional[int] = None


def build_deposition_groupby_output(
    group_object: Optional[DepositionGroupByOptions],
    keys: list[str],
    value: Any,
) -> DepositionGroupByOptions:
    """
    Given a list of (potentially nested) fields representing the key of a groupby query and the value,
    build the proper groupby object.
    """
    if not group_object:
        group_object = DepositionGroupByOptions()

    key = keys.pop(0)
    match key:
        case _:
            pass
    setattr(group_object, key, value)
    return group_object
