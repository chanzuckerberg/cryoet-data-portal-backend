"""
Define GraphQL types and helper functions for supporting GROUPBY queries.

Auto-gereanted by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/groupby_helpers.py.j2 instead.
"""

from typing import Any, Optional, TYPE_CHECKING, Annotated
import strawberry
import datetime
import uuid
from support.enums import alignment_type_enum, alignment_method_type_enum
import graphql_api.helpers.annotation_file as annotation_file_helper
import graphql_api.helpers.per_section_alignment_parameters as per_section_alignment_parameters_helper
import graphql_api.helpers.deposition as deposition_helper
import graphql_api.helpers.tiltseries as tiltseries_helper
import graphql_api.helpers.tomogram as tomogram_helper
import graphql_api.helpers.run as run_helper

if TYPE_CHECKING:
    from graphql_api.helpers.annotation_file import AnnotationFileGroupByOptions
    from graphql_api.helpers.per_section_alignment_parameters import PerSectionAlignmentParametersGroupByOptions
    from graphql_api.helpers.deposition import DepositionGroupByOptions
    from graphql_api.helpers.tiltseries import TiltseriesGroupByOptions
    from graphql_api.helpers.tomogram import TomogramGroupByOptions
    from graphql_api.helpers.run import RunGroupByOptions
else:
    AnnotationFileGroupByOptions = "AnnotationFileGroupByOptions"
    PerSectionAlignmentParametersGroupByOptions = "PerSectionAlignmentParametersGroupByOptions"
    DepositionGroupByOptions = "DepositionGroupByOptions"
    TiltseriesGroupByOptions = "TiltseriesGroupByOptions"
    TomogramGroupByOptions = "TomogramGroupByOptions"
    RunGroupByOptions = "RunGroupByOptions"


"""
Define groupby options for Alignment type.
These are only used in aggregate queries.
"""


@strawberry.type
class AlignmentGroupByOptions:
    annotation_files: Optional[
        Annotated["AnnotationFileGroupByOptions", strawberry.lazy("graphql_api.helpers.annotation_file")]
    ] = None
    per_section_alignments: Optional[
        Annotated[
            "PerSectionAlignmentParametersGroupByOptions",
            strawberry.lazy("graphql_api.helpers.per_section_alignment_parameters"),
        ]
    ] = None
    deposition: Optional[Annotated["DepositionGroupByOptions", strawberry.lazy("graphql_api.helpers.deposition")]] = (
        None
    )
    tiltseries: Optional[Annotated["TiltseriesGroupByOptions", strawberry.lazy("graphql_api.helpers.tiltseries")]] = (
        None
    )
    tomograms: Optional[Annotated["TomogramGroupByOptions", strawberry.lazy("graphql_api.helpers.tomogram")]] = None
    run: Optional[Annotated["RunGroupByOptions", strawberry.lazy("graphql_api.helpers.run")]] = None
    alignment_type: Optional[alignment_type_enum] = None
    alignment_method: Optional[alignment_method_type_enum] = None
    volume_x_dimension: Optional[float] = None
    volume_y_dimension: Optional[float] = None
    volume_z_dimension: Optional[float] = None
    volume_x_offset: Optional[float] = None
    volume_y_offset: Optional[float] = None
    volume_z_offset: Optional[float] = None
    x_rotation_offset: Optional[float] = None
    tilt_offset: Optional[float] = None
    affine_transformation_matrix: Optional[str] = None
    s3_alignment_metadata: Optional[str] = None
    https_alignment_metadata: Optional[str] = None
    is_portal_standard: Optional[bool] = None
    id: Optional[int] = None


def build_alignment_groupby_output(
    group_object: Optional[AlignmentGroupByOptions],
    keys: list[str],
    value: Any,
) -> AlignmentGroupByOptions:
    """
    Given a list of (potentially nested) fields representing the key of a groupby query and the value,
    build the proper groupby object.
    """
    if not group_object:
        group_object = AlignmentGroupByOptions()

    key = keys.pop(0)
    match key:
        case "annotation_files":
            if getattr(group_object, key):
                value = annotation_file_helper.build_annotation_file_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = annotation_file_helper.build_annotation_file_groupby_output(
                    None,
                    keys,
                    value,
                )
        case "per_section_alignments":
            if getattr(group_object, key):
                value = per_section_alignment_parameters_helper.build_per_section_alignment_parameters_groupby_output(
                    getattr(group_object, key),
                    keys,
                    value,
                )
            else:
                value = per_section_alignment_parameters_helper.build_per_section_alignment_parameters_groupby_output(
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
        case _:
            pass
    setattr(group_object, key, value)
    return group_object
