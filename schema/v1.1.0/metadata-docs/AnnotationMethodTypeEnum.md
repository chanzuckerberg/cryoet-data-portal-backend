# Enum: AnnotationMethodTypeEnum




_Describes how the annotations were generated._



URI: [AnnotationMethodTypeEnum](AnnotationMethodTypeEnum.md)

## Permissible Values

| Value | Meaning | Description |
| --- | --- | --- |
| manual | None | Annotations were generated manually |
| automated | None | Annotations were generated automatically |
| hybrid | None | Annotations were generated semi-automatically |




## Slots

| Name | Description |
| ---  | --- |
| [method_type](method_type.md) | Classification of the annotation method based on supervision |






## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## LinkML Source

<details>
```yaml
name: annotation_method_type_enum
description: Describes how the annotations were generated.
from_schema: metadata
rank: 1000
permissible_values:
  manual:
    text: manual
    description: Annotations were generated manually.
  automated:
    text: automated
    description: Annotations were generated automatically.
  hybrid:
    text: hybrid
    description: Annotations were generated semi-automatically.

```
</details>
