"""
Basic tests to check that we can hash where-clause dicts reliably
"""

import datetime
import enum

import strawberry

from platformics.graphql_api.core.gql_loaders import get_input_hash


@strawberry.enum
class MyTestEnum(enum.Enum):
    option_1 = "value1"
    option_2 = "value2"


def test_hash_consistency() -> None:
    where_1 = {
        "description": {"key1": "kaboom", "_ilike": {"not": {"nested": "%b%"}}},
        "list_thing": ["10", "11", "12"],
    }
    where_2 = {
        "description": {"_ilike": {"not": {"nested": "%b%"}}, "key1": "kaboom"},
        "list_thing": ["10", "11", "12"],
    }
    assert get_input_hash(where_1) == get_input_hash(where_2)


def test_hash_inconsistency() -> None:
    where_1 = {
        "description": {"key1": "kaboom", "_ilike": {"not": {"nested": "%c%"}}},
        "list_thing": ["10", "11", "12"],
    }
    where_2 = {
        "description": {"_ilike": {"not": {"nested": "%b%"}}, "key1": "kaboom"},
        "list_thing": ["10", "11", "12"],
    }
    assert get_input_hash(where_1) != get_input_hash(where_2)
    where_2 = {
        "description": {"key1": "kaboom", "_ilike": {"not": {"nested": "%c%"}}},
        "list_thing": ["10", "11", "12"],
        "extra_item": "foo",
    }
    assert get_input_hash(where_1) != get_input_hash(where_2)


def test_list_comparisons() -> None:
    # equality
    where_1 = {
        "description": {"key1": "kaboom", "_ilike": {"not": {"nested": "%b%"}}},
        "nested": {"list_thing": ["10", "11", "12"]},
    }
    where_2 = {
        "description": {"_ilike": {"not": {"nested": "%b%"}}, "key1": "kaboom"},
        "nested": {"list_thing": ["10", "11", "12"]},
    }
    assert get_input_hash(where_1) == get_input_hash(where_2)

    # inequality in nested lists
    where_2 = {
        "description": {"_ilike": {"not": {"nested": "%b%"}}, "key1": "kaboom"},
        "nested": {"list_thing": ["10", "11", "12", "13"]},
    }
    assert get_input_hash(where_1) != get_input_hash(where_2)
    # inequality in nested keys
    where_1 = {
        "description": {"key2": "kaboom", "_ilike": {"not": {"nested": "%b%"}}},
        "nested": {"list_thing": ["10", "11", "12"]},
    }
    assert get_input_hash(where_1) != get_input_hash(where_2)


def test_hash_compairsons_with_weird_types() -> None:
    # Enum equality
    where_1 = {
        "description": {"key1": "kaboom", "_ilike": {"not": {"nested": MyTestEnum.option_2}}},
        "list_thing": ["10", "11", "12"],
    }
    where_2 = {
        "description": {"_ilike": {"not": {"nested": MyTestEnum.option_2}}, "key1": "kaboom"},
        "list_thing": ["10", "11", "12"],
    }
    assert get_input_hash(where_1) == get_input_hash(where_2)
    # Enum inequality
    where_2 = {
        "description": {"_ilike": {"not": {"nested": MyTestEnum.option_1}}, "key1": "kaboom"},
        "list_thing": ["10", "11", "12"],
    }
    assert get_input_hash(where_1) != get_input_hash(where_2)

    # Date equality
    where_1 = {
        "description": {"key1": "kaboom", "_ilike": {"not": {"nested": datetime.datetime(2022, 1, 1, 10, 20)}}},
        "list_thing": ["10", "11", "12"],
    }
    where_2 = {
        "description": {"_ilike": {"not": {"nested": datetime.datetime(2022, 1, 1, 10, 20)}}, "key1": "kaboom"},
        "list_thing": ["10", "11", "12"],
    }
    assert get_input_hash(where_1) == get_input_hash(where_2)

    # Date inequality
    where_2 = {
        "description": {"_ilike": {"not": {"nested": datetime.datetime(2023, 1, 1, 10, 20)}}, "key1": "kaboom"},
        "list_thing": ["10", "11", "12"],
    }
    assert get_input_hash(where_1) != get_input_hash(where_2)
