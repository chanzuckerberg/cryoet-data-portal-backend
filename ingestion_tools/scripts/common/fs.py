import contextlib
import glob
import os
import os.path
import shutil
from hashlib import md5

import boto3
from s3fs import S3FileSystem


class FileSystemApi:
    force_overwrite: bool = False

    @classmethod
    def get_fs_api(cls, mode: str, force_overwrite: bool, client_kwargs: None | dict[str, str] = None):
        if mode == "s3":
            return S3Filesystem(force_overwrite=force_overwrite, client_kwargs=client_kwargs)
        else:
            return LocalFilesystem(force_overwrite=force_overwrite)

    def glob(self, *args):
        pass

    def open(self, path: str, mode: str):
        pass

    def localreadable(self, path: str) -> str:  # type: ignore
        pass

    def makedirs(self, path: str) -> None:
        pass

    def localwritable(self, path) -> str:  # type: ignore
        pass

    def push(self, path):
        pass

    def destformat(self, path) -> str:  # type: ignore
        pass

    def copy(self, src_path: str, dest_path: str):
        pass

    def read_block(self, path: str, start: int, end: int):
        pass


class S3Filesystem(FileSystemApi):
    def __init__(self, force_overwrite: bool, client_kwargs: None | dict[str, str] = None):
        self.s3fs = S3FileSystem(anon=False, client_kwargs=client_kwargs)
        self.tmpdir = "/tmp"
        self.force_overwrite = force_overwrite

    def _calc_etag(self, inputfile, partsize=8388608):
        md5_digests = []
        with open(inputfile, "rb") as f:
            for chunk in iter(lambda: f.read(partsize), b""):
                md5_digests.append(md5(chunk).digest())
        return md5(b"".join(md5_digests)).hexdigest() + "-" + str(len(md5_digests))

    def glob(self, *args):
        return self.s3fs.glob(*args)

    def open(self, path: str, mode: str):
        return self.s3fs.open(path, mode)

    def localreadable(self, path) -> str:
        local_dest_file = os.path.join(self.tmpdir, path)
        # Don't re-download it if it's already available.
        if os.path.exists(local_dest_file):
            remote_checksum = self.s3fs.info(path)["ETag"].strip('"')
            local_checksum = self._calc_etag(local_dest_file)
            if remote_checksum == local_checksum:
                print(f"Skipping re-download of {path}")
                return local_dest_file
        self.s3fs.get(path, local_dest_file)
        return local_dest_file

    def localwritable(self, path) -> str:
        local_dest_file = os.path.join(self.tmpdir, path)
        os.makedirs(os.path.dirname(local_dest_file), exist_ok=True)
        return local_dest_file

    def destformat(self, path) -> str:
        return f"s3://{path}"

    def push(self, path):
        remote_file = os.path.relpath(path, self.tmpdir)
        src_size = os.path.getsize(path)
        dest_size = 0
        with contextlib.suppress(FileNotFoundError):
            dest_size = self.s3fs.size(remote_file)
        if src_size == dest_size:
            if self.force_overwrite:
                print(f"Forcing re-upload of {path}")
            else:
                print(f"Skipping re-upload of {path}")
                return
        print(f"Pushing {path} to {remote_file}")
        self.s3fs.put_file(path, remote_file)

    # Copy from one s3 location to another
    def copy(self, src_path: str, dest_path: str):
        # Don't re-copy it if it's already available.
        if self.s3fs.exists(dest_path):
            # TODO, s3 etags aren't sufficient here, so we're cheating and using size.
            src_size = self.s3fs.size(src_path)
            dest_size = self.s3fs.size(dest_path)
            if src_size == dest_size:
                print(f"Skipping copy of {src_path} to {dest_path}")
                return

        src = src_path.split("/", 1)
        dest = dest_path.split("/", 1)
        s3 = boto3.resource("s3")
        s3.meta.client.copy({"Bucket": src[0], "Key": src[1]}, dest[0], dest[1])

        # fsspec automatically expands path strings, but we have filenames with
        # square brackets [] in them, and that breaks its copy method.
        # self.s3fs.copy(src_path, dest_path, expand=False)

    def read_block(self, path: str, start: int = 0, end: int = 1024):
        local_dest_file = self.localwritable(path)
        if os.path.exists(local_dest_file):
            remote_checksum = self.s3fs.info(path)["ETag"].strip('"')
            local_checksum = self._calc_etag(local_dest_file)
            if remote_checksum == local_checksum:
                print(f"Block skipping re-download of {path}")
                return local_dest_file

        block_path = f"{path}-block-{start}-{end}"
        local_dest_file = self.localwritable(block_path)
        with open(local_dest_file, "wb+") as local_file:
            block = self.s3fs.read_block(path, start, end)
            local_file.write(block)

        return local_dest_file


class LocalFilesystem(FileSystemApi):
    def __init__(self, force_overwrite: bool):
        self.force_overwrite = force_overwrite

    def glob(self, *args):
        return glob.glob(*args)

    def open(self, path: str, mode: str):
        return open(path, mode)

    def localreadable(self, path) -> str:
        return path

    def localwritable(self, path) -> str:
        return path

    def makedirs(self, path: str) -> None:
        os.makedirs(path, exist_ok=True)

    def destformat(self, path) -> str:
        return path

    def copy(self, src_path: str, dest_path: str):
        shutil.copy(src_path, dest_path)

    def read_block(self, path: str, start: int, end: int):
        return path
