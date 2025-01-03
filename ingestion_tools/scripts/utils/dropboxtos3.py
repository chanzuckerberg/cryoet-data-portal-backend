import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from urllib.parse import urlparse

import boto3
import botocore
import click
import dropbox
import dropbox.files

TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")


@click.group()
def cli():
    pass


def upload_file(dropbox_file, file_size, bucket, s3_key):
    with dropbox.Dropbox(TOKEN) as dbx:
        s3_resource = boto3.resource("s3")
        print(f"Checking {s3_key} size: {file_size / (1024*1024)}MB", flush=True)
        try:
            objinfo = s3_resource.meta.client.head_object(Bucket=bucket, Key=s3_key)
            if objinfo["ContentLength"] == file_size:
                return f"Skipping {s3_key} / {file_size / (1024 * 1024)}MB"
        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == 404:
                pass
        print(
            f"Uploading {dropbox_file} to {s3_key} / {file_size / (1024 * 1024)}MB",
            flush=True,
        )
        _, dbxfile = dbx.files_download(dropbox_file)
        s3_resource.meta.client.upload_fileobj(dbxfile.raw, Bucket=bucket, Key=s3_key)
        return f"DONE: {s3_key} / {file_size / (1024 * 1024)}MB"


def get_dropbox_files(dbx, prefix):
    result = dbx.files_list_folder(prefix, recursive=True)

    while True:
        for entry in result.entries:
            if isinstance(entry, dropbox.files.FileMetadata):
                yield entry

        if result.has_more:
            result = dbx.files_list_folder_continue(result.cursor)
            continue
        break


@cli.command()
@click.argument("dropbox_path", required=True, type=str)
@click.argument("destination", required=True, type=str)
@click.option("--parallelism", type=int, default=5, help="How many uploads to run in parallel")
def upload(dropbox_path: str, destination: str, parallelism: int):
    s3_location = urlparse(destination)
    tasks = []
    with ProcessPoolExecutor(max_workers=parallelism) as workerpool:
        with dropbox.Dropbox(TOKEN) as dbx:
            for file in get_dropbox_files(dbx, dropbox_path):
                dest_path = file.path_display[len(dropbox_path) :]
                s3_key = f"{s3_location.path.rstrip('/')}/{dest_path}".lstrip("/")
                tasks.append(
                    workerpool.submit(
                        upload_file,
                        file.path_display,
                        file.size,
                        s3_location.netloc,
                        s3_key,
                    ),
                )
        for taskres in as_completed(tasks):
            print(taskres.result())


if __name__ == "__main__":
    cli()
