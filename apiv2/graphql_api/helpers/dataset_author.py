"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

from typing import Any, Optional, TYPE_CHECKING
import strawberry
import datetime
import uuid
from graphql_api.helpers.dataset import DatasetGroupByOptions, build_dataset_groupby_output

if TYPE_CHECKING:
    from api.types.dataset import Dataset
else:
    Dataset = "Dataset"


"""
Define groupby options for DatasetAuthor type.
These are only used in aggregate queries.
"""


@strawberry.type
class DatasetAuthorGroupByOptions:
    dataset: Optional[DatasetGroupByOptions] = None
    author_list_order: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None
    affiliation_name: Optional[str] = None
    affiliation_address: Optional[str] = None
    affiliation_identifier: Optional[str] = None
    corresponding_author_status: Optional[bool] = None
    primary_author_status: Optional[bool] = None
    orcid: Optional[str] = None
    annotation_id: Optional[int] = None
    id: Optional[int] = None


def build_dataset_author_groupby_output(
    group_object: Optional[DatasetAuthorGroupByOptions],
    keys: list[str],
    value: Any,
) -> DatasetAuthorGroupByOptions:
    """
    Given a list of (potentially nested) fields representing the key of a groupby query and the value,
    build the proper groupby object.
    """
    if not group_object:
        group_object = DatasetAuthorGroupByOptions()

    key = keys.pop(0)
    match key:
        case "dataset":
            if getattr(group_object, key):
                value = build_dataset_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = build_dataset_groupby_output(
                    None,
                    keys,
                    value,
                )
        case _:
            pass
    setattr(group_object, key, value)
    return group_object
