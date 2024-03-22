import csv
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class InstancePoint:
    x_coord: float
    y_coord: float
    z_coord: float
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


def instances_from_csv(
    local_file: str,
    filter_key: str,
    binning: float = 1,
    axis_columns: Tuple[int, int, int] = (0, 1, 2),
    id_column: int = 3,
    skip_header: bool = False,
) -> List[InstancePoint]:
    points = []

    with open(local_file, "r") as f:
        reader = csv.reader(f)
        # Skip header.
        next(reader)
        for row in reader:
            points.append(
                InstancePoint(
                    x_coord=float(row[axis_columns[0]]) / binning,
                    y_coord=float(row[axis_columns[1]]) / binning,
                    z_coord=float(row[axis_columns[2]]) / binning,
                    ID=int(row[id_column]),
                ),
            )

    return points


def from_tardis(
    local_file: str,
    filter_key: str,
    binning: float = 1,
    order: str = "xyz",
) -> List[InstancePoint]:
    return instances_from_csv(local_file, filter_key, binning, skip_header=True, axis_columns=(1, 2, 3), id_column=0)
