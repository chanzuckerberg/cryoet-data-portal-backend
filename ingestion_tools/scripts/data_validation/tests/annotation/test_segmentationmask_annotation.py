from typing import Dict, List

import numpy as np
import pytest
import zarr
from base_annotation import BaseAnnotation
from mrcfile import utils
from mrcfile.mrcinterpreter import MrcInterpreter


@pytest.mark.annotation
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestSegmentationMaskHeader(BaseAnnotation):
    MAP_ID = b"MAP "
    VOLUME_SPACEGROUP = 1
    # Tolerance for voxel spacing assertions
    SPACING_TOLERANCE = 0.01

    """Validate the mrc file header for a volume annotation."""

    ### BEGIN MRC Self-consistency tests ###
    def test_is_volume(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the mrc file is a volume."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"Annotation Object: {base}")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}")
                header = interpreter.header
                assert header.ispg == self.VOLUME_SPACEGROUP

    def test_map_id_string(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the MAP ID is correct."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"Annotation Object: {base}")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}")
                header = interpreter.header
                assert header.map == self.MAP_ID

    def test_machine_stamp(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the machine stamp is valid."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"Annotation Object: {base}")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}")
                header = interpreter.header
                try:
                    utils.byte_order_from_machine_stamp(header.machst)
                except ValueError:
                    pytest.fail(f"Machine stamp is invalid: {utils.pretty_machine_stamp(header.machst)}")

    def test_mrc_mode(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the mrc mode is valid."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"Annotation Object: {base}")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}")
                header = interpreter.header
                try:
                    assert utils.dtype_from_mode(header.mode) == np.int8
                except ValueError:
                    pytest.fail(f"Mode is invalid: {header.mode}")

    def test_map_dimension_fields(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the map dimension fields are non-negative."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"Annotation Object: {base}")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}")
                header = interpreter.header
                for field in ["nx", "ny", "nz", "mx", "my", "mz", "ispg", "nlabl"]:
                    assert header[field] >= 0

    def test_cell_dimensions(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the cell dimensions are non-negative and match the voxel size."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"Annotation Object: {base}")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}")
                header = interpreter.header
                assert header.cella.x >= 0 and header.cella.x == pytest.approx(
                    header.mx * interpreter.voxel_size["x"].astype(float),
                )
                assert header.cella.y >= 0 and header.cella.y == pytest.approx(
                    header.my * interpreter.voxel_size["y"].astype(float),
                )
                assert header.cella.z >= 0 and header.cella.z == pytest.approx(
                    header.mz * interpreter.voxel_size["z"].astype(float),
                )

    def test_nlabel(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the nlabel is correct."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"Annotation Object: {base}")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}")
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

    def test_nversion(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the nversion is correct."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"Annotation Object: {base}")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}")
                header = interpreter.header
                assert header.nversion in [20140, 20141]

    def test_exttyp(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the exttyp is correct."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"Annotation Object: {base}")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}")
                header = interpreter.header
                if header.nsymbt > 0:
                    assert header.exttyp in [b"CCP4", b"MRCO", b"SERI", b"AGAR", b"FEI1", b"FEI2", b"HDF5"]
                assert (
                    header.nsymbt == 0
                    and interpreter.extended_header is None
                    or header.nsymbt == interpreter.extended_header.nbytes
                )

    def test_spacing_consistent(
        self,
        seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]],
        voxel_spacing: float,
    ):
        """Check that the voxel spacing is consistent with the mrc header."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"Annotation Object: {base}")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}")
                assert voxel_spacing == pytest.approx(
                    interpreter.voxel_size["x"].astype(float),
                    abs=self.SPACING_TOLERANCE,
                )
                assert voxel_spacing == pytest.approx(
                    interpreter.voxel_size["y"].astype(float),
                    abs=self.SPACING_TOLERANCE,
                )
                assert voxel_spacing == pytest.approx(
                    interpreter.voxel_size["z"].astype(float),
                    abs=self.SPACING_TOLERANCE,
                )

    def test_axis_mapping(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the axis mapping is x == col, y == row, z == sec."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"Annotation Object: {base}")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}")
                header = interpreter.header

                # Standard axis mapping
                assert header.mapc == 1
                assert header.mapr == 2
                assert header.maps == 3

    def test_unit_cell_valid_for_3d_volume(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the unit cell is valid for a volume."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"Annotation Object: {base}")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}")
                header = interpreter.header

                # Unit cell z-size is 1
                assert header.mx == header.nx
                assert header.my == header.ny
                assert header.mz == header.nz

                # Check that the unit cell angles specify cartesian system
                assert header.cellb.alpha == 90
                assert header.cellb.beta == 90
                assert header.cellb.gamma == 90

    def test_origin_is_zero(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the origin is zero."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"Annotation Object: {base}")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}")
                header = interpreter.header

                # Origin is zero
                assert header.origin.x == 0
                assert header.origin.y == 0
                assert header.origin.z == 0

    def test_subimage_start_is_zero(self, seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]]):
        """Check that the subimage start is zero for a volume."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"Annotation Object: {base}")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}")
                header = interpreter.header

                # Subimage start is zero
                assert header.nxstart == 0
                assert header.nystart == 0
                assert header.nzstart == 0

    ### END MRC Self-consistency tests ###

    ### BEGIN ZARR Self-consistency tests ###
    def test_zarr_info(self, seg_mask_annotation_zarr_files: Dict[str, List[str]]):
        for base, files in seg_mask_annotation_zarr_files.items():
            print(f"Annotation Object: {base}")

            for file in files:
                print(f"\tFile: {file}")
                with zarr.open(file, mode="r") as z:
                    assert ("Type", "zarr.hierarchy.Group") in z.info.items
                    assert ("No. groups", 0) in z.info.items
                    assert ("No. arrays", 3) in z.info.items
                    assert ("Arrays", "0, 1, 2") in z.info.items

    def test_zarr_voxel_spacing(self, seg_mask_annotation_zarr_files: Dict[str, List[str]], voxel_spacing: float):
        for base, files in seg_mask_annotation_zarr_files.items():
            print(f"Annotation Object: {base}")

            for file in files:
                print(f"\tFile: {file}")
                with zarr.open(file, mode="r") as z:
                    for i in range(3):
                        datasets_entry = z.attrs.asdict()["multiscales"][0]["datasets"][i]
                        assert datasets_entry["coordinateTransformations"][0]["scale"] == [voxel_spacing * (2**i)] * 3
                        assert datasets_entry["path"] == str(i)

    def test_zarr_data_type(self, seg_mask_annotation_zarr_files: Dict[str, List[str]]):
        for base, files in seg_mask_annotation_zarr_files.items():
            print(f"Annotation Object: {base}")

            for file in files:
                print(f"\tFile: {file}")
                with zarr.open(file, mode="r") as z:
                    for i in range(3):
                        assert z[str(i)].dtype == np.int8

    ### BEGIN Tomogram-consistency tests ###
    def test_contained_in_tomo(
        self,
        seg_mask_annotation_mrc_headers: Dict[str, Dict[str, MrcInterpreter]],
        canonical_tomogram_metadata: Dict,
    ):
        """Check that the annotation volume is contained within the canonical tomogram dimensions."""

        for base, annotations in seg_mask_annotation_mrc_headers.items():
            print(f"Annotation Object: {base}")
            for filename, interpreter in annotations.items():
                print(f"\tFile: {filename}")
                header = interpreter.header
                assert header.nx == canonical_tomogram_metadata["size"]["x"]
                assert header.ny == canonical_tomogram_metadata["size"]["y"]
                assert header.nz == canonical_tomogram_metadata["size"]["z"]

    ### END Tomogram-consistency tests ###
