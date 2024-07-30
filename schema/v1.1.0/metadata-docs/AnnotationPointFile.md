

# Class: AnnotationPointFile


_File and sourcing data for a point annotation. Annotation that identifies points in the volume._





URI: [cdp-meta:AnnotationPointFile](metadataAnnotationPointFile)






```mermaid
 classDiagram
    class AnnotationPointFile
    click AnnotationPointFile href "../AnnotationPointFile"
      AnnotationSourceFile <|-- AnnotationPointFile
        click AnnotationSourceFile href "../AnnotationSourceFile"

      AnnotationPointFile : binning

      AnnotationPointFile : columns

      AnnotationPointFile : delimiter

      AnnotationPointFile : file_format

      AnnotationPointFile : glob_string

      AnnotationPointFile : glob_strings

      AnnotationPointFile : is_visualization_default


```





## Inheritance
* [AnnotationSourceFile](AnnotationSourceFile.md)
    * **AnnotationPointFile**



## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [binning](binning.md) | 0..1 <br/> [Float](Float.md) | The binning factor for a point / oriented point / instance segmentation annot... | direct |
| [columns](columns.md) | 0..1 <br/> [String](String.md) | The columns used in a point annotation file | direct |
| [delimiter](delimiter.md) | 0..1 <br/> [String](String.md) | The delimiter used in a point annotation file | direct |
| [file_format](file_format.md) | 1 <br/> [String](String.md) | File format for this file | direct |
| [glob_string](glob_string.md) | 0..1 <br/> [String](String.md) | Glob string to match annotation files in the dataset | direct |
| [glob_strings](glob_strings.md) | * <br/> [String](String.md) | Glob strings to match annotation files in the dataset | direct |
| [is_visualization_default](is_visualization_default.md) | 0..1 <br/> [Boolean](Boolean.md) | This annotation will be rendered in neuroglancer by default | direct |







## Aliases


* Point



## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:AnnotationPointFile |
| native | cdp-meta:AnnotationPointFile |







## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: AnnotationPointFile
description: File and sourcing data for a point annotation. Annotation that identifies
  points in the volume.
from_schema: metadata
aliases:
- Point
is_a: AnnotationSourceFile
attributes:
  binning:
    name: binning
    description: The binning factor for a point / oriented point / instance segmentation
      annotation file.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_binning
    ifabsent: float(1)
    alias: binning
    owner: AnnotationPointFile
    domain_of:
    - AnnotationOrientedPointFile
    - AnnotationPointFile
    - AnnotationInstanceSegmentationFile
    range: float
    inlined: true
    inlined_as_list: true
    minimum_value: 0
  columns:
    name: columns
    description: The columns used in a point annotation file.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_columns
    rank: 1000
    ifabsent: string(xyz)
    alias: columns
    owner: AnnotationPointFile
    domain_of:
    - AnnotationPointFile
    range: string
    inlined: true
    inlined_as_list: true
  delimiter:
    name: delimiter
    description: The delimiter used in a point annotation file.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_delimiter
    rank: 1000
    ifabsent: string(,)
    alias: delimiter
    owner: AnnotationPointFile
    domain_of:
    - AnnotationPointFile
    range: string
    inlined: true
    inlined_as_list: true
  file_format:
    name: file_format
    description: File format for this file
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_format
    alias: file_format
    owner: AnnotationPointFile
    domain_of:
    - AnnotationSourceFile
    - AnnotationOrientedPointFile
    - AnnotationInstanceSegmentationFile
    - AnnotationPointFile
    - AnnotationSegmentationMaskFile
    - AnnotationSemanticSegmentationMaskFile
    range: string
    required: true
    inlined: true
    inlined_as_list: true
  glob_string:
    name: glob_string
    description: Glob string to match annotation files in the dataset. Required if
      annotation_source_file_glob_strings is not provided.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_glob_string
    alias: glob_string
    owner: AnnotationPointFile
    domain_of:
    - AnnotationSourceFile
    - AnnotationOrientedPointFile
    - AnnotationInstanceSegmentationFile
    - AnnotationPointFile
    - AnnotationSegmentationMaskFile
    - AnnotationSemanticSegmentationMaskFile
    range: string
    required: false
    inlined: true
    inlined_as_list: true
  glob_strings:
    name: glob_strings
    description: Glob strings to match annotation files in the dataset. Required if
      annotation_source_file_glob_string is not provided.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_glob_strings
    alias: glob_strings
    owner: AnnotationPointFile
    domain_of:
    - AnnotationSourceFile
    - AnnotationOrientedPointFile
    - AnnotationInstanceSegmentationFile
    - AnnotationPointFile
    - AnnotationSegmentationMaskFile
    - AnnotationSemanticSegmentationMaskFile
    range: string
    required: false
    multivalued: true
    inlined: true
    inlined_as_list: true
  is_visualization_default:
    name: is_visualization_default
    description: This annotation will be rendered in neuroglancer by default.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_is_visualization_default
    ifabsent: 'False'
    alias: is_visualization_default
    owner: AnnotationPointFile
    domain_of:
    - AnnotationSourceFile
    - AnnotationOrientedPointFile
    - AnnotationInstanceSegmentationFile
    - AnnotationPointFile
    - AnnotationSegmentationMaskFile
    - AnnotationSemanticSegmentationMaskFile
    range: boolean
    inlined: true
    inlined_as_list: true

```
</details>

### Induced

<details>
```yaml
name: AnnotationPointFile
description: File and sourcing data for a point annotation. Annotation that identifies
  points in the volume.
from_schema: metadata
aliases:
- Point
is_a: AnnotationSourceFile
attributes:
  binning:
    name: binning
    description: The binning factor for a point / oriented point / instance segmentation
      annotation file.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_binning
    ifabsent: float(1)
    alias: binning
    owner: AnnotationPointFile
    domain_of:
    - AnnotationOrientedPointFile
    - AnnotationPointFile
    - AnnotationInstanceSegmentationFile
    range: float
    inlined: true
    inlined_as_list: true
    minimum_value: 0
  columns:
    name: columns
    description: The columns used in a point annotation file.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_columns
    rank: 1000
    ifabsent: string(xyz)
    alias: columns
    owner: AnnotationPointFile
    domain_of:
    - AnnotationPointFile
    range: string
    inlined: true
    inlined_as_list: true
  delimiter:
    name: delimiter
    description: The delimiter used in a point annotation file.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_delimiter
    rank: 1000
    ifabsent: string(,)
    alias: delimiter
    owner: AnnotationPointFile
    domain_of:
    - AnnotationPointFile
    range: string
    inlined: true
    inlined_as_list: true
  file_format:
    name: file_format
    description: File format for this file
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_format
    alias: file_format
    owner: AnnotationPointFile
    domain_of:
    - AnnotationSourceFile
    - AnnotationOrientedPointFile
    - AnnotationInstanceSegmentationFile
    - AnnotationPointFile
    - AnnotationSegmentationMaskFile
    - AnnotationSemanticSegmentationMaskFile
    range: string
    required: true
    inlined: true
    inlined_as_list: true
  glob_string:
    name: glob_string
    description: Glob string to match annotation files in the dataset. Required if
      annotation_source_file_glob_strings is not provided.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_glob_string
    alias: glob_string
    owner: AnnotationPointFile
    domain_of:
    - AnnotationSourceFile
    - AnnotationOrientedPointFile
    - AnnotationInstanceSegmentationFile
    - AnnotationPointFile
    - AnnotationSegmentationMaskFile
    - AnnotationSemanticSegmentationMaskFile
    range: string
    required: false
    inlined: true
    inlined_as_list: true
  glob_strings:
    name: glob_strings
    description: Glob strings to match annotation files in the dataset. Required if
      annotation_source_file_glob_string is not provided.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_glob_strings
    alias: glob_strings
    owner: AnnotationPointFile
    domain_of:
    - AnnotationSourceFile
    - AnnotationOrientedPointFile
    - AnnotationInstanceSegmentationFile
    - AnnotationPointFile
    - AnnotationSegmentationMaskFile
    - AnnotationSemanticSegmentationMaskFile
    range: string
    required: false
    multivalued: true
    inlined: true
    inlined_as_list: true
  is_visualization_default:
    name: is_visualization_default
    description: This annotation will be rendered in neuroglancer by default.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_is_visualization_default
    ifabsent: 'False'
    alias: is_visualization_default
    owner: AnnotationPointFile
    domain_of:
    - AnnotationSourceFile
    - AnnotationOrientedPointFile
    - AnnotationInstanceSegmentationFile
    - AnnotationPointFile
    - AnnotationSegmentationMaskFile
    - AnnotationSemanticSegmentationMaskFile
    range: boolean
    inlined: true
    inlined_as_list: true

```
</details>
