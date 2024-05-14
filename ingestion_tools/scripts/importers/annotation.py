import csv
import json
import re
import os
import os.path
from typing import TYPE_CHECKING, Any, TypedDict

import ndjson
import numpy as np
import contextlib

from common import instance_point_converter as ipc
from common import oriented_point_converter as opc
from common.finders import DefaultImporterFactory
from common.fs import FileSystemApi
from common.image import check_mask_for_label, scale_mrcfile
from common.metadata import AnnotationMetadata
from importers.base_importer import BaseImporter
from common.config import DepositionImportConfig
from common.finders import (
    BaseFinder,
    BaseLiteralValueFinder,
    DepositionObjectImporterFactory,
    DestinationGlobFinder,
    SourceGlobFinder,
)

if TYPE_CHECKING:
    pass

class AnnotationObject(TypedDict):
    name: str
    id: str
    description: str
    state: str


class AnnotationSource(TypedDict):
    columns: str
    shape: str
    file_format: str
    delimiter: str | None
    binning: int | None
    order: str | None
    filter_value: str | None
    is_visualization_default: bool | None
    mask_label: str | None


class AnnotationMap(TypedDict):
    metadata: dict[str, Any]
    sources: list[AnnotationSource]

class AnnotationImporterFactory(DepositionObjectImporterFactory):
    def load(
        self,
        config: DepositionImportConfig,
        **parent_objects: dict[str, Any] | None,
    ) -> BaseFinder:
        source = self.source
        return SourceGlobFinder(source["glob_string"])

    def _instantiate(
        self,
        cls,
        config: DepositionImportConfig,
        metadata: dict[str, Any],
        name: str,
        path: str,
        parents: dict[str, Any] | None,
    ):
        source_args = dict(self.source)
        del source_args["shape"]
        del source_args["glob_string"]
        instance_args = {
            "identifier": 100,
            "config": config,
            "metadata": metadata,
            "name": name,
            "path": path,
            "parents": parents,
            **source_args,
        }
        shape = self.source["shape"]
        if shape == "SegmentationMask":
            anno = SegmentationMaskAnnotation(**instance_args)
        if shape == "SemanticSegmentationMask":
            anno = SemanticSegmentationMaskAnnotation(**instance_args)
        if shape == "OrientedPoint":
            anno = OrientedPointAnnotation(**instance_args)
        if shape == "Point":
            anno = PointAnnotation(**instance_args)
        if shape == "InstanceSegmentation":
            anno = InstanceSegmentationAnnotation(**instance_args)
        if not anno:
            raise NotImplementedError(f"Unknown shape {shape}")
        if anno.is_valid(config.fs):
            return anno


    def xxfind(self, config: DepositionImportConfig, glob_vars: dict[str, Any]):
        annotations = []
        # make this a dict so we can pass by reference
        vs = self.parents["voxel_spacing"]
        current_identifier = {"identifier": 100}
        existing_annotations = vs.get_existing_annotation_metadatas(config.fs)
        configs = config._get_object_configs(cls.type_key, **parents)
        for annotation_config in configs:
            metadata = AnnotationMetadata(config.fs, config.deposition_id, annotation_config["metadata"])
            identifier = AnnotationImporter.get_identifier(metadata, existing_annotations, current_identifier)
            annotations.append(
                AnnotationImporter(
                    identifier=identifier,
                    config=config,
                    annotation_metadata=metadata,
                    annotation_config=annotation_config,
                    metadata=annotation_config["metadata"],  # TODO this is redundant and should probably be fixed?
                    parents=parents,
                )
            )
            identifier += 1

        # Annotation has to have at least one valid source to be imported.
        annotations = [a for a in annotations if a.has_valid_source()]

        return annotations

class AnnotationImporter(BaseImporter):
    type_key = "annotation"
    plural_key = "annotations"
    finder_factory = AnnotationImporterFactory
    has_metadata = True
    written_metadata_files = [] # This is a class variable that helps us avoid writing metadata files multiple times.

    def __init__(
        self,
        identifier: int,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.identifier: int = identifier
        self.local_metadata = {"object_count": 0, "files": []}
        self.annotation_metadata = AnnotationMetadata(self.config.fs, self.config.deposition_id, self.metadata)

    # Functions to support writing annotation data
    def import_item(self):
        dest_prefix = self.get_output_path()
        self.convert(
            self.config.fs,
            self.config.input_path,
            dest_prefix,
        )

    # Functions to support writing annotation metadata
    def has_valid_source(self):
        return len(self.sources) > 0

    def get_output_files(self, fs, output_dir):
        path = os.path.relpath(output_dir, self.config.output_prefix)
        files = []
        for source in self.sources:
            files.extend(source.get_metadata(path))
        return files

    def get_object_count(self) -> int:
        object_counts = []
        dest_prefix = self.get_output_path()
        for source in self.sources:
            object_counts.append(source.get_object_count(self.config.fs, dest_prefix))
        return max(object_counts) if object_counts else 0

    def get_output_path(self):
        output_dir = super().get_output_path()
        return self.annotation_metadata.get_filename_prefix(output_dir, self.identifier)

    def import_metadata(self):
        dest_prefix = self.get_output_path()
        filename = f"{dest_prefix}.json"
        if filename in self.written_metadata_files:
            return  # We've already written this metadata file

        run_name = self.get_run().name
        print(f"importing annotations for {run_name}")
        real_sources = 0
        for source in self.sources:
            # Don't panic if we don't have a source file for this annotation source
            try:
                source.path
                real_sources += 1
            except Exception:
                continue
        if not real_sources:
            print(f"Skipping writing metadata for run {run_name} due to missing files")
            return
        self.local_metadata["object_count"] = self.get_object_count()
        self.local_metadata["files"] = self.get_output_files(self.config.fs, dest_prefix)

        print(filename)
        self.annotation_metadata.write_metadata(filename, self.local_metadata)

    @classmethod
    def get_identifier(
        cls,
        metadata_obj: AnnotationMetadata,
        existing_annotations: list[dict[str, Any]],
        current_identifier: dict[str, int],
    ):
        # See if we have an exact match we should use
        for annotation_id, existing_metadata in existing_annotations.items():
            if all(
                [
                    existing_metadata.get("deposition_id") == metadata_obj.deposition_id,
                    existing_metadata["annotation_object"]["description"]
                    == metadata_obj.metadata["annotation_object"]["description"],
                    existing_metadata["annotation_object"]["name"]
                    == metadata_obj.metadata["annotation_object"]["name"],
                    existing_metadata["annotation_method"] == metadata_obj.metadata["annotation_method"],
                ],
            ):
                return annotation_id
        if existing_annotations and current_identifier["identifier"] <= max(existing_annotations.keys()):
            current_identifier["identifier"] = max(existing_annotations.keys()) + 1
        return_value = current_identifier["identifier"]
        current_identifier["identifier"] += 1
        return return_value

class BaseAnnotationSource(AnnotationImporter):
    is_visualization_default: bool
    valid_file_formats: list[str] = []

    shape: str
    file_format: str

    is_visualization_default: bool | None

    def __init__(
        self,
        file_format: str,
        is_visualization_default: bool = False,
        *args,
        **kwargs,
    ) -> None:
        self.file_format = file_format
        self.is_visualization_default = is_visualization_default

        if self.valid_file_formats and self.file_format not in self.valid_file_formats:
            raise Exception("Invalid file format")

        super().__init__(*args, **kwargs)


    def get_object_count(self, fs: FileSystemApi, output_prefix: str):
        # We currently don't count objects in segmentation masks.
        return 0

    def is_valid(self, *args, **kwargs):
        # To be overridden by subclasses to communicate whether this source contains valid information for this run.
        return True

    def convert(
        self,
        fs: FileSystemApi,
        input_prefix: str,
        output_prefix: str,
    ):
        pass


class VolumeAnnotationSource(BaseAnnotationSource):
    valid_file_formats: list[str] = ["mrc"]

    def get_output_filename(self, output_prefix: str, extension: str | None = None):
        filename = f"{output_prefix}_{self.shape.lower()}"
        if extension:
            filename = f"{filename}.{extension}"
        return filename

    def get_metadata(self, output_prefix: str):
        metadata = [
            {
                "format": fmt,
                "path": self.get_output_filename(output_prefix, fmt),
                "shape": self.shape,
                "is_visualization_default": self.is_visualization_default,
            }
            for fmt in ["zarr", "mrc"]
        ]
        return metadata


class SegmentationMaskAnnotation(VolumeAnnotationSource):
    shape = "SegmentationMask"  # Don't expose SemanticSegmentationMask to the public portal.

    mask_label: int

    def __init__(
        self,
        mask_label: int,
        *args,
        **kwargs,
    ) -> None:
        self.mask_label = mask_label
        super().__init__(*args, **kwargs)
        
    def convert(
        self,
        fs: FileSystemApi,
        input_prefix: str,
        output_prefix: str,
    ):
        return scale_mrcfile(
            fs,
            self.get_output_filename(output_prefix),
            self.path,
            write_mrc=self.config.write_mrc,
            write_zarr=self.config.write_zarr,
            voxel_spacing=self.get_voxel_spacing().as_float(),
        )


class SemanticSegmentationMaskAnnotation(VolumeAnnotationSource):
    shape = "SegmentationMask"  # Don't expose SemanticSegmentationMask to the public portal.

    def convert(
        self,
        fs: FileSystemApi,
        input_prefix: str,
        output_prefix: str,
    ):
        return scale_mrcfile(
            fs,
            self.get_output_filename(output_prefix),
            self.path,
            label=self.mask_label,
            write_mrc=self.config.write_mrc,
            write_zarr=self.config.write_zarr,
            voxel_spacing=self.get_voxel_spacing().as_float(),
        )

    def is_valid(self, fs: FileSystemApi) -> bool:
        try:
            input_file = self.path
            return check_mask_for_label(fs, input_file, self.mask_label)
        except Exception:
            return False


class PointAnnotation(BaseAnnotationSource):
    shape = "Point"
    valid_file_formats = ["csv", "csv_with_header"]

    columns: str
    delimiter: str

    def __init__(
        self,
        columns: str,
        delimiter: str | None,
        *args,
        **kwargs,
    ) -> None:
        self.columns = columns
        if not delimiter:
            delimiter = ","
        self.delimiter = delimiter

        super().__init__(*args, **kwargs)

    def point(self, x: int, y: int, z: int):
        annotation = {
            "type": "point",
            "location": {"x": x, "y": y, "z": z},
        }
        return annotation

    def load(
        self,
        fs: FileSystemApi,
        csvfilename: str,
    ):
        skip_header = self.file_format == "csv_with_header"
        # Convert to xyz order
        coord_order = [0, 1, 2]
        if self.columns == "zyx":
            coord_order = [2, 1, 0]
        annotation_set = []
        with fs.open(csvfilename, "r") as data:
            points = csv.reader(data, delimiter=self.delimiter)
            if skip_header:
                next(points)
            for coord in points:
                annotation_set.append(
                    self.point(
                        float(coord[coord_order[0]]),
                        float(coord[coord_order[1]]),
                        float(coord[coord_order[2]]),
                    ),
                )
        return annotation_set

    def get_metadata(self, output_prefix: str):
        metadata = [
            {
                "format": "ndjson",
                "path": self.get_output_filename(output_prefix),
                "shape": self.shape,
                "is_visualization_default": self.is_visualization_default,
            },
        ]
        return metadata

    def get_output_filename(self, output_prefix: str):
        filename = f"{output_prefix}_{self.shape.lower()}.ndjson"
        return filename

    def get_object_count(self, fs, output_prefix):
        return len(self.get_output_data(fs, output_prefix))

    def get_output_data(self, fs, output_prefix):
        with fs.open(self.get_output_filename(output_prefix), "r") as f:
            annotations = ndjson.load(f)
        return annotations

    def convert(
        self,
        fs: FileSystemApi,
        input_prefix: str,
        output_prefix: str,
    ):
        filename = self.get_output_filename(output_prefix)
        annotations = self.load(fs, self.path)
        with fs.open(filename, "w") as fh:
            ndjson.dump(annotations, fh)


class OrientedPointAnnotation(PointAnnotation):
    shape = "OrientedPoint"
    map_functions = {
        "relion3_star": opc.from_relion3_star,
        "relion4_star": opc.from_relion4_star,
        "tomoman_relion_star": opc.from_tomoman_relion_star,
        "stopgap_star": opc.from_stopgap_star,
    }
    valid_file_formats = [k for k in map_functions.keys()]

    binning: int
    order: str | None
    filter_value: str

    def __init__(
        self,
        binning: int,
        filter_value: str,
        order: str | None = None,
        *args,
        **kwargs,
    ) -> None:
        self.binning = binning
        self.order = order
        super().__init__(*args, **kwargs)
        if filter_value:
            self.filter_value = filter_value.format(**self.get_glob_vars())


    def oriented_point(
        self,
        position: np.ndarray,
        rot_matrix: np.ndarray,
    ):
        position = position.tolist()
        rot_matrix = rot_matrix.tolist()
        annotation = {
            "type": "orientedPoint",
            "location": {
                "x": position[2],
                "y": position[1],
                "z": position[0],
            },
            "xyz_rotation_matrix": rot_matrix,
        }
        return annotation

    def load(
        self,
        fs: FileSystemApi,
        starfilename: str,
    ):
        method = self.map_functions[self.file_format]
        local_file = fs.localreadable(starfilename)
        annotation_set = []
        try:
            positions, rotations = method(local_file, self.filter_value, self.binning, self.order)
        except ValueError as err:
            print(err)
            return []
        for rownum in range(len(positions)):
            annotation_set.append(self.oriented_point(positions[rownum], rotations[rownum]))
        return annotation_set


class InstanceSegmentationAnnotation(OrientedPointAnnotation):
    shape = "InstanceSegmentation"
    map_functions = {
        "tardis": ipc.from_tardis,
    }

    def get_object_count(self, fs, output_prefix):
        data = self.get_output_data(fs, output_prefix)

        ids = [d["instance_id"] for d in data]

        # In case of instance segmentation, we need to count the unique IDs (i.e. number of instances)
        return len(set(ids))

    def load(self, fs: FileSystemApi, filename: str):
        method = self.map_functions[self.file_format]
        local_file = fs.localreadable(filename)

        try:
            print(self.binning)
            points = method(local_file, self.filter_value, self.binning, self.order)
        except ValueError as err:
            print(err)
            return []

        return points

    def convert(
        self,
        fs: FileSystemApi,
        input_prefix: str,
        output_prefix: str,
    ):
        filename = self.get_output_filename(output_prefix)
        annotations = self.load(fs, self.path)

        with fs.open(filename, "w") as fh:
            ndjson.dump([a.to_dict() for a in annotations], fh)