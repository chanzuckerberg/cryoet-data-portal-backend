"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

from typing import TYPE_CHECKING, Any, Optional

import strawberry
from graphql_api.helpers.dataset import DatasetGroupByOptions, build_dataset_groupby_output

if TYPE_CHECKING:
    from api.types.dataset import Dataset
else:
    Dataset = "Dataset"


"""
Define groupby options for DatasetFunding type.
These are only used in aggregate queries.
"""


@strawberry.type
class DatasetFundingGroupByOptions:
    dataset: Optional[DatasetGroupByOptions] = None
    funding_agency_name: Optional[str] = None
    grant_id: Optional[str] = None
    id: Optional[int] = None


def build_dataset_funding_groupby_output(
    group_object: Optional[DatasetFundingGroupByOptions],
    keys: list[str],
    value: Any,
) -> DatasetFundingGroupByOptions:
    """
    Given a list of (potentially nested) fields representing the key of a groupby query and the value,
    build the proper groupby object.
    """
    if not group_object:
        group_object = DatasetFundingGroupByOptions()

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
