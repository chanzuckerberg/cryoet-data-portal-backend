# Enum: AnnotationShapeEnum




_Annotation shape types available on the data portal._



URI: [AnnotationShapeEnum](AnnotationShapeEnum.md)

## Permissible Values

| Value | Meaning | Description |
| --- | --- | --- |
| Point | None | Annotations were generated manually |
| OrientedPoint | None | Annotations were generated semi-automatically |
| SegmentationMask | None | Annotations were generated automatically |









## Identifier and Mapping Information







### Schema Source


* from schema: https://cryoetdataportal.czscience.com/schema-docs/metadata




## LinkML Source

<details>
```yaml
name: annotation_shape_enum
description: Annotation shape types available on the data portal.
from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
rank: 1000
permissible_values:
  Point:
    text: Point
    description: Annotations were generated manually.
  OrientedPoint:
    text: OrientedPoint
    description: Annotations were generated semi-automatically.
  SegmentationMask:
    text: SegmentationMask
    description: Annotations were generated automatically.

```
</details>
