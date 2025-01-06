"""
Test basic queries and mutations
"""

import datetime

import pytest

from platformics.database.connect import SyncDB
from platformics.test_infra.factories.base import SessionStorage
from test_infra.factories.dataset import DatasetFactory
from test_infra.factories.deposition import DepositionFactory
from test_infra.factories.run import RunFactory

date_now = datetime.datetime.now()


@pytest.mark.asyncio
async def test_simple_aggregate_filter(
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
        DatasetFactory.create(id=45678)  # Just extra data that shouldn't be included by default.
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


@pytest.mark.asyncio
async def test_nested_aggregate_filter(
    sync_db: SyncDB,
    gql_client,
) -> None:
    """
    Test that we can filter depositions by the number of runs in deposited datasets
    """

    # Create mock data
    with sync_db.session() as session:
        SessionStorage.set_session(session)
        dep1 = DepositionFactory(id=111)
        dep2 = DepositionFactory(id=222)
        dep3 = DepositionFactory(id=333)
        d1 = DatasetFactory.create(id=12345, deposition=dep1)
        d2 = DatasetFactory.create(id=23456, deposition=dep2)
        d3 = DatasetFactory.create(id=34567, deposition=dep3)  # Two datasets with the same deposition
        d4 = DatasetFactory.create(id=45678, deposition=dep3)  # Two datasets with the same deposition
        RunFactory.create_batch(3, dataset=d1, name="__first__")
        RunFactory.create_batch(6, dataset=d2, name="__second__")
        RunFactory.create_batch(9, dataset=d3, name="__third__")
        RunFactory.create_batch(1, dataset=d4, name="__fourth__")

    # Fetch all depositions that have datasets with 9 runs
    query = """
        query MyQuery($_num_runs: Int = 9) {
          depositions(
            where: {datasets: {runsAggregate: {count: {predicate: {_eq: $_num_runs}}}}}
          ) {
            id
          }
        }
    """
    output = await gql_client.query(query)
    deposition_ids = {item["id"] for item in output["data"]["depositions"]}
    assert deposition_ids == {333}
