"""Unit tests for the IMOD CTF (.defocus) parser.

The parser is flag-driven: the bit ``flag`` (read from a version-3 header line, or assumed 0
for the header-less single-defocus layout) determines the column layout. Flag bits:
``1`` astigmatism, ``2`` astigmatism angle in radians, ``4`` phase shift, ``8`` phase shift in
radians, ``16`` invert tilt angles, ``32`` cut-on frequency.

See https://bio3d.colorado.edu/imod/doc/man/ctfphaseflip.html for the format and the flag
definitions reproduced in ``imod.utils.getDefocusFileFlag`` (scipion-em-imod).
"""

import math
from unittest.mock import Mock

import pytest

from common.ctf_converter import IMODCTF


def _imod(tmp_path, contents: str) -> IMODCTF:
    path = tmp_path / "ctf.defocus"
    path.write_text(contents)
    config = Mock()
    config.fs.localreadable.return_value = str(path)
    return IMODCTF(config, str(path))


# --- from_str: one row under an explicit flag ---------------------------------------------------


def test_from_str_single_defocus():
    # flag 0, 5 columns: startView endView startTilt endTilt defocus[nm]
    info = IMODCTF.from_str("3  3  -58.86  -58.86  7589")
    assert info.section == 3
    assert info.defocus_1 == 75890.0  # 7589 nm -> A
    assert info.defocus_2 == 75890.0  # no astigmatism: defocus_2 mirrors defocus_1
    assert info.azimuth == 0.0
    assert info.phase_shift == 0.0


def test_from_str_single_defocus_tolerates_trailing_version():
    # The first row of a header-less file may carry a trailing version number (6 cols); ignore it.
    info = IMODCTF.from_str("1  1  -64.88  -64.88  7643  2")
    assert info.section == 1
    assert info.defocus_1 == info.defocus_2 == 76430.0
    assert info.azimuth == 0.0


def test_from_str_astigmatism():
    # flag 1, 7 columns: startView endView startTilt endTilt defU[nm] defV[nm] azimuth[deg]
    info = IMODCTF.from_str("1  1  -50.00  -50.00  3665  3472  -62.10", flag=IMODCTF.ASTIGMATISM)
    assert info.section == 1
    assert info.defocus_1 == 36650.0
    assert info.defocus_2 == 34720.0
    assert info.azimuth == -62.10


def test_from_str_phase_only_no_astigmatism():
    # flag 4, 6 columns: ... defocus[nm] phaseShift[deg]; phase emitted in radians.
    info = IMODCTF.from_str("1 1 -50 -50 7000 90", flag=IMODCTF.PHASE_SHIFT)
    assert info.defocus_1 == info.defocus_2 == 70000.0
    assert info.azimuth == 0.0
    assert info.phase_shift == pytest.approx(math.pi / 2)


def test_from_str_astigmatism_phase_cuton():
    # flag 37 (1+4+32), 9 columns: ... defU defV azimuth phaseShift cutOn (cut-on ignored).
    flag = IMODCTF.ASTIGMATISM | IMODCTF.PHASE_SHIFT | IMODCTF.CUT_ON_FREQUENCY
    info = IMODCTF.from_str("1 1 -50 -50 3665 3472 -62.10 180 0.1686", flag=flag)
    assert info.defocus_1 == 36650.0
    assert info.defocus_2 == 34720.0
    assert info.azimuth == -62.10
    assert info.phase_shift == pytest.approx(math.pi)  # 180 deg -> pi rad


def test_from_str_radian_units_converted():
    # flag 3 (1+2): astigmatism angle is in radians; emit degrees.
    info = IMODCTF.from_str("1 1 -50 -50 3665 3472 -1.0838", flag=IMODCTF.ASTIGMATISM | IMODCTF.ASTIGMATISM_RADIANS)
    assert info.azimuth == pytest.approx(-62.10, abs=1e-2)
    # flag 12 (4+8): phase shift already in radians; pass through unchanged.
    info = IMODCTF.from_str("1 1 -50 -50 7000 1.5708", flag=IMODCTF.PHASE_SHIFT | IMODCTF.PHASE_SHIFT_RADIANS)
    assert info.phase_shift == pytest.approx(1.5708)


def test_from_str_too_few_columns():
    with pytest.raises(ValueError, match="expected >= 7"):
        IMODCTF.from_str("1 1 -50 -50 3665", flag=IMODCTF.ASTIGMATISM)


# --- get_ctf_info: whole-file parsing, header/version detection -----------------------------------


def test_get_ctf_info_v2_single_defocus_file(tmp_path):
    # Version 2 (BYU-style): first line carries a trailing version number (6 cols), rest are 5-col.
    contents = "1\t1\t-64.88\t-64.88\t7643\t2\n2\t2\t-61.87\t-61.87\t7650\n3\t3\t-58.86\t-58.86\t7589\n"
    infos = _imod(tmp_path, contents).get_ctf_info()
    assert [i.section for i in infos] == [1, 2, 3]
    assert infos[0].defocus_1 == infos[0].defocus_2 == 76430.0
    assert all(i.azimuth == 0.0 for i in infos)


def test_get_ctf_info_v1_single_defocus_file(tmp_path):
    # Version 1: every line (including the first) is 5-column single defocus, no version/header.
    contents = "1 1 -60.0 -60.0 7000\n2 2 -57.0 -57.0 7100\n"
    infos = _imod(tmp_path, contents).get_ctf_info()
    assert [i.section for i in infos] == [1, 2]
    assert infos[0].defocus_1 == infos[0].defocus_2 == 70000.0


def test_get_ctf_info_v3_single_defocus_with_header(tmp_path):
    # Version-3 flag-0 header ("0 0 0.0 0.0 0.0 3") followed by 5-column single-defocus data.
    contents = "0 0 0.0 0.0 0.0 3\n1 1 -60.0 -60.0 7000\n2 2 -57.0 -57.0 7100\n"
    infos = _imod(tmp_path, contents).get_ctf_info()
    assert len(infos) == 2  # header dropped
    assert infos[0].defocus_1 == infos[0].defocus_2 == 70000.0
    assert infos[0].azimuth == 0.0


def test_get_ctf_info_v3_astigmatism_file_skips_header(tmp_path):
    # Version-3 astigmatism file (flag 1): a header line precedes the 7-column data.
    contents = "1 0 0.0 0.0 0.0 3\n1 1 -50.00 -50.00 3665 3472 -62.10\n2 2 -47.00 -47.00 3600 3400 -61.0\n"
    infos = _imod(tmp_path, contents).get_ctf_info()
    assert len(infos) == 2  # header dropped
    assert infos[0].defocus_1 == 36650.0
    assert infos[0].defocus_2 == 34720.0
    assert infos[0].azimuth == -62.10


def test_get_ctf_info_v3_phase_only_file(tmp_path):
    # flag 4: phase shift, no astigmatism -> 6-column data. Previously rejected outright.
    contents = "4 0 0.0 0.0 0.0 3\n1 1 -50 -50 7000 180\n2 2 -47 -47 7100 180\n"
    infos = _imod(tmp_path, contents).get_ctf_info()
    assert len(infos) == 2
    assert infos[0].defocus_1 == infos[0].defocus_2 == 70000.0
    assert infos[0].azimuth == 0.0
    assert infos[0].phase_shift == pytest.approx(math.pi)


def test_get_ctf_info_v3_phase_cuton_no_astigmatism(tmp_path):
    # flag 36 (4+32): phase + cut-on, NO astigmatism -> 7-column data that must NOT be read as astig.
    contents = "36 0 0.0 0.0 0.0 3\n1 1 -50 -50 7000 180 0.17\n"
    infos = _imod(tmp_path, contents).get_ctf_info()
    assert infos[0].defocus_1 == infos[0].defocus_2 == 70000.0  # not 7000/180 misread as defU/defV
    assert infos[0].azimuth == 0.0  # cut-on (0.17) is NOT mistaken for azimuth
    assert infos[0].phase_shift == pytest.approx(math.pi)


def test_get_ctf_info_keeps_zero_tilt_data(tmp_path):
    # A 0-degree tilt data line has nonzero defocus and must not be mistaken for the header.
    infos = _imod(tmp_path, "20\t20\t0.0\t0.0\t7000\n").get_ctf_info()
    assert len(infos) == 1
    assert infos[0].defocus_1 == 70000.0


def test_get_ctf_info_rejects_headerless_astigmatism(tmp_path):
    # Astigmatism (>=7-col) data with no header is assumed flag 0; the width guard rejects it
    # rather than silently reading defU as a single defocus.
    contents = "1 1 -60.0 -60.0 3665 3472 -62.0\n2 2 -57.0 -57.0 3600 3400 -61.0\n"
    with pytest.raises(ValueError, match="header-less astigmatism"):
        _imod(tmp_path, contents).get_ctf_info()


def test_get_ctf_info_rejects_truncated_row(tmp_path):
    # A row narrower than the flag implies is a hard error.
    contents = "1 0 0.0 0.0 0.0 3\n1 1 -50 -50 3665 3472 -62.0\n2 2 -47 -47 3600\n"
    with pytest.raises(ValueError, match="columns, expected 7"):
        _imod(tmp_path, contents).get_ctf_info()


def test_get_ctf_info_rejects_zero_based_views(tmp_path):
    # Pre-IMOD-4.1 0-based view numbering (off-by-one bug) is rejected, not silently shifted.
    contents = "0 0 -60.0 -60.0 7000\n1 1 -57.0 -57.0 7100\n"
    with pytest.raises(ValueError, match="0-based view numbers"):
        _imod(tmp_path, contents).get_ctf_info()


def test_get_ctf_info_empty_file(tmp_path):
    assert _imod(tmp_path, "\n  \n").get_ctf_info() == []
