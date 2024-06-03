import colorsys
import hashlib
import json
from typing import Any

import distinctipy

INT_COLOR = tuple[int, int, int]  # Returns RGB colors in the range [0, 255]
FLOAT_COLOR = tuple[float, float, float]  # Returns RGB colors in the range [0, 1]
HEX_COLOR = str
INT_COLOR_PAIR = tuple[list[INT_COLOR], list[FLOAT_COLOR]]
HEX_COLOR_PAIR = tuple[list[HEX_COLOR], list[FLOAT_COLOR]]
_MAX_SEED_VALUE = int(2**32 - 1)
_KEYS_FOR_COLOR_SEED = {"annotation_method", "annotation_object", "deposition_id", "ground_truth_status"}


def _convert_colors_to_int(input_colors: list[FLOAT_COLOR]) -> list[INT_COLOR]:
    return [tuple(round(c * 255) for c in color) for color in input_colors]


def _convert_colors_to_hex(input_colors: list[FLOAT_COLOR]) -> list[HEX_COLOR]:
    return [f"#{''.join(f'{round(c * 255):02x}' for c in color)}" for color in input_colors]


def _is_valid_color(color: FLOAT_COLOR) -> bool:
    # Filter out very light colors and very dark colors
    # as they are hard to see on the neuroglancer UI
    _, s, v = colorsys.rgb_to_hsv(*color)
    return s > 0.15 and v > 0.25


def _get_colors(n_colors: int, exclude: list[FLOAT_COLOR], seed: int = None) -> list[FLOAT_COLOR]:
    colors = distinctipy.get_colors(n_colors, exclude_colors=exclude, rng=seed)
    output_colors = [color for color in colors if _is_valid_color(color)]
    if len(output_colors) < n_colors:
        return output_colors + _get_colors(n_colors - len(output_colors), exclude=exclude + colors)
    return output_colors


def get_int_colors(n_colors: int, exclude: list[FLOAT_COLOR], seed: int = None) -> INT_COLOR_PAIR:
    colors = _get_colors(n_colors, exclude=exclude, seed=seed)
    return _convert_colors_to_int(colors), colors


def get_hex_colors(
    n_colors: int,
    exclude: list[FLOAT_COLOR],
    seed: int = None,
) -> tuple[list[HEX_COLOR], list[FLOAT_COLOR]]:
    colors = _get_colors(n_colors, exclude=exclude, seed=seed)
    return _convert_colors_to_hex(colors), colors


def generate_hash(hash_input: dict[str, Any]) -> int:
    md5_hash = hashlib.md5(json.dumps(hash_input, sort_keys=True).encode("utf-8"))
    return int(md5_hash.hexdigest(), 16) % _MAX_SEED_VALUE


def to_base_hash_input(metadata: dict[str, Any]) -> dict[str, Any]:
    hash_input = {key: metadata.get(key) for key in _KEYS_FOR_COLOR_SEED}
    if anno_obj := hash_input["annotation_object"]:
        hash_input["annotation_object"] = {key: anno_obj.get(key) for key in {"id", "name"}}
    return hash_input
