import base64
import logging
import typing

import h5py
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


def hff_output_files(input_file: str) -> typing.List[str]:
    output_files = []
    with h5py.File(input_file, 'r') as fp:
        # All the meshes are stored in the 'segment_list'
        logger.info(f"Schema version: {fp['version'][()]}")
        for mesh_list in fp['segment_list/'].keys():
            # Mesh name
            mesh_name_raw: bytes = fp[f"segment_list/{mesh_list}/biological_annotation/name"][()]
            if not mesh_name_raw:
                raise ValueError("No mesh name found at segment_list/{mesh_list} in the hff file")
            else:
                output_file: str = mesh_name_raw.decode()
                if output_file in output_files:
                    raise ValueError(f"Duplicate mesh name found: {output_file}")
    return output_files

@convert_mesh_to_glb
def from_hff(input_file: str) -> typing.List[str]:
    """
    Convert an hff file to one or more glb file. More information about this format can be found
    here: https://emdb-empiar.github.io/EMDB-SFF/

    Each group mesh in the hff file is stored as a separate glb file. The name of the mesh file is the biological
    annotation name suffixed with '.glb'.

    :param input_file: the path to an hff file.
    :return: A list of meshes with the file extension .glb
    """

    def _extract(_f, path) -> np.ndarray:
        data_path = f'{path}/data'
        # The data is stored as a string of base64 encoded bytes, so we need to decode them
        data = base64.b64decode(fp[data_path][()])

        mode_path = f'{path}/mode'
        mode = fp[mode_path][()].decode('utf-8')
        dtype = getattr(np, mode)

        return np.frombuffer(data, dtype=dtype).reshape(-1, 3)

    output_files = []

    # Open the HDF5 file
    with h5py.File(input_file, 'r') as fp:
        # All the meshes are stored in the 'segment_list'
        logger.info(f"Schema version: {fp['version'][()]}")
        for mesh_list in fp['segment_list/'].keys():
            # Mesh name
            mesh_name_raw: bytes = fp[f"segment_list/{mesh_list}/biological_annotation/name"][()]
            if not mesh_name_raw:
                raise ValueError("No mesh name found at segment_list/{mesh_list} in the hff file")
            else:
                mesh_name: str = mesh_name_raw.decode() + '.glb'
                if mesh_name in output_files:
                    raise ValueError(f"Duplicate mesh name found: {mesh_name}")
            logger.info(f"Processing mesh: {mesh_name}")
            # Color is a 4-tuple of RGBA values, 0-1 range (normalized from 0-255)
            color = fp[f'segment_list/{mesh_list}/colour'][()]
            meshes = []
            for mesh in fp[f'segment_list/{mesh_list}/mesh_list/'].keys():
                # Create a trimesh object from the vertices and triangles data
                triangle_path = f'segment_list/{mesh_list}/mesh_list/{mesh}/triangles'
                triangles = _extract(fp, triangle_path)

                # Do the same for the vertices
                vertices_data_path = f'segment_list/{mesh_list}/mesh_list/{mesh}/vertices'
                vertices = _extract(fp, vertices_data_path)

                # Create a trimesh object from the vertices and triangles data
                mesh = trimesh.Trimesh(vertices=vertices, faces=triangles, face_colors=color)
                meshes.append(mesh)

            # Combine all the meshes into a single scene and export it as a GLB file
            concat_meshes = trimesh.util.concatenate(meshes)
            scene = trimesh.Scene(concat_meshes)
            output_files.append(mesh_name)
            scene.export(mesh_name)
    return output_files

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


if __name__ == '__main__':
    from_hff(
        '/Users/trentsmith/workspace/cryoet/cryoet-data-portal-backend/ingestion_tools/scripts/tests/fixtures'
        '/annotations/TE10.hff')
    # convert_stl("/Users/trentsmith/workspace/cryoet/cryoet-data-portal-backend/ingestion_tools/scripts/tests
    # /fixtures/annotations/Endospore.stl")
