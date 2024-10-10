import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Type

import sqlalchemy as sa
from db_import.common.config import DBImportConfig, map_to_value
from sqlalchemy.exc import NoResultFound

from platformics.database.models.base import Base

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client

    from apiv2.db_import.common.finders import ItemFinder
else:
    S3Client = object
    ItemFinder = Any

logger = logging.getLogger("db_import")


class ItemDBImporter:
    model_class: Type[Base]
    direct_mapped_fields: dict[str, list[str]] = {}
    id_fields: list[str] = []

    def __init__(self, config: DBImportConfig, input_data: dict[str, Any]):
        self.config = config
        self.input_data = input_data
        self.model_args = {}

    def _map_direct_fields(self):
        # Load direct mapped fields
        for db_key, _ in self.direct_mapped_fields.items():
            self.model_args[db_key] = map_to_value(db_key, self.direct_mapped_fields, self.input_data)

    def load_computed_fields(self):
        pass

    def _get_identifiers(self) -> dict[str, Any]:
        identifiers = {id_field: self.model_args[id_field] for id_field in self.id_fields}
        return identifiers

    def load(self, session) -> Base:
        """
        Gets the mapping, and queries to check if the table already has a record matching the id fields. If not, it will
        create a new object and insert it, else it will update the object with values from the metadata.
        """
        self._map_direct_fields()
        self.load_computed_fields()
        identifiers = self._get_identifiers()

        try:
            query = sa.select(self.model_class).where(
                sa.and_(*[getattr(self.model_class, k) == v for k, v in identifiers.items()]),
            )
            db_obj = session.scalars(query).one()
        except NoResultFound:
            db_obj = self.model_class()

        for db_key, val in self.model_args.items():
            setattr(db_obj, db_key, val)

        session.add(db_obj)

        return db_obj

    @classmethod
    def get_hash_value(cls, record: Base) -> str:
        """
        Generates hash value for a record from values of its id fields separated by "-".
        """
        return "-".join([f"{getattr(record, attr)}" for attr in cls.id_fields])


class IntegratedDBImporter(ABC):
    finder: Type[ItemFinder]
    row_importer: Type[ItemDBImporter]
    # If true, will delete stale records after importing a batch of new/updated rows.
    # This should be False for datasets since we often import one dataset at a time and
    # don't want to remove other datasets if we just processed one.
    clean_up_siblings: bool = False

    def __init__(self, config: DBImportConfig):
        self.config = config
        self.parents: dict[str, Base] = {}

    @abstractmethod
    def get_finder_args(self) -> dict[str, Any]:
        """Gets arguments to this class's cls.finder constructor."""
        pass

    @abstractmethod
    def get_filters(self) -> dict[str, Any]:
        """
        This method finds all the existing records in the DB that belong to this Importer object.
        It's used to determine which records are stale (as in, which ones weren't updated by this
        importer's latest run) and need to be deleted.
        """
        pass

    def cleanup_unused_items(self, session, imported_objects):
        """
        Looks for all rows in the database that match the filter criteria and compares them to the
        rows we just imported. Then removes any stale rows.
        """
        if not self.clean_up_siblings:
            return
        # Compare the list of objects we just imported to the list of all objects in the DB
        # that match the filter criteria, and delete any rows that we didn't import.
        existing_objs = self.get_existing_objects(session)
        keep_row_ids = [row.id for row in imported_objects]
        rows_to_delete = [row for id, row in existing_objs.items() if id not in keep_row_ids]
        for row in rows_to_delete:
            session.delete(row)

    def import_items(self):
        """
        Find all items that need to be imported, import them, and clean up any stale items.
        """
        session = self.config.get_db_session()

        finder = self.finder(self.config, **self.get_finder_args())
        items = finder.find(self.row_importer, self.parents)
        db_objects = [item.load(session) for item in items]
        session.flush()
        self.cleanup_unused_items(session, db_objects)
        session.flush()
        return db_objects

    def get_existing_objects(self, session) -> dict[int, Base]:
        """
        Creates a map of existing items by querying using the filter criteria. The map is keyed on the item id
        """
        records = session.scalars(
            sa.select(self.row_importer.model_class).where(
                sa.and_(*[getattr(self.row_importer.model_class, k) == v for k, v in self.get_filters().items()]),
            ),
        ).all()
        return {record.id: record for record in records}
