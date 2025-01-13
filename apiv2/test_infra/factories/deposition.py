"""
Factory for generating Deposition objects.

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/test_infra/factories/class_name.py.j2 instead.
"""

# ruff: noqa: E501 Line too long

import factory
from database.models import Deposition
from factory import Faker, fuzzy
from faker_biology.bioseq import Bioseq
from faker_biology.physiology import Organ
from faker_enum import EnumProvider

from platformics.test_infra.factories.base import CommonFactory

Faker.add_provider(Bioseq)
Faker.add_provider(Organ)
Faker.add_provider(EnumProvider)


class DepositionFactory(CommonFactory):
    class Meta:
        sqlalchemy_session = None  # workaround for a bug in factoryboy
        model = Deposition

        sqlalchemy_get_or_create = ("id",)

    title = fuzzy.FuzzyText()
    description = fuzzy.FuzzyText()
    deposition_publications = fuzzy.FuzzyText()
    related_database_entries = fuzzy.FuzzyText()
    deposition_date = factory.Faker("date")
    release_date = factory.Faker("date")
    last_modified_date = factory.Faker("date")
    key_photo_url = fuzzy.FuzzyText()
    key_photo_thumbnail_url = fuzzy.FuzzyText()

    # Auto increment integer identifiers starting with 1
    id = factory.Sequence(lambda n: n + 1)
