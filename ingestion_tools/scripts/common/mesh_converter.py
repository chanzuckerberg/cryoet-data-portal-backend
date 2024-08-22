import logging
import typing

import numpy as np
import trimesh
from trimesh import load as trimesh_load

logger = logging.getLogger(__name__)


def convert_mesh_to_glb(convert_func: typing.Callable[[str], trimesh.Trimesh]) -> typing.Callable:
    """
    A decorator to convert and scale a mesh by a given factor

    :param convert_func: the function to convert a mesh file to a trimesh object.
    """

    def wrapper(input_file: str, output_file: str, scale_factor: float = 1.0) -> None:
        """
        Convert a mesh file to a glb file and scale it by a given factor.

        :param input_file: the path to a mesh file to convert.
        :param output_file: the name of the output file.
        :param scale_factor: the factor to scale the mesh by.
        """
        mesh: trimesh.Trimesh = convert_func(input_file)
        mesh.apply_scale(scale_factor)
        mesh.export(output_file)

    return wrapper


@convert_mesh_to_glb
def from_generic(input_file: str) -> trimesh.Trimesh:
    """
    Load a mesh file into a trimesh object.

    Supports the following formats:
    - obj: https://en.wikipedia.org/wiki/Wavefront_.obj_file
    - stl: https://en.wikipedia.org/wiki/STL_(file_format)
    - glb: https://en.wikipedia.org/wiki/GlTF

    :param input_file: the path to a mesh file.
    :return: the mesh loaded into a trimesh object.
    """
    return trimesh_load(input_file)


@convert_mesh_to_glb
def from_vtk(input_file: str) -> trimesh.Trimesh:
    """
    Load a vtk file into a trimesh object.. More information about this format can be found
    here https://en.wikipedia.org/wiki/VTK

    :param input_file: the path to a vtk file.
    :return: the mesh loaded into a trimesh object.
    """
    import vtk

    def read_vtk(file_path):
        reader = vtk.vtkPolyDataReader()
        reader.SetFileName(file_path)
        reader.Update()
        return reader.GetOutput()

    def vtk_to_trimesh(vtk_data):
        points = vtk_data.GetPoints()
        vertices = np.array([points.GetPoint(i) for i in range(points.GetNumberOfPoints())])

        faces = []
        for i in range(vtk_data.GetNumberOfCells()):
            cell = vtk_data.GetCell(i)
            face = [cell.GetPointId(j) for j in range(cell.GetNumberOfPoints())]
            faces.append(face)

        return trimesh.Trimesh(vertices=vertices, faces=faces)

    vkt_data = read_vtk(input_file)
    mesh = vtk_to_trimesh(vkt_data)
    return mesh
