from mrcfile.mrcinterpreter import MrcInterpreter

from common.fs import FileSystemApi


def get_header(mrcfile: str) -> MrcInterpreter:
    """Get the mrc file header for a tilt series without downloading the entire file."""
    fs = FileSystemApi.get_fs_api(mode="s3", force_overwrite=False)
    with fs.open(mrcfile, "rb") as f:
        header = MrcInterpreter(iostream=f, permissive=True, header_only=True)
    return header
