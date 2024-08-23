import json
import os
import os.path
from abc import abstractmethod
from collections import defaultdict
from functools import partial
from typing import TYPE_CHECKING, Any

import ndjson

from common import point_converter as pc
from common.config import DepositionImportConfig
from common.finders import BaseFinder, DepositionObjectImporterFactory, SourceGlobFinder, SourceMultiGlobFinder
from common.fs import FileSystemApi
from common.image import check_mask_for_label, make_pyramids
from common.metadata import AnnotationMetadata
from importers.base_importer import BaseImporter

if TYPE_CHECKING:
    from importers.voxel_spacing import VoxelSpacingImporter
else:
    VoxelSpacingImporter = "VoxelSpacingImporter"


# This class is basically a global var that lets us cache metadata and identifiers for annotations,
# so we can generate non-conflicting sequential identifiers for annotations as they're imported.
class AnnotationIdentifierHelper:
    next_identifier: dict[str, int] = defaultdict(partial(int, 100))
    cached_identifiers: dict[str, int] = {}
    loaded_vs_metadatas: dict[str, bool] = {}

    @classmethod
    def load_current_ids(
        cls,
        next_id_key: str,
        config: DepositionImportConfig,
        vs: VoxelSpacingImporter,
        deposition_id: int,
    ):
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
            current_ids_key = cls.get_ids_key(next_id_key, metadata, deposition_id)
            cls.cached_identifiers[current_ids_key] = identifier
        cls.loaded_vs_metadatas[next_id_key] = True

    @classmethod
    def get_ids_key(cls, next_id_key, metadata, deposition_id):
        return "-".join(
            [
                next_id_key,
                str(metadata.get("deposition_id", deposition_id)),
                metadata["annotation_object"].get("description") or "",
                metadata["annotation_object"]["name"],
                metadata["annotation_method"],
            ],
        )

    @classmethod
    def get_identifier(cls, config: DepositionImportConfig, metadata: dict[str, Any], parents: dict[str, Any]):
        vs = parents["voxel_spacing"]
        next_id_key = vs.get_output_path()
        deposition_id = int(parents["deposition"].name)

        current_ids_key = cls.get_ids_key(next_id_key, metadata, deposition_id)
        cls.load_current_ids(next_id_key, config, vs, deposition_id)

        if cached_id := cls.cached_identifiers.get(current_ids_key):
            return cached_id

        return_value = cls.next_identifier[next_id_key]
        cls.cached_identifiers[current_ids_key] = return_value
        cls.next_identifier[next_id_key] += 1
        return return_value


class AnnotationImporterFactory(DepositionObjectImporterFactory):
    def __init__(self, source: dict[str, Any]):
        super().__init__(source)
        # flatten self.source additional layer that specifies the type of annotation file it is
        clean_source = {k: v for k, v in self.source.items() if k not in {"parent_filters", "exclude"}}
        if not (len(clean_source.keys()) == 1):
            raise ValueError("Incorrect annotation source format")
        source_file = list(clean_source.values())[0]
        source_file["shape"] = list(clean_source.keys())[0]
        self.source = source_file

    def load(
        self,
        config: DepositionImportConfig,
        **parent_objects: dict[str, Any] | None,
    ) -> BaseFinder:
        if self.source.get("glob_string"):
            return SourceGlobFinder(self.source["glob_string"])
        if self.source.get("glob_strings"):
            return SourceMultiGlobFinder(self.source["glob_strings"])

    def _instantiate(
        self,
        cls,
        config: DepositionImportConfig,
        metadata: dict[str, Any],
        name: str,
        path: str,
        parents: dict[str, Any] | None,
    ):
        source_args = {k: v for k, v in self.source.items() if k not in {"shape", "glob_string", "glob_strings"}}
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
        anno = None
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
        if anno.is_valid():
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
        self.annotation_metadata = AnnotationMetadata(self.config.fs, self.get_deposition().name, self.metadata)

    # Functions to support writing annotation data
    def import_item(self):
        dest_prefix = self.get_output_path()
        self.convert(dest_prefix)

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

        try:
            self.local_metadata["object_count"] = max(
                [anno.get_object_count(output_dir) for anno in anno_files],
                default=0,
            )
            self.local_metadata["files"] = files
        except FileNotFoundError:
            print("Skipping metadata write since not all files have been written yet")
            return

        self.written_metadata_files.append(filename)
        self.annotation_metadata.write_metadata(filename, self.local_metadata)


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

    @abstractmethod
    def convert(self, output_prefix: str):
        # To be overridden by subclasses to handle the import of the annotation.
        pass

    def get_object_count(self, output_prefix: str) -> int:
        # To be overridden by subclasses where necessary to return the number of objects in the annotation.
        return 0

    def is_valid(self, *args, **kwargs) -> bool:
        # To be overridden by subclasses when additional check needed to validate if a source contains valid information
        # for this run.
        return True

    @abstractmethod
    def get_metadata(self, output_prefix: str) -> list[dict[str, Any]]:
        # To be overridden by subclasses to return the metadata for the files property of the metadata.
        pass

    def get_output_filename(self, output_prefix: str, extension: str | None = None) -> str:
        filename = f"{output_prefix}_{self.shape.lower()}"
        if extension:
            filename = f"{filename}.{extension}"
        return filename


class VolumeAnnotationSource(BaseAnnotationSource):
    valid_file_formats: list[str] = ["mrc", "zarr"]

    def get_metadata(self, output_prefix: str) -> list[dict[str, Any]]:
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
        mask_label: int | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        if not mask_label:
            mask_label = 1
        self.mask_label = mask_label

    def convert(self, output_prefix: str):
        return make_pyramids(
            self.config.fs,
            self.get_output_filename(output_prefix),
            self.path,
            label=self.mask_label,
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

    def convert(self, output_prefix: str):
        return make_pyramids(
            self.config.fs,
            self.get_output_filename(output_prefix),
            self.path,
            label=self.mask_label,
            write_mrc=self.config.write_mrc,
            write_zarr=self.config.write_zarr,
            voxel_spacing=self.get_voxel_spacing().as_float(),
        )

    def is_valid(self) -> bool:
        try:
            input_file = self.path
            return check_mask_for_label(self.config.fs, input_file, self.mask_label)
        except Exception:
            return False


class AbstractPointAnnotation(BaseAnnotationSource):
    map_functions = {}

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
        # To be overridden by subclasses to return the arguments to pass to the point converter function.
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

    def get_metadata(self, output_prefix: str) -> list[dict[str, Any]]:
        metadata = [
            {
                "format": "ndjson",
                "path": self.get_output_filename(output_prefix),
                "shape": self.shape,
                "is_visualization_default": self.is_visualization_default,
            },
        ]
        return metadata

    def get_output_filename(self, output_prefix: str, extension: str | None = None) -> str:
        return f"{output_prefix}_{self.shape.lower()}.ndjson"

    def get_object_count(self, output_prefix: str) -> int:
        return len(self.get_output_data(output_prefix))

    def get_output_data(self, output_prefix) -> list[dict[str, Any]]:
        with self.config.fs.open(self.get_output_filename(output_prefix), "r") as f:
            annotations = ndjson.load(f)
        return annotations

    def convert(self, output_prefix: str):
        filename = self.get_output_filename(output_prefix)
        annotations = self.load(self.config.fs, self.path)
        with self.config.fs.open(filename, "w") as fh:
            ndjson.dump([a.to_dict() for a in annotations], fh)


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
        "mod": pc.from_oriented_mod,
    }
    valid_file_formats = list(map_functions.keys())

    binning: int
    order: str | None
    filter_value: str | None

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


class InstanceSegmentationAnnotation(OrientedPointAnnotation):
    shape = "InstanceSegmentation"
    map_functions = {
        "tardis": pc.from_tardis,
    }
    valid_file_formats = list(map_functions.keys())

    def get_distinct_ids(self, output_prefix: str) -> set[int]:
        data = self.get_output_data(output_prefix)
        return {d["instance_id"] for d in data}

    def get_object_count(self, output_prefix) -> int:
        # In case of instance segmentation, we need to count the unique IDs (i.e. number of instances)
        return len(self.get_distinct_ids(output_prefix))
