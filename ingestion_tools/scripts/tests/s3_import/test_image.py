import mrcfile
import numpy as np

from common.fs import FileSystemApi
from common.image import MRCReader, VolumeInfo


def test_volume_info_dimensions() -> None:
    info = VolumeInfo(voxel_size=1.0, xdim=10, ydim=20, zdim=30, rms=0.5, dmean=0.1)
    assert info.get_dimensions() == {"x": 10, "y": 20, "z": 30}
    assert info.get_max_dimension() == 30


def _write_mrc(path: str, shape: tuple[int, int, int], starts: tuple[int, int, int]) -> None:
    """Write a minimal MRC at `path` with the given (z, y, x) shape and non-zero (nx,ny,nz)start."""
    data = np.zeros(shape, dtype=np.float32)
    with mrcfile.new(path, overwrite=True) as mrc:
        mrc.set_data(data)
        mrc.header.nxstart = starts[0]
        mrc.header.nystart = starts[1]
        mrc.header.nzstart = starts[2]
        mrc.voxel_size = 1.0


def test_mrc_reader_dimensions_ignore_nstart(local_fs: FileSystemApi, tmp_path) -> None:
    """nxstart/nystart/nzstart are origin coords per MRC2014 spec; they must not affect reported dims."""
    mrc_path = str(tmp_path / "with_nstart.mrc")
    # shape is (z, y, x) -> nz=30, ny=20, nx=10; non-zero starts must be ignored for dims
    _write_mrc(mrc_path, shape=(30, 20, 10), starts=(5, 7, 9))

    reader = MRCReader(local_fs, mrc_path)
    volume_info = reader.get_volume_info()

    assert volume_info.get_dimensions() == {"x": 10, "y": 20, "z": 30}
    assert volume_info.xdim == 10
    assert volume_info.ydim == 20
    assert volume_info.zdim == 30


def test_mrc_reader_dimensions_zero_nstart(local_fs: FileSystemApi, tmp_path) -> None:
    """Sanity check: zero nstart still produces correct dims."""
    mrc_path = str(tmp_path / "zero_nstart.mrc")
    _write_mrc(mrc_path, shape=(30, 20, 10), starts=(0, 0, 0))

    volume_info = MRCReader(local_fs, mrc_path).get_volume_info()
    assert volume_info.get_dimensions() == {"x": 10, "y": 20, "z": 30}
