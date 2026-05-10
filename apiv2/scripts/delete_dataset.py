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
@click.option("--dry-run", is_flag=True, default=False, help="Preview cascade scope and roll back without committing.")
def delete_dataset(dataset_id: int, i_am_super_sure: str, db_uri: str, dry_run: bool):
    if not db_uri:
        db_uri = (
            f"postgresql+psycopg://{os.environ['PLATFORMICS_DATABASE_USER']}:{os.environ['PLATFORMICS_DATABASE_PASSWORD']}@{os.environ['PLATFORMICS_DATABASE_HOST']}:{os.environ['PLATFORMICS_DATABASE_PORT']}/{os.environ['PLATFORMICS_DATABASE_NAME']}",
        )

    if dry_run:
        print(f"DRY RUN: previewing cascade for dataset {dataset_id} (no commit)")
    else:
        print(f"DELETING DATASET {dataset_id}")
        if i_am_super_sure != "yes":
            print("You must specify '--i-am-super-sure yes' to delete a dataset")
            exit(1)
    db = init_sync_db(db_uri)
    with db.session() as session:
        obj = session.scalars(sa.select(models.Dataset).where(models.Dataset.id == dataset_id)).one()

        if dry_run:
            run_ids_subq = sa.select(models.Run.id).where(models.Run.dataset_id == dataset_id).scalar_subquery()
            counts = {
                "dataset": 1,
                "run": session.scalar(
                    sa.select(sa.func.count()).select_from(models.Run).where(models.Run.dataset_id == dataset_id),
                ),
                "annotation": session.scalar(
                    sa.select(sa.func.count())
                    .select_from(models.Annotation)
                    .where(models.Annotation.run_id.in_(run_ids_subq)),
                ),
                "tomogram": session.scalar(
                    sa.select(sa.func.count())
                    .select_from(models.Tomogram)
                    .where(models.Tomogram.run_id.in_(run_ids_subq)),
                ),
                "tiltseries": session.scalar(
                    sa.select(sa.func.count())
                    .select_from(models.Tiltseries)
                    .where(models.Tiltseries.run_id.in_(run_ids_subq)),
                ),
                "alignment": session.scalar(
                    sa.select(sa.func.count())
                    .select_from(models.Alignment)
                    .where(models.Alignment.run_id.in_(run_ids_subq)),
                ),
                "frame": session.scalar(
                    sa.select(sa.func.count()).select_from(models.Frame).where(models.Frame.run_id.in_(run_ids_subq)),
                ),
            }
            print("Rows that would be cascade-deleted:")
            for table, n in counts.items():
                print(f"  {table:12s} {n}")

        session.delete(obj)
        session.flush()
        if dry_run:
            session.rollback()
            print("DRY RUN: rolled back. No changes committed.")
        else:
            session.commit()


if __name__ == "__main__":
    delete_dataset()
