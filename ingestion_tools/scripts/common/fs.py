import contextlib
import glob
import os
import os.path
import shutil
from abc import ABC, abstractmethod
from hashlib import md5
from io import TextIOBase

import boto3
from s3fs import S3FileSystem


class FileSystemApi(ABC):
    force_overwrite: bool = False

    @classmethod
    def get_fs_api(
        cls,
        mode: str,
        force_overwrite: bool,
        client_kwargs: None | dict[str, str] = None,
    ) -> "FileSystemApi":
        if mode == "s3":
            return S3Filesystem(force_overwrite=force_overwrite, client_kwargs=client_kwargs)
        else:
            return LocalFilesystem(force_overwrite=force_overwrite)

    @abstractmethod
    def glob(self, *args: list[str]) -> list[str]:
        pass

    @abstractmethod
    def open(self, path: str, mode: str) -> TextIOBase:
        pass

    @abstractmethod
    def localreadable(self, path: str) -> str:
        pass

    def makedirs(self, path: str) -> None:
        return None

    @abstractmethod
    def localwritable(self, path: str) -> str:
        pass

    @abstractmethod
    def push(self, path: str) -> None:
        pass

    @abstractmethod
    def destformat(self, path: str) -> str:
        pass

    @abstractmethod
    def copy(self, src_path: str, dest_path: str) -> None:
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        pass

    @abstractmethod
    def read_block(self, path: str, start: int | None = None, end: int | None = None) -> str:
        pass


class S3Filesystem(FileSystemApi):
    def __init__(self, force_overwrite: bool, client_kwargs: None | dict[str, str] = None):
        self.client_kwargs = client_kwargs or {}
        self.s3fs = S3FileSystem(anon=False, client_kwargs=client_kwargs)
        self.tmpdir = "/tmp"
        self.force_overwrite = force_overwrite

    def _calc_etag(self, inputfile: str, partsize: int = 8388608) -> bytes:
        md5_digests = []
        with open(inputfile, "rb") as f:
            for chunk in iter(lambda: f.read(partsize), b""):
                md5_digests.append(md5(chunk).digest())
        return md5(b"".join(md5_digests)).hexdigest() + "-" + str(len(md5_digests))

    def glob(self, *args: list[str]) -> list[str]:
        return self.s3fs.glob(*args)

    def open(self, path: str, mode: str) -> TextIOBase:
        return self.s3fs.open(path, mode)

    def localreadable(self, path: str) -> str:
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

    def localwritable(self, path: str) -> str:
        local_dest_file = os.path.join(self.tmpdir, path)
        os.makedirs(os.path.dirname(local_dest_file), exist_ok=True)
        return local_dest_file

    def destformat(self, path: str) -> str:
        return f"s3://{path}"

    def push(self, path: str) -> None:
        remote_file = os.path.relpath(path, self.tmpdir)
        if os.path.isfile(path):
            src_size = os.path.getsize(path)
            dest_size = 0
            with contextlib.suppress(FileNotFoundError):
                dest_size = self.s3fs.size(remote_file)
            # TODO: Update this to use Etag
            if src_size == dest_size:
                if self.force_overwrite:
                    print(f"Forcing re-upload of {path}")
                else:
                    print(f"Skipping re-upload of {path}")
                    return
        print(f"Pushing {path} to {remote_file}")
        self.s3fs.put(path, remote_file, recursive=True)

    def exists(self, path: str) -> bool:
        return self.s3fs.exists(path)

    # Copy from one s3 location to another
    def copy(self, src_path: str, dest_path: str) -> None:
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
        s3 = boto3.resource("s3", **self.client_kwargs)
        s3.meta.client.copy({"Bucket": src[0], "Key": src[1]}, dest[0], dest[1])

        # fsspec automatically expands path strings, but we have filenames with
        # square brackets [] in them, and that breaks its copy method.
        # self.s3fs.copy(src_path, dest_path, expand=False)

    def read_block(self, path: str, start: int | None = None, end: int | None = None) -> str:
        if start is None:
            start = 0
        if end is None:
            end = 1024
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

    def glob(self, *args: list[str]) -> list[str]:
        return glob.glob(*args)

    def open(self, path: str, mode: str) -> TextIOBase:
        return open(path, mode)  # noqa

    def localreadable(self, path: str) -> str:
        return path

    def localwritable(self, path: str) -> str:
        return path

    def makedirs(self, path: str) -> None:
        os.makedirs(path, exist_ok=True)

    def destformat(self, path: str) -> str:
        return path

    def copy(self, src_path: str, dest_path: str) -> None:
        shutil.copy(src_path, dest_path)

    def read_block(self, path: str, start: int | None = None, end: int | None = None) -> str:
        return path

    def push(self, path: str) -> None:
        pass

    def exists(self, path: str) -> bool:
        return os.path.exists(path)
