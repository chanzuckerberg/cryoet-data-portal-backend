from typing import Tuple

from strawberry.types.nodes import SelectedField

from platformics.graphql_api.core.errors import PlatformicsError


def filter_meta_fields(selections: list[SelectedField]) -> list[SelectedField]:
    return [item for item in selections if not item.name.startswith("__")]


def get_field_by_name(selections: list[SelectedField], item_name: str) -> SelectedField:
    for item in selections:
        if item.name == item_name:
            return item


def exclude_fields_by_name(selections: list[SelectedField], item_name: str) -> list[SelectedField]:
    return [item for item in selections if item.name != item_name]


def get_nested_selected_fields(selected_fields: list[SelectedField]) -> list[SelectedField]:
    selected_fields = selected_fields[0].selections
    selections = []
    for outer_field in filter_meta_fields(selected_fields):
        selections.extend(filter_meta_fields(outer_field.selections))
    return selections


def get_aggregate_selections(selected_fields: list[SelectedField]) -> Tuple[list[SelectedField], list[SelectedField]]:
    schema_fields = get_nested_selected_fields(selected_fields)
    aggregate_selections = exclude_fields_by_name(schema_fields, "groupBy")
    groupby = get_field_by_name(schema_fields, "groupBy")
    groupby_selections = []
    if groupby:
        groupby_selections.extend(filter_meta_fields(groupby.selections))

    if not aggregate_selections:
        raise PlatformicsError("No aggregate functions selected")

    return aggregate_selections, groupby_selections
