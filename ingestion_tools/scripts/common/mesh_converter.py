import base64
import logging
import typing

import h5py
import numpy as np
import trimesh
from trimesh import load as trimesh_load

logger = logging.getLogger(__name__)


def convert_mesh_to_glb(convert_func: typing.Callable[[str], trimesh.Trimesh]) -> typing.Callable:
    """
    A decorator to convert and scale a mesh by a given factor

    :param convert_func: the function to convert a mesh file to a trimesh object.
    """

    def wrapper(input_file: str, output_file: str, scale_factor: float = 1.0, *args, **kwargs) -> None:
        """
        Convert a mesh file to a glb file and scale it by a given factor.

        :param input_file: the path to a mesh file to convert.
        :param output_file: the name of the output file.
        :param scale_factor: the factor to scale the mesh by.
        """
        mesh: trimesh.Trimesh = convert_func(input_file, *args, **kwargs)
        mesh.apply_scale(scale_factor)
        mesh.export(output_file)

    return wrapper


def check_mesh_name(input_file: str, name: str) -> str:
    with h5py.File(input_file, "r") as fp:
        for mesh_list in fp["segment_list/"].key:
            # Mesh name
            mesh_name_raw: bytes = fp[f"segment_list/{mesh_list}/biological_annotation/name"][()]
            if not mesh_name_raw:
                logger.warning("No mesh name found at segment_list/{mesh_list} in the hff file")
            else:
                mesh_name: str = mesh_name_raw.decode()
                if mesh_name == name:
                    return mesh_list
        raise ValueError(f"Mesh name {name} not found in the hff file")


@convert_mesh_to_glb
def from_hff(input_file: str, name: str) -> trimesh.Trimesh:
    """
    Convert an hff file to one or more glb file. More information about this format can be found
    here: https://emdb-empiar.github.io/EMDB-SFF/

    Each group mesh in the hff file is stored as a separate glb file. The name of the mesh file is the biological
    annotation name suffixed with '.glb'.

    :param input_file: the path to an hff file.
    :param name: the name of the mesh to extract. The name is the biological annotation name.
    :return: A list of meshes with the file extension .glb
    """

    def _extract(_f, path) -> np.ndarray:
        data_path = f"{path}/data"
        # The data is stored as a string of base64 encoded bytes, so we need to decode them
        data = base64.b64decode(fp[data_path][()])

        mode_path = f"{path}/mode"
        mode = fp[mode_path][()].decode("utf-8")
        dtype = getattr(np, mode)

        return np.frombuffer(data, dtype=dtype).reshape(-1, 3)

    mesh_index = check_mesh_name(input_file, name)
    # Open the HDF5 file
    with h5py.File(input_file, "r") as fp:
        # All the meshes are stored in the 'segment_list'Explore & Visualize HDF5 Files
        logger.info(f"Schema version: {fp['version'][()]}")  # noqa
        # Mesh name
        logger.info(f"Processing mesh: {name}")  # noqa
        # Color is a 4-tuple of RGBA values, 0-1 range (normalized from 0-255)
        color = fp[f"segment_list/{mesh_index}/colour"][()]
        meshes = []
        for mesh in fp[f"segment_list/{mesh_index}/mesh_list/"].key:
            # Create a trimesh object from the vertices and triangles data
            triangle_path = f"segment_list/{mesh_index}/mesh_list/{mesh}/triangles"
            triangles = _extract(fp, triangle_path)

            # Do the same for the vertices
            vertices_data_path = f"segment_list/{mesh_index}/mesh_list/{mesh}/vertices"
            vertices = _extract(fp, vertices_data_path)

            # Create a trimesh object from the vertices and triangles data
            mesh = trimesh.Trimesh(vertices=vertices, faces=triangles, face_colors=color)
            meshes.append(mesh)

        # Combine all the meshes into a single mesh
        concat_meshes = trimesh.util.concatenate(meshes)  # hff color is cause an issue
    return concat_meshes


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
