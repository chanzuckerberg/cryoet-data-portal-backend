

# Class: AnnotationInstanceSegmentationFile


_File and sourcing data for an instance segmentation annotation._





URI: [cdp-meta:AnnotationInstanceSegmentationFile](metadataAnnotationInstanceSegmentationFile)






```mermaid
 classDiagram
    class AnnotationInstanceSegmentationFile
    click AnnotationInstanceSegmentationFile href "../AnnotationInstanceSegmentationFile"
      AnnotationOrientedPointFile <|-- AnnotationInstanceSegmentationFile
        click AnnotationOrientedPointFile href "../AnnotationOrientedPointFile"
      
      AnnotationInstanceSegmentationFile : binning
        
      AnnotationInstanceSegmentationFile : file_format
        
      AnnotationInstanceSegmentationFile : filter_value
        
      AnnotationInstanceSegmentationFile : glob_string
        
      AnnotationInstanceSegmentationFile : is_visualization_default
        
      AnnotationInstanceSegmentationFile : order
        
      
```





## Inheritance
* [AnnotationSourceFile](AnnotationSourceFile.md)
    * [AnnotationOrientedPointFile](AnnotationOrientedPointFile.md)
        * **AnnotationInstanceSegmentationFile**



## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [binning](binning.md) | 0..1 <br/> [Integer](Integer.md) |  | direct |
| [filter_value](filter_value.md) | 0..1 <br/> [String](String.md) |  | direct |
| [order](order.md) | 0..1 <br/> [String](String.md) |  | direct |
| [file_format](file_format.md) | 1 <br/> [String](String.md) |  | direct |
| [glob_string](glob_string.md) | 1 <br/> [String](String.md) |  | direct |
| [is_visualization_default](is_visualization_default.md) | 0..1 <br/> [Boolean](Boolean.md) |  | direct |







## Aliases


* InstanceSegmentation



## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:AnnotationInstanceSegmentationFile |
| native | cdp-meta:AnnotationInstanceSegmentationFile |







## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: AnnotationInstanceSegmentationFile
description: File and sourcing data for an instance segmentation annotation.
from_schema: metadata
aliases:
- InstanceSegmentation
is_a: AnnotationOrientedPointFile
attributes:
  binning:
    name: binning
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_binning
    alias: binning
    owner: AnnotationInstanceSegmentationFile
    domain_of:
    - AnnotationOrientedPointFile
    - AnnotationPointFile
    - AnnotationInstanceSegmentationFile
    range: integer
    inlined: true
    inlined_as_list: true
  filter_value:
    name: filter_value
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_filter_value
    alias: filter_value
    owner: AnnotationInstanceSegmentationFile
    domain_of:
    - AnnotationOrientedPointFile
    - AnnotationInstanceSegmentationFile
    range: string
    inlined: true
    inlined_as_list: true
  order:
    name: order
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_order
    alias: order
    owner: AnnotationInstanceSegmentationFile
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
    owner: AnnotationInstanceSegmentationFile
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
    owner: AnnotationInstanceSegmentationFile
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
    owner: AnnotationInstanceSegmentationFile
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
name: AnnotationInstanceSegmentationFile
description: File and sourcing data for an instance segmentation annotation.
from_schema: metadata
aliases:
- InstanceSegmentation
is_a: AnnotationOrientedPointFile
attributes:
  binning:
    name: binning
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_binning
    alias: binning
    owner: AnnotationInstanceSegmentationFile
    domain_of:
    - AnnotationOrientedPointFile
    - AnnotationPointFile
    - AnnotationInstanceSegmentationFile
    range: integer
    inlined: true
    inlined_as_list: true
  filter_value:
    name: filter_value
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_filter_value
    alias: filter_value
    owner: AnnotationInstanceSegmentationFile
    domain_of:
    - AnnotationOrientedPointFile
    - AnnotationInstanceSegmentationFile
    range: string
    inlined: true
    inlined_as_list: true
  order:
    name: order
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_order
    alias: order
    owner: AnnotationInstanceSegmentationFile
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
    owner: AnnotationInstanceSegmentationFile
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
    owner: AnnotationInstanceSegmentationFile
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
    owner: AnnotationInstanceSegmentationFile
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