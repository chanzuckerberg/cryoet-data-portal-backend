"""Migrate published Zarr v2 / OME-NGFF 0.4 images to Zarr v3 / OME-NGFF 0.5.

Reads the images of the given datasets from a source root (default: the public bucket, anonymously) and writes the
converted images, with their updated metadata JSON and Neuroglancer configs, to the same relative keys under a
destination root (default: the staging bucket), from where they can be published:

* tomograms -> cryoET storage profile v0.1 volumes (int16 codes with scale_factor/add_offset, mean-binned levels),
* tilt series -> cryoET storage profile v0.1 tilt series (float32, Fourier-cropped levels),
* segmentation masks (semantic and instance) -> the same pyramids, dtypes and chunks in Zarr v3 (format-only).

Every new image is converted from level 0 of the source and verified against it before its migration marker
(``attributes.cryoet_data_portal.migration``, with a fingerprint of the source metadata) is written. Images whose
marker matches the source are skipped, so runs can be repeated. MRC files, Neuroglancer precomputed annotations and
meshes, and key images are not touched.

    python migrate_zarr_v3.py plan --dataset 10001
    python migrate_zarr_v3.py run --dataset 10001 [--dest-root s3://... | /local/dir] [--on-existing skip|fail|replace]
    python migrate_zarr_v3.py verify --dataset 10001
    python migrate_zarr_v3.py publish-plan --dataset 10001   # prints the commands; runs nothing

After publishing a dataset (``aws s3 sync --delete`` per image, so no Zarr v2 keys remain next to the v3 ones), its
database records (viewer config, file sizes, scales) must be re-imported: ``enqueue_runs.py db-import``.
"""

from __future__ import annotations

import datetime
import fnmatch
import hashlib
import json
import math
import os
import posixpath
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, dataclass
from typing import Any, Iterable

import click
import numpy as np
import zarr
from cryoet_data_portal_neuroglancer.io import OmeZarrImage
from cryoet_data_portal_neuroglancer.models.json_generator import EXTRA_AXES
from zarr.abc.store import Store

from common import cryoet_profile as cp
from common.ome_zarr_writer import write_label_pyramid, write_tilt_series, write_volume

ENTITY_PATTERNS = {
    "tomogram": "*/Reconstructions/VoxelSpacing*/Tomograms/*/*.zarr",
    "tiltseries": "*/TiltSeries/*/*.zarr",
    "segmentationmask": "*/Reconstructions/VoxelSpacing*/Annotations/*/*_segmentationmask.zarr",
    "instancesegmentationmask": "*/Reconstructions/VoxelSpacing*/Annotations/*/*_instancesegmentationmask.zarr",
}
METADATA_JSON = {"tomogram": "tomogram_metadata.json", "tiltseries": "tiltseries_metadata.json"}
MARKER_KEY = "cryoet_data_portal"
TOOL = "ingestion_tools/scripts/migrate_zarr_v3.py"
TOOL_VERSION = 1
DEFAULT_SRC_ROOT = "s3://cryoet-data-portal-public"
DEFAULT_DEST_ROOT = "s3://cryoet-data-portal-staging"


# ---------------------------------------------------------------------------------------------------- storage roots
class Root:
    """A bucket prefix (``s3://bucket/prefix``) or a local directory holding the Portal's layout."""

    def __init__(self, url: str, anon: bool = False, endpoint_url: str | None = None):
        self.url = url.rstrip("/")
        self.anon = anon
        self.endpoint_url = endpoint_url
        if self.is_s3:
            import s3fs

            self.fs = s3fs.S3FileSystem(**self.storage_options)
        else:
            import fsspec

            self.fs = fsspec.filesystem("file")

    @property
    def is_s3(self) -> bool:
        return self.url.startswith("s3://")

    @property
    def storage_options(self) -> dict[str, Any]:
        options: dict[str, Any] = {"anon": self.anon, "use_listings_cache": False}
        if self.endpoint_url:
            options["client_kwargs"] = {"endpoint_url": self.endpoint_url}
        return options

    def path(self, rel: str) -> str:
        return f"{self.url}/{rel}" if rel else self.url

    def rel(self, path: str) -> str:
        base = self.url.split("://", 1)[-1]
        return posixpath.relpath(path.split("://", 1)[-1], base)

    def zarr_store(self, path: str, read_only: bool = True) -> Store:
        """Duck-types ``FileSystemApi.zarr_store`` for the writers (``path`` is a full path under this root)."""
        from zarr.storage import FsspecStore, LocalStore

        if self.is_s3:
            return FsspecStore.from_url(path, storage_options=self.storage_options, read_only=read_only)
        if not read_only:
            os.makedirs(path, exist_ok=True)
        return LocalStore(path, read_only=read_only)

    def store(self, rel: str, read_only: bool = True) -> Store:
        return self.zarr_store(self.path(rel), read_only=read_only)

    def exists(self, rel: str) -> bool:
        return self.fs.exists(self.path(rel))

    def read_bytes(self, rel: str) -> bytes:
        with self.fs.open(self.path(rel), "rb") as f:
            return f.read()

    def read_json(self, rel: str) -> Any:
        return json.loads(self.read_bytes(rel))

    def write_text(self, rel: str, text: str) -> None:
        if not self.is_s3:
            os.makedirs(posixpath.dirname(self.path(rel)), exist_ok=True)
        with self.fs.open(self.path(rel), "w") as f:
            f.write(text)

    def write_json(self, rel: str, obj: Any) -> None:
        self.write_text(rel, json.dumps(obj, indent=4))

    def glob(self, pattern: str) -> list[str]:
        return sorted(self.rel(p) for p in self.fs.glob(self.path(pattern)))

    def datasets(self) -> list[str]:
        names = [posixpath.basename(p.rstrip("/")) for p in self.fs.ls(self.url, detail=False)]
        return sorted(n for n in names if n.isdigit())


@dataclass(frozen=True)
class RootSpec:
    """Picklable description of a Root, for worker processes."""

    url: str
    anon: bool = False
    endpoint_url: str | None = None

    def open(self) -> Root:
        return Root(self.url, self.anon, self.endpoint_url)


# ---------------------------------------------------------------------------------------------------- discovery
@dataclass(frozen=True)
class Item:
    entity: str
    rel: str  # key of the .zarr directory, relative to the root


def discover(root: Root, datasets: Iterable[str], entities: Iterable[str], run_pattern: str | None = None) -> list[Item]:
    items = []
    for dataset in datasets:
        for entity in entities:
            for rel in root.glob(f"{dataset}/{ENTITY_PATTERNS[entity]}"):
                run = rel.split("/")[1]
                if run_pattern and not fnmatch.fnmatch(run, run_pattern):
                    continue
                items.append(Item(entity, rel))
    return items


def fingerprint(root: Root, rel: str, image: OmeZarrImage) -> str:
    """SHA-256 of the source's Zarr v2 metadata files: changes whenever the source image is rewritten."""
    h = hashlib.sha256()
    for name in [".zgroup", ".zattrs"] + [f"{d['path']}/.zarray" for d in image.datasets]:
        h.update(name.encode())
        h.update(root.read_bytes(f"{rel}/{name}"))
    return h.hexdigest()


def read_marker(root: Root, rel: str) -> dict[str, Any] | None:
    try:
        meta = root.read_json(f"{rel}/zarr.json")
    except FileNotFoundError:
        return None
    return meta.get("attributes", {}).get(MARKER_KEY, {}).get("migration")


# ---------------------------------------------------------------------------------------------------- sidecar files
def neuroglancer_config_rel(tomogram_rel: str) -> str:
    """``.../VoxelSpacing{vs}/Tomograms/{id}/{run}.zarr`` -> ``.../VoxelSpacing{vs}/NeuroglancerPrecompute/{id}-neuroglancer_config.json``"""
    vs_dir, rest = tomogram_rel.split("/Tomograms/", 1)
    return f"{vs_dir}/NeuroglancerPrecompute/{rest.split('/')[0]}-neuroglancer_config.json"


def patch_neuroglancer_config(
    config: dict[str, Any],
    zarr_rel: str,
    scale_factor: float,
    add_offset: float,
    extra_axes: tuple[str, ...] = ("t", "c"),
) -> int:
    """Update the image layer(s) of a converted tomogram: list the t/c axes of the 5-D source in the transform (mapped
    to local dimensions) and convert the contrast controls (``range``/``window``) to code units. The source URL is kept
    (``zarr://``). Returns the number of layers patched."""
    patched = 0
    for layer in config.get("layers", []):
        source = layer.get("source")
        url = source.get("url") if isinstance(source, dict) else source
        if layer.get("type") != "image" or not isinstance(url, str) or not url.rstrip("/").endswith(zarr_rel):
            continue
        if isinstance(source, dict) and "transform" in source:
            transform = source["transform"]
            for axis in extra_axes:
                input_name, output_name, scale_unit = EXTRA_AXES[axis]
                transform.setdefault("inputDimensions", {})[input_name] = list(scale_unit)
                transform.setdefault("outputDimensions", {})[output_name] = list(scale_unit)
        for control in layer.get("shaderControls", {}).values():
            if not isinstance(control, dict):
                continue
            for key in ("range", "window"):
                if isinstance(control.get(key), list):
                    control[key] = [(float(v) - add_offset) / scale_factor for v in control[key]]
        patched += 1
    return patched


def update_metadata_json(src: Root, dest: Root, item: Item, dest_group: zarr.Group) -> str | None:
    name = METADATA_JSON.get(item.entity)
    if name is None:
        return None
    rel = f"{posixpath.dirname(item.rel)}/{name}"
    if not src.exists(rel):
        return None
    metadata = src.read_json(rel)
    scales = []
    for dataset in OmeZarrImage(dest_group).datasets:
        z, y, x = (int(n) for n in dest_group[dataset["path"]].shape[-3:])
        scales.append({"z": z, "y": y, "x": x})
    metadata["scales"] = scales
    metadata["size"] = scales[0]
    dest.write_json(rel, metadata)
    return rel


# ---------------------------------------------------------------------------------------------------- conversion
@dataclass
class Result:
    entity: str
    rel: str
    status: str  # migrated | verified | skipped-up-to-date | skipped-existing | would-migrate | not-v2 | failed
    fingerprint: str | None = None
    encoding: dict[str, Any] | None = None
    level_shapes: list[list[int]] | None = None
    max_error: float | None = None
    rms_ratio: float | None = None
    sidecars: list[str] | None = None
    error: str | None = None
    seconds: float = 0.0


def _load_levels(image: OmeZarrImage, all_levels: bool) -> list[np.ndarray]:
    paths = [d["path"] for d in image.datasets] if all_levels else [image.datasets[0]["path"]]
    return [np.asarray(image.group[p][:]) for p in paths]


def verify(item: Item, src_levels: list[np.ndarray], dest: Root, dest_group: zarr.Group, result: Result) -> None:
    """Compare the destination with the source and check the profile (on the stored zarr.json documents); raises
    AssertionError on a mismatch."""
    if item.entity in ("tomogram", "tiltseries"):
        group_meta = dest.read_json(f"{item.rel}/zarr.json")
        arrays = {
            d["path"]: dest.read_json(f"{item.rel}/{d['path']}/zarr.json")
            for d in group_meta["attributes"]["ome"]["multiscales"][0]["datasets"]
        }
        errors = cp.check_profile(group_meta, arrays)
        assert not errors, "; ".join(errors)
    if item.entity == "tomogram":
        source = src_levels[0]
        attrs = dest_group["0"].attrs
        sf, ao = float(attrs["scale_factor"]), float(attrs["add_offset"])
        max_err, sq = 0.0, 0.0
        codes = dest_group["0"]
        for z0 in range(0, source.shape[0], 32):
            decoded = cp.decode_codes(codes[0, 0, z0 : z0 + 32], {"scale_factor": sf, "add_offset": ao})
            diff = decoded - source[z0 : z0 + 32].astype(np.float64)
            max_err = max(max_err, float(np.abs(diff).max()))
            sq += float(np.square(diff).sum())
        result.max_error = max_err
        # RMS error relative to the rounding-noise expectation scale_factor / sqrt(12) (about 1 for continuous data)
        result.rms_ratio = math.sqrt(sq / source.size) / (sf / math.sqrt(12))
        bound = 0.0 if result.encoding and result.encoding.get("integer") else sf / 2 * (1 + 1e-9)
        assert max_err <= bound, f"max |decoded - source| = {max_err:.6g} exceeds {bound:.6g}"
    elif item.entity == "tiltseries":
        np.testing.assert_array_equal(dest_group["0"][:], src_levels[0], err_msg="tilt-series level 0 differs")
    else:
        for k, level in enumerate(src_levels):
            np.testing.assert_array_equal(dest_group[str(k)][:], level, err_msg=f"mask level {k} differs")


def migrate_item(
    item: Item,
    src_spec: RootSpec,
    dest_spec: RootSpec,
    on_existing: str = "skip",
    dry_run: bool = False,
) -> Result:
    t0 = time.time()
    result = Result(item.entity, item.rel, "failed")
    try:
        src, dest = src_spec.open(), dest_spec.open()
        src_group = zarr.open_group(src.store(item.rel), mode="r")
        if src_group.metadata.zarr_format != 2:
            result.status = "not-v2"
            return result
        image = OmeZarrImage(src_group)
        result.fingerprint = fingerprint(src, item.rel, image)

        marker = read_marker(dest, item.rel)
        if marker and marker.get("source_fingerprint") == result.fingerprint and on_existing != "replace":
            result.status = "skipped-up-to-date"
            return result
        if dest.exists(item.rel) and on_existing != "replace":
            if on_existing == "fail":
                raise FileExistsError(f"{dest.path(item.rel)} exists and was not migrated from this source")
            result.status = "skipped-existing"
            return result
        if dry_run:
            result.status = "would-migrate"
            return result

        dest_path = dest.path(item.rel)
        levels = _load_levels(image, all_levels=item.entity not in ("tomogram", "tiltseries"))
        spacing = float(image.scale(0)[-1])
        if item.entity == "tomogram":
            written = write_volume(dest, np.asarray(levels[0], dtype=np.float32), dest_path, round(spacing, 3))
            result.encoding = asdict(written.encoding)
        elif item.entity == "tiltseries":
            written = write_tilt_series(dest, np.asarray(levels[0], dtype=np.float32), dest_path, round(spacing, 3))
        else:
            write_label_pyramid(
                dest,
                levels,
                dest_path,
                voxel_spacing=[image.scale(k)[-3:] for k in range(len(levels))],
                chunk_size=image.array(0).chunks,
                label_values=image.label_values,
            )
        dest_group = zarr.open_group(dest.store(item.rel, read_only=False), mode="r+")
        result.level_shapes = [list(dest_group[d["path"]].shape) for d in OmeZarrImage(dest_group).datasets]
        verify(item, levels, dest, dest_group, result)

        sidecars = []
        if rel := update_metadata_json(src, dest, item, dest_group):
            sidecars.append(rel)
        if item.entity == "tomogram":
            ng_rel = neuroglancer_config_rel(item.rel)
            if src.exists(ng_rel):
                config = src.read_json(ng_rel)
                enc = result.encoding or {}
                if patch_neuroglancer_config(config, item.rel, enc["scale_factor"], enc["add_offset"]):
                    dest.write_json(ng_rel, config)
                    sidecars.append(ng_rel)
        result.sidecars = sidecars

        # the marker goes last: an image without it is incomplete and is redone (or flagged) by the next run
        dest_group.attrs[MARKER_KEY] = {
            "migration": {
                "from": "zarr_v2/ome-ngff-0.4",
                "source": src.path(item.rel),
                "source_fingerprint": result.fingerprint,
                "tool": TOOL,
                "tool_version": TOOL_VERSION,
                "time": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            },
        }
        result.status = "migrated"
    except Exception as e:  # noqa: BLE001 - one bad image must not stop a dataset
        result.status = "failed"
        result.error = f"{type(e).__name__}: {e}\n{traceback.format_exc(limit=3)}"
    finally:
        result.seconds = round(time.time() - t0, 2)
    return result


def verify_item(item: Item, src_spec: RootSpec, dest_spec: RootSpec) -> Result:
    t0 = time.time()
    result = Result(item.entity, item.rel, "failed")
    try:
        src, dest = src_spec.open(), dest_spec.open()
        image = OmeZarrImage(zarr.open_group(src.store(item.rel), mode="r"))
        result.fingerprint = fingerprint(src, item.rel, image)
        dest_group = zarr.open_group(dest.store(item.rel), mode="r")
        marker = dict(dest_group.attrs).get(MARKER_KEY, {}).get("migration")
        assert marker and marker.get("source_fingerprint") == result.fingerprint, "missing or stale migration marker"
        if item.entity == "tomogram":
            result.encoding = {
                "scale_factor": dest_group["0"].attrs["scale_factor"],
                "add_offset": dest_group["0"].attrs["add_offset"],
                "integer": dest_group["0"].attrs["scale_factor"] == 1.0
                and float(dest_group["0"].attrs["add_offset"]).is_integer(),
            }
        levels = _load_levels(image, all_levels=item.entity not in ("tomogram", "tiltseries"))
        result.level_shapes = [list(dest_group[d["path"]].shape) for d in OmeZarrImage(dest_group).datasets]
        verify(item, levels, dest, dest_group, result)
        result.status = "verified"
    except Exception as e:  # noqa: BLE001
        result.error = f"{type(e).__name__}: {e}"
    finally:
        result.seconds = round(time.time() - t0, 2)
    return result


# ---------------------------------------------------------------------------------------------------- CLI
def common_options(func):
    options = [
        click.option("--src-root", default=DEFAULT_SRC_ROOT, show_default=True, help="Root holding the v2 images"),
        click.option("--src-anon/--no-src-anon", default=True, show_default=True, help="Read the source anonymously"),
        click.option("--dest-root", default=DEFAULT_DEST_ROOT, show_default=True, help="Root for the v3 images"),
        click.option("--endpoint-url", default=None, help="S3 endpoint (e.g. moto) for both roots"),
        click.option("--dataset", "datasets", multiple=True, help="Dataset id (repeatable)"),
        click.option("--all-datasets", is_flag=True, help="Every dataset under the source root"),
        click.option(
            "--entity",
            "entities",
            multiple=True,
            type=click.Choice(sorted(ENTITY_PATTERNS)),
            help="Entity types (repeatable; default: all)",
        ),
        click.option("--run-name", default=None, help="Shell-style pattern for run names"),
        click.option("--workers", default=1, show_default=True, help="Images converted in parallel"),
        click.option("--manifest", default=None, help="JSONL manifest path (default: under the destination root)"),
    ]
    for option in reversed(options):
        func = option(func)
    return func


def _setup(src_root, src_anon, dest_root, endpoint_url, datasets, all_datasets, entities, run_name):
    src_spec = RootSpec(src_root, anon=src_anon, endpoint_url=endpoint_url)
    dest_spec = RootSpec(dest_root, anon=False, endpoint_url=endpoint_url)
    src = src_spec.open()
    if all_datasets:
        datasets = src.datasets()
    if not datasets:
        raise click.UsageError("give --dataset (repeatable) or --all-datasets")
    items = discover(src, datasets, entities or sorted(ENTITY_PATTERNS), run_name)
    return src_spec, dest_spec, list(datasets), items


def _run_all(func, items: list[Item], workers: int, *args) -> list[Result]:
    if workers <= 1:
        return [func(item, *args) for item in items]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(func, items, *[[a] * len(items) for a in args]))


def _write_manifest(results: list[Result], dest_spec: RootSpec, manifest: str | None, command: str, datasets) -> str:
    lines = "".join(json.dumps(asdict(r)) + "\n" for r in results)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if manifest is None:
        rel = f"_migrations/zarr_v3/{stamp}-{command}-{'-'.join(datasets)[:60]}.jsonl"
        dest_spec.open().write_text(rel, lines)
        return dest_spec.open().path(rel)
    os.makedirs(os.path.dirname(os.path.abspath(manifest)), exist_ok=True)
    with open(manifest, "w") as f:
        f.write(lines)
    return manifest


def _summarize(results: list[Result]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for r in results:
        summary[r.status] = summary.get(r.status, 0) + 1
    return summary


@click.group()
def cli():
    pass


@cli.command()
@common_options
def plan(src_root, src_anon, dest_root, endpoint_url, datasets, all_datasets, entities, run_name, workers, manifest):
    """List the images that would be migrated, and their state at the destination."""
    src_spec, dest_spec, datasets, items = _setup(
        src_root, src_anon, dest_root, endpoint_url, datasets, all_datasets, entities, run_name,
    )
    results = _run_all(migrate_item, items, workers, src_spec, dest_spec, "skip", True)
    for r in results:
        click.echo(f"{r.status:20s} {r.entity:25s} {r.rel}")
    click.echo(json.dumps(_summarize(results)))
    if manifest:
        _write_manifest(results, dest_spec, manifest, "plan", datasets)


@cli.command()
@common_options
@click.option(
    "--on-existing",
    type=click.Choice(["skip", "fail", "replace"]),
    default="skip",
    show_default=True,
    help="What to do with a destination image that was not migrated from this source "
    "(images whose migration marker matches the source are always skipped, except with replace)",
)
@click.option("--dry-run", is_flag=True)
def run(src_root, src_anon, dest_root, endpoint_url, datasets, all_datasets, entities, run_name, workers, manifest,
        on_existing, dry_run):
    """Convert and verify the images; write a JSONL manifest."""
    src_spec, dest_spec, datasets, items = _setup(
        src_root, src_anon, dest_root, endpoint_url, datasets, all_datasets, entities, run_name,
    )
    results = _run_all(migrate_item, items, workers, src_spec, dest_spec, on_existing, dry_run)
    for r in results:
        click.echo(f"{r.status:20s} {r.seconds:8.1f}s {r.rel}" + (f"\n    {r.error}" if r.error else ""))
    summary = _summarize(results)
    click.echo(json.dumps(summary))
    if not dry_run:
        click.echo(f"manifest: {_write_manifest(results, dest_spec, manifest, 'run', datasets)}")
    if summary.get("failed"):
        sys.exit(1)


@cli.command(name="verify")
@common_options
def verify_command(src_root, src_anon, dest_root, endpoint_url, datasets, all_datasets, entities, run_name, workers,
                   manifest):
    """Re-check migrated images against their sources (marker, profile rules, decoded values)."""
    src_spec, dest_spec, datasets, items = _setup(
        src_root, src_anon, dest_root, endpoint_url, datasets, all_datasets, entities, run_name,
    )
    results = _run_all(verify_item, items, workers, src_spec, dest_spec)
    for r in results:
        click.echo(f"{r.status:10s} {r.rel}" + (f"  {r.error}" if r.error else ""))
    summary = _summarize(results)
    click.echo(json.dumps(summary))
    if manifest:
        _write_manifest(results, dest_spec, manifest, "verify", datasets)
    if summary.get("failed"):
        sys.exit(1)


@cli.command(name="publish-plan")
@common_options
@click.option("--publish-root", default=DEFAULT_SRC_ROOT, show_default=True, help="Where the images are published")
def publish_plan(src_root, src_anon, dest_root, endpoint_url, datasets, all_datasets, entities, run_name, workers,
                 manifest, publish_root):
    """Print the commands that publish verified images (runs nothing).

    Each image is synced with --delete, so no Zarr v2 keys remain next to the v3 ones (Neuroglancer refuses a store
    with both); then its metadata JSON and viewer config are copied, the CDN cache is invalidated and the dataset's
    database records are re-imported."""
    src_spec, dest_spec, datasets, items = _setup(
        src_root, src_anon, dest_root, endpoint_url, datasets, all_datasets, entities, run_name,
    )
    dest = dest_spec.open()
    for item in items:
        marker = read_marker(dest, item.rel)
        if not marker:
            click.echo(f"# not migrated: {item.rel}")
            continue
        click.echo(f"aws s3 sync --delete {dest.path(item.rel)}/ {publish_root}/{item.rel}/")
        sidecars = [f"{posixpath.dirname(item.rel)}/{METADATA_JSON[item.entity]}"] if item.entity in METADATA_JSON else []
        if item.entity == "tomogram":
            sidecars.append(neuroglancer_config_rel(item.rel))
        for rel in sidecars:
            if dest.exists(rel):
                click.echo(f"aws s3 cp {dest.path(rel)} {publish_root}/{rel}")
    click.echo("# then: invalidate the CDN for the published prefixes, and per dataset:")
    for dataset in datasets:
        click.echo(f"python enqueue_runs.py db-import --environment prod --include-dataset {dataset}")


if __name__ == "__main__":
    cli()
