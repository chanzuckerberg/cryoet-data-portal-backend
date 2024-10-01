"""
Helpers for writing Jinja2 templates based on LinkML schema objects.

The wrapper classes in this module are entirely centered around providing convenience
functions to keep complicated LinkML-specific logic out of our Jinja2 templates.
"""

import contextlib
from functools import cached_property

import strcase
from linkml_runtime.linkml_model.meta import ClassDefinition, EnumDefinition, SlotDefinition
from linkml_runtime.utils.schemaview import SchemaView


class FieldWrapper:
    """
    Convenience functions for LinkML slots
    """

    def __init__(self, view: SchemaView, wrapped_field: SlotDefinition):
        self.view = view
        self.wrapped_field = wrapped_field

    def __getattr__(self, attr: str) -> str:
        """
        Error if a property doesn't exist
        """
        raise NotImplementedError(f"please define field property {self.wrapped_field.name}.{attr}")

    @cached_property
    def identifier(self) -> str:
        return self.wrapped_field.identifier

    @cached_property
    def name(self) -> str:
        return self.wrapped_field.name.replace(" ", "_")

    @cached_property
    def description(self) -> str:
        # Make sure to quote this so it's safe!
        return repr(self.wrapped_field.description)

    @cached_property
    def camel_name(self) -> str:
        return strcase.to_lower_camel(self.name)

    @cached_property
    def type_designator(self) -> bool:
        if self.wrapped_field.designates_type:
            return True
        return False

    @cached_property
    def multivalued(self) -> str:
        return self.wrapped_field.multivalued

    @cached_property
    def required(self) -> bool:
        return self.wrapped_field.required or False

    @cached_property
    def designates_type(self) -> bool:
        return self.wrapped_field.designates_type

    # Validation attributes
    @cached_property
    def minimum_value(self) -> float | int | None:
        if self.wrapped_field.minimum_value is not None:
            return self.wrapped_field.minimum_value
        return None

    @cached_property
    def maximum_value(self) -> float | int | None:
        if self.wrapped_field.maximum_value is not None:
            return self.wrapped_field.maximum_value
        return None

    @cached_property
    def is_list_field(self) -> bool:
        if self.wrapped_field.multivalued and self.wrapped_field.inlined_as_list is not None:
            return self.wrapped_field.inlined_as_list
        return False

    @cached_property
    def default_value(self) -> str | None:
        try:
            if self.wrapped_field.ifabsent is not None:
                default_value = self.wrapped_field.ifabsent
                # Make sure to quote this so it's safe!
                return repr(default_value.value)
            if "default_sa_function" in self.wrapped_field.annotations:
                return "func.{func}".format(func=self.wrapped_field.annotations["default_sa_function"].value)
        except AttributeError:
            pass
        return None

    @cached_property
    def default_callable(self) -> str | None:
        if "default_value_callable" in self.wrapped_field.annotations:
            return self.wrapped_field.annotations["default_value_callable"].value
        return None

    @cached_property
    def auto_increment(self) -> bool:
        if "auto_increment" in self.wrapped_field.annotations:
            return self.wrapped_field.annotations["auto_increment"].value
        return False

    @cached_property
    def onupdate(self) -> str | None:
        if "onupdate" in self.wrapped_field.annotations:
            # Make sure to quote this so it's safe!
            return repr(self.wrapped_field.annotations["onupdate"].value)
        if "onupdate_sa_function" in self.wrapped_field.annotations:
            return "func.{func}".format(func=self.wrapped_field.annotations["onupdate_sa_function"].value)
        return None

    @cached_property
    def indexed(self) -> bool:
        if "indexed" in self.wrapped_field.annotations:
            return self.wrapped_field.annotations["indexed"].value
        if self.identifier:
            return True
        with contextlib.suppress(NotImplementedError, AttributeError, ValueError):
            if self.related_class.identifier:
                return True
        return False

    @cached_property
    def minimum_length(self) -> int | None:
        if "minimum_length" in self.wrapped_field.annotations:
            return self.wrapped_field.annotations["minimum_length"].value
        return None

    @cached_property
    def maximum_length(self) -> int | None:
        if "maximum_length" in self.wrapped_field.annotations:
            return self.wrapped_field.annotations["maximum_length"].value
        return None

    @cached_property
    def pattern(self) -> str | None:
        return self.wrapped_field.pattern or None

    # Whether these fields should be exposed in the GQL API
    @cached_property
    def hidden(self) -> bool:
        if "hidden" in self.wrapped_field.annotations:
            return self.wrapped_field.annotations["hidden"].value
        return False

    # Whether these fields can only be written by the API internals
    # All fields are writable by default
    @cached_property
    def readonly(self) -> bool:
        is_readonly = self.wrapped_field.readonly
        if is_readonly:
            return True
        return False

    # Whether these fields should be available to change via an `Update` mutation
    # All fields are mutable by default, so long as they're not marked as readonly
    @cached_property
    def mutable(self) -> bool:
        if self.readonly:
            return False
        if "mutable" in self.wrapped_field.annotations:
            return self.wrapped_field.annotations["mutable"].value
        return True

    # Whether these fields can only be modified by a system user
    @cached_property
    def system_writable_only(self) -> bool:
        if "system_writable_only" in self.wrapped_field.annotations:
            return self.wrapped_field.annotations["system_writable_only"].value
        return False

    @cached_property
    def type(self) -> str:
        return self.wrapped_field.range

    @cached_property
    def inverse(self) -> str:
        return self.wrapped_field.inverse

    @cached_property
    def inverse_class(self) -> str:
        return self.wrapped_field.inverse.split(".")[0]

    @cached_property
    def inverse_class_snake_name(self) -> str:
        return strcase.to_snake(self.inverse_class)

    @cached_property
    def inverse_field(self) -> str:
        return self.wrapped_field.inverse.split(".")[1]

    @cached_property
    def is_enum(self) -> bool:
        field = self.view.get_element(self.wrapped_field.range)
        if isinstance(field, EnumDefinition):
            return True
        return False

    @cached_property
    def is_entity(self) -> bool:
        field = self.view.get_element(self.wrapped_field.range)
        if isinstance(field, ClassDefinition):
            return True
        return False

    @property
    def related_class(self) -> "EntityWrapper":
        return EntityWrapper(self.view, self.view.get_element(self.wrapped_field.range))

    @property
    def related_enum(self) -> "EnumWrapper":
        return EnumWrapper(self.view, self.view.get_element(self.wrapped_field.range))

    @property
    def factory_type(self) -> str | None:
        if "factory_type" in self.wrapped_field.annotations:
            return self.wrapped_field.annotations["factory_type"].value
        return None

    @cached_property
    def is_cascade_delete(self) -> bool:
        if "cascade_delete" in self.wrapped_field.annotations:
            return self.wrapped_field.annotations["cascade_delete"].value
        return False

    @cached_property
    def is_virtual_relationship(self) -> bool | None:
        return self.wrapped_field.range in self.view.all_classes() and self.multivalued


class EnumWrapper:
    """
    Convenience functions for LinkML enums
    """

    def __init__(self, view: SchemaView, wrapped_class: EnumDefinition):
        self.view = view
        self.wrapped_class = wrapped_class

    # Blow up if a property doesn't exist
    def __getattr__(self, attr: str) -> str:
        raise NotImplementedError(f"please define enum property {attr}")

    @cached_property
    def name(self) -> str:
        return self.wrapped_class.name

    @cached_property
    def permissible_values(self) -> str:
        return self.wrapped_class.permissible_values


class EntityWrapper:
    """
    Convenience functions for LinkML entities
    """

    def __init__(self, view: SchemaView, wrapped_class: ClassDefinition):
        self.view = view
        self.wrapped_class = wrapped_class

    # Blow up if a property doesn't exist
    def __getattr__(self, attr: str) -> str:
        raise NotImplementedError(f"please define entity property {self.wrapped_class.name}.{attr}")

    @cached_property
    def description(self) -> str:
        # Make sure to quote this so it's safe!
        return repr(self.wrapped_class.description)

    @cached_property
    def is_abstract(self) -> str:
        return self.wrapped_class.abstract

    @cached_property
    def is_a(self) -> str:
        return self.wrapped_class.is_a

    @cached_property
    def is_a_snake(self) -> str:
        return strcase.to_snake(self.is_a)

    @cached_property
    def parent_key(self) -> FieldWrapper | None:
        if not self.is_a:
            return
        for field in self.all_fields:
            if field.inverse and field.inverse.split(".")[0] == self.is_a_snake:
                return field

    @cached_property
    def type_designator(self) -> FieldWrapper:
        for field in self.all_fields:
            if field.designates_type:
                return field

    @cached_property
    def name(self) -> str:
        return self.wrapped_class.name

    @cached_property
    def plural_camel_name(self) -> str:
        return self.wrapped_class.annotations["plural"].value

    @cached_property
    def plural_snake_name(self) -> str:
        return strcase.to_snake(self.plural_camel_name)

    @cached_property
    def camel_name(self) -> str:
        return self.wrapped_class.name

    @cached_property
    def snake_name(self) -> str:
        return strcase.to_snake(self.name)

    @cached_property
    def writable_fields(self) -> list[FieldWrapper]:
        return [FieldWrapper(self.view, item) for item in self.view.class_induced_slots(self.name) if not item.readonly]

    @cached_property
    def identifier(self) -> FieldWrapper:
        # Prioritize sending back identifiers from the current class and mixins instead of inherited fields.
        domains_owned_by_this_class = set(self.wrapped_class.mixins + [self.name])
        for field in self.all_fields:
            if field.identifier and domains_owned_by_this_class.intersection(set(field.wrapped_field.domain_of)):
                return field
        for field in self.all_fields:
            if field.identifier and self.name in field.wrapped_field.domain_of:
                return field
        raise Exception("No identifier found")

    @cached_property
    def create_fields(self) -> list[FieldWrapper]:
        return [
            field
            for field in self.visible_fields
            if not field.readonly and not field.hidden and not field.is_virtual_relationship
        ]

    @cached_property
    def mutable_fields(self) -> list[FieldWrapper]:
        if not self.is_mutable:
            return []
        return [field for field in self.visible_fields if field.mutable and not field.is_virtual_relationship]

    @cached_property
    def is_mutable(self) -> bool:
        if "mutable" in self.wrapped_class.annotations:
            return self.wrapped_class.annotations["mutable"].value
        return True

    @cached_property
    def is_system_only_mutable(self) -> bool:
        if "system_writable_only" in self.wrapped_class.annotations:
            return self.wrapped_class.annotations["system_writable_only"].value
        return False

    @cached_property
    def all_fields(self) -> list[FieldWrapper]:
        return [FieldWrapper(self.view, item) for item in self.view.class_induced_slots(self.name)]

    @cached_property
    def visible_fields(self) -> list[FieldWrapper]:
        return [field for field in self.all_fields if not field.hidden]

    @cached_property
    def numeric_fields(self) -> list[FieldWrapper]:
        return [field for field in self.visible_fields if field.type in ["integer", "float"]]

    @cached_property
    def user_create_fields(self) -> list[FieldWrapper]:
        if self.is_system_only_mutable:
            return []
        return [field for field in self.create_fields if not field.system_writable_only]

    @cached_property
    def system_only_create_fields(self) -> list[FieldWrapper]:
        if self.is_system_only_mutable:
            return list(self.create_fields)
        return [field for field in self.create_fields if field.system_writable_only]

    @cached_property
    def user_mutable_fields(self) -> list[FieldWrapper]:
        if self.is_system_only_mutable:
            return []
        return [field for field in self.mutable_fields if not field.system_writable_only]

    @cached_property
    def system_only_mutable_fields(self) -> list[FieldWrapper]:
        if self.is_system_only_mutable:
            return list(self.mutable_fields)
        return [field for field in self.mutable_fields if field.system_writable_only]

    @cached_property
    def owned_fields(self) -> list[FieldWrapper]:
        domains_owned_by_this_class = set(self.wrapped_class.mixins + [self.name])
        return [
            FieldWrapper(self.view, item)
            for item in self.view.class_induced_slots(self.name)
            if domains_owned_by_this_class.intersection(set(item.domain_of))
        ]

    @cached_property
    def enum_fields(self) -> list[FieldWrapper]:
        enumfields = self.view.all_enums()
        class_names = [k for k, _ in enumfields.items()]
        return [field for field in self.visible_fields if field.type in class_names]

    @cached_property
    def related_fields(self) -> list[FieldWrapper]:
        return [field for field in self.visible_fields if field.is_entity]


class ViewWrapper:
    """
    Convenience functions for LinkML schema views
    """

    def __init__(self, view: SchemaView):
        self.view = view

    # Blow up if a property doesn't exist
    def __getattr__(self, attr: str) -> str:
        raise NotImplementedError(f"please define view property {attr}")

    @cached_property
    def enums(self) -> list[EnumWrapper]:
        enums = []
        for enum_name in self.view.all_enums():
            enum = self.view.get_element(enum_name)
            # Don't codegen stuff that users asked us not to.
            if enum.annotations.get("skip_codegen") and enum.annotations["skip_codegen"].value:
                continue
            enums.append(EnumWrapper(self.view, enum))
        return enums

    @cached_property
    def entities(self) -> list[EntityWrapper]:
        classes = []
        for class_name in self.view.all_classes():
            cls = self.view.get_element(class_name)
            # Don't codegen stuff that users asked us not to.
            if cls.annotations.get("skip_codegen") and cls.annotations["skip_codegen"].value:
                continue
            # Mixins don't get represented in the outputted schemas
            if cls.mixin:
                continue
            classes.append(EntityWrapper(self.view, cls))
        return classes
