

# Class: AnnotationSourceFile


_File and sourcing data for an annotation. Represents an entry in annotation.sources._





URI: [cdp-meta:AnnotationSourceFile](metadataAnnotationSourceFile)






```mermaid
 classDiagram
    class AnnotationSourceFile
    click AnnotationSourceFile href "../AnnotationSourceFile"
      AnnotationSourceFile <|-- AnnotationOrientedPointFile
        click AnnotationOrientedPointFile href "../AnnotationOrientedPointFile"
      AnnotationSourceFile <|-- AnnotationPointFile
        click AnnotationPointFile href "../AnnotationPointFile"
      AnnotationSourceFile <|-- AnnotationSegmentationMaskFile
        click AnnotationSegmentationMaskFile href "../AnnotationSegmentationMaskFile"
      AnnotationSourceFile <|-- AnnotationSemanticSegmentationMaskFile
        click AnnotationSemanticSegmentationMaskFile href "../AnnotationSemanticSegmentationMaskFile"
      
      AnnotationSourceFile : file_format
        
      AnnotationSourceFile : glob_string
        
      AnnotationSourceFile : is_visualization_default
        
      
```





## Inheritance
* **AnnotationSourceFile**
    * [AnnotationOrientedPointFile](AnnotationOrientedPointFile.md)
    * [AnnotationPointFile](AnnotationPointFile.md)
    * [AnnotationSegmentationMaskFile](AnnotationSegmentationMaskFile.md)
    * [AnnotationSemanticSegmentationMaskFile](AnnotationSemanticSegmentationMaskFile.md)



## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [file_format](file_format.md) | 1 <br/> [String](String.md) | File format for this file | direct |
| [glob_string](glob_string.md) | 1 <br/> [String](String.md) | Glob string to match annotation files in the dataset | direct |
| [is_visualization_default](is_visualization_default.md) | 0..1 <br/> [Boolean](Boolean.md) | This annotation will be rendered in neuroglancer by default | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [Annotation](Annotation.md) | [files](files.md) | range | [AnnotationSourceFile](AnnotationSourceFile.md) |






## Identifier and Mapping Information







### Schema Source


* from schema: metadata





## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:AnnotationSourceFile |
| native | cdp-meta:AnnotationSourceFile |





## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: AnnotationSourceFile
description: File and sourcing data for an annotation. Represents an entry in annotation.sources.
from_schema: metadata
attributes:
  file_format:
    name: file_format
    description: File format for this file
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_format
    rank: 1000
    alias: file_format
    owner: AnnotationSourceFile
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
    description: Glob string to match annotation files in the dataset.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_glob_string
    rank: 1000
    alias: glob_string
    owner: AnnotationSourceFile
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
    description: This annotation will be rendered in neuroglancer by default.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_is_visualization_default
    rank: 1000
    alias: is_visualization_default
    owner: AnnotationSourceFile
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
name: AnnotationSourceFile
description: File and sourcing data for an annotation. Represents an entry in annotation.sources.
from_schema: metadata
attributes:
  file_format:
    name: file_format
    description: File format for this file
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_format
    rank: 1000
    alias: file_format
    owner: AnnotationSourceFile
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
    description: Glob string to match annotation files in the dataset.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_glob_string
    rank: 1000
    alias: glob_string
    owner: AnnotationSourceFile
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
    description: This annotation will be rendered in neuroglancer by default.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_is_visualization_default
    rank: 1000
    alias: is_visualization_default
    owner: AnnotationSourceFile
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