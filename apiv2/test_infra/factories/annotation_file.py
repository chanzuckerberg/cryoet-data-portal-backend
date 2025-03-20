"""
Factory for generating AnnotationFile objects.

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/test_infra/factories/class_name.py.j2 instead.
"""

# ruff: noqa: E501 Line too long

import factory
from database.models import AnnotationFile
from factory import Faker, fuzzy
from faker_biology.bioseq import Bioseq
from faker_biology.physiology import Organ
from faker_enum import EnumProvider

from platformics.test_infra.factories.base import CommonFactory
from test_infra.factories.alignment import AlignmentFactory
from test_infra.factories.annotation_shape import AnnotationShapeFactory
from test_infra.factories.tomogram_voxel_spacing import TomogramVoxelSpacingFactory

Faker.add_provider(Bioseq)
Faker.add_provider(Organ)
Faker.add_provider(EnumProvider)


class AnnotationFileFactory(CommonFactory):
    class Meta:
        sqlalchemy_session = None  # workaround for a bug in factoryboy
        model = AnnotationFile

        sqlalchemy_get_or_create = ("id",)


    alignment = factory.SubFactory(
        AlignmentFactory,
    )
    annotation_shape = factory.SubFactory(
        AnnotationShapeFactory,
    )
    tomogram_voxel_spacing = factory.SubFactory(
        TomogramVoxelSpacingFactory,
    )
    format = fuzzy.FuzzyText()
    s3_path = fuzzy.FuzzyText()
    file_size = fuzzy.FuzzyFloat(1, 100)
    https_path = fuzzy.FuzzyText()
    is_visualization_default = factory.Faker("boolean")
    source = fuzzy.FuzzyChoice([
        "dataset_author",
        "community",
        "portal_standard",
    ])

    # Auto increment integer identifiers starting with 1
    id = factory.Sequence(lambda n: n + 1)
