"""Flags of standardize_dirs.py convert that are off by default:
- --dca/--no-dca: off writes Zarr v2 / OME-NGFF 0.4 as before;
- --skip-mrc/--no-skip-mrc: off writes MRC files as before; on (requires --dca) writes none.
"""

import pytest
from click.testing import CliRunner
from standardize_dirs import convert

ARGS = ["config.yaml", "input-bucket", "output-path"]


@pytest.mark.parametrize("flag, expected", [([], False), (["--no-dca"], False), (["--dca"], True)])
def test_convert_parses_dca_flag(flag: list[str], expected: bool) -> None:
    ctx = convert.make_context("convert", [*ARGS, *flag])
    assert ctx.params["dca"] is expected


@pytest.mark.parametrize(
    "flag, expected",
    [([], False), (["--no-skip-mrc"], False), (["--dca", "--skip-mrc"], True)],
)
def test_convert_parses_skip_mrc_flag(flag: list[str], expected: bool) -> None:
    ctx = convert.make_context("convert", [*ARGS, *flag])
    assert ctx.params["skip_mrc"] is expected


def test_skip_mrc_requires_dca() -> None:
    result = CliRunner().invoke(convert, [*ARGS, "--skip-mrc"])
    assert result.exit_code == 2
    assert "--skip-mrc requires --dca" in result.output
