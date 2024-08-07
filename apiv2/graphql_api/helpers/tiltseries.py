"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

from typing import Any, Optional, TYPE_CHECKING
import strawberry
import datetime
import uuid
from support.enums import tiltseries_microscope_manufacturer_enum
from graphql_api.helpers.run import RunGroupByOptions, build_run_groupby_output
from graphql_api.helpers.deposition import DepositionGroupByOptions, build_deposition_groupby_output

if TYPE_CHECKING:
    from api.types.run import Run
else:
    Run = "Run"
if TYPE_CHECKING:
    from api.types.deposition import Deposition
else:
    Deposition = "Deposition"


"""
Define groupby options for Tiltseries type.
These are only used in aggregate queries.
"""


@strawberry.type
class TiltseriesGroupByOptions:
    run: Optional[RunGroupByOptions] = None
    deposition: Optional[DepositionGroupByOptions] = None
    s3_omezarr_dir: Optional[str] = None
    s3_mrc_bin1: Optional[str] = None
    https_omezarr_dir: Optional[str] = None
    https_mrc_bin1: Optional[str] = None
    s3_collection_metadata: Optional[str] = None
    https_collection_metadata: Optional[str] = None
    s3_angle_list: Optional[str] = None
    https_angle_list: Optional[str] = None
    s3_gain_file: Optional[str] = None
    https_gain_file: Optional[str] = None
    acceleration_voltage: Optional[float] = None
    spherical_abberation_constant: Optional[float] = None
    microscope_manufacturer: Optional[tiltseries_microscope_manufacturer_enum] = None
    microscope_model: Optional[str] = None
    microscope_energy_filter: Optional[str] = None
    microscope_phase_plate: Optional[str] = None
    microscope_image_corrector: Optional[str] = None
    microscope_additional_info: Optional[str] = None
    camera_manufacturer: Optional[str] = None
    camera_model: Optional[str] = None
    tilt_min: Optional[float] = None
    tilt_max: Optional[float] = None
    tilt_range: Optional[float] = None
    tilt_step: Optional[float] = None
    tilting_scheme: Optional[str] = None
    tilt_axis: Optional[float] = None
    total_flux: Optional[float] = None
    data_acquisition_software: Optional[str] = None
    related_empiar_entry: Optional[str] = None
    binning_from_frames: Optional[float] = None
    tilt_series_quality: Optional[int] = None
    is_aligned: Optional[bool] = None
    pixel_spacing: Optional[float] = None
    aligned_tiltseries_binning: Optional[float] = None
    tiltseries_frames_count: Optional[int] = None
    id: Optional[int] = None


def build_tiltseries_groupby_output(
    group_object: Optional[TiltseriesGroupByOptions],
    keys: list[str],
    value: Any,
) -> TiltseriesGroupByOptions:
    """
    Given a list of (potentially nested) fields representing the key of a groupby query and the value,
    build the proper groupby object.
    """
    if not group_object:
        group_object = TiltseriesGroupByOptions()

    key = keys.pop(0)
    match key:
        case "run":
            if getattr(group_object, key):
                value = build_run_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = build_run_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "deposition":
            if getattr(group_object, key):
                value = build_deposition_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = build_deposition_groupby_output(
                    None,
                    keys,
                    value,
                )
        case _:
            pass
    setattr(group_object, key, value)
    return group_object
