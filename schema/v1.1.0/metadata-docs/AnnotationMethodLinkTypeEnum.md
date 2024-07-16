# Enum: AnnotationMethodLinkTypeEnum




_Describes the type of link associated to the annotation method._



URI: [AnnotationMethodLinkTypeEnum](AnnotationMethodLinkTypeEnum.md)

## Permissible Values

| Value | Meaning | Description |
| --- | --- | --- |
| documentation | None | Links to the documentation related to the method |
| models_weights | None | Links to the weights that the models used for generating annotations were tra... |
| other | None | Link to resources that does not fit in the other categories |
| source_code | None | Links to the source code of the method |
| website | None | Links to a website of the method or tool used to generate the annotation |




## Slots

| Name | Description |
| ---  | --- |
| [link_type](link_type.md) | Type of link (e |






## Identifier and Mapping Information







### Schema Source


* from schema: metadata






## LinkML Source

<details>
```yaml
name: annotation_method_link_type_enum
description: Describes the type of link associated to the annotation method.
from_schema: metadata
rank: 1000
permissible_values:
  documentation:
    text: documentation
    description: Links to the documentation related to the method.
  models_weights:
    text: models_weights
    description: Links to the weights that the models used for generating annotations
      were trained with.
  other:
    text: other
    description: Link to resources that does not fit in the other categories.
  source_code:
    text: source_code
    description: Links to the source code of the method.
  website:
    text: website
    description: Links to a website of the method or tool used to generate the annotation.

```
</details>
