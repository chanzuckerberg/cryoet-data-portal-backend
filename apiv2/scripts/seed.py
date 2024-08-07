"""
Populate the database with mock data for local development
"""

import factory.random
from platformics.database.connect import init_sync_db
from platformics.settings import CLISettings
from platformics.test_infra.factories.base import FileFactory, SessionStorage
from test_infra.factories.sample import SampleFactory
from test_infra.factories.sequencing_read import SequencingReadFactory


def use_factoryboy() -> None:
    """
    Use factoryboy to create mock data
    """
    settings = CLISettings.model_validate({})
    app_db = init_sync_db(settings.SYNC_DB_URI)
    session = app_db.session()
    SessionStorage.set_session(session)
    factory.random.reseed_random(1234567)

    # create some samples with multiple SequencingReads
    sa1 = SampleFactory(owner_user_id=222, collection_id=555)
    sa2 = SampleFactory(owner_user_id=333, collection_id=666)
    sa3 = SampleFactory(owner_user_id=111, collection_id=444)

    SequencingReadFactory.create_batch(3, sample=sa1, owner_user_id=sa1.owner_user_id, collection_id=sa1.collection_id)
    SequencingReadFactory.create_batch(2, sample=sa2, owner_user_id=sa2.owner_user_id, collection_id=sa2.collection_id)
    SequencingReadFactory.create_batch(3, sample=sa3, owner_user_id=sa3.owner_user_id, collection_id=sa3.collection_id)

    FileFactory.update_file_ids()

    session.commit()


if __name__ == "__main__":
    print("Seeding database")
    use_factoryboy()
    print("Seeding complete")
