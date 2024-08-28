"""
Populate the database with mock data for local development
"""

import factory.random

from platformics.database.connect import init_sync_db
from platformics.settings import CLISettings
from platformics.test_infra.factories.base import FileFactory, SessionStorage
from test_infra.factories.dataset import DatasetFactory
from test_infra.factories.run import RunFactory


def use_factoryboy() -> None:
    """
    Use factoryboy to create mock data
    """
    settings = CLISettings.model_validate({})
    app_db = init_sync_db(settings.SYNC_DB_URI)
    session = app_db.session()
    SessionStorage.set_session(session)
    factory.random.reseed_random(1234567)

    # create some datasets with multiple runs
    ds1 = DatasetFactory()
    RunFactory.create_batch(3, dataset=ds1)

    FileFactory.update_file_ids()

    session.commit()


if __name__ == "__main__":
    print("Seeding database")
    use_factoryboy()
    print("Seeding complete")
