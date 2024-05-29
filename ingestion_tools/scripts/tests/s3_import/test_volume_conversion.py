import mrcfile
import zarr
import ome_zarr
import ome_zarr.io
from common.fs import FileSystemApi
from common.image import make_pyramids
from ome_zarr.io import parse_url as ZarrLocation
from ome_zarr.reader import Reader as Reader


def test_convert_mrc_to_mrc(s3_fs: FileSystemApi, test_output_bucket: str) -> None:
    output_path = f"{test_output_bucket}/output"
    input_file = "test-public-bucket/input_bucket/sample_tomos/input_mrc.mrc"
    make_pyramids(s3_fs, output_path, input_file)

    output_mrc = s3_fs.localreadable(output_path + ".mrc")
    mrc = mrcfile.open(output_mrc, "r")
    assert round(mrc.voxel_size.y.item(), 2) == 14.08

    assert round(mrc.header.cella.x.item(), 2) == 56.32
    assert round(mrc.header.cella.x.item(), 2) == 56.32
    assert round(mrc.header.cella.x.item(), 2) == 56.32

    assert round(mrc.header.rms.item(), 2) == 1.12
    assert round(mrc.header.dmean.item(), 1) == 2.5
    assert round(mrc.header.dmax.item(), 1) == 4
    assert round(mrc.header.dmin.item(), 1) == 1

    assert mrc.header.nxstart.item() == 0
    assert mrc.header.nystart.item() == 0
    assert mrc.header.nzstart.item() == 0

    assert mrc.header.mx.item() == 4
    assert mrc.header.my.item() == 4
    assert mrc.header.mz.item() == 4

def test_convert_zarr_to_mrc(s3_fs: FileSystemApi, test_output_bucket: str) -> None:
    output_path = f"{test_output_bucket}/output"
    input_file = "test-public-bucket/input_bucket/sample_tomos/input_omezarr.zarr"
    make_pyramids(s3_fs, output_path, input_file)

    output_mrc = s3_fs.localreadable(output_path + ".mrc")
    mrc = mrcfile.open(output_mrc, "r")
    assert round(mrc.voxel_size.y.item(), 2) == 14.08

    assert round(mrc.header.cella.x.item(), 2) == 56.32
    assert round(mrc.header.cella.x.item(), 2) == 56.32
    assert round(mrc.header.cella.x.item(), 2) == 56.32

    assert round(mrc.header.rms.item(), 2) == 1.12
    assert round(mrc.header.dmean.item(), 1) == 2.5
    assert round(mrc.header.dmax.item(), 1) == 4
    assert round(mrc.header.dmin.item(), 1) == 1

    assert mrc.header.nxstart.item() == 0
    assert mrc.header.nystart.item() == 0
    assert mrc.header.nzstart.item() == 0

    assert mrc.header.mx.item() == 4
    assert mrc.header.my.item() == 4
    assert mrc.header.mz.item() == 4

def test_convert_mrc_to_omezarr(s3_fs: FileSystemApi, test_output_bucket: str) -> None:
    output_path = f"{test_output_bucket}/output"
    input_file = "test-public-bucket/input_bucket/sample_tomos/input_mrc.mrc"
    make_pyramids(s3_fs, output_path, input_file)

    fsstore = zarr.storage.FSStore(url=f"{output_path}.zarr", mode="r", fs=s3_fs.s3fs)
    loc = ZarrLocation(fsstore)
    root_group = zarr.group(loc.store)
    attrs = loc.root_attrs
    assert attrs["multiscales"][0]["axes"][0] == {"name": "z", "unit": "angstrom", "type": "space"}

    assert len(attrs["multiscales"][0]["datasets"]) == 3
    spacing = 14.08
    for ds in attrs["multiscales"][0]["datasets"]:
        assert ds["coordinateTransformations"][0]["scale"] == [spacing, spacing, spacing]
        spacing *= 2
    
    reader = Reader(loc)
    nodes = list(reader())
    assert len(nodes[0].data) == 3
    img_dim = 4
    for node in nodes[0].data:
        assert node.shape == (img_dim, img_dim, img_dim)
        img_dim /= 2

def test_convert_omezarr_to_omezarr(s3_fs: FileSystemApi, test_output_bucket: str) -> None:
    output_path = f"{test_output_bucket}/output"
    input_file = "test-public-bucket/input_bucket/sample_tomos/input_omezarr.zarr"
    make_pyramids(s3_fs, output_path, input_file)

    fsstore = zarr.storage.FSStore(url=f"{output_path}.zarr", mode="r", fs=s3_fs.s3fs)
    loc = ZarrLocation(fsstore)
    root_group = zarr.group(loc.store)
    attrs = loc.root_attrs
    assert attrs["multiscales"][0]["axes"][0] == {"name": "z", "unit": "angstrom", "type": "space"}

    assert len(attrs["multiscales"][0]["datasets"]) == 3
    spacing = 14.08
    for ds in attrs["multiscales"][0]["datasets"]:
        assert ds["coordinateTransformations"][0]["scale"] == [spacing, spacing, spacing]
        spacing *= 2
    
    reader = Reader(loc)
    nodes = list(reader())
    assert len(nodes[0].data) == 3
    img_dim = 4
    for node in nodes[0].data:
        assert node.shape == (img_dim, img_dim, img_dim)
        img_dim /= 2