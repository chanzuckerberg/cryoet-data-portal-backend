# cryoET data portal metadata schema

This directory contains the metadata schema for the cryoET data portal. Browse contained classes [here](metadata-docs/index.md).

Metadata file and directory layout specs:

<pre>
[dataset_identifier]/
|-- <a href="metadata-docs/Dataset.md">dataset_metadata.json</a>
|-- [run_name]/
|   |-- run_metadata.json
|   |-- Frames/
|   |   |-- [tiff|eer|mrc]
|   |   |-- Gain_reference.mrc|dm4
|   |   |-- frame_acquisition_order.json
|   |-- TiltSeries/
|   |   |-- <a href="metadata-docs/TiltSeries.md">tiltseries_metadata.json</a>
|   |   |-- [run_name].mrc
|   |   |-- [run_name].zarr/
|   |   |   |-- [subdirectories according to <a href="https://ngff.openmicroscopy.org/latest/">OME-NGFF spec</a> at 100%, 50% and 25% scale]
|   |   |-- [run_name].mdoc [optional, sometimes]
|   |   |-- [run_name].rawtlt [optional, sometimes]
|   |   |-- [run_name].tlt [optional, sometimes]
|   |-- Tomograms/
|   |   |-- VoxelSpacing[xx.yyy]
|   |   |   |-- CanonicalTomogram
|   |   |   |   |-- <a href="metadata-docs/Tomogram.md">tomogram_metadata.json</a>
|   |   |   |   |-- neuroglancer_config.json
|   |   |   |   |-- [run_name].mrc
|   |   |   |   |-- [run_name].xf [optional, sometimes]
|   |   |   |   |-- [run_name].zarr/
|   |   |   |   |   |-- [subdirectories according to <a href="https://ngff.openmicroscopy.org/latest/">OME-NGFF spec</a> at 100%, 50% and 25% scale]
|   |   |   |-- Annotations/
|   |   |   |   |-- XXX_[object_name]_[version]_point.ndjson
|   |   |   |   |-- <a href="metadata-docs/Annotation.md">XXX_[object_name]_[version].json</a>
|   |   |   |   |-- YYY_[object_name]_[version]_segmentationmask.mrc
|   |   |   |   |-- YYY_[object_name]_[version]_segmentationmask.zarr
|   |   |   |   |   |-- [subdirectories according to <a href="https://ngff.openmicroscopy.org/latest/">OME-NGFF spec</a> at 100%, 50% and 25% scale]
|   |   |   |   |-- <a href="metadata-docs/Annotation.md">YYY_[object_name]_[version].json</a>

</pre>

## Building the schema and docs

To build the schema, markdown docs and pydantic classes:

```bash
cd schema/v2.0.0
make build
```
