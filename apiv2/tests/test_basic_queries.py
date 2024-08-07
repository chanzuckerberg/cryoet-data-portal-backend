"""
Test basic queries and mutations
"""

import datetime
import pytest
from platformics.database.connect import SyncDB
from conftest import GQLTestClient, SessionStorage
from test_infra.factories.sample import SampleFactory

date_now = datetime.datetime.now()


@pytest.mark.asyncio
async def test_graphql_query(
    sync_db: SyncDB,
    gql_client: GQLTestClient,
) -> None:
    """
    Test that we can only fetch samples from the database that we have access to
    """
    user_id = 12345
    secondary_user_id = 67890
    project_id = 123

    # Create mock data
    with sync_db.session() as session:
        SessionStorage.set_session(session)
        SampleFactory.create_batch(
            2,
            collection_location="San Francisco, CA",
            collection_date=date_now,
            owner_user_id=user_id,
            collection_id=project_id,
        )
        SampleFactory.create_batch(
            6,
            collection_location="Mountain View, CA",
            collection_date=date_now,
            owner_user_id=user_id,
            collection_id=project_id,
        )
        SampleFactory.create_batch(
            4,
            collection_location="Phoenix, AZ",
            collection_date=date_now,
            owner_user_id=secondary_user_id,
            collection_id=9999,
        )

    # Fetch all samples
    query = """
        query MyQuery {
            samples {
                id,
                collectionLocation
            }
        }
    """
    output = await gql_client.query(query, user_id=user_id, member_projects=[project_id])
    locations = [sample["collectionLocation"] for sample in output["data"]["samples"]]
    assert "San Francisco, CA" in locations
    assert "Mountain View, CA" in locations
    assert "Phoenix, AZ" not in locations


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "projects_allowed",
    [[123], [456]],
)
async def test_graphql_mutations(
    projects_allowed: list[int],
    gql_client: GQLTestClient,
) -> None:
    """
    Validate that can only create/modify samples in collections the user has access to
    """
    project_id = 123
    query = """
        mutation createOneSample {
            createSample(input: {
                name: "Test Sample"
                sampleType: "Type 1"
                waterControl: false
                collectionLocation: "San Francisco, CA"
                collectionDate: "2024-01-01"
                collectionId: 123
            }) {
                id,
                collectionLocation
            }
        }
    """
    output = await gql_client.query(query, member_projects=projects_allowed)

    # Make sure unauthorized users can't create samples in this collection
    if project_id not in projects_allowed:
        assert output["data"] is None
        assert "Unauthorized" in output["errors"][0]["message"]

    # Otherwise, modify the sample we created (note the {{ so we don't treat them as variables)
    else:
        assert output["data"]["createSample"]["collectionLocation"] == "San Francisco, CA"

        new_location = "Chicago, IL"
        sample_id = output["data"]["createSample"]["id"]
        query = f"""
            mutation modifyOneSample {{
                updateSample(
                    input: {{
                        collectionLocation: "{new_location}"
                    }}
                    where: {{
                        id: {{ _eq: "{sample_id}" }}
                    }}
                ) {{
                    id,
                    collectionLocation
                }}
            }}
        """
        output = await gql_client.query(query, member_projects=projects_allowed)
        assert output["data"]["updateSample"][0]["collectionLocation"] == new_location

        # Test deletion
        query = f"""
            mutation deleteOneSample {{
                deleteSample(
                    where: {{ id: {{ _eq: "{sample_id}" }} }}
                ) {{
                    id,
                    collectionLocation
                }}
            }}
        """
        output = await gql_client.query(query, member_projects=projects_allowed)
        assert "errors" not in output
        assert len(output["data"]["deleteSample"]) == 1
        assert output["data"]["deleteSample"][0]["id"] == sample_id
        assert output["data"]["deleteSample"][0]["collectionLocation"] == new_location

        # Try to fetch sample now that it's deleted
        query = f"""
            query GetDeletedSample {{
                samples ( where: {{ id: {{ _eq: "{sample_id}" }} }}) {{
                    id,
                    collectionLocation
                }}
            }}
        """
        output = await gql_client.query(query, member_projects=projects_allowed)
        assert output["data"]["samples"] == []
