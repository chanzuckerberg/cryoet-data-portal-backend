"""
Test basic queries and mutations
"""

import datetime

import pytest
from tests.helpers import deep_eq

from platformics.database.connect import SyncDB
from platformics.test_infra.factories.base import SessionStorage
from test_infra.factories.dataset import DatasetFactory
from test_infra.factories.deposition import DepositionFactory

date_now = datetime.datetime.now()


@pytest.mark.asyncio
async def test_top_meta_fields_aggregate(
    sync_db: SyncDB,
    gql_client,
) -> None:
    """
    Test that we can include gql meta fields at each level of an aggregate query
    """

    # Create mock data
    with sync_db.session() as session:
        SessionStorage.set_session(session)
        DepositionFactory.create(id=12345)
        DepositionFactory.create(id=23456)
        DepositionFactory.create(id=34567)

    # Fetch all datasets that have at least one run
    query = """
        query MyQuery {
          depositionsAggregate {
            __typename
            aggregate {
              __typename
              count(columns: id)
              groupBy {
                __typename
                id
              }
            }
          }
        }
    """
    output = await gql_client.query(query)
    assert output["data"]["depositionsAggregate"]["__typename"] == "DepositionAggregate"
    aggregates = output["data"]["depositionsAggregate"]["aggregate"]
    assert len(aggregates) == 3
    dep_ids = {12345, 23456, 34567}
    for item in aggregates:
        assert item["__typename"] == "DepositionAggregateFunctions"
        assert item["count"] == 1
        assert item["groupBy"]["__typename"] == "DepositionGroupByOptions"
        assert item["groupBy"]["id"] in dep_ids


@pytest.mark.asyncio
async def test_nested_meta_fields_aggregate(
    sync_db: SyncDB,
    gql_client,
) -> None:
    """
    Test that we can include gql meta fields at each level of a nested aggregate query
    """

    # Create mock data
    with sync_db.session() as session:
        SessionStorage.set_session(session)
        d1 = DepositionFactory.create(id=12345)
        DatasetFactory.create(deposition=d1, id=222)

    # Fetch all datasets that have at least one run
    query = """
        query MyQuery {
          depositions {
            __typename
            id
            datasetsAggregate {
              __typename
              aggregate {
                __typename
                count(columns: id, distinct: true)
                sum {
                  __typename
                  id
                }
                groupBy {
                  __typename
                  id
                }
              }
            }
          }
        }
    """
    output = await gql_client.query(query)
    assert len(output["data"]["depositions"]) == 1
    aggregate = output["data"]["depositions"][0]
    assert aggregate["__typename"] == "Deposition"
    assert aggregate["id"] == 12345

    agg_info = aggregate["datasetsAggregate"]
    assert agg_info["__typename"] == "DatasetAggregate"
    assert len(agg_info["aggregate"]) == 1

    agg_data = agg_info["aggregate"][0]
    assert agg_data["__typename"] == "DatasetAggregateFunctions"
    assert agg_data["count"] == 1
    assert agg_data["sum"]["__typename"] == "DatasetNumericalColumns"
    assert agg_data["sum"]["id"] == 222
    assert agg_data["groupBy"]["__typename"] == "DatasetGroupByOptions"
    assert agg_data["groupBy"]["id"] == 222


@pytest.mark.asyncio
async def test_nested_meta_fields_resolver(
    sync_db: SyncDB,
    gql_client,
) -> None:
    """
    Test that we can include gql meta fields at each level of a nested NON-aggregate query
    """

    # Create mock data
    with sync_db.session() as session:
        SessionStorage.set_session(session)
        d1 = DepositionFactory.create(id=12345)
        DatasetFactory.create(deposition=d1, id=222)

    # Fetch all datasets that have at least one run
    query = """
        query MyQuery {
          depositions {
            __typename
            id
            datasets {
              __typename
              edges {
                __typename
                node {
                  __typename
                  id
                  deposition {
                    __typename
                    id
                  }
                }
              }
            }
          }
        }
    """
    output = await gql_client.query(query)

    expected = {
        "data": {
            "depositions": [
                {
                    "__typename": "Deposition",
                    "id": 12345,
                    "datasets": {
                        "__typename": "DatasetConnection",
                        "edges": [
                            {
                                "__typename": "DatasetEdge",
                                "node": {
                                    "__typename": "Dataset",
                                    "id": 222,
                                    "deposition": {
                                        "__typename": "Deposition",
                                        "id": 12345,
                                    },
                                },
                            },
                        ],
                    },
                },
            ],
        },
    }
    assert deep_eq(output, expected)
