import json
from datetime import date, datetime
from typing import Any


def json_serial(obj: Any) -> str:
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def tojson(data: Any) -> str:
    return json.dumps(data, indent=4, default=json_serial)


def json_dumps(value: str | dict) -> str:
    """If value is a string, return it as is, otherwise convert to JSON string."""
    return value if isinstance(value, str) else json.dumps(value)
