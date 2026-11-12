"""The cryoET storage profile v0.1 (common.cryoet_profile) and its writers (common.ome_zarr_writer).

Pure-function tests plus round trips through the local filesystem; the S3 path is covered by test_volume_conversion.
"""

import json
import math
from pathlib import Path

import numpy as np
import pytest

from common import cryoet_profile as cp
from common.fs import FileSystemApi
from common.ome_zarr_writer import tilt_grid, write_label_pyramid, write_tilt_series, write_volume


def read_metas(zarr_dir: Path) -> tuple[dict, dict[str, dict]]:
    group = json.loads((zarr_dir / "zarr.json").read_text())
    arrays = {
        p.parent.name: json.loads(p.read_text())
        for p in zarr_dir.glob("*/zarr.json")
        if json.loads(p.read_text())["node_type"] == "array"
    }
    return group, arrays


# ---------------------------------------------------------------------------------------------------- layout
@pytest.mark.parametrize(
    "shape, image_type, expected",
    [
        ((4, 4, 4), "volume", 3),
        ((492, 1260, 1260), "volume", 3),
        ((500, 8192, 8192), "volume", 3),
        ((500, 8193, 100), "volume", 4),
        ((9000, 100, 100), "volume", 4),
        ((41, 4092, 5760), "tilt_series", 3),
        ((41, 11520, 8184), "tilt_series", 4),
        ((9000, 100, 100), "tilt_series", 3),  # z is the section index: not counted
    ],
)
def test_num_levels(shape, image_type, expected):
    assert cp.num_levels(shape, image_type) == expected


def test_volume_shards_of_the_spec_example():
    shapes = cp.volume_level_shapes((492, 1260, 1260), 3)
    assert shapes == [(492, 1260, 1260), (246, 630, 630), (123, 315, 315)]
    assert [cp.volume_shard_shape(s) for s in shapes] == [(512, 1280, 1280), (256, 640, 640), (128, 384, 384)]
    # at most 2048 in y, x and 4 GiB
    assert cp.volume_shard_shape((2000, 4096, 4096)) == (512, 2048, 2048)
    assert 2 * math.prod(cp.volume_shard_shape((2000, 4096, 4096))) == 2**32


def test_volume_translations():
    assert [cp.volume_translation(5.006, k) for k in range(3)] == pytest.approx([0.0, 2.503, 7.509])


# ---------------------------------------------------------------------------------------------------- Fourier cropping
def test_fourier_plan_spec_examples():
    # dataset 10453: 4092 x 5760; the 4x level pads y by 2 on each side, so o = -2
    p = cp.fourier_plan(4092, 4)
    assert (p.m, p.padded, p.pad_left, p.pad_right, p.crop, p.offset) == (1024, 4096, 2, 2, 0, -2)
    assert cp.fourier_plan(4092, 2).offset == 0
    assert cp.fourier_plan(4096, 4).offset == 0
    # odd sizes (amended spec): one more pixel after the image
    assert [(cp.fourier_plan(1023, s).m, cp.fourier_plan(1023, s).offset) for s in (2, 4)] == [(512, 0), (256, 0)]
    p = cp.fourier_plan(999, 8)
    assert (p.m, p.padded, p.pad_left, p.pad_right, p.crop, p.offset) == (124, 1008, 4, 5, 1, 4)


def _fourier_reference(image: np.ndarray, s: int) -> np.ndarray:
    """Full complex FFT with an explicit centre crop of the shifted spectrum."""
    py_, px_ = cp.fourier_plan(image.shape[0], s), cp.fourier_plan(image.shape[1], s)
    a = np.pad(image, ((py_.pad_left, py_.pad_right), (px_.pad_left, px_.pad_right)), constant_values=image.mean())
    f = np.fft.fftshift(np.fft.fft2(a))
    qy, qx = a.shape[0] // s, a.shape[1] // s
    y0, x0 = a.shape[0] // 2 - qy // 2, a.shape[1] // 2 - qx // 2
    g = f[y0 : y0 + qy, x0 : x0 + qx].copy()
    g[0, :] = 0
    g[:, 0] = 0
    out = np.fft.ifft2(np.fft.ifftshift(g)).real * (qy * qx) / a.size
    return out[py_.crop : py_.crop + py_.m, px_.crop : px_.crop + px_.m]


@pytest.mark.parametrize("n", [64, 66, 67, 90, 99, 101, 128])
@pytest.mark.parametrize("s", [2, 4, 8])
def test_fourier_downsample_matches_full_fft_and_keeps_mean(n, s):
    rng = np.random.default_rng(n * s)
    image = rng.normal(size=(n, n + 7))
    out = cp.fourier_downsample(image, cp.fourier_plan(n, s), cp.fourier_plan(n + 7, s))
    np.testing.assert_allclose(out, _fourier_reference(image, s), atol=1e-12)


@pytest.mark.parametrize("n", [1023, 1024, 999, 1001])
@pytest.mark.parametrize("s", [2, 4])
def test_fourier_offsets_place_pixels(n, s):
    """A smooth blob at level-0 position c appears at level position (c - o) / s."""
    c = n / 2 + 3.3
    sigma = 6.0 * s
    y = np.arange(n)
    image = np.exp(-0.5 * ((y[:, None] - c) / sigma) ** 2) * np.ones((1, 40))
    plan_y, plan_x = cp.fourier_plan(n, s), cp.fourier_plan(40, s)
    profile = cp.fourier_downsample(image, plan_y, plan_x).mean(axis=1)
    expected = (c - plan_y.offset) / s
    k = np.arange(profile.size)
    window = np.abs(k - expected) <= 5 * sigma / s
    centroid = (profile[window] * k[window]).sum() / profile[window].sum()
    assert abs(centroid - expected) < 0.01


# ---------------------------------------------------------------------------------------------------- encoding
def _stats(x: np.ndarray) -> cp.RunningStats:
    st = cp.RunningStats()
    for z0 in range(0, x.shape[0], 3):
        st.update(x[z0 : z0 + 3])
    return st


def test_running_stats_match_numpy():
    x = np.random.default_rng(1).normal(5.0, 2.0, size=(10, 20, 30)).astype(np.float32)
    st = _stats(x)
    assert st.mean == pytest.approx(x.astype(np.float64).mean(), rel=1e-12)
    assert st.std == pytest.approx(x.astype(np.float64).std(), rel=1e-10)
    assert (st.vmin, st.vmax) == (float(x.min()), float(x.max()))
    assert st.finite and not st.integer


def test_continuous_encoding_error_bound():
    x = (np.random.default_rng(2).normal(size=(12, 16, 20)) * 1e-6 - 8e-8).astype(np.float32)
    enc = cp.choose_volume_encoding(_stats(x))
    assert not enc.integer
    codes = cp.encode_codes(x, enc, slab=5)
    assert codes.dtype == np.int16 and codes.min() >= -32767 and codes.max() <= 32767
    assert max(abs(int(codes.min())), int(codes.max())) == 32767  # the full range is used
    err = np.abs(cp.decode_codes(codes, enc) - x.astype(np.float64))
    assert err.max() <= enc.scale_factor / 2 * (1 + 1e-9)
    assert abs(codes.mean()) < 200  # centred on the mean


def test_integer_volume_is_lossless():
    x = np.random.default_rng(3).integers(-128, 128, size=(8, 9, 10)).astype(np.float32) + 1000
    enc = cp.choose_volume_encoding(_stats(x))
    assert enc.integer and enc.scale_factor == 1.0 and enc.add_offset == np.rint(x.astype(np.float64).mean())
    np.testing.assert_array_equal(cp.decode_codes(cp.encode_codes(x, enc), enc), x)


def test_wide_integer_volume_falls_back_to_scaling():
    x = np.zeros((4, 4, 4), dtype=np.float32)
    x[0, 0, 0], x[1, 1, 1] = -40000, 40000
    x[2] = 3
    enc = cp.choose_volume_encoding(_stats(x))
    assert not enc.integer


def test_constant_volumes():
    enc = cp.choose_volume_encoding(_stats(np.full((3, 3, 3), 0.25, dtype=np.float32)))
    assert (enc.add_offset, enc.scale_factor) == (0.25, 1.0)
    assert not cp.encode_codes(np.full((3, 3, 3), 0.25, dtype=np.float32), enc).any()
    enc = cp.choose_volume_encoding(_stats(np.full((3, 3, 3), 7.0, dtype=np.float32)))
    assert (enc.add_offset, enc.scale_factor, enc.integer) == (7.0, 1.0, True)


def test_corrupt_volumes_are_rejected():
    x = np.random.default_rng(4).normal(size=(10, 10, 10)).astype(np.float32)
    x[0, 0, 0] = np.nan
    with pytest.raises(cp.CorruptVolumeError, match="NaN"):
        cp.choose_volume_encoding(_stats(x))
    # like tomogram 16248: real content within +/- 9 and a voxel near the float32 limit. One outlier among N voxels
    # lies about sqrt(N) standard deviations from the mean (it inflates the std itself), so the 1000-std rule needs
    # N > 10^6: tomogram-sized volumes.
    x = np.random.default_rng(5).normal(size=(128, 128, 128)).astype(np.float32)
    x[3, 4, 5] = 2.8e38
    with pytest.raises(cp.CorruptVolumeError, match="1000 standard deviations"):
        cp.choose_volume_encoding(_stats(x))


def test_rounding_is_half_to_even():
    enc = cp.VolumeEncoding(add_offset=0.0, scale_factor=1.0, integer=False)
    np.testing.assert_array_equal(cp.encode_codes(np.array([[[0.5, 1.5, -0.5, 2.5]]]), enc), [[[0, 2, 0, 2]]])


@pytest.mark.parametrize("shape", [(4, 4, 4), (5, 7, 9), (1, 1, 3), (33, 2, 17)])
def test_bin2_codes_matches_brute_force(shape):
    codes = np.random.default_rng(6).integers(-32767, 32768, size=shape).astype(np.int16)
    out = cp.bin2_codes(codes, slab=4)
    expected = np.empty(tuple(-(-n // 2) for n in shape), dtype=np.int16)
    for idx in np.ndindex(expected.shape):
        block = codes[tuple(slice(2 * i, 2 * i + 2) for i in idx)]
        expected[idx] = np.rint(block.astype(np.float64).mean())
    np.testing.assert_array_equal(out, expected)


def test_histogram_statistics_equal_numpy():
    codes = np.random.default_rng(7).integers(-3000, 3000, size=(17, 19, 23)).astype(np.int16)
    stats = cp.stats_from_histogram(cp.code_histogram(codes, slab=4))
    v = codes.astype(np.float64).ravel()
    for key, q in {"p1": 1, "p5": 5, "p95": 95, "p99": 99, "median": 50}.items():
        assert stats[key] == pytest.approx(np.percentile(v, q), abs=1e-9)
    assert stats["mean"] == pytest.approx(v.mean(), rel=1e-12)
    assert stats["std"] == pytest.approx(v.std(), rel=1e-12)
    assert stats["iqr"] == pytest.approx(np.percentile(v, 75) - np.percentile(v, 25))
    assert stats == pytest.approx(cp.stats_from_values(v))


# ---------------------------------------------------------------------------------------------------- writers
@pytest.fixture
def local_fs() -> FileSystemApi:
    return FileSystemApi.get_fs_api(mode="local", force_overwrite=False)


def test_write_volume_round_trip(local_fs, tmp_path):
    import zarr

    x = (np.random.default_rng(8).normal(size=(37, 70, 45)) * 2e-6 - 8e-8).astype(np.float32)
    zarr_dir = tmp_path / "tomo.zarr"
    result = write_volume(local_fs, x, str(zarr_dir), 5.006)
    group, arrays = read_metas(zarr_dir)
    assert cp.check_profile(group, arrays) == []
    assert result.level_shapes == [(37, 70, 45), (19, 35, 23), (10, 18, 12)]

    root = zarr.open_group(str(zarr_dir), mode="r")
    enc = result.encoding
    codes0 = root["0"][0, 0]
    np.testing.assert_array_equal(codes0, cp.encode_codes(x, enc))
    assert root["0"].attrs["scale_factor"] == enc.scale_factor == root["2"].attrs["scale_factor"]
    np.testing.assert_array_equal(root["1"][0, 0], cp.bin2_codes(codes0))
    np.testing.assert_array_equal(root["2"][0, 0], cp.bin2_codes(cp.bin2_codes(codes0)))
    stats = group["attributes"]["dca"]["normalization_statistics"]
    assert stats["0"]["dataset_statistics"] == pytest.approx(cp.stats_from_values(codes0))
    assert stats["0"]["level_statistics"]["2"]["dataset_statistics"] == pytest.approx(
        cp.stats_from_values(root["2"][:]),
    )
    ms = group["attributes"]["ome"]["multiscales"][0]
    assert ms["datasets"][1]["coordinateTransformations"][1]["translation"] == pytest.approx([0, 0, 2.503, 2.503, 2.503])


def test_write_volume_rejects_corrupt_volume(local_fs, tmp_path):
    x = np.zeros((4, 4, 4), dtype=np.float32)
    x[0, 0, 0] = np.inf
    with pytest.raises(cp.CorruptVolumeError):
        write_volume(local_fs, x, str(tmp_path / "bad.zarr"), 10.0)


def test_write_volume_replaces_existing_v2_store(local_fs, tmp_path):
    zarr_dir = tmp_path / "tomo.zarr"
    zarr_dir.mkdir()
    (zarr_dir / ".zgroup").write_text('{"zarr_format": 2}')
    (zarr_dir / ".zattrs").write_text("{}")
    write_volume(local_fs, np.ones((4, 4, 4), dtype=np.float32), str(zarr_dir), 10.0)
    assert not (zarr_dir / ".zgroup").exists() and not (zarr_dir / ".zattrs").exists()


@pytest.mark.parametrize("shape", [(3, 64, 90), (2, 66, 43)])
def test_write_tilt_series_round_trip(local_fs, tmp_path, shape):
    import zarr

    x = np.random.default_rng(9).normal(10.0, 3.0, size=shape).astype(np.float32)
    zarr_dir = tmp_path / "ts.zarr"
    result = write_tilt_series(local_fs, x, str(zarr_dir), 1.68)
    group, arrays = read_metas(zarr_dir)
    assert cp.check_profile(group, arrays) == []
    root = zarr.open_group(str(zarr_dir), mode="r")
    np.testing.assert_array_equal(root["0"][:], x)
    py_, px_ = cp.fourier_plan(shape[1], 4), cp.fourier_plan(shape[2], 4)
    np.testing.assert_allclose(
        root["2"][1],
        cp.fourier_downsample(x[1].astype(np.float64), py_, px_).astype(np.float32),
    )
    stats = group["attributes"]["dca"]["normalization_statistics"]
    assert len(stats["0"]["section_statistics"]) == shape[0]
    assert len(stats["0"]["level_statistics"]["2"]["section_statistics"]) == shape[0]
    assert stats["metadata"]["grid"] == tilt_grid(shape) == 1
    assert stats["0"]["section_statistics"]["1"] == pytest.approx(cp.stats_from_values(x[1]))
    translation = group["attributes"]["ome"]["multiscales"][0]["datasets"][2]["coordinateTransformations"][1]
    assert translation["translation"] == pytest.approx([0.0, py_.offset * 1.68, px_.offset * 1.68])
    assert result.level_shapes[2] == (shape[0], py_.m, px_.m)


def test_tilt_grid_bounds_the_statistics_sample():
    assert tilt_grid((41, 4092, 5760)) == 4
    assert tilt_grid((3, 64, 90)) == 1


def test_check_profile_reports_violations(local_fs, tmp_path):
    zarr_dir = tmp_path / "tomo.zarr"
    write_volume(local_fs, np.random.default_rng(10).normal(size=(6, 7, 8)).astype(np.float32), str(zarr_dir), 3.0)
    group, arrays = read_metas(zarr_dir)
    del group["attributes"]["dca"]["profile"]
    arrays["1"]["attributes"] = {}
    arrays["2"]["fill_value"] = 5
    ms = group["attributes"]["ome"]["multiscales"][0]
    ms["datasets"][1]["coordinateTransformations"] = ms["datasets"][1]["coordinateTransformations"][:1]
    errors = cp.check_profile(group, arrays)
    assert any("dca block" in e for e in errors)
    assert any("level 1: scale_factor/add_offset" in e for e in errors)
    assert any("level 2: fill_value" in e for e in errors)
    assert any("level 1: need scale + translation" in e for e in errors)


def _stats0(dca: dict) -> dict:
    return dca["normalization_statistics"]["0"]


# dca-block violations: the first group the schema generated from schema/dca_metadata (LinkML) rejects, the second
# check_profile's checks against the arrays (statistics keys, image-type rules), which the schema can't state
DCA_VIOLATIONS = {
    "missing version": ("volume", lambda d: d.pop("version"), "dca block"),
    "wrong version": ("volume", lambda d: d.update(version="0.2"), "dca block"),
    "bad image_type": ("volume", lambda d: d.update(image_type="image"), "dca block"),
    "profile name": ("volume", lambda d: d["profile"].update(name="other"), "dca block"),
    "profile extra key": ("volume", lambda d: d["profile"].update(extra=1), "dca block"),
    "missing key 0": ("volume", lambda d: d["normalization_statistics"].pop("0"), "dca block"),
    "std < 0": ("volume", lambda d: _stats0(d)["dataset_statistics"].update(std=-1.0), "dca block"),
    "missing p99": ("volume", lambda d: _stats0(d)["dataset_statistics"].pop("p99"), "dca block"),
    "extra statistic": ("volume", lambda d: _stats0(d)["dataset_statistics"].update(p50=1.0), "dca block"),
    "section std < 0": ("tilt", lambda d: _stats0(d)["section_statistics"]["0"].update(std=-2.0), "dca block"),
    "level key 0": (
        "volume",
        lambda d: _stats0(d)["level_statistics"].update({"0": _stats0(d)["level_statistics"]["1"]}),
        "level_statistics keys",
    ),
    "one level missing": ("volume", lambda d: _stats0(d)["level_statistics"].pop("2"), "level_statistics keys"),
    "level as bare statistics": (
        "volume",
        lambda d: _stats0(d)["level_statistics"].update({"1": _stats0(d)["dataset_statistics"]}),
        "needs dataset_statistics",
    ),
    "volume with sections": (
        "volume",
        lambda d: _stats0(d).update(section_statistics={"0": _stats0(d)["dataset_statistics"]}),
        "volumes have no section_statistics",
    ),
    "tilt series without level-0 sections": (
        "tilt",
        lambda d: _stats0(d).pop("section_statistics"),
        "level 0: need section statistics",
    ),
    "tilt series without level-1 sections": (
        "tilt",
        lambda d: _stats0(d)["level_statistics"]["1"].pop("section_statistics"),
        "level 1: need section statistics",
    ),
    "tilt series section key 'x'": (
        "tilt",
        lambda d: _stats0(d)["section_statistics"].update({"x": _stats0(d)["section_statistics"]["0"]}),
        "level 0: need section statistics",
    ),
}


@pytest.fixture(scope="module")
def profile_images(tmp_path_factory) -> dict[str, Path]:
    fs = FileSystemApi.get_fs_api(mode="local", force_overwrite=False)
    root = tmp_path_factory.mktemp("profile_images")
    rng = np.random.default_rng(12)
    write_volume(fs, rng.normal(size=(20, 30, 40)).astype(np.float32), str(root / "volume.zarr"), 5.0)
    write_tilt_series(fs, rng.normal(size=(3, 66, 43)).astype(np.float32), str(root / "tilt.zarr"), 1.68)
    return {"volume": root / "volume.zarr", "tilt": root / "tilt.zarr"}


def test_dca_schema_is_the_generated_linkml_schema():
    schema = json.loads(cp.DCA_SCHEMA_PATH.read_text())
    assert schema["title"] == "cdp-dca-metadata"
    assert schema["$id"].endswith("/schema/dca_metadata")


@pytest.mark.parametrize("case", sorted(DCA_VIOLATIONS))
def test_check_profile_rejects_dca_violations(profile_images, case):
    image, mutate, message = DCA_VIOLATIONS[case]
    group, arrays = read_metas(profile_images[image])
    assert cp.check_profile(group, arrays) == []
    mutate(group["attributes"]["dca"])
    errors = cp.check_profile(group, arrays)
    assert any(message in e for e in errors), errors


def test_check_profile_allows_further_dca_fields(profile_images):
    """DCA adds fields to the dca block (channels, experimental metadata): the profile doesn't forbid them."""
    group, arrays = read_metas(profile_images["volume"])
    group["attributes"]["dca"]["channels"] = []
    assert cp.check_profile(group, arrays) == []


def test_write_label_pyramid(local_fs, tmp_path):
    import zarr
    from cryoet_data_portal_neuroglancer.io import open_omezarr

    labels = np.zeros((8, 8, 8), dtype=np.uint16)
    labels[2:5, 2:5, 2:5] = 3
    labels[6, 6, 6] = 9
    pyramid = [labels, labels[::2, ::2, ::2], labels[::4, ::4, ::4]]
    zarr_dir = tmp_path / "mask.zarr"
    write_label_pyramid(local_fs, pyramid, str(zarr_dir), [(10.0,) * 3, (20.0,) * 3, (40.0,) * 3], label_values=[3, 9])
    group, arrays = read_metas(zarr_dir)
    assert group["zarr_format"] == 3 and group["attributes"]["ome"]["version"] == "0.5"
    assert group["attributes"]["ome"]["image-label"] == {"colors": [{"label-value": 3}, {"label-value": 9}]}
    assert arrays["0"]["data_type"] == "uint16"
    assert arrays["0"]["chunk_grid"]["configuration"]["chunk_shape"] == [256, 256, 256]
    assert arrays["0"]["codecs"][1]["name"] == "blosc"
    root = zarr.open_group(str(zarr_dir), mode="r")
    np.testing.assert_array_equal(root["1"][:], pyramid[1])
    assert open_omezarr(str(zarr_dir)).label_values == [3, 9]
