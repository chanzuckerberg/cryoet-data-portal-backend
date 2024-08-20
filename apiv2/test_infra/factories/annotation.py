"""
Factory for generating Annotation objects.

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/test_infra/factories/class_name.py.j2 instead.
"""

# ruff: noqa: E501 Line too long

import factory
from database.models import Annotation
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


class AnnotationFactory(CommonFactory):
    class Meta:
        sqlalchemy_session = None  # workaround for a bug in factoryboy
        model = Annotation

        sqlalchemy_get_or_create = ("id",)

    run = factory.SubFactory(
        RunFactory,
        owner_user_id=factory.SelfAttribute("..owner_user_id"),
        collection_id=factory.SelfAttribute("..collection_id"),
    )
    deposition = factory.SubFactory(
        DepositionFactory,
        owner_user_id=factory.SelfAttribute("..owner_user_id"),
        collection_id=factory.SelfAttribute("..collection_id"),
    )
    s3_metadata_path = fuzzy.FuzzyText()
    https_metadata_path = fuzzy.FuzzyText()
    annotation_publication = fuzzy.FuzzyText()
    annotation_method = fuzzy.FuzzyText()
    ground_truth_status = factory.Faker("boolean")
    object_id = fuzzy.FuzzyText()
    object_name = fuzzy.FuzzyText()
    object_description = fuzzy.FuzzyText()
    object_state = fuzzy.FuzzyText()
    object_count = fuzzy.FuzzyInteger(1, 1000)
    confidence_precision = fuzzy.FuzzyFloat(1, 100)
    confidence_recall = fuzzy.FuzzyFloat(1, 100)
    ground_truth_used = fuzzy.FuzzyText()
    annotation_software = fuzzy.FuzzyText()
    is_curator_recommended = factory.Faker("boolean")
    method_type = fuzzy.FuzzyChoice(["manual", "automated", "hybrid"])
    deposition_date = factory.Faker("date")
    release_date = factory.Faker("date")
    last_modified_date = factory.Faker("date")
    id = fuzzy.FuzzyInteger(1, 1000)