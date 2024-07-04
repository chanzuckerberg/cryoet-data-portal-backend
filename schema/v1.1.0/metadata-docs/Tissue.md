

# Class: Tissue


_The type of tissue from which the sample was derived._





URI: [cdp-meta:Tissue](metadataTissue)






```mermaid
 classDiagram
    class Tissue
    click Tissue href "../Tissue"
      Tissue : id
        
      Tissue : name
        
      
```




<!-- no inheritance hierarchy -->


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [name](name.md) | 0..1 <br/> [String](String.md) |  | direct |
| [id](id.md) | 0..1 _recommended_ <br/> [String](String.md) | The UBERON identifier for the tissue | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [ExperimentalMetadata](ExperimentalMetadata.md) | [tissue](tissue.md) | range | [Tissue](Tissue.md) |
| [Dataset](Dataset.md) | [tissue](tissue.md) | range | [Tissue](Tissue.md) |






## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:Tissue |
| native | cdp-meta:Tissue |







## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Tissue
description: The type of tissue from which the sample was derived.
from_schema: metadata
attributes:
  name:
    name: name
    from_schema: metadata
    exact_mappings:
    - cdp-common:tissue_name
    alias: name
    owner: Tissue
    domain_of:
    - Author
    - Organism
    - Tissue
    - CellType
    - CellStrain
    - CellComponent
    - AnnotationObject
    range: string
    inlined: true
    inlined_as_list: true
  id:
    name: id
    description: The UBERON identifier for the tissue.
    from_schema: metadata
    exact_mappings:
    - cdp-common:tissue_id
    rank: 1000
    alias: id
    owner: Tissue
    domain_of:
    - Tissue
    - CellType
    - CellStrain
    - CellComponent
    - AnnotationObject
    range: string
    recommended: true
    inlined: true
    inlined_as_list: true

```
</details>

### Induced

<details>
```yaml
name: Tissue
description: The type of tissue from which the sample was derived.
from_schema: metadata
attributes:
  name:
    name: name
    from_schema: metadata
    exact_mappings:
    - cdp-common:tissue_name
    alias: name
    owner: Tissue
    domain_of:
    - Author
    - Organism
    - Tissue
    - CellType
    - CellStrain
    - CellComponent
    - AnnotationObject
    range: string
    inlined: true
    inlined_as_list: true
  id:
    name: id
    description: The UBERON identifier for the tissue.
    from_schema: metadata
    exact_mappings:
    - cdp-common:tissue_id
    rank: 1000
    alias: id
    owner: Tissue
    domain_of:
    - Tissue
    - CellType
    - CellStrain
    - CellComponent
    - AnnotationObject
    range: string
    recommended: true
    inlined: true
    inlined_as_list: true

```
</details>