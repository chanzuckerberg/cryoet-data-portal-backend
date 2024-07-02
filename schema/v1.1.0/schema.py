import click
from linkml.utils.helpers import write_to_file
from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.utils.schemaview import SchemaView


def _materialize_classes(schema: SchemaView) -> None:
    all_classes = schema.all_classes()

    for c_name, c_def in all_classes.items():
        attrs = schema.class_induced_slots(c_name)
        for attr in attrs:
            c_def.attributes[attr.name] = attr


def _materialize_schema(schema: SchemaView, common_schema: SchemaView) -> SchemaView:
    """
    Copy range, descriptions and patterns from exact_mappings to common_schema.
    """
    # Make all slots attributes of their classes
    _materialize_classes(schema)

    # Copy descriptions and ranges from common_schema
    input_slots = schema.all_slots()
    common_slots = common_schema.all_slots()

    for s in input_slots:
        slot = input_slots.get(s)
        mappings = slot["exact_mappings"]
        if mappings:
            mappings = [m.replace("cdp-common:", "") for m in mappings if "cdp-common:" in m]

            if len(mappings) > 1:
                raise ValueError(
                    f"Slot {slot['name']} has multiple mappings to common schema",
                )

            common_slot = common_slots.get(mappings[0])

            if not common_slot:
                raise ValueError(
                    f"Slot {mappings[0]} does not exist in common schema. Check the exact_mappings for {slot['name']}.",
                )

            slot["range"] = common_slot["range"]
            slot["description"] = common_slot["description"]
            slot["pattern"] = common_slot["pattern"]

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
