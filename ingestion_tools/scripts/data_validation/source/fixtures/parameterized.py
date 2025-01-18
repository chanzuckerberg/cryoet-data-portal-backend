import re

import pytest
from importers.base_importer import BaseImporter
from importers.dataset import DatasetImporter
from importers.deposition import DepositionImporter
from importers.frame import FrameImporter
from importers.run import RunImporter
from importers.tiltseries import TiltSeriesImporter
from importers.utils import IMPORTERS

from common.config import DepositionImportConfig
from common.fs import FileSystemApi

# ============================================================================
# Pytest parametrized fixtures
# ============================================================================

class CryoetTestEntities:

    def __init__(self, config: pytest.Config, ingestion_config_path: str):
        self._pytest_config = config
        self._fs = FileSystemApi.get_fs_api(mode="s3", force_overwrite=False)
        self._ingestion_config = self._create_ingestion_config(ingestion_config_path)
        self._deposition: DepositionImporter = None
        self._dataset: list[DatasetImporter] = None
        self._runs: list[RunImporter] = None
        self._frames: list[FrameImporter] = None
        self._tiltseries: list[TiltSeriesImporter] = None

    @property
    def deposition(self) -> DepositionImporter:
        if self._deposition is None:
            depositions = list(DepositionImporter.finder(self._ingestion_config))
            self._deposition = depositions[0]
        return self._deposition

    @property
    def dataset(self) -> list[DatasetImporter]:
        if self._dataset is None:
            self._dataset = self._get_entities(DatasetImporter, [self.deposition])
        return self._dataset

    @property
    def runs(self) -> list[RunImporter]:
        if self._runs is None:
            self._runs = self._get_entities(RunImporter, self.dataset)
        return self._runs

    @property
    def tiltseries(self) -> list[TiltSeriesImporter]:
        if self._tiltseries is None:
            self._tiltseries = self._get_entities(TiltSeriesImporter, self.runs)
        return self._tiltseries

    @property
    def frames(self) -> list[FrameImporter]:
        if self._frames is None:
            self._frames = self._get_entities(FrameImporter, self.runs)
        return self._frames

    def _get_entities(self, importer_class: BaseImporter, parents: list[BaseImporter]) -> list[BaseImporter]:
        items = []
        name_filter = self._pytest_config.getoption(f"--filter-{importer_class.type_key}-name")
        name_regex = re.compile(name_filter) if name_filter else None
        for parent in parents:
            new_items = [
                instance
                for instance in importer_class.finder(self._ingestion_config, **self._get_all_ancestors(parent))
                if not name_regex or name_regex.match(instance.name)
            ]
            items.extend(new_items)
        print(f"Found {len(items)} {importer_class.type_key} entities")
        print([item.name for item in items])
        return items

    def _create_ingestion_config(self, ingestion_config_path: str)-> DepositionImportConfig:
        input_bucket = self._pytest_config.getoption("--input-bucket")
        output_bucket = self._pytest_config.getoption("--output-bucket")
        print(f"Using input bucket {input_bucket}")
        return DepositionImportConfig(self._fs, ingestion_config_path, output_bucket, input_bucket, IMPORTERS)

    @classmethod
    def _get_all_ancestors(cls, parent: BaseImporter) -> dict[str, BaseImporter]:
        return {**parent.parents, parent.type_key: parent}
