"""
Supported GraphQL queries for files and entities

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/graphql_api/queries.py.j2 instead.
"""

import strawberry
from strawberry import relay
from typing import Sequence, List
from graphql_api.types.gain_file import GainFile, resolve_gain_files, GainFileAggregate, resolve_gain_files_aggregate
from graphql_api.types.frame_acquisition_file import (
    FrameAcquisitionFile,
    resolve_frame_acquisition_files,
    FrameAcquisitionFileAggregate,
    resolve_frame_acquisition_files_aggregate,
)
from graphql_api.types.alignment import Alignment, resolve_alignments, AlignmentAggregate, resolve_alignments_aggregate
from graphql_api.types.annotation_author import (
    AnnotationAuthor,
    resolve_annotation_authors,
    AnnotationAuthorAggregate,
    resolve_annotation_authors_aggregate,
)
from graphql_api.types.annotation_file import (
    AnnotationFile,
    resolve_annotation_files,
    AnnotationFileAggregate,
    resolve_annotation_files_aggregate,
)
from graphql_api.types.annotation_shape import (
    AnnotationShape,
    resolve_annotation_shapes,
    AnnotationShapeAggregate,
    resolve_annotation_shapes_aggregate,
)
from graphql_api.types.annotation import (
    Annotation,
    resolve_annotations,
    AnnotationAggregate,
    resolve_annotations_aggregate,
)
from graphql_api.types.dataset_author import (
    DatasetAuthor,
    resolve_dataset_authors,
    DatasetAuthorAggregate,
    resolve_dataset_authors_aggregate,
)
from graphql_api.types.dataset_funding import (
    DatasetFunding,
    resolve_dataset_funding,
    DatasetFundingAggregate,
    resolve_dataset_funding_aggregate,
)
from graphql_api.types.dataset import Dataset, resolve_datasets, DatasetAggregate, resolve_datasets_aggregate
from graphql_api.types.deposition_author import (
    DepositionAuthor,
    resolve_deposition_authors,
    DepositionAuthorAggregate,
    resolve_deposition_authors_aggregate,
)
from graphql_api.types.deposition import (
    Deposition,
    resolve_depositions,
    DepositionAggregate,
    resolve_depositions_aggregate,
)
from graphql_api.types.deposition_type import (
    DepositionType,
    resolve_deposition_types,
    DepositionTypeAggregate,
    resolve_deposition_types_aggregate,
)
from graphql_api.types.frame import Frame, resolve_frames, FrameAggregate, resolve_frames_aggregate
from graphql_api.types.per_section_alignment_parameters import (
    PerSectionAlignmentParameters,
    resolve_per_section_alignment_parameters,
    PerSectionAlignmentParametersAggregate,
    resolve_per_section_alignment_parameters_aggregate,
)
from graphql_api.types.per_section_parameters import (
    PerSectionParameters,
    resolve_per_section_parameters,
    PerSectionParametersAggregate,
    resolve_per_section_parameters_aggregate,
)
from graphql_api.types.run import Run, resolve_runs, RunAggregate, resolve_runs_aggregate
from graphql_api.types.tiltseries import (
    Tiltseries,
    resolve_tiltseries,
    TiltseriesAggregate,
    resolve_tiltseries_aggregate,
)
from graphql_api.types.tomogram_author import (
    TomogramAuthor,
    resolve_tomogram_authors,
    TomogramAuthorAggregate,
    resolve_tomogram_authors_aggregate,
)
from graphql_api.types.tomogram_voxel_spacing import (
    TomogramVoxelSpacing,
    resolve_tomogram_voxel_spacings,
    TomogramVoxelSpacingAggregate,
    resolve_tomogram_voxel_spacings_aggregate,
)
from graphql_api.types.tomogram import Tomogram, resolve_tomograms, TomogramAggregate, resolve_tomograms_aggregate
from graphql_api.types.annotation_method_link import (
    AnnotationMethodLink,
    resolve_annotation_method_links,
    AnnotationMethodLinkAggregate,
    resolve_annotation_method_links_aggregate,
)


@strawberry.type
class Query:
    # Allow relay-style queries by node ID
    #    node: relay.Node = relay.node()
    #    nodes: List[relay.Node] = relay.node()

    #

    # Query entities
    gain_files: Sequence[GainFile] = resolve_gain_files
    frame_acquisition_files: Sequence[FrameAcquisitionFile] = resolve_frame_acquisition_files
    alignments: Sequence[Alignment] = resolve_alignments
    annotation_authors: Sequence[AnnotationAuthor] = resolve_annotation_authors
    annotation_files: Sequence[AnnotationFile] = resolve_annotation_files
    annotation_shapes: Sequence[AnnotationShape] = resolve_annotation_shapes
    annotations: Sequence[Annotation] = resolve_annotations
    dataset_authors: Sequence[DatasetAuthor] = resolve_dataset_authors
    dataset_funding: Sequence[DatasetFunding] = resolve_dataset_funding
    datasets: Sequence[Dataset] = resolve_datasets
    deposition_authors: Sequence[DepositionAuthor] = resolve_deposition_authors
    depositions: Sequence[Deposition] = resolve_depositions
    deposition_types: Sequence[DepositionType] = resolve_deposition_types
    frames: Sequence[Frame] = resolve_frames
    per_section_alignment_parameters: Sequence[PerSectionAlignmentParameters] = resolve_per_section_alignment_parameters
    per_section_parameters: Sequence[PerSectionParameters] = resolve_per_section_parameters
    runs: Sequence[Run] = resolve_runs
    tiltseries: Sequence[Tiltseries] = resolve_tiltseries
    tomogram_authors: Sequence[TomogramAuthor] = resolve_tomogram_authors
    tomogram_voxel_spacings: Sequence[TomogramVoxelSpacing] = resolve_tomogram_voxel_spacings
    tomograms: Sequence[Tomogram] = resolve_tomograms
    annotation_method_links: Sequence[AnnotationMethodLink] = resolve_annotation_method_links

    # Query entity aggregates
    gain_files_aggregate: GainFileAggregate = resolve_gain_files_aggregate
    frame_acquisition_files_aggregate: FrameAcquisitionFileAggregate = resolve_frame_acquisition_files_aggregate
    alignments_aggregate: AlignmentAggregate = resolve_alignments_aggregate
    annotation_authors_aggregate: AnnotationAuthorAggregate = resolve_annotation_authors_aggregate
    annotation_files_aggregate: AnnotationFileAggregate = resolve_annotation_files_aggregate
    annotation_shapes_aggregate: AnnotationShapeAggregate = resolve_annotation_shapes_aggregate
    annotations_aggregate: AnnotationAggregate = resolve_annotations_aggregate
    dataset_authors_aggregate: DatasetAuthorAggregate = resolve_dataset_authors_aggregate
    dataset_funding_aggregate: DatasetFundingAggregate = resolve_dataset_funding_aggregate
    datasets_aggregate: DatasetAggregate = resolve_datasets_aggregate
    deposition_authors_aggregate: DepositionAuthorAggregate = resolve_deposition_authors_aggregate
    depositions_aggregate: DepositionAggregate = resolve_depositions_aggregate
    deposition_types_aggregate: DepositionTypeAggregate = resolve_deposition_types_aggregate
    frames_aggregate: FrameAggregate = resolve_frames_aggregate
    per_section_alignment_parameters_aggregate: PerSectionAlignmentParametersAggregate = (
        resolve_per_section_alignment_parameters_aggregate
    )
    per_section_parameters_aggregate: PerSectionParametersAggregate = resolve_per_section_parameters_aggregate
    runs_aggregate: RunAggregate = resolve_runs_aggregate
    tiltseries_aggregate: TiltseriesAggregate = resolve_tiltseries_aggregate
    tomogram_authors_aggregate: TomogramAuthorAggregate = resolve_tomogram_authors_aggregate
    tomogram_voxel_spacings_aggregate: TomogramVoxelSpacingAggregate = resolve_tomogram_voxel_spacings_aggregate
    tomograms_aggregate: TomogramAggregate = resolve_tomograms_aggregate
    annotation_method_links_aggregate: AnnotationMethodLinkAggregate = resolve_annotation_method_links_aggregate
