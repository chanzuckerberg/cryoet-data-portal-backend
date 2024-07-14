from __future__ import annotations

from typing import List, Optional

from dataset_config_models import (
    Annotation,
    AnnotationConfidence,
    AnnotationEntity,
    AnnotationSource,
    Author,
    Container,
)
from pydantic import field_validator, model_validator
from typing_extensions import Self


def validate_authors(authors: List[Author]) -> List[ValueError]:
    errors = []
    primary_author_status_count = 0
    corresponding_author_status_count = 0
    for author in authors:
        if author.primary_author_status:
            primary_author_status_count += 1
        if author.corresponding_author_status:
            corresponding_author_status_count += 1

    if primary_author_status_count == 0:
        errors.append(ValueError("Annotation must have at least one primary author"))
    if corresponding_author_status_count == 0:
        errors.append(ValueError("Annotation must have at least one corresponding author"))

    return errors


class ExtendedValidationAnnotationConfidence(AnnotationConfidence):
    @model_validator(mode="after")
    def valid_confidence(self) -> Self:
        provided_values = []
        valid_ground_truth_used = isinstance(self.ground_truth_used, str) and len(self.ground_truth_used) > 0
        if self.precision is not None:
            provided_values.append("'precision'")
        if self.recall is not None:
            provided_values.append("'recall'")
        if len(provided_values) > 0 and not valid_ground_truth_used:
            raise ValueError(
                f"Annotation confidence must have 'ground_truth_used' if {', '.join(provided_values)} {'are' if len(provided_values) > 1 else 'is'} provided",
            )

        return self


class ExtendedValidationAnnotation(Annotation):
    confidence: Optional[ExtendedValidationAnnotationConfidence] = Annotation.model_fields["confidence"]

    @model_validator(mode="after")
    def valid_metadata(self) -> Self:
        if self.method_type == "automated" and self.ground_truth_status:
            raise ValueError(
                "Annotation metadata cannot have 'ground_truth_status' as true if 'method_type' is 'automated'",
            )
        return self

    @field_validator("authors")
    @classmethod
    def valid_annotation_authors(cls: Self, authors: List[Author]) -> List[Author]:
        author_errors = validate_authors(authors)
        if len(author_errors) > 0:
            raise ValueError(author_errors)

        return authors


class ExtendedValidationAnnotationEntity(AnnotationEntity):
    metadata: ExtendedValidationAnnotation = AnnotationEntity.model_fields["metadata"]

    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[AnnotationSource]) -> List[AnnotationSource]:
        total_errors = []

        # For verifying that all source entries don't have one shape used multiple times in different source entries
        used_shapes = set()
        shapes_used_multiple_times_errors = set()

        for source_element in source_list:
            for shape in source_element.model_fields:
                if getattr(source_element, shape) is not None:
                    # If the shape is already used in another source entry, add the shape to the error set
                    if shape in used_shapes:
                        shapes_used_multiple_times_errors.add(shape)
                    else:
                        used_shapes.add(shape)

        # For verifying that all source entries each only have one shape entry
        multiple_shapes_in_all_source_entries_errors = []

        for i, source_element in enumerate(source_list):
            shapes_in_source_entry = []
            for shape in source_element.model_fields:
                # If the shape is not None, add it to the list of shapes in the source entry
                if getattr(source_element, shape) is not None:
                    shapes_in_source_entry.append(shape)
            # If there are more than one shape in the source entry, add the source entry index and the shapes to the error set
            if len(shapes_in_source_entry) > 1:
                multiple_shapes_in_all_source_entries_errors.append((i, shapes_in_source_entry))

        if len(shapes_used_multiple_times_errors) > 0:
            total_errors.append(
                ValueError(f"Annotation cannot have multiple same-shape sources: {shapes_used_multiple_times_errors}"),
            )
        for i, shapes in multiple_shapes_in_all_source_entries_errors:
            total_errors.append(ValueError(f"Source entry {i} cannot have multiple shapes: {shapes}"))

        if len(total_errors) > 0:
            raise ValueError(total_errors)

        return source_list


class ExtendedValidationContainer(Container):
    annotations: Optional[List[ExtendedValidationAnnotationEntity]] = Container.model_fields["annotations"]


ExtendedValidationAnnotationConfidence.model_rebuild()
ExtendedValidationAnnotation.model_rebuild()
ExtendedValidationAnnotationEntity.model_rebuild()
ExtendedValidationContainer.model_rebuild()
