import base64
import logging
import typing

import numpy as np
import trimesh

logger = logging.getLogger(__name__)


def convert_mesh_to_glb(convert_func: typing.Callable[[str], trimesh.Trimesh]) -> typing.Callable:
    """
    A decorator to convert  and scale a mesh by a given factor

    :param convert_func: the function to convert a mesh file to a trimesh object.
    """

    def wrapper(input_file: str, output_file: str, scale: float = 1.0) -> None:
        """
        Convert a mesh file to a glb file and scale it by a given factor.

        :param input_file: the path to a mesh file to convert.
        :param output_file: the name of the output file.
        :param scale: the factor to scale the mesh by.
        """
        mesh: trimesh.Trimesh = convert_func(input_file)
        mesh.apply_scale(scale) # TODO test
        mesh.export(output_file)

    return wrapper


@convert_mesh_to_glb
def from_obj(input_file: str) -> trimesh.Trimesh:
    """
    Convert an obj file to a glb file. More information about this format can be found
    here: https://en.wikipedia.org/wiki/Wavefront_.obj_file

    :param input_file: the path to an obj file.
    :return: the converted mesh as a trimesh object.
    """
    return trimesh.load(input_file)


@convert_mesh_to_glb
def from_stl(input_file: str):
    """
    Convert an stl file to a glb file.

    :param input_file: the path to an stl file.
    :return: the converted mesh as a trimesh object.
    """
    return trimesh.load(input_file)


@convert_mesh_to_glb
def from_vtk(input_file: str) -> trimesh.Trimesh:
    """
    Convert an vtk file to a glb file. More information about this format can be found
       vtk -(vtk)-> stl -(trimesh)-> glb
    :param input_file: the path to an vtk file.
    :return: the converted mesh as a trimesh object.

    meshio or vtk?
    meshio
    - has a lot of starts and forks on github,
    - it was last updated 7 months ago
    - only one primary contributor.
    - MIT license

    vtk
    - license BSD License (BSD)
    - back by and organization Kitware
    - for activitiy stats https://openhub.net/p/vtk. It still has a lot of activity.

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
