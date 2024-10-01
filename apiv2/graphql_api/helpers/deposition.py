"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

import datetime
from typing import Any, Optional

import strawberry

"""
Define groupby options for Deposition type.
These are only used in aggregate queries.
"""


@strawberry.type
class DepositionGroupByOptions:
    title: Optional[str] = None
    description: Optional[str] = None
    deposition_publications: Optional[str] = None
    related_database_entries: Optional[str] = None
    deposition_date: Optional[datetime.datetime] = None
    release_date: Optional[datetime.datetime] = None
    last_modified_date: Optional[datetime.datetime] = None
    key_photo_url: Optional[str] = None
    key_photo_thumbnail_url: Optional[str] = None
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
