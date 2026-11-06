# Migrating published data to Zarr v3

`scripts/migrate_zarr_v3.py` converts the Portal's published Zarr v2 / OME-NGFF 0.4 images to the Zarr v3 /
OME-NGFF 0.5 format that ingestion now writes (see [s3_ingestion.md](s3_ingestion.md#1-standardized-entity)):

| Entity | Conversion |
|---|---|
| Tomograms | cryoET storage profile volume: 5-D `int16` codes with `scale_factor`/`add_offset`, mean-binned levels, statistics |
| Tilt series | cryoET storage profile tilt series: `float32`, Fourier-cropped levels, per-tilt statistics |
| Segmentation masks (semantic, instance) | same levels, dtypes and chunks in Zarr v3; instance label values under `ome["image-label"]` |

Each image is rebuilt from level 0 of the source and verified before it is marked as migrated:
- tomograms decode to within half a quantization step of the source (exactly for integer-valued sources);
- tilt-series level 0 and all mask levels are identical to the source;
- tomograms and tilt series pass `common.cryoet_profile.check_profile`.

The script also rewrites the sidecar files:
- `tomogram_metadata.json` / `tiltseries_metadata.json` (`scales`, `size`; tilt-series levels change size with Fourier cropping);
- the tomogram's `{id}-neuroglancer_config.json`: the transform lists the `t`/`c` axes as local dimensions, and the contrast controls are converted to code units. The `zarr://` source URL is unchanged.

MRC files, Neuroglancer precomputed annotations and meshes, and key images are not touched.

## Usage

```bash
cd ingestion_tools/scripts
# what would be migrated (and what is already done at the destination)
python migrate_zarr_v3.py plan --dataset 10440
# pilot: read the public bucket anonymously, write to a local directory
python migrate_zarr_v3.py run --dataset 10440 --run-name TS_86_3 --dest-root /scratch/zarr3-pilot --workers 4
# convert into the staging bucket (default destination), then re-check
python migrate_zarr_v3.py run --dataset 10440 --workers 4
python migrate_zarr_v3.py verify --dataset 10440
# print the publishing commands (does not run them)
python migrate_zarr_v3.py publish-plan --dataset 10440
```

- **Roots**: `--src-root` defaults to `s3://cryoet-data-portal-public`, read anonymously (`--no-src-anon` uses credentials). `--dest-root` defaults to `s3://cryoet-data-portal-staging`. Both accept local directories. Images keep their relative keys.
- **Selection**: `--dataset` (repeatable) or `--all-datasets`, optionally narrowed with `--entity` and `--run-name` (shell pattern).
- **Repeated runs**: an image whose migration marker (`attributes.cryoet_data_portal.migration`, holding a fingerprint of the source's v2 metadata) matches the source is skipped. The marker is written last, so an interrupted image is redone.
- **Existing destinations**: `--on-existing` controls what happens to a destination image without a matching marker, such as the Zarr v2 copies staging holds today:
  - `skip` (default): leave it;
  - `fail`: report the item as failed;
  - `replace`: delete the destination prefix first, so no v2 keys remain next to the v3 metadata.
- **Manifest**: one JSONL line per image, with status, encoding, level shapes, max error, RMS error relative to `scale_factor/√12`, sidecars and duration. It is written to `--manifest`, or by default under `<dest-root>/_migrations/zarr_v3/`. The exit code is non-zero if any image failed.
- **Memory**: tomograms are converted in memory (float32 level 0, plus one shard of codes and level 1). Plan about 7 bytes per voxel of the largest tomogram, plus about 13 GB for writing a 4 GiB shard.

## At scale

`enqueue_runs.py migrate-zarr-v3` queues one SWIPE job per dataset with `infra/migrate_zarr_v3-v0.0.1.wdl`. The WDL must be uploaded to the swipe-wdl bucket first, like the other workflow files. Jobs default to 64 GB.

```bash
python enqueue_runs.py migrate-zarr-v3 --environment staging --include-dataset 10440 --include-dataset 10441 --workers 2
```

## Publishing (per dataset)

1. Sync each verified image to the public bucket **with `--delete`** (`publish-plan` prints the commands). Neuroglancer refuses a store that holds both Zarr v2 and v3 metadata, and a plain sync would leave the v2 keys in place.
2. Copy the rewritten metadata JSON and viewer configs.
3. Invalidate the CDN for the published prefixes.
4. Re-import the dataset's database records (`enqueue_runs.py db-import --include-dataset <id>`). The database holds the viewer config, file sizes and level dimensions.

Publish only after readers can handle the new format. Clients need a Zarr v3 reader with sharding, must drop the singleton `t`/`c` axes of tomograms, and must apply `scale_factor`/`add_offset` (copick, the Portal Python client and user scripts).
