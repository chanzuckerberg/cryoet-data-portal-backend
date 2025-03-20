"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

import datetime
from typing import TYPE_CHECKING, Annotated, Any, Optional

import graphql_api.helpers.alignment as alignment_helper
import graphql_api.helpers.deposition as deposition_helper
import graphql_api.helpers.run as run_helper
import graphql_api.helpers.tomogram_author as tomogram_author_helper
import graphql_api.helpers.tomogram_voxel_spacing as tomogram_voxel_spacing_helper
import strawberry
from support.enums import fiducial_alignment_status_enum, tomogram_processing_enum, tomogram_reconstruction_method_enum

if TYPE_CHECKING:
    from graphql_api.helpers.alignment import AlignmentGroupByOptions
    from graphql_api.helpers.deposition import DepositionGroupByOptions
    from graphql_api.helpers.run import RunGroupByOptions
    from graphql_api.helpers.tomogram_author import TomogramAuthorGroupByOptions
    from graphql_api.helpers.tomogram_voxel_spacing import TomogramVoxelSpacingGroupByOptions
else:
    AlignmentGroupByOptions = "AlignmentGroupByOptions"
    TomogramAuthorGroupByOptions = "TomogramAuthorGroupByOptions"
    DepositionGroupByOptions = "DepositionGroupByOptions"
    RunGroupByOptions = "RunGroupByOptions"
    TomogramVoxelSpacingGroupByOptions = "TomogramVoxelSpacingGroupByOptions"


"""
Define groupby options for Tomogram type.
These are only used in aggregate queries.
"""


@strawberry.type
class TomogramGroupByOptions:
    alignment: Optional[Annotated["AlignmentGroupByOptions", strawberry.lazy("graphql_api.helpers.alignment")]] = None
    authors: Optional[
        Annotated["TomogramAuthorGroupByOptions", strawberry.lazy("graphql_api.helpers.tomogram_author")]
    ] = None
    deposition: Optional[Annotated["DepositionGroupByOptions", strawberry.lazy("graphql_api.helpers.deposition")]] = (
        None
    )
    run: Optional[Annotated["RunGroupByOptions", strawberry.lazy("graphql_api.helpers.run")]] = None
    tomogram_voxel_spacing: Optional[
        Annotated["TomogramVoxelSpacingGroupByOptions", strawberry.lazy("graphql_api.helpers.tomogram_voxel_spacing")]
    ] = None
    name: Optional[str] = None
    size_x: Optional[int] = None
    size_y: Optional[int] = None
    size_z: Optional[int] = None
    voxel_spacing: Optional[float] = None
    fiducial_alignment_status: Optional[fiducial_alignment_status_enum] = None
    reconstruction_method: Optional[tomogram_reconstruction_method_enum] = None
    processing: Optional[tomogram_processing_enum] = None
    tomogram_version: Optional[float] = None
    processing_software: Optional[str] = None
    reconstruction_software: Optional[str] = None
    is_portal_standard: Optional[bool] = None
    is_author_submitted: Optional[bool] = None
    is_visualization_default: Optional[bool] = None
    s3_omezarr_dir: Optional[str] = None
    https_omezarr_dir: Optional[str] = None
    file_size_omezarr: Optional[float] = None
    s3_mrc_file: Optional[str] = None
    https_mrc_file: Optional[str] = None
    file_size_mrc: Optional[float] = None
    scale0_dimensions: Optional[str] = None
    scale1_dimensions: Optional[str] = None
    scale2_dimensions: Optional[str] = None
    ctf_corrected: Optional[bool] = None
    offset_x: Optional[int] = None
    offset_y: Optional[int] = None
    offset_z: Optional[int] = None
    key_photo_url: Optional[str] = None
    key_photo_thumbnail_url: Optional[str] = None
    neuroglancer_config: Optional[str] = None
    publications: Optional[str] = None
    related_database_entries: Optional[str] = None
    id: Optional[int] = None
    deposition_date: Optional[datetime.datetime] = None
    release_date: Optional[datetime.datetime] = None
    last_modified_date: Optional[datetime.datetime] = None


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
                value = alignment_helper.build_alignment_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = alignment_helper.build_alignment_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "authors":
            if getattr(group_object, key):
                value = tomogram_author_helper.build_tomogram_author_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = tomogram_author_helper.build_tomogram_author_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "deposition":
            if getattr(group_object, key):
                value = deposition_helper.build_deposition_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = deposition_helper.build_deposition_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "run":
            if getattr(group_object, key):
                value = run_helper.build_run_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = run_helper.build_run_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "tomogram_voxel_spacing":
            if getattr(group_object, key):
                value = tomogram_voxel_spacing_helper.build_tomogram_voxel_spacing_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = tomogram_voxel_spacing_helper.build_tomogram_voxel_spacing_groupby_output(
                    None,
                    keys,
                    value,
                )
        case _:
            pass
    setattr(group_object, key, value)
    return group_object
