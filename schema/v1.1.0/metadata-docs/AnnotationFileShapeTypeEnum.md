# Enum: AnnotationFileShapeTypeEnum




_Describes the shape of the annotation_



URI: [AnnotationFileShapeTypeEnum](AnnotationFileShapeTypeEnum.md)

## Permissible Values

| Value | Meaning | Description |
| --- | --- | --- |
| SegmentationMask | None | A binary mask volume |
| OrientedPoint | None | A series of coordinates and an orientation |
| Point | None | A series of coordinates |
| InstanceSegmentation | None | A volume with labels for multiple instances |









## Identifier and Mapping Information







### Schema Source


* from schema: metadata






## LinkML Source

<details>
```yaml
name: annotation_file_shape_type_enum
description: Describes the shape of the annotation
from_schema: metadata
rank: 1000
permissible_values:
  SegmentationMask:
    text: SegmentationMask
    description: A binary mask volume
  OrientedPoint:
    text: OrientedPoint
    description: A series of coordinates and an orientation
  Point:
    text: Point
    description: A series of coordinates
  InstanceSegmentation:
    text: InstanceSegmentation
    description: A volume with labels for multiple instances

```
</details>
