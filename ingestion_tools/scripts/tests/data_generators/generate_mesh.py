"""
The module contains functions that can be used to generate mesh files for testing purposes.
"""

import base64

import h5py
import numpy as np
import trimesh


def generate_hff_mesh(input_file: str, output_file: str) -> None:
    """
    Generate a hff mesh file from a trimesh compatible mesh file.

    :param input_file: the path to a file that can be loaded by trimesh.
    :param output_file: the path to the output hff file that will be created
    :return:
    """
    mesh = trimesh.load(input_file, force="mesh")
    with h5py.File(output_file, "w") as fp:
        # Add the version
        fp.create_dataset("version", data="0.8.0.dev1")

        # Add the biological annotation name
        fp.create_group("segment_list/1/biological_annotation")
        fp["segment_list/1/biological_annotation"].create_dataset("name", data="special_name")

        # Add the vertices
        fp.create_group("segment_list/1/mesh_list/1/vertices")
        vertices = mesh.vertices.view(np.ndarray)
        vertices_b64 = base64.b64encode(vertices)
        fp["segment_list/1/mesh_list/1/vertices"].create_dataset("data", data=vertices_b64)
        fp["segment_list/1/mesh_list/1/vertices"].create_dataset("mode", data=vertices.dtype.name)

        # Add the triangles
        fp.create_group("segment_list/1/mesh_list/1/triangles")
        faces = mesh.faces.view(np.ndarray)
        faces_b64 = base64.b64encode(faces)
        fp["segment_list/1/mesh_list/1/triangles"].create_dataset("data", data=faces_b64)
        fp["segment_list/1/mesh_list/1/triangles"].create_dataset("mode", data=faces.dtype.name)

        # Add the colour
        fp["segment_list/1"].create_dataset("colour", data=mesh.visual.face_colors[0])


if __name__ == "__main__":
    import os

    # get test data location
    cd = os.path.dirname(__file__).split("/")[0:-1]
    test_data_location = os.path.join("/", *cd, "fixtures/annotations")

    # create the input and output file paths
    file_prefix = os.path.join(test_data_location, "triangular_mesh")
    input_file = f"{file_prefix}.glb"
    output_file = f"{file_prefix}.hff"

    # generate the hff mesh file
    generate_hff_mesh(input_file, output_file)
