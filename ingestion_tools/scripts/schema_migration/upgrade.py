import json
import logging
from collections import OrderedDict
from typing import Any

import yaml

from schema_migration import migrate_v1_0_0, migrate_v1_1_0, migrate_v1_2_0, migrate_v1_3_0

logger = logging.getLogger(__name__)


def upgrade_config(data: dict[str, Any]) -> dict[str, Any]:
    version_map = OrderedDict(
        # Version_map must be updated when a new migration is needed.
        # Order matters.
        {
            # current_version: (update_function, next_version)
            "0.0.0": (migrate_v1_0_0.upgrade, "1.0.0"),
            "1.0.0": (migrate_v1_1_0.upgrade, "1.1.0"),
            "1.1.0": (migrate_v1_2_0.upgrade, "1.2.0"),
            "1.2.0": (migrate_v1_3_0.upgrade, "1.3.0"),
        },
    )

    if not data.get("version"):
        logger.warning("No version found in config file. Assuming version 0.0.0.")
        # The default version is 0.0.0
        data["version"] = "0.0.0"
    initial_version = data["version"]

    for current_version, item in version_map.items():
        update_func, result_version = item
        if data["version"] == current_version:
            data = update_func(data)
    logger.info("Updated config from %s to %s", initial_version, result_version)
    return data


def has_changes(file, config):
    with open(file, "r") as file:
        old_config = yaml.safe_load(file)
    return json.dumps(old_config) != json.dumps(config)


def upgrade_file(filename: str) -> None:
    with open(filename, "r") as fh:
        logger.debug("Reading %s", filename)
        data = yaml.safe_load(fh.read())

    upgrade_config(data)

    if not has_changes(filename, data):
        return

    with open(filename, "w") as fh:
        logger.debug("Writing %s", filename)
        fh.write(yaml.dump(data))
