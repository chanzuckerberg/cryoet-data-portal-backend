"""
Factory for generating AnnotationMethodLink objects.

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/test_infra/factories/class_name.py.j2 instead.
"""

# ruff: noqa: E501 Line too long

import random
import factory
import uuid6
from database.models import AnnotationMethodLink
from platformics.test_infra.factories.base import FileFactory, CommonFactory
from test_infra.factories.annotation import AnnotationFactory
from factory import Faker, fuzzy
from faker_biology.bioseq import Bioseq
from faker_biology.physiology import Organ
from faker_enum import EnumProvider

Faker.add_provider(Bioseq)
Faker.add_provider(Organ)
Faker.add_provider(EnumProvider)


class AnnotationMethodLinkFactory(CommonFactory):
    class Meta:
        sqlalchemy_session = None  # workaround for a bug in factoryboy
        model = AnnotationMethodLink

        sqlalchemy_get_or_create = ("id",)

    annotation = factory.SubFactory(
        AnnotationFactory,
    )
    link_type = fuzzy.FuzzyChoice(["documentation", "models_weights", "other", "source_code", "website"])
    name = fuzzy.FuzzyText()
    link = fuzzy.FuzzyText()

    # Auto increment integer identifiers starting with 1
    id = factory.Sequence(lambda n: n + 1)
