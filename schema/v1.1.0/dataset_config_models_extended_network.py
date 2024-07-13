from __future__ import annotations

import asyncio
from typing import List, Optional

import aiohttp
from dataset_config_models import AnnotationEntity, Container
from pydantic import field_validator

running_orcid_list = {}


class ExtendedNetworkValidationContainer(Container):
    async def check_orcid(self, session, orcid_id):
        url = f"https://pub.orcid.org/v3.0/{orcid_id}"
        headers = {"Accept": "application/json"}
        async with session.get(url, headers=headers) as response:
            return orcid_id, response.status == 200

    async def verify_orcids(self, orcid_list):
        invalid_orcids = []
        new_orcids = []
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
            tasks = [self.check_orcid(self, session, orcid) for orcid in new_orcids]
            results = await asyncio.gather(*tasks)
            invalid_orcids += [orcid for orcid, valid in results if not valid]
            for orcid, valid in results:
                running_orcid_list[orcid] = valid
            return invalid_orcids

    @field_validator("annotations")
    @classmethod
    def valid_annotation_authors(cls, value: Optional[List[AnnotationEntity]]) -> Optional[List[AnnotationEntity]]:
        if value is None:
            return None
        for annotation in value:
            orcids = list({author.ORCID for author in annotation.metadata.authors if author.ORCID is not None})
            invalid_orcids = asyncio.run(cls.verify_orcids(cls, orcids))
            if len(invalid_orcids) > 0:
                raise ValueError(f"Invalid ORCIDs found in annotation authors: {invalid_orcids}")
        return value
