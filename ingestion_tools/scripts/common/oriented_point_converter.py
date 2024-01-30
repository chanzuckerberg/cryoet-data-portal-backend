"""
Various conversion of euler angle to rotation matrix
"""
import numpy as np
import starfile
from scipy.spatial.transform import Rotation as R


def invert_rot_matrices_axis_order(rot_xyz):
    """
    Rotate n x (3,3) rotation matrices in ndarray based on xyz order to numpy standard zyx, and vice versa
    """
    rot_len = rot_xyz.shape[0]
    rot_zyx = np.flip(np.ravel(rot_xyz).reshape((rot_len, 3, 3)), [1, 2])
    return rot_zyx


def invert_positions_axis_order(xyz):
    """
    Invert n x (3,) coordinate vectors in ndarray based on xyz order to numpy standard zyx, and vice versa
    """
    coord_len = xyz.shape[0]
    zyx = np.flip(np.ravel(xyz).reshape((coord_len, 3)), axis=(1,))
    return zyx


def apply_rotation(points, rotation_matrix):
    rotated = np.matmul(rotation_matrix, points)
    return rotated


def apply_xyz_affine(xyzs, affine_matrix):
    """
    Return xyz points in (n,3) ndarray
    Inputs:
        xyz points in (n,3) ndarray
        xyz affine_matrix in (4,4) ndarray where [3:] is the translation
    """
    in_hcoords = np.hstack((xyzs, np.ones((xyzs.shape[0], 1))))
    out_hcoords = in_hcoords @ affine_matrix
    return out_hcoords[:, :-1]


def _from_relion3_star_filtered(file_path, filter_value, filter_key="rlnMicrographName", binning=1.0, order="xyz"):
    """
    Filter Relion3 star file according to filter_value and filter_key
    and then convert to position and rotation matrix
    to be applied to the instance volume.
    """
    df = starfile.read(file_path)
    if filter_value:
        df2 = df[(df[filter_key] == filter_value)]
    else:
        df2 = df
    xyz_c = df2[["rlnCoordinateX", "rlnCoordinateY", "rlnCoordinateZ"]].to_numpy()
    try:
        xyz_s = df2[["rlnOriginX", "rlnOriginY", "rlnOriginZ"]].to_numpy()  # shift
        positions = (xyz_c - xyz_s) / float(binning)
    except:
        # do not have origin (shift)
        positions = xyz_c / float(binning)
    euler_angles = df2[["rlnAngleRot", "rlnAngleTilt", "rlnAnglePsi"]].to_numpy()
    # intrinsic transformation
    rot = R.from_euler(angles=euler_angles, seq="ZYZ", degrees=True).inv().as_matrix()
    if order == "zyx":
        rot = invert_rot_matrices_axis_order(rot)
        positions = invert_positions_axis_order(positions)
    return positions, rot


def from_relion3_star(file_path, micrograph_name, binning=1.0, order="xyz"):
    """
    Relion3 star format convertion to position and rotation matrix
    to be applied to the instance volume.
    """
    filter_key = "rlnMicrographName"
    return _from_relion3_star_filtered(file_path, micrograph_name, filter_key, binning, order)


def from_tomoman_relion_star(file_path, micrograph_name, binning=1.0, order="xyz"):
    """
    Tomoman Relion3 star format convertion to position and rotation matrix
    to be applied to the instance volume.
    """
    filter_key = "rlnTomoName"
    return _from_relion3_star_filtered(file_path, micrograph_name, filter_key, binning, order)


def from_relion4_star(file_path, tomo_name, binning=1.0, order="xyz"):
    """
    Relion4 star format convertion to position and rotation matrix
    to be applied to the instance volume.
    """
    df = starfile.read(file_path)
    pixel_a = df["optics"]["rlnImagePixelSize"][0]
    df2 = df["particles"][(df["particles"]["rlnTomoName"] == tomo_name)]
    xyz_c = df2[["rlnCoordinateX", "rlnCoordinateY", "rlnCoordinateZ"]].to_numpy()
    xyz_s_a = df2[["rlnOriginXAngst", "rlnOriginYAngst", "rlnOriginZAngst"]].to_numpy()  # shift in angstrom
    positions = (xyz_c - (xyz_s_a / pixel_a)) / float(binning)
    euler_angles = df2[["rlnAngleRot", "rlnAngleTilt", "rlnAnglePsi"]].to_numpy()
    # intrinsic transformation
    rot = R.from_euler(angles=euler_angles, seq="ZYZ", degrees=True).inv().as_matrix()
    if order == "zyx":
        rot = invert_rot_matrices_axis_order(rot)
        positions = invert_positions_axis_order(positions)
    return positions, rot


def from_stopgap_star(file_path, micrograph_name, binning=1.0, order="xyz"):
    """
    STOPGAP star format convertion to position and rotation matrix
    to be applied to the instance volume.
    """
    try:
        micrograph_name = int(micrograph_name)
    except:
        pass
    df = starfile.read(file_path)
    # Looks like Pandas auto convert to micrograph_name to integer if doable
    df2 = df[(df["tomo_num"] == micrograph_name)]
    if len(df2) == 0:
        raise ValueError(f"No annotations in {file_path} for tomo {micrograph_name}")
    xyz_c = df2[["orig_x", "orig_y", "orig_z"]].to_numpy()
    xyz_s = df2[["x_shift", "y_shift", "z_shift"]].to_numpy()  # shift
    positions = (xyz_c + xyz_s) / binning
    euler_angles = df2[["phi", "the", "psi"]].to_numpy()
    # extrinsic transformation
    rot = R.from_euler(angles=euler_angles, seq="zxz", degrees=True).as_matrix()
    if order == "zyx":
        rot = invert_rot_matrices_axis_order(rot)
        positions = invert_positions_axis_order(positions)
    return positions, rot


def from_trf(file_path, mircograph_name, binning=1.0, order="xyz"):
    f = open(file_path, "r")
    lines = f.readlines()
    xyz_c = np.zeros((len(lines), 3))
    rot = np.zeros((len(lines), 3, 3))
    for i, l in enumerate(lines):
        bits = l[:-1].split(" ")
        bits = [i for i in bits if i != ""]
        c = np.array((bits[1], bits[2], bits[3]), dtype=np.float32)
        r = np.array(bits[7:], dtype=np.float32).reshape((3, 3))
        xyz_c[i, :] = c
        rot[i, :, :] = r
    if order == "zyx":
        rot = invert_rot_matrices_axis_order(rot)
        positions = invert_positions_axis_order(xyz_c)
    return positions, rot
