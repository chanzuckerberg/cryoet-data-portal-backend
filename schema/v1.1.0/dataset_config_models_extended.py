from __future__ import annotations

import asyncio
import re
from typing import Dict, List, Optional, Set, Tuple

import aiohttp
from async_lru import alru_cache
from dataset_config_models import (
    Annotation,
    AnnotationConfidence,
    AnnotationEntity,
    AnnotationObject,
    AnnotationSource,
    Author,
    Container,
)
from pydantic import field_validator, model_validator
from typing_extensions import Self

CELLULAR_COMPONENT_GO_ID = "GO:0005575"

running_network_validation = False

# ==============================================================================
# Annotation Object Validation
# ==============================================================================


@alru_cache
async def validate_go_id(go_id: str) -> Tuple[bool, dict]:
    url = f"https://api.geneontology.org/api/ontology/term/{go_id}"
    headers = {"Accept": "application/json"}
    async with aiohttp.ClientSession() as session, session.get(url, headers=headers) as response:
        go_id_data = await response.json()
        return "label" in go_id_data or "description" in go_id_data, go_id_data


@alru_cache
async def is_go_id_ancestor(go_id_ancestor: str, go_id: str) -> bool:
    url = f"https://api.geneontology.org/api/ontology/term/{go_id}/subgraph?start=0&rows=100"
    headers = {"Accept": "application/json"}
    async with aiohttp.ClientSession() as session, session.get(url, headers=headers) as response:
        response_json = await response.json()
        return go_id_ancestor in [ancestor["id"] for ancestor in response_json["ancestors"]]


class ExtendedValidationAnnotationObject(AnnotationObject):
    @model_validator(mode="after")
    def validate_annotation_object(self) -> Self:
        if not running_network_validation:
            return self

        # All of this checking is based on the id, so return if id is None
        if self.id is None:
            return self

        # First ensure that the id is valid
        valid_go_id, go_id_data = asyncio.run(validate_go_id(self.id))
        if not valid_go_id:
            raise ValueError(f"Invalid GO ID found in annotation object: {self.id}")

        # Then check that the name matches
        go_id_synonyms = go_id_data["synonyms"]

        go_id_synonyms = [s.replace("@", "") for s in go_id_synonyms]
        if self.name not in go_id_data["label"] and not any(
            self.name in go_id_synonym for go_id_synonym in go_id_synonyms
        ):
            raise ValueError(f"Annotation object name '{self.name}' does not match id: {self.id}")

        # Then check that the go_id is part of the cellular_component ontology
        if not asyncio.run(is_go_id_ancestor(CELLULAR_COMPONENT_GO_ID, self.id)):
            raise ValueError(f"Annotation object id {self.id} is not a cellular component")

        return self


# ==============================================================================
# Annotation Publication Validation
# ==============================================================================


@alru_cache
async def lookup_doi(doi: str) -> Tuple[str, bool]:
    url = f"https://api.crossref.org/works/{doi}/agency"
    async with aiohttp.ClientSession() as session, session.head(url) as response:
        return doi, response.status == 200


@alru_cache
async def lookup_empiar(empiar_id: str) -> Tuple[str, bool]:
    url = f"https://www.ebi.ac.uk/empiar/api/entry/{empiar_id}/"
    async with aiohttp.ClientSession() as session, session.head(url) as response:
        return empiar_id, response.status == 200


@alru_cache
async def lookup_emdb(emdb_id: str) -> Tuple[str, bool]:
    url = f"https://www.ebi.ac.uk/emdb/api/entry/{emdb_id}"
    async with aiohttp.ClientSession() as session, session.head(url) as response:
        return emdb_id, response.status == 200


PUBLICATION_REGEXES_AND_FUNCTIONS = {
    "doi": (r"^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+$", lookup_doi),
    "empiar": (r"^EMPIAR-[0-9]{5}$", lookup_empiar),
    "emdb": (r"^EMD-[0-9]{4,5}$", lookup_emdb),
}


async def validate_publication_lists(publication_list: List[str]) -> List[str]:
    # list of invalid publications
    invalid_publications: List[str] = []
    new_publications: Dict[str, Set[str]] = {
        publication_type: set() for publication_type in PUBLICATION_REGEXES_AND_FUNCTIONS
    }

    for publication in publication_list:
        for publication_type, (regex, _) in PUBLICATION_REGEXES_AND_FUNCTIONS.items():
            if re.match(regex, publication):
                # edge case for DOI, remove the doi: prefix
                if publication_type == "doi":
                    publication = publication.replace("doi:", "")
                new_publications[publication_type].add(publication)
                break

    tasks = []
    for publication_type, (_, validate_function) in PUBLICATION_REGEXES_AND_FUNCTIONS.items():
        tasks += [validate_function(entry) for entry in list(new_publications[publication_type])]

    results = await asyncio.gather(*tasks)
    invalid_publications += [publication for publication, valid in results if not valid]

    return invalid_publications


# ==============================================================================
# Annotation Author Validation
# ==============================================================================


def validate_authors_status(authors: List[Author]) -> List[ValueError]:
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


@alru_cache
async def lookup_orcid(orcid_id: str) -> Tuple[str, bool]:
    url = f"https://pub.orcid.org/v3.0/{orcid_id}"
    async with aiohttp.ClientSession() as session, session.head(url) as response:
        return orcid_id, response.status == 200


async def validate_orcids(orcid_list: List[str]) -> List[str]:
    invalid_orcids: List[str] = []

    tasks = [lookup_orcid(orcid) for orcid in orcid_list]
    results = await asyncio.gather(*tasks)
    invalid_orcids += [orcid for orcid, valid in results if not valid]
    return invalid_orcids


def get_invalid_orcids(authors: List[Author]) -> List[str]:
    orcids = list({author.ORCID for author in authors if author.ORCID is not None})
    return asyncio.run(validate_orcids(orcids))


# ==============================================================================
# Annotation Confidence Validation
# ==============================================================================


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


# ==============================================================================
# Annotation Validation
# ==============================================================================


class ExtendedValidationAnnotation(Annotation):
    annotation_object: ExtendedValidationAnnotationObject = Annotation.model_fields["annotation_object"]
    confidence: Optional[ExtendedValidationAnnotationConfidence] = Annotation.model_fields["confidence"]

    @model_validator(mode="after")
    def valid_metadata(self) -> Self:
        if self.method_type == "automated" and self.ground_truth_status:
            raise ValueError(
                "Annotation metadata cannot have 'ground_truth_status' as true if 'method_type' is 'automated'",
            )
        return self

    @field_validator("annotation_publications")
    @classmethod
    def validate_annotation_publications(cls, annotation_publications: str) -> str:
        if not running_network_validation:
            return annotation_publications

        if annotation_publications is None or annotation_publications == "":
            return annotation_publications

        annotation_publications_list = annotation_publications.replace(" ", "").split(",")
        if annotation_publications_list[-1] == "":
            annotation_publications_list.pop()

        invalid_publications = asyncio.run(validate_publication_lists(annotation_publications_list))
        if len(invalid_publications) > 0:
            raise ValueError(f"Invalid publications found in annotation publications: {invalid_publications}")
        return annotation_publications

    @field_validator("authors")
    @classmethod
    def valid_annotation_authors(cls: Self, authors: List[Author]) -> List[Author]:
        all_errors = validate_authors_status(authors)

        if running_network_validation:
            invalid_orcids = get_invalid_orcids(authors)
            if len(invalid_orcids) > 0:
                all_errors.append(ValueError(f"Invalid ORCIDs found in annotation authors: {invalid_orcids}"))

        if len(all_errors) > 0:
            raise ValueError(all_errors)

        return authors


# ==============================================================================
# Annotation Sources Validation
# ==============================================================================


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
    # Set global network_validation flag
    def __init__(self, **data):
        global running_network_validation
        running_network_validation = data.pop("network_validation", False)
        super().__init__(**data)

    annotations: Optional[List[ExtendedValidationAnnotationEntity]] = Container.model_fields["annotations"]


ExtendedValidationAnnotationConfidence.model_rebuild()
ExtendedValidationAnnotation.model_rebuild()
ExtendedValidationAnnotationEntity.model_rebuild()
ExtendedValidationContainer.model_rebuild()
