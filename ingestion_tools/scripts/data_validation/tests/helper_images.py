import io

import pytest
import requests
from PIL import Image

from common.fs import FileSystemApi


def check_photo_valid(
    photo_uri_path: str,
    bucket: str,
    filesystem: FileSystemApi,
    min_height: int = 50,
    aspect_ratio: float = 1.0,
):
    """Check that a photo URL is valid. Default dimension constraint of 50px min height, 50px min width."""
    print(f"Checking photo: {photo_uri_path}")
    photo_data = None
    if photo_uri_path.startswith("http"):
        response = requests.get(photo_uri_path)
        assert response.status_code < 400
        photo_data = response.content
    else:
        if photo_uri_path.startswith("s3://"):
            pass
        elif photo_uri_path.startswith(bucket):
            photo_uri_path = filesystem.destformat(photo_uri_path)
        else:
            photo_uri_path = filesystem.destformat(f"{bucket}/{photo_uri_path}")

        assert filesystem.exists(photo_uri_path)
        photo_data = filesystem.open(photo_uri_path, "rb").read()

    image = Image.open(io.BytesIO(photo_data))
    try:
        image.verify()
    except Exception:
        pytest.fail(f"Image verification failed: {photo_uri_path}")
    assert image.format in ["JPEG", "PNG", "GIF"]
    assert image.size[0] >= min_height * aspect_ratio
    assert image.size[1] >= min_height
