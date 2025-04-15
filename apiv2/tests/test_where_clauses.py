"""
Test basic queries and mutations
"""

import datetime

import pytest
from platformics.database.connect import SyncDB
from platformics.test_infra.factories.base import SessionStorage

from test_infra.factories.annotation import AnnotationFactory
from test_infra.factories.dataset import DatasetFactory
from test_infra.factories.run import RunFactory
from test_infra.factories.tomogram import TomogramFactory

date_now = datetime.datetime.now()


@pytest.mark.asyncio
async def test_filter_query(
    sync_db: SyncDB,
    gql_client,
) -> None:
    """
    Test that we can filter by both our own fields *and* 1:many fields, *and* that we don't
    wind up with a cartesian product if there are multiple matches for the related class filter.
    """

    # Create mock data
    with sync_db.session() as session:
        SessionStorage.set_session(session)
        r1 = RunFactory.create(name="001")
        r2 = RunFactory.create(name="002")
        # create a run that matches the annotation filter but not the name filter.
        r3 = RunFactory.create(name="012")
        for run in [r1, r2, r3]:
            # important: add *two* membrane annotations for each run!
            AnnotationFactory.create(run=run, object_name="some membrane")
            AnnotationFactory.create(run=run, object_name="another membrane")
            AnnotationFactory.create(run=run, object_name="ribosome")
        # create a run that matches the name filter but not the annotation filter
        r3 = RunFactory.create(name="003")
        AnnotationFactory.create(run=r3, object_name="ribosome")

    # Fetch all runs that have membrane annotations and names starting with "00"
    query = """
        query MyQuery {
            runs (where: {name: {_like: "00%"}, annotations: {objectName: {_like: "%membrane%"}}}) {
                id,
                name
            }
        }
    """
    output = await gql_client.query(query)
    runs = [run["name"] for run in output["data"]["runs"]]
    assert len(runs) == 2
    assert "001" in runs
    assert "002" in runs


@pytest.mark.asyncio
async def test_aggregate_filter_query(
    sync_db: SyncDB,
    gql_client,
) -> None:
    """
    Test that we can combine aggregate queries and filters on the same related type and that they
    don't interfere with each other.
    """

    # Create mock data
    with sync_db.session() as session:
        SessionStorage.set_session(session)
        ds = DatasetFactory.create()
        r1 = RunFactory.create(name="001", dataset=ds)
        r2 = RunFactory.create(name="002", dataset=ds)
        # create a run that matches the annotation filter but not the name filter.
        r3 = RunFactory.create(name="012", dataset=ds)
        for run in [r1, r2, r3]:
            # important: add *two* membrane annotations for each run!
            TomogramFactory.create(run=run, name=run.name)
            AnnotationFactory.create(run=run, object_name="some membrane")
            AnnotationFactory.create(run=run, object_name="another membrane")
            AnnotationFactory.create(run=run, object_name="ribosome")
        # create a run that matches the name filter but not the annotation filter
        r3 = RunFactory.create(name="003", dataset=ds)
        TomogramFactory.create(run=r3, name=r3.name)
        AnnotationFactory.create(run=r3, object_name="ribosome")

    # Fetch aggregate stats for tomograms that belong to runs with membrane annotations.
    query = """
        query MyQuery {
            tomogramsAggregate(
                where: {name: {_like: "00%"}, run: {annotations: {objectName: {_like: "%membrane%"}}}}
            ) {
                aggregate {
                    count(columns: id)
                    groupBy {
                        run {
                            name
                            dataset {
                                id
                            }
                        }
                    }
                }
            }
        }
    """
    output = await gql_client.query(query)
    aggregates = output["data"]["tomogramsAggregate"]["aggregate"]
    assert len(aggregates) == 2
    for item in aggregates:
        assert item["count"] == 1
        assert item["groupBy"]["run"]["name"] in ["001", "002"]
