# Schema of the CryoET data portal

## CryoET data portal directory structure

Metadata file and directory layout specs:

<pre>
.
├── [dataset_id]/
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
│   │   │       │   └── [annotation_id]/
│   │   │       │       ├── annotation_files
│   │   │       │       └── <annotation_key>.json (metadata file)
│   │   │       ├── Images/
│   │   │       │   └── [tomogram_id]/
│   │   │       │       ├── key-photo-expanded.png
│   │   │       │       ├── key-photo-original.png
│   │   │       │       ├── key-photo-thumbnail.png
│   │   │       │       └── key-photo-snapshot.png
│   │   │       ├── NeuroglancerPrecompute/
│   │   │       │   ├── [annotation_id]-shape_precompute
│   │   │       │   └── [tomogram_id]-neuroglancer-config.json
│   │   │       └── Tomograms/
│   │   │           └── [tomogram_id]/
│   │   │               ├── tomogram-metadata.json
│   │   │               ├── [run_name].zarr/
│   │   │               │   └── subdirectories according to <a href="https://ngff.openmicroscopy.org/latest/">OME-NGFF spec</a> at 100%, 50% and 25% scale
│   │   │               └── [run_name].mrc
│   │   ├── TiltSeries/
│   │   │   └── [tiltseries_id]/
│   │   │       ├── [run_name].mrc
│   │   │       ├── [run_name].zarr/
│   │   │       │   └── subdirectories according to <a href="https://ngff.openmicroscopy.org/latest/">OME-NGFF spec</a> at 100%, 50% and 25% scale
│   │   │       ├── tiltseries_metadata.json
│   │   │       └── [name_in_source].rawtlt
│   │   └── run_metadata.json
│   ├── Images/
│   │   ├── snapshot.png
│   │   └── thumbnail.png
│   └── dataset_metadata.json
└── DepositionMetadata/
    └── [deposition-id]/
        ├── deposition_metadata.json
        └── Images/
            ├── snapshot.png
            └── thumbnail.png
</pre>

## Setting up your schema environment

The dependencies for the schema are managed using [poetry](https://python-poetry.org/). Install poetry if you don't have it already.
Poetry provides an easy way to create a virtual environment with shell and install your dependencies. This ensures that same versions of the dependencies are used across different environments, as all the dependencies are tracked in the poetry.lock file.

```bash
# Make the schema your working directory
cd schema
# Initialize the poetry shell
poetry shell
# Install the dependencies
poetry install
```


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

## Building the ingestion config schema validation
If you have updated any of the core yamls or the ingestion_config yamls, you will need to rebuild the ingestion config validation schema. To do this, run the following command:

```bash
cd schema/
make build-ingestion-config
```
This will clean the existing codegen files for the current version of ingestion config and regenerate the files again.


## Building the api config schema
If you have updated any of the core yamls or the api yamls, you will need to rebuild the api schema. To do this, run the following command:

```bash
cd schema/
make build-api
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
