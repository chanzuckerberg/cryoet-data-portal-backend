"""
Factory for generating Dataset objects.

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/test_infra/factories/class_name.py.j2 instead.
"""

# ruff: noqa: E501 Line too long

import factory
from database.models import Dataset
from factory import Faker, fuzzy
from faker_biology.bioseq import Bioseq
from faker_biology.physiology import Organ
from faker_enum import EnumProvider

from platformics.test_infra.factories.base import CommonFactory
from test_infra.factories.deposition import DepositionFactory

Faker.add_provider(Bioseq)
Faker.add_provider(Organ)
Faker.add_provider(EnumProvider)


class DatasetFactory(CommonFactory):
    class Meta:
        sqlalchemy_session = None  # workaround for a bug in factoryboy
        model = Dataset

        sqlalchemy_get_or_create = ("id",)

    deposition = factory.SubFactory(
        DepositionFactory,
    )
    title = fuzzy.FuzzyText()
    description = fuzzy.FuzzyText()
    organism_name = fuzzy.FuzzyText()
    organism_taxid = fuzzy.FuzzyInteger(1, 1000)
    tissue_name = fuzzy.FuzzyText()
    tissue_id = fuzzy.FuzzyText()
    cell_name = fuzzy.FuzzyText()
    cell_type_id = fuzzy.FuzzyText()
    cell_strain_name = fuzzy.FuzzyText()
    cell_strain_id = fuzzy.FuzzyText()
    sample_type = fuzzy.FuzzyChoice(
        ["cell", "tissue", "organism", "organelle", "virus", "in_vitro", "in_silico", "other"],
    )
    sample_preparation = fuzzy.FuzzyText()
    grid_preparation = fuzzy.FuzzyText()
    other_setup = fuzzy.FuzzyText()
    key_photo_url = fuzzy.FuzzyText()
    key_photo_thumbnail_url = fuzzy.FuzzyText()
    cell_component_name = fuzzy.FuzzyText()
    cell_component_id = fuzzy.FuzzyText()
    deposition_date = factory.Faker("date")
    release_date = factory.Faker("date")
    last_modified_date = factory.Faker("date")
    dataset_publications = fuzzy.FuzzyText()
    related_database_entries = fuzzy.FuzzyText()
    s3_prefix = fuzzy.FuzzyText()
    https_prefix = fuzzy.FuzzyText()
    file_size = fuzzy.FuzzyInteger(1, 1000)
    id = fuzzy.FuzzyInteger(1, 1000)
