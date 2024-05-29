import mrcfile
import numpy as np
import ome_zarr
import ome_zarr.io
import ome_zarr.writer
import zarr


def get_data():
    data = np.arange(64, dtype=np.float32).reshape(4, 4, 4)
    data[:, 0] = 1.0
    data[:, 1] = 2.0
    data[:, 2] = 3.0
    data[:, 3] = 4.0
    return data


def write_mrc(filename: str, data, voxel_size: float):
    mrc = mrcfile.new(filename, data, overwrite=True)

    mrc.voxel_size = voxel_size
    # header = mrc.header
    # isotropic_voxel_size = np.float32(voxel_spacing)
    # header.cella.x = isotropic_voxel_size * data.shape[2]
    # header.cella.y = isotropic_voxel_size * data.shape[1]
    # header.cella.z = isotropic_voxel_size * data.shape[0]
    mrc.flush()
    mrc.close()


def write_zarr(filename: str, data: np.array, voxel_size: float):
    loc = ome_zarr.io.parse_url(filename, mode="w")
    root_group = zarr.group(loc.store, overwrite=True)
    chunk_size = (256, 256, 256)

    scales = [[{"scale": [voxel_size, voxel_size, voxel_size], "type": "scale"}]]
    pyramid = [data]

    # Write the pyramid to the zarr store
    return ome_zarr.writer.write_multiscale(
        pyramid,
        group=root_group,
        axes=[{"name": item, "type": "space"} for item in "xyz"],
        coordinate_transformations=scales,
        storage_options=dict(chunks=chunk_size, overwrite=True),
        compute=True,
    )


if __name__ == "__main__":
    data = get_data()
    write_mrc("run1.mrc", data, 14.08)
    write_zarr("run1.zarr", data, 14.08)
