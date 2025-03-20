"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

from typing import Any, Optional, TYPE_CHECKING, Annotated
import strawberry
import datetime
import uuid
import graphql_api.helpers.run as run_helper

if TYPE_CHECKING:
    from graphql_api.helpers.run import RunGroupByOptions
else:
    RunGroupByOptions = "RunGroupByOptions"


"""
Define groupby options for GainFile type.
These are only used in aggregate queries.
"""


@strawberry.type
class GainFileGroupByOptions:
    run: Optional[Annotated["RunGroupByOptions", strawberry.lazy("graphql_api.helpers.run")]] = None
    s3_file_path: Optional[str] = None
    https_file_path: Optional[str] = None
    id: Optional[int] = None


def build_gain_file_groupby_output(
    group_object: Optional[GainFileGroupByOptions],
    keys: list[str],
    value: Any,
) -> GainFileGroupByOptions:
    """
    Given a list of (potentially nested) fields representing the key of a groupby query and the value,
    build the proper groupby object.
    """
    if not group_object:
        group_object = GainFileGroupByOptions()

    key = keys.pop(0)
    match key:
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
        case _:
            pass
    setattr(group_object, key, value)
    return group_object
