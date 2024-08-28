"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

from typing import Any, Optional, TYPE_CHECKING
import strawberry
import datetime
import uuid
from support.enums import (
    fiducial_alignment_status_enum,
    tomogram_reconstruction_method_enum,
    tomogram_processing_enum,
    tomogram_type_enum,
)
from graphql_api.helpers.alignment import AlignmentGroupByOptions, build_alignment_groupby_output
from graphql_api.helpers.deposition import DepositionGroupByOptions, build_deposition_groupby_output
from graphql_api.helpers.run import RunGroupByOptions, build_run_groupby_output
from graphql_api.helpers.tomogram_voxel_spacing import (
    TomogramVoxelSpacingGroupByOptions,
    build_tomogram_voxel_spacing_groupby_output,
)

if TYPE_CHECKING:
    from api.types.alignment import Alignment
else:
    Alignment = "Alignment"
if TYPE_CHECKING:
    from api.types.deposition import Deposition
else:
    Deposition = "Deposition"
if TYPE_CHECKING:
    from api.types.run import Run
else:
    Run = "Run"
if TYPE_CHECKING:
    from api.types.tomogram_voxel_spacing import TomogramVoxelSpacing
else:
    TomogramVoxelSpacing = "TomogramVoxelSpacing"


"""
Define groupby options for Tomogram type.
These are only used in aggregate queries.
"""


@strawberry.type
class TomogramGroupByOptions:
    alignment: Optional[AlignmentGroupByOptions] = None
    deposition: Optional[DepositionGroupByOptions] = None
    run: Optional[RunGroupByOptions] = None
    tomogram_voxel_spacing: Optional[TomogramVoxelSpacingGroupByOptions] = None
    name: Optional[str] = None
    size_x: Optional[float] = None
    size_y: Optional[float] = None
    size_z: Optional[float] = None
    voxel_spacing: Optional[float] = None
    fiducial_alignment_status: Optional[fiducial_alignment_status_enum] = None
    reconstruction_method: Optional[tomogram_reconstruction_method_enum] = None
    processing: Optional[tomogram_processing_enum] = None
    tomogram_version: Optional[float] = None
    processing_software: Optional[str] = None
    reconstruction_software: Optional[str] = None
    is_canonical: Optional[bool] = None
    s3_omezarr_dir: Optional[str] = None
    https_omezarr_dir: Optional[str] = None
    s3_mrc_file: Optional[str] = None
    https_mrc_file: Optional[str] = None
    scale0_dimensions: Optional[str] = None
    scale1_dimensions: Optional[str] = None
    scale2_dimensions: Optional[str] = None
    ctf_corrected: Optional[bool] = None
    offset_x: Optional[int] = None
    offset_y: Optional[int] = None
    offset_z: Optional[int] = None
    affine_transformation_matrix: Optional[str] = None
    key_photo_url: Optional[str] = None
    key_photo_thumbnail_url: Optional[str] = None
    neuroglancer_config: Optional[str] = None
    tomogram_type: Optional[tomogram_type_enum] = None
    is_standardized: Optional[bool] = None
    id: Optional[int] = None


def build_tomogram_groupby_output(
    group_object: Optional[TomogramGroupByOptions],
    keys: list[str],
    value: Any,
) -> TomogramGroupByOptions:
    """
    Given a list of (potentially nested) fields representing the key of a groupby query and the value,
    build the proper groupby object.
    """
    if not group_object:
        group_object = TomogramGroupByOptions()

    key = keys.pop(0)
    match key:
        case "alignment":
            if getattr(group_object, key):
                value = build_alignment_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = build_alignment_groupby_output(
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
        case "tomogram_voxel_spacing":
            if getattr(group_object, key):
                value = build_tomogram_voxel_spacing_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = build_tomogram_voxel_spacing_groupby_output(
                    None,
                    keys,
                    value,
                )
        case _:
            pass
    setattr(group_object, key, value)
    return group_object
