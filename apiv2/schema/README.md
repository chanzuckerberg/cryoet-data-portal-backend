# Schema Configuration

Platformics supports defining a schema as a human-readable YAML file using the [LinkML](https://linkml.io/linkml/) language, and also supports some additional functionality on top of LinkML's features.

For a list of commands to run when making changes to the schema, see also [Iterating on your schema](https://github.com/chanzuckerberg/platformics/tree/main?tab=readme-ov-file#iterating-on-your-schema).

## Writing your own schema

### Types

> See also LinkML's [documentation on types](https://linkml.io/linkml/schemas/models.html#types).

Types are scalar data values such as strings, integers, and floats. LinkML defines some types by default which can be extended, and you can also define your own types.

These are typically used to define the `range` of a `class`'s [attribute](#attributes).

```yaml
types:
    string:
        uri: xsd:string
        base: str
        description: A character string

    integer:
        uri: xsd:integer
        base: int
        description: An integer

    uuid:
        uri: xsd:string
        typeof: str
        base: str
        description: A UUID
```

### Enums

> See also LinkML's [documentation on enums](https://linkml.io/linkml/schemas/models.html#enums).

Enums can be used to define a set of allowed string attributes. You may optionally include a description of the enum's options.

```yaml
enums:
    Month:
        permissible_values:
            January:
            February:
            March:
            April:
            May:
            June:
            July:
            August:
            September:
            October:
            November:
            December:

    Status:
        permissible_values:
            SUCCESS:
                description: The file finished processing successfully.
            FAILED:
                description: The file encountered an error and failed to process.
            PENDING:
                description: The file is currently being uploaded and has not started processing yet.
```

### Classes

> See also LinkML's [documentation on classes](https://linkml.io/linkml/schemas/models.html#classes).

Classes equate to the models in the schema (i.e. tables in the database).

They are defined in a `classes` block, with the class name as the key.

```yaml
classes:
    Book:
        ...
```

#### Attributes

> See also LinkML's [documentation on attributes](https://linkml.io/linkml/schemas/models.html#the-attributes-slot).

An attribute equates to a field on the model (i.e. a column on the database table).

There are a few properities on attributes that are used in Platformics:

* [range](https://linkml.io/linkml/schemas/slots.html#ranges) (required): Defines the type of a field. This can be a type, enum, or another class.
* [multivalued](https://linkml.io/linkml/schemas/slots.html#multivalued): Boolean indicating if the attribute is a list; `false` by default.
* [required](https://linkml.io/linkml/schemas/slots.html#required): Boolean indicating if the attribute is required for this class; `false` by default.
* [inverse](https://linkml.io/linkml/schemas/slots.html#inverse): String indicating the inverse relationship. This typically should only be used if `range` is another class, which has a corresponding attribute.
  * In base LinkML, this is typically just used as documentation. However, in Platformics, this field is used to establish relationships between classes, and additional code will be generated appropriately.
* [identifier](https://linkml.io/linkml/schemas/slots.html#identifiers): Boolean indicating that the field is a unique key for members of the class; `false` by default.
* `readonly`: Boolean indicating whether field can only be written by the API internals; `false` by default. This is implemented by Platformics and is not a part of base LinkML functionality.
* `minimum_length` / `maximum_length`: Used to set lower/upper bounds on the length for values in a `string` column.
* `minimum_value` / `maximum_value`: Used to set lower/upper bounds on the values in a numerical column.

```yaml
classes:
    Author:
        attributes:
            name:
                range: string
                required: true
                minimum_length: 4
                maximum_length: 128
            published_works:
                range: Book
                multivalued: true
                inverse: Book.author
            id:
                identifier: true
                range: integer
                readonly: true
                minimum_value: 0
                maximum_value: 10000

    Book:
        attributes:
            title:
                range: string
                required: true
            author:
                range: Author
                inverse: Author.published_works
```

#### Annotations

> See also the LinkML [documentation on annotations](https://linkml.io/linkml/schemas/annotations.html).

Annotations are used to provide additional information on a class or its attributes.

##### Class Annotations

* `plural` (required): String indicating the plural form of the class's name; used for human-readability and parts of codegen. This is implemented by Platformics and is not a part of base LinkML functionality.

```yaml
classes:
    Author:
        annotations:
            plural: Authors

    Book:
        annotations:
            plural: Books

    Entity:
        annotations:
            plural: Entities
```

##### Attribute Annotations

The follow annotations are related to setting permissions; they are implemented by Platformics and are not a part of base LinkML functionality:
* `hidden`: Boolean indicating whether field will be exposed in the GQL API; `false` by default.
* `system_writable_only`: Boolean indicating whether field can only be modified by a system user; `false` by default.
* `mutable`: Boolean indicating whether field is available to be modified via an `Update` mutation. If the field is **not** marked as `readonly`, `mutable` is `true` by default.

```yaml
classes:
    Author:
        attributes:
            name:
                range: string
                required: true
            published_works:
                range: Book
                multivalued: true
                inverse: Book.author
            address:
                range: string
                annotations:
                    hidden: true
            id:
                identifier: true
                range: integer
                readonly: true

    Book:
        attributes:
            title:
                range: string
                required: true
            author:
                range: Author
                inverse: Author.published_works
            ISBN: # International Standard Book Number
                identifier: true
                range: integer
                annotations:
                    mutable: false
                    system_writable_only: true

```

Other annotations; these are implemented by Platformics and are not a part of base LinkML functionality:
* `indexed`: Boolean indicating whether to create an index for this column; `false` by default.
* `cascade_delete`: Boolean indicating if the child object should be deleted along with the parent object; `false` by default.
* `factory_type`: Used in testing and for generating default seed data. We use [Faker](https://factoryboy.readthedocs.io/en/stable/reference.html#faker) from `factory` to generate data, so `factory_type` must be a type supported by `Faker`.

```yaml
classes:
    Author:
        attributes:
            name:
                range: string
                required: true
                annotations:
                    factory_type: name
            published_works:
                range: Book
                multivalued: true
                inverse: Book.author
                annotations:
                    # If the author is deleted, delete the associated books as well
                    cascade_delete: true

    Book:
        attributes:
            title:
                range: string
                required: true
            author:
                range: Author
                inverse: Author.published_works
            ISBN: # International Standard Book Number
                identifier: true
                range: integer
                annotations:
                    indexed: true
```

#### Inheritance

> See also LinkML's [documentation on inheritance](https://linkml.io/linkml/schemas/inheritance.html).

##### Type designators

> See also LinkML's [documentation on type designators](https://linkml.io/linkml/schemas/type-designators.html).

To enforce that object instances have the `type` of its `class`, you can set the `designates_type` slot on the `class` to `true`.

In this example, any instance of "Organization" (or any instance of a subclass that inherits from "Organization") must have the `type` "Organization."

```yaml
classes:
    Organization:
        attributes:
        name:
        type:
            designates_type: true
            range: string
    Business:
        is_a: Organization
    EducationalOrganization:
        is_a: Organization
    ...
```


##### `is_a`

A class can inherit from another class, including its inheritable attributes, using the `is_a` slot.

```yaml
classes:
    Literature:
        attributes:
            title:
                range: string
                required: true
            author:
                range: string
                required: true
            ...

    Book:
        # Book will inherit the attributes of Literature
        is_a: Literature
        attributes:
            ...

    Article:
        # Article will inherit the attributes of Literature
        is_a: Literature
        attributes:
            ...
```


##### Mixins

> See also LinkML's [documentation on mixins](https://linkml.io/linkml/schemas/inheritance.html#mixin-classes-and-slots).

Mixins can be used to define a set of shared attributes among classes that don't necessarily inherit from each other.

Use the `mixin` boolean slot to indicate that a class is a mixin, and the `mixins` multivalued slot to indicate which mixins a class inherits from.


```yaml
classes:
    Author:
        # Specify mixin parent(s)
        mixins:
            - Alias
        published_works:
            range: Book
            multivalued: true
            inverse: Book.author


    Book:
        # Specify mixin parent(s)
        mixins:
            - Alias
        attributes:
            author:
                range: Author
                inverse: Author.published_works

    Alias:
        # Declare the class as a mixin
        mixin: true
        attributes:
            name:
                range: string
                required: true
            nickname:
                range: string
            description:
                range: string
```
