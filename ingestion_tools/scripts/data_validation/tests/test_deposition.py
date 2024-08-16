"""
Validate deposition metadata. This is not an actual pytest class that is run, but instead a static class that is called
by other test classes to validate their corresponding deposition's metadata.
"""

import json
from typing import Dict, Union

from tests.helper_images import check_photo_valid

from common.fs import FileSystemApi


class HelperTestDeposition:
    """
    Not an actual pytest class, but a static class that is called by other test classes to validate their corresponding
    deposition's metadata.
    """

    cached_deposition_valid: Dict[str, bool] = {}

    @staticmethod
    def _get_deposition_metadata_file(deposition_id: str, bucket: str, filesystem: FileSystemApi) -> str:
        dst = f"s3://{bucket}/depositions_metadata/{deposition_id}/deposition_metadata.json"
        assert filesystem.s3fs.exists(dst)
        return dst

    @staticmethod
    def _get_deposition_metadata(deposition_metadata_file: str, filesystem: FileSystemApi) -> Dict:
        """Load the deposition metadata."""
        print(f"Loading deposition metadata: {deposition_metadata_file}")
        with filesystem.open(deposition_metadata_file, "r") as f:
            return json.load(f)

    @staticmethod
    def check_deposition_metadata(deposition_id: Union[str, int], bucket: str, filesystem: FileSystemApi) -> Dict:
        """A deposition metadata sanity check and ensuring that photos are valid."""
        # No need to check the same deposition twice.
        deposition_id = str(deposition_id)
        if deposition_id in HelperTestDeposition.cached_deposition_valid:
            return
        print(f"Checking deposition: {deposition_id}")
        HelperTestDeposition.cached_deposition_valid[deposition_id] = False
        deposition_file = HelperTestDeposition._get_deposition_metadata_file(deposition_id, bucket, filesystem)
        deposition_metadata = HelperTestDeposition._get_deposition_metadata(deposition_file, filesystem)
        assert deposition_metadata["deposition_description"]
        assert deposition_metadata["deposition_title"]
        assert deposition_metadata["deposition_identifier"]
        assert deposition_metadata["deposition_id"]
        assert isinstance(deposition_metadata["authors"], list)
        assert isinstance(deposition_metadata["authors"][0], dict)

        if (thumbnail := deposition_metadata["key_photos"]["thumbnail"]) is not None:
            check_photo_valid(thumbnail, bucket, filesystem)

        if (snapshot := deposition_metadata["key_photos"]["snapshot"]) is not None:
            check_photo_valid(snapshot, bucket, filesystem)

        HelperTestDeposition.cached_deposition_valid[deposition_id] = True
