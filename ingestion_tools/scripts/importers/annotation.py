import os
import os.path
from abc import abstractmethod
from typing import Any, Callable, Type

import ndjson

from common import mesh_converter as mc
from common import point_converter as pc
from common.config import DepositionImportConfig
from common.finders import BaseFinder, DepositionObjectImporterFactory, SourceGlobFinder, SourceMultiGlobFinder
from common.fs import FileSystemApi
from common.id_helper import IdentifierHelper
from common.image import check_mask_for_label, make_pyramids
from common.metadata import AnnotationMetadata
from importers.alignment import AlignmentImporter
from importers.base_importer import BaseImporter


class AnnotationIdentifierHelper(IdentifierHelper):
    @classmethod
    def _get_container_key(cls, config: DepositionImportConfig, parents: dict[str, Any], *args, **kwargs):
        return "-".join(["annotation", parents["voxel_spacing"].get_output_path()])

    @classmethod
    def _get_metadata_glob(cls, config: DepositionImportConfig, parents: dict[str, Any], *args, **kwargs) -> str:
        vs = parents["voxel_spacing"]
        anno_dir_path = config.resolve_output_path("annotation", vs, {"annotation_id": "*"})
        return os.path.join(anno_dir_path, "*.json")

    @classmethod
    def _generate_hash_key(cls, container_key: str, metadata: dict[str, Any], parents: dict[str, Any], *args, **kwargs):
        return "-".join(
            [
                container_key,
                str(metadata.get("deposition_id", int(parents["deposition"].name))),
                metadata["annotation_object"].get("description") or "",
                metadata["annotation_object"]["name"],
                metadata["annotation_method"],
                metadata["annotation_object"].get("state") or "",
                metadata.get("alignment_metadata_path", kwargs.get("alignment_metadata_path")),
            ],
        )


class AnnotationImporterFactory(DepositionObjectImporterFactory):
    def __init__(self, source: dict[str, Any], importer_cls: Type[BaseImporter]):
        super().__init__(source, importer_cls)
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
        config: DepositionImportConfig,
        metadata: dict[str, Any],
        name: str,
        path: str,
        allow_imports: bool,
        parents: dict[str, Any] | None,
    ):
        source_args = {k: v for k, v in self.source.items() if k not in {"shape", "glob_string", "glob_strings"}}
        alignment_path = config.to_formatted_path(self._get_alignment_metadata_path(config, parents))
        identifier = AnnotationIdentifierHelper.get_identifier(
            config,
            metadata,
            parents,
            alignment_metadata_path=alignment_path,
        )
        instance_args = {
            "identifier": identifier,
            "config": config,
            "metadata": metadata,
            "name": name,
            "path": path,
            "parents": parents,
            "alignment_metadata_path": alignment_path,
            "allow_imports": allow_imports,
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
        if shape == "TriangularMesh":
            anno = TriangularMeshAnnotation(**instance_args)
        if shape == "TriangularMeshGroup":
            anno = TriangularMeshAnnotationGroup(**instance_args)
        if not anno:
            raise NotImplementedError(f"Unknown shape {shape}")
        if anno.is_valid():
            return anno

    @classmethod
    def _get_alignment_metadata_path(cls, config: DepositionImportConfig, parents: dict[str, Any]) -> str:
        for alignment in AlignmentImporter.finder(config, **parents):
            return alignment.get_metadata_path()
        return ""


class AnnotationImporter(BaseImporter):
    type_key = "annotation"
    plural_key = "annotations"
    finder_factory = AnnotationImporterFactory
    has_metadata = True
    dir_path = "{dataset_name}/{run_name}/Reconstructions/VoxelSpacing{voxel_spacing_name}/Annotations/{annotation_id}"
    metadata_path = dir_path
    written_metadata_files = []  # This is a *class* variable that helps us avoid writing metadata files multiple times.

    def __init__(
        self,
        identifier: int,
        alignment_metadata_path: str,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.identifier: int = identifier
        self.local_metadata = {
            "object_count": 0,
            "files": [],
            "alignment_metadata_path": alignment_metadata_path,
        }
        self.annotation_metadata = AnnotationMetadata(self.config.fs, self.get_deposition().name, self.metadata)

    # Functions to support writing annotation data
    def import_item(self):
        if not self.is_import_allowed():
            print(f"Skipping import of {self.name}")
            return
        dest_prefix = self.get_output_path()
        self.convert(dest_prefix)

    # Functions to support writing annotation metadata
    def get_output_path(self):
        output_dir = super().get_output_path().format(annotation_id=self.identifier)
        self.config.fs.makedirs(output_dir)
        return self.annotation_metadata.get_filename_prefix(output_dir)

    def import_metadata(self):
        if not self.is_import_allowed():
            print(f"Skipping import of {self.name} metadata")
            return
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

    def get_output_dim(self) -> tuple[int, int, int]:
        """Returns the dimensions of the output volume at the Annotation's VoxelSpacing."""
        alignment = list(AlignmentImporter.finder(self.config, **self.parents))[0]
        dims = alignment.metadata.get("volume_dimension", None)
        if not dims:
            dims = alignment.get_extra_metadata()["volume_dimension"]
        voxel_spacing = self.parents["voxel_spacing"].as_float()

        dims = (
            int(round(dims["z"] / voxel_spacing)),
            int(round(dims["y"] / voxel_spacing)),
            int(round(dims["x"] / voxel_spacing)),
        )
        return dims

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


# TODO: Refactor to remove duplications in SemanticSegmentationMaskAnnotation and SegmentationMaskAnnotation
class SegmentationMaskAnnotation(VolumeAnnotationSource):
    shape = "SegmentationMask"  # Don't expose SemanticSegmentationMask to the public portal.
    mask_label: int
    rescale: bool = False
    threshold: float | None

    def __init__(
        self,
        mask_label: int | None = None,
        rescale: bool = False,
        threshold: float | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        if not mask_label:
            mask_label = 1
        self.mask_label = mask_label
        self.rescale = rescale
        self.threshold = threshold

        if mask_label != 1 and threshold is not None:
            raise ValueError("Thresholding and selecting by label are mutually exclusive")

    def convert(self, output_prefix: str):
        output_dims = self.get_output_dim() if self.rescale else None
        return make_pyramids(
            self.config.fs,
            self.get_output_filename(output_prefix),
            self.path,
            label=self.mask_label,
            write_mrc=self.config.write_mrc,
            write_zarr=self.config.write_zarr,
            voxel_spacing=self.get_voxel_spacing().as_float(),
            scale_0_dims=output_dims,
            threshold=self.threshold,
        )


class SemanticSegmentationMaskAnnotation(VolumeAnnotationSource):
    shape = "SegmentationMask"  # Don't expose SemanticSegmentationMask to the public portal.
    mask_label: int
    rescale: bool = False
    threshold: float | None

    def __init__(
        self,
        mask_label: int | None = None,
        rescale: bool = False,
        threshold: float | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        if not mask_label:
            mask_label = 1
        self.mask_label = mask_label
        self.rescale = rescale
        self.threshold = threshold

        if mask_label != 1 and threshold is not None:
            raise ValueError("Thresholding and selecting by label are mutually exclusive")

    def convert(self, output_prefix: str):
        output_dims = self.get_output_dim() if self.rescale else None
        return make_pyramids(
            self.config.fs,
            self.get_output_filename(output_prefix),
            self.path,
            label=self.mask_label,
            write_mrc=self.config.write_mrc,
            write_zarr=self.config.write_zarr,
            voxel_spacing=self.get_voxel_spacing().as_float(),
            scale_0_dims=output_dims,
            threshold=self.threshold,
        )

    def is_valid(self) -> bool:
        try:
            input_file = self.path
            return check_mask_for_label(self.config.fs, input_file, self.mask_label, threshold=self.threshold)
        except Exception:
            return False


class AbstractPointAnnotation(BaseAnnotationSource):
    map_functions = {}

    def __init__(
        self,
        binning: float | None = None,
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
        "relion3_star": pc.point_from_relion3_star,
        "relion4_star": pc.point_from_relion4_star,
        "tomoman_relion_star": pc.point_from_tomoman_relion_star,
        "copick": pc.point_from_copick,
    }
    valid_file_formats = list(map_functions.keys())

    columns: str
    delimiter: str
    filter_value: str | None

    def __init__(
        self,
        columns: str | None = None,
        delimiter: str | None = None,
        filter_value: str | None = None,
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

        self.filter_value = None
        if filter_value:
            self.filter_value = filter_value.format(**self.get_glob_vars())

    def get_converter_args(self):
        return {
            "binning": self.binning,
            "order": self.columns,
            "delimiter": self.delimiter,
            "filter_value": self.filter_value,
        }


class OrientedPointAnnotation(AbstractPointAnnotation):
    shape = "OrientedPoint"
    map_functions = {
        "relion3_star": pc.from_relion3_star,
        "relion4_star": pc.from_relion4_star,
        "tomoman_relion_star": pc.from_tomoman_relion_star,
        "stopgap_star": pc.from_stopgap_star,
        "mod": pc.from_oriented_mod,
        "copick": pc.from_copick,
    }
    valid_file_formats = list(map_functions.keys())

    binning: int
    order: str | None
    filter_value: str | None
    mesh_source_path: str | None

    def __init__(
        self,
        filter_value: str | None = None,
        order: str | None = None,
        mesh_source_path: str | None = None,
        *args,
        **kwargs,
    ) -> None:
        self.order = order
        super().__init__(*args, **kwargs)
        self.filter_value = None
        if filter_value:
            self.filter_value = filter_value.format(**self.get_glob_vars())

        self.mesh_source_path = None
        if mesh_source_path:
            self.mesh_source_path = mesh_source_path.format(**self.get_glob_vars())

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
        "copick": pc.instance_from_copick,
    }
    valid_file_formats = list(map_functions.keys())

    def get_distinct_ids(self, output_prefix: str) -> set[int]:
        data = self.get_output_data(output_prefix)
        return {d["instance_id"] for d in data}

    def get_object_count(self, output_prefix) -> int:
        # In case of instance segmentation, we need to count the unique IDs (i.e. number of instances)
        return len(self.get_distinct_ids(output_prefix))


class AbstractTriangularMeshAnnotation(BaseAnnotationSource):
    shape = "TriangularMesh"
    map_functions: dict[str, Callable]
    valid_file_formats: list[str]
    output_format: str = "glb"
    scale_factor: float

    def __init__(
        self,
        scale_factor: float = 1.0,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.scale_factor = scale_factor

    def get_metadata(self, output_prefix: str) -> list[dict[str, Any]]:
        metadata = [
            {
                "format": self.output_format,
                "path": self.get_output_filename(output_prefix, self.output_format),
                "shape": self.shape,
                "is_visualization_default": self.is_visualization_default,
            },
        ]
        return metadata

    def get_object_count(self, output_prefix: str) -> int:
        return 1

    @property
    def mesh_file(self) -> str:
        if not hasattr(self, "_mesh_file"):
            self._mesh_file = self.config.fs.localreadable(self.path)
        return self._mesh_file

    @abstractmethod
    def convert(self, output_prefix: str):
        """convert the mesh and write it to the output directory"""
        pass


class TriangularMeshAnnotation(AbstractTriangularMeshAnnotation):
    """Triangular Meshes are converted to glb format"""

    map_functions = {
        "obj": mc.from_generic,
        "stl": mc.from_generic,
        "vtk": mc.from_vtk,
        "glb": mc.from_generic,
    }
    valid_file_formats = list(map_functions.keys())

    def convert(self, output_prefix: str):
        output_file_name = self.get_output_filename(output_prefix, self.output_format)
        output_file = self.config.fs.localwritable(output_file_name)
        self.map_functions[self.file_format](self.mesh_file, output_file, scale_factor=self.scale_factor)
        self.config.fs.push(output_file)


class TriangularMeshAnnotationGroup(AbstractTriangularMeshAnnotation):
    map_functions = {
        "hff": mc.from_hff,
    }
    valid_file_formats = list(map_functions.keys())
    mesh_name: str

    def __init__(self, mesh_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mesh_name = mesh_name

    def convert(self, output_prefix: str):
        output_file_name = self.get_output_filename(output_prefix, self.output_format)
        output_file = self.config.fs.localwritable(output_file_name)
        self.map_functions[self.file_format](
            self.mesh_file,
            output_file,
            scale_factor=self.scale_factor,
            name=self.mesh_name,
        )
        self.config.fs.push(output_file)

    def is_valid(self) -> bool:
        return bool(mc.check_mesh_name(self.mesh_file, self.mesh_name))
