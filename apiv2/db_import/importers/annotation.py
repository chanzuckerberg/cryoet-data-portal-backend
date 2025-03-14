import os
from typing import Any

from database import models

from db_import.common.finders import JsonDataFinder, MetadataFileFinder
from db_import.importers.base import IntegratedDBImporter, ItemDBImporter


class AnnotationItem(ItemDBImporter):
    id_fields = ["run_id", "deposition_id", "annotation_method", "object_name", "object_description", "object_state"]
    model_class = models.Annotation
    direct_mapped_fields = {
        "deposition_id": ["deposition_id"],
        "deposition_date": ["dates", "deposition_date"],
        "release_date": ["dates", "release_date"],
        "last_modified_date": ["dates", "last_modified_date"],
        "annotation_publication": ["annotation_publications"],
        "annotation_method": ["annotation_method"],
        "ground_truth_status": ["ground_truth_status"],
        "object_name": ["annotation_object", "name"],
        "object_id": ["annotation_object", "id"],
        "object_description": ["annotation_object", "description"],
        "object_state": ["annotation_object", "state"],
        "object_count": ["object_count"],
        "confidence_precision": ["confidence", "precision"],
        "confidence_recall": ["confidence", "recall"],
        "ground_truth_used": ["confidence", "ground_truth_used"],
        "annotation_software": ["annotation_software"],
        "is_curator_recommended": ["is_curator_recommended"],
        "method_type": ["method_type"],
    }

    def normalize_to_unknown_str(self, value: str) -> str:
        return value if value else "Unknown"

    def load_computed_fields(self):
        extra_data = {
            "run_id": self.input_data["run"].id,
            "s3_metadata_path": self.get_s3_url(self.input_data["file"]),
            "https_metadata_path": self.get_https_url(self.input_data["file"]),
        }
        self.model_args.update(extra_data)


class AnnotationShapeItem(ItemDBImporter):
    id_fields = ["annotation_id", "shape_type"]
    model_class = models.AnnotationShape
    direct_mapped_fields = {
        "shape_type": ["shape"],
    }

    def load_computed_fields(self):
        self.model_args["annotation_id"] = self.input_data["annotation"].id


class AnnotationFileItem(ItemDBImporter):
    id_fields = ["format", "tomogram_voxel_spacing_id", "annotation_shape_id"]
    model_class = models.AnnotationFile
    direct_mapped_fields = {
        "format": ["format"],
        "is_visualization_default": ["is_visualization_default"],
    }

    def calculate_source(self) -> str:
        # "dataset_author" or "community" or "portal_standard"
        if self.input_data["annotation"].deposition.id == self.input_data["run"].dataset.deposition_id:
            return "dataset_author"
        else:
            if self.input_data.get("is_portal_standard"):
                return "portal_standard"
            return "community"

    def load_computed_fields(self):
        alignment_path = self.get_s3_url(self.input_data["original_data"]["alignment_metadata_path"])
        self.model_args["annotation_shape_id"] = self.input_data["annotation_shape"].id
        self.model_args["tomogram_voxel_spacing_id"] = self.input_data["tomogram_voxel_spacing"].id
        if alignment_path:
            self.model_args["alignment_id"] = self.config.get_alignment_by_path(
                alignment_path,
                self.input_data["run"].id,
            )
        self.model_args["source"] = self.calculate_source()
        self.model_args["s3_path"] = self.get_s3_url(self.input_data["path"])
        self.model_args["https_path"] = self.get_https_url(self.input_data["path"])
        self.model_args["file_size"] = self.get_file_size(self.input_data["path"])


class AnnotationImporter(IntegratedDBImporter):
    finder = MetadataFileFinder
    row_importer = AnnotationItem
    # TODO This should ideally be True, but we've disabled it for the moment since
    # we are only looking for annotations within a voxel spacing, however those
    # annotations are only associated with runs.
    clean_up_siblings = False

    def __init__(self, config, run: models.Run, tomogram_voxel_spacing: models.TomogramVoxelSpacing, **unused_parents):
        self.run = run
        self.tomogram_voxel_spacing = tomogram_voxel_spacing
        self.config = config
        self.parents = {"run": run, "tomogram_voxel_spacing": tomogram_voxel_spacing}

    def get_filters(self) -> dict[str, Any]:
        raise NotImplementedError("This method should not be called, since annotations don't support sibling cleanup")

    def get_finder_args(self) -> dict[str, Any]:
        return {
            "path": os.path.join(self.tomogram_voxel_spacing.s3_prefix, "Annotations/"),
            "file_glob": "*/*.json",
        }


class AnnotationShapeImporter(IntegratedDBImporter):
    finder = JsonDataFinder
    row_importer = AnnotationShapeItem
    clean_up_siblings = True

    def __init__(
        self,
        config,
        annotation: models.Annotation,
        run: models.Run,
        tomogram_voxel_spacing: models.TomogramVoxelSpacing,
        **unused_parents,
    ):
        self.run = run
        self.tomogram_voxel_spacing = tomogram_voxel_spacing
        self.annotation = annotation
        self.config = config
        self.parents = {"run": run, "tomogram_voxel_spacing": tomogram_voxel_spacing, "annotation": annotation}

    def get_filters(self) -> dict[str, Any]:
        return {"annotation_id": self.annotation.id}

    def get_finder_args(self) -> dict[str, Any]:
        metadata_path = self.annotation.s3_metadata_path
        return {
            "path": self.convert_to_finder_path(metadata_path),
            "list_key": ["files"],
        }


class AnnotationFileImporter(IntegratedDBImporter):
    finder = JsonDataFinder
    row_importer = AnnotationFileItem
    clean_up_siblings = True

    def __init__(
        self,
        config,
        annotation: models.Annotation,
        annotation_shape: models.AnnotationShape,
        run: models.Run,
        tomogram_voxel_spacing: models.TomogramVoxelSpacing,
        **unused_parents,
    ):
        self.run = run
        self.tomogram_voxel_spacing = tomogram_voxel_spacing
        self.annotation = annotation
        self.annotation_shape = annotation_shape
        self.config = config
        self.parents = {
            "run": run,
            "tomogram_voxel_spacing": tomogram_voxel_spacing,
            "annotation_shape": annotation_shape,
            "annotation": annotation,
        }

    def get_filters(self) -> dict[str, Any]:
        return {"annotation_shape_id": self.annotation_shape.id}

    def get_finder_args(self) -> dict[str, Any]:
        metadata_path = self.annotation.s3_metadata_path
        return {
            "path": self.convert_to_finder_path(metadata_path),
            "list_key": ["files"],
            "match_key": "shape",
            "match_value": self.annotation_shape.shape_type,
        }


class AnnotationAuthorItem(ItemDBImporter):
    id_fields = ["annotation_id", "name"]
    model_class = models.AnnotationAuthor
    direct_mapped_fields = {
        "orcid": ["ORCID"],
        "name": ["name"],
        "primary_author_status": ["primary_author_status"],
        "corresponding_author_status": ["corresponding_author_status"],
        "email": ["email"],
        "affiliation_name": ["affiliation_name"],
        "affiliation_address": ["affiliation_address"],
        "affiliation_identifier": ["affiliation_identifier"],
        "author_list_order": ["index"],
        "kaggle_id": ["kaggle_id"],
    }

    def load_computed_fields(self):
        if not self.model_args.get("primary_author_status"):
            self.model_args["primary_author_status"] = False
        if not self.model_args.get("corresponding_author_status"):
            self.model_args["corresponding_author_status"] = False
        self.model_args["annotation_id"] = self.input_data["annotation"].id


class AnnotationAuthorImporter(IntegratedDBImporter):
    finder = JsonDataFinder
    row_importer = AnnotationAuthorItem
    clean_up_siblings = True

    def __init__(self, config, annotation: models.Annotation, **unused_parents):
        self.annotation = annotation
        self.config = config
        self.parents = {"annotation": annotation}

    def get_filters(self) -> dict[str, Any]:
        return {"annotation_id": self.annotation.id}

    def get_finder_args(self) -> dict[str, Any]:
        metadata_path = self.annotation.s3_metadata_path
        return {
            "path": self.convert_to_finder_path(metadata_path),
            "list_key": ["authors"],
        }


class AnnotationMethodLinkItem(ItemDBImporter):
    id_fields = ["annotation_id", "link"]
    model_class = models.AnnotationMethodLink
    direct_mapped_fields = {
        "link_type": ["link_type"],
        "name": ["custom_name"],
        "link": ["link"],
    }

    def load_computed_fields(self):
        self.model_args["annotation_id"] = self.input_data["annotation"].id


class AnnotationMethodLinkImporter(IntegratedDBImporter):
    finder = JsonDataFinder
    row_importer = AnnotationMethodLinkItem
    clean_up_siblings = True

    def __init__(self, config, annotation: models.Annotation, **unused_parents):
        self.annotation = annotation
        self.config = config
        self.parents = {"annotation": annotation}

    def get_filters(self) -> dict[str, Any]:
        return {"annotation_id": self.annotation.id}

    def get_finder_args(self) -> dict[str, Any]:
        metadata_path = self.annotation.s3_metadata_path
        return {
            "path": self.convert_to_finder_path(metadata_path),
            "list_key": ["method_links"],
        }
