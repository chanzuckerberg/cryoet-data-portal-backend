from __future__ import annotations

from typing import List, Optional

from dataset_config_models import (
    Annotation,
    AnnotationConfidence,
    AnnotationEntity,
    AnnotationSource,
    Container,
)
from pydantic import field_validator


class ExtendedValidationContainer(Container):
    annotations: Optional[List[ExtendedValidationAnnotationEntity]]


class ExtendedValidationAnnotationEntity(AnnotationEntity):
    metadata: Optional[ExtendedValidationAnnotation]
    sources: List[AnnotationSource]

    @field_validator("metadata")
    @classmethod
    def valid_metadata(cls, value: Optional[ExtendedValidationAnnotation]) -> Optional[ExtendedValidationAnnotation]:
        if value is None:
            return None
        if value.__getattribute__("method_type") == "automated" and value.__getattribute__("ground_truth_status"):
            raise ValueError(
                "Annotation metadata cannot have 'ground_truth_status' as true if 'method_type' is 'automated'",
            )
        return value

    @field_validator("sources")
    @classmethod
    def valid_sources(cls, value: List[AnnotationSource]) -> List[AnnotationSource]:
        total_errors = []

        # For verifying that all source entries don't have one shape used multiple times in different source entries
        used_shapes = set()
        shapes_used_multiple_times_errors = set()

        for source_element in value:
            for shape in source_element.model_fields:
                if source_element.__getattribute__(shape) is not None:
                    # If the shape is already used in another source entry, add the shape to the error set
                    if shape in used_shapes:
                        shapes_used_multiple_times_errors.add(shape)
                    else:
                        used_shapes.add(shape)

        # For verifying that all source entries each only have one shape entry
        multiple_shapes_in_all_source_entries_errors = []

        for i, source_element in enumerate(value):
            shapes_in_source_entry = []
            for shape in source_element.model_fields:
                # If the shape is not None, add it to the list of shapes in the source entry
                if source_element.__getattribute__(shape) is not None:
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


class ExtendedValidationAnnotation(Annotation):
    @field_validator("confidence")
    @classmethod
    def valid_confidence(cls, value: Optional[AnnotationConfidence]) -> Optional[AnnotationConfidence]:
        if value is None:
            return None
        provided_values = []
        precision = value.__getattribute__("precision")
        recall = value.__getattribute__("recall")
        ground_truth_used = value.__getattribute__("ground_truth_used")
        valid_ground_truth_used = isinstance(ground_truth_used, str) and len(ground_truth_used) > 0
        if precision is not None:
            provided_values.append("'precision'")
        if recall is not None:
            provided_values.append("'recall'")
        if len(provided_values) > 0 and not valid_ground_truth_used:
            raise ValueError(
                f"Annotation confidence must have 'ground_truth_used' if {', '.join(provided_values)} {'are' if len(provided_values) > 1 else 'is'} provided",
            )

        return value
