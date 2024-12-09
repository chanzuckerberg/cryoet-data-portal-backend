# NOTE: This file is manually generated!
# TODO: Async-ify / parallelize network requests more
from __future__ import annotations

import asyncio
import logging
import re
import urllib
from typing import List, Optional, Set, Tuple, Union

import aiohttp
import numpy
from async_lru import alru_cache
from codegen.ingestion_config_models import (
    Alignment,
    AlignmentEntity,
    AlignmentSource,
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
    CollectionMetadataEntity,
    CollectionMetadataSource,
    Container,
    CrossReferences,
    Dataset,
    DatasetEntity,
    DatasetKeyPhotoEntity,
    DatasetKeyPhotoSource,
    DatasetSource,
    DateStamp,
    Deposition,
    DepositionEntity,
    DepositionKeyPhotoEntity,
    DepositionKeyPhotoSource,
    DepositionSource,
    FrameEntity,
    FrameSource,
    GainEntity,
    GainSource,
    KeyImageEntity,
    KeyImageSource,
    KeyPhotoLiteral,
    OrganismDetails,
    PicturePath,
    RawTiltEntity,
    RawTiltSource,
    RunEntity,
    RunSource,
    SampleTypeEnum,
    StandardSource,
    TiltRange,
    TiltSeries,
    TiltSeriesEntity,
    TiltSeriesSource,
    TissueDetails,
    Tomogram,
    TomogramEntity,
    TomogramSource,
    VoxelSpacingEntity,
    VoxelSpacingSource,
)
from pydantic import BaseModel, field_validator, model_validator
from typing_extensions import Self

logger = logging.getLogger(__name__)

validation_exclusions = {}
CELLULAR_COMPONENT_GO_ID = "GO:0005575"
GO_ID_REGEX = r"^GO:[0-9]{7}$"
UNIPROT_ID_REGEX = r"^UniProtKB:[A-Z0-9]+$"
STRING_FORMATTED_STRING_REGEX = r"^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$"
VALID_IMAGE_FORMATS = ("image/png", "image/jpeg", "image/jpg", "image/gif")
# Note that model namees should all be uppercase or pascal case
CAMERA_MANUFACTURER_TO_MODEL = {
    ("FEI", "TFS"): ["FALCON IV", "Falcon4i"],
    ("Gatan"): ["K2", "K2 SUMMIT", "K3", "K3 BIOQUANTUM", "UltraCam", "UltraScan"],
    ("SIMULATED"): ["SIMULATED"],
}
SOURCE_FILTER_FIELDS = {"parent_filters", "exclude"}

# Flag to determine if network validation should be run (set by provided Container arg)
running_network_validation = False


# ==============================================================================
# Helper Functions
# ==============================================================================
def skip_validation(obj: BaseModel, field_name: str, case_sensitive: bool = True) -> bool:
    # Check if the original class name is in the validation exclusions
    global validation_exclusions

    for base in obj.__class__.__bases__:
        if base.__name__ not in validation_exclusions:
            continue

        if field_name not in validation_exclusions[base.__name__]:
            continue

        field_exclusions = [
            field if case_sensitive else field.lower() for field in validation_exclusions[base.__name__][field_name]
        ]
        field_value = getattr(obj, field_name) if case_sensitive else getattr(obj, field_name).lower()
        if field_value in field_exclusions:
            logger.debug(
                "Skipping %s %s validation for %s, found in validation exclusions",
                base.__name__,
                field_name,
                field_value,
            )
            return True
    return False


# ==============================================================================
# Author Validation
# ==============================================================================
def validate_authors_status(authors: List[Author]) -> List[ValueError]:
    errors = []
    contains_primary_author = False
    contains_corresponding_author = False
    for author in authors:
        contains_primary_author = contains_primary_author or author.primary_author_status
        contains_corresponding_author = contains_corresponding_author or author.corresponding_author_status

    if not contains_primary_author:
        errors.append(ValueError("Annotation must have at least one primary author"))
    if not contains_corresponding_author:
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


async def validate_orcids(orcid_list: Set[str]) -> Set[str]:
    """
    Returns a list of invalid ORCIDs, from the provided list
    """
    invalid_orcids: Set[str] = []

    tasks = [lookup_orcid(orcid) for orcid in orcid_list]
    results = await asyncio.gather(*tasks)
    invalid_orcids += {orcid for orcid, valid in results if not valid}
    return invalid_orcids


def validate_authors(authors: List[Author]) -> List[ValueError]:
    """
    Returns a list of errors found in the authors list
    """
    all_errors = validate_authors_status(authors)

    if not running_network_validation:
        return all_errors

    orcids = {author.ORCID for author in authors if author.ORCID is not None}

    if not orcids:
        return all_errors

    logger.debug("Checking ORCIDs: %s", orcids)
    invalid_orcids = asyncio.run(validate_orcids(orcids))
    if invalid_orcids:
        all_errors.append(ValueError(f"Invalid ORCIDs found in authors: {invalid_orcids}"))

    return all_errors


# ==============================================================================
# Cross References Validation
# ==============================================================================
class ExtendedValidationCrossReferences(CrossReferences):
    @field_validator("publications")
    @classmethod
    def validate_publications(cls: Self, publications: str) -> str:
        return validate_publications(publications)

    @field_validator("related_database_entries")
    @classmethod
    def validate_related_database_entries(cls: Self, related_database_entries: str) -> str:
        return validate_publications(related_database_entries)


# ==============================================================================
# Date Validation
# ==============================================================================
class ExtendedValidationDateStamp(DateStamp):
    @model_validator(mode="after")
    def valid_dates(self) -> Self:
        if self.deposition_date <= self.release_date:
            return self

        raise ValueError(
            f"Deposition date ({self.deposition_date}) cannot be after release date ({self.release_date})",
        )


# ==============================================================================
# ID Object Validation
# ==============================================================================
@alru_cache
async def validate_id(id: str) -> Tuple[List[str], bool]:
    """
    Returns a tuple of the ID names (including original label) and whether or not it is valid.
    """
    # Encode the IRI
    iri = f"http://purl.obolibrary.org/obo/{id.replace(':', '_')}"
    encoded_iri = urllib.parse.quote(iri, safe="")

    # OLS API URL
    url = f"https://www.ebi.ac.uk/ols/api/terms?iri={encoded_iri}"

    logger.debug("Getting ID %s at %s", id, url)

    async with aiohttp.ClientSession() as session, session.get(url) as response:
        if response.status >= 400:
            return [], False
        data = await response.json()
        names = []
        for entry in data["_embedded"]["terms"]:
            names.append(entry["label"])
            names += entry["synonyms"]
        return names, True


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
        ancestor_ids = [ancestor["obo_id"] for ancestor in (await response.json())["_embedded"]["terms"]]
        return response.status == 200 and id_ancestor in ancestor_ids


@alru_cache
async def validate_wormbase_id(id: str) -> Tuple[List[str], bool]:
    """
    Returns a tuple of the ID names (including original label) and whether or not it is valid.
    """

    url = f"http://rest.wormbase.org/rest/field/strain/{id}/name"

    logger.debug("Getting ID %s at %s", id, url)

    names = []
    async with aiohttp.ClientSession() as session, session.get(url) as response:
        if response.status >= 400:
            return [], False
        data = await response.json()
        if label := data["name"]["data"]["label"]:
            names.append(label)

    names_url = f"http://rest.wormbase.org/rest/field/strain/{id}/other_names"

    async with aiohttp.ClientSession() as session, session.get(names_url) as response:
        if response.status >= 400:
            return [], True
        data = await response.json()
        if other_names := data.get("other_names", {}).get("data", []):
            names += other_names

    return names, True


@alru_cache
async def validate_uniprot_id(id: str) -> Tuple[List[str], bool]:
    """
    Returns a tuple of the ID names and whether or not it is valid.
    """

    # Strip the UniProtKB: prefix
    id = id.replace("UniProtKB:", "")
    url = f"https://rest.uniprot.org/uniprotkb/{id}"

    logger.debug("Getting ID %s at %s", id, url)

    async with aiohttp.ClientSession() as session, session.get(url) as response:
        if response.status >= 400:
            return [], False
        data = await response.json()
        name = data["proteinDescription"]["recommendedName"]["fullName"]["value"]
        return [name], True


def validate_id_name_object(
    self: Union[AnnotationObject, CellComponent, CellStrain, CellType, OrganismDetails, TissueDetails],
    id: str,
    name: str,
    id_field_name: str = "id",
    validate_name: bool = True,
    ancestor: str | None = None,
    validate_id_function: callable = validate_id,
    validate_ancestor_function: callable = is_id_ancestor,
) -> None:
    """
    Validates the ID and name, ensuring that:
    - The ID is valid (exists in the OLS API)
    - The name matches the ID
    - The name is an ancestor of the ancestor ID (if provided)
    """
    if (
        not running_network_validation
        or getattr(self, id_field_name) is None
        or skip_validation(self, id_field_name, case_sensitive=True)
    ):
        return

    logger.debug("Validating %s with ID %s", name, id)

    id = id.strip()
    name = name.strip()
    retrieved_names, valid_id = asyncio.run(validate_id_function(id))

    if not valid_id:
        raise ValueError(f"Invalid ID {id}")

    # return here since if name validation is not done, we don't need to check ancestors
    if not validate_name or skip_validation(self, "name", case_sensitive=True):
        return

    logger.debug("Valid ID, now checking if name '%s' matches ID: %s", name, id)

    # if retrieved_names is empty, we can assume the name is valid
    valid_name = retrieved_names == [] or any(name == retrieved_name for retrieved_name in retrieved_names)

    if not valid_name:
        raise ValueError(f"name '{name}' does not match id: {id}")

    if ancestor is None:
        return

    logger.debug("Valid name, now checking if %s is an ancestor of %s", name, ancestor)
    if not asyncio.run(validate_ancestor_function(ancestor, id)):
        raise ValueError(f"'{name}' is not a descendant of {ancestor}")


def validate_cell_strain_object(self: CellStrain) -> CellStrain:
    """
    Validates a cell strain object, with slightly different validation (also looking at wormbase cell strain IDs)
    """
    if not running_network_validation or self.id is None:
        return self

    if self.id.startswith("WBStrain"):
        validate_id_name_object(self, self.id, self.name, validate_id_function=validate_wormbase_id)
    else:
        validate_id_name_object(self, self.id, self.name)

    return self


# ==============================================================================
# Key Photo Validation
# ==============================================================================
@alru_cache
async def validate_image_format(image_url: str | None) -> bool:
    if not running_network_validation or image_url is None:
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


class ExtendedValidationPicturePath(PicturePath):
    @field_validator("snapshot")
    @classmethod
    def valid_snapshot(cls: Self, snapshot: str) -> str:
        if asyncio.run(validate_image_format(snapshot)):
            return snapshot

        raise ValueError(f"Invalid key photo snapshot: {snapshot}")

    @field_validator("thumbnail")
    @classmethod
    def valid_thumbnail(cls: Self, thumbnail: str) -> str:
        if asyncio.run(validate_image_format(thumbnail)):
            return thumbnail

        raise ValueError(f"Invalid key photo thumbnail: {thumbnail}")


class ExtendedValidationKeyPhotoLiteral(KeyPhotoLiteral):
    value: ExtendedValidationPicturePath = KeyPhotoLiteral.model_fields["value"]


class ExtendedValidationDatasetKeyPhotoSource(DatasetKeyPhotoSource):
    literal: Optional[ExtendedValidationKeyPhotoLiteral] = DatasetKeyPhotoSource.model_fields["literal"]


class ExtendedValidationDepositionKeyPhotoSource(DepositionKeyPhotoSource):
    literal: Optional[ExtendedValidationKeyPhotoLiteral] = DepositionKeyPhotoSource.model_fields["literal"]


# ==============================================================================
# Publication Validation
# ==============================================================================
@alru_cache
async def lookup_doi(doi: str) -> Tuple[str, bool]:
    doi = doi.replace("doi:", "")
    url = f"https://api.crossref.org/works/{doi}/agency"
    logger.debug("Checking DOI %s at %s", doi, url)
    async with aiohttp.ClientSession() as session, session.head(url) as response:
        return doi, response.status == 200


@alru_cache
async def lookup_empiar(empiar_id: str) -> Tuple[str, bool]:
    url = f"https://www.ebi.ac.uk/empiar/api/entry/{empiar_id}/"
    logger.debug("Checking EMPIAR ID %s at %s", empiar_id, url)
    async with aiohttp.ClientSession() as session, session.head(url) as response:
        return empiar_id, response.status == 200


@alru_cache
async def lookup_emdb(emdb_id: str) -> Tuple[str, bool]:
    url = f"https://www.ebi.ac.uk/emdb/api/entry/{emdb_id}"
    logger.debug("Checking EMDB ID %s at %s", emdb_id, url)
    async with aiohttp.ClientSession() as session, session.head(url) as response:
        return emdb_id, response.status == 200


@alru_cache
async def lookup_pdb(pdb_id: str) -> Tuple[str, bool]:
    pdb_id = pdb_id.replace("PDB-", "")
    url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"
    logger.debug("Checking PDB ID %s at %s", pdb_id, url)
    async with aiohttp.ClientSession() as session, session.get(url) as response:
        return pdb_id, response.status == 200


PUBLICATION_REGEXES_AND_FUNCTIONS = {
    "doi": (r"^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+$", lookup_doi),
    "empiar": (r"^EMPIAR-[0-9]{5}$", lookup_empiar),
    "emdb": (r"^EMD-[0-9]{4,5}$", lookup_emdb),
    "pdb": (r"^PDB-[0-9a-zA-Z]{4,8}$", lookup_pdb),
}


async def validate_publication_lists(publication_list: List[str]) -> List[str]:
    tasks = []

    for publication in publication_list:
        for _, (regex, validate_function) in PUBLICATION_REGEXES_AND_FUNCTIONS.items():
            if not re.match(regex, publication):
                continue
            tasks.append(validate_function(publication))
            break

    results = await asyncio.gather(*tasks)
    return [publication for publication, valid in results if not valid]


def validate_publications(publications: Optional[str]) -> Optional[str]:
    if not running_network_validation or not publications:
        return publications

    # Convert the string to a list of publications
    publication_list = publications.replace(" ", "").rstrip(",").split(",")

    invalid_publications = asyncio.run(validate_publication_lists(publication_list))
    if invalid_publications:
        raise ValueError(f"Invalid publications found in annotation publications: {invalid_publications}")

    return publications


# ==============================================================================
# Sources Validation
# ==============================================================================
def validate_sources(source_list: List[StandardSource] | List[VoxelSpacingSource]) -> None:
    total_errors = []

    for index, source_element in enumerate(source_list):
        finders_in_source_entry = []
        for finder in source_element.model_fields:
            # If the finder is not None and an actual finder, add it to the list of finders in the source entry
            if getattr(source_element, finder) is not None and finder not in SOURCE_FILTER_FIELDS:
                finders_in_source_entry.append(finder)
        # If there are more than one finder in the source entry, add the source entry index and the finders to the error set
        if len(finders_in_source_entry) > 1:
            total_errors.append(
                ValueError(
                    f"Source entry {index} cannot have multiple finders (split into multiple entries): {finders_in_source_entry}",
                ),
            )
        if len(finders_in_source_entry) == 0:
            for source_child in SOURCE_FILTER_FIELDS:
                if getattr(source_element, source_child) is None:
                    continue
                total_errors.append(
                    ValueError(f"Source entry {index} cannot have a {source_child} entry without a finder"),
                )

    if total_errors:
        raise ValueError(total_errors)


# ==============================================================================
# Alignment Entity Validation
# ==============================================================================
class ExtendedValidationAlignmentEntity(AlignmentEntity):
    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[AlignmentSource]) -> List[AlignmentSource]:
        return validate_sources(source_list)

# ==============================================================================
# Alignment Validation
# ==============================================================================
class ExtendValidationAlignment(Alignment):
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


# ==============================================================================
# Annotation Object Validation
# ==============================================================================
class ExtendedValidationAnnotationObject(AnnotationObject):
    @model_validator(mode="after")
    def validate_annotation_object(self) -> Self:
        if re.match(GO_ID_REGEX, self.id):
            validate_id_name_object(self, self.id, self.name, ancestor=CELLULAR_COMPONENT_GO_ID)
        elif re.match(UNIPROT_ID_REGEX, self.id):
            validate_id_name_object(self, self.id, self.name, validate_id_function=validate_uniprot_id)
        return self


# ==============================================================================
# Annotation Confidence Validation
# ==============================================================================
class ExtendedValidationAnnotationConfidence(AnnotationConfidence):
    @model_validator(mode="after")
    def valid_confidence(self) -> Self:
        if isinstance(self.ground_truth_used, str) and len(self.ground_truth_used) != 0:
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

        if all_errors:
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
                if getattr(source_element, shape) is None:
                    continue

                # If the shape is already used in another source entry, add the shape to the error set
                if shape in used_shapes:
                    shapes_used_multiple_times_errors.add(shape)
                else:
                    used_shapes.add(shape)

        # For verifying that all source entries:
        # - each only have one shape entry
        # - that there is only one of glob_string and glob_strings
        # - cannot have only a filter entry without a shape
        for i, source_element in enumerate(source_list):
            shapes_in_source_entry = []
            for shape in source_element.model_fields:
                # If the shape is not None and an actual shape, add it to the list of shapes in the source entry
                shape_entry = getattr(source_element, shape)
                if shape_entry is None or shape in SOURCE_FILTER_FIELDS:
                    continue

                shapes_in_source_entry.append(shape)
                has_glob_string = getattr(shape_entry, "glob_string", None) is not None
                has_glob_strings = getattr(shape_entry, "glob_strings", None) is not None and shape_entry.glob_strings
                if has_glob_string and has_glob_strings:
                    total_errors.append(
                        ValueError(
                            f"Source entry {i} shape {shape} must have exactly one of glob_string or glob_strings",
                        ),
                    )

            # If there are more than one shape in the source entry, add the source entry index and the shapes to the error set
            if len(shapes_in_source_entry) > 1:
                total_errors.append(
                    ValueError(
                        f"Source entry {i} cannot have multiple shapes (split into multiple entries): {shapes_in_source_entry}",
                    ),
                )
            if len(shapes_in_source_entry) == 0:
                for source_child in SOURCE_FILTER_FIELDS:
                    if getattr(source_element, source_child) is None:
                        continue
                    total_errors.append(
                        ValueError(f"Source entry {i} cannot have a {source_child} entry without a shape"),
                    )

        if shapes_used_multiple_times_errors:
            total_errors.append(
                ValueError(f"Annotation cannot have multiple same-shape sources: {shapes_used_multiple_times_errors}"),
            )

        if total_errors:
            raise ValueError(total_errors)

        return source_list


# ==============================================================================
# Collection Metadata Validation
# ==============================================================================


class ExtendedValidationCollectionMetadataEntity(CollectionMetadataEntity):
    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[CollectionMetadataSource]) -> List[CollectionMetadataSource]:
        return validate_sources(source_list)


# ==============================================================================
# Dataset Key Photo Validation
# ==============================================================================


class ExtendedValidationDatasetKeyPhotoEntity(DatasetKeyPhotoEntity):
    sources: List[ExtendedValidationDatasetKeyPhotoSource] = DatasetKeyPhotoEntity.model_fields["sources"]

    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[DatasetKeyPhotoSource]) -> List[DatasetKeyPhotoSource]:
        return validate_sources(source_list)


# ==============================================================================
# Dataset Validation
# ==============================================================================
class ExtendedValidationCellComponent(CellComponent):
    @model_validator(mode="after")
    def validate_cell_component(self) -> Self:
        validate_id_name_object(self, self.id, self.name, ancestor=CELLULAR_COMPONENT_GO_ID)
        return self


class ExtendedValidationCellStrain(CellStrain):
    @model_validator(mode="after")
    def validate_cell_strain(self) -> Self:
        return validate_cell_strain_object(self)


class ExtendedValidationCellType(CellType):
    @model_validator(mode="after")
    def validate_cell_type(self) -> Self:
        validate_id_name_object(self, self.id, self.name)
        return self


class ExtendedValidationTissue(TissueDetails):
    @model_validator(mode="after")
    def validate_tissue(self) -> Self:
        validate_id_name_object(self, self.id, self.name)
        return self


class ExtendedValidationOrganism(OrganismDetails):
    @model_validator(mode="after")
    def validate_organism(self) -> Self:
        validate_id_name_object(
            self,
            f"NCBITaxon:{self.taxonomy_id}",
            self.name,
            id_field_name="taxonomy_id",
            validate_name=False,
        )
        return self


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

        if all_errors:
            raise ValueError(all_errors)

        return authors


class ExtendedValidationDatasetEntity(DatasetEntity):
    metadata: Optional[ExtendedValidationDataset] = DatasetEntity.model_fields["metadata"]

    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[DatasetSource]) -> List[DatasetSource]:
        return validate_sources(source_list)


# ==============================================================================
# Deposition Key Photo Validation
# ==============================================================================
class ExtendedValidationDepositionKeyPhotoEntity(DepositionKeyPhotoEntity):
    sources: List[ExtendedValidationDepositionKeyPhotoSource] = DepositionKeyPhotoEntity.model_fields["sources"]

    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[DepositionKeyPhotoSource]) -> List[DepositionKeyPhotoSource]:
        return validate_sources(source_list)


# ==============================================================================
# Deposition Validation
# ==============================================================================
class ExtendedValidationDeposition(Deposition):
    dates: ExtendedValidationDateStamp = Deposition.model_fields["dates"]
    cross_references: Optional[ExtendedValidationCrossReferences] = Deposition.model_fields["cross_references"]

    @field_validator("authors")
    @classmethod
    def valid_deposition_authors(cls: Self, authors: List[Author]) -> List[Author]:
        all_errors = validate_authors(authors)

        if all_errors:
            raise ValueError(all_errors)

        return authors


class ExtendedValidationDepositionEntity(DepositionEntity):
    metadata: Optional[ExtendedValidationDeposition] = DepositionEntity.model_fields["metadata"]

    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[DepositionSource]) -> List[DepositionSource]:
        return validate_sources(source_list)


# ==============================================================================
# Frame Validation
# ==============================================================================
class ExtendedValidationFrameEntity(FrameEntity):
    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[FrameSource]) -> List[FrameSource]:
        return validate_sources(source_list)


# ==============================================================================
# Gain Validation
# ==============================================================================
class ExtendedValidationGainEntity(GainEntity):
    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[GainSource]) -> List[GainSource]:
        return validate_sources(source_list)


# ==============================================================================
# Key Image Validation
# ==============================================================================
class ExtendedValidationKeyImageEntity(KeyImageEntity):
    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[KeyImageSource]) -> List[KeyImageSource]:
        return validate_sources(source_list)


# ==============================================================================
# Raw Tilt Validation
# ==============================================================================
class ExtendedValidationRawTiltEntity(RawTiltEntity):
    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[RawTiltSource]) -> List[RawTiltSource]:
        return validate_sources(source_list)


# ==============================================================================
# Run Validation
# ==============================================================================
class ExtendedValidationRunEntity(RunEntity):
    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[RunSource]) -> List[RunSource]:
        return validate_sources(source_list)


# ==============================================================================
# Tilt Series Validation
# ==============================================================================
class ExtendedValidationCameraDetails(CameraDetails):
    @model_validator(mode="after")
    def valid_camera_details(self) -> Self:
        if re.match(STRING_FORMATTED_STRING_REGEX, self.model):
            return self

        for manufacturers, models in CAMERA_MANUFACTURER_TO_MODEL.items():
            if self.manufacturer not in manufacturers:
                continue

            if self.model not in models:
                # A warning for now
                logger.warning(
                    "Camera model '%s' is not valid for manufacturer '%s'",
                    self.model,
                    self.manufacturer,
                )

            return self

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
    metadata: Optional[ExtendedValidationTiltSeries] = TiltSeriesEntity.model_fields["metadata"]

    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[TiltSeriesSource]) -> List[TiltSeriesSource]:
        return validate_sources(source_list)


# ==============================================================================
# Tomogram Validation
# ==============================================================================
class ExtendedValidationTomogram(Tomogram):
    @field_validator("authors")
    @classmethod
    def valid_tomogram_authors(cls: Self, authors: List[Author]) -> List[Author]:
        all_errors = validate_authors(authors)

        if all_errors:
            raise ValueError(all_errors)

        return authors


class ExtendedValidationTomogramEntity(TomogramEntity):
    metadata: Optional[ExtendedValidationTomogram] = TomogramEntity.model_fields["metadata"]

    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[TomogramSource]) -> List[TomogramSource]:
        return validate_sources(source_list)


# ==============================================================================
# Voxel Spacing Validation
# ==============================================================================
class ExtendedValidationVoxelSpacingEntity(VoxelSpacingEntity):
    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[VoxelSpacingSource]) -> List[VoxelSpacingSource]:
        return validate_sources(source_list)


class ExtendedValidationContainer(Container):
    # Set global network_validation flag
    def __init__(self, **data):
        global running_network_validation
        global validation_exclusions
        global logger
        running_network_validation = data.pop("network_validation", False)
        validation_exclusions = data.pop("validation_exclusions", {})
        if logger_name := data.pop("logger_name", None):
            logger = logging.getLogger(logger_name)

        super().__init__(**data)

    annotations: Optional[List[ExtendedValidationAnnotationEntity]] = Container.model_fields["annotations"]
    collection_metadata: Optional[List[ExtendedValidationCollectionMetadataEntity]] = Container.model_fields[
        "collection_metadata"
    ]
    dataset_keyphotos: Optional[List[ExtendedValidationDatasetKeyPhotoEntity]] = Container.model_fields[
        "dataset_keyphotos"
    ]
    datasets: List[ExtendedValidationDatasetEntity] = Container.model_fields["datasets"]
    deposition_keyphotos: Optional[List[ExtendedValidationDepositionKeyPhotoEntity]] = Container.model_fields[
        "deposition_keyphotos"
    ]
    depositions: List[ExtendedValidationDepositionEntity] = Container.model_fields["depositions"]
    frames: Optional[List[ExtendedValidationFrameEntity]] = Container.model_fields["frames"]
    gains: Optional[List[ExtendedValidationGainEntity]] = Container.model_fields["gains"]
    key_images: Optional[List[ExtendedValidationKeyImageEntity]] = Container.model_fields["key_images"]
    rawtilts: Optional[List[ExtendedValidationRawTiltEntity]] = Container.model_fields["rawtilts"]
    runs: List[ExtendedValidationRunEntity] = Container.model_fields["runs"]
    tiltseries: Optional[List[ExtendedValidationTiltSeriesEntity]] = Container.model_fields["tiltseries"]
    tomograms: Optional[List[ExtendedValidationTomogramEntity]] = Container.model_fields["tomograms"]
    voxel_spacings: List[ExtendedValidationVoxelSpacingEntity] = Container.model_fields["voxel_spacings"]
