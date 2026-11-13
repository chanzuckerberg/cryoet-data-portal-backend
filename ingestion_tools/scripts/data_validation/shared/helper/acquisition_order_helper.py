"""Helpers to detect tilt-series metadata whose order doesn't match the stack or the acquisition.

These back warnings rather than failures: an acquisition-ordered stack, or a non-SerialEM DateTime format, is
legitimate, so the checks flag data for a curator to look at.
"""

from datetime import datetime

import pandas as pd

# SerialEM writes e.g. "06-Jun-22  16:54:02" or, in newer versions, "15-Oct-2024  20:39:16". Runs of whitespace are
# collapsed before parsing.
SERIALEM_DATETIME_FORMATS = ("%d-%b-%y %H:%M:%S", "%d-%b-%Y %H:%M:%S")
ANGLE_DECIMAL_PLACES = 2


def _rank(values: list) -> list[int]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0] * len(values)
    for position, index in enumerate(order):
        ranks[index] = position
    return ranks


def mdoc_datetime_order_differs_from_zvalue(mdoc_data: pd.DataFrame) -> bool | None:
    """
    Whether the mdoc sections' DateTime order differs from their ZValue order, as when a tool (e.g. PACEtomo) has
    re-sorted the mdoc by tilt angle and renumbered ZValue. None if it can't be told: a DateTime is missing, doesn't
    parse with a SerialEM format, or repeats.
    """
    if "DateTime" not in mdoc_data or "ZValue" not in mdoc_data:
        return None
    values = list(mdoc_data["DateTime"])
    if not all(isinstance(value, str) for value in values):
        return None
    for datetime_format in SERIALEM_DATETIME_FORMATS:
        try:
            datetimes = [datetime.strptime(" ".join(value.split()), datetime_format) for value in values]
        except ValueError:
            continue
        if len(set(datetimes)) != len(datetimes):
            return None
        return _rank(datetimes) != _rank(list(mdoc_data["ZValue"]))
    return None


def rawtlt_in_mdoc_zvalue_order_not_sorted(raw_angles: list[float], mdoc_data: pd.DataFrame) -> bool:
    """
    Whether the rawtlt angles are not monotonic but follow the mdoc's ZValue (usually acquisition) order. Tilt-series
    stacks are usually sorted by angle; if this one is, rawtlt line i is paired with the wrong section.
    """
    raw = [round(angle, ANGLE_DECIMAL_PLACES) for angle in raw_angles]
    if len(raw) < 3 or raw == sorted(raw) or raw == sorted(raw, reverse=True):
        return False
    present = set(raw)
    in_zvalue_order = [
        angle
        for angle in (round(a, ANGLE_DECIMAL_PLACES) for a in mdoc_data.sort_values("ZValue")["TiltAngle"])
        if angle in present
    ]
    return in_zvalue_order == raw
