"""
Auto-generated by running `make codegen`. Do not edit!
Make changes to the template platformics/codegen/templates/test_infra/factories/class_name.py.j2 instead.

Factory for generating GainFile objects.
"""

# ruff: noqa: E501 Line too long

import factory
from database.models import GainFile
from factory import Faker, fuzzy
from faker_biology.bioseq import Bioseq
from faker_biology.physiology import Organ
from faker_enum import EnumProvider

from platformics.test_infra.factories.base import CommonFactory
from test_infra.factories.run import RunFactory

Faker.add_provider(Bioseq)
Faker.add_provider(Organ)
Faker.add_provider(EnumProvider)


class GainFileFactory(CommonFactory):
    class Meta:
        sqlalchemy_session = None  # workaround for a bug in factoryboy
        model = GainFile

        sqlalchemy_get_or_create = ("id",)

    run = factory.SubFactory(
        RunFactory,
    )
    s3_file_path = fuzzy.FuzzyText()
    https_file_path = fuzzy.FuzzyText()

    # Auto increment integer identifiers starting with 1
    id = factory.Sequence(lambda n: n + 1)
