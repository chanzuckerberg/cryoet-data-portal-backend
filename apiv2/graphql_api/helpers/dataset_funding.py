"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

from typing import TYPE_CHECKING, Annotated, Any, Optional

import graphql_api.helpers.dataset as dataset_helper
import strawberry

if TYPE_CHECKING:
    from graphql_api.helpers.dataset import DatasetGroupByOptions
else:
    DatasetGroupByOptions = "DatasetGroupByOptions"


"""
Define groupby options for DatasetFunding type.
These are only used in aggregate queries.
"""


@strawberry.type
class DatasetFundingGroupByOptions:
    dataset: Optional[Annotated["DatasetGroupByOptions", strawberry.lazy("graphql_api.helpers.dataset")]] = None
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
                value = dataset_helper.build_dataset_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = dataset_helper.build_dataset_groupby_output(
                    None,
                    keys,
                    value,
                )
        case _:
            pass
    setattr(group_object, key, value)
    return group_object
