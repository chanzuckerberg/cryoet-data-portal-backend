"""End-to-end test of migrate_zarr_v3.py on Portal-like Zarr v2 / OME-NGFF 0.4 images in moto."""

import json
import os

import numpy as np
import pytest
import zarr
from click.testing import CliRunner
from cryoet_data_portal_neuroglancer.io import open_omezarr
from cryoet_data_portal_neuroglancer.state_generator import combine_json_layers, generate_image_layer
from migrate_zarr_v3 import (
    Item,
    Root,
    RootSpec,
    cli,
    discover,
    migrate_item,
    neuroglancer_config_rel,
    verify_item,
)

from common import cryoet_profile as cp

DATASET = "10001"
VS = "Reconstructions/VoxelSpacing10.000"
TOMO_CONT = f"{DATASET}/TS_run1/{VS}/Tomograms/100/TS_run1.zarr"
TOMO_INT = f"{DATASET}/TS_run2/{VS}/Tomograms/101/TS_run2.zarr"
TILT = f"{DATASET}/TS_run1/TiltSeries/100/TS_run1.zarr"
SEG = f"{DATASET}/TS_run1/{VS}/Annotations/100/ribosome-1.0_segmentationmask.zarr"
INST = f"{DATASET}/TS_run1/{VS}/Annotations/101/ribosome-1.0_instancesegmentationmask.zarr"
AXES = [{"name": a, "type": "space", "unit": "angstrom"} for a in "zyx"]


def write_v2_image(root: Root, rel: str, level0: np.ndarray, spacing: float, z_binned: bool = True,
                   metadata: dict | None = None) -> list[np.ndarray]:
    """A Zarr v2 / OME-NGFF 0.4 image as the Portal wrote them: 3 levels, scale-only transforms, '/' chunk keys."""
    group = zarr.open_group(root.store(rel, read_only=False), mode="w", zarr_format=2)
    levels, datasets = [level0], []
    for _ in range(2):
        levels.append(levels[-1][:: 2 if z_binned else 1, ::2, ::2])
    for k, arr in enumerate(levels):
        a = group.create_array(
            str(k), shape=arr.shape, dtype=arr.dtype, chunks=(256, 256, 256), fill_value=0,
            chunk_key_encoding={"name": "v2", "separator": "/"},
        )
        a[...] = arr
        s = spacing * 2**k
        datasets.append({"path": str(k), "coordinateTransformations": [
            {"type": "scale", "scale": [s if z_binned else spacing, s, s]}]})
    multiscale = {"axes": AXES, "datasets": datasets, "name": "/", "version": "0.4"}
    if metadata:
        multiscale["metadata"] = metadata
    group.attrs["multiscales"] = [multiscale]
    return levels


@pytest.fixture
def roots(test_output_bucket: str, endpoint_url: str) -> tuple[RootSpec, RootSpec]:
    src = RootSpec(f"s3://{test_output_bucket}/public", anon=False, endpoint_url=endpoint_url)
    dest = RootSpec(f"s3://{test_output_bucket}/staging", anon=False, endpoint_url=endpoint_url)
    return src, dest


@pytest.fixture
def portal(roots) -> dict:
    src = roots[0].open()
    rng = np.random.default_rng(0)
    data = {
        TOMO_CONT: (rng.normal(size=(20, 30, 40)) * 2e-6 - 8e-8).astype(np.float32),
        TOMO_INT: rng.integers(-100, 100, size=(9, 14, 11)).astype(np.float32) + 500,
        TILT: rng.normal(10.0, 2.0, size=(3, 66, 43)).astype(np.float32),
    }
    write_v2_image(src, TOMO_CONT, data[TOMO_CONT], 10.0)
    write_v2_image(src, TOMO_INT, data[TOMO_INT], 10.0)
    write_v2_image(src, TILT, data[TILT], 1.68, z_binned=False)
    seg = (rng.random(size=(20, 30, 40)) > 0.7).astype(np.int8)
    data[SEG] = write_v2_image(src, SEG, seg, 10.0)
    inst = rng.integers(0, 4, size=(20, 30, 40)).astype(np.uint16)
    data[INST] = write_v2_image(
        src, INST, inst, 10.0,
        metadata={"image-label": {"version": "0.4", "colors": [{"label-value": v} for v in (1, 2, 3)]}},
    )
    # sidecars
    src.write_json(f"{os.path.dirname(TOMO_CONT)}/tomogram_metadata.json",
                   {"omezarr_dir": TOMO_CONT, "scales": [{"z": 20, "y": 30, "x": 40}] * 3, "size": {"z": 20}, "x": 1})
    src.write_json(f"{os.path.dirname(TILT)}/tiltseries_metadata.json",
                   {"omezarr_dir": TILT, "scales": [], "size": {}, "pixel_spacing": 1.68})
    x = data[TOMO_CONT].astype(np.float64)
    layer = generate_image_layer(
        TOMO_CONT, scale=(1e-9,) * 3, size={"x": 40, "y": 30, "z": 20}, url="https://files.example/",
        mean=float(x.mean()), rms=float(x.std()), threedee_contrast_limits=(float(x.min()), float(x.max())),
    )
    src.write_json(neuroglancer_config_rel(TOMO_CONT), combine_json_layers([layer], scale=1e-9))
    return data


def test_migration_end_to_end(roots, portal):
    src_spec, dest_spec = roots
    src, dest = src_spec.open(), dest_spec.open()
    items = discover(src, [DATASET], ["tomogram", "tiltseries", "segmentationmask", "instancesegmentationmask"])
    assert sorted(i.rel for i in items) == sorted([TOMO_CONT, TOMO_INT, TILT, SEG, INST])

    results = {i.rel: migrate_item(i, src_spec, dest_spec) for i in items}
    assert {r: res.status for r, res in results.items()} == {r: "migrated" for r in results}, [
        res.error for res in results.values() if res.error
    ]

    # tomograms: profile volumes within the quantization bound; the integer one is lossless
    cont, integer = results[TOMO_CONT], results[TOMO_INT]
    assert cont.encoding["integer"] is False and cont.max_error <= cont.encoding["scale_factor"] / 2 * (1 + 1e-9)
    assert 0.9 < cont.rms_ratio < 1.1
    assert integer.encoding == {"add_offset": 500.0, "scale_factor": 1.0, "integer": True} or integer.encoding[
        "integer"
    ]
    assert integer.max_error == 0.0
    tomo = zarr.open_group(dest.store(TOMO_CONT), mode="r")
    assert tomo["0"].shape == (1, 1, 20, 30, 40) and tomo["0"].dtype == np.int16
    assert tomo.attrs["cryoet_data_portal"]["migration"]["source_fingerprint"] == cont.fingerprint

    # tilt series: level 0 kept exactly, Fourier-cropped levels recorded in the metadata JSON
    ts = zarr.open_group(dest.store(TILT), mode="r")
    np.testing.assert_array_equal(ts["0"][:], portal[TILT])
    ts_meta = dest.read_json(f"{os.path.dirname(TILT)}/tiltseries_metadata.json")
    assert ts_meta["scales"][2] == {"z": 3, "y": cp.fourier_plan(66, 4).m, "x": cp.fourier_plan(43, 4).m}
    assert ts_meta["pixel_spacing"] == 1.68  # other fields kept

    # masks: same levels and dtypes, label values moved to ome["image-label"]
    for rel in (SEG, INST):
        group = zarr.open_group(dest.store(rel), mode="r")
        assert group.metadata.zarr_format == 3
        for k, level in enumerate(portal[rel]):
            np.testing.assert_array_equal(group[str(k)][:], level)
    assert open_omezarr(dest.store(INST)).label_values == [1, 2, 3]

    # tomogram metadata and viewer config
    meta = dest.read_json(f"{os.path.dirname(TOMO_CONT)}/tomogram_metadata.json")
    assert meta["scales"] == [{"z": 20, "y": 30, "x": 40}, {"z": 10, "y": 15, "x": 20}, {"z": 5, "y": 8, "x": 10}]
    old = src.read_json(neuroglancer_config_rel(TOMO_CONT))["layers"][0]
    new = dest.read_json(neuroglancer_config_rel(TOMO_CONT))["layers"][0]
    assert new["source"]["url"] == old["source"]["url"]
    assert new["source"]["transform"]["outputDimensions"]["t'"] == [1, "s"]
    assert new["source"]["transform"]["inputDimensions"]["c'"] == [1, ""]
    sf, ao = cont.encoding["scale_factor"], cont.encoding["add_offset"]
    for name in ("contrast", "contrast_3D"):
        expected = [(v - ao) / sf for v in old["shaderControls"][name]["range"]]
        assert new["shaderControls"][name]["range"] == pytest.approx(expected)
    # the 3D limits were the data range: in codes they span (about) the full int16 range
    assert max(abs(v) for v in new["shaderControls"]["contrast_3D"]["range"]) == pytest.approx(32767, rel=1e-6)

    # repeated runs skip up-to-date images; verify re-checks them
    assert {migrate_item(i, src_spec, dest_spec).status for i in items} == {"skipped-up-to-date"}
    assert {verify_item(i, src_spec, dest_spec).status for i in items} == {"verified"}


def test_existing_destination_policies(roots, portal, test_output_bucket, endpoint_url):
    src_spec = roots[0]
    dest_spec = RootSpec(f"s3://{test_output_bucket}/staging2", anon=False, endpoint_url=endpoint_url)
    dest = dest_spec.open()
    item = Item("segmentationmask", SEG)
    # a stale Zarr v2 copy at the destination (as staging holds today)
    dest.write_text(f"{SEG}/.zgroup", '{"zarr_format": 2}')
    dest.write_text(f"{SEG}/0/0/0/0", "x")
    assert migrate_item(item, src_spec, dest_spec, on_existing="skip").status == "skipped-existing"
    failed = migrate_item(item, src_spec, dest_spec, on_existing="fail")
    assert failed.status == "failed" and "FileExistsError" in failed.error
    assert migrate_item(item, src_spec, dest_spec, on_existing="replace").status == "migrated"
    # no v2 keys remain next to the v3 metadata
    assert not dest.exists(f"{SEG}/.zgroup") and not dest.exists(f"{SEG}/0/0/0/0")
    assert dest.exists(f"{SEG}/zarr.json")


def test_local_destination_and_cli(roots, portal, tmp_path, endpoint_url):
    src_spec = roots[0]
    runner = CliRunner()
    common = ["--src-root", src_spec.url, "--no-src-anon", "--endpoint-url", endpoint_url, "--dataset", DATASET]
    dest_dir = str(tmp_path / "pilot")

    dry = runner.invoke(cli, ["run", *common, "--dest-root", dest_dir, "--dry-run", "--entity", "tomogram"])
    assert dry.exit_code == 0, dry.output
    assert sum(line.startswith("would-migrate ") for line in dry.output.splitlines()) == 2
    assert '{"would-migrate": 2}' in dry.output

    result = runner.invoke(
        cli, ["run", *common, "--dest-root", dest_dir, "--entity", "tomogram", "--manifest", str(tmp_path / "m.jsonl")],
    )
    assert result.exit_code == 0, result.output
    lines = [json.loads(line) for line in (tmp_path / "m.jsonl").read_text().splitlines()]
    assert {line["status"] for line in lines} == {"migrated"} and len(lines) == 2
    assert os.path.exists(os.path.join(dest_dir, TOMO_CONT, "zarr.json"))

    published = runner.invoke(
        cli, ["publish-plan", *common, "--dest-root", dest_dir, "--entity", "tomogram", "--publish-root", "s3://pub"],
    )
    assert published.exit_code == 0, published.output
    assert f"aws s3 sync --delete {dest_dir}/{TOMO_CONT}/ s3://pub/{TOMO_CONT}/" in published.output
    assert "db-import" in published.output
