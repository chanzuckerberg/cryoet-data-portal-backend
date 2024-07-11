from __future__ import annotations
from typing import Any, ClassVar, List, Literal, Dict, Optional, Union
import requests
# import grequests

from pydantic import field_validator

from dataset_config_models import Container, AnnotationEntity

class ExtendedContainer(Container):
    def lookup_orcid(orcid: str) -> bool:
        """
        Check if the orcid is a valid ORCID, assuming that the orcid has already gone through the LinkML regex validation.
        """
        url = f"https://pub.orcid.org/v3.0/{orcid}"
        headers = {"Accept": "application/json"}

        response = requests.head(url, headers=headers)

        return response.status_code == 200
    
    @field_validator("annotations", check_fields=False)
    def valid_annotation_authors(cls, value: Optional[List[AnnotationEntity]]) -> Optional[List[AnnotationEntity]]:
        if value is None:
            return None
        for annotation in value:
            for author in annotation.metadata.authors:
                if author.ORCID is not None and not cls.lookup_orcid(author.ORCID):
                    raise ValueError(f"Invalid ORCID: {author.ORCID}")
        return value
    