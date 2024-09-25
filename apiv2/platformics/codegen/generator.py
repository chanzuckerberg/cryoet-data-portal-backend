"""
Code generation script to generate SQLAlchemy models, GraphQL types,
Cerbos policies, and Factoryboy factories from a LinkML schema.
"""

import logging
import os
import re

import jinja2.ext
from jinja2 import Environment, FileSystemLoader
from linkml_runtime.utils.schemaview import SchemaView

from platformics.codegen.lib.linkml_wrappers import ViewWrapper

DIR_CODEGEN = [
    "support",
    "graphql_api/types",
    "graphql_api/helpers",
    "database/models",
    "database/migrations",
    "database/migrations/versions",
    "cerbos/policies",
    "cerbos/policies/_schemas",
    "test_infra/factories",
    "validators",
]


def generate_enums(output_prefix: str, environment: Environment, view: ViewWrapper) -> None:
    """
    Code generation for GraphQL enums
    """
    filename = "support/enums.py"
    template = environment.get_template(f"{filename}.j2")
    logging.debug("generating enums")

    content = template.render(
        enums=view.enums,
    )
    with open(os.path.join(output_prefix, filename), mode="w", encoding="utf-8") as message:
        message.write(content)
        print(f"... wrote {filename}")


def generate_limit_offset_type(output_prefix: str, environment: Environment) -> None:
    """
    Code generation for GraphQL limit offset type
    """
    filename = "support/limit_offset.py"
    template = environment.get_template(f"{filename}.j2")
    logging.debug("generating limit offset type")

    content = template.render()
    with open(os.path.join(output_prefix, filename), mode="w", encoding="utf-8") as message:
        message.write(content)
        print(f"... wrote {filename}")


def generate_entity_subclass_files(
    output_prefix: str,
    template_filename: str,
    environment: Environment,
    view: ViewWrapper,
    render_files: bool,
) -> None:
    """
    Code generation for SQLAlchemy models, GraphQL types, Cerbos policies, and Factoryboy factories
    """
    template = environment.get_template(f"{template_filename}.j2")

    for entity in view.entities:
        print(f"Generating {entity.name}")
        dest_filename = str(template_filename).replace("class_name", entity.snake_name)

        if f"{dest_filename}.j2" in environment.list_templates():
            override_template = environment.get_template(f"{dest_filename}.j2")
            content = override_template.render(
                cls=entity,
                render_files=render_files,
                view=view,
            )
        else:
            content = template.render(
                cls=entity,
                render_files=render_files,
                view=view,
            )
        with open(os.path.join(output_prefix, dest_filename), mode="w", encoding="utf-8") as outfile:
            outfile.write(content)
            print(f"... wrote {dest_filename}")


def generate_entity_import_files(
    output_prefix: str,
    environment: Environment,
    view: ViewWrapper,
    render_files: bool,
) -> None:
    """
    Code generation for database model imports, and GraphQL queries/mutations
    """
    import_templates = [
        "cerbos/config.yaml",
        "cerbos/policies/file.yaml",
        "cerbos/policies/derived_roles_common.yaml",
        "cerbos/policies/_schemas/principal.json",
        "database/models/__init__.py",
        "database/migrations/env.py",
        "database/migrations/script.py.mako",
        "graphql_api/queries.py",
        "graphql_api/mutations.py",
    ]
    classes = view.entities
    for filename in import_templates:
        import_template = environment.get_template(f"{filename}.j2")
        content = import_template.render(
            classes=classes,
            render_files=render_files,
            view=view,
        )
        with open(os.path.join(output_prefix, filename), mode="w", encoding="utf-8") as outfile:
            outfile.write(content)
            print(f"... wrote {filename}")


def regex_replace(txt, rgx, val, ignorecase=False, multiline=False):
    flag = 0
    if ignorecase:
        flag |= re.I
    if multiline:
        flag |= re.M
    compiled_rgx = re.compile(rgx, flag)
    return compiled_rgx.sub(val, txt)


def generate(schemafile: str, output_prefix: str, render_files: bool, template_override_paths: tuple[str]) -> None:
    """
    Launch code generation
    """
    template_paths = list(template_override_paths)
    template_paths.append(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), "templates/"),
    )  # default template path
    environment = Environment(loader=FileSystemLoader(template_paths), extensions=[jinja2.ext.loopcontrols])
    environment.filters["regex_replace"] = regex_replace
    view = SchemaView(schemafile)
    view.imports_closure()
    wrapped_view = ViewWrapper(view)

    logging.debug("Generating code")

    # Create needed folders if they don't exist already
    for dir in DIR_CODEGEN:
        os.makedirs(f"{output_prefix}/{dir}", exist_ok=True)

    # Generate enums and import files
    generate_enums(output_prefix, environment, wrapped_view)
    generate_limit_offset_type(output_prefix, environment)
    generate_entity_import_files(output_prefix, environment, wrapped_view, render_files=render_files)

    # Generate database models, GraphQL types, Cerbos policies, and Factoryboy factories
    generate_entity_subclass_files(
        output_prefix,
        "database/models/class_name.py",
        environment,
        wrapped_view,
        render_files=render_files,
    )
    generate_entity_subclass_files(
        output_prefix,
        "graphql_api/types/class_name.py",
        environment,
        wrapped_view,
        render_files=render_files,
    )
    generate_entity_subclass_files(
        output_prefix,
        "validators/class_name.py",
        environment,
        wrapped_view,
        render_files=render_files,
    )
    generate_entity_subclass_files(
        output_prefix,
        "cerbos/policies/class_name.yaml",
        environment,
        wrapped_view,
        render_files=render_files,
    )
    generate_entity_subclass_files(
        output_prefix,
        "test_infra/factories/class_name.py",
        environment,
        wrapped_view,
        render_files=render_files,
    )
    generate_entity_subclass_files(
        output_prefix,
        "graphql_api/helpers/class_name.py",
        environment,
        wrapped_view,
        render_files=render_files,
    )
