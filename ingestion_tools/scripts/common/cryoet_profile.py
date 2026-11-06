"""The cryoET storage profile v0.1 of the DCA v0.3 spec, for tomograms ("volume") and tilt series ("tilt_series").

Spec: https://github.com/chanzuckerberg/dynamic-cell-atlas-specs, docs/cryoet/v0.1. In short:

* Volumes: 5-D ``[1, 1, Z, Y, X]`` (t, c, z, y, x) ``int16`` codes centred on the mean, decoded with the CF
  attributes ``value = add_offset + scale_factor * code``; ``K + 1`` levels of 2x mean binning of the codes; inner
  chunks 128^3 in shards of up to 2048 in y, x and 4 GiB; zstd level 3.
* Tilt series: 3-D ``[Z, Y, X]`` float32 as acquired; ``K + 1`` levels made by Fourier cropping each tilt image from
  level 0; inner chunks ``[1, 128, 128]`` in one shard per tilt image; Blosc lz4.
* Both: every level has a scale and a translation that place pixel centres exactly; the group carries ``ome``
  (OME-NGFF 0.5) and ``dca`` (profile declaration and image statistics) attributes.

This module holds the pure rules (shapes, encoding, resampling, statistics, metadata and a checker); the writers are
in ``common.ome_zarr_writer``.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Sequence

import numpy as np

ImageType = Literal["volume", "tilt_series"]

PROFILE = {
    "name": "cryoet",
    "version": "0.1",
    "url": "https://raw.githubusercontent.com/chanzuckerberg/dynamic-cell-atlas-specs/main/docs/cryoet/v0.1/schema.json",
}
DCA_VERSION = "0.3"
DCA_SCHEMA_URL = "https://raw.githubusercontent.com/chanzuckerberg/dynamic-cell-atlas-specs/main/docs/v0.3/schema.json"
PROFILE_SCHEMA_PATH = Path(__file__).parent / "schemas" / "cryoet_profile_v0.1.schema.json"

INNER_CHUNK = 128
MAX_LEVEL_EDGE = 2048
CODE_MAX = 32767
CORRUPT_STD = 1000.0
SHARD_MAX_BYTES = 2**32

SPACE_AXIS = {"type": "space", "unit": "angstrom"}
AXES: dict[str, list[dict[str, str]]] = {
    "volume": [
        {"name": "t", "type": "time", "unit": "second"},
        {"name": "c", "type": "channel"},
        {"name": "z", **SPACE_AXIS},
        {"name": "y", **SPACE_AXIS},
        {"name": "x", **SPACE_AXIS},
    ],
    "tilt_series": [{"name": "z", **SPACE_AXIS}, {"name": "y", **SPACE_AXIS}, {"name": "x", **SPACE_AXIS}],
}
DIMENSION_NAMES = {k: [a["name"] for a in v] for k, v in AXES.items()}
MULTISCALE_TYPE = {"volume": "mean", "tilt_series": "fourier"}
MULTISCALE_NAME = {"volume": "tomogram", "tilt_series": "tilt_series"}
INNER_CODECS: dict[str, list[dict[str, Any]]] = {
    "volume": [
        {"name": "bytes", "configuration": {"endian": "little"}},
        {"name": "zstd", "configuration": {"level": 3, "checksum": False}},
    ],
    "tilt_series": [
        {"name": "bytes", "configuration": {"endian": "little"}},
        {
            "name": "blosc",
            "configuration": {"cname": "lz4", "clevel": 5, "shuffle": "shuffle", "typesize": 4, "blocksize": 0},
        },
    ],
}
INDEX_CODECS = [{"name": "bytes", "configuration": {"endian": "little"}}, {"name": "crc32c"}]
DATA_TYPE = {"volume": "int16", "tilt_series": "float32"}
PERCENTILES = {"p1": 1, "p5": 5, "p25": 25, "median": 50, "p75": 75, "p95": 95, "p99": 99}


class CorruptVolumeError(ValueError):
    """The volume holds non-finite values or values too far from its mean to be stored under the profile."""


# ---------------------------------------------------------------------------------------------------- layout
def round_up(n: int, multiple: int = INNER_CHUNK) -> int:
    return -(-int(n) // multiple) * multiple


def num_levels(shape_zyx: Sequence[int], image_type: ImageType) -> int:
    """``K + 1`` with ``K = max(2, ceil(log2(m / 2048)))``; ``m`` is ``max(Z, Y, X)`` for volumes and ``max(Y, X)``
    for tilt series."""
    m = max(shape_zyx) if image_type == "volume" else max(shape_zyx[1:])
    k = math.ceil(math.log2(m / MAX_LEVEL_EDGE)) if m > MAX_LEVEL_EDGE else 0
    return max(2, k) + 1


def volume_level_shapes(shape_zyx: Sequence[int], levels: int) -> list[tuple[int, int, int]]:
    shapes = [tuple(int(n) for n in shape_zyx)]
    for _ in range(levels - 1):
        shapes.append(tuple(-(-n // 2) for n in shapes[-1]))
    return shapes  # type: ignore[return-value]


def volume_shard_shape(level_zyx: Sequence[int], itemsize: int = 2) -> tuple[int, int, int]:
    """``S_y = min(Y', 2048)``, ``S_x = min(X', 2048)``, ``S_z = min(Z', 128 * floor(2^32 / (b * 128 * S_y * S_x)))``
    with ``Z', Y', X'`` the level's sizes rounded up to multiples of 128."""
    z, y, x = (round_up(n) for n in level_zyx)
    sy, sx = min(y, MAX_LEVEL_EDGE), min(x, MAX_LEVEL_EDGE)
    sz = min(z, INNER_CHUNK * (SHARD_MAX_BYTES // (itemsize * INNER_CHUNK * sy * sx)))
    return sz, sy, sx


def tilt_shard_shape(level_zyx: Sequence[int]) -> tuple[int, int, int]:
    return 1, round_up(level_zyx[1]), round_up(level_zyx[2])


def volume_translation(voxel_size: float, level: int) -> float:
    """Offset of a 2^level mean-binned level: the centre of its first block, ``p * (2^k - 1) / 2``."""
    return voxel_size * (2**level - 1) / 2


# ---------------------------------------------------------------------------------------------------- Fourier cropping
@dataclass(frozen=True)
class FourierAxisPlan:
    """Fourier cropping of one image axis of length ``n`` by ``s`` (spec: tilt-series.rst, Fourier Cropping)."""

    n: int
    s: int
    m: int  # output length
    padded: int  # P
    pad_left: int
    pad_right: int
    crop: int

    @property
    def offset(self) -> int:
        """Level-0 pixel of output pixel 0: ``o = s * crop - pad_left``."""
        return self.s * self.crop - self.pad_left


def fourier_plan(n: int, s: int) -> FourierAxisPlan:
    m = 2 * round(n / (2 * s))  # Python's round: half to even (n / 2s is exact for s a power of two)
    if m < 2:
        raise ValueError(f"an axis of {n} pixels is too short for Fourier cropping by {s}")
    padded = -(-n // (2 * s)) * 2 * s
    pad_left = (padded - n) // 2
    crop = (padded // s - m) // 2
    return FourierAxisPlan(n, s, m, padded, pad_left, padded - n - pad_left, crop)


def fourier_downsample(image: np.ndarray, plan_y: FourierAxisPlan, plan_x: FourierAxisPlan) -> np.ndarray:
    """One tilt image (2-D, float64) Fourier-cropped by ``s``: pad with its mean, keep the ``P/s`` lowest
    frequencies with the new Nyquist row and column set to zero, transform back and multiply by ``1/s^2``, then
    keep the ``m_y x m_x`` window at ``(crop_y, crop_x)``."""
    s = plan_y.s
    a = np.pad(
        np.asarray(image, dtype=np.float64),
        ((plan_y.pad_left, plan_y.pad_right), (plan_x.pad_left, plan_x.pad_right)),
        constant_values=float(np.mean(image, dtype=np.float64)),
    )
    py, px = a.shape
    qy, qx = py // s, px // s
    f = np.fft.rfft2(a)
    g = np.zeros((qy, qx // 2 + 1), dtype=np.complex128)
    g[: qy // 2, :] = f[: qy // 2, : qx // 2 + 1]
    g[qy - qy // 2 + 1 :, :] = f[py - qy // 2 + 1 :, : qx // 2 + 1]  # negative frequencies; row qy/2 stays 0
    g[:, qx // 2] = 0  # new Nyquist column
    out = np.fft.irfft2(g, s=(qy, qx)) * (qy * qx) / (py * px)
    return out[plan_y.crop : plan_y.crop + plan_y.m, plan_x.crop : plan_x.crop + plan_x.m]


# ---------------------------------------------------------------------------------------------------- encoding
@dataclass
class RunningStats:
    """Count, mean and sum of squared deviations (Chan et al.), min, max, finiteness and integrality, in float64,
    updated block by block."""

    n: int = 0
    mean: float = 0.0
    m2: float = 0.0
    vmin: float = math.inf
    vmax: float = -math.inf
    finite: bool = True
    integer: bool = True

    def update(self, x: np.ndarray) -> None:
        x = np.asarray(x)
        if x.size == 0:
            return
        if x.dtype.kind == "f" and not np.isfinite(x).all():
            self.finite = False
            return
        b = x.astype(np.float64)
        nb = b.size
        mb = float(b.mean())
        m2b = float(np.square(b - mb).sum())
        n = self.n + nb
        delta = mb - self.mean
        self.mean += delta * nb / n
        self.m2 += m2b + delta * delta * self.n * nb / n
        self.n = n
        self.vmin = min(self.vmin, float(b.min()))
        self.vmax = max(self.vmax, float(b.max()))
        if self.integer and x.dtype.kind == "f":
            self.integer = bool(np.array_equal(b, np.rint(b)))

    @property
    def std(self) -> float:
        return math.sqrt(self.m2 / self.n) if self.n else 0.0


@dataclass(frozen=True)
class VolumeEncoding:
    add_offset: float
    scale_factor: float
    integer: bool  # lossless (integer-valued source)


def choose_volume_encoding(st: RunningStats) -> VolumeEncoding:
    """Steps 1-3 of the volume encoding (spec: volumes.rst, Data Type and Encoding)."""
    if not st.finite:
        raise CorruptVolumeError("the volume holds NaN or infinite values")
    if st.n == 0:
        raise CorruptVolumeError("the volume is empty")
    dev = max(st.vmax - st.mean, st.mean - st.vmin)
    if dev > CORRUPT_STD * st.std:
        raise CorruptVolumeError(
            f"the largest deviation from the mean ({dev:.6g}) exceeds {CORRUPT_STD:g} standard deviations "
            f"({st.std:.6g}): the volume holds corrupt voxels",
        )
    if st.integer:
        offset = float(np.rint(st.mean))  # round half to even
        if max(st.vmax - offset, offset - st.vmin) <= CODE_MAX:
            return VolumeEncoding(offset, 1.0, True)
    scale = dev / CODE_MAX
    return VolumeEncoding(st.mean, scale if scale > 0 else 1.0, False)


def encode_codes(x: np.ndarray, enc: VolumeEncoding, out: np.ndarray | None = None, slab: int = 32) -> np.ndarray:
    """``code = round((x - add_offset) / scale_factor)``, half to even, in float64, as int16 in
    ``[-32767, 32767]``; computed in slabs along the first axis to bound the float64 temporaries."""
    out = np.empty(x.shape, dtype=np.int16) if out is None else out
    for z0 in range(0, x.shape[0], slab):
        c = np.rint((np.asarray(x[z0 : z0 + slab], dtype=np.float64) - enc.add_offset) / enc.scale_factor)
        np.clip(c, -CODE_MAX, CODE_MAX, out=c)
        out[z0 : z0 + slab] = c
    return out


def decode_codes(codes: np.ndarray, enc_or_attrs: VolumeEncoding | dict[str, Any]) -> np.ndarray:
    if isinstance(enc_or_attrs, VolumeEncoding):
        sf, ao = enc_or_attrs.scale_factor, enc_or_attrs.add_offset
    else:
        sf, ao = float(enc_or_attrs["scale_factor"]), float(enc_or_attrs["add_offset"])
    return codes.astype(np.float64) * sf + ao


def bin2_codes(codes: np.ndarray, slab: int = 64) -> np.ndarray:
    """2x2x2 mean of int16 codes (blocks starting at index 0; a block cut by the array end averages the voxels it
    has), rounded half to even. Shape ``ceil(n / 2)`` per axis."""
    z, y, x = codes.shape
    oz, oy, ox = -(-z // 2), -(-y // 2), -(-x // 2)
    out = np.empty((oz, oy, ox), dtype=np.int16)
    cy = np.full(oy, 2.0)
    cx = np.full(ox, 2.0)
    if y % 2:
        cy[-1] = 1.0
    if x % 2:
        cx[-1] = 1.0
    slab -= slab % 2
    for z0 in range(0, z, slab):
        part = codes[z0 : z0 + slab].astype(np.int32)
        pz = part.shape[0] % 2
        part = np.pad(part, ((0, pz), (0, y % 2), (0, x % 2)))
        sums = part.reshape(part.shape[0] // 2, 2, oy, 2, ox, 2).sum(axis=(1, 3, 5))
        cz = np.full(sums.shape[0], 2.0)
        if pz:
            cz[-1] = 1.0
        counts = cz[:, None, None] * cy[None, :, None] * cx[None, None, :]
        out[z0 // 2 : z0 // 2 + sums.shape[0]] = np.rint(sums / counts)
    return out


# ---------------------------------------------------------------------------------------------------- statistics
def _finish_stats(mean: float, std: float, pct: dict[str, float]) -> dict[str, float]:
    return {
        "p1": pct["p1"],
        "p5": pct["p5"],
        "p95": pct["p95"],
        "p99": pct["p99"],
        "mean": mean,
        "std": std,
        "p95_p5": pct["p95"] - pct["p5"],
        "p99_p1": pct["p99"] - pct["p1"],
        "median": pct["median"],
        "iqr": pct["p75"] - pct["p25"],
    }


def code_histogram(codes: np.ndarray, slab: int = 64) -> np.ndarray:
    """Histogram of int16 codes over all 65536 values (index = code + 32768)."""
    hist = np.zeros(65536, dtype=np.int64)
    for z0 in range(0, codes.shape[0], slab):
        hist += np.bincount(codes[z0 : z0 + slab].ravel().astype(np.int32) + 32768, minlength=65536)
    return hist


def stats_from_histogram(hist: np.ndarray, offset: int = -32768) -> dict[str, float]:
    """Exact statistics of integer values from their histogram: mean, population std and percentiles with linear
    interpolation between the closest ranks (NumPy's default method)."""
    counts = np.asarray(hist, dtype=np.int64)
    n = int(counts.sum())
    nz = np.flatnonzero(counts)
    values = (nz + offset).astype(np.float64)
    weights = counts[nz].astype(np.float64)
    mean = float(np.dot(values, weights) / n)
    std = float(math.sqrt(np.dot(np.square(values - mean), weights) / n))
    cum = np.cumsum(counts[nz])

    def at_rank(r: int) -> float:  # value of the r-th smallest element (0-based)
        return float(values[np.searchsorted(cum, r, side="right")])

    pct = {}
    for key, q in PERCENTILES.items():
        h = (n - 1) * q / 100
        lo = math.floor(h)
        v0 = at_rank(lo)
        v1 = at_rank(min(lo + 1, n - 1))
        pct[key] = v0 + (h - lo) * (v1 - v0)
    return _finish_stats(mean, std, pct)


def stats_from_values(values: np.ndarray) -> dict[str, float]:
    v = np.asarray(values, dtype=np.float64).ravel()
    p = np.percentile(v, list(PERCENTILES.values()))
    return _finish_stats(float(v.mean()), float(v.std()), {k: float(x) for k, x in zip(PERCENTILES, p, strict=True)})


# ---------------------------------------------------------------------------------------------------- metadata
def ome_attrs(
    image_type: ImageType,
    voxel_size: float,
    translations: Sequence[Sequence[float]],
    software: str = "cryoet-data-portal-backend",
) -> dict[str, Any]:
    """``attributes.ome`` of the image group. ``translations[k]`` are level k's z, y, x translations in Angstrom."""
    datasets = []
    for k, t in enumerate(translations):
        if image_type == "volume":
            scale = [1.0, 1.0] + [voxel_size * 2**k] * 3
            translation = [0.0, 0.0, *map(float, t)]
        else:
            scale = [voxel_size, voxel_size * 2**k, voxel_size * 2**k]
            translation = [float(v) for v in t]
        datasets.append(
            {
                "path": str(k),
                "coordinateTransformations": [
                    {"type": "scale", "scale": scale},
                    {"type": "translation", "translation": translation},
                ],
            },
        )
    return {
        "version": "0.5",
        "multiscales": [
            {
                "name": MULTISCALE_NAME[image_type],
                "type": MULTISCALE_TYPE[image_type],
                "axes": AXES[image_type],
                "datasets": datasets,
                "metadata": {"software": software, "profile": f"{PROFILE['name']} {PROFILE['version']}"},
            },
        ],
    }


def dca_attrs(image_type: ImageType, normalization_statistics: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": DCA_VERSION,
        "url": DCA_SCHEMA_URL,
        "profile": dict(PROFILE),
        "image_type": image_type,
        "normalization_statistics": normalization_statistics,
    }


# ---------------------------------------------------------------------------------------------------- checker
@dataclass
class ProfileCheck:
    errors: list[str] = field(default_factory=list)

    def expect(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def _close(a: Sequence[float], b: Sequence[float], tol: float = 1e-6) -> bool:
    return len(a) == len(b) and all(abs(float(x) - float(y)) <= tol * max(1.0, abs(float(y))) for x, y in zip(a, b))


def check_profile(group_meta: dict[str, Any], array_metas: dict[str, dict[str, Any]]) -> list[str]:
    """Check an image group against the profile's MUST rules: ``group_meta`` is the group's ``zarr.json``,
    ``array_metas`` maps each level path to the array's ``zarr.json``. Returns the violations (empty if none)."""
    import jsonschema

    chk = ProfileCheck()
    attrs = group_meta.get("attributes", {})
    chk.expect(group_meta.get("zarr_format") == 3 and group_meta.get("node_type") == "group", "not a Zarr v3 group")
    ome, dca = attrs.get("ome", {}), attrs.get("dca", {})
    chk.expect(ome.get("version") == "0.5", "ome.version must be 0.5")
    try:
        jsonschema.validate({"dca": dca}, json.loads(PROFILE_SCHEMA_PATH.read_text()))
    except jsonschema.ValidationError as e:
        chk.errors.append(f"dca block: {e.message}")
    image_type = dca.get("image_type")
    if image_type not in AXES or len(ome.get("multiscales", [])) != 1:
        chk.errors.append("need dca.image_type 'volume' or 'tilt_series' and exactly one multiscales entry")
        return chk.errors
    ms = ome["multiscales"][0]
    chk.expect(ms.get("type") == MULTISCALE_TYPE[image_type], f"multiscales type must be {MULTISCALE_TYPE[image_type]}")
    chk.expect(ms.get("axes") == AXES[image_type], f"axes must be {AXES[image_type]}")
    datasets = ms.get("datasets", [])
    paths = [d.get("path") for d in datasets]
    chk.expect(paths == [str(k) for k in range(len(paths))], f"level paths must be 0, 1, 2, ...: {paths}")
    chk.expect(set(paths) == set(array_metas), f"arrays {sorted(array_metas)} do not match the levels {paths}")
    if not datasets or "0" not in array_metas:
        return chk.errors

    shape0 = array_metas["0"].get("shape", [])
    zyx = shape0[-3:]
    if image_type == "volume":
        chk.expect(shape0[:2] == [1, 1], "volume shape must be [1, 1, Z, Y, X]")
    n_levels = num_levels(zyx, image_type)
    chk.expect(len(datasets) == n_levels, f"expected {n_levels} levels, found {len(datasets)}")
    p = datasets[0]["coordinateTransformations"][0].get("scale", [None])[-1]
    stats = dca.get("normalization_statistics", {}).get("0", {})
    level_stats = stats.get("level_statistics", {})
    attrs0 = array_metas["0"].get("attributes", {})
    expected_shape = list(zyx)
    for k, d in enumerate(datasets):
        meta = array_metas.get(str(k))
        if meta is None:
            continue
        where = f"level {k}"
        transforms = d.get("coordinateTransformations", [])
        chk.expect([t.get("type") for t in transforms] == ["scale", "translation"], f"{where}: need scale + translation")
        if image_type == "volume":
            if k > 0:
                expected_shape = [-(-n // 2) for n in expected_shape]
            shape = [1, 1, *expected_shape]
            scale = [1.0, 1.0] + [p * 2**k] * 3
            translation = [0.0, 0.0] + [volume_translation(p, k)] * 3
            shard = [1, 1, *volume_shard_shape(expected_shape)]
            inner = [1, 1, INNER_CHUNK, INNER_CHUNK, INNER_CHUNK]
            chk.expect(
                meta.get("attributes", {}).get("scale_factor") == attrs0.get("scale_factor")
                and meta.get("attributes", {}).get("add_offset") == attrs0.get("add_offset")
                and "scale_factor" in attrs0
                and "add_offset" in attrs0,
                f"{where}: scale_factor/add_offset missing or different from level 0",
            )
        else:
            s = 2**k
            if k == 0:
                plans = None
                shape = list(zyx)
                translation = [0.0, 0.0, 0.0]
            else:
                plans = (fourier_plan(zyx[1], s), fourier_plan(zyx[2], s))
                shape = [zyx[0], plans[0].m, plans[1].m]
                translation = [0.0, plans[0].offset * p, plans[1].offset * p]
            scale = [p, p * s, p * s]
            shard = list(tilt_shard_shape(shape))
            inner = [1, INNER_CHUNK, INNER_CHUNK]
            sections = (stats if k == 0 else level_stats.get(str(k), {})).get("section_statistics", {})
            chk.expect(len(sections) == zyx[0], f"{where}: need section statistics for all {zyx[0]} sections")
        if len(transforms) == 2:
            chk.expect(_close(transforms[0].get("scale", []), scale), f"{where}: scale {transforms[0].get('scale')} != {scale}")
            chk.expect(
                _close(transforms[1].get("translation", []), translation, tol=1e-6),
                f"{where}: translation {transforms[1].get('translation')} != {translation}",
            )
        chk.expect(meta.get("zarr_format") == 3 and meta.get("node_type") == "array", f"{where}: not a Zarr v3 array")
        chk.expect(meta.get("shape") == shape, f"{where}: shape {meta.get('shape')} != {shape}")
        chk.expect(meta.get("data_type") == DATA_TYPE[image_type], f"{where}: data_type must be {DATA_TYPE[image_type]}")
        chk.expect(meta.get("dimension_names") == DIMENSION_NAMES[image_type], f"{where}: wrong dimension_names")
        chk.expect(meta.get("fill_value") == 0, f"{where}: fill_value must be 0")
        chk.expect(
            meta.get("chunk_key_encoding") == {"name": "default", "configuration": {"separator": "/"}},
            f"{where}: chunk_key_encoding must be default with '/'",
        )
        grid = meta.get("chunk_grid", {}).get("configuration", {}).get("chunk_shape")
        chk.expect(grid == shard, f"{where}: shard shape {grid} != {shard}")
        codecs = meta.get("codecs", [])
        ok = len(codecs) == 1 and codecs[0].get("name") == "sharding_indexed"
        conf = codecs[0].get("configuration", {}) if ok else {}
        chk.expect(ok, f"{where}: must use exactly the sharding_indexed codec")
        chk.expect(conf.get("chunk_shape") == inner, f"{where}: inner chunk shape {conf.get('chunk_shape')} != {inner}")
        chk.expect(conf.get("codecs") == INNER_CODECS[image_type], f"{where}: inner codecs {conf.get('codecs')}")
        chk.expect(conf.get("index_codecs") == INDEX_CODECS, f"{where}: index codecs {conf.get('index_codecs')}")
        chk.expect(conf.get("index_location", "end") == "end", f"{where}: index_location must be end")
        if k > 0:
            chk.expect(str(k) in level_stats, f"{where}: missing level_statistics")
    return chk.errors
