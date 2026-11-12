"""OME-Zarr writers.

Zarr v3 / OME-NGFF 0.5 (``--dca`` ingestion):

* ``write_volume`` and ``write_tilt_series`` write tomograms and tilt series under the cryoET profile v0.1
  (``common.cryoet_profile``).
* ``write_label_pyramid`` writes segmentation masks: a format-only port of the Zarr v2 masks (same dtypes, levels,
  chunks and scale-only transforms; label values under ``ome["image-label"]``).

Every v3 array is written in whole shards (or whole arrays for the unsharded masks): zarr-python reads back and
rewrites a shard on a partial write.

Zarr v2 / OME-NGFF 0.4 (default ingestion):

* ``write_v2_pyramid`` writes any pyramid exactly as the ingestion did with zarr-python 2 and ome-zarr 0.9 (checked
  against recorded output by ``tests/s3_import/test_zarr_v2_golden.py``).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Sequence

import numpy as np
import zarr
from zarr.codecs import BloscCodec, BytesCodec, ZstdCodec

from common import cryoet_profile as cp
from common.retry import s3_retry_decorator

if TYPE_CHECKING:
    from common.fs import FileSystemApi

CHUNK_KEY_ENCODING = {"name": "default", "separator": "/"}
MASK_AXES = [{"name": a, "type": "space", "unit": "angstrom"} for a in "zyx"]
TILT_STATS_MAX_VALUES = 64_000_000  # values per level used for tilt-series statistics (grid subsample)


@dataclass
class ProfileWriteResult:
    image_type: str
    level_shapes: list[tuple[int, ...]]
    encoding: cp.VolumeEncoding | None = None
    normalization_statistics: dict[str, Any] = field(default_factory=dict)


@s3_retry_decorator
def write_region(array: zarr.Array, selection: tuple[slice, ...], data: np.ndarray) -> None:
    array[selection] = data


@s3_retry_decorator
def open_new_group(fs: FileSystemApi, zarr_dir: str, zarr_format: int = 3) -> zarr.Group:
    """An empty group at ``zarr_dir``; anything already stored there (e.g. an earlier version of the same image in the
    other Zarr format) is removed first, so v2 and v3 metadata never coexist."""
    return zarr.open_group(fs.zarr_store(zarr_dir, read_only=False), mode="w", zarr_format=zarr_format)


def _shard_slices(shape: Sequence[int], shard: Sequence[int]) -> list[tuple[slice, ...]]:
    grids = [range(0, n, s) for n, s in zip(shape, shard, strict=True)]
    out: list[tuple[slice, ...]] = [()]
    for g, n, s in zip(grids, shape, shard, strict=True):
        out = [prev + (slice(i, min(i + s, n)),) for prev in out for i in g]
    return out


def _create_profile_array(
    group: zarr.Group,
    image_type: cp.ImageType,
    level: int,
    shape_zyx: Sequence[int],
    attributes: dict[str, Any] | None = None,
) -> zarr.Array:
    if image_type == "volume":
        shape = (1, 1, *shape_zyx)
        chunks = (1, 1, cp.INNER_CHUNK, cp.INNER_CHUNK, cp.INNER_CHUNK)
        shards = (1, 1, *cp.volume_shard_shape(shape_zyx))
        compressors = [ZstdCodec(level=3, checksum=False)]
        dtype = np.int16
    else:
        shape = tuple(shape_zyx)
        chunks = (1, cp.INNER_CHUNK, cp.INNER_CHUNK)
        shards = cp.tilt_shard_shape(shape_zyx)
        compressors = [BloscCodec(cname="lz4", clevel=5, shuffle="shuffle", typesize=4, blocksize=0)]
        dtype = np.float32
    return group.create_array(
        str(level),
        shape=shape,
        dtype=dtype,
        chunks=chunks,
        shards=shards,
        serializer=BytesCodec(endian="little"),
        compressors=compressors,
        fill_value=0,
        chunk_key_encoding=CHUNK_KEY_ENCODING,
        dimension_names=cp.DIMENSION_NAMES[image_type],
        attributes=attributes or {},
        overwrite=True,
    )


def volume_statistics(data: np.ndarray, slab: int = 64) -> cp.RunningStats:
    st = cp.RunningStats()
    for z0 in range(0, data.shape[0], slab):
        st.update(data[z0 : z0 + slab])
    return st


def write_volume(
    fs: FileSystemApi,
    data: np.ndarray,
    zarr_dir: str,
    voxel_size: float,
    software: str = "cryoet-data-portal-backend",
) -> ProfileWriteResult:
    """Write a tomogram (3-D ``z, y, x`` array of values) as a cryoET-profile volume: centred int16 codes,
    a mean-binned code pyramid, statistics in code units.

    Raises ``cryoet_profile.CorruptVolumeError`` for volumes the profile does not allow (non-finite values or
    a range beyond 1000 standard deviations).
    """
    st = volume_statistics(data)
    enc = cp.choose_volume_encoding(st)
    n_levels = cp.num_levels(data.shape, "volume")
    shapes = cp.volume_level_shapes(data.shape, n_levels)
    attrs = {"scale_factor": float(enc.scale_factor), "add_offset": float(enc.add_offset)}

    group = open_new_group(fs, zarr_dir)
    arrays = [_create_profile_array(group, "volume", k, shapes[k], attrs) for k in range(n_levels)]

    # Level 0, shard by shard; each shard's codes are binned into level 1 (shard edges are multiples of 128, so no
    # 2x2x2 block straddles two shards).
    tc = (slice(0, 1), slice(0, 1))  # the singleton t and c axes
    level1 = np.empty(shapes[1], dtype=np.int16)
    hist = np.zeros(65536, dtype=np.int64)
    for sel in _shard_slices(shapes[0], cp.volume_shard_shape(shapes[0])):
        codes = cp.encode_codes(data[sel], enc)
        hist += cp.code_histogram(codes)
        write_region(arrays[0], (*tc, *sel), codes[None, None])
        level1[tuple(slice(s.start // 2, -(-s.stop // 2)) for s in sel)] = cp.bin2_codes(codes)
        del codes
    histograms = [hist]

    level = level1
    for k in range(1, n_levels):
        histograms.append(cp.code_histogram(level))
        for sel in _shard_slices(shapes[k], cp.volume_shard_shape(shapes[k])):
            write_region(arrays[k], (*tc, *sel), level[sel][None, None])
        if k + 1 < n_levels:
            level = cp.bin2_codes(level)

    stats = {
        "0": {
            "dataset_statistics": cp.stats_from_histogram(histograms[0]),
            "level_statistics": {
                str(k): {"dataset_statistics": cp.stats_from_histogram(histograms[k])} for k in range(1, n_levels)
            },
        },
        "metadata": {"grid": 1},
    }
    translations = [[cp.volume_translation(voxel_size, k)] * 3 for k in range(n_levels)]
    group.attrs.update(
        {
            "ome": cp.ome_attrs("volume", voxel_size, translations, software=software),
            "dca": cp.dca_attrs("volume", stats),
        },
    )
    return ProfileWriteResult("volume", shapes, enc, stats)


def tilt_grid(shape: Sequence[int], max_values: int = TILT_STATS_MAX_VALUES) -> int:
    """Stride along y and x of the statistics subsample, so that level 0 contributes at most ``max_values``."""
    return max(1, math.ceil(math.sqrt(math.prod(shape) / max_values)))


def write_tilt_series(
    fs: FileSystemApi,
    data: np.ndarray,
    zarr_dir: str,
    pixel_size: float,
    software: str = "cryoet-data-portal-backend",
) -> ProfileWriteResult:
    """Write a tilt series (3-D ``z, y, x`` float array, one image per tilt) as a cryoET-profile tilt series: float32,
    Fourier-cropped levels computed from level 0 tilt by tilt, one shard per tilt image."""
    z, y, x = data.shape
    n_levels = cp.num_levels(data.shape, "tilt_series")
    plans = [None] + [(cp.fourier_plan(y, 2**k), cp.fourier_plan(x, 2**k)) for k in range(1, n_levels)]
    shapes: list[tuple[int, ...]] = [(z, y, x)] + [(z, py.m, px.m) for py, px in plans[1:]]  # type: ignore[union-attr]
    grid = tilt_grid(data.shape)

    group = open_new_group(fs, zarr_dir)
    arrays = [_create_profile_array(group, "tilt_series", k, shapes[k]) for k in range(n_levels)]
    section_stats: list[dict[str, dict[str, float]]] = [{} for _ in range(n_levels)]
    samples: list[list[np.ndarray]] = [[] for _ in range(n_levels)]
    for i in range(z):
        image = np.asarray(data[i], dtype=np.float32)
        if not np.isfinite(image).all():
            raise cp.CorruptVolumeError(f"tilt image {i} holds NaN or infinite values")
        levels = [image] + [
            cp.fourier_downsample(image, py, px).astype(np.float32) for py, px in plans[1:]  # type: ignore[misc]
        ]
        for k, img in enumerate(levels):
            write_region(arrays[k], (slice(i, i + 1), slice(None), slice(None)), img[None])
            sub = img[::grid, ::grid]
            section_stats[k][str(i)] = cp.stats_from_values(sub)
            samples[k].append(sub.ravel())

    stats = {
        "0": {
            "dataset_statistics": cp.stats_from_values(np.concatenate(samples[0])),
            "section_statistics": section_stats[0],
            "level_statistics": {
                str(k): {
                    "dataset_statistics": cp.stats_from_values(np.concatenate(samples[k])),
                    "section_statistics": section_stats[k],
                }
                for k in range(1, n_levels)
            },
        },
        "metadata": {"grid": grid},
    }
    translations = [[0.0, 0.0, 0.0]] + [
        [0.0, py.offset * pixel_size, px.offset * pixel_size] for py, px in plans[1:]  # type: ignore[misc]
    ]
    group.attrs.update(
        {
            "ome": cp.ome_attrs("tilt_series", pixel_size, translations, software=software),
            "dca": cp.dca_attrs("tilt_series", stats),
        },
    )
    return ProfileWriteResult("tilt_series", shapes, None, stats)


def write_label_pyramid(
    fs: FileSystemApi,
    pyramid: Sequence[np.ndarray],
    zarr_dir: str,
    voxel_spacing: Sequence[Sequence[float]],
    chunk_size: Sequence[int] = (256, 256, 256),
    label_values: Sequence[int] | None = None,
) -> None:
    """Write a segmentation-mask pyramid (3-D ``z, y, x`` levels) as Zarr v3 / OME-NGFF 0.5, with the conventions of
    the earlier Zarr v2 masks: unsharded chunks of ``chunk_size``, Blosc lz4 (level 5, byte shuffle), scale-only
    transforms; label values (instance masks) under ``ome["image-label"]``."""
    if len(pyramid) != len(voxel_spacing):
        raise ValueError(f"Length of voxel_size ({len(voxel_spacing)}) must match length of data ({len(pyramid)})")
    group = open_new_group(fs, zarr_dir)
    datasets = []
    for k, (arr, vs) in enumerate(zip(pyramid, voxel_spacing, strict=True)):
        z = group.create_array(
            str(k),
            shape=arr.shape,
            dtype=arr.dtype,
            chunks=tuple(int(c) for c in chunk_size),
            serializer=BytesCodec(endian="little"),
            compressors=[BloscCodec(cname="lz4", clevel=5, shuffle="shuffle", typesize=arr.dtype.itemsize)],
            fill_value=0,
            chunk_key_encoding=CHUNK_KEY_ENCODING,
            dimension_names=["z", "y", "x"],
            overwrite=True,
        )
        write_region(z, (slice(None),) * 3, np.ascontiguousarray(arr))
        datasets.append(
            {"path": str(k), "coordinateTransformations": [{"type": "scale", "scale": [float(v) for v in vs]}]},
        )
    ome: dict[str, Any] = {
        "version": "0.5",
        "multiscales": [{"axes": MASK_AXES, "datasets": datasets, "name": "/"}],
    }
    if label_values is not None:
        ome["image-label"] = {"colors": [{"label-value": int(v)} for v in label_values]}
    group.attrs.update({"ome": ome})


def write_v2_pyramid(
    fs: FileSystemApi,
    pyramid: Sequence[np.ndarray],
    zarr_dir: str,
    voxel_spacing: Sequence[Sequence[float]],
    chunk_size: Sequence[int] = (256, 256, 256),
    label_values: Sequence[int] | None = None,
) -> None:
    """Write a pyramid (3-D ``z, y, x`` levels) as Zarr v2 / OME-NGFF 0.4, exactly as the ingestion did with
    zarr-python 2 and ome-zarr 0.9: ``chunk_size`` chunks at every level, Blosc lz4 (level 5, byte shuffle), fill value
    0, '/' chunk keys, empty chunks written, scale-only transforms, and ``multiscales[0].metadata`` holding the label
    values of instance masks (``{}`` otherwise)."""
    import numcodecs
    from zarr.core.sync import sync

    if len(pyramid) != len(voxel_spacing):
        raise ValueError(f"Length of voxel_size ({len(voxel_spacing)}) must match length of data ({len(pyramid)})")
    group = open_new_group(fs, zarr_dir, zarr_format=2)
    datasets = []
    zc, yc, xc = (int(c) for c in chunk_size)
    for k, (arr, vs) in enumerate(zip(pyramid, voxel_spacing, strict=True)):
        z = group.create_array(
            str(k),
            shape=arr.shape,
            dtype=arr.dtype,
            chunks=(zc, yc, xc),
            # zarr-python 2's defaults, set explicitly: zarr-python 3 uses zstd and skips empty chunks
            compressors=numcodecs.Blosc(cname="lz4", clevel=5, shuffle=numcodecs.Blosc.SHUFFLE, blocksize=0),
            fill_value=0,
            order="C",
            chunk_key_encoding={"name": "v2", "separator": "/"},
            config={"write_empty_chunks": True},
            overwrite=True,
        )
        # zarr-python 3 also writes an empty .zattrs for each v2 array, which zarr-python 2 did not
        sync(group.store.delete(f"{k}/.zattrs"))
        nz, ny, nx = (int(n) for n in arr.shape)
        for z0 in range(0, nz, zc):
            for y0 in range(0, ny, yc):
                for x0 in range(0, nx, xc):
                    sel = (slice(z0, min(z0 + zc, nz)), slice(y0, min(y0 + yc, ny)), slice(x0, min(x0 + xc, nx)))
                    write_region(z, sel, np.asarray(arr[sel], dtype=arr.dtype, order="C"))
        datasets.append(
            {"path": str(k), "coordinateTransformations": [{"scale": [vs[0], vs[1], vs[2]], "type": "scale"}]},
        )
    metadata: dict[str, Any] = {}
    if label_values is not None:
        metadata["image-label"] = {"version": "0.4", "colors": [{"label-value": int(v)} for v in label_values]}
    # as ome_zarr.writer.write_multiscales_metadata (0.9) wrote it, with name "/"
    group.attrs["multiscales"] = [
        {"version": "0.4", "datasets": datasets, "name": "/", "metadata": metadata, "axes": MASK_AXES},
    ]
