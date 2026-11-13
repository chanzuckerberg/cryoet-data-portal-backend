import os
from datetime import datetime

from mdocfile.data_models import Mdoc, MdocSectionData

from common.config import DepositionImportConfig
from common.finders import DefaultImporterFactory
from importers.base_importer import BaseFileImporter

# SerialEM writes e.g. "06-Jun-22  16:54:02" or, in newer versions, "15-Oct-2024  20:39:16". Runs of whitespace are
# collapsed before parsing.
SERIALEM_DATETIME_FORMATS = ("%d-%b-%y %H:%M:%S", "%d-%b-%Y %H:%M:%S")


def _parse_datetime(value: str | None, datetime_format: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(" ".join(value.split()), datetime_format)
    except ValueError:
        return None


def parse_mdoc_datetimes(sections: list[MdocSectionData], datetime_formats: tuple[str, ...]) -> list[datetime | None]:
    """
    Parse each section's DateTime with the first of the strptime formats that fits every section; None where a value
    is missing or doesn't parse (with the format that fits the most sections).
    """
    best = None
    for datetime_format in datetime_formats:
        parsed = [_parse_datetime(section.DateTime, datetime_format) for section in sections]
        if None not in parsed:
            return parsed
        if best is None or parsed.count(None) < best.count(None):
            best = parsed
    return best or []


def rank(values: list) -> list[int]:
    """The 0-based rank of each value (values must be unique and sortable)."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0] * len(values)
    for position, index in enumerate(order):
        ranks[index] = position
    return ranks


class CollectionMetadataImporter(BaseFileImporter):
    type_key = plural_key = "collection_metadata"
    finder_factory = DefaultImporterFactory
    has_metadata = False
    dir_path = "{dataset_name}/{run_name}/Frames"

    def get_destination_path(self) -> str:
        filename = f"{self.parents['run'].name}.mdoc"
        return os.path.join(self.get_output_path(), filename)

    def get_output_data(self) -> Mdoc:
        path = self.get_destination_path()
        local_path = self.config.fs.localreadable(path)
        return Mdoc.from_file(local_path)

    @property
    def acquisition_order_from_datetime(self) -> bool:
        return bool((self.get_base_metadata() or {}).get("acquisition_order_from_datetime"))

    def get_acquisition_orders(self, sections: list[MdocSectionData]) -> list[int]:
        """
        The acquisition order of each mdoc section, aligned with `sections` (the mdoc's section_data).

        By default this is the section's ZValue. With the collection_metadata option
        `acquisition_order_from_datetime`, it is the 0-based rank of the section's DateTime instead: some tools
        (e.g. PACEtomo) re-sort the mdoc by tilt angle and renumber ZValue, so ZValue then gives the angle rank, not
        the time rank.
        """
        options = self.get_base_metadata() or {}
        datetime_formats = (options["datetime_format"],) if options.get("datetime_format") else SERIALEM_DATETIME_FORMATS
        datetimes = parse_mdoc_datetimes(sections, datetime_formats)
        zvalue_orders = [section.ZValue for section in sections]
        run_name = self.parents["run"].name

        if not self.acquisition_order_from_datetime:
            comparable = None not in datetimes and None not in zvalue_orders and len(set(datetimes)) == len(datetimes)
            if comparable and rank(datetimes) != rank(zvalue_orders):
                print(
                    f"WARNING: the mdoc sections for run {run_name} are not in DateTime order (the mdoc may have been "
                    "sorted by tilt angle). Acquisition order and accumulated dose follow ZValue; set the "
                    "collection_metadata option acquisition_order_from_datetime if DateTime is the true order.",
                )
            return zvalue_orders

        unparsed = [section.ZValue for section, value in zip(sections, datetimes) if value is None]
        if unparsed:
            raise ValueError(
                f"acquisition_order_from_datetime is set, but the mdoc for run {run_name} has sections whose DateTime "
                f"is missing or doesn't match the format {' or '.join(map(repr, datetime_formats))} "
                f"(ZValue {unparsed}).",
            )
        repeated = sorted({value for value in datetimes if datetimes.count(value) > 1})
        if repeated:
            raise ValueError(
                f"acquisition_order_from_datetime is set, but the mdoc for run {run_name} has sections that share a "
                f"DateTime ({', '.join(str(value) for value in repeated)}), so their acquisition order is ambiguous.",
            )
        return rank(datetimes)

    @classmethod
    def get_importer(cls, config: DepositionImportConfig, **parents) -> "CollectionMetadataImporter":
        importers = list(cls.finder(config, **parents))
        if importers:
            return importers[-1]
        raise FileNotFoundError(f"No mdoc found for run: {parents['run'].name}")
