# Enum: AnnotationMethodTypeEnum




_Describes how the annotations were generated._



URI: [AnnotationMethodTypeEnum](AnnotationMethodTypeEnum.md)

## Permissible Values

| Value | Meaning | Description |
| --- | --- | --- |
| manual | None | Annotations were generated manually |
| automated | None | Annotations were generated semi-automatically |
| hybrid | None | Annotations were generated automatically |




## Slots

| Name | Description |
| ---  | --- |
| [annotation_method_type](annotation_method_type.md) | Classification of the annotation method based on supervision |






## Identifier and Mapping Information







### Schema Source


* from schema: https://cryoetdataportal.czscience.com/schema-docs/metadata




## LinkML Source

<details>
```yaml
name: annotation_method_type_enum
description: Describes how the annotations were generated.
from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
rank: 1000
permissible_values:
  manual:
    text: manual
    description: Annotations were generated manually.
  automated:
    text: automated
    description: Annotations were generated semi-automatically.
  hybrid:
    text: hybrid
    description: Annotations were generated automatically.

```
</details>
