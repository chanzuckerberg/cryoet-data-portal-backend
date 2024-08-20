"""
Test basic queries and mutations
"""

import datetime

import pytest
from conftest import GQLTestClient, SessionStorage
from platformics.database.connect import SyncDB

from test_infra.factories.dataset import DatasetFactory

date_now = datetime.datetime.now()


@pytest.mark.asyncio
async def test_graphql_query(
    sync_db: SyncDB,
    gql_client: GQLTestClient,
) -> None:
    """
    Test that we can only fetch datasets from the database that we have access to
    """

    # Create mock data
    with sync_db.session() as session:
        SessionStorage.set_session(session)
        DatasetFactory.create(title="first")
        DatasetFactory.create(title="second")
        DatasetFactory.create(title="third")

    # Fetch all datasets
    query = """
        query MyQuery {
            datasets {
                id,
                title
            }
        }
    """
    output = await gql_client.query(query)
    datasets = [dataset["title"] for dataset in output["data"]["datasets"]]
    assert "first" in datasets
    assert "second" in datasets
    assert "third" in datasets
