import os
import os.path
from typing import TYPE_CHECKING, Any, Dict, List, TypedDict

import ndjson

from common import point_converter as pc
from common.fs import FileSystemApi
from common.image import check_mask_for_label, scale_mrcfile
from common.metadata import AnnotationMetadata
from importers.base_importer import BaseImporter

if TYPE_CHECKING:
    from importers.tomogram import TomogramImporter


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


class SemanticSegmentationMaskFile(VolumeAnnotationSource):
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


class AbstractPointFile(BaseAnnotationSource):
    output_type = ""
    map_functions = {}

    def __init__(
        self,
        shape: str,
        glob_string: str,
        glob_vars: dict[str, str],
        file_format: str,
        is_visualization_default: bool = False,
    ):
        # Common metadata
        self.shape = shape
        self.glob_string = glob_string
        self.glob_vars = glob_vars
        self.glob_string = glob_string.format(**glob_vars)
        self.is_visualization_default = is_visualization_default

        # Format
        self._test_valid_format(file_format)
        self.file_format = file_format

        # Converter arguments
        self.converter_args = {}

    def _test_valid_format(self, file_format: str):
        valid_formats = self.map_functions.keys()
        if file_format not in valid_formats:
            raise NotImplementedError(
                f"We only support {', '.join(valid_formats)} files for {self.output_type} annotations.",
            )

    def load(
        self,
        fs: FileSystemApi,
        filename: str,
    ) -> List[pc.Point | pc.InstancePoint | pc.OrientedPoint]:
        method = self.map_functions[self.file_format]
        local_file = fs.localreadable(filename)

        try:
            points = method(local_file, **self.converter_args)
        except ValueError as err:
            print(err)
            return []

        return points

    def get_metadata(self, output_prefix: str) -> List[Dict[str, Any]]:
        metadata = [
            {
                "format": "ndjson",
                "path": self.get_output_filename(output_prefix),
                "shape": self.shape,
                "is_visualization_default": self.is_visualization_default,
            },
        ]
        return metadata

    def get_output_filename(self, output_prefix: str) -> str:
        filename = f"{output_prefix}_{self.shape.lower()}.ndjson"
        return filename

    def get_object_count(self, fs: FileSystemApi, output_prefix: str) -> int:
        return len(self.get_output_data(fs, output_prefix))

    def get_output_data(
        self,
        fs: FileSystemApi,
        output_prefix: str,
    ) -> List[pc.Point | pc.InstancePoint | pc.OrientedPoint]:
        with fs.open(self.get_output_filename(output_prefix), "r") as f:
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
            ndjson.dump([a.to_dict() for a in annotations], fh)


class PointFile(AbstractPointFile):
    output_type = "point"
    map_functions = {
        "csv": pc.from_csv,
        "csv_with_header": pc.from_csv_with_header,
        "mod": pc.from_mod,
    }

    def __init__(
        self,
        shape: str,
        glob_string: str,
        glob_vars: dict[str, str],
        file_format: str,
        is_visualization_default: bool = False,
        binning: int = 1,
        columns: str = "xyz",
        filter_value: str = "",
        delimiter: str = ",",
    ):
        super().__init__(shape, glob_string, glob_vars, file_format, is_visualization_default)

        self.columns = columns
        self.delimiter = delimiter

        self.converter_args = {
            "binning": binning,
            "order": self.columns,
            "filter_value": filter_value,
            "delimiter": self.delimiter,
        }


class OrientedPointFile(AbstractPointFile):
    output_type = "orientedPoint"
    map_functions = {
        "relion3_star": pc.from_relion3_star,
        "relion4_star": pc.from_relion4_star,
        "tomoman_relion_star": pc.from_tomoman_relion_star,
        "stopgap_star": pc.from_stopgap_star,
    }

    def __init__(
        self,
        shape: str,
        glob_string: str,
        glob_vars: dict[str, str],
        file_format: str,
        is_visualization_default: bool = False,
        binning: int = 1,
        order: str | None = None,
        filter_value: str | None = None,
    ):
        super().__init__(shape, glob_string, glob_vars, file_format, is_visualization_default)

        # Converter arguments
        if filter_value:
            self.filter_value = filter_value.format(**glob_vars)
        else:
            self.filter_value = ""

        self.order = order
        self.binning = binning

        self.converter_args = {
            "binning": self.binning,
            "order": self.order,
            "filter_value": self.filter_value,
        }


class InstanceSegmentationFile(AbstractPointFile):
    output_type = "instancePoint"
    map_functions = {
        "tardis": pc.from_tardis,
    }

    def __init__(
        self,
        shape: str,
        glob_string: str,
        glob_vars: dict[str, str],
        file_format: str,
        is_visualization_default: bool = False,
        binning: int = 1,
        order: str | None = None,
        filter_value: str | None = None,
    ):
        super().__init__(shape, glob_string, glob_vars, file_format, is_visualization_default)

        # Converter arguments
        if filter_value:
            self.filter_value = filter_value.format(**glob_vars)
        else:
            self.filter_value = ""

        self.order = order
        self.binning = binning
        self.converter_args = {
            "order": self.order,
            "binning": self.binning,
            "filter_value": self.filter_value,
        }

    def get_object_count(self, fs: FileSystemApi, output_prefix: str) -> int:
        data = self.get_output_data(fs, output_prefix)
        ids = [d["instance_id"] for d in data]

        # In case of instance segmentation, we need to count the unique IDs (i.e. number of instances)
        return len(set(ids))


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

    @classmethod
    def find_annotations(cls, config, tomo: "TomogramImporter"):
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
        annotations = [a for a in annotations if a.has_valid_source()]

        return annotations
