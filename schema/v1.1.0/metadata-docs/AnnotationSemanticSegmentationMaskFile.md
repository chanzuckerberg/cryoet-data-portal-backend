

# Class: AnnotationSemanticSegmentationMaskFile


_File and sourcing data for a semantic segmentation mask annotation._





URI: [cdp-meta:AnnotationSemanticSegmentationMaskFile](metadataAnnotationSemanticSegmentationMaskFile)






```mermaid
 classDiagram
    class AnnotationSemanticSegmentationMaskFile
    click AnnotationSemanticSegmentationMaskFile href "../AnnotationSemanticSegmentationMaskFile"
      AnnotationFile <|-- AnnotationSemanticSegmentationMaskFile
        click AnnotationFile href "../AnnotationFile"
      
      AnnotationSemanticSegmentationMaskFile : file_format
        
          
    
    
    AnnotationSemanticSegmentationMaskFile --> "1" String : file_format
    click String href "../String"

        
      AnnotationSemanticSegmentationMaskFile : glob_string
        
          
    
    
    AnnotationSemanticSegmentationMaskFile --> "1" String : glob_string
    click String href "../String"

        
      AnnotationSemanticSegmentationMaskFile : is_visualization_default
        
          
    
    
    AnnotationSemanticSegmentationMaskFile --> "0..1" Boolean : is_visualization_default
    click Boolean href "../Boolean"

        
      AnnotationSemanticSegmentationMaskFile : mask_label
        
          
    
    
    AnnotationSemanticSegmentationMaskFile --> "0..1" Integer : mask_label
    click Integer href "../Integer"

        
      
```





## Inheritance
* [AnnotationFile](AnnotationFile.md)
    * **AnnotationSemanticSegmentationMaskFile**



## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [mask_label](mask_label.md) | 0..1 <br/> [xsd:integer](http://www.w3.org/2001/XMLSchema#integer) | The mask label for a semantic segmentation mask annotation file | direct |
| [file_format](file_format.md) | 1 <br/> [xsd:string](http://www.w3.org/2001/XMLSchema#string) |  | direct |
| [glob_string](glob_string.md) | 1 <br/> [xsd:string](http://www.w3.org/2001/XMLSchema#string) |  | direct |
| [is_visualization_default](is_visualization_default.md) | 0..1 <br/> [xsd:boolean](http://www.w3.org/2001/XMLSchema#boolean) |  | direct |







## Aliases


* SemanticSegmentationMask



## Identifier and Mapping Information







### Schema Source


* from schema: metadata





## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:AnnotationSemanticSegmentationMaskFile |
| native | cdp-meta:AnnotationSemanticSegmentationMaskFile |





## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: AnnotationSemanticSegmentationMaskFile
description: File and sourcing data for a semantic segmentation mask annotation.
from_schema: metadata
aliases:
- SemanticSegmentationMask
is_a: AnnotationFile
attributes:
  mask_label:
    name: mask_label
    description: The mask label for a semantic segmentation mask annotation file.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_file_semantic_segmentation_mask_label
    rank: 1000
    alias: mask_label
    owner: AnnotationSemanticSegmentationMaskFile
    domain_of:
    - AnnotationSemanticSegmentationMaskFile
    range: integer
    inlined: true
    inlined_as_list: true
  file_format:
    name: file_format
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_file_format
    alias: file_format
    owner: AnnotationSemanticSegmentationMaskFile
    domain_of:
    - AnnotationFile
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
    - cdp-common:annotation_file_glob_string
    alias: glob_string
    owner: AnnotationSemanticSegmentationMaskFile
    domain_of:
    - AnnotationFile
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
    - cdp-common:annotation_file_is_visualization_default
    alias: is_visualization_default
    owner: AnnotationSemanticSegmentationMaskFile
    domain_of:
    - AnnotationFile
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
name: AnnotationSemanticSegmentationMaskFile
description: File and sourcing data for a semantic segmentation mask annotation.
from_schema: metadata
aliases:
- SemanticSegmentationMask
is_a: AnnotationFile
attributes:
  mask_label:
    name: mask_label
    description: The mask label for a semantic segmentation mask annotation file.
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_file_semantic_segmentation_mask_label
    rank: 1000
    alias: mask_label
    owner: AnnotationSemanticSegmentationMaskFile
    domain_of:
    - AnnotationSemanticSegmentationMaskFile
    range: integer
    inlined: true
    inlined_as_list: true
  file_format:
    name: file_format
    from_schema: metadata
    exact_mappings:
    - cdp-common:annotation_file_format
    alias: file_format
    owner: AnnotationSemanticSegmentationMaskFile
    domain_of:
    - AnnotationFile
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
    - cdp-common:annotation_file_glob_string
    alias: glob_string
    owner: AnnotationSemanticSegmentationMaskFile
    domain_of:
    - AnnotationFile
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
    - cdp-common:annotation_file_is_visualization_default
    alias: is_visualization_default
    owner: AnnotationSemanticSegmentationMaskFile
    domain_of:
    - AnnotationFile
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