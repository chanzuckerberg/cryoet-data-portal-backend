import datetime
import enum
import uuid
from typing import Generic, Optional, TypeVar

import strawberry
from sqlalchemy import func
from typing_extensions import TypedDict

T = TypeVar("T")


operator_map = {
    "_eq": "__eq__",
    "_neq": "__ne__",
    "_in": "in_",
    "_nin": "not_in",
    "_is_null": "IS_NULL",
    "_gt": "__gt__",
    "_gte": "__ge__",
    "_lt": "__lt__",
    "_lte": "__le__",
    "_like": "like",
    "_nlike": "notlike",
    "_ilike": "ilike",
    "_nilike": "notilike",
    "_regex": "regexp_match",
    "_nregex": {"comparator": "regexp_match", "should_negate": True, "flag": None},
    "_iregex": {"comparator": "regexp_match", "should_negate": False, "flag": "i"},
    "_niregex": {"comparator": "regexp_match", "should_negate": True, "flag": "i"},
}

aggregator_map = {
    "count": func.count,
    "avg": func.avg,
    "sum": func.sum,
    "min": func.min,
    "max": func.max,
    "stddev": func.stddev,
    "variance": func.variance,
}


@strawberry.enum
class orderBy(enum.Enum):  # noqa
    # defaults to nulls last
    asc = "asc"
    asc_nulls_first = "asc_nulls_first"
    asc_nulls_last = "asc_nulls_last"
    # defaults to nulls first
    desc = "desc"
    desc_nulls_first = "desc_nulls_first"
    desc_nulls_last = "desc_nulls_last"


@strawberry.input()
class EnumComparators(TypedDict, Generic[T]):
    _eq: Optional[T]
    _neq: Optional[T]
    _in: Optional[list[T]]
    _nin: Optional[list[T]]
    _gt: Optional[T]
    _gte: Optional[T]
    _lt: Optional[T]
    _lte: Optional[T]
    _is_null: Optional[bool]


@strawberry.input
class BoolComparators(TypedDict):
    _eq: Optional[int]
    _neq: Optional[int]
    _in: Optional[list[int]]
    _nin: Optional[list[int]]
    _gt: Optional[int]
    _gte: Optional[int]
    _lt: Optional[int]
    _lte: Optional[int]
    _is_null: Optional[bool]


@strawberry.input
class DatetimeComparators(TypedDict):
    _eq: Optional[datetime.datetime]
    _neq: Optional[datetime.datetime]
    _in: Optional[list[datetime.datetime]]
    _nin: Optional[list[datetime.datetime]]
    _gt: Optional[datetime.datetime]
    _gte: Optional[datetime.datetime]
    _lt: Optional[datetime.datetime]
    _lte: Optional[datetime.datetime]
    _is_null: Optional[bool]


@strawberry.input
class IntComparators(TypedDict):
    _eq: Optional[int]
    _neq: Optional[int]
    _in: Optional[list[int]]
    _nin: Optional[list[int]]
    _gt: Optional[int]
    _gte: Optional[int]
    _lt: Optional[int]
    _lte: Optional[int]
    _is_null: Optional[bool]


@strawberry.input
class FloatComparators(TypedDict):
    _eq: Optional[float]
    _neq: Optional[float]
    _in: Optional[list[float]]
    _nin: Optional[list[float]]
    _gt: Optional[float]
    _gte: Optional[float]
    _lt: Optional[float]
    _lte: Optional[float]
    _is_null: Optional[bool]


@strawberry.input
class UUIDComparators(TypedDict):
    _eq: Optional[uuid.UUID]
    _neq: Optional[uuid.UUID]
    _in: Optional[list[uuid.UUID]]
    _nin: Optional[list[uuid.UUID]]
    _gt: Optional[uuid.UUID]
    _gte: Optional[uuid.UUID]
    _lt: Optional[uuid.UUID]
    _lte: Optional[uuid.UUID]
    _is_null: Optional[bool]


@strawberry.input
class StrComparators(TypedDict):
    _eq: Optional[str]
    _neq: Optional[str]
    _in: Optional[list[str]]
    _nin: Optional[list[str]]
    _is_null: Optional[bool]
    _gt: Optional[str]
    _gte: Optional[str]
    _lt: Optional[str]
    _lte: Optional[str]
    _like: Optional[str]
    _nlike: Optional[str]
    _ilike: Optional[str]
    _nilike: Optional[str]
    _regex: Optional[str]
    _nregex: Optional[str]
    _iregex: Optional[str]
    _niregex: Optional[str]
