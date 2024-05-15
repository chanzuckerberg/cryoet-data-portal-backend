import csv
import json
import os
import os.path
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict

import ndjson
import numpy as np

from common import colors
from common import instance_point_converter as ipc
from common import oriented_point_converter as opc
from common.fs import FileSystemApi
from common.image import check_mask_for_label, scale_mrcfile
from common.metadata import AnnotationMetadata
from importers.base_importer import BaseImporter

if TYPE_CHECKING:
    from importers.tomogram import TomogramImporter


from cryoet_data_portal_neuroglancer.precompute import points


class AnnotationObject(TypedDict):
    name: str
    id: str
    description: str
    state: str


class AnnotationSource(TypedDict):
    columns: str
    shape: str
    glob_string: str
    file_format: str
    binning: int | None
    order: str | None
    filter_value: str | None


class AnnotationMap(TypedDict):
    metadata: dict[str, Any]
    sources: list[AnnotationSource]


class BaseAnnotationSource:
    is_visualization_default: bool

    def get_source_file(self, fs: FileSystemApi, input_prefix: str):
        source_path = os.path.join(input_prefix, self.glob_string)
        for file in fs.glob(source_path):
            return file
        raise Exception(f"No annotation source file found for {source_path}!")

    def get_object_count(self, fs: FileSystemApi, output_prefix: str):
        # We currently don't count objects in segmentation masks.
        return 0

    def is_valid(self, *args, **kwargs):
        # To be overridden by subclasses to communicate whether this source contains valid information for this run.
        return True

    def get_neuroglancer_precompute_path(self, annotation_path: str, output_prefix: str) -> str:
        file_name = os.path.basename(f"{annotation_path}_{self.shape.lower()}")
        return os.path.join(output_prefix, file_name, "")

    def neuroglancer_precompute(
        self,
        fs: FileSystemApi,
        annotation_path: str,
        output_prefix: str,
        voxel_spacing: float,
    ):
        pass

    def convert(
        self,
        fs: FileSystemApi,
        input_prefix: str,
        output_prefix: str,
        voxel_spacing: float,
        write_mrc: bool = True,
        write_zarr: bool = True,
    ):
        pass


class VolumeAnnotationSource(BaseAnnotationSource):
    shape: str

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


class SegmentationMaskFile(VolumeAnnotationSource):
    def __init__(
        self,
        shape: str,
        glob_string: str,
        glob_vars: dict[str, str],
        file_format: str,
        is_visualization_default: bool = False,
    ):
        self.glob_string = glob_string.format(**glob_vars)
        self.file_format = file_format
        self.shape = shape
        self.is_visualization_default = is_visualization_default
        if self.file_format not in ["mrc"]:
            raise NotImplementedError("We only support MRC files for segmentation masks")

    def convert(
        self,
        fs: FileSystemApi,
        input_prefix: str,
        output_prefix: str,
        voxel_spacing: float,
        write_mrc: bool = True,
        write_zarr: bool = True,
    ):
        return scale_mrcfile(
            fs,
            self.get_output_filename(output_prefix),
            self.get_source_file(fs, input_prefix),
            write_mrc=write_mrc,
            write_zarr=write_zarr,
            voxel_spacing=voxel_spacing,
        )


class SemanticSegmentationMaskFile(SegmentationMaskFile):
    def __init__(
        self,
        shape: str,
        glob_string: str,
        glob_vars: dict[str, str],
        file_format: str,
        mask_label: int = 1,  # No explicit label means we are dealing with a binary mask already
        is_visualization_default: bool = False,
    ):
        self.glob_string = glob_string.format(**glob_vars)
        self.file_format = file_format
        self.shape = "SegmentationMask"  # Don't expose SemanticSegmentationMask to the public portal.
        self.label = mask_label
        self.is_visualization_default = is_visualization_default

        if self.file_format not in ["mrc"]:
            raise NotImplementedError("We only support MRC files for segmentation masks")

    def convert(
        self,
        fs: FileSystemApi,
        input_prefix: str,
        output_prefix: str,
        voxel_spacing: float = None,
        write_mrc: bool = True,
        write_zarr: bool = True,
    ):
        return scale_mrcfile(
            fs,
            self.get_output_filename(output_prefix),
            self.get_source_file(fs, input_prefix),
            label=self.label,
            write_mrc=write_mrc,
            write_zarr=write_zarr,
            voxel_spacing=voxel_spacing,
        )

    def is_valid(self, fs: FileSystemApi, input_prefix: str) -> bool:
        try:
            input_file = self.get_source_file(fs, input_prefix)
            return check_mask_for_label(fs, input_file, self.label)
        except Exception:
            return False


class PointFile(BaseAnnotationSource):
    def __init__(
        self,
        shape: str,
        glob_string: str,
        glob_vars: dict[str, str],
        file_format: str,
        columns: str,
        is_visualization_default: bool = False,
        delimiter: str = ",",
    ):
        self.glob_string = glob_string.format(**glob_vars)
        self.file_format = file_format
        self.columns = columns
        self.shape = shape
        self.delimiter = delimiter
        self.is_visualization_default = is_visualization_default
        if self.file_format not in ["csv", "csv_with_header"]:
            raise NotImplementedError("We only support CSV files for Point files")

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
        return f"{output_prefix}_{self.shape.lower()}.ndjson"

    def get_object_count(self, fs: FileSystemApi, output_prefix: str):
        return len(self.get_output_data(fs, output_prefix))

    def get_output_data(self, fs: FileSystemApi, output_prefix: str):
        path = fs.localreadable(self.get_output_filename(output_prefix))
        with open(path, "r") as f:
            annotations = ndjson.load(f)
        return annotations

    def convert(
        self,
        fs: FileSystemApi,
        input_prefix: str,
        output_prefix: str,
        voxel_spacing: float,
        write_mrc: bool = True,
        write_zarr: bool = True,
    ):
        filename = self.get_output_filename(output_prefix)
        annotations = self.load(fs, self.get_source_file(fs, input_prefix))
        with fs.open(filename, "w") as fh:
            ndjson.dump(annotations, fh)

    def neuroglancer_precompute_args(
        self,
        fs: FileSystemApi,
        output_prefix: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        return {}

    def neuroglancer_precompute(
        self,
        fs: FileSystemApi,
        annotation_path: str,
        output_prefix: str,
        voxel_spacing: float,
    ):
        precompute_path = self.get_neuroglancer_precompute_path(annotation_path, output_prefix)
        tmp_path = fs.localwritable(precompute_path)
        annotation_metadata_path = fs.localreadable(f"{annotation_path}.json")
        with open(annotation_metadata_path) as f:
            annotation_metadata = json.load(f)
        points.encode_annotation(
            self.get_output_data(fs, annotation_path),
            annotation_metadata,
            Path(tmp_path),
            voxel_spacing * 1e-10,
            **self.neuroglancer_precompute_args(fs, output_prefix, annotation_metadata),
        )
        fs.push(tmp_path)


class OrientedPointFile(PointFile):
    map_functions = {
        "relion3_star": opc.from_relion3_star,
        "relion4_star": opc.from_relion4_star,
        "tomoman_relion_star": opc.from_tomoman_relion_star,
        "stopgap_star": opc.from_stopgap_star,
    }

    def __init__(
        self,
        shape: str,
        glob_vars: dict[str, str],
        file_format: str,
        binning: int,
        glob_string: str,
        is_visualization_default: bool = False,
        order: str | None = None,
        filter_value: str | None = None,
    ):
        self.shape = shape
        self.file_format = file_format
        self.binning = binning
        self.glob_string = glob_string
        self.glob_vars = glob_vars
        self.glob_string = glob_string.format(**glob_vars)
        self.order = order
        self.filter_value = ""
        self.is_visualization_default = is_visualization_default
        if filter_value:
            self.filter_value = filter_value.format(**glob_vars)
        valid_formats = self.map_functions.keys()
        if self.file_format not in valid_formats:
            raise NotImplementedError(
                f"We only support {', '.join(self.map_functions.keys())} files for oriented points",
            )

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

    def neuroglancer_precompute_args(
        self,
        fs: FileSystemApi,
        output_prefix: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        return {"is_oriented": True}


class InstanceSegmentationFile(OrientedPointFile):
    map_functions = {
        "tardis": ipc.from_tardis,
    }

    def get_object_count(self, fs: FileSystemApi, output_prefix: str):
        # In case of instance segmentation, we need to count the unique IDs (i.e. number of instances)
        return len(self._get_distinct_ids(fs, output_prefix))

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
        voxel_spacing: float,
        write_mrc: bool = True,
        write_zarr: bool = True,
    ):
        filename = self.get_output_filename(output_prefix)
        annotations = self.load(fs, self.get_source_file(fs, input_prefix))

        with fs.open(filename, "w") as fh:
            ndjson.dump([a.to_dict() for a in annotations], fh)

    def neuroglancer_precompute_args(
        self,
        fs: FileSystemApi,
        output_prefix: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        ids = self._get_distinct_ids(fs, output_prefix)
        color_map = dict(zip(ids, colors.get_instance_seg_colors(len(ids))))
        object_name = metadata.get("annotation_object", {}).get("name", "")
        names_by_id = {id: f"{object_name} {id}" for id in ids}
        return {
            "names_by_id": names_by_id,
            "label_key_mapper": lambda x: x["instance_id"],
            "color_mapper": lambda x: color_map.get(x["instance_id"], (255, 255, 255)),
        }

    def _get_distinct_ids(self, fs: FileSystemApi, output_prefix: str) -> set[int]:
        data = self.get_output_data(fs, output_prefix)
        return {d["instance_id"] for d in data}


def annotation_source_factory(source_config, glob_vars):
    if source_config["shape"] == "SegmentationMask":
        return SegmentationMaskFile(**source_config, glob_vars=glob_vars)
    if source_config["shape"] == "SemanticSegmentationMask":
        return SemanticSegmentationMaskFile(**source_config, glob_vars=glob_vars)
    if source_config["shape"] == "OrientedPoint":
        return OrientedPointFile(**source_config, glob_vars=glob_vars)
    if source_config["shape"] == "Point":
        return PointFile(**source_config, glob_vars=glob_vars)
    if source_config["shape"] == "InstanceSegmentation":
        return InstanceSegmentationFile(**source_config, glob_vars=glob_vars)
    raise NotImplementedError(f"Unknown shape {source_config['shape']}")


class AnnotationImporter(BaseImporter):
    type_key = "annotation"

    def __init__(
        self,
        identifier: int,
        annotation_config: AnnotationMap,
        annotation_metadata: AnnotationMetadata,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.identifier: int = identifier
        self.annotation_config = annotation_config
        self.annotation_metadata = annotation_metadata
        self.local_metadata = {"object_count": 0, "files": []}
        self.metadata = annotation_config["metadata"]

        sources = [annotation_source_factory(item, self.get_glob_vars()) for item in annotation_config["sources"]]
        self.sources = [source for source in sources if source.is_valid(self.config.fs, self.config.input_path)]

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

    def import_annotations(self, write_mrc: bool = True, write_zarr: bool = True):
        run_name = self.parent.get_run().run_name
        dest_prefix = self.get_output_path()
        for source in self.sources:
            # Don't panic if we don't have a source file for this annotation source
            try:
                source.get_source_file(self.config.fs, self.config.input_path)
            except Exception:
                print(f"Skipping writing annotations for run {run_name} due to missing files")
                continue
            source.convert(
                self.config.fs,
                self.config.input_path,
                dest_prefix,
                self.parent.get_voxel_spacing(),
                write_mrc,
                write_zarr,
            )

    def import_metadata(self):
        run_name = self.parent.get_run().run_name
        print(f"importing annotations for {run_name}")
        real_sources = 0
        for source in self.sources:
            # Don't panic if we don't have a source file for this annotation source
            try:
                source.get_source_file(self.config.fs, self.config.input_path)
                real_sources += 1
            except Exception:
                continue
        if not real_sources:
            print(f"Skipping writing metadata for run {run_name} due to missing files")
            return
        dest_prefix = self.get_output_path()
        self.local_metadata["object_count"] = self.get_object_count()
        self.local_metadata["files"] = self.get_output_files(self.config.fs, dest_prefix)

        filename = f"{dest_prefix}.json"
        print(filename)
        self.annotation_metadata.write_metadata(filename, self.local_metadata)

    def import_neuroglancer_component(self):
        run_name = self.parent.get_run().run_name
        voxel_size = self.config.get_run_voxelsize(self)
        ng_output_path = self.config.resolve_output_path("neuroglancer_precompute", run_name, voxel_size)
        for source in self.sources:
            try:
                source.get_source_file(self.config.fs, self.config.input_path)
            except Exception:
                print(f"Skipping generating annotations neuroglancer config for run {run_name} due to missing files")
                continue
            source.neuroglancer_precompute(
                self.config.fs,
                self.get_output_path(),
                ng_output_path,
                float(voxel_size),
            )

    @classmethod
    def find_annotations(cls, config, tomo: "TomogramImporter") -> list["AnnotationImporter"]:
        annotations = []
        identifier = 100
        for annotation_config in config.annotation_template:
            metadata = AnnotationMetadata(config.fs, annotation_config["metadata"])
            annotations.append(
                AnnotationImporter(
                    identifier=identifier,
                    config=config,
                    parent=tomo,
                    annotation_metadata=metadata,
                    annotation_config=annotation_config,
                ),
            )
            identifier += 1

        # Annotation has to have at least one valid source to be imported.
        return [a for a in annotations if a.has_valid_source()]
