import zipfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from urllib.parse import urlparse

import boto3
import botocore
import click


@click.group()
def cli():
    pass


def upload_file(zipfilename, file_in_zip, file_size, bucket, s3_key):
    with open(zipfilename, "r+b") as buffer:
        s3_resource = boto3.resource("s3")
        print(f"Checking {s3_key} size: {file_size / (1024*1024)}MB", flush=True)
        try:
            objinfo = s3_resource.meta.client.head_object(Bucket=bucket, Key=s3_key)
            if objinfo["ContentLength"] == file_size:
                return f"Skipping {s3_key} / {file_size / (1024 * 1024)}MB"
        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == 404:
                pass
        print(f"Uploading {s3_key} / {file_size / (1024 * 1024)}MB", flush=True)
        z = zipfile.ZipFile(buffer)
        s3_resource.meta.client.upload_fileobj(
            z.open(file_in_zip), Bucket=bucket, Key=s3_key
        )
        return f"DONE: {s3_key} / {file_size / (1024 * 1024)}MB"


@cli.command()
@click.argument("zipfilename", required=True, type=str)
@click.argument("destination", required=True, type=str)
@click.option(
    "--parallelism", type=int, default=5, help="How many uploads to run in parallel"
)
def upload(zipfilename, destination, parallelism):
    s3_location = urlparse(destination)
    with open(zipfilename, "r+b") as buffer:
        z = zipfile.ZipFile(buffer)
        with ProcessPoolExecutor(max_workers=parallelism) as workerpool:
            tasks = []
            for filename in z.namelist():
                file_info = z.getinfo(filename)
                s3_key = f"{s3_location.path.rstrip('/')}/{filename}".lstrip("/")
                tasks.append(
                    workerpool.submit(
                        upload_file,
                        zipfilename,
                        filename,
                        file_info.file_size,
                        s3_location.netloc,
                        s3_key,
                    )
                )
            for taskres in as_completed(tasks):
                print(taskres.result())


if __name__ == "__main__":
    cli()
