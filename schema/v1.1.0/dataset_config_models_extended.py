# TODO: Async-ify / parallelize network requests more
from __future__ import annotations

import asyncio
import logging
import re
import urllib
from functools import cache
from typing import Dict, List, Optional, Set, Tuple, Union

import aiohttp
import requests
from dataset_config_models import (
    Annotation,
    AnnotationConfidence,
    AnnotationEntity,
    AnnotationObject,
    AnnotationSource,
    Author,
    CellComponent,
    CellStrain,
    CellType,
    Container,
    CrossReferences,
    Dataset,
    DatasetEntity,
    DatasetKeyPhotoEntity,
    DatasetKeyPhotoLiteral,
    DatasetKeyPhotoSource,
    DateStamp,
    OrganismDetails,
    PicturePath,
    SampleTypeEnum,
    TissueDetails,
)
from pydantic import field_validator, model_validator
from typing_extensions import Self

logger = logging.getLogger("dataset-validate")

CELLULAR_COMPONENT_GO_ID = "GO:0005575"
VALID_IMAGE_FORMTS = ("image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp", "image/svg+xml")

# stores publication IDs (DOI, EMPIAR, EMDB) and their information
running_publication_list: Dict[str, bool] = {}
# stores image URLs and whether or not they are valid
running_image_list: Dict[str, bool] = {}

# Flag to determine if network validation should be run (set by provided Container arg)
running_network_validation = False


# ==============================================================================
# Author Validation
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


@cache
async def lookup_orcid(session: aiohttp.ClientSession, orcid_id: str) -> Tuple[str, bool]:
    """
    Returns a tuple of the ORCID ID and whether or not it is valid
    """
    url = f"https://pub.orcid.org/v3.0/{orcid_id}"
    async with session.head(url) as response:
        return orcid_id, response.status == 200


async def validate_orcids(orcid_list: List[str]) -> List[str]:
    """
    Returns a list of invalid ORCIDs, from the provided list
    """
    invalid_orcids: List[str] = []

    async with aiohttp.ClientSession() as session:
        tasks = [lookup_orcid(session, orcid) for orcid in orcid_list]
        results = await asyncio.gather(*tasks)
        invalid_orcids += [orcid for orcid, valid in results if not valid]
        return invalid_orcids


def validate_authors(authors: List[Author]) -> List[ValueError]:
    """
    Returns a list of errors found in the authors list
    """
    all_errors = validate_authors_status(authors)

    if running_network_validation:
        orcids = list({author.ORCID for author in authors if author.ORCID is not None})
        logger.debug("Checking ORCIDs: %s", orcids)
        invalid_orcids = asyncio.run(validate_orcids(orcids))
        if len(invalid_orcids) > 0:
            all_errors.append(ValueError(f"Invalid ORCIDs found in annotation authors: {invalid_orcids}"))

    return all_errors


# ==============================================================================
# Date Validation
# ==============================================================================
class ExtendedValidationDateStamp(DateStamp):
    @model_validator(mode="after")
    def valid_dates(self) -> Self:
        if self.deposition_date > self.release_date:
            raise ValueError(
                f"Deposition date ({self.deposition_date}) cannot be after release date ({self.release_date})",
            )
        return self


# ==============================================================================
# ID Object Validation
# ==============================================================================
@cache
def validate_id(id: str) -> Tuple[dict, bool]:
    """
    Returns a tuple of the ID data and whether or not it is valid.
    """
    # Encode the IRI
    iri = f"http://purl.obolibrary.org/obo/{id.replace(':', '_')}"
    encoded_iri = urllib.parse.quote(iri, safe="")

    # OLS API URL
    url = f"https://www.ebi.ac.uk/ols/api/terms?iri={encoded_iri}"

    logger.debug("Getting ID %s at %s", id, url)

    response = requests.get(url)
    data = response.json() if response.status_code == 200 else {}

    return data, data.get("page", {}).get("totalElements", 0) > 0


@cache
def is_id_ancestor(id_ancestor: str, id: str) -> bool:
    """
    Returns whether or not id_ancestor is an ancestor of id
    """
    # Encode the IRI
    iri = f"http://purl.obolibrary.org/obo/{id.replace(':', '_')}"
    encoded_iri = urllib.parse.quote(iri, safe="")

    # Encode the IRI again, as per the OLS API
    encoded_iri = urllib.parse.quote(encoded_iri, safe="")

    # OLS API URL
    ontology = id_ancestor.split(":")[0]
    url = f"https://www.ebi.ac.uk/ols4/api/ontologies/{ontology}/terms/{encoded_iri}/ancestors"

    logger.debug("Getting ancestors for ID %s at %s", id, url)

    response = requests.get(url)
    return response.status_code == 200 and id_ancestor in [
        ancestor["obo_id"] for ancestor in response.json()["_embedded"]["terms"]
    ]


def validate_id_name_object(
    id: str,
    name: str,
    field_name: str,
    validate_name: Optional[bool] = True,
    ancestor: Optional[str] = None,
) -> None:
    """
    Validates the ID and name, ensuring that:
    - The ID is valid (exists in the OLS API)
    - The name matches the ID
    - The name is an ancestor of the ancestor ID (if provided)
    """
    logger.debug("Validating %s %s with ID %s", field_name, name, id)

    id_data, valid_id = validate_id(id)

    if not valid_id:
        raise ValueError(f"Invalid ID found in {field_name}: {id}")

    if not validate_name:
        return

    logger.debug("Valid ID, now checking if %s name '%s' matches ID: %s", field_name, name, id)
    # check if the name matches the ID's label or any of its synonyms
    valid_name = False
    for entry in id_data["_embedded"]["terms"]:
        if name == entry["label"].lower():
            valid_name = True
            break
        if name in [synonym.lower() for synonym in entry["synonyms"]]:
            valid_name = True
            break

    if not valid_name:
        raise ValueError(f"{field_name} name '{name}' does not match id: {id}")

    if ancestor is not None:
        logger.debug("Valid name, now checking if %s is an ancestor of %s", field_name, ancestor)
        if not is_id_ancestor(ancestor, id):
            raise ValueError(f"{field_name} '{name}' is not a descendant of {ancestor}")


def validate_ontology_object(
    self: Union[AnnotationObject, CellComponent, CellStrain, CellType, TissueDetails],
    field_name: str,
    ancestor: Optional[str] = None,
) -> CellType:
    """
    Validates a typical object with an ontology ID and name
    """
    if not running_network_validation:
        return self

    if self.id is None:
        return self

    validate_id_name_object(self.id.strip().upper(), self.name.strip().lower(), field_name, True, ancestor)

    return self


def validate_organism_object(self: OrganismDetails) -> OrganismDetails:
    """
    Validates an organism object, with slightly different validation (taxonomy_id, but needs to be prefixed with NCBITaxon)
    """
    if not running_network_validation:
        return self

    if self.taxonomy_id is None:
        return self

    validate_id_name_object(f"NCBITaxon:{self.taxonomy_id}", self.name.strip().lower(), "organism", False)

    return self


# ==============================================================================
# Publication Validation
# ==============================================================================
async def lookup_doi(session: aiohttp.ClientSession, doi: str) -> Tuple[str, bool]:
    url = f"https://api.crossref.org/works/{doi}/agency"
    logger.debug("Checking DOI %s at %s", doi, url)
    async with session.head(url) as response:
        return doi, response.status == 200


async def lookup_empiar(session: aiohttp.ClientSession, empiar_id: str) -> Tuple[str, bool]:
    url = f"https://www.ebi.ac.uk/empiar/api/entry/{empiar_id}/"
    logger.debug("Checking EMPIAR %s at %s", empiar_id, url)
    async with session.head(url) as response:
        return empiar_id, response.status == 200


async def lookup_emdb(session: aiohttp.ClientSession, emdb_id: str) -> Tuple[str, bool]:
    url = f"https://www.ebi.ac.uk/emdb/api/entry/{emdb_id}"
    logger.debug("Checking EMDB %s at %s", emdb_id, url)
    async with session.head(url) as response:
        return emdb_id, response.status == 200


# Maps publication types to regexes and lookup functions
PUBLICATION_REGEXES_AND_FUNCTIONS = {
    "doi": (r"^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+$", lookup_doi),
    "empiar": (r"^EMPIAR-[0-9]{5}$", lookup_empiar),
    "emdb": (r"^EMD-[0-9]{4,5}$", lookup_emdb),
}


async def validate_publication_lists(publication_list: List[str]) -> List[str]:
    """
    Returns a list of invalid publications from the provided list, updating the running_publication_list.
    """
    # list of invalid publications
    invalid_publications: List[str] = []
    # type of publication to list of new publications to lookup
    new_publications: Dict[str, Set[str]] = {}

    # check if the publication is already in the running_publication_list,
    # otherwise find the matching publication type and add it to the new_publications
    for publication in publication_list:
        if publication in running_publication_list:
            if not running_publication_list[publication]:
                invalid_publications.append(publication)
        else:
            for publication_type, (regex, _) in PUBLICATION_REGEXES_AND_FUNCTIONS.items():
                # Note that we don't actually need to check if the provided list has types it shouldn't have,
                # because the provided list is based off of a string that has been regex validated
                if re.match(regex, publication):
                    # edge case for DOI, remove the doi: prefix
                    if publication_type == "doi":
                        publication = publication.replace("doi:", "")
                    if publication_type not in new_publications:
                        new_publications[publication_type] = set()
                    new_publications[publication_type].add(publication)
                    break

    if len(new_publications) == 0:
        return invalid_publications

    # Loop through the different publication types, create new requests for each publication, and then check if they are valid
    async with aiohttp.ClientSession() as session:
        lookup_requests = []
        for publication_type, (_, validate_function) in PUBLICATION_REGEXES_AND_FUNCTIONS.items():
            if publication_type in new_publications:
                # validate_fucntion will return a tuple of the publication and whether or not it is valid
                lookup_requests += [
                    validate_function(session, entry) for entry in list(new_publications[publication_type])
                ]

        results = await asyncio.gather(*lookup_requests)
        invalid_publications += [publication for publication, valid in results if not valid]
        for publication, valid in results:
            running_publication_list[publication] = valid

    return invalid_publications


def validate_publications(publications: str) -> str:
    if not running_network_validation:
        return publications

    if publications is None or publications == "":
        return publications

    # Convert the string to a list of publications
    publication_list = publications.replace(" ", "").split(",")
    if publication_list[-1] == "":
        publication_list.pop()

    invalid_publications = asyncio.run(validate_publication_lists(publication_list))
    if len(invalid_publications) > 0:
        raise ValueError(f"Invalid publications found in annotation publications: {invalid_publications}")
    return publications


# ==============================================================================
# Annotation Object Validation
# ==============================================================================
class ExtendedValidationAnnotationObject(AnnotationObject):
    @model_validator(mode="after")
    def validate_annotation_object(self) -> Self:
        return validate_ontology_object(self, "annotation object", CELLULAR_COMPONENT_GO_ID)


# ==============================================================================
# Annotation Confidence Validation
# ==============================================================================
class ExtendedValidationAnnotationConfidence(AnnotationConfidence):
    @model_validator(mode="after")
    def valid_confidence(self) -> Self:
        if not isinstance(self.ground_truth_used, str) or len(self.ground_truth_used) == 0:
            return self

        if self.precision is not None or self.recall is not None:
            raise ValueError("Annotation confidence cannot have 'precision' or 'recall' without 'ground_truth_used'")

        return self


# ==============================================================================
# Annotation Validation
# ==============================================================================
class ExtendedValidationAnnotation(Annotation):
    annotation_object: ExtendedValidationAnnotationObject = Annotation.model_fields["annotation_object"]
    confidence: Optional[ExtendedValidationAnnotationConfidence] = Annotation.model_fields["confidence"]
    dates: ExtendedValidationDateStamp = Annotation.model_fields["dates"]

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
        return validate_publications(annotation_publications)

    @field_validator("authors")
    @classmethod
    def valid_annotation_authors(cls: Self, authors: List[Author]) -> List[Author]:
        all_errors = validate_authors(authors)

        if len(all_errors) > 0:
            raise ValueError(all_errors)

        return authors


# ==============================================================================
# Annotation Entity Validation
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

        # For verifying that all source entries have exactly one of glob_string and glob_strings
        multiple_glob_strings_errors = []

        for i, source_element in enumerate(source_list):
            for shape in source_element.model_fields:
                source_entry = getattr(source_element, shape)
                if source_entry is not None:
                    glob_strings_entries = 0
                    if getattr(source_entry, "glob_string", None) is not None:
                        glob_strings_entries += 1
                    if getattr(source_entry, "glob_strings", None) is not None:
                        glob_strings_entries += 1
                    if glob_strings_entries != 1:
                        multiple_glob_strings_errors.append((i, shape))

        if len(shapes_used_multiple_times_errors) > 0:
            total_errors.append(
                ValueError(f"Annotation cannot have multiple same-shape sources: {shapes_used_multiple_times_errors}"),
            )
        for i, shapes in multiple_shapes_in_all_source_entries_errors:
            total_errors.append(ValueError(f"Source entry {i} cannot have multiple shapes: {shapes}"))
        for i, shape in multiple_glob_strings_errors:
            total_errors.append(
                ValueError(f"Source entry {i} shape {shape} must have exactly one of glob_string or glob_strings"),
            )

        if len(total_errors) > 0:
            raise ValueError(total_errors)

        return source_list


# ==============================================================================
# Dataset Key Photo Validation
# ==============================================================================
class ExtendedPicturePath(PicturePath):
    @field_validator("snapshot")
    @classmethod
    def valid_snapshot(cls: Self, snapshot: str) -> str:
        if not running_network_validation:
            return snapshot

        if snapshot is None:
            return snapshot

        # Check if the snapshot is a valid link
        if snapshot.startswith("https"):
            if snapshot not in running_image_list:
                r = requests.head(snapshot)
                running_image_list[snapshot] = r.headers["content-type"] in VALID_IMAGE_FORMTS
            if not running_image_list[snapshot]:
                raise ValueError(f"Invalid dataset key photo snapshot: {snapshot}")

        return snapshot

    @field_validator("thumbnail")
    @classmethod
    def valid_thumbnail(cls: Self, thumbnail: str) -> str:
        if not running_network_validation:
            return thumbnail

        if thumbnail is None:
            return thumbnail

        # Check if the thumbnail is a valid link
        if thumbnail.startswith("https"):
            if thumbnail not in running_image_list:
                r = requests.head(thumbnail)
                running_image_list[thumbnail] = r.headers["content-type"] in VALID_IMAGE_FORMTS
            if not running_image_list[thumbnail]:
                raise ValueError(f"Invalid dataset key photo thumbnail: {thumbnail}")

        return thumbnail


class ExtendedValidationDatasetKeyPhotoLiteral(DatasetKeyPhotoLiteral):
    value: ExtendedPicturePath = DatasetKeyPhotoLiteral.model_fields["value"]


class ExtendedValidationDatasetKeyPhotoSource(DatasetKeyPhotoSource):
    literal: Optional[ExtendedValidationDatasetKeyPhotoLiteral] = DatasetKeyPhotoSource.model_fields["literal"]


class ExtendedValidationDatasetKeyPhotoEntity(DatasetKeyPhotoEntity):
    sources: List[ExtendedValidationDatasetKeyPhotoSource] = DatasetKeyPhotoEntity.model_fields["sources"]


# ==============================================================================
# Dataset Validation
# ==============================================================================
class ExtendedValidationCellComponent(CellComponent):
    @model_validator(mode="after")
    def validate_cell_component(self) -> Self:
        return validate_ontology_object(self, "cell component", CELLULAR_COMPONENT_GO_ID)


class ExtendedValidationCellStrain(CellStrain):
    @model_validator(mode="after")
    def validate_cell_strain(self) -> Self:
        return validate_ontology_object(self, "cell strain")


class ExtendedValidationCellType(CellType):
    @model_validator(mode="after")
    def validate_cell_type(self) -> Self:
        return validate_ontology_object(self, "cell type")


class ExtendedValidationTissue(TissueDetails):
    @model_validator(mode="after")
    def validate_tissue(self) -> Self:
        return validate_ontology_object(self, "tissue")


class ExtendedValidationOrganism(OrganismDetails):
    @model_validator(mode="after")
    def validate_organism(self) -> Self:
        return validate_organism_object(self)


class ExtendedValidationCrossReferences(CrossReferences):
    @field_validator("dataset_publications")
    @classmethod
    def validate_dataset_publications(cls: Self, dataset_publications: str) -> str:
        return validate_publications(dataset_publications)

    @field_validator("related_database_entries")
    @classmethod
    def validate_related_database_entries(cls: Self, related_database_entries: str) -> str:
        return validate_publications(related_database_entries)


class ExtendedValidationDataset(Dataset):
    dates: ExtendedValidationDateStamp = Dataset.model_fields["dates"]
    cell_component: Optional[ExtendedValidationCellComponent] = Dataset.model_fields["cell_component"]
    cell_strain: Optional[ExtendedValidationCellStrain] = Dataset.model_fields["cell_strain"]
    cell_type: Optional[ExtendedValidationCellType] = Dataset.model_fields["cell_type"]
    tissue: Optional[ExtendedValidationTissue] = Dataset.model_fields["tissue"]
    organism: Optional[ExtendedValidationOrganism] = Dataset.model_fields["organism"]
    cross_references: Optional[ExtendedValidationCrossReferences] = Dataset.model_fields["cross_references"]

    @model_validator(mode="after")
    def valid_metadata(self) -> Self:
        if self.sample_type == SampleTypeEnum.cell and self.cell_type is None:
            raise ValueError("Dataset must have 'cell_type' if 'sample_type' is 'cell'")
        elif self.sample_type == SampleTypeEnum.tissue and self.tissue is None:
            raise ValueError("Dataset must have 'tissue' if 'sample_type' is 'tissue'")
        elif self.sample_type == SampleTypeEnum.organism and self.organism is None:
            raise ValueError("Dataset must have 'organism' if 'sample_type' is 'organism'")
        elif self.sample_type == SampleTypeEnum.organelle and (self.cell_component is None or self.organism is None):
            raise ValueError("Dataset must have 'cell_component' and 'organism' if 'sample_type' is 'organelle'")
        elif self.sample_type == SampleTypeEnum.virus and self.organism is None:
            raise ValueError("Dataset must have 'organism' if 'sample_type' is 'virus'")

    @field_validator("authors")
    @classmethod
    def valid_dataset_authors(cls: Self, authors: List[Author]) -> List[Author]:
        all_errors = validate_authors(authors)

        if len(all_errors) > 0:
            raise ValueError(all_errors)

        return authors


class ExtendedValidationDatasetEntity(DatasetEntity):
    metadata: ExtendedValidationDataset = DatasetEntity.model_fields["metadata"]


class ExtendedValidationContainer(Container):
    # Set global network_validation flag
    def __init__(self, **data):
        global running_network_validation
        running_network_validation = data.pop("network_validation", False)
        super().__init__(**data)

    annotations: Optional[List[ExtendedValidationAnnotationEntity]] = Container.model_fields["annotations"]
    dataset_keyphotos: Optional[List[ExtendedValidationDatasetKeyPhotoEntity]] = Container.model_fields[
        "dataset_keyphotos"
    ]
    datasets: List[ExtendedValidationDatasetEntity] = Container.model_fields["datasets"]


ExtendedValidationAnnotationConfidence.model_rebuild()
ExtendedValidationAnnotation.model_rebuild()
ExtendedValidationAnnotationEntity.model_rebuild()
ExtendedValidationContainer.model_rebuild()
