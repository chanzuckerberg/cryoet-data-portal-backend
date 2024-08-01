from typing import Dict

import allure
import pytest
from mrcfile import utils
from mrcfile.mrcinterpreter import MrcInterpreter

# Tolerance for pixel spacing assertions
SPACING_TOLERANCE = 0.01


@pytest.mark.tomogram
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestCanonicalTomogramHeader:
    """Validate the mrc file header for a tomogram."""

    MAP_ID = b"MAP "
    VOLUME_SPACEGROUP = 1

    @pytest.fixture(autouse=True)
    def _set_info(self, dataset, run_name, voxel_spacing):
        """Set the dataset and run name for the tests."""
        self.dataset = dataset
        self.run_name = run_name
        self.voxel_spacing = voxel_spacing

    @allure.title("Check that the mrc files are volumes.")
    def test_is_volume(self, canonical_tomo_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the mrc file is a volume."""

        for file, interpreter in canonical_tomo_mrc_headers.items():
            print(f"\nFile: {file}\n")
            interpreter.validate()
            header = interpreter.header
            assert header.ispg == self.VOLUME_SPACEGROUP

    @allure.title("Tomo MAP IDs are correct.")
    def test_map_id_string(self, canonical_tomo_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the MAP ID is correct."""

        for file, interpreter in canonical_tomo_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header
            assert header.map == self.MAP_ID

    @allure.title("Tomo machine stamps are valid.")
    def test_machine_stamp(self, canonical_tomo_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the machine stamp is valid."""

        for file, interpreter in canonical_tomo_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header
            try:
                utils.byte_order_from_machine_stamp(header.machst)
            except ValueError:
                pytest.fail(f"Machine stamp is invalid: {utils.pretty_machine_stamp(header.machst)}")

    @allure.title("Tomo MRC modes are valid.")
    def test_mrc_mode(self, canonical_tomo_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the mrc mode is valid."""

        for file, interpreter in canonical_tomo_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header
            try:
                utils.dtype_from_mode(header.mode)
            except ValueError:
                pytest.fail(f"Mode is invalid: {header.mode}")

    @allure.title("Tomo map dimension fields are non-negative.")
    def test_map_dimension_fields(self, canonical_tomo_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the map dimension fields are non-negative."""

        for file, interpreter in canonical_tomo_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header
            for field in ["nx", "ny", "nz", "mx", "my", "mz", "ispg", "nlabl"]:
                assert header[field] >= 0

    @allure.title("Tomo cell dimensions are non-negative.")
    def test_cell_dimensions(self, canonical_tomo_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the cell dimensions are non-negative."""

        for file, interpreter in canonical_tomo_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header
            for field in ["x", "y", "z"]:
                assert header.cella[field] >= 0

    @allure.title("Tomo labels are valid.")
    def test_nlabel(self, canonical_tomo_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the nlabel are valid."""

        for file, interpreter in canonical_tomo_mrc_headers.items():
            print(f"\nFile: {file}\n")
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

    @allure.title("Tomo MRC version is correct.")
    def test_nversion(self, canonical_tomo_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the nversion is correct."""

        for file, interpreter in canonical_tomo_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header
            assert header.nversion in [20140, 20141]

    @allure.title("Tomo MRC ext type is valid.")
    def test_exttyp(self, canonical_tomo_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the exttyp is valid."""

        for file, interpreter in canonical_tomo_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header
            if header.nsymbt > 0:
                assert header.exttyp in [b"CCP4", b"MRCO", b"SERI", b"AGAR", b"FEI1", b"FEI2", b"HDF5"]

    @allure.title("Voxel spacing is consistent with tomo MRC header.")
    def test_spacing_consistent(self, canonical_tomo_mrc_headers: Dict[str, MrcInterpreter], voxel_spacing: float):
        """Check that the voxel spacing is consistent with the mrc header."""

        for file, interpreter in canonical_tomo_mrc_headers.items():
            print(f"\nFile: {file}\n")
            assert voxel_spacing == pytest.approx(interpreter.voxel_size["x"].astype(float), abs=SPACING_TOLERANCE)
            assert voxel_spacing == pytest.approx(interpreter.voxel_size["y"].astype(float), abs=SPACING_TOLERANCE)
            assert voxel_spacing == pytest.approx(interpreter.voxel_size["z"].astype(float), abs=SPACING_TOLERANCE)

    @allure.title("Tomo axis mapping is x == col, y == row, z == sec.")
    def test_axis_mapping(self, canonical_tomo_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the axis mapping is x == col, y == row, z == sec."""

        for file, interpreter in canonical_tomo_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header

            # Standard axis mapping
            assert header.mapc == 1
            assert header.mapr == 2
            assert header.maps == 3

    @allure.title("Tomo unit cell is valid for a 3D volume.")
    def test_unit_cell_valid_for_3d_volume(self, canonical_tomo_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the unit cell is valid for a volume."""

        for file, interpreter in canonical_tomo_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header

            # Unit cell z-size is 1
            assert header.mx == header.nx
            assert header.my == header.ny
            assert header.mz == header.nz

            # Check that the unit cell angles specify cartesian system
            assert header.cellb.alpha == 90
            assert header.cellb.beta == 90
            assert header.cellb.gamma == 90

    @allure.title("Tomo origin is zero for a 3D volume.")
    def test_origin_is_zero(self, canonical_tomo_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the origin is zero for a volume."""

        for file, interpreter in canonical_tomo_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header

            # Origin is zero
            assert header.origin.x == 0
            assert header.origin.y == 0
            assert header.origin.z == 0

    @allure.title("Tomo subimage start is zero for a 3D volume.")
    def test_subimage_start_is_zero(self, canonical_tomo_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the subimage start is zero for a volume."""

        for file, interpreter in canonical_tomo_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header

            # Subimage start is zero
            assert header.nxstart == 0
            assert header.nystart == 0
            assert header.nzstart == 0


@pytest.mark.tomogram
@pytest.mark.metadata
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestCanonicalTomogramMeta:

    ### BEGIN Fixtures ###
    @pytest.fixture(autouse=True)
    def _set_info(self, dataset, run_name, voxel_spacing):
        """Set the dataset and run name for the tests."""
        self.dataset = dataset
        self.run_name = run_name
        self.voxel_spacing = voxel_spacing

    ### END Fixtures ###

    ### BEGIN Metadata self-consistency tests ###
    @allure.title("Voxel spacing is consistent with tomo metadata.")
    def test_spacing_consistent(self, canonical_tomogram_metadata: Dict, voxel_spacing: float):
        """Check that the voxel spacing is consistent with the metadata."""

        assert voxel_spacing == canonical_tomogram_metadata["voxel_spacing"]

    ### END Metadata self-consistency tests ###

    ### BEGIN Metadata to MRC-consistency tests ###
    @allure.title("Tomo MRC size is consistent with tomo metadata.")
    def test_mrc_size_consistent(
        self,
        canonical_tomogram_metadata: Dict,
        canonical_tomo_mrc_headers: Dict[str, MrcInterpreter],
    ):
        """Check that the mrc file size is consistent with the metadata."""

        for file, interpreter in canonical_tomo_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header
            assert header.nx == canonical_tomogram_metadata["size"]["x"]
            assert header.ny == canonical_tomogram_metadata["size"]["y"]
            assert header.nz == canonical_tomogram_metadata["size"]["z"]

    @allure.title("Tomo MRC spacing is consistent with tomo metadata.")
    def test_mrc_spacing_consistent(
        self,
        canonical_tomogram_metadata: Dict,
        canonical_tomo_mrc_headers: Dict[str, MrcInterpreter],
    ):
        """Check that the mrc file spacing is consistent with the metadata."""

        for file, interpreter in canonical_tomo_mrc_headers.items():
            print(f"\nFile: {file}\n")
            assert pytest.approx(
                canonical_tomogram_metadata["voxel_spacing"],
                abs=SPACING_TOLERANCE,
            ) == interpreter.voxel_size["x"].astype(float)
            assert pytest.approx(
                canonical_tomogram_metadata["voxel_spacing"],
                abs=SPACING_TOLERANCE,
            ) == interpreter.voxel_size["y"].astype(float)
            assert pytest.approx(
                canonical_tomogram_metadata["voxel_spacing"],
                abs=SPACING_TOLERANCE,
            ) == interpreter.voxel_size["z"].astype(float)

    ### END Metadata to MRC-consistency tests ###

    ### BEGIN Metadata to OME-Zarr-consistency tests ###
    ### END Metadata to OME-Zarr-consistency tests ###
