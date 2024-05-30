import json
import os
import os.path
from collections import defaultdict
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict

import ndjson

from common import colors
from common import point_converter as pc
from common.config import DepositionImportConfig
from common.finders import (
    BaseFinder,
    DepositionObjectImporterFactory,
    SourceGlobFinder,
)
from common.fs import FileSystemApi
from common.image import check_mask_for_label, scale_mrcfile
from common.metadata import AnnotationMetadata
from importers.base_importer import BaseImporter

if TYPE_CHECKING:
    from importers.voxel_spacing import VoxelSpacingImporter
else:
    VoxelSpacingImporter = "VoxelSpacingImporter"


from cryoet_data_portal_neuroglancer.precompute import points


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


# This class is basically a global var that lets us cache metadata and identifiers for annotations,
# so we can generate non-conflicting sequential identifiers for annotations as they're imported.
class AnnotationIdentifierHelper:
    next_identifier: dict[str, int] = defaultdict(partial(int, 100))
    cached_identifiers: dict[str, int] = {}
    loaded_vs_metadatas: dict[str, bool] = {}

    @classmethod
    def load_current_ids(cls, next_id_key: str, config: DepositionImportConfig, vs: VoxelSpacingImporter):
        if next_id_key in cls.loaded_vs_metadatas:
            return
        metadatas = {}
        vs_path = config.resolve_output_path("annotation", vs)
        metadata_glob = f"{vs_path}/*.json"
        for file in config.fs.glob(metadata_glob):
            identifier = int(os.path.basename(file).split("-")[0])
            if identifier >= cls.next_identifier[next_id_key]:
                cls.next_identifier[next_id_key] = identifier + 1
            metadata = json.loads(config.fs.open(file, "r").read())
            metadatas[identifier] = metadata
            current_ids_key = cls.get_ids_key(next_id_key, config, metadata)
            cls.cached_identifiers[current_ids_key] = identifier
        cls.loaded_vs_metadatas[next_id_key] = True

    @classmethod
    def get_ids_key(cls, next_id_key, config, metadata):
        return "-".join(
            [
                next_id_key,
                str(metadata.get("deposition_id", config.deposition_id)),
                metadata["annotation_object"].get("description") or "",
                metadata["annotation_object"]["name"],
                metadata["annotation_method"],
            ],
        )

    @classmethod
    def get_identifier(cls, config: DepositionImportConfig, metadata: dict[str, Any], parents: dict[str, Any]):
        vs = parents["voxel_spacing"]
        next_id_key = vs.get_output_path()

        current_ids_key = cls.get_ids_key(next_id_key, config, metadata)
        cls.load_current_ids(next_id_key, config, vs)

        if cached_id := cls.cached_identifiers.get(current_ids_key):
            return cached_id

        return_value = cls.next_identifier[next_id_key]
        cls.cached_identifiers[current_ids_key] = return_value
        cls.next_identifier[next_id_key] += 1
        return return_value


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
        source_args = {k: v for k, v in self.source.items() if k not in ["shape", "glob_string"]}
        instance_args = {
            "identifier": AnnotationIdentifierHelper.get_identifier(config, metadata, parents),
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


class AnnotationImporter(BaseImporter):
    type_key = "annotation"
    plural_key = "annotations"
    finder_factory = AnnotationImporterFactory
    has_metadata = True
    written_metadata_files = []  # This is a *class* variable that helps us avoid writing metadata files multiple times.

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
            dest_prefix,
        )

    # Functions to support writing annotation metadata
    def get_output_path(self):
        output_dir = super().get_output_path()
        return self.annotation_metadata.get_filename_prefix(output_dir, self.identifier)

    def import_metadata(self):
        dest_prefix = self.get_output_path()
        filename = f"{dest_prefix}.json"
        if filename in self.written_metadata_files:
            return  # We've already written this metadata file

        anno_files = [
            item
            for item in AnnotationImporter.finder(self.config, **self.parents)
            if item.identifier == self.identifier
        ]

        output_dir = self.get_output_path()
        path = os.path.relpath(output_dir, self.config.output_prefix)
        files = []
        for source in anno_files:
            files.extend(source.get_metadata(path))

        self.local_metadata["object_count"] = max([anno.get_object_count(output_dir) for anno in anno_files], default=0)
        self.local_metadata["files"] = files

        self.written_metadata_files.append(filename)
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


class BaseAnnotationSource(AnnotationImporter):
    is_visualization_default: bool
    valid_file_formats: list[str] = []

    shape: str
    file_format: str

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

    def get_object_count(self, output_prefix: str):
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

    def convert(
        self,
        fs: FileSystemApi,
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

    mask_label: int

    def __init__(
        self,
        mask_label: int | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        if not mask_label:
            mask_label = 1
        self.mask_label = mask_label

    def convert(
        self,
        fs: FileSystemApi,
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


class AbstractPointAnnotation(BaseAnnotationSource):
    shape = "Point"
    map_functions = {}
    valid_file_formats = []

    def __init__(
        self,
        binning: int | None = None,
        *args,
        **kwargs,
    ) -> None:
        if not binning:
            binning = 1
        self.binning = binning

        super().__init__(*args, **kwargs)

    def get_converter_args(self):
        return {}

    def load(
        self,
        fs: FileSystemApi,
        filename: str,
    ) -> list[pc.Point | pc.InstancePoint | pc.OrientedPoint]:
        method = self.map_functions[self.file_format]
        local_file = fs.localreadable(filename)

        try:
            points = method(local_file, **self.get_converter_args())
        except ValueError as err:
            print(err)
            return []

        return points

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

    def get_object_count(self, output_prefix: str):
        return len(self.get_output_data(self.config.fs, output_prefix))

    def get_output_data(self, fs, output_prefix):
        with fs.open(self.get_output_filename(output_prefix), "r") as f:
            annotations = ndjson.load(f)
        return annotations

    def convert(
        self,
        fs: FileSystemApi,
        output_prefix: str,
    ):
        filename = self.get_output_filename(output_prefix)
        annotations = self.load(fs, self.path)
        with fs.open(filename, "w") as fh:
            ndjson.dump([a.to_dict() for a in annotations], fh)

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


class PointAnnotation(AbstractPointAnnotation):
    shape = "Point"
    map_functions = {
        "csv": pc.from_csv,
        "csv_with_header": pc.from_csv_with_header,
        "mod": pc.from_mod,
    }
    valid_file_formats = list(map_functions.keys())

    columns: str
    delimiter: str

    def __init__(
        self,
        columns: str | None = None,
        delimiter: str | None = None,
        *args,
        **kwargs,
    ) -> None:
        if not delimiter:
            delimiter = ","
        self.delimiter = delimiter

        if not columns:
            columns = "xyz"
        self.columns = columns

        super().__init__(*args, **kwargs)

    def get_converter_args(self):
        return {
            "binning": self.binning,
            "order": self.columns,
            "delimiter": self.delimiter,
        }


class OrientedPointAnnotation(AbstractPointAnnotation):
    shape = "OrientedPoint"
    map_functions = {
        "relion3_star": pc.from_relion3_star,
        "relion4_star": pc.from_relion4_star,
        "tomoman_relion_star": pc.from_tomoman_relion_star,
        "stopgap_star": pc.from_stopgap_star,
    }
    valid_file_formats = list(map_functions.keys())

    binning: int
    order: str | None
    filter_value: str

    def __init__(
        self,
        filter_value: str | None = None,
        order: str | None = None,
        *args,
        **kwargs,
    ) -> None:
        self.order = order
        super().__init__(*args, **kwargs)
        self.filter_value = None
        if filter_value:
            self.filter_value = filter_value.format(**self.get_glob_vars())

    def get_converter_args(self):
        return {
            "binning": self.binning,
            "order": self.order,
            "filter_value": self.filter_value,
        }

    def neuroglancer_precompute_args(
        self,
        fs: FileSystemApi,
        output_prefix: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        return {"is_oriented": True}


class InstanceSegmentationAnnotation(OrientedPointAnnotation):
    shape = "InstanceSegmentation"
    map_functions = {
        "tardis": pc.from_tardis,
    }
    valid_file_formats = list(map_functions.keys())

    def _get_distinct_ids(self, output_prefix: str) -> set[int]:
        data = self.get_output_data(self.config.fs, output_prefix)
        return {d["instance_id"] for d in data}

    def get_object_count(self, output_prefix):
        # In case of instance segmentation, we need to count the unique IDs (i.e. number of instances)
        return len(self._get_distinct_ids(output_prefix))

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
