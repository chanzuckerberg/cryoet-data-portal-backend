"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

import datetime
from typing import TYPE_CHECKING, Annotated, Any, Optional

import graphql_api.helpers.dataset_author as dataset_author_helper
import graphql_api.helpers.dataset_funding as dataset_funding_helper
import graphql_api.helpers.deposition as deposition_helper
import graphql_api.helpers.run as run_helper
import strawberry
from support.enums import sample_type_enum

if TYPE_CHECKING:
    from graphql_api.helpers.dataset_author import DatasetAuthorGroupByOptions
    from graphql_api.helpers.dataset_funding import DatasetFundingGroupByOptions
    from graphql_api.helpers.deposition import DepositionGroupByOptions
    from graphql_api.helpers.run import RunGroupByOptions
else:
    DepositionGroupByOptions = "DepositionGroupByOptions"
    DatasetFundingGroupByOptions = "DatasetFundingGroupByOptions"
    DatasetAuthorGroupByOptions = "DatasetAuthorGroupByOptions"
    RunGroupByOptions = "RunGroupByOptions"


"""
Define groupby options for Dataset type.
These are only used in aggregate queries.
"""


@strawberry.type
class DatasetGroupByOptions:
    deposition: Optional[Annotated["DepositionGroupByOptions", strawberry.lazy("graphql_api.helpers.deposition")]] = (
        None
    )
    funding_sources: Optional[
        Annotated["DatasetFundingGroupByOptions", strawberry.lazy("graphql_api.helpers.dataset_funding")]
    ] = None
    authors: Optional[
        Annotated["DatasetAuthorGroupByOptions", strawberry.lazy("graphql_api.helpers.dataset_author")]
    ] = None
    runs: Optional[Annotated["RunGroupByOptions", strawberry.lazy("graphql_api.helpers.run")]] = None
    title: Optional[str] = None
    description: Optional[str] = None
    organism_name: Optional[str] = None
    organism_taxid: Optional[int] = None
    tissue_name: Optional[str] = None
    tissue_id: Optional[str] = None
    cell_name: Optional[str] = None
    cell_type_id: Optional[str] = None
    cell_strain_name: Optional[str] = None
    cell_strain_id: Optional[str] = None
    sample_type: Optional[sample_type_enum] = None
    sample_preparation: Optional[str] = None
    grid_preparation: Optional[str] = None
    other_setup: Optional[str] = None
    key_photo_url: Optional[str] = None
    key_photo_thumbnail_url: Optional[str] = None
    cell_component_name: Optional[str] = None
    cell_component_id: Optional[str] = None
    deposition_date: Optional[datetime.datetime] = None
    release_date: Optional[datetime.datetime] = None
    last_modified_date: Optional[datetime.datetime] = None
    dataset_publications: Optional[str] = None
    related_database_entries: Optional[str] = None
    s3_prefix: Optional[str] = None
    https_prefix: Optional[str] = None
    id: Optional[int] = None


def build_dataset_groupby_output(
    group_object: Optional[DatasetGroupByOptions],
    keys: list[str],
    value: Any,
) -> DatasetGroupByOptions:
    """
    Given a list of (potentially nested) fields representing the key of a groupby query and the value,
    build the proper groupby object.
    """
    if not group_object:
        group_object = DatasetGroupByOptions()

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
        case "funding_sources":
            if getattr(group_object, key):
                value = dataset_funding_helper.build_dataset_funding_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = dataset_funding_helper.build_dataset_funding_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "authors":
            if getattr(group_object, key):
                value = dataset_author_helper.build_dataset_author_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = dataset_author_helper.build_dataset_author_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "runs":
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
