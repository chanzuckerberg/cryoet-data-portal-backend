"""
Test basic queries and mutations
"""

import datetime

import pytest

from platformics.database.connect import SyncDB
from platformics.test_infra.factories.base import SessionStorage
from test_infra.factories.deposition import DepositionFactory

date_now = datetime.datetime.now()


@pytest.mark.asyncio
async def test_meta_fields_aggregate(
    sync_db: SyncDB,
    gql_client,
) -> None:
    """
    Test that we can filter datasets by the number of runs they have
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
