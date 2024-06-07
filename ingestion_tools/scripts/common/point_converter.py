"""
Various conversion of euler angle to rotation matrix
"""

import contextlib
import csv
import os
from dataclasses import dataclass
from typing import List, Tuple, Union

import imodmodel
import numpy as np
import starfile
from scipy.spatial.transform import Rotation


@dataclass
class Point:
    x_coord: float
    y_coord: float
    z_coord: float

    def to_dict(self):
        return {
            "type": "point",
            "location": {
                "x": self.x_coord,
                "y": self.y_coord,
                "z": self.z_coord,
            },
        }


@dataclass
class OrientedPoint(Point):
    rot_matrix: np.ndarray

    def to_dict(self):
        return {
            "type": "orientedPoint",
            "location": {
                "x": self.x_coord,
                "y": self.y_coord,
                "z": self.z_coord,
            },
            "xyz_rotation_matrix": self.rot_matrix.tolist(),
        }


@dataclass
class InstancePoint(Point):
    ID: int

    def to_dict(self):
        return {
            "type": "instancePoint",
            "location": {
                "x": self.x_coord,
                "y": self.y_coord,
                "z": self.z_coord,
            },
            "instance_id": self.ID,
        }


AXIS_ORDER = {"xyz": (0, 1, 2), "zyx": (2, 1, 0)}
MATRIX_TRANSFORM = {"xyz": lambda x: x, "zyx": np.flip}


def _from_csv(
    local_file: str,
    filter_value: str = "",
    binning: float = 1,
    axis_columns: Tuple[int, int, int] = (0, 1, 2),
    id_column: int = 3,
    skip_header: bool = False,
    delimiter: str = ",",
    instance_point: bool = False,
) -> List[Union[Point, InstancePoint]]:
    points = []

    with open(local_file, "r") as f:
        reader = csv.reader(f, delimiter=delimiter)

        # Skip header.
        if skip_header:
            next(reader)

        for row in reader:
            if instance_point:
                points.append(
                    InstancePoint(
                        x_coord=float(row[axis_columns[0]]) / binning,
                        y_coord=float(row[axis_columns[1]]) / binning,
                        z_coord=float(row[axis_columns[2]]) / binning,
                        ID=int(row[id_column]),
                    ),
                )
            else:
                points.append(
                    Point(
                        x_coord=float(row[axis_columns[0]]) / binning,
                        y_coord=float(row[axis_columns[1]]) / binning,
                        z_coord=float(row[axis_columns[2]]) / binning,
                    ),
                )

    return points


def from_csv(
    local_file: Union[str, os.PathLike],
    filter_value: str = "",
    binning: float = 1.0,
    order: str = "xyz",
    delimiter: str = ",",
) -> List[Point]:
    return _from_csv(
        local_file,
        filter_value=filter_value,
        binning=binning,
        skip_header=False,
        axis_columns=AXIS_ORDER[order],
        delimiter=delimiter,
        instance_point=False,
    )


def from_csv_with_header(
    local_file: Union[str, os.PathLike],
    filter_value: str = "",
    binning: float = 1.0,
    order: str = "xyz",
    delimiter: str = ",",
) -> List[Point]:
    return _from_csv(
        local_file,
        filter_value=filter_value,
        binning=binning,
        skip_header=True,
        axis_columns=AXIS_ORDER[order],
        delimiter=delimiter,
        instance_point=False,
    )


def from_tardis(
    local_file: Union[str, os.PathLike],
    filter_value: str,
    binning: float = 1,
    order: str = "xyz",
) -> List[InstancePoint]:
    return _from_csv(
        local_file,
        filter_value=filter_value,
        binning=binning,
        skip_header=True,
        axis_columns=(1, 2, 3),
        id_column=0,
        delimiter=",",
        instance_point=True,
    )


def from_mod(
    local_file: Union[str, os.PathLike],
    filter_value: str = "",
    binning: float = 1.0,
    order="xyz",
    delimiter: str = None,
) -> List[Point]:
    """Read IMOD model file and convert to list of points."""

    axis_order = AXIS_ORDER[order]

    model = imodmodel.read(local_file)

    points = []
    for _, row in model.iterrows():
        coords = (row["x"], row["y"], row["z"])
        points.append(
            Point(
                x_coord=coords[axis_order[0]] / binning,
                y_coord=coords[axis_order[1]] / binning,
                z_coord=coords[axis_order[2]] / binning,
            ),
        )

    return points


def from_trf(
    local_file: Union[str, os.PathLike],
    micrograph_name: str = "",
    binning: float = 1.0,
    order: str = "xyz",
) -> List[OrientedPoint]:
    """Read TRF file and convert to list of points."""

    axis_order = AXIS_ORDER[order]
    matrix_transform = MATRIX_TRANSFORM[order]

    with open(local_file, "r") as f:
        lines = f.readlines()

    points = []

    for j in lines:
        bits = j[:-1].split(" ")
        bits = [i for i in bits if i != ""]
        coords = np.array((bits[1], bits[2], bits[3]), dtype=np.float32)
        rot = np.array(bits[7:], dtype=np.float32).reshape((3, 3))

        points.append(
            OrientedPoint(
                x_coord=coords[axis_order[0]] / binning,
                y_coord=coords[axis_order[1]] / binning,
                z_coord=coords[axis_order[2]] / binning,
                rot_matrix=matrix_transform(rot),
            ),
        )

    return points


def from_stopgap_star(
    local_file: Union[str, os.PathLike],
    filter_value: str,
    binning: float = 1.0,
    order: str = "xyz",
) -> List[OrientedPoint]:
    """
    STOPGAP star format convertion to position and rotation matrix
    to be applied to the instance volume.
    """

    axis_order = AXIS_ORDER[order]
    matrix_transform = MATRIX_TRANSFORM[order]

    with contextlib.suppress(Exception):
        filter_value = int(filter_value)

    df = starfile.read(local_file)

    # Looks like Pandas auto convert to micrograph_name to integer if doable
    df2 = df[(df["tomo_num"] == filter_value)]

    if len(df2) == 0:
        raise ValueError(f"No annotations in {local_file} for tomo {filter_value}")

    xyz_c = df2[["orig_x", "orig_y", "orig_z"]].to_numpy()
    xyz_s = df2[["x_shift", "y_shift", "z_shift"]].to_numpy()  # shift
    positions = (xyz_c + xyz_s) / binning
    euler_angles = df2[["phi", "the", "psi"]].to_numpy()

    points = []
    for i in range(len(df2)):
        points.append(
            OrientedPoint(
                x_coord=positions[i, axis_order[0]],
                y_coord=positions[i, axis_order[1]],
                z_coord=positions[i, axis_order[2]],
                rot_matrix=matrix_transform(
                    Rotation.from_euler(angles=euler_angles[i], seq="zxz", degrees=True).as_matrix(),
                ),
            ),
        )

    return points


def from_relion4_star(
    local_file: Union[str, os.PathLike],
    filter_value: str,
    binning: float = 1.0,
    order: str = "xyz",
) -> List[OrientedPoint]:
    """
    Relion4 star format convertion to position and rotation matrix
    to be applied to the instance volume.
    """

    axis_order = AXIS_ORDER[order]
    matrix_transform = MATRIX_TRANSFORM[order]

    df = starfile.read(local_file)

    pixel_a = df["optics"]["rlnImagePixelSize"][0]
    df2 = df["particles"][(df["particles"]["rlnTomoName"] == filter_value)]
    xyz_c = df2[["rlnCoordinateX", "rlnCoordinateY", "rlnCoordinateZ"]].to_numpy()
    xyz_s_a = df2[["rlnOriginXAngst", "rlnOriginYAngst", "rlnOriginZAngst"]].to_numpy()  # shift in angstrom
    positions = (xyz_c - (xyz_s_a / pixel_a)) / float(binning)
    euler_angles = df2[["rlnAngleRot", "rlnAngleTilt", "rlnAnglePsi"]].to_numpy()

    points = []
    for i in range(len(df2)):
        points.append(
            OrientedPoint(
                x_coord=positions[i, axis_order[0]],
                y_coord=positions[i, axis_order[1]],
                z_coord=positions[i, axis_order[2]],
                rot_matrix=matrix_transform(
                    Rotation.from_euler(angles=euler_angles[i], seq="ZYZ", degrees=True).as_matrix(),
                ),
            ),
        )

    return points


def _from_relion3_star_filtered(
    local_file: Union[str, os.PathLike],
    filter_value: str,
    filter_key: str = "rlnMicrographName",
    binning: float = 1.0,
    order: str = "xyz",
):
    """
    Filter Relion3 star file according to filter_value and filter_key
    and then convert to position and rotation matrix
    to be applied to the instance volume.
    """

    axis_order = AXIS_ORDER[order]
    matrix_transform = MATRIX_TRANSFORM[order]

    df = starfile.read(local_file)
    df2 = df[df[filter_key] == filter_value] if filter_value else df
    xyz_c = df2[["rlnCoordinateX", "rlnCoordinateY", "rlnCoordinateZ"]].to_numpy()

    try:
        xyz_s = df2[["rlnOriginX", "rlnOriginY", "rlnOriginZ"]].to_numpy()  # shift
        positions = (xyz_c - xyz_s) / float(binning)
    except Exception:
        # do not have origin (shift)
        positions = xyz_c / float(binning)

    euler_angles = df2[["rlnAngleRot", "rlnAngleTilt", "rlnAnglePsi"]].to_numpy()

    points = []
    for i in range(len(df2)):
        points.append(
            OrientedPoint(
                x_coord=positions[i, axis_order[0]],
                y_coord=positions[i, axis_order[1]],
                z_coord=positions[i, axis_order[2]],
                rot_matrix=matrix_transform(
                    Rotation.from_euler(angles=euler_angles[i], seq="ZYZ", degrees=True).as_matrix(),
                ),
            ),
        )

    return points


def from_relion3_star(
    file_path: Union[str, os.PathLike],
    filter_value: str,
    binning: float = 1.0,
    order: str = "xyz",
) -> List[OrientedPoint]:
    """
    Relion3 star format convertion to position and rotation matrix
    to be applied to the instance volume.
    """
    filter_key = "rlnMicrographName"
    return _from_relion3_star_filtered(file_path, filter_value, filter_key, binning, order)


def from_tomoman_relion_star(
    file_path: Union[str, os.PathLike],
    filter_value: str,
    binning: float = 1.0,
    order: str = "xyz",
) -> List[OrientedPoint]:
    """
    Tomoman Relion3 star format convertion to position and rotation matrix
    to be applied to the instance volume.
    """
    filter_key = "rlnTomoName"
    return _from_relion3_star_filtered(file_path, filter_value, filter_key, binning, order)
