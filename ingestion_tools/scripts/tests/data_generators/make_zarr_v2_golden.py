"""Golden output of the default (Zarr v2 / OME-NGFF 0.4) ingestion path, recorded with origin/main's code from before
the move to zarr-python 3 (zarr 2.18, ome-zarr 0.9, numpy 1.26).

``tests/s3_import/test_zarr_v2_golden.py`` runs the same cases with the current code and requires identical output:
- the same files;
- equal ``.zgroup``/``.zarray``/``.zattrs`` (compared as parsed JSON);
- every chunk with identical content and an identical Blosc header (version, flags, typesize, uncompressed size, block
  size, compressed size);
- the same MRC data and header (except the label holding the conversion time).

Raw chunk bytes are not compared: zarr-python 2 ran Blosc with up to 8 threads, whose blocks land in the frame in
completion order, so the old code itself wrote different bytes for the same data from run to run.

To regenerate (only needed if the cases change; the reference is the code before the switch):

    git worktree add --detach /tmp/backend-origin-main <commit before the switch>
    uv venv -p 3.11 /tmp/zarr2-golden-env
    uv pip install --python /tmp/zarr2-golden-env/bin/python zarr==2.18.7 ome-zarr==0.9.0 numpy==1.26.4 \
        numcodecs==0.15.1 mrcfile==1.5.4 scikit-image==0.22.0 scipy==1.16.3 dask==2025.12.0 tenacity==9.1.2 \
        s3fs==2026.9.0 fsspec==2026.9.0 boto3 pyyaml==6.0.3
    cd /tmp && PYTHONPATH=/tmp/backend-origin-main/ingestion_tools/scripts /tmp/zarr2-golden-env/bin/python \
        <repo>/ingestion_tools/scripts/tests/data_generators/make_zarr_v2_golden.py \
        <repo>/ingestion_tools/scripts/tests/fixtures/zarr_v2_golden.json

Only numpy and mrcfile are imported at module level, so the test can reuse the case definitions.
"""

import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

import mrcfile
import numpy as np

SAMPLE_TOMOS = Path(__file__).resolve().parents[4] / "test_infra" / "test_files" / "input_bucket" / "sample_tomos"
METADATA_FILES = {".zarray", ".zattrs", ".zgroup", "zarr.json"}


def _volume(name: str) -> tuple[np.ndarray, float]:
    """Deterministic synthetic inputs (arithmetic, no RNG)."""
    if name == "tomo_float":
        z, y, x = np.indices((37, 70, 45)).astype(np.float64)
        return (np.sin(0.31 * z) * np.cos(0.17 * y) + 0.013 * x - 0.4 * np.sin(0.05 * x * y)).astype(np.float32), 10.0
    if name == "tilt":
        z, y, x = np.indices((3, 66, 43)).astype(np.float64)
        return (100.0 + 7.0 * np.cos(0.21 * y + z) * np.sin(0.13 * x) + 0.5 * x).astype(np.float32), 1.68
    if name == "labels":
        z, y, x = np.indices((20, 30, 40))
        return (((3 * z + 5 * y + 7 * x) // 11) % 4).astype(np.int8), 10.0
    if name == "probability":
        z, y, x = np.indices((20, 30, 40)).astype(np.float64)
        return (0.5 + 0.5 * np.sin(0.3 * z) * np.cos(0.2 * y + 0.1 * x)).astype(np.float32), 10.0
    if name == "instances":
        z, y, x = np.indices((20, 30, 40))
        return ((1 + (z // 6) * 9 + (y // 8) * 3 + (x // 11)) * ((x + y + z) % 4 != 0)).astype(np.uint16), 10.0
    raise KeyError(name)


def tilt_header_mapper(header) -> None:
    # as TiltSeriesImporter.mrc_header_mapper
    header.ispg = 0
    header.mz = 1
    header.cella.z = 1 * 1.68


# name -> (input, make_pyramids keyword arguments); "sample:" inputs come from test_infra/test_files
CASES: dict[str, tuple[str, dict[str, Any]]] = {
    "tomogram_mrc": ("tomo_float", {"voxel_spacing": 10.0}),
    "tomogram_sample_mrc": ("sample:input_mrc.mrc", {}),
    "tomogram_v2_zarr_source": ("sample:input_omezarr.zarr", {}),
    "tiltseries": ("tilt", {"scale_z_axis": False, "voxel_spacing": 1.68, "chunk_size": (1, 1024, 1024)}),
    "semantic_mask_label": ("labels", {"label": 2, "dtype": "int8", "voxel_spacing": 10.0}),
    "semantic_mask_rescaled": ("labels", {"label": 1, "dtype": "int8", "voxel_spacing": 10.0, "scale_0_dims": (30, 45, 60)}),
    "semantic_mask_threshold": ("probability", {"label": 1, "threshold": 0.5, "dtype": "int8", "voxel_spacing": 10.0}),
    "instance_mask": ("instances", {"multilabels": True, "voxel_spacing": 10.0}),
    "unsigned_int8_mrc": ("sample:unsigned_ints.mrc", {}),
}


def _jsonable(v: Any) -> Any:
    if isinstance(v, bytes):
        return v.decode("latin-1")
    if isinstance(v, (list, tuple)):
        return [_jsonable(i) for i in v]
    if isinstance(v, float) and v != v:
        return "nan"
    return v


def _sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def chunk_fingerprint(frame: bytes) -> dict[str, Any]:
    """Content hash and Blosc header of a Blosc-compressed chunk (independent of the block order in the frame)."""
    import numcodecs

    return {
        "content_sha256": _sha256(numcodecs.Blosc().decode(frame)),
        "blosc_version": frame[0],
        "blosc_flags": frame[2],
        "typesize": frame[3],
        "nbytes": int.from_bytes(frame[4:8], "little"),
        "blocksize": int.from_bytes(frame[8:12], "little"),
        "cbytes": int.from_bytes(frame[12:16], "little"),
    }


def snapshot(out_prefix: Path) -> dict[str, Any]:
    zarr_dir = Path(f"{out_prefix}.zarr")
    files: dict[str, Any] = {}
    for p in sorted(zarr_dir.rglob("*")):
        if p.is_file():
            rel = p.relative_to(zarr_dir).as_posix()
            files[rel] = json.loads(p.read_text()) if p.name in METADATA_FILES else chunk_fingerprint(p.read_bytes())
    with mrcfile.open(f"{out_prefix}.mrc", permissive=True) as m:
        header = {
            name: _jsonable(np.asarray(m.header[name]).tolist()) for name in m.header.dtype.names if name != "label"
        }
        ext = m.extended_header
        mrc = {
            "dtype": str(m.data.dtype),
            "shape": list(m.data.shape),
            "data_sha256": _sha256(np.ascontiguousarray(m.data).tobytes()),
            "header": header,
            "extended_header_sha256": None if ext is None else _sha256(np.asarray(ext).tobytes()),
        }
    return {"zarr": files, "mrc": mrc}


def _input_path(spec: str, workdir: Path, sample_dir: Path = SAMPLE_TOMOS) -> Path:
    if spec.startswith("sample:"):
        src = sample_dir / spec.split(":", 1)[1]
        dst = workdir / "inputs" / src.name
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            (shutil.copytree if src.is_dir() else shutil.copy)(src, dst)
        return dst
    dst = workdir / "inputs" / f"{spec}.mrc"
    if not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        data, voxel = _volume(spec)
        with mrcfile.new(dst, overwrite=True) as m:
            m.set_data(data)
            m.voxel_size = voxel
    return dst


def run_case(
    make_pyramids: Callable[..., Any],
    fs: Any,
    workdir: Path,
    name: str,
    sample_dir: Path = SAMPLE_TOMOS,
) -> dict[str, Any]:
    """Run one case; ``sample_dir`` holds test_infra/test_files/input_bucket/sample_tomos (or a copy of it)."""
    spec, kwargs = CASES[name]
    kwargs = dict(kwargs)
    if name == "tiltseries":
        kwargs["header_mapper"] = tilt_header_mapper
    src = _input_path(spec, workdir, sample_dir)
    out = workdir / "out" / name / "output"
    out.parent.mkdir(parents=True, exist_ok=True)
    make_pyramids(fs, str(out), str(src), **kwargs)
    return snapshot(out)


def main(dest: str) -> None:
    from common.fs import FileSystemApi
    from common.image import make_pyramids

    fs = FileSystemApi.get_fs_api(mode="local", force_overwrite=False)
    with tempfile.TemporaryDirectory() as tmp:
        golden = {name: run_case(make_pyramids, fs, Path(tmp), name) for name in CASES}
    Path(dest).write_text(json.dumps(golden, indent=1, sort_keys=True) + "\n")
    print({name: len(g["zarr"]) for name, g in golden.items()})


if __name__ == "__main__":
    main(sys.argv[1])
