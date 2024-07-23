# NOTE: This file is manually generated!
# TODO: Async-ify / parallelize network requests more
from __future__ import annotations

import asyncio
import logging
import re
import sys
import urllib
from typing import List, Optional, Set, Tuple, Union

import aiohttp
import numpy
from async_lru import alru_cache
from dataset_config_models import (
    Annotation,
    AnnotationConfidence,
    AnnotationEntity,
    AnnotationObject,
    AnnotationSource,
    AnnotationSourceFile,
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
    DatasetSource,
    DateStamp,
    DefaultSource,
    Deposition,
    DepositionEntity,
    DepositionKeyPhotoEntity,
    DepositionSource,
    FrameEntity,
    FrameSource,
    GainEntity,
    GainSource,
    KeyImageEntity,
    KeyImageSource,
    KeyPhotoLiteral,
    KeyPhotoSource,
    OrganismDetails,
    PicturePath,
    RawTiltEntity,
    RawTiltSource,
    RunEntity,
    RunSource,
    SampleTypeEnum,
    SourceParentFiltersEntity,
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
from pydantic import field_validator, model_validator
from typing_extensions import Self

ROOT_DIR = "../../"
sys.path.append(ROOT_DIR)
sys.path.append(ROOT_DIR + "ingestion_tools/scripts/")

from ingestion_tools.scripts.importers.annotation import AnnotationImporter  # noqa: E402
from ingestion_tools.scripts.importers.dataset import DatasetImporter  # noqa: E402
from ingestion_tools.scripts.importers.dataset_key_photo import DatasetKeyPhotoImporter  # noqa: E402
from ingestion_tools.scripts.importers.frame import FrameImporter  # noqa: E402
from ingestion_tools.scripts.importers.gain import GainImporter  # noqa: E402
from ingestion_tools.scripts.importers.rawtilt import RawTiltImporter  # noqa: E402
from ingestion_tools.scripts.importers.run import RunImporter  # noqa: E402
from ingestion_tools.scripts.importers.tiltseries import TiltSeriesImporter  # noqa: E402
from ingestion_tools.scripts.importers.tomogram import TomogramImporter  # noqa: E402
from ingestion_tools.scripts.importers.voxel_spacing import VoxelSpacingImporter  # noqa: E402
from ingestion_tools.scripts.standardize_dirs import IMPORTER_DEP_TREE, flatten_dependency_tree  # noqa: E402

logger = logging.getLogger("dataset_config_validate")

CELLULAR_COMPONENT_GO_ID = "GO:0005575"
STRING_FORMATTED_STRING_REGEX = r"^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$"
VALID_IMAGE_FORMATS = ("image/png", "image/jpeg", "image/jpg", "image/gif")
# Note that model namees should all be uppercase or pascal case
CAMERA_MANUFACTURER_TO_MODEL = {
    ("FEI", "TFS"): ["FALCON IV", "Falcon4i"],
    ("Gatan", "GATAN"): ["K2", "K2 SUMMIT", "K3", "K3 BIOQUANTUM", "UltraCam", "UltraScan"],
}
FLATTENED_DEP_TREE = {
    key.type_key: {value.type_key for value in value_set}
    for key, value_set in flatten_dependency_tree(IMPORTER_DEP_TREE).items()
}

# Flag to determine if network validation should be run (set by provided Container arg)
running_network_validation = False


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
        all_errors.append(ValueError(f"Invalid ORCIDs found in annotation authors: {invalid_orcids}"))

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
        ancestor_ids = [ancestor["obo_id"] for ancestor in (await response.json())["_embedded"]["terms"]]
        return response.status == 200 and id_ancestor in ancestor_ids


def validate_id_name_object(
    id: str,
    name: str,
    validate_name: bool = True,
    ancestor: str | None = None,
) -> None:
    """
    Validates the ID and name, ensuring that:
    - The ID is valid (exists in the OLS API)
    - The name matches the ID
    - The name is an ancestor of the ancestor ID (if provided)
    """
    logger.debug("Validating %s with ID %s", name, id)

    id_data, valid_id = asyncio.run(validate_id(id))

    if not valid_id:
        raise ValueError(f"Invalid ID {id}")

    # return here since if name validation is not done, we don't need to check ancestors
    if not validate_name:
        return

    logger.debug("Valid ID, now checking if name '%s' matches ID: %s", name, id)
    # check if the name matches the ID's label or any of its synonyms
    valid_name = False
    for entry in id_data["_embedded"]["terms"]:
        if name == entry["label"].lower() or name in [synonym.lower() for synonym in entry["synonyms"]]:
            valid_name = True
            break

    if not valid_name:
        raise ValueError(f"name '{name}' does not match id: {id}")

    if ancestor is None:
        return

    logger.debug("Valid name, now checking if %s is an ancestor of %s", name, ancestor)
    if not asyncio.run(is_id_ancestor(ancestor, id)):
        raise ValueError(f"'{name}' is not a descendant of {ancestor}")


def validate_ontology_object(
    self: Union[AnnotationObject, CellComponent, CellStrain, CellType, TissueDetails],
    ancestor: str = None,
) -> CellType:
    """
    Validates a typical object with an ontology ID and name
    """
    if not running_network_validation:
        return self

    if self.id is None:
        return self

    validate_id_name_object(self.id.strip(), self.name.strip().lower(), True, ancestor)

    return self


def validate_organism_object(self: OrganismDetails) -> OrganismDetails:
    """
    Validates an organism object, with slightly different validation (taxonomy_id, but needs to be prefixed with NCBITaxon)
    """
    if not running_network_validation:
        return self

    if self.taxonomy_id is None:
        return self

    validate_id_name_object(f"NCBITaxon:{self.taxonomy_id}", self.name.strip().lower(), validate_name=False)

    return self


# ==============================================================================
# Key Photo Validation
# ==============================================================================
@alru_cache
async def validate_image_format(image_url: str | None) -> bool:
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


class ExtendedValidationKeyPhotoSource(KeyPhotoSource):
    literal: Optional[ExtendedValidationKeyPhotoLiteral] = KeyPhotoSource.model_fields["literal"]


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
    tasks = []

    for publication in publication_list:
        for publication_type, (regex, validate_function) in PUBLICATION_REGEXES_AND_FUNCTIONS.items():
            if not re.match(regex, publication):
                continue
            # edge case for DOI, remove the doi: prefix
            updated_publication = publication.replace("doi:", "") if publication_type == "doi" else publication
            tasks.append(validate_function(updated_publication))
            break

    results = await asyncio.gather(*tasks)
    return [publication for publication, valid in results if not valid]


def validate_publications(publications: Optional[str]) -> Optional[str]:
    if not running_network_validation:
        return publications

    if publications is None or publications == "":
        return publications

    # Convert the string to a list of publications
    publication_list = publications.replace(" ", "").rstrip(",").split(",")

    invalid_publications = asyncio.run(validate_publication_lists(publication_list))
    if len(invalid_publications) > 0:
        raise ValueError(f"Invalid publications found in annotation publications: {invalid_publications}")

    return publications


# ==============================================================================
# Sources Validation
# ==============================================================================
def validate_sources_parent_filters(source_list: List[SourceParentFiltersEntity], class_name: str) -> None:
    errors = []

    # list of sources, each possibly with a parent_filters attribute
    for i, source_element in enumerate(source_list):
        parent_filters = source_element.parent_filters
        if parent_filters is None:
            continue

        # list of types of filters being applied (include, exclude, etc.)
        for filter_type in parent_filters.model_fields:
            parent_filter = getattr(parent_filters, filter_type)
            if parent_filter is None:
                continue

            # the list of parents that are being filtered (annotation, dataset, run, etc.)
            filters = [filter for filter in parent_filter.model_fields if len(getattr(parent_filter, filter, [])) != 0]
            for filter in filters:
                if class_name in FLATTENED_DEP_TREE[filter]:
                    continue

                errors.append(
                    ValueError(f"Source entry {i} parent filter '{filter}' cannot be used with '{class_name}'"),
                )

    return errors


def validate_sources(
    source_list: List[DefaultSource] | List[VoxelSpacingSource],
    class_name: str,
    skip_parent_filters: bool = False,
) -> None:
    total_errors = []

    # For verifying that all source entries each only have one finder type
    multiple_finders_in_each_source_entries_errors = []
    standalone_finders_in_each_source_entries_errors = []

    for i, source_element in enumerate(source_list):
        finders_in_source_entry = []
        has_parent_filters = False
        for finder in source_element.model_fields:
            # If the finder is not None, add it to the list of finders in the source entry
            if getattr(source_element, finder) is None:
                continue

            if finder == "parent_filters":
                has_parent_filters = True
            else:
                finders_in_source_entry.append(finder)
        # If there are more than one finder in the source entry, add the source entry index and the finders to the error set
        if len(finders_in_source_entry) > 1:
            multiple_finders_in_each_source_entries_errors.append((i, finders_in_source_entry))
        elif len(finders_in_source_entry) == 0 and has_parent_filters:
            # means there's only a parent_filters entry
            standalone_finders_in_each_source_entries_errors.append(i)

    for i, finders in multiple_finders_in_each_source_entries_errors:
        total_errors.append(
            ValueError(f"Source entry {i} cannot have multiple finders (split into multiple entries): {finders}"),
        )
    for index in standalone_finders_in_each_source_entries_errors:
        total_errors.append(ValueError(f"Source entry {index} cannot only have a parent_filters entry"))

    if not skip_parent_filters:
        # For verifying that all parent_filters' include and exclude entries have the right filters
        total_errors += validate_sources_parent_filters(source_list, class_name)

    if len(total_errors) > 0:
        raise ValueError(total_errors)


# ==============================================================================
# Annotation Object Validation
# ==============================================================================
class ExtendedValidationAnnotationObject(AnnotationObject):
    @model_validator(mode="after")
    def validate_annotation_object(self) -> Self:
        return validate_ontology_object(self, CELLULAR_COMPONENT_GO_ID)


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
                if getattr(source_element, shape) is None:
                    continue

                # If the shape is already used in another source entry, add the shape to the error set
                if shape in used_shapes:
                    shapes_used_multiple_times_errors.add(shape)
                else:
                    used_shapes.add(shape)

        # For verifying that all source entries each only have one shape entry
        multiple_shapes_in_each_source_entries_errors = []

        for i, source_element in enumerate(source_list):
            shapes_in_source_entry = []
            for shape in source_element.model_fields:
                if getattr(source_element, shape) is None:
                    continue

                # If the shape is not None, add it to the list of shapes in the source entry
                shapes_in_source_entry.append(shape)
            # If there are more than one shape in the source entry, add the source entry index and the shapes to the error set
            if len(shapes_in_source_entry) > 1:
                multiple_shapes_in_each_source_entries_errors.append((i, shapes_in_source_entry))

        # For verifying that all source entries have exactly one of glob_string and glob_strings
        multiple_glob_strings_errors = []

        for i, source_element in enumerate(source_list):
            for shape in source_element.model_fields:
                source_entry: AnnotationSourceFile | None = getattr(source_element, shape)
                if source_entry is None:
                    continue

                has_glob_string = getattr(source_entry, "glob_string", None) is not None
                has_glob_strings = getattr(source_entry, "glob_strings", None) is not None and source_entry.glob_strings
                if has_glob_string and has_glob_strings:
                    multiple_glob_strings_errors.append((i, shape))

        if len(shapes_used_multiple_times_errors) > 0:
            total_errors.append(
                ValueError(f"Annotation cannot have multiple same-shape sources: {shapes_used_multiple_times_errors}"),
            )
        for i, shapes in multiple_shapes_in_each_source_entries_errors:
            total_errors.append(
                ValueError(f"Source entry {i} cannot have multiple shapes (split into multiple entries): {shapes}"),
            )
        for i, shape in multiple_glob_strings_errors:
            total_errors.append(
                ValueError(f"Source entry {i} shape {shape} must have exactly one of glob_string or glob_strings"),
            )

        # For verifying that all parent_filters' include and exclude entries have the right filters
        total_errors += validate_sources_parent_filters(source_list, AnnotationImporter.type_key)

        if len(total_errors) > 0:
            raise ValueError(total_errors)

        return source_list


# ==============================================================================
# Dataset Key Photo Validation
# ==============================================================================


class ExtendedValidationDatasetKeyPhotoEntity(DatasetKeyPhotoEntity):
    sources: List[ExtendedValidationKeyPhotoSource] = DatasetKeyPhotoEntity.model_fields["sources"]

    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[KeyPhotoSource]) -> List[KeyPhotoSource]:
        return validate_sources_parent_filters(source_list, DatasetKeyPhotoImporter.type_key)


# ==============================================================================
# Dataset Validation
# ==============================================================================
class ExtendedValidationCellComponent(CellComponent):
    @model_validator(mode="after")
    def validate_cell_component(self) -> Self:
        return validate_ontology_object(self, CELLULAR_COMPONENT_GO_ID)


class ExtendedValidationCellStrain(CellStrain):
    @model_validator(mode="after")
    def validate_cell_strain(self) -> Self:
        return validate_ontology_object(self)


class ExtendedValidationCellType(CellType):
    @model_validator(mode="after")
    def validate_cell_type(self) -> Self:
        return validate_ontology_object(self)


class ExtendedValidationTissue(TissueDetails):
    @model_validator(mode="after")
    def validate_tissue(self) -> Self:
        return validate_ontology_object(self)


class ExtendedValidationOrganism(OrganismDetails):
    @model_validator(mode="after")
    def validate_organism(self) -> Self:
        return validate_organism_object(self)


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

    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[DatasetSource]) -> List[DatasetSource]:
        return validate_sources(source_list, DatasetImporter.type_key, skip_parent_filters=True)


# ==============================================================================
# Deposition Key Photo Validation
# ==============================================================================
class ExtendedValidationDepositionKeyPhotoEntity(DepositionKeyPhotoEntity):
    sources: List[ExtendedValidationKeyPhotoSource] = DepositionKeyPhotoEntity.model_fields["sources"]

    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[KeyPhotoSource]) -> List[KeyPhotoSource]:
        # TODO: change "deposition_keyphoto" to the correct importer type when it gets implemented
        return validate_sources_parent_filters(source_list, "deposition_keyphoto")


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

        if len(all_errors) > 0:
            raise ValueError(all_errors)

        return authors


class ExtendedValidationDepositionEntity(DepositionEntity):
    metadata: ExtendedValidationDeposition = DepositionEntity.model_fields["metadata"]

    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[DepositionSource]) -> List[DepositionSource]:
        # TODO: change "deposition" to the correct importer type
        return validate_sources(source_list, "deposition", skip_parent_filters=True)


# ==============================================================================
# Frame Validation
# ==============================================================================
class ExtendedValidationFrameEntity(FrameEntity):
    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[FrameSource]) -> List[FrameSource]:
        return validate_sources(source_list, FrameImporter.type_key)


# ==============================================================================
# Gain Validation
# ==============================================================================
class ExtendedValidationGainEntity(GainEntity):
    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[GainSource]) -> List[GainSource]:
        return validate_sources(source_list, GainImporter.type_key)


# ==============================================================================
# Key Image Validation
# ==============================================================================
class ExtendedValidationKeyImageEntity(KeyImageEntity):
    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[KeyImageSource]) -> List[KeyImageSource]:
        return validate_sources(source_list, "key_image")


# ==============================================================================
# Raw Tilt Validation
# ==============================================================================
class ExtendedValidationRawTiltEntity(RawTiltEntity):
    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[RawTiltSource]) -> List[RawTiltSource]:
        return validate_sources(source_list, RawTiltImporter.type_key)


# ==============================================================================
# Run Validation
# ==============================================================================
class ExtendedValidationRunEntity(RunEntity):
    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[RunSource]) -> List[RunSource]:
        return validate_sources(source_list, RunImporter.type_key)


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
    metadata: ExtendedValidationTiltSeries = TiltSeriesEntity.model_fields["metadata"]

    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[TiltSeriesSource]) -> List[TiltSeriesSource]:
        return validate_sources(source_list, TiltSeriesImporter.type_key)


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

    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[TomogramSource]) -> List[TomogramSource]:
        return validate_sources(source_list, TomogramImporter.type_key)


# ==============================================================================
# Voxel Spacing Validation
# ==============================================================================
class ExtendedValidationVoxelSpacingEntity(VoxelSpacingEntity):
    @field_validator("sources")
    @classmethod
    def valid_sources(cls: Self, source_list: List[VoxelSpacingSource]) -> List[VoxelSpacingSource]:
        return validate_sources(source_list, VoxelSpacingImporter.type_key)


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
    deposition_keyphotos: Optional[List[ExtendedValidationDepositionKeyPhotoEntity]] = Container.model_fields[
        "deposition_keyphotos"
    ]
    depositions: List[ExtendedValidationDepositionEntity] = Container.model_fields["depositions"]
    frames: Optional[List[ExtendedValidationFrameEntity]] = Container.model_fields["frames"]
    gains: Optional[List[ExtendedValidationGainEntity]] = Container.model_fields["gains"]
    key_images: Optional[List[ExtendedValidationKeyImageEntity]] = Container.model_fields["key_images"]
    rawtilts: Optional[List[ExtendedValidationRawTiltEntity]] = Container.model_fields["rawtilts"]
    runs: Optional[List[ExtendedValidationRunEntity]] = Container.model_fields["runs"]
    tiltseries: Optional[List[ExtendedValidationTiltSeriesEntity]] = Container.model_fields["tiltseries"]
    tomograms: Optional[List[ExtendedValidationTomogramEntity]] = Container.model_fields["tomograms"]
    voxel_spacings: Optional[List[ExtendedValidationVoxelSpacingEntity]] = Container.model_fields["voxel_spacings"]
