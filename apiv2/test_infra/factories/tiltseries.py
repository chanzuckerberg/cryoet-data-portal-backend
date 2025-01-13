"""
Factory for generating Tiltseries objects.

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/test_infra/factories/class_name.py.j2 instead.
"""

# ruff: noqa: E501 Line too long

import factory
from database.models import Tiltseries
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


class TiltseriesFactory(CommonFactory):
    class Meta:
        sqlalchemy_session = None  # workaround for a bug in factoryboy
        model = Tiltseries

        sqlalchemy_get_or_create = ("id",)

    run = factory.SubFactory(
        RunFactory,
    )
    deposition = factory.SubFactory(
        DepositionFactory,
    )
    s3_omezarr_dir = fuzzy.FuzzyText()
    file_size_omezarr = fuzzy.FuzzyInteger(1, 1000)
    s3_mrc_file = fuzzy.FuzzyText()
    file_size_mrc = fuzzy.FuzzyInteger(1, 1000)
    https_omezarr_dir = fuzzy.FuzzyText()
    https_mrc_file = fuzzy.FuzzyText()
    s3_angle_list = fuzzy.FuzzyText()
    https_angle_list = fuzzy.FuzzyText()

    acceleration_voltage = fuzzy.FuzzyInteger(1, 1000)

    spherical_aberration_constant = fuzzy.FuzzyFloat(1, 100)
    microscope_manufacturer = fuzzy.FuzzyChoice(["FEI", "TFS", "JEOL", "SIMULATED"])
    microscope_model = fuzzy.FuzzyText()
    microscope_energy_filter = fuzzy.FuzzyText()
    microscope_phase_plate = fuzzy.FuzzyText()
    microscope_image_corrector = fuzzy.FuzzyText()
    microscope_additional_info = fuzzy.FuzzyText()
    camera_manufacturer = fuzzy.FuzzyText()
    camera_model = fuzzy.FuzzyText()
    tilt_min = fuzzy.FuzzyFloat(1, 100)
    tilt_max = fuzzy.FuzzyFloat(1, 100)
    tilt_range = fuzzy.FuzzyFloat(1, 100)
    tilt_step = fuzzy.FuzzyFloat(1, 100)
    tilting_scheme = fuzzy.FuzzyText()
    tilt_axis = fuzzy.FuzzyFloat(1, 100)
    total_flux = fuzzy.FuzzyFloat(1, 100)
    data_acquisition_software = fuzzy.FuzzyText()
    related_empiar_entry = fuzzy.FuzzyText()
    binning_from_frames = fuzzy.FuzzyFloat(1, 100)

    tilt_series_quality = fuzzy.FuzzyInteger(1, 1000)

    is_aligned = factory.Faker("boolean")
    pixel_spacing = fuzzy.FuzzyFloat(1, 100)

    aligned_tiltseries_binning = fuzzy.FuzzyInteger(1, 1000)

    size_x = fuzzy.FuzzyInteger(1, 1000)

    size_y = fuzzy.FuzzyInteger(1, 1000)

    size_z = fuzzy.FuzzyInteger(1, 1000)

    # Auto increment integer identifiers starting with 1
    id = factory.Sequence(lambda n: n + 1)
