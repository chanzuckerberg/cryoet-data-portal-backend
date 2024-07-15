from __future__ import annotations

import asyncio
import re
from typing import Dict, List, Optional, Set, Tuple

import aiohttp
import requests
from dataset_config_models import Annotation, AnnotationEntity, AnnotationObject, Author, Container
from pydantic import field_validator, model_validator
from typing_extensions import Self

CELLULAR_COMPONENT_GO_ID = "GO:0005575"

# Stores whether or not the IDs are valid
running_orcid_list: Dict[str, bool] = {}
running_go_id_list: Dict[str, bool] = {}
running_publication_list: Dict[str, bool] = {}


async def lookup_orcid(session: aiohttp.ClientSession, orcid_id: str) -> Tuple[str, bool]:
    url = f"https://pub.orcid.org/v3.0/{orcid_id}"
    async with session.head(url) as response:
        return orcid_id, response.status == 200


async def validate_orcids(orcid_list: List[str]) -> List[str]:
    invalid_orcids: List[str] = []
    new_orcids: List[str] = []
    for orcid in orcid_list:
        if orcid in running_orcid_list:
            if not running_orcid_list[orcid]:
                invalid_orcids.append(orcid)
            else:
                pass
        else:
            new_orcids.append(orcid)

    # No new ids to check
    if len(new_orcids) == 0:
        return invalid_orcids

    async with aiohttp.ClientSession() as session:
        tasks = [lookup_orcid(session, orcid) for orcid in new_orcids]
        results = await asyncio.gather(*tasks)
        invalid_orcids += [orcid for orcid, valid in results if not valid]
        for orcid, valid in results:
            running_orcid_list[orcid] = valid
        return invalid_orcids


def get_invalid_orcids(authors: List[Author]) -> List[str]:
    orcids = list({author.ORCID for author in authors if author.ORCID is not None})
    return asyncio.run(validate_orcids(orcids))


def validate_go_id(go_id: str) -> bool:
    if go_id not in running_go_id_list:
        url = f"https://api.geneontology.org/api/ontology/term/{go_id}"
        headers = {"Accept": "application/json"}
        running_go_id_list[go_id] = requests.get(url, headers=headers).json()

    go_id_data = running_go_id_list[go_id]

    return "label" in go_id_data or "description" in go_id_data


def is_go_id_ancestor(go_id_ancestor: str, go_id: str) -> bool:
    # This is ONLY run after validating the go_id, so we know that the entry exists already in `running_go_id_list`
    if "ancestors" not in running_go_id_list[go_id]:
        url = f"https://api.geneontology.org/api/ontology/term/{go_id}/subgraph?start=0&rows=100"
        headers = {"Accept": "application/json"}
        response_json = requests.get(url, headers=headers).json()
        running_go_id_list[go_id]["ancestors"] = [ancestor["id"] for ancestor in response_json["ancestors"]]

    return go_id_ancestor in running_go_id_list[go_id]["ancestors"]


async def lookup_doi(session: aiohttp.ClientSession, doi: str) -> Tuple[str, bool]:
    url = f"https://api.crossref.org/works/{doi}/agency"
    async with session.head(url) as response:
        return doi, response.status == 200


async def lookup_empiar(session: aiohttp.ClientSession, empiar_id: str) -> Tuple[str, bool]:
    url = f"https://www.ebi.ac.uk/empiar/api/entry/{empiar_id}/"
    async with session.head(url) as response:
        return empiar_id, response.status == 200


async def lookup_emdb(session: aiohttp.ClientSession, emdb_id: str) -> Tuple[str, bool]:
    url = f"https://www.ebi.ac.uk/emdb/api/entry/{emdb_id}"
    async with session.head(url) as response:
        return emdb_id, response.status == 200


PUBLICATION_REGEXES_AND_FUNCTIONS = {
    "doi": (r"^(doi:)?10\.[0-9]{4,9}/[-._;()/:a-zA-Z0-9]+$", lookup_doi),
    "empiar": (r"^EMPIAR-[0-9]{5}$", lookup_empiar),
    "emdb": (r"^EMD-[0-9]{4,5}$", lookup_emdb),
}


async def validate_publication_lists(publication_list: List[str]) -> List[str]:
    # list of invalid publications
    invalid_publications: List[str] = []
    # type of publication to list of new publications to lookup
    new_publications: Dict[str, Set[str]] = {}

    for publication in publication_list:
        if publication in running_publication_list:
            if not running_publication_list[publication]:
                invalid_publications.append(publication)
        else:
            for publication_type, (regex, _) in PUBLICATION_REGEXES_AND_FUNCTIONS.items():
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

    tasks = []
    async with aiohttp.ClientSession() as session:
        for publication_type, (_, validate_function) in PUBLICATION_REGEXES_AND_FUNCTIONS.items():
            if publication_type in new_publications:
                tasks += [validate_function(session, entry) for entry in list(new_publications[publication_type])]

        results = await asyncio.gather(*tasks)
        invalid_publications += [publication for publication, valid in results if not valid]
        for publication, valid in results:
            running_publication_list[publication] = valid

    return invalid_publications


class NetworkValidationAnnotationObject(AnnotationObject):
    @model_validator(mode="after")
    def validate_annotation_object(self) -> Self:
        # All of this checking is based on the id, so return if id is None
        if self.id is None:
            return self

        # First ensure that the id is valid
        if not validate_go_id(self.id):
            raise ValueError(f"Invalid GO ID found in annotation object: {self.id}")

        # Then check that the name matches
        go_id_data = running_go_id_list[self.id]
        go_id_synonyms = running_go_id_list[self.id]["synonyms"]

        go_id_synonyms = [s.replace("@", "") for s in go_id_synonyms]
        if self.name not in go_id_data["label"] and not any(
            self.name in go_id_synonym for go_id_synonym in go_id_synonyms
        ):
            raise ValueError(f"Annotation object name '{self.name}' does not match id: {self.id}")

        # Then check that the go_id is part of the cellular_component ontology
        if not is_go_id_ancestor(CELLULAR_COMPONENT_GO_ID, self.id):
            raise ValueError(f"Annotation object id {self.id} is not a cellular component")

        return self


class NetworkValidationAnnotation(Annotation):
    annotation_object: NetworkValidationAnnotationObject = Annotation.model_fields["annotation_object"]

    # Make it a field validator so we can take in the whole list of authors and submit async requests
    @field_validator("authors")
    @classmethod
    def validate_annotation_authors(cls, authors: List[Author]) -> List[Author]:
        # will error if invalid
        invalid_orcids = get_invalid_orcids(authors)
        if len(invalid_orcids) > 0:
            raise ValueError(f"Invalid ORCIDs found in annotation authors: {invalid_orcids}")

        return authors

    @field_validator("annotation_publications")
    @classmethod
    def validate_annotation_publications(cls, annotation_publications: str) -> str:
        if annotation_publications is None or annotation_publications == "":
            return annotation_publications

        annotation_publications_list = annotation_publications.replace(" ", "").split(",")
        if annotation_publications_list[-1] == "":
            annotation_publications_list.pop()

        invalid_publications = asyncio.run(validate_publication_lists(annotation_publications_list))
        if len(invalid_publications) > 0:
            raise ValueError(f"Invalid publications found in annotation publications: {invalid_publications}")
        return annotation_publications


class NetworkValidationAnnotationEntity(AnnotationEntity):
    metadata: NetworkValidationAnnotation = AnnotationEntity.model_fields["metadata"]


class NetworkValidationContainer(Container):
    annotations: Optional[List[NetworkValidationAnnotationEntity]] = Container.model_fields["annotations"]


NetworkValidationAnnotationObject.model_rebuild()
NetworkValidationAnnotation.model_rebuild()
NetworkValidationAnnotationEntity.model_rebuild()
NetworkValidationContainer.model_rebuild()
