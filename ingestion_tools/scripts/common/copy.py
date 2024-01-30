import requests

from common.fs import FileSystemApi


def copy_by_src(src_path: str, dest_path: str, fs: FileSystemApi):
    if src_path.startswith("https://"):
        file_path = fs.localwritable(dest_path)
        with open(file_path, mode="wb") as file:
            response = requests.get(src_path)
            file.write(response.content)
        fs.push(file_path)
    else:
        fs.copy(src_path, dest_path)
