"""
Test basic queries and mutations
"""

import datetime

import pytest

from platformics.database.connect import SyncDB
from platformics.test_infra.factories.base import SessionStorage
from test_infra.factories.dataset import DatasetFactory
from test_infra.factories.run import RunFactory

date_now = datetime.datetime.now()


@pytest.mark.asyncio
async def test_simple_aggregate(
    sync_db: SyncDB,
    gql_client,
) -> None:
    """
    Test that we can filter datasets by the number of runs they have
    """

    # Create mock data
    with sync_db.session() as session:
        SessionStorage.set_session(session)
        d1 = DatasetFactory.create(id=12345)
        d2 = DatasetFactory.create(id=23456)
        d3 = DatasetFactory.create(id=34567)
        d4 = DatasetFactory.create(id=45678)
        RunFactory.create_batch(3, dataset=d1, name="__first__")
        RunFactory.create_batch(6, dataset=d2, name="__second__")
        RunFactory.create_batch(9, dataset=d3, name="__third__")

    # Fetch all datasets that have at least one run
    query = """
        query MyQuery {
            datasets(
                where: {runsAggregate: {count: {predicate: {_gt: 0}}}}
            ) {
                id
            }
        }
    """
    output = await gql_client.query(query)
    dataset_ids = {item["id"] for item in output["data"]["datasets"]}
    assert dataset_ids == {12345, 23456, 34567}

    # Fetch all datasets that have between 4 and 8 runs
    query = """
        query MyQuery {
            datasets(
                where: {runsAggregate: {count: {predicate: {_gt: 3, _lt: 9}}}}
            ) {
                id
            }
        }
    """
    output = await gql_client.query(query)
    dataset_ids = {item["id"] for item in output["data"]["datasets"]}
    assert dataset_ids == {23456}

    # Fetch datasets that <= 1 unique run name starting with "RUN"
    query = """
        query MyQuery {
            datasets(
              where: {runsAggregate: {count: {
                predicate: {_eq: 1},
                distinct: true,
                arguments: name,
                filter: {name: {_like: "%second%"}}}
              }}
            ) {
              id
            }
        }
    """
    output = await gql_client.query(query)
    dataset_ids = {item["id"] for item in output["data"]["datasets"]}
    assert dataset_ids == {23456}
