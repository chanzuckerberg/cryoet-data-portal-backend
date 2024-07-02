# Enum: AnnotationShapeEnum




_Annotation shape types available on the data portal._



URI: [AnnotationShapeEnum](AnnotationShapeEnum.md)

## Permissible Values

| Value | Meaning | Description |
| --- | --- | --- |
| InstanceSegmentation | None | Annotation that identifies individual instances of object shapes |
| Point | None | Annotation that identifies points in the volume |
| OrientedPoint | None | Annotation that identifies points along with orientation in the volume |
| SegmentationMask | None | Annotation that identifies an object |
| SemanticSegmentationMask | None | Annotation that identifies classes of objects |









## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## LinkML Source

<details>
```yaml
name: annotation_shape_enum
description: Annotation shape types available on the data portal.
from_schema: metadata
rank: 1000
permissible_values:
  InstanceSegmentation:
    text: InstanceSegmentation
    description: Annotation that identifies individual instances of object shapes.
  Point:
    text: Point
    description: Annotation that identifies points in the volume.
  OrientedPoint:
    text: OrientedPoint
    description: Annotation that identifies points along with orientation in the volume.
  SegmentationMask:
    text: SegmentationMask
    description: Annotation that identifies an object.
  SemanticSegmentationMask:
    text: SemanticSegmentationMask
    description: Annotation that identifies classes of objects.

```
</details>
