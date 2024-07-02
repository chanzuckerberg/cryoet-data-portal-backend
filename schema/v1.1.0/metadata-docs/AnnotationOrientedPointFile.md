

# Class: AnnotationOrientedPointFile


_File and sourcing data for an oriented point annotation. Annotation that identifies points along with orientation in the volume._





URI: [cdp-meta:AnnotationOrientedPointFile](metadataAnnotationOrientedPointFile)






```mermaid
 classDiagram
    class AnnotationOrientedPointFile
    click AnnotationOrientedPointFile href "../AnnotationOrientedPointFile"
      AnnotationSourceFile <|-- AnnotationOrientedPointFile
        click AnnotationSourceFile href "../AnnotationSourceFile"
      

      AnnotationOrientedPointFile <|-- AnnotationInstanceSegmentationFile
        click AnnotationInstanceSegmentationFile href "../AnnotationInstanceSegmentationFile"
      
      
      AnnotationOrientedPointFile : binning
        
      AnnotationOrientedPointFile : file_format
        
      AnnotationOrientedPointFile : filter_value
        
      AnnotationOrientedPointFile : glob_string
        
      AnnotationOrientedPointFile : is_visualization_default
        
      AnnotationOrientedPointFile : order
        
      
```





## Inheritance
* [AnnotationSourceFile](AnnotationSourceFile.md)
    * **AnnotationOrientedPointFile**
        * [AnnotationInstanceSegmentationFile](AnnotationInstanceSegmentationFile.md)



## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [binning](binning.md) | 0..1 <br/> [Integer](Integer.md) | The binning factor for a point / oriented point / instance segmentation annot... | direct |
| [filter_value](filter_value.md) | 0..1 <br/> [String](String.md) | The filter value for an oriented point / instance segmentation annotation fil... | direct |
| [order](order.md) | 0..1 <br/> [String](String.md) | The order of axes for an oriented point / instance segmentation annotation fi... | direct |
| [file_format](file_format.md) | 1 <br/> [String](String.md) |  | direct |
| [glob_string](glob_string.md) | 1 <br/> [String](String.md) |  | direct |
| [is_visualization_default](is_visualization_default.md) | 0..1 <br/> [Boolean](Boolean.md) |  | direct |







## Aliases


* OrientedPoint



## Identifier and Mapping Information







### Schema Source


* from schema: metadata





## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:AnnotationOrientedPointFile |
| native | cdp-meta:AnnotationOrientedPointFile |





## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: AnnotationOrientedPointFile
description: File and sourcing data for an oriented point annotation. Annotation that
  identifies points along with orientation in the volume.
from_schema: metadata
aliases:
- OrientedPoint
is_a: AnnotationSourceFile
attributes:
  binning:
    name: binning
    description: The binning factor for a point / oriented point / instance segmentation
      annotation file.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_binning
    rank: 1000
    ifabsent: int(1)
    alias: binning
    owner: AnnotationOrientedPointFile
    domain_of:
    - AnnotationOrientedPointFile
    - AnnotationPointFile
    - AnnotationInstanceSegmentationFile
    range: integer
    inlined: true
    inlined_as_list: true
  filter_value:
    name: filter_value
    description: The filter value for an oriented point / instance segmentation annotation
      file.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_filter_value
    rank: 1000
    alias: filter_value
    owner: AnnotationOrientedPointFile
    domain_of:
    - AnnotationOrientedPointFile
    - AnnotationInstanceSegmentationFile
    range: string
    inlined: true
    inlined_as_list: true
  order:
    name: order
    description: The order of axes for an oriented point / instance segmentation annotation
      file.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_order
    rank: 1000
    alias: order
    owner: AnnotationOrientedPointFile
    domain_of:
    - AnnotationOrientedPointFile
    - AnnotationInstanceSegmentationFile
    range: string
    inlined: true
    inlined_as_list: true
  file_format:
    name: file_format
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_format
    alias: file_format
    owner: AnnotationOrientedPointFile
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
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_glob_string
    alias: glob_string
    owner: AnnotationOrientedPointFile
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
  is_visualization_default:
    name: is_visualization_default
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_is_visualization_default
    alias: is_visualization_default
    owner: AnnotationOrientedPointFile
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
name: AnnotationOrientedPointFile
description: File and sourcing data for an oriented point annotation. Annotation that
  identifies points along with orientation in the volume.
from_schema: metadata
aliases:
- OrientedPoint
is_a: AnnotationSourceFile
attributes:
  binning:
    name: binning
    description: The binning factor for a point / oriented point / instance segmentation
      annotation file.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_binning
    rank: 1000
    ifabsent: int(1)
    alias: binning
    owner: AnnotationOrientedPointFile
    domain_of:
    - AnnotationOrientedPointFile
    - AnnotationPointFile
    - AnnotationInstanceSegmentationFile
    range: integer
    inlined: true
    inlined_as_list: true
  filter_value:
    name: filter_value
    description: The filter value for an oriented point / instance segmentation annotation
      file.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_filter_value
    rank: 1000
    alias: filter_value
    owner: AnnotationOrientedPointFile
    domain_of:
    - AnnotationOrientedPointFile
    - AnnotationInstanceSegmentationFile
    range: string
    inlined: true
    inlined_as_list: true
  order:
    name: order
    description: The order of axes for an oriented point / instance segmentation annotation
      file.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_order
    rank: 1000
    alias: order
    owner: AnnotationOrientedPointFile
    domain_of:
    - AnnotationOrientedPointFile
    - AnnotationInstanceSegmentationFile
    range: string
    inlined: true
    inlined_as_list: true
  file_format:
    name: file_format
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_format
    alias: file_format
    owner: AnnotationOrientedPointFile
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
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_glob_string
    alias: glob_string
    owner: AnnotationOrientedPointFile
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
  is_visualization_default:
    name: is_visualization_default
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_is_visualization_default
    alias: is_visualization_default
    owner: AnnotationOrientedPointFile
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