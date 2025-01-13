"""
Factory for generating Frame objects.

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/test_infra/factories/class_name.py.j2 instead.
"""

# ruff: noqa: E501 Line too long

import factory
from database.models import Frame
from factory import Faker, fuzzy
from faker_biology.bioseq import Bioseq
from faker_biology.physiology import Organ
from faker_enum import EnumProvider

from platformics.test_infra.factories.base import CommonFactory
from test_infra.factories.deposition import DepositionFactory
from test_infra.factories.run import RunFactory

Faker.add_provider(Bioseq)
Faker.add_provider(Organ)
Faker.add_provider(EnumProvider)


class FrameFactory(CommonFactory):
    class Meta:
        sqlalchemy_session = None  # workaround for a bug in factoryboy
        model = Frame

        sqlalchemy_get_or_create = ("id",)

    deposition = factory.SubFactory(
        DepositionFactory,
    )
    run = factory.SubFactory(
        RunFactory,
    )
    raw_angle = fuzzy.FuzzyFloat(1, 100)

    acquisition_order = fuzzy.FuzzyInteger(1, 1000)

    dose = fuzzy.FuzzyFloat(1, 100)
    is_gain_corrected = factory.Faker("boolean")
    s3_frame_path = fuzzy.FuzzyText()
    https_frame_path = fuzzy.FuzzyText()
    file_size = fuzzy.FuzzyInteger(1, 1000)
    # Auto increment integer identifiers starting with 1
    id = factory.Sequence(lambda n: n + 1)