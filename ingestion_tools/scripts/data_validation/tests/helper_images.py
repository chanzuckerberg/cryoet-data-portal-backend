import io

import pytest
import requests
from PIL import Image

from common.fs import FileSystemApi


def check_photo_valid(photo: str, bucket: str, filesystem: FileSystemApi):
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
    # 100px min height, 4:3 aspect ratio
    assert image.size[0] >= 134
    assert image.size[1] >= 100
