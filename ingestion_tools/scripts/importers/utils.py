from importers.alignment import AlignmentImporter
from importers.annotation import AnnotationImporter
from importers.collection_metadata import CollectionMetadataImporter
from importers.dataset import DatasetImporter
from importers.dataset_key_photo import DatasetKeyPhotoImporter
from importers.deposition import DepositionImporter
from importers.deposition_key_photo import DepositionKeyPhotoImporter
from importers.frame import FrameImporter
from importers.gain import GainImporter
from importers.key_image import KeyImageImporter
from importers.rawtilt import RawTiltImporter
from importers.run import RunImporter
from importers.tiltseries import TiltSeriesImporter
from importers.tomogram import TomogramImporter
from importers.visualization_config import VisualizationConfigImporter
from importers.visualization_precompute import AnnotationVisualizationImporter
from importers.voxel_spacing import VoxelSpacingImporter

IMPORTERS = [
    AlignmentImporter,
    AnnotationImporter,
    AnnotationVisualizationImporter,
    CollectionMetadataImporter,
    DatasetKeyPhotoImporter,
    DatasetImporter,
    DepositionImporter,
    DepositionKeyPhotoImporter,
    FrameImporter,
    GainImporter,
    KeyImageImporter,
    RawTiltImporter,
    RunImporter,
    TiltSeriesImporter,
    TomogramImporter,
    VoxelSpacingImporter,
    VisualizationConfigImporter,
]
IMPORTER_DICT = {cls.type_key: cls for cls in IMPORTERS}

# NOTE - ordering of keys is important here, the importer will respect it!
IMPORTER_DEP_TREE = {
    DepositionImporter: {
        DatasetImporter: {
            RunImporter: {
                GainImporter: {},
                CollectionMetadataImporter: {},
                FrameImporter: {},
                TiltSeriesImporter: {
                    RawTiltImporter: {},
                },
                AlignmentImporter: {},
                VoxelSpacingImporter: {
                    AnnotationImporter: {
                        AnnotationVisualizationImporter: {},
                    },
                    TomogramImporter: {
                        VisualizationConfigImporter: {},
                        KeyImageImporter: {},
                    },
                },
            },
            DatasetKeyPhotoImporter: {},
        },
        DepositionKeyPhotoImporter: {},
    },
}


def get_importer_output_path(key: str) -> str | None:
    if key in IMPORTER_DICT:
        return IMPORTER_DICT[key].dir_path
    key_without_metadata = key.removesuffix("_metadata")
    if key_without_metadata in IMPORTER_DICT:
        importer = IMPORTER_DICT.get(key_without_metadata)
        if importer.has_metadata and importer.metadata_path:
            return importer.metadata_path
    return None
