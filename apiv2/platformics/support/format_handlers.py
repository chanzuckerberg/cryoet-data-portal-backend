"""
Logic to validate that a file of a certain format is valid
"""

import gzip
import io
import json
from abc import abstractmethod
from typing import Protocol

from Bio import SeqIO
from mypy_boto3_s3.client import S3Client


class FileFormatHandler(Protocol):
    """
    Interface for a file format handler
    """

    s3client: S3Client
    bucket: str
    key: str

    def __init__(self, s3client: S3Client, bucket: str, key: str):
        self.s3client = s3client
        self.bucket = bucket
        self.key = key

    def contents(self) -> str:
        """
        Get the contents of the file
        """
        body = self.s3client.get_object(Bucket=self.bucket, Key=self.key, Range="bytes=0-1000000")["Body"]
        if self.key.endswith(".gz"):
            with gzip.GzipFile(fileobj=body) as fp:
                return fp.read().decode("utf-8")
        return body.read().decode("utf-8")

    @abstractmethod
    def validate(self) -> None:
        raise NotImplementedError


class FastaHandler(FileFormatHandler):
    """
    Validate FASTA files. Note that even truncated FASTA files are supported:
    ">" is a valid FASTA file, and so is ">abc" (without a sequence).
    """

    def validate(self) -> None:
        sequences = 0
        for _ in SeqIO.parse(io.StringIO(self.contents()), "fasta"):
            sequences += 1
        assert sequences > 0


class FastqHandler(FileFormatHandler):
    """
    Validate FASTQ files. Can't use biopython directly because large file would be truncated.
    This removes truncated FASTQ records by assuming 1 read = 4 lines.
    """

    def validate(self) -> None:
        # Load file and only keep non-truncated FASTQ records (4 lines per record)
        fastq = self.contents().split("\n")
        fastq = fastq[: len(fastq) - (len(fastq) % 4)]

        # Validate it with SeqIO
        reads = 0
        for _ in SeqIO.parse(io.StringIO("\n".join(fastq)), "fastq"):
            reads += 1
        assert reads > 0


class BedHandler(FileFormatHandler):
    """
    Validate BED files using basic checks.
    """

    def validate(self) -> None:
        # Ignore last line since it could be truncated
        records = self.contents().split("\n")[:-1]
        assert len(records) > 0

        # BED files must have at least 3 columns - error out if the file incorrectly uses spaces instead of tabs
        num_cols = -1
        for record in records:
            assert len(record.split("\t")) >= 3
            # All rows should have the same number of columns
            if num_cols == -1:
                num_cols = len(record.split("\t"))
            else:
                assert num_cols == len(record.split("\t"))


class JsonHandler(FileFormatHandler):
    """
    Validate JSON files
    """

    def validate(self) -> None:
        json.loads(self.contents())  # throws an exception for invalid JSON


class ZipHandler(FileFormatHandler):
    """
    Validate ZIP files
    """

    def validate(self) -> None:
        assert self.key.endswith(".zip")  # throws an exception if the file is not a zip file


def get_validator(format: str) -> type[FileFormatHandler]:
    """
    Returns the validator for a given file format
    """
    if format in ["fa", "fasta"]:
        return FastaHandler
    elif format == "fastq":
        return FastqHandler
    elif format == "bed":
        return BedHandler
    elif format == "json":
        return JsonHandler
    elif format == "zip":
        return ZipHandler
    else:
        raise Exception(f"Unknown file format '{format}'")
