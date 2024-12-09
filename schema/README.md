# cryoET data portal metadata schema

This directory contains the metadata schema for the cryoET data portal. Browse contained classes [here](metadata_docs/index.md).

Metadata file and directory layout specs:


<pre>
.
├── [dataset_identifier]/
│   ├── [run_name]/
│   │   ├── Alignments/
│   │   │   └── [alignment_id]/
│   │   │       ├── alignment_metadata.json
│   │   │       └── [name_in_source].(aln|xf|tlt|json|xtilt|com)
│   │   ├── Frames/
│   │   │   ├── [name_in_source].(tiff|eer|mrc)
│   │   │   ├── [name_in_source].mdoc
│   │   │   └── frames_metadata.json
│   │   ├── Gains/
│   │   │   └── [name_in_source]_gain.(mrc|gain|dm4)
│   │   ├── Reconstructions/
│   │   │   └── VoxelSpacingXX.XXX/
│   │   │       ├── Annotations/
│   │   │       │   └── <anno-id>/
│   │   │       │       ├── annotation_files
│   │   │       │       └── <annotation_key>.json (metadata file)
│   │   │       ├── Images/
│   │   │       │   └── <tomo-id>/
│   │   │       │       ├── key-photo-expanded.png
│   │   │       │       ├── key-photo-original.png
│   │   │       │       ├── key-photo-thumbnail.png
│   │   │       │       └── key-photo-snapshot.png
│   │   │       ├── NeuroglancerPrecompute/
│   │   │       │   ├── <anno-id>-shape_precompute
│   │   │       │   └── <tomo-id>-neuroglancer-config.json
│   │   │       └── Tomograms/
│   │   │           └── <tomo-id>/
│   │   │               ├── tomogram-metadata.json
│   │   │               ├── <run-name>.zarr/
│   │   │               │   └── subdirectories according to <a href="https://ngff.openmicroscopy.org/latest/">OME-NGFF spec</a> at 100%, 50% and 25% scale
│   │   │               └── <run-name>.mrc
│   │   ├── TiltSeries/
│   │   │   └── <ts-id>/
│   │   │       ├── <run-name>.mrc
│   │   │       ├── <run-name>.zarr/
│   │   │       │   └── subdirectories according to <a href="https://ngff.openmicroscopy.org/latest/">OME-NGFF spec</a> at 100%, 50% and 25% scale
│   │   │       ├── tiltseries_metadata.json
│   │   │       └── [name_in_source].rawtlt
│   │   └── run_metadata.json
│   ├── Images/
│   │   ├── snapshot.png
│   │   └── thumbnail.png
│   └── dataset_metadata.json
└── DepositionMetadata/
    └── <deposition-id>/
        ├── deposition_metadata.json
        └── Images/
            ├── snapshot.png
            └── thumbnail.png
</pre>

<pre>
[dataset_identifier]/
|-- <a href="metadata_docs/Dataset.md">dataset_metadata.json</a>
|-- [run_name]/
|   |-- run_metadata.json
|   |-- Frames/
|   |   |-- [tiff|eer|mrc]
|   |   |-- Gain_reference.mrc|dm4
|   |   |-- frame_acquisition_order.json
|   |-- TiltSeries/
|   |   |-- <a href="metadata_docs/TiltSeries.md">tiltseries_metadata.json</a>
|   |   |-- [run_name].mrc
|   |   |-- [run_name].zarr/
|   |   |   |-- [subdirectories according to <a href="https://ngff.openmicroscopy.org/latest/">OME-NGFF spec</a> at 100%, 50% and 25% scale]
|   |   |-- [run_name].mdoc [optional, sometimes]
|   |   |-- [run_name].rawtlt [optional, sometimes]
|   |   |-- [run_name].tlt [optional, sometimes]
|   |-- Tomograms/
|   |   |-- VoxelSpacing[xx.yyy]
|   |   |   |-- CanonicalTomogram
|   |   |   |   |-- <a href="metadata_docs/Tomogram.md">tomogram_metadata.json</a>
|   |   |   |   |-- neuroglancer_config.json
|   |   |   |   |-- [run_name].mrc
|   |   |   |   |-- [run_name].xf [optional, sometimes]
|   |   |   |   |-- [run_name].zarr/
|   |   |   |   |   |-- [subdirectories according to <a href="https://ngff.openmicroscopy.org/latest/">OME-NGFF spec</a> at 100%, 50% and 25% scale]
|   |   |   |-- Annotations/
|   |   |   |   |-- XXX_[object_name]_[version]_point.ndjson
|   |   |   |   |-- <a href="metadata_docs/Annotation.md">XXX_[object_name]_[version].json</a>
|   |   |   |   |-- YYY_[object_name]_[version]_segmentationmask.mrc
|   |   |   |   |-- YYY_[object_name]_[version]_segmentationmask.zarr
|   |   |   |   |   |-- [subdirectories according to <a href="https://ngff.openmicroscopy.org/latest/">OME-NGFF spec</a> at 100%, 50% and 25% scale]
|   |   |   |   |-- <a href="metadata_docs/Annotation.md">YYY_[object_name]_[version].json</a>

</pre>

## Building the schema and docs

To build the schema (core schema, API schema, and ingestion config file schema), run the following command:

```bash
cd schema/
make build
```

To build the docs, run the following command:

```bash
cd schema/
make build-docs
```

## Building the ingestion config validation
If you have updated any of the core yamls or the ingestion config yamls, you will need to rebuild the ingestion config validation schema. To do this, run the following command:

```bash
cd schema/
make build-ingestion-config
```

## Upgrading schema versions (api/, core/, and ingestion_config/)

After creating the new version(s) in their respective directories (with the folder name being the version), edit the corresponding version string(s) in the .version file in the schema/ directory.

Additionally, if you are updating the ingestion_config/ directory, update the "latest/" symbolic link to the new version:

```bash
cd schema/ingestion_config
rm latest
ln -s [new_version] latest
```

Finally, rebuild the schema:

```bash
cd schema/
make build
```
