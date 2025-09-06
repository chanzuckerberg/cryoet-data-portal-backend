"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

from typing import TYPE_CHECKING, Annotated, Any, Optional

import graphql_api.helpers.alignment as alignment_helper
import graphql_api.helpers.annotation as annotation_helper
import graphql_api.helpers.dataset as dataset_helper
import graphql_api.helpers.frame as frame_helper
import graphql_api.helpers.frame_acquisition_file as frame_acquisition_file_helper
import graphql_api.helpers.gain_file as gain_file_helper
import graphql_api.helpers.identified_object as identified_object_helper
import graphql_api.helpers.per_section_parameters as per_section_parameters_helper
import graphql_api.helpers.tiltseries as tiltseries_helper
import graphql_api.helpers.tomogram as tomogram_helper
import graphql_api.helpers.tomogram_voxel_spacing as tomogram_voxel_spacing_helper
import strawberry

if TYPE_CHECKING:
    from graphql_api.helpers.alignment import AlignmentGroupByOptions
    from graphql_api.helpers.annotation import AnnotationGroupByOptions
    from graphql_api.helpers.dataset import DatasetGroupByOptions
    from graphql_api.helpers.frame import FrameGroupByOptions
    from graphql_api.helpers.frame_acquisition_file import FrameAcquisitionFileGroupByOptions
    from graphql_api.helpers.gain_file import GainFileGroupByOptions
    from graphql_api.helpers.identified_object import IdentifiedObjectGroupByOptions
    from graphql_api.helpers.per_section_parameters import PerSectionParametersGroupByOptions
    from graphql_api.helpers.tiltseries import TiltseriesGroupByOptions
    from graphql_api.helpers.tomogram import TomogramGroupByOptions
    from graphql_api.helpers.tomogram_voxel_spacing import TomogramVoxelSpacingGroupByOptions
else:
    AlignmentGroupByOptions = "AlignmentGroupByOptions"
    AnnotationGroupByOptions = "AnnotationGroupByOptions"
    DatasetGroupByOptions = "DatasetGroupByOptions"
    FrameGroupByOptions = "FrameGroupByOptions"
    GainFileGroupByOptions = "GainFileGroupByOptions"
    IdentifiedObjectGroupByOptions = "IdentifiedObjectGroupByOptions"
    FrameAcquisitionFileGroupByOptions = "FrameAcquisitionFileGroupByOptions"
    PerSectionParametersGroupByOptions = "PerSectionParametersGroupByOptions"
    TiltseriesGroupByOptions = "TiltseriesGroupByOptions"
    TomogramVoxelSpacingGroupByOptions = "TomogramVoxelSpacingGroupByOptions"
    TomogramGroupByOptions = "TomogramGroupByOptions"


"""
Define groupby options for Run type.
These are only used in aggregate queries.
"""


@strawberry.type
class RunGroupByOptions:
    alignments: Optional[Annotated["AlignmentGroupByOptions", strawberry.lazy("graphql_api.helpers.alignment")]] = None
    annotations: Optional[Annotated["AnnotationGroupByOptions", strawberry.lazy("graphql_api.helpers.annotation")]] = (
        None
    )
    dataset: Optional[Annotated["DatasetGroupByOptions", strawberry.lazy("graphql_api.helpers.dataset")]] = None
    frames: Optional[Annotated["FrameGroupByOptions", strawberry.lazy("graphql_api.helpers.frame")]] = None
    gain_files: Optional[Annotated["GainFileGroupByOptions", strawberry.lazy("graphql_api.helpers.gain_file")]] = None
    identified_objects: Optional[
        Annotated["IdentifiedObjectGroupByOptions", strawberry.lazy("graphql_api.helpers.identified_object")]
    ] = None
    frame_acquisition_files: Optional[
        Annotated["FrameAcquisitionFileGroupByOptions", strawberry.lazy("graphql_api.helpers.frame_acquisition_file")]
    ] = None
    per_section_parameters: Optional[
        Annotated["PerSectionParametersGroupByOptions", strawberry.lazy("graphql_api.helpers.per_section_parameters")]
    ] = None
    tiltseries: Optional[Annotated["TiltseriesGroupByOptions", strawberry.lazy("graphql_api.helpers.tiltseries")]] = (
        None
    )
    tomogram_voxel_spacings: Optional[
        Annotated["TomogramVoxelSpacingGroupByOptions", strawberry.lazy("graphql_api.helpers.tomogram_voxel_spacing")]
    ] = None
    tomograms: Optional[Annotated["TomogramGroupByOptions", strawberry.lazy("graphql_api.helpers.tomogram")]] = None
    name: Optional[str] = None
    s3_prefix: Optional[str] = None
    https_prefix: Optional[str] = None
    id: Optional[int] = None


def build_run_groupby_output(
    group_object: Optional[RunGroupByOptions],
    keys: list[str],
    value: Any,
) -> RunGroupByOptions:
    """
    Given a list of (potentially nested) fields representing the key of a groupby query and the value,
    build the proper groupby object.
    """
    if not group_object:
        group_object = RunGroupByOptions()

    key = keys.pop(0)
    match key:
        case "alignments":
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
        case "annotations":
            if getattr(group_object, key):
                value = annotation_helper.build_annotation_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = annotation_helper.build_annotation_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "dataset":
            if getattr(group_object, key):
                value = dataset_helper.build_dataset_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = dataset_helper.build_dataset_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "frames":
            if getattr(group_object, key):
                value = frame_helper.build_frame_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = frame_helper.build_frame_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "gain_files":
            if getattr(group_object, key):
                value = gain_file_helper.build_gain_file_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = gain_file_helper.build_gain_file_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "identified_objects":
            if getattr(group_object, key):
                value = identified_object_helper.build_identified_object_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = identified_object_helper.build_identified_object_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "frame_acquisition_files":
            if getattr(group_object, key):
                value = frame_acquisition_file_helper.build_frame_acquisition_file_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = frame_acquisition_file_helper.build_frame_acquisition_file_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "per_section_parameters":
            if getattr(group_object, key):
                value = per_section_parameters_helper.build_per_section_parameters_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = per_section_parameters_helper.build_per_section_parameters_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "tiltseries":
            if getattr(group_object, key):
                value = tiltseries_helper.build_tiltseries_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = tiltseries_helper.build_tiltseries_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "tomogram_voxel_spacings":
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
        case "tomograms":
            if getattr(group_object, key):
                value = tomogram_helper.build_tomogram_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = tomogram_helper.build_tomogram_groupby_output(
                    None,
                    keys,
                    value,
                )
        case _:
            pass
    setattr(group_object, key, value)
    return group_object
