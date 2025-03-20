"""
Factory for generating Alignment objects.

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/test_infra/factories/class_name.py.j2 instead.
"""

# ruff: noqa: E501 Line too long

import random
import factory
import uuid6
from database.models import Alignment
from platformics.test_infra.factories.base import FileFactory, CommonFactory
from test_infra.factories.deposition import DepositionFactory
from test_infra.factories.tiltseries import TiltseriesFactory
from test_infra.factories.run import RunFactory
from factory import Faker, fuzzy
from faker_biology.bioseq import Bioseq
from faker_biology.physiology import Organ
from faker_enum import EnumProvider

Faker.add_provider(Bioseq)
Faker.add_provider(Organ)
Faker.add_provider(EnumProvider)


class AlignmentFactory(CommonFactory):
    class Meta:
        sqlalchemy_session = None  # workaround for a bug in factoryboy
        model = Alignment

        sqlalchemy_get_or_create = ("id",)

    deposition = factory.SubFactory(
        DepositionFactory,
    )
    tiltseries = factory.SubFactory(
        TiltseriesFactory,
    )
    run = factory.SubFactory(
        RunFactory,
    )
    alignment_type = fuzzy.FuzzyChoice(["LOCAL", "GLOBAL"])
    alignment_method = fuzzy.FuzzyChoice(["projection_matching", "patch_tracking", "fiducial_based"])
    volume_x_dimension = fuzzy.FuzzyFloat(1, 100)
    volume_y_dimension = fuzzy.FuzzyFloat(1, 100)
    volume_z_dimension = fuzzy.FuzzyFloat(1, 100)
    volume_x_offset = fuzzy.FuzzyFloat(1, 100)
    volume_y_offset = fuzzy.FuzzyFloat(1, 100)
    volume_z_offset = fuzzy.FuzzyFloat(1, 100)
    x_rotation_offset = fuzzy.FuzzyFloat(1, 100)
    tilt_offset = fuzzy.FuzzyFloat(1, 100)
    affine_transformation_matrix = fuzzy.FuzzyText()
    s3_alignment_metadata = fuzzy.FuzzyText()
    https_alignment_metadata = fuzzy.FuzzyText()
    is_portal_standard = factory.Faker("boolean")

    # Auto increment integer identifiers starting with 1
    id = factory.Sequence(lambda n: n + 1)
