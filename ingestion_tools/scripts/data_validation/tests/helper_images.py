import io

import pytest
import requests
from PIL import Image

from common.fs import FileSystemApi


def check_photo_valid(
    photo: str,
    bucket: str,
    filesystem: FileSystemApi,
    min_height: int = 50,
    aspect_ratio: float = 1.0,
):
    """Check that a photo URL is valid. Default dimension constraint of 50px min height, 50px min width."""
    print(f"Checking photo: {photo}")
    photo_data = None
    if photo.startswith("http"):
        response = requests.get(photo)
        assert response.status_code < 400
        photo_data = response.content
    else:
        if photo.startswith("s3://"):
            pass
        elif photo.startswith(bucket):
            photo = filesystem.destformat(photo)
        else:
            photo = filesystem.destformat(f"{bucket}/{photo}")

        assert filesystem.exists(photo)
        photo_data = filesystem.open(photo, "rb").read()

    image = Image.open(io.BytesIO(photo_data))
    try:
        image.verify()
    except Exception:
        pytest.fail(f"Image verification failed: {photo}")
    assert image.format in ["JPEG", "PNG", "GIF"]
    assert image.size[0] >= min_height * aspect_ratio
    assert image.size[1] >= min_height