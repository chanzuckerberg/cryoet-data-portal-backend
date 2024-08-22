"""
Factory for generating Tomogram objects.

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/test_infra/factories/class_name.py.j2 instead.
"""

# ruff: noqa: E501 Line too long

import factory
from database.models import Tomogram
from factory import Faker, fuzzy
from faker_biology.bioseq import Bioseq
from faker_biology.physiology import Organ
from faker_enum import EnumProvider
from platformics.test_infra.factories.base import CommonFactory

from test_infra.factories.alignment import AlignmentFactory
from test_infra.factories.deposition import DepositionFactory
from test_infra.factories.run import RunFactory
from test_infra.factories.tomogram_voxel_spacing import TomogramVoxelSpacingFactory

Faker.add_provider(Bioseq)
Faker.add_provider(Organ)
Faker.add_provider(EnumProvider)


class TomogramFactory(CommonFactory):
    class Meta:
        sqlalchemy_session = None  # workaround for a bug in factoryboy
        model = Tomogram

        sqlalchemy_get_or_create = ("id",)

    alignment = factory.SubFactory(
        AlignmentFactory,
    )
    deposition = factory.SubFactory(
        DepositionFactory,
    )
    run = factory.SubFactory(
        RunFactory,
    )
    tomogram_voxel_spacing = factory.SubFactory(
        TomogramVoxelSpacingFactory,
    )
    name = fuzzy.FuzzyText()
    size_x = fuzzy.FuzzyFloat(1, 100)
    size_y = fuzzy.FuzzyFloat(1, 100)
    size_z = fuzzy.FuzzyFloat(1, 100)
    voxel_spacing = fuzzy.FuzzyFloat(1, 100)
    fiducial_alignment_status = fuzzy.FuzzyChoice(["FIDUCIAL", "NON_FIDUCIAL"])
    reconstruction_method = fuzzy.FuzzyChoice(["SART", "Fourier Space", "SIRT", "WBP", "Unknown"])
    processing = fuzzy.FuzzyChoice(["denoised", "filtered", "raw"])
    tomogram_version = fuzzy.FuzzyFloat(1, 100)
    processing_software = fuzzy.FuzzyText()
    reconstruction_software = fuzzy.FuzzyText()
    is_canonical = factory.Faker("boolean")
    s3_omezarr_dir = fuzzy.FuzzyText()
    https_omezarr_dir = fuzzy.FuzzyText()
    s3_mrc_scale0 = fuzzy.FuzzyText()
    https_mrc_scale0 = fuzzy.FuzzyText()
    scale0_dimensions = fuzzy.FuzzyText()
    scale1_dimensions = fuzzy.FuzzyText()
    scale2_dimensions = fuzzy.FuzzyText()
    ctf_corrected = factory.Faker("boolean")
    offset_x = fuzzy.FuzzyInteger(1, 1000)
    offset_y = fuzzy.FuzzyInteger(1, 1000)
    offset_z = fuzzy.FuzzyInteger(1, 1000)
    affine_transformation_matrix = fuzzy.FuzzyText()
    key_photo_url = fuzzy.FuzzyText()
    key_photo_thumbnail_url = fuzzy.FuzzyText()
    neuroglancer_config = fuzzy.FuzzyText()
    tomogram_type = fuzzy.FuzzyChoice(["CANONICAL", "UNKNOWN"])
    is_standardized = factory.Faker("boolean")
    id = fuzzy.FuzzyInteger(1, 1000)