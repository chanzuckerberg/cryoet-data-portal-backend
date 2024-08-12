import base64
import logging
import typing

import numpy as np
import trimesh
import h5py

logger = logging.getLogger(__name__)


def convert_hff(input_file: str) -> typing.List[str]:
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

if __name__ == '__main__':
    convert_hff(
        '/Users/trentsmith/workspace/cryoet/cryoet-data-portal-backend/ingestion_tools/scripts/tests/fixtures'
        '/annotations/TE10.hff')
