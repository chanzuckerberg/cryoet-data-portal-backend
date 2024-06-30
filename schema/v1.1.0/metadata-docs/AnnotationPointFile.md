

# Class: AnnotationPointFile


_File and sourcing data for a point annotation._





URI: [cdp-meta:AnnotationPointFile](metadataAnnotationPointFile)






```mermaid
 classDiagram
    class AnnotationPointFile
    click AnnotationPointFile href "../AnnotationPointFile"
      AnnotationSourceFile <|-- AnnotationPointFile
        click AnnotationSourceFile href "../AnnotationSourceFile"
      
      AnnotationPointFile : binning
        
          
    
    
    AnnotationPointFile --> "0..1" Integer : binning
    click Integer href "../Integer"

        
      AnnotationPointFile : columns
        
          
    
    
    AnnotationPointFile --> "0..1" String : columns
    click String href "../String"

        
      AnnotationPointFile : delimiter
        
          
    
    
    AnnotationPointFile --> "0..1" String : delimiter
    click String href "../String"

        
      AnnotationPointFile : file_format
        
          
    
    
    AnnotationPointFile --> "1" String : file_format
    click String href "../String"

        
      AnnotationPointFile : glob_string
        
          
    
    
    AnnotationPointFile --> "1" String : glob_string
    click String href "../String"

        
      AnnotationPointFile : is_visualization_default
        
          
    
    
    AnnotationPointFile --> "0..1" Boolean : is_visualization_default
    click Boolean href "../Boolean"

        
      
```





## Inheritance
* [AnnotationSourceFile](AnnotationSourceFile.md)
    * **AnnotationPointFile**



## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [binning](binning.md) | 0..1 <br/> [xsd:integer](http://www.w3.org/2001/XMLSchema#integer) |  | direct |
| [columns](columns.md) | 0..1 <br/> [xsd:string](http://www.w3.org/2001/XMLSchema#string) | The columns used in a point annotation file | direct |
| [delimiter](delimiter.md) | 0..1 <br/> [xsd:string](http://www.w3.org/2001/XMLSchema#string) | The delimiter used in a oriented point annotation file | direct |
| [file_format](file_format.md) | 1 <br/> [xsd:string](http://www.w3.org/2001/XMLSchema#string) |  | direct |
| [glob_string](glob_string.md) | 1 <br/> [xsd:string](http://www.w3.org/2001/XMLSchema#string) |  | direct |
| [is_visualization_default](is_visualization_default.md) | 0..1 <br/> [xsd:boolean](http://www.w3.org/2001/XMLSchema#boolean) |  | direct |







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
description: File and sourcing data for a point annotation.
from_schema: metadata
aliases:
- Point
is_a: AnnotationSourceFile
attributes:
  binning:
    name: binning
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_point_binning
    alias: binning
    owner: AnnotationPointFile
    domain_of:
    - AnnotationOrientedPointFile
    - AnnotationPointFile
    - AnnotationInstanceSegmentationFile
    range: integer
    inlined: true
    inlined_as_list: true
  columns:
    name: columns
    description: The columns used in a point annotation file.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_point_columns
    rank: 1000
    alias: columns
    owner: AnnotationPointFile
    domain_of:
    - AnnotationPointFile
    range: string
    inlined: true
    inlined_as_list: true
  delimiter:
    name: delimiter
    description: The delimiter used in a oriented point annotation file.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_point_delimiter
    rank: 1000
    alias: delimiter
    owner: AnnotationPointFile
    domain_of:
    - AnnotationPointFile
    range: string
    inlined: true
    inlined_as_list: true
  file_format:
    name: file_format
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
    required: true
    inlined: true
    inlined_as_list: true
  is_visualization_default:
    name: is_visualization_default
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_is_visualization_default
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
description: File and sourcing data for a point annotation.
from_schema: metadata
aliases:
- Point
is_a: AnnotationSourceFile
attributes:
  binning:
    name: binning
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_point_binning
    alias: binning
    owner: AnnotationPointFile
    domain_of:
    - AnnotationOrientedPointFile
    - AnnotationPointFile
    - AnnotationInstanceSegmentationFile
    range: integer
    inlined: true
    inlined_as_list: true
  columns:
    name: columns
    description: The columns used in a point annotation file.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_point_columns
    rank: 1000
    alias: columns
    owner: AnnotationPointFile
    domain_of:
    - AnnotationPointFile
    range: string
    inlined: true
    inlined_as_list: true
  delimiter:
    name: delimiter
    description: The delimiter used in a oriented point annotation file.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_point_delimiter
    rank: 1000
    alias: delimiter
    owner: AnnotationPointFile
    domain_of:
    - AnnotationPointFile
    range: string
    inlined: true
    inlined_as_list: true
  file_format:
    name: file_format
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
    required: true
    inlined: true
    inlined_as_list: true
  is_visualization_default:
    name: is_visualization_default
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_source_file_is_visualization_default
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