from typing import List

import pandas as pd
import pytest

ANGLE_TOLERANCE = 0.01
BIG_ANGLE_TOLERANCE = 1
MIN_ANGLE_COUNT = 0.5


@pytest.mark.tilt
@pytest.mark.metadata
@pytest.mark.parametrize("run_name", pytest.run_name, scope="session")
class TestTiltAndRawTilt:
    def helper_angles_injection(
        self,
        domain_angles: List[float],
        codomain_angles: List[float],
        domain_name: str,
        codomain_name: str,
    ) -> List[str]:
        """Helper function to check if all angles in the domain are in the codomain."""
        errors = []
        remaining_angles = codomain_angles.copy()
        for domain_angle in domain_angles:
            found_match = False
            for codomain_angle in codomain_angles:
                if abs(domain_angle - codomain_angle) < ANGLE_TOLERANCE:
                    found_match = True
                    remaining_angles.remove(codomain_angle)
                    break
            if not found_match:
                errors.append(f"No match found for angle {domain_angle} in {domain_name} in {codomain_name}")
        if len(domain_angles) > len(codomain_angles):
            errors.append(
                f"More angles in {domain_name} than in {codomain_name} ({len(domain_angles)} vs {len(codomain_angles)})",
            )
        return errors

    ### BEGIN Tilt .tlt tests ###
    def test_tilt_count(self, tiltseries_tilt: pd.DataFrame):
        """Ensure that there are tilt angles."""
        assert len(tiltseries_tilt) > 0

    def test_tilt_angle_range(self, tiltseries_tilt: pd.DataFrame):
        """Ensure that the tilt angles are within the expected range."""
        assert all(-90 <= angle <= 90 for angle in tiltseries_tilt["TiltAngle"])

    def test_tilt_raw_tilt(self, tiltseries_tilt: pd.DataFrame, tiltseries_raw_tilt: pd.DataFrame):
        """Ensure that every tilt angle matches to a raw tilt angle."""
        errors = self.helper_angles_injection(
            tiltseries_tilt["TiltAngle"].to_list(),
            tiltseries_raw_tilt["TiltAngle"].to_list(),
            "tilt file",
            "raw tilt file",
        )
        assert len(errors) == 0, "\n".join(errors)

    ### BEGIN Raw Tilt .rawtlt tests ###
    def test_raw_tilt_count(self, tiltseries_raw_tilt: pd.DataFrame):
        """Ensure that there are raw tilt angles."""
        assert len(tiltseries_raw_tilt) > 0

    def test_raw_tilt_angle_range(self, tiltseries_raw_tilt: pd.DataFrame):
        """Ensure that the raw tilt angles are within the expected range."""
        assert all(-90 <= angle <= 90 for angle in tiltseries_raw_tilt["TiltAngle"])

    def test_raw_tilt_tiltseries_mdoc(self, tiltseries_raw_tilt: pd.DataFrame, tiltseries_mdoc: pd.DataFrame):
        """Ensure that every mdoc angle matches to a raw tilt angle."""
        errors = self.helper_angles_injection(
            tiltseries_mdoc["TiltAngle"].to_list(),
            tiltseries_raw_tilt["TiltAngle"].to_list(),
            "mdoc file",
            "raw tilt file",
        )
        assert len(errors) == 0, "\n".join(errors)
