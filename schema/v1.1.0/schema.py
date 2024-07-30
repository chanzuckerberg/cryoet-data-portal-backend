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


def _add_to_slot_minimum_value(slot: dict, minimum_value: Union[int, float]) -> Union[int, float]:
    """
    Add the minimum_value from the common schema to the slot minimum_value.
    """
    if "minimum_value" in slot and slot["minimum_value"] is not None and slot["minimum_value"] != minimum_value:
        print(
            f"[WARNING]: Minimum value already set for slot {slot['name']} ({slot['minimum_value']}). NOT overwriting with {minimum_value}",
        )
        return slot["minimum_value"]
    else:
        return minimum_value


def _add_to_slot_maximum_value(slot: dict, maximum_value: Union[int, float]) -> Union[int, float]:
    """
    Add the maximum_value from the common schema to the slot maximum_value.
    """
    if "maximum_value" in slot and slot["maximum_value"] is not None and slot["maximum_value"] != maximum_value:
        print(
            f"[WARNING]: Maximum value already set for slot {slot['name']} ({slot['maximum_value']}). NOT overwriting with {maximum_value}",
        )
        return slot["maximum_value"]
    else:
        return maximum_value


def _materialize_schema(schema: SchemaView, common_schema: SchemaView) -> SchemaView:
    """
    Copy range, descriptions and patterns from exact_mappings to common_schema.
    """
    # Make all slots attributes of their classes
    _materialize_classes(schema)

    # Copy descriptions and ranges from common_schema
    common_slots = common_schema.all_slots()

    # Ensure types are properly implemented in the generated Pydantic
    schema_types = schema.all_types()

    # Ensure enums are properly implemented in the generated Pydantic
    schema_enums = schema.all_enums()

    # Loop through all classes and their attributes, adding relevant attributes from common schema
    for c in schema.all_classes():
        clz = schema.get_class(c)
        for s in clz.attributes:
            slot = clz.attributes[s]
            original_mappings = slot["exact_mappings"]
            if original_mappings:
                mappings = [m.replace("cdp-common:", "") for m in original_mappings if "cdp-common:" in m]

                if len(mappings) > 1:
                    raise ValueError(
                        f"Slot {slot['name']} with mappings {original_mappings} has multiple mappings to common schema",
                    )

                if len(mappings) == 0:
                    raise ValueError(
                        f"Slot {slot['name']} with mappings {original_mappings} does not have a mapping to common schema",
                    )

                common_slot = common_slots.get(mappings[0])

                if not common_slot:
                    raise ValueError(
                        f"Slot {mappings[0]} does not exist in common schema. Check the exact_mappings for {slot['name']}.",
                    )

                slot["range"] = common_slot["range"]
                slot["any_of"] = common_slot["any_of"]
                slot["description"] = common_slot["description"]
                slot["multivalued"] = common_slot["multivalued"]
                slot["unit"] = common_slot["unit"]
                slot["minimum_value"] = common_slot["minimum_value"]
                slot["maximum_value"] = common_slot["maximum_value"]
                slot["required"] = common_slot["required"]
                slot["recommended"] = common_slot["recommended"]
                slot["pattern"] = _add_to_slot_pattern(slot, common_slot["pattern"])
                slot["ifabsent"] = common_slot["ifabsent"]
            # if the slot's multivalued and required, add a minimum_cardinality of 1
            if slot["multivalued"] and slot["required"]:
                slot["minimum_cardinality"] = 1
            # if the slot's range is a type, add the pattern from the type
            if slot["range"] in schema_types:
                slot["pattern"] = _add_to_slot_pattern(slot, schema.get_type(slot["range"]).pattern)
            # if the slot's range is an enum, add the pattern from the enum
            if slot["range"] in schema_enums:
                for _, e in enumerate(schema.get_enum(slot["range"]).permissible_values):
                    slot["pattern"] = _add_to_slot_pattern(slot, f"^{e}$")
            # if the slot has an any_of attribute (with possibly multiple ranges and each of those ranges
            # possibly being a enum / type, add all those patterns
            # also add any corresponding minimum_value and maximum_value attributes
            if "any_of" in slot:
                for _, a in enumerate(slot["any_of"]):
                    range_type = None
                    if "range" in a:
                        range_type = a["range"].replace("cdp-common:", "")
                        if range_type in schema_types and "pattern" in schema.get_type(range_type):
                            a["range"] = range_type
                            slot["pattern"] = _add_to_slot_pattern(slot, schema.get_type(range_type).pattern)
                        if common_slot := common_slots.get(range_type):
                            slot["description"] = common_slot["description"]
                            slot["unit"] = common_slot["unit"]
                            a["range"] = common_slot["range"]
                            # Switch range_type to the field's type so that we can check it for ENUM-ness below.
                            range_type = a["range"]
                            a["minimum_value"] = common_slot["minimum_value"]
                            a["maximum_value"] = common_slot["maximum_value"]
                        if range_type in schema_enums:
                            for _, e in enumerate(schema.get_enum(range_type).permissible_values):
                                slot["pattern"] = _add_to_slot_pattern(slot, f"^{e}$")
                    if "minimum_value" in a and a["minimum_value"] is not None:
                        slot["minimum_value"] = _add_to_slot_minimum_value(slot, a["minimum_value"])
                    if "maximum_value" in a and a["maximum_value"] is not None:
                        slot["maximum_value"] = _add_to_slot_maximum_value(slot, a["maximum_value"])

    # Make sure the descriptions from mixin classes are carried over
    for c in schema.all_classes():
        clz = schema.get_class(c)
        for m in clz.mixins:
            mixin = schema.get_class(m)
            for name, attr in mixin.attributes.items():
                clz.attributes[name].description = attr.description

    # Make sure the attributes that have classes as range have their descriptions set
    for c in schema.all_classes():
        clz = schema.get_class(c)
        for _, attr in clz.attributes.items():
            if attr.range in schema.all_classes():
                attr.description = schema.get_class(attr.range).description

    return schema


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

    output = yaml_dumper.dumps(output_schema.schema)
    write_to_file(output_path, output)


if __name__ == "__main__":
    cli()
