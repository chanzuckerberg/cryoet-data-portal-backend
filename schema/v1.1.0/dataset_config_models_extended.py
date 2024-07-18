# TODO: Async-ify / parallelize network requests more
from __future__ import annotations

import asyncio
import logging
import re
import urllib
from typing import Dict, List, Optional, Set, Tuple, Union

import aiohttp
import numpy
from async_lru import alru_cache
from dataset_config_models import (
    Annotation,
    AnnotationConfidence,
    AnnotationEntity,
    AnnotationObject,
    AnnotationSource,
    Author,
    CameraDetails,
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
    TiltRange,
    TiltSeries,
    TiltSeriesEntity,
    TissueDetails,
    Tomogram,
    TomogramEntity,
)
from pydantic import field_validator, model_validator
from typing_extensions import Self

logger = logging.getLogger("dataset-validate")

CELLULAR_COMPONENT_GO_ID = "GO:0005575"
STRING_FORMATTED_STRING_REGEX = r"^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$"
VALID_IMAGE_FORMATS = ("image/png", "image/jpeg", "image/jpg", "image/gif")
# Note that model namees should all be uppercase or pascal case
CAMERA_MANUFACTURER_TO_MODEL = {
    ("FEI", "TFS"): ["FALCON IV", "Falcon4i"],
    ("Gatan", "GATAN"): ["K2", "K2 SUMMIT", "K3", "K3 BIOQUANTUM", "UltraCam", "UltraScan"],
}


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


@alru_cache
async def lookup_orcid(orcid_id: str) -> Tuple[str, bool]:
    """
    Returns a tuple of the ORCID ID and whether or not it is valid
    """
    url = f"https://pub.orcid.org/v3.0/{orcid_id}"
    async with aiohttp.ClientSession() as session, session.head(url) as response:
        return orcid_id, response.status == 200


async def validate_orcids(orcid_list: List[str]) -> List[str]:
    """
    Returns a list of invalid ORCIDs, from the provided list
    """
    invalid_orcids: List[str] = []

    tasks = [lookup_orcid(orcid) for orcid in orcid_list]
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

        if len(orcids) == 0:
            return all_errors

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
@alru_cache
async def validate_id(id: str) -> Tuple[dict, bool]:
    """
    Returns a tuple of the ID data and whether or not it is valid.
    """
    # Encode the IRI
    iri = f"http://purl.obolibrary.org/obo/{id.replace(':', '_')}"
    encoded_iri = urllib.parse.quote(iri, safe="")

    # OLS API URL
    url = f"https://www.ebi.ac.uk/ols/api/terms?iri={encoded_iri}"

    logger.debug("Getting ID %s at %s", id, url)

    async with aiohttp.ClientSession() as session, session.get(url) as response:
        data = await response.json() if response.status == 200 else {}
        return data, data.get("page", {}).get("totalElements", 0) > 0


@alru_cache
async def is_id_ancestor(id_ancestor: str, id: str) -> bool:
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

    async with aiohttp.ClientSession() as session, session.get(url) as response:
        return response.status == 200 and id_ancestor in [
            ancestor["obo_id"] for ancestor in (await response.json())["_embedded"]["terms"]
        ]


def validate_id_name_object(
    id: str,
    name: str,
    field_name: str,
    validate_name: bool = True,
    ancestor: str = None,
) -> None:
    """
    Validates the ID and name, ensuring that:
    - The ID is valid (exists in the OLS API)
    - The name matches the ID
    - The name is an ancestor of the ancestor ID (if provided)
    """
    logger.debug("Validating %s %s with ID %s", field_name, name, id)

    id_data, valid_id = asyncio.run(validate_id(id))

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
        if not asyncio.run(is_id_ancestor(ancestor, id)):
            raise ValueError(f"{field_name} '{name}' is not a descendant of {ancestor}")


def validate_ontology_object(
    self: Union[AnnotationObject, CellComponent, CellStrain, CellType, TissueDetails],
    field_name: str,
    ancestor: str = None,
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


@alru_cache
async def lookup_pdb(pdb_id: str) -> Tuple[str, bool]:
    url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"
    async with aiohttp.ClientSession() as session, session.head(url) as response:
        return pdb_id, response.status == 200


PUBLICATION_REGEXES_AND_FUNCTIONS = {
    "doi": (r"^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+$", lookup_doi),
    "empiar": (r"^EMPIAR-[0-9]{5}$", lookup_empiar),
    "emdb": (r"^EMD-[0-9]{4,5}$", lookup_emdb),
    "pdb": (r"^pdb[0-9a-zA-Z]{4,8}$", lookup_pdb),
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
        if publication_type in new_publications:
            tasks += [validate_function(entry) for entry in list(new_publications[publication_type])]

    results = await asyncio.gather(*tasks)
    invalid_publications += [publication for publication, valid in results if not valid]

    return invalid_publications


def validate_publications(publications: Optional[str]) -> Optional[str]:
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
        if isinstance(self.ground_truth_used, str) and len(self.ground_truth_used) == 0:
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
    def validate_annotation_publications(cls, annotation_publications: Optional[str]) -> str:
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
                    if getattr(source_entry, "glob_strings", None) is not None and source_entry.glob_strings != []:
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
@alru_cache
async def validate_image_format(image_url: Optional[str]) -> bool:
    if not running_network_validation:
        return True

    if image_url is None:
        return True

    # don't check non-http(s) URLs
    if not image_url.startswith("http"):
        return True

    if not image_url.startswith("https"):
        logger.warning("URL %s is not HTTPS", image_url)

    async with aiohttp.ClientSession() as session, session.head(image_url) as response:
        if response.status >= 400:
            return False

        return response.headers["content-type"] in VALID_IMAGE_FORMATS


class ExtendedPicturePath(PicturePath):
    @field_validator("snapshot")
    @classmethod
    def valid_snapshot(cls: Self, snapshot: Optional[str]) -> str:
        if asyncio.run(validate_image_format(snapshot)):
            return snapshot

        raise ValueError(f"Invalid dataset key photo snapshot: {snapshot}")

    @field_validator("thumbnail")
    @classmethod
    def valid_thumbnail(cls: Self, thumbnail: Optional[str]) -> str:
        if asyncio.run(validate_image_format(thumbnail)):
            return thumbnail

        raise ValueError(f"Invalid dataset key photo thumbnail: {thumbnail}")


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
    @field_validator("publications")
    @classmethod
    def validate_publications(cls: Self, publications: Optional[str]) -> Optional[str]:
        return validate_publications(publications)

    @field_validator("related_database_entries")
    @classmethod
    def validate_related_database_entries(cls: Self, related_database_entries: Optional[str]) -> Optional[str]:
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


# ==============================================================================
# Tilt Series Validation
# ==============================================================================


class ExtendedValidationCameraDetails(CameraDetails):
    @model_validator(mode="after")
    def valid_camera_details(self) -> Self:
        if re.match(STRING_FORMATTED_STRING_REGEX, self.model):
            return self

        for manufacturer, models in CAMERA_MANUFACTURER_TO_MODEL.items():
            if self.manufacturer in manufacturer and self.model not in models:
                # A warning for now
                logger.warning(
                    "Camera model '%s' is not valid for manufacturer '%s'",
                    self.model,
                    self.manufacturer,
                )

        logger.warning("Camera model '%s' of manufacturer '%s' was not recognized", self.model, self.manufacturer)
        return self


class ExtendedValidationTiltRange(TiltRange):
    @model_validator(mode="after")
    def valid_tilt_range(self) -> Self:
        if self.min > self.max:
            raise ValueError(
                f"Minimum tilt ({self.min}) cannot be greater than maximum tilt ({self.max})",
            )
        return self


class ExtendedValidationTiltSeries(TiltSeries):
    camera: ExtendedValidationCameraDetails = TiltSeries.model_fields["camera"]
    tilt_range: ExtendedValidationTiltRange = TiltSeries.model_fields["tilt_range"]


class ExtendedValidationTiltSeriesEntity(TiltSeriesEntity):
    metadata: ExtendedValidationTiltSeries = TiltSeriesEntity.model_fields["metadata"]


# ==============================================================================
# Tomogram Validation
# ==============================================================================
class ExtendedValidationTomogram(Tomogram):
    @field_validator("affine_transformation_matrix")
    @classmethod
    def valid_affine_transformation_matrix(
        cls: Self,
        affine_transformation_matrix: Optional[List[List[float]]],
    ) -> Optional[List[List[float]]]:
        if affine_transformation_matrix is None:
            return None

        errors = []
        # Bottom row of the matrix should be [0, 0, 0, 1]
        if affine_transformation_matrix[3] != [0, 0, 0, 1]:
            errors.append(ValueError("Bottom row of the affine transformation matrix must be [0, 0, 0, 1]"))

        # Check that top left 3x3 matrix is an invertible matrix
        top_left_matrix = numpy.array(
            [
                affine_transformation_matrix[0][0:3],
                affine_transformation_matrix[1][0:3],
                affine_transformation_matrix[2][0:3],
            ],
        )
        if numpy.linalg.det(top_left_matrix) == 0:
            errors.append(ValueError("Top left 3x3 matrix of the affine transformation matrix must be invertible"))

        return affine_transformation_matrix

    @field_validator("authors")
    @classmethod
    def valid_tomogram_authors(cls: Self, authors: List[Author]) -> List[Author]:
        all_errors = validate_authors(authors)

        if len(all_errors) > 0:
            raise ValueError(all_errors)

        return authors


class ExtendedValidationTomogramEntity(TomogramEntity):
    metadata: ExtendedValidationTomogram = TomogramEntity.model_fields["metadata"]


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
    tiltseries: Optional[List[ExtendedValidationTiltSeriesEntity]] = Container.model_fields["tiltseries"]
    tomograms: Optional[List[ExtendedValidationTomogramEntity]] = Container.model_fields["tomograms"]


ExtendedValidationAnnotationConfidence.model_rebuild()
ExtendedValidationAnnotation.model_rebuild()
ExtendedValidationAnnotationEntity.model_rebuild()
ExtendedValidationContainer.model_rebuild()
