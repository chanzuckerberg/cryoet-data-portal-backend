def add_frames_metadata(config: dict):
    standardization_config = config.get("standardization_config")
    frame_dose_rate = standardization_config.get("frame_dose_rate", 0)

    if not frame_dose_rate and "frames" not in config:
        return

    if "frames" not in config:
        config["frames"] = [
            {
                "sources": [
                    {"literal": {"value": ["default"]}},
                ],
            },
        ]

    for entry in config["frames"]:
        entry["metadata"] = {
            "dose_rate": frame_dose_rate,
            "is_gain_corrected": "gain" in config,
        }

def clean_up_standard_config(config: dict):
    standardization_config = config.get("standardization_config")
    standardization_config.pop("frame_dose_rate", None)

def upgrade(config: dict) -> dict:
    add_frames_metadata(config)
    clean_up_standard_config(config)
    return config
