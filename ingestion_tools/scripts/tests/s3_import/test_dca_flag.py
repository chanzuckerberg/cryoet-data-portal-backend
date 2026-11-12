"""--dca/--no-dca on standardize_dirs.py convert: off by default (Zarr v2 / OME-NGFF 0.4 as before)."""

import pytest
from standardize_dirs import convert


@pytest.mark.parametrize("flag, expected", [([], False), (["--no-dca"], False), (["--dca"], True)])
def test_convert_parses_dca_flag(flag: list[str], expected: bool) -> None:
    ctx = convert.make_context("convert", ["config.yaml", "input-bucket", "output-path", *flag])
    assert ctx.params["dca"] is expected
