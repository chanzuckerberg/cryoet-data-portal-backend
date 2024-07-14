from __future__ import annotations

import asyncio
from typing import Dict, List, Optional

import aiohttp
import requests
from dataset_config_models import Annotation, AnnotationEntity, AnnotationObject, Author, Container
from pydantic import field_validator, model_validator
from typing_extensions import Self

# Stores whether or not the IDs are valid
running_orcid_list: Dict[str, bool] = {}
running_go_id_list: Dict[str, bool] = {}


async def check_orcid(session: aiohttp.ClientSession, orcid_id: str):
    url = f"https://pub.orcid.org/v3.0/{orcid_id}"
    headers = {"Accept": "application/json"}
    async with session.head(url, headers=headers) as response:
        return orcid_id, response.status == 200


async def verify_orcids(orcid_list: List[str]):
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

    if len(new_orcids) == 0:
        return invalid_orcids

    async with aiohttp.ClientSession() as session:
        tasks = [check_orcid(session, orcid) for orcid in new_orcids]
        results = await asyncio.gather(*tasks)
        invalid_orcids += [orcid for orcid, valid in results if not valid]
        for orcid, valid in results:
            running_orcid_list[orcid] = valid
        return invalid_orcids


def valid_authors(value: List[Author]) -> List[Author]:
    orcids = list({author.ORCID for author in value if author.ORCID is not None})
    invalid_orcids = asyncio.run(verify_orcids(orcids))
    if len(invalid_orcids) > 0:
        raise ValueError(f"Invalid ORCIDs found in annotation authors: {invalid_orcids}")
    return value


def valid_go_id(value: str) -> str:
    if value in running_go_id_list:
        if not running_go_id_list[value]:
            raise ValueError(f"Invalid GO ID found in annotation object: {value}")
        return value
    url = f"https://api.geneontology.org/api/ontology/term/{value}"
    headers = {"Accept": "application/json"}
    response_json = requests.get(url, headers=headers).json()
    if "label" not in response_json and "description" not in response_json:
        running_go_id_list[value] = False
        raise ValueError(f"Invalid GO ID found in annotation object: {value}")
    else:
        running_go_id_list[value] = True
    return value


class NetworkValidationAnnotationObject(AnnotationObject):
    @field_validator("id")
    @classmethod
    def valid_annotation_object_id(cls, value: str) -> str:
        return valid_go_id(value)

class NetworkValidationAnnotation(Annotation):
    annotation_object: NetworkValidationAnnotationObject = Annotation.model_fields["annotation_object"]

    # Make it a field validator so we can take in the whole list of authors and submit async requests
    @field_validator("authors")
    @classmethod
    def valid_annotation_authors(cls, value: List[Author]) -> List[Author]:
        return valid_authors(value)


class NetworkValidationAnnotationEntity(AnnotationEntity):
    metadata: NetworkValidationAnnotation = AnnotationEntity.model_fields["metadata"]


class NetworkValidationContainer(Container):
    annotations: Optional[List[NetworkValidationAnnotationEntity]] = Container.model_fields["annotations"]


NetworkValidationAnnotationObject.model_rebuild()
NetworkValidationAnnotation.model_rebuild()
NetworkValidationAnnotationEntity.model_rebuild()
NetworkValidationContainer.model_rebuild()
