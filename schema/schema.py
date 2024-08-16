import os
from typing import Union

import click
from linkml.utils.helpers import write_to_file
from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.utils.schemaview import SchemaView


def _materialize_classes(schema: SchemaView) -> dict:
    all_classes = schema.all_classes()

    for c_name, c_def in all_classes.items():
        attrs = schema.class_induced_slots(c_name)
        for attr in attrs:
            c_def.attributes[attr.name] = attr


# =============================================================================
# Functions to merge slot fields
# =============================================================================


def _merge_field(slot: dict, slot_to_merge: dict, field: str) -> None:
    """
    Merge an arbitrary field from slot_to_merge into slot.
    """
    if field not in slot_to_merge or slot_to_merge[field] in [None, []]:
        return
    if slot[field] not in [None, []] and slot[field] != slot_to_merge[field]:
        print(
            f"{field} already set for slot {slot['name']} ({slot[field]}). NOT overwriting with {slot_to_merge[field]}",
        )
    else:
        slot[field] = slot_to_merge[field]


def _add_to_slot_minimum_value(slot: dict, minimum_value: Union[int, float, None]) -> Union[int, float, None]:
    """
    Add the minimum_value from the common schema to the slot minimum_value.
    """
    if minimum_value is None:
        return slot["minimum_value"]

    if "minimum_value" in slot and slot["minimum_value"] is not None and slot["minimum_value"] != minimum_value:
        print(
            f"[WARNING]: Minimum value already set for slot {slot['name']} ({slot['minimum_value']}). NOT overwriting with {minimum_value}",
        )
        return slot["minimum_value"]

    return minimum_value


def _add_to_slot_maximum_value(slot: dict, maximum_value: Union[int, float, None]) -> Union[int, float, None]:
    """
    Add the maximum_value from the common schema to the slot maximum_value.
    """
    if maximum_value is None:
        return slot["maximum_value"]

    if "maximum_value" in slot and slot["maximum_value"] is not None and slot["maximum_value"] != maximum_value:
        print(
            f"[WARNING]: Maximum value already set for slot {slot['name']} ({slot['maximum_value']}). NOT overwriting with {maximum_value}",
        )
        return slot["maximum_value"]

    return maximum_value


def _add_to_slot_pattern(slot: dict, pattern: Union[str, None]) -> str:
    """
    Add the pattern from the common schema to the slot pattern.
    """
    if pattern is None:
        return None
    elif "pattern" not in slot or slot["pattern"] is None:
        return pattern
    else:
        # For when the pattern is already in the pattern, no need to add it again
        if f"({pattern})" in slot["pattern"]:
            return slot["pattern"]

        # For when the pattern is a list of patterns already, no need to add the parenthesis again
        if slot["pattern"][0] == "(" and slot["pattern"][-1] == ")":
            return f"{slot['pattern']}|({pattern})"
        else:
            return f"({slot['pattern']})|({pattern})"


# =============================================================================
# Functions to merge slots
# =============================================================================


def _merge_common_into_slot(slot: dict, common_slot: dict) -> None:
    """
    Function that merges common slot fields into the slot.
    We keep these merges separate from regular merging because we want to overwrite the slot's range or any_of field.
    """
    if common_slot["range"] in ["Any", None]:
        pass
    elif slot["range"] not in ["Any", None] and slot["range"] != common_slot["range"]:
        print(
            f"[WARNING]: Range already set for slot {slot['name']} ({slot['range']}). NOT overwriting with {common_slot['range']}",
        )
    else:
        slot["range"] = common_slot["range"]
    _merge_field(slot, common_slot, "any_of")


def _merge_into_slot(slot: dict, slot_to_merge: dict) -> None:
    """
    Merging function that merges slot_to_merge fields into slot. For both common and any_of merging.
    Doesn't merge the range or any_of fields, or it would prevent further any_of merging.
    """
    _merge_field(slot, slot_to_merge, "description")
    _merge_field(slot, slot_to_merge, "multivalued")
    _merge_field(slot, slot_to_merge, "unit")
    _merge_field(slot, slot_to_merge, "recommended")
    _merge_field(slot, slot_to_merge, "required")
    _merge_field(slot, slot_to_merge, "ifabsent")

    slot["minimum_value"] = _add_to_slot_minimum_value(slot, slot_to_merge["minimum_value"])
    slot["maximum_value"] = _add_to_slot_maximum_value(slot, slot_to_merge["maximum_value"])
    slot["pattern"] = _add_to_slot_pattern(slot, slot_to_merge["pattern"])


# =============================================================================
# Function to copy over common schema slots
# =============================================================================


def _import_common_mapping(slot_expression: dict, common_slots: dict) -> None:
    """
    Merge common schema fields into the slot expression.
    """
    original_mappings = slot_expression["exact_mappings"]
    if not original_mappings:
        return

    if len(original_mappings) > 1:
        raise ValueError(f"Slot {slot_expression['name']} has multiple mappings to common schema: {original_mappings}.")

    if len(original_mappings) == 0:
        raise ValueError(f"Slot {slot_expression['name']} has no mappings to common schema.")

    common_slot = common_slots.get(original_mappings[0].replace("cdp-common:", ""))

    if not common_slot:
        raise ValueError(
            f"Slot {original_mappings[0]} does not exist in common schema. Check the exact_mappings for {slot_expression['name']}.",
        )

    _merge_common_into_slot(slot_expression, common_slot)
    _merge_into_slot(slot_expression, common_slot)


# =============================================================================
# Function to add custom fields to slots
# =============================================================================


def _add_custom_fields(slot_expression: dict, schema: SchemaView) -> None:
    schema_types = schema.all_types()
    schema_enums = schema.all_enums()

    # if the slot's multivalued and required, add a minimum_cardinality of 1
    if slot_expression["multivalued"] and slot_expression["required"]:
        slot_expression["minimum_cardinality"] = 1

    if slot_expression["range"] is None:
        return

    slot_expression["range"] = slot_expression["range"].replace("cdp-common:", "")
    # if the slot's range is a type, add the pattern from the type
    if slot_expression["range"] in schema_types:
        slot_expression["pattern"] = _add_to_slot_pattern(
            slot_expression,
            schema.get_type(slot_expression["range"]).pattern,
        )
    # if the slot's range is an enum, add the pattern from the enum
    if slot_expression["range"] in schema_enums:
        for e in schema.get_enum(slot_expression["range"]).permissible_values:
            slot_expression["pattern"] = _add_to_slot_pattern(slot_expression, f"^{e}$")


# =============================================================================
# Function to handle the slots' any_of attribute
# =============================================================================


def _handle_slot_any_of(slot: dict, common_slots: dict, schema: SchemaView) -> None:
    # if the slot has an any_of attribute (with possibly multiple ranges and each of those ranges
    # possibly being a enum / type, add all those patterns
    # also add any corresponding minimum_value and maximum_value attributes
    if "any_of" not in slot:
        return

    for any_of_slot in slot["any_of"]:
        _import_common_mapping(any_of_slot, common_slots)
        _add_custom_fields(any_of_slot, schema)
        _merge_into_slot(slot, any_of_slot)
        # to make sure equality checks work when merging fields
        any_of_slot["pattern"] = None


def _materialize_schema(schema: SchemaView, common_schema: SchemaView) -> SchemaView:
    """
    Copy range, descriptions and patterns from exact_mappings to common_schema.
    """
    # Copy descriptions and ranges from common_schema
    common_slots = common_schema.all_slots()

    # Make all slots attributes of their classes
    _materialize_classes(schema)

    # Loop through all classes and their attributes, adding relevant attributes from common schema
    for c in schema.all_classes():
        clz = schema.get_class(c)
        for s in clz.attributes:
            slot = clz.attributes[s]
            _import_common_mapping(slot, common_slots)
            _add_custom_fields(slot, schema)
            _handle_slot_any_of(slot, common_slots, schema)

    # Make sure the descriptions from mixin classes are carried over
    for c in schema.all_classes():
        clz = schema.get_class(c)
        for m in clz.mixins:
            mixin = schema.get_class(m)
            for name, attr in mixin.attributes.items():
                if attr.description is None:
                    continue
                clz.attributes[name].description = attr.description

    # Make sure the attributes that have classes as range have their descriptions set
    for c in schema.all_classes():
        clz = schema.get_class(c)
        for _, attr in clz.attributes.items():
            if attr.range in schema.all_classes():
                if schema.get_class(attr.range).description is None:
                    continue
                attr.description = schema.get_class(attr.range).description

    return schema


def correct_relative_import_paths(imports: list, schema_file: str, output_path: str) -> list:
    """
    Correct the relative import paths in the schema file to be relative to the output path.
    """
    corrected_imports = []
    for original_imp in imports:
        # Add a LinkML-inferred yaml extension if it doesn't exist
        imp = f"{original_imp}.yaml" if not original_imp.endswith(".yaml") else original_imp

        # Get absolute path of the import file
        absolute_imp_path = os.path.abspath(os.path.join(os.path.dirname(schema_file), imp))

        # if the path doesn't exist to the import, just add the original import string
        if not os.path.exists(absolute_imp_path):
            corrected_imports.append(original_imp)
            continue

        # Now remove the .yaml extension (last 5 chars) before creating the new relative path
        absolute_imp_path = absolute_imp_path[:-5]

        # Now get the relative path from the output path to the import file
        relative_imp_path = os.path.relpath(absolute_imp_path, os.path.dirname(output_path))
        corrected_imports.append(relative_imp_path)
    return corrected_imports


@click.group()
@click.pass_context
def cli(ctx):
    pass


@cli.command()
@click.argument("schema_file", required=True, type=str)
@click.argument("common_schema_file", required=True, type=str)
@click.argument("output_path", required=True, type=str)
@click.pass_context
def materialize(ctx, schema_file: str, common_schema_file: str, output_path: str):
    # Load
    schema = SchemaView(schema_file)
    common_schema = SchemaView(common_schema_file)

    # Copy common elements from common definitions to schema
    for t in common_schema.all_types():
        schema.add_type(common_schema.get_type(t))

    _materialize_classes(common_schema)
    for c in common_schema.all_classes():
        schema.add_class(common_schema.get_class(c))

    for e in common_schema.all_enums():
        schema.add_enum(common_schema.get_enum(e))

    # Materialize output schema from common schema
    schema.materialize_derived_schema()
    output_schema = _materialize_schema(schema, common_schema)

    # Correct the relative import paths in the schema file to be relative to the output path
    output_schema.schema.imports = correct_relative_import_paths(schema.schema.imports, schema_file, output_path)

    output = yaml_dumper.dumps(output_schema.schema)
    write_to_file(output_path, output)


if __name__ == "__main__":
    cli()
