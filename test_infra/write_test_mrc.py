import mrcfile
import numpy as np

data = np.arange(64, dtype=np.float32).reshape(4, 4, 4)

mrc = mrcfile.new("run1.rec", data, overwrite=True)

header = mrc.header
voxel_spacing = 14.08
isotropic_voxel_size = np.float32(voxel_spacing)
header.cella.x = isotropic_voxel_size * data.shape[2]
header.cella.y = isotropic_voxel_size * data.shape[1]
header.cella.z = isotropic_voxel_size * data.shape[0]
mrc.flush()
mrc.close()
