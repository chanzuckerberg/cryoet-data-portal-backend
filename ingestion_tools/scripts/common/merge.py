from copy import deepcopy
from typing import Any


def deep_merge(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(a)
    for bk, bv in b.items():
        av = result.get(bk)
        if isinstance(av, dict) and isinstance(bv, dict):
            result[bk] = deep_merge(av, bv)
        else:
            result[bk] = deepcopy(bv)
    return result
