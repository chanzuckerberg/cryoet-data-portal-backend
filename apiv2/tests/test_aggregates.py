"""
Test basic queries and mutations
"""

import datetime

import pytest

from platformics.database.connect import SyncDB
from platformics.test_infra.factories.base import SessionStorage
from test_infra.factories.annotation import AnnotationFactory
from test_infra.factories.annotation_shape import AnnotationShapeFactory
from test_infra.factories.dataset import DatasetFactory, DepositionFactory
from test_infra.factories.run import RunFactory

date_now = datetime.datetime.now()


@pytest.mark.asyncio
async def test_simple_aggregate(
    sync_db: SyncDB,
    gql_client,
) -> None:
    """
    Test that we can aggregate and filter by both our own fields *and* 1:many fields, *and* that we don't
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
                annotationsAggregate {
                    aggregate {
                        count
                    }
                }
            }
        }
    """
    output = await gql_client.query(query)
    runs = output["data"]["runs"]
    assert len(runs) == 2
    # I know this looks weird, but this is actually correct!!
    # We've filtered *runs* by runs that contain membrane annotations, but for the matching runs
    # we want to count *ALL* annotations.
    assert runs[0]["annotationsAggregate"]["aggregate"][0]["count"] == 3


@pytest.mark.asyncio
async def test_filtered_aggregate(
    sync_db: SyncDB,
    gql_client,
) -> None:
    """
    Test that we can aggregate and filter by both our own fields *and* 1:many fields, *and* that we don't
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
            runsAggregate (where: {name: {_like: "00%"}, annotations: {objectName: {_like: "%membrane%"}}}) {
                aggregate {
                  count
                }
            }
        }
    """
    output = await gql_client.query(query)
    runs = output["data"]["runsAggregate"]
    assert len(runs) == 1
    assert runs["aggregate"][0]["count"] == 2


@pytest.mark.asyncio
async def test_onetomany_groupby_aggregate(
    sync_db: SyncDB,
    gql_client,
) -> None:
    """
    Test that we can group aggregates on 1:many relationships.
    """

    # Create mock data
    with sync_db.session() as session:
        SessionStorage.set_session(session)
        dep = DepositionFactory.create()
        dep2 = DepositionFactory.create()
        ds = DatasetFactory.create(deposition=dep)
        r1 = RunFactory.create(name="001", dataset=ds)
        r2 = RunFactory.create(name="002", dataset=ds)
        # create a run that matches the annotation filter but not the name filter.
        r3 = RunFactory.create(name="012", dataset=ds)
        for run in [r1, r2, r3]:
            annos = []
            annos.append(AnnotationFactory.create(run=run, object_name="some membrane", deposition=dep))
            annos.append(AnnotationFactory.create(run=run, object_name="another membrane", deposition=dep))
            annos.append(AnnotationFactory.create(run=run, object_name="ribosome", deposition=dep))
            annos.append(AnnotationFactory.create(run=run, object_name="ribosome", deposition=dep2))
            for anno in annos:
                AnnotationShapeFactory.create(annotation=anno, shape_type="SegmentationMask")
            AnnotationShapeFactory.create(annotation=annos[1], shape_type="OrientedPoint")

    # Fetch aggregate stats for tomograms that belong to runs with membrane annotations.
    query = """
        query MyQuery {
            depositions {
                id
                annotationsAggregate {
                    aggregate {
                        count(columns: id)
                        groupBy {
                            annotationShapes {
                                shapeType
                            }
                        }
                    }
                }
            }
        }
    """
    output = await gql_client.query(query)
    depositions = output["data"]["depositions"]
    assert len(depositions) == 2
    gql_dep_1 = [item for item in depositions if item["id"] == dep.id].pop()
    gql_dep_2 = [item for item in depositions if item["id"] == dep2.id].pop()
    # We have seg masks and oriented points for dep 1
    dep1_aggs = gql_dep_1["annotationsAggregate"]["aggregate"]
    assert len(dep1_aggs) == 2
    dep1_points = [
        item for item in dep1_aggs if item["groupBy"]["annotationShapes"]["shapeType"] == "OrientedPoint"
    ].pop()
    dep1_masks = [
        item for item in dep1_aggs if item["groupBy"]["annotationShapes"]["shapeType"] == "SegmentationMask"
    ].pop()
    assert dep1_points["count"] == 3
    assert dep1_masks["count"] == 9
    # We only have seg masks for dep 2
    dep2_aggs = gql_dep_2["annotationsAggregate"]["aggregate"]
    assert len(dep2_aggs) == 1
    assert dep2_aggs[0]["groupBy"]["annotationShapes"]["shapeType"] == "SegmentationMask"
    assert dep2_aggs[0]["count"] == 3


@pytest.mark.asyncio
async def test_manytoone_groupby_aggregate(
    sync_db: SyncDB,
    gql_client,
) -> None:
    """
    Test that we can group aggregates on many:1 relationships.
    """

    # Create mock data
    with sync_db.session() as session:
        SessionStorage.set_session(session)
        dep = DepositionFactory.create()
        dep2 = DepositionFactory.create()
        ds = DatasetFactory.create(deposition=dep)
        r1 = RunFactory.create(name="001", dataset=ds)
        r2 = RunFactory.create(name="002", dataset=ds)
        # create a run that matches the annotation filter but not the name filter.
        r3 = RunFactory.create(name="012", dataset=ds)
        for run in [r1, r2, r3]:
            annos = []
            annos.append(AnnotationFactory.create(run=run, object_name="some membrane", deposition=dep))
            annos.append(AnnotationFactory.create(run=run, object_name="another membrane", deposition=dep))
            annos.append(AnnotationFactory.create(run=run, object_name="ribosome", deposition=dep))
            annos.append(AnnotationFactory.create(run=run, object_name="ribosome", deposition=dep2))
            for anno in annos:
                AnnotationShapeFactory.create(annotation=anno, shape_type="SegmentationMask")
            AnnotationShapeFactory.create(annotation=annos[1], shape_type="OrientedPoint")

    # Fetch aggregate stats for tomograms that belong to runs with membrane annotations.
    query = """
        query MyQuery {
            depositions {
                id
                annotationsAggregate {
                    aggregate {
                        count(columns: id)
                        groupBy {
                            run {
                                id
                            }
                        }
                    }
                }
            }
        }
    """
    output = await gql_client.query(query)
    depositions = output["data"]["depositions"]
    assert len(depositions) == 2
    gql_dep_1 = [item for item in depositions if item["id"] == dep.id].pop()
    gql_dep_2 = [item for item in depositions if item["id"] == dep2.id].pop()

    dep1_aggs = gql_dep_1["annotationsAggregate"]["aggregate"]
    assert len(dep1_aggs) == 3
    for item in dep1_aggs:
        assert item["count"] == 3

    dep2_aggs = gql_dep_2["annotationsAggregate"]["aggregate"]
    assert len(dep2_aggs) == 3
    for item in dep2_aggs:
        assert item["count"] == 1
