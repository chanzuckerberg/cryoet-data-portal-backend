from typing import Dict

import allure
import pytest
from mrcfile import utils
from mrcfile.mrcinterpreter import MrcInterpreter

# Tolerance for pixel spacing assertions
SPACING_TOLERANCE = 0.01


@pytest.mark.annotation
@pytest.mark.metadata
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestPointAnnotations:

    ### BEGIN Fixtures ###
    @pytest.fixture(autouse=True)
    def _set_info(self, dataset, run_name, voxel_spacing):
        """Set the dataset and run name for the tests."""
        self.dataset = dataset
        self.run_name = run_name
        self.voxel_spacing = voxel_spacing

    ### END Fixtures ###

    ### BEGIN Self-consistency tests ###
    @allure.title("Number of point annotations consistent between metadata and ndjson file.")
    def test_number_consistent(
        self,
        point_annotations: Dict[str, Dict[str, Dict]],
        annotation_metadata: Dict[str, Dict],
    ):
        """Check that the number of annotations is consistent between the metadata and the ndjson file."""

        for base in point_annotations:
            metadata = annotation_metadata[base]
            print(f"\nAnnotation Object: {base}\n")

            files = point_annotations[base]
            for filename, data in files.items():
                print(f"\tFile: {filename}\n")
                assert len(data) == metadata["object_count"]

    ### END Self-consistency tests ###

    ### BEGIN Tomogram-consistency tests ###
    @allure.title("All points are contained within the tomogram dimensions.")
    def test_contained_in_tomo(self, point_annotations: Dict[str, Dict[str, Dict]], canonical_tomogram_metadata: Dict):
        """Check that all points are contained within the tomogram dimensions."""

        for base, annotations in point_annotations.items():
            print(f"\nAnnotation Object: {base}\n")

            for filename, points in annotations.items():
                print(f"\tFile: {filename}\n")
                for ann in points:
                    assert 0 <= ann["location"]["x"] <= canonical_tomogram_metadata["size"]["x"] - 1
                    assert 0 <= ann["location"]["y"] <= canonical_tomogram_metadata["size"]["y"] - 1
                    assert 0 <= ann["location"]["z"] <= canonical_tomogram_metadata["size"]["z"] - 1

    ### END Tomogram-consistency tests ###


@pytest.mark.annotation
@pytest.mark.metadata
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestOrientedPointAnnotations:

    ### BEGIN Fixtures ###
    @pytest.fixture(autouse=True)
    def _set_info(self, dataset, run_name, voxel_spacing):
        """Set the dataset and run name for the tests."""
        self.dataset = dataset
        self.run_name = run_name
        self.voxel_spacing = voxel_spacing

    ### END Fixtures ###

    ### BEGIN Self-consistency tests ###
    @allure.title("Number of oriented point annotations consistent between metadata and ndjson file.")
    def test_number_consistent(
        self,
        oriented_point_annotations: Dict[str, Dict[str, Dict]],
        annotation_metadata: Dict[str, Dict],
    ):
        """Check that the number of annotations is consistent between the metadata and the ndjson file."""

        for base in oriented_point_annotations:
            metadata = annotation_metadata[base]
            print(f"\nAnnotation Object: {base}\n")

            files = oriented_point_annotations[base]
            for filename, data in files.items():
                print(f"\tFile: {filename}\n")
                assert len(data) == metadata["object_count"]

    ### END Self-consistency tests ###

    ### BEGIN Tomogram-consistency tests ###
    @allure.title("All oriented points are contained within the tomogram dimensions.")
    def test_contained_in_tomo(
        self,
        oriented_point_annotations: Dict[str, Dict[str, Dict]],
        canonical_tomogram_metadata: Dict,
    ):
        """Check that all oriented points are contained within the tomogram dimensions."""

        for base, annotations in oriented_point_annotations.items():
            print(f"\nAnnotation Object: {base}\n")

            for filename, points in annotations.items():
                print(f"\tFile: {filename}\n")
                for ann in points:
                    assert 0 <= ann["location"]["x"] <= canonical_tomogram_metadata["size"]["x"] - 1
                    assert 0 <= ann["location"]["y"] <= canonical_tomogram_metadata["size"]["y"] - 1
                    assert 0 <= ann["location"]["z"] <= canonical_tomogram_metadata["size"]["z"] - 1

    ### END Tomogram-consistency tests ###


@pytest.mark.annotation
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestSegmentationMaskHeader:
    """Validate the mrc file header for a volume annotation."""

    MAP_ID = b"MAP "
    VOLUME_SPACEGROUP = 1

    ### BEGIN Fixtures ###
    @pytest.fixture(autouse=True)
    def _set_info(self, dataset, run_name, voxel_spacing):
        """Set the dataset and run name for the tests."""
        self.dataset = dataset
        self.run_name = run_name
        self.voxel_spacing = voxel_spacing

    ### END Fixtures ###

    ### BEGIN MRC Self-consistency tests ###
    @allure.title("Annotation MRC file is a volume")
    def test_is_volume(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the mrc file is a volume."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"\nAnnotation Object: {base}\n")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}\n")
                header = interpreter.header
                assert header.ispg == self.VOLUME_SPACEGROUP

    @allure.title("Annotation mrc MAP ID is correct.")
    def test_map_id_string(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the MAP ID is correct."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"\nAnnotation Object: {base}\n")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}\n")
                header = interpreter.header
                assert header.map == self.MAP_ID

    @allure.title("Annotation mrc machine stamps are valid.")
    def test_machine_stamp(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the machine stamp is valid."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"\nAnnotation Object: {base}\n")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}\n")
                header = interpreter.header
                try:
                    utils.byte_order_from_machine_stamp(header.machst)
                except ValueError:
                    pytest.fail(f"Machine stamp is invalid: {utils.pretty_machine_stamp(header.machst)}")

    @allure.title("Annotation mrc modes are valid.")
    def test_mrc_mode(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the mrc mode is valid."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"\nAnnotation Object: {base}\n")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}\n")
                header = interpreter.header
                try:
                    utils.dtype_from_mode(header.mode)
                except ValueError:
                    pytest.fail(f"Mode is invalid: {header.mode}")

    @allure.title("Annotation mrc map dimension fields are non-negative.")
    def test_map_dimension_fields(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the map dimension fields are non-negative."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"\nAnnotation Object: {base}\n")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}\n")
                header = interpreter.header
                for field in ["nx", "ny", "nz", "mx", "my", "mz", "ispg", "nlabl"]:
                    assert header[field] >= 0

    @allure.title("Annotation mrc cell dimensions are non-negative.")
    def test_cell_dimensions(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the cell dimensions are non-negative."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"\nAnnotation Object: {base}\n")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}\n")
                header = interpreter.header
                for field in ["x", "y", "z"]:
                    assert header.cella[field] >= 0

    @allure.title("Annotation mrc nlabel is correct.")
    def test_nlabel(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the nlabel is correct."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"\nAnnotation Object: {base}\n")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}\n")
                header = interpreter.header
                count = 0
                empty_label = False
                for label in header.label:
                    if len(label.strip()) > 0:
                        count += 1

                    if len(label) != 0 and len(label.strip()) == 0:
                        empty_label = True

                assert count == header.nlabl
                assert empty_label is False

    @allure.title("Annotation mrc versions are correct.")
    def test_nversion(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the nversion is correct."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"\nAnnotation Object: {base}\n")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}\n")
                header = interpreter.header
                assert header.nversion in [20140, 20141]

    @allure.title("Annotation mrc ext types are correct.")
    def test_exttyp(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the exttyp is correct."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"\nAnnotation Object: {base}\n")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}\n")
                header = interpreter.header
                if header.nsymbt > 0:
                    assert header.exttyp in [b"CCP4", b"MRCO", b"SERI", b"AGAR", b"FEI1", b"FEI2", b"HDF5"]

    @allure.title("Voxel spacing is consistent with the anotation mrc header.")
    def test_spacing_consistent(
        self,
        seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]],
        voxel_spacing: float,
    ):
        """Check that the voxel spacing is consistent with the mrc header."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"\nAnnotation Object: {base}\n")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}\n")
                assert voxel_spacing == pytest.approx(interpreter.voxel_size["x"].astype(float), abs=SPACING_TOLERANCE)
                assert voxel_spacing == pytest.approx(interpreter.voxel_size["y"].astype(float), abs=SPACING_TOLERANCE)
                assert voxel_spacing == pytest.approx(interpreter.voxel_size["z"].astype(float), abs=SPACING_TOLERANCE)

    @allure.title("Annotation mrc axis mapping is x == col, y == row, z == sec.")
    def test_axis_mapping(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the axis mapping is x == col, y == row, z == sec."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"\nAnnotation Object: {base}\n")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}\n")
                header = interpreter.header

                # Standard axis mapping
                assert header.mapc == 1
                assert header.mapr == 2
                assert header.maps == 3

    @allure.title("Annotation mrc unit cells are valid for a volume.")
    def test_unit_cell_valid_for_3d_volume(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the unit cell is valid for a volume."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"\nAnnotation Object: {base}\n")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}\n")
                header = interpreter.header

                # Unit cell z-size is 1
                assert header.mx == header.nx
                assert header.my == header.ny
                assert header.mz == header.nz

                # Check that the unit cell angles specify cartesian system
                assert header.cellb.alpha == 90
                assert header.cellb.beta == 90
                assert header.cellb.gamma == 90

    @allure.title("Annotation mrc origins are zero.")
    def test_origin_is_zero(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the origin is zero."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"\nAnnotation Object: {base}\n")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}\n")
                header = interpreter.header

                # Origin is zero
                assert header.origin.x == 0
                assert header.origin.y == 0
                assert header.origin.z == 0

    @allure.title("Annotation mrc subimage starts are zero for a volume.")
    def test_subimage_start_is_zero(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the subimage start is zero for a volume."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"\nAnnotation Object: {base}\n")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}\n")
                header = interpreter.header

                # Subimage start is zero
                assert header.nxstart == 0
                assert header.nystart == 0
                assert header.nzstart == 0

    ### BEGIN MRC Self-consistency tests ###

    ### BEGIN Tomogram-consistency tests ###
    @allure.title("Annotation volume is contained within the canonical tomogram dimensions.")
    def test_contained_in_tomo(
        self,
        seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]],
        canonical_tomogram_metadata: Dict,
    ):
        """Check that the annotation volume is contained within the canonical tomogram dimensions."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"\nAnnotation Object: {base}\n")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}\n")
                header = interpreter.header
                assert header.nx == canonical_tomogram_metadata["size"]["x"]
                assert header.ny == canonical_tomogram_metadata["size"]["y"]
                assert header.nz == canonical_tomogram_metadata["size"]["z"]

    ### END Tomogram-consistency tests ###


# @pytest.mark.metadata
# @pytest.mark.parametrize("voxel_spacing", pytest.voxel_spacing, )
# @pytest.mark.parametrize("run_name", pytest.run_name, )
# class TestVolumeAnnotationsMeta:
#
#     ### BEGIN Fixtures ###
#     @pytest.fixture(autouse=True)
#     def _set_info(self, dataset, run_name, voxel_spacing):
#         """Set the dataset and run name for the tests."""
#         self.dataset = dataset
#         self.run_name = run_name
#         self.voxel_spacing = voxel_spacing
### END Fixtures ###

### BEGIN Self-consistency tests ###
# TODO: The segmentation mask annotation should probably have its voxel size in the metadata file?
# def test_spacing_consistent(self,
#                             mrc_annotation_metadata: Dict[str, Dict],
#                             voxel_spacing: float):
#     """Check that the voxel spacing is consistent with the metadata."""
#
#     #reset_allure.dynamic.title("Voxel spacing is consistent with the anotation metadata voxel spacing.")
#     #reset_allure.dynamic.epic(f"Dataset {self.dataset}")
#     #reset_allure.dynamic.feature(f"Run {self.run_name}")
#     #reset_allure.dynamic.story(f"Voxel spacing {self.voxel_spacing}")
#
#     for file, metadata in mrc_annotation_metadata.items():
#         print(f"\nFile: {file}\n")
#         assert voxel_spacing == metadata['voxel_spacing']
### END Self-consistency tests ###

### BEGIN Metadata to MRC-consistency tests ###
# TODO: The segmentation mask annotation should probably have its size in the metadata file?
# def test_mrc_size_consistent(self,
#                              mrc_annotation_metadata: Dict[str, Dict],
#                              mrc_annotation_headers: Dict[str, MrcInterpreter]):
#     """Check that the mrc file size is consistent with the metadata."""
#
#     #reset_allure.dynamic.title("Annotation mrc file size is consistent with the metadata.")
#     #reset_allure.dynamic.epic(f"Dataset {self.dataset}")
#     #reset_allure.dynamic.feature(f"Run {self.run_name}")
#     #reset_allure.dynamic.story(f"Voxel spacing {self.voxel_spacing}")
#
#     for base in mrc_annotation_headers.keys():
#         print(f"\nFile: {base}\n")
#         interpreter = mrc_annotation_headers[base]
#         metadata = mrc_annotation_metadata[base]
#         header = interpreter.header
#         assert header.nx == metadata['size']['x']
#         assert header.ny == metadata['size']['y']
#         assert header.nz == metadata['size']['z']
### END Metadata to MRC-consistency tests ###

### BEGIN Tomogram-consistency tests ###
### END Tomogram-consistency tests ###
