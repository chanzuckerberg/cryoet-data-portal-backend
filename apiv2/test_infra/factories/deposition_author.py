"""
Factory for generating DepositionAuthor objects.

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/test_infra/factories/class_name.py.j2 instead.
"""

# ruff: noqa: E501 Line too long

import factory
from database.models import DepositionAuthor
from factory import Faker, fuzzy
from faker_biology.bioseq import Bioseq
from faker_biology.physiology import Organ
from faker_enum import EnumProvider

from platformics.test_infra.factories.base import CommonFactory
from test_infra.factories.deposition import DepositionFactory

Faker.add_provider(Bioseq)
Faker.add_provider(Organ)
Faker.add_provider(EnumProvider)


class DepositionAuthorFactory(CommonFactory):
    class Meta:
        sqlalchemy_session = None  # workaround for a bug in factoryboy
        model = DepositionAuthor

        sqlalchemy_get_or_create = ("id",)

    deposition = factory.SubFactory(
        DepositionFactory,
    )

    # Auto increment integer identifiers starting with 1
    id = factory.Sequence(lambda n: n + 1)

    author_list_order = fuzzy.FuzzyInteger(1, 1000)

    orcid = fuzzy.FuzzyText()
    name = fuzzy.FuzzyText()
    email = fuzzy.FuzzyText()
    affiliation_name = fuzzy.FuzzyText()
    affiliation_address = fuzzy.FuzzyText()
    affiliation_identifier = fuzzy.FuzzyText()
    corresponding_author_status = factory.Faker("boolean")
    primary_author_status = factory.Faker("boolean")
