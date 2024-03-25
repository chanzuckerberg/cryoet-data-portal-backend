import os

from importers.alignment import AlignmentImporter
from importers.annotation import AnnotationImporter
from importers.base import BaseImporter
from importers.dataset import DatasetImporter
from importers.run import RunImporter
from importers.tomogram import TomogramImporter
from importers.voxel_spacing import VoxelSpacingImporter

from common.formats import tojson
from common.fs import FileSystemApi


class BaseOutputFinder:
    def __init__(self, base_path, args):
        self.base_path = base_path
        self.args = args

    def write_index_file(self, fs: FileSystemApi, found_items: list[BaseImporter]):
        fname = os.path.join(self.base_path, "index.json")
        index_data = [{item.get_output_path()} for item in found_items]
        with fs.open(fname, "w") as fh:
            fh.write(tojson(index_data))

    def find(self, config, parent, find_config, context):
        path = self.find_stuff()
        return self.instantiate(path, config, parent)


class DatasetOutputFinder(BaseOutputFinder):
    def instantiate(self, path, config, parent):
        return DatasetImporter(config, None)


class RunOutputFinder(BaseOutputFinder):
    def instantiate(self, path, config, parent):
        return RunImporter(path=path, config=config, parent=parent)


class VoxelSpacingOutputFinder(BaseOutputFinder):
    def instantiate(self, path, config, parent):
        return VoxelSpacingImporter(path=path, config=config, parent=parent)


class AlignmentOutputFinder(BaseOutputFinder):
    def instantiate(self, path, config, parent):
        return AlignmentImporter()


class TomogramOutputFinder(BaseOutputFinder):
    def instantiate(self, path, config, parent):
        return TomogramImporter()


# We need this to be able to generate index files.
class AnnotationOutputFinder(BaseOutputFinder):
    def instantiate(self, path, config, parent):
        return AnnotationImporter(path=path, config=config, parent=parent)


# I don't think we need this right now.
# class TiltSeriesOutputFinder(BaseOutputFinder):
#    def instantiate(self, path, config, parent):
#        return TiltSeriesImporter()
