"""
File factory
"""

import factory
import faker
import sqlalchemy as sa
from factory import Faker, fuzzy
from faker_biology.bioseq import Bioseq
from faker_biology.physiology import Organ
from faker_enum import EnumProvider

from platformics.database.models.file import File, FileStatus
from platformics.support import sqlalchemy_helpers

Faker.add_provider(Bioseq)
Faker.add_provider(Organ)
Faker.add_provider(EnumProvider)


def generate_relative_file_path(obj) -> str:  # type: ignore
    fake = faker.Faker()
    # Can't use absolute=True param because that requires newer version of faker than faker-biology supports
    return fake.file_path(depth=3, extension=obj.file_format).lstrip("/")


class SessionStorage:
    """
    TODO: this is a lame singleton to prevent this library from requiring an active SA session at import-time. We
    should try to refactor it out when we know more about factoryboy
    """

    session = None

    @classmethod
    def set_session(cls, session: sa.orm.Session) -> None:
        cls.session = session

    @classmethod
    def get_session(cls) -> sa.orm.Session | None:
        return cls.session


class CommonFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Base class for all factories
    """

    class Meta:
        sqlalchemy_session_factory = SessionStorage.get_session
        sqlalchemy_session_persistence = "commit"
        sqlalchemy_session = None  # workaround for a bug in factoryboy


class FileFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Factory for generating files
    """

    class Meta:
        sqlalchemy_session_factory = SessionStorage.get_session
        sqlalchemy_session_persistence = "commit"
        sqlalchemy_session = None  # workaround for a bug in factoryboy
        model = File
        # What fields do we try to match to existing db rows to determine whether we
        # should create a new row or not?
        sqlalchemy_get_or_create = ("namespace", "path")

    status = factory.Faker("enum", enum_cls=FileStatus)
    protocol = "s3"
    namespace = fuzzy.FuzzyChoice(["local-bucket", "remote-bucket"])
    path = factory.LazyAttribute(lambda o: generate_relative_file_path(o))
    file_format = fuzzy.FuzzyChoice(["fasta", "fastq", "bam"])
    compression_type = fuzzy.FuzzyChoice(["gz", "bz2", "xz"])
    size = fuzzy.FuzzyInteger(1024, 1024 * 1024 * 1024)  # Between 1k and 1G
    upload_client = fuzzy.FuzzyChoice(["browser", "cli", "s3", "basespace"])

    @classmethod
    def update_file_ids(cls) -> None:
        """
        Function used by tests after creating entities to link files to entities
        e.g. for SequencingRead, sets SequencingRead.r1_file_id = File.id
        """
        session = SessionStorage.get_session()
        if not session:
            raise Exception("No session found")
        # For each file, find the entity associated with it
        # and update the file_id for that entity.
        files = session.query(File).all()

        for file in files:
            if file.entity_id:
                related_class = sqlalchemy_helpers.get_orm_class_by_name(file.entity_class_name)
                table_entity = related_class.__table__
                _, pk_col = sqlalchemy_helpers.get_primary_key(table_entity)
                entity_field_name = f"{file.entity_field_name}_id"

                entity = session.query(related_class).filter(pk_col == file.entity_id).first()
                if entity:
                    setattr(entity, entity_field_name, file.id)
        session.commit()
