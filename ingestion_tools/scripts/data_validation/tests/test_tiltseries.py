from typing import Dict

import allure
import pytest
from mrcfile import utils
from mrcfile.mrcinterpreter import MrcInterpreter

# Tolerance for pixel spacing assertions
SPACING_TOLERANCE = 0.01


@pytest.mark.tiltseries
@pytest.mark.parametrize("run_name", pytest.run_name, scope="session")
class TestTiltSeriesHeader:
    """Validate the mrc file header for a tilt series."""

    MAP_ID = b"MAP "
    IMAGE_STACK_SPACEGROUP = 0

    @pytest.fixture(autouse=True)
    def _set_info(self, dataset, run_name):
        """Set the dataset and run name for the tests."""
        self.dataset = dataset
        self.run_name = run_name

    @allure.title("Tilt Series are 2D image stacks.")
    def test_is_image_stack(self, tiltseries_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the mrc file is a stack of images."""

        # reset_allure.dynamic.epic(f"Dataset {self.dataset}")
        # reset_allure.dynamic.feature(f"Run {self.run_name}")

        for file, interpreter in tiltseries_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header
            assert header.ispg == self.IMAGE_STACK_SPACEGROUP

    @allure.title("Tilt series MAP IDs are correct.")
    def test_map_id_string(self, tiltseries_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the MAP ID is correct."""

        # reset_allure.dynamic.epic(f"Dataset {self.dataset}")
        # reset_allure.dynamic.feature(f"Run {self.run_name}")

        for file, interpreter in tiltseries_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header
            assert header.map == self.MAP_ID

    @allure.title("Tilt series machine stamps are valid.")
    def test_machine_stamp(self, tiltseries_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the machine stamp is valid."""

        # reset_allure.dynamic.epic(f"Dataset {self.dataset}")
        # reset_allure.dynamic.feature(f"Run {self.run_name}")

        for file, interpreter in tiltseries_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header
            try:
                utils.byte_order_from_machine_stamp(header.machst)
            except ValueError:
                pytest.fail(f"Machine stamp is invalid: {utils.pretty_machine_stamp(header.machst)}")

    @allure.title("Tilt series mrc modes are valid.")
    def test_mrc_mode(self, tiltseries_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the mrc mode is valid."""

        # reset_allure.dynamic.epic(f"Dataset {self.dataset}")
        # reset_allure.dynamic.feature(f"Run {self.run_name}")

        for file, interpreter in tiltseries_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header
            try:
                utils.dtype_from_mode(header.mode)
            except ValueError:
                pytest.fail(f"Mode is invalid: {header.mode}")

    @allure.title("Tilt series map dimension fields are non-negative.")
    def test_map_dimension_fields(self, tiltseries_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the map dimension fields are non-negative."""

        # reset_allure.dynamic.epic(f"Dataset {self.dataset}")
        # reset_allure.dynamic.feature(f"Run {self.run_name}")

        for file, interpreter in tiltseries_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header
            for field in ["nx", "ny", "nz", "mx", "my", "mz", "ispg", "nlabl"]:
                assert header[field] >= 0

    @allure.title("Tilt series cell dimensions are non-negative.")
    def test_cell_dimensions(self, tiltseries_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the cell dimensions are non-negative."""

        # reset_allure.dynamic.epic(f"Dataset {self.dataset}")
        # reset_allure.dynamic.feature(f"Run {self.run_name}")

        for file, interpreter in tiltseries_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header
            for field in ["x", "y", "z"]:
                assert header.cella[field] >= 0

    @allure.title("Tilt series label numbers are correct.")
    def test_nlabel(self, tiltseries_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the nlabel is correct."""

        # reset_allure.dynamic.epic(f"Dataset {self.dataset}")
        # reset_allure.dynamic.feature(f"Run {self.run_name}")

        for file, interpreter in tiltseries_mrc_headers.items():
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

    @allure.title("Tilt series MRC versions are correct.")
    def test_nversion(self, tiltseries_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the nversion is correct."""

        # reset_allure.dynamic.epic(f"Dataset {self.dataset}")
        # reset_allure.dynamic.feature(f"Run {self.run_name}")

        for file, interpreter in tiltseries_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header
            assert header.nversion in [20140, 20141]

    @allure.title("Tilt series extended header types are valid.")
    def test_exttyp(self, tiltseries_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the exttyp is valid."""

        # reset_allure.dynamic.epic(f"Dataset {self.dataset}")
        # reset_allure.dynamic.feature(f"Run {self.run_name}")

        for file, interpreter in tiltseries_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header
            if header.nsymbt > 0:
                assert header.exttyp in [b"CCP4", b"MRCO", b"SERI", b"AGAR", b"FEI1", b"FEI2", b"HDF5"]

    @allure.title("Tilt series axis mapping is x == col, y == row, z == sec.")
    def test_axis_mapping(self, tiltseries_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the axis mapping is x == col, y == row, z == sec."""

        # reset_allure.dynamic.epic(f"Dataset {self.dataset}")
        # reset_allure.dynamic.feature(f"Run {self.run_name}")

        for file, interpreter in tiltseries_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header

            # Standard axis mapping
            assert header.mapc == 1
            assert header.mapr == 2
            assert header.maps == 3

    @allure.title("Tilt series unit cells are valid for stacks of images.")
    def test_unit_cell_valid_for_2d_stack(self, tiltseries_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the unit cell is valid for a stack of images."""

        # reset_allure.dynamic.epic(f"Dataset {self.dataset}")
        # reset_allure.dynamic.feature(f"Run {self.run_name}")

        for file, interpreter in tiltseries_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header

            # Unit cell z-size is 1
            assert header.mx == header.nx
            assert header.my == header.ny
            assert header.mz == 1

            # Check that the unit cell angles specify cartesian system
            assert header.cellb.alpha == 90
            assert header.cellb.beta == 90
            assert header.cellb.gamma == 90

    @allure.title("Tilt series origins are zero.")
    def test_origin_is_zero(self, tiltseries_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the origin is zero for a stack of images."""

        # reset_allure.dynamic.epic(f"Dataset {self.dataset}")
        # reset_allure.dynamic.feature(f"Run {self.run_name}")

        for file, interpreter in tiltseries_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header

            # Origin is zero
            assert header.origin.x == 0
            assert header.origin.y == 0
            assert header.origin.z == 0

    @allure.title("Tilt series subimage starts are zero.")
    def test_subimage_start_is_zero(self, tiltseries_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the subimage start is zero for a stack of images."""

        # reset_allure.dynamic.epic(f"Dataset {self.dataset}")
        # reset_allure.dynamic.feature(f"Run {self.run_name}")

        for file, interpreter in tiltseries_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header

            # Subimage start is zero
            assert header.nxstart == 0
            assert header.nystart == 0
            assert header.nzstart == 0

    # def test_tilt_angles_present(self, tiltseries_mrc_headers: Dict[str, MrcInterpreter]):
    #     """Check that the tilt angles are present."""
    #     #TODO: Reader for IMOD tilt angles from extended header
    #     assert True is False


@pytest.mark.tiltseries
@pytest.mark.metadata
@pytest.mark.parametrize("run_name", pytest.run_name, scope="session")
class TestTiltSeriesMeta:

    ### BEGIN Fixtures ###
    @pytest.fixture(autouse=True)
    def _set_info(self, dataset, run_name):
        """Set the dataset and run name for the tests."""
        self.dataset = dataset
        self.run_name = run_name

    @pytest.fixture()
    def tiltcount(self, tiltseries_metadata: Dict):
        tilt_max = tiltseries_metadata["tilt_range"]["max"]
        tilt_min = tiltseries_metadata["tilt_range"]["min"]
        tilt_step = tiltseries_metadata["tilt_step"]

        if tilt_max is None:
            pytest.fail("Tilt max is None.")

        if tilt_min is None:
            pytest.fail("Tilt min is None.")

        if tilt_step is None:
            pytest.fail("Tilt step is None.")

        tilt_count = ((tilt_max - tilt_min) / tilt_step) + 1
        return tilt_count

    ### END Fixtures ###

    ### BEGIN Metadata self-consistency tests ###
    @allure.title("Tilt series metadata exist.")
    def test_exists(self, tiltseries_metadata: Dict):
        """Check that the metadata exist."""
        assert tiltseries_metadata is not None

    @allure.title("TS MRC and Zarr section Number consistent with tilt range and tilt step.")
    def test_tiltcount_consistent(self, tiltseries_metadata: Dict, tiltcount: int):
        """Check that the tilt count (z-sizes) are consistent with the tilt range and tilt step."""

        # Tiltcount consistent with tilt range and tilt step
        # SIZE
        assert tiltseries_metadata["size"]["z"] == tiltcount
        # Zarr Scales
        for s in tiltseries_metadata["scales"]:
            assert s["z"] == tiltcount

    ### END Metadata self-consistency tests ###

    ### BEGIN Metadata to MRC-consistency tests ###
    @allure.title("TS MRC and metadata size is consistent.")
    def test_mrc_size_consistent(self, tiltseries_metadata: Dict, tiltseries_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the metadata size is consistent with the mrc header."""

        for file, interpreter in tiltseries_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header
            assert tiltseries_metadata["size"]["x"] == header.nx
            assert tiltseries_metadata["size"]["y"] == header.ny
            assert tiltseries_metadata["size"]["z"] == header.nz

    @allure.title("TS MRC and metadata pixel spacing is consistent.")
    def test_mrc_spacing_consistent(self, tiltseries_metadata: Dict, tiltseries_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the metadata pixel spacing is consistent with the mrc header."""

        for file, interpreter in tiltseries_mrc_headers.items():
            print(f"\nFile: {file}\n")

            assert pytest.approx(tiltseries_metadata["pixel_spacing"], abs=SPACING_TOLERANCE) == interpreter.voxel_size[
                "x"
            ].astype(float)
            assert pytest.approx(tiltseries_metadata["pixel_spacing"], abs=SPACING_TOLERANCE) == interpreter.voxel_size[
                "y"
            ].astype(float)
            assert pytest.approx(tiltseries_metadata["pixel_spacing"], abs=SPACING_TOLERANCE) == interpreter.voxel_size[
                "z"
            ].astype(float)

    @allure.title("TS MRC header and metadata implied tilt count is consistent.")
    def test_mrc_tiltcount_consistent(self, tiltcount, tiltseries_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the metadata tilt count is consistent with the mrc header."""

        for file, interpreter in tiltseries_mrc_headers.items():
            print(f"\nFile: {file}\n")
            header = interpreter.header

            assert header.nz == tiltcount

    ### END Metadata to MRC-consistency tests ###

    ### BEGIN Metadata to OME-Zarr-consistency tests ###
    ### END Metadata to OME-Zarr-consistency tests ###


# @pytest.mark.tiltseries
# @pytest.mark.metadata
# @pytest.mark.parametrize("run_name", pytest.run_name, )
# class TestMDOC:
#     ### BEGIN Fixtures ###
#     @pytest.fixture()
#     def tiltcount(self, tiltseries_metadata: Dict):
#         tilt_max = tiltseries_metadata['tilt_range']['max']
#         tilt_min = tiltseries_metadata['tilt_range']['min']
#         tilt_step = tiltseries_metadata['tilt_step']
#         tilt_count = ((tilt_max - tilt_min) / tilt_step) + 1
#         return tilt_count
#     ### END Fixtures ###
#
#     ### BEGIN MDOC to metadata-consistency tests ###
#     def test_mdoc_tiltcount_consistent(self, tiltcount, tiltseries_mdoc: pd.DataFrame):
#         """Check that the mdoc tilt count is consistent with the metadata."""
#         assert tiltcount == len(tiltseries_mdoc)
#
#     def test_mdoc_tiltrange_consistent(self, tiltseries_metadata: Dict, tiltseries_mdoc: pd.DataFrame):
#         """Check that the mdoc tilt range is consistent with the metadata."""
#         pass
#
#     def test_mdoc_tiltstep_consistent(self, tiltseries_metadata: Dict, tiltseries_mdoc: pd.DataFrame):
#         """Check that the mdoc tilt step is consistent with the metadata."""
#         pass
#
#
#     ### BEGIN MDOC to metadata-consistency tests ###
#
