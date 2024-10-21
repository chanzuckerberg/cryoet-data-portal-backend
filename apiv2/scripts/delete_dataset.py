# Copies data from a v1 GraphQL api into a v2 database.
import os

import click
import sqlalchemy as sa
from database import models

from platformics.database.connect import init_sync_db


@click.command()
@click.argument("dataset_id", required=True, type=int)
@click.option("--i-am-super-sure", help="this argument must be yes", type=str)
@click.option("--db-uri", help="Database URI", type=str)
def delete_dataset(dataset_id: int, i_am_super_sure: str, db_uri: str):
    if not db_uri:
        db_uri = (
            f"postgresql+psycopg://{os.environ['PLATFORMICS_DATABASE_USER']}:{os.environ['PLATFORMICS_DATABASE_PASSWORD']}@{os.environ['PLATFORMICS_DATABASE_HOST']}:{os.environ['PLATFORMICS_DATABASE_PORT']}/{os.environ['PLATFORMICS_DATABASE_NAME']}",
        )

    print(f"DELETING DATASET {dataset_id}")
    if i_am_super_sure != "yes":
        print("You must specify '--i-am-super-sure yes' to delete a dataset")
        exit(1)
    db = init_sync_db(db_uri)
    with db.session() as session:
        obj = session.scalars(sa.select(models.Dataset).where(models.Dataset.id == dataset_id)).one()
        session.delete(obj)
        session.flush()
        session.commit()


if __name__ == "__main__":
    delete_dataset()
