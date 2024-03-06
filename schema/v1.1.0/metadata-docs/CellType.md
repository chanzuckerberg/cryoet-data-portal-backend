# Class: CellType


_The cell type from which the sample was derived._





URI: [cdp-meta:CellType](https://cryoetdataportal.czscience.com/schema/metadata/CellType)




```mermaid
 classDiagram
    class CellType
      CellType : id
        
          CellType --> string : id
        
      CellType : name
        
          CellType --> string : name
        
      
```




<!-- no inheritance hierarchy -->


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [name](name.md) | 0..1 <br/> [xsd:string](http://www.w3.org/2001/XMLSchema#string) |  | direct |
| [id](id.md) | 0..1 <br/> [xsd:string](http://www.w3.org/2001/XMLSchema#string) |  | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [ExperimentalMetadata](ExperimentalMetadata.md) | [cell_type](cell_type.md) | range | [CellType](CellType.md) |
| [Dataset](Dataset.md) | [cell_type](cell_type.md) | range | [CellType](CellType.md) |






## Identifier and Mapping Information







### Schema Source


* from schema: https://cryoetdataportal.czscience.com/schema-docs/metadata





## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:CellType |
| native | cdp-meta:CellType |





## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: CellType
description: The cell type from which the sample was derived.
from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
attributes:
  name:
    name: name
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:cell_name
    alias: name
    owner: CellType
    domain_of:
    - Author
    - Annotator
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
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:cell_type_id
    alias: id
    owner: CellType
    domain_of:
    - Tissue
    - CellType
    - CellStrain
    - CellComponent
    - AnnotationObject
    range: string
    inlined: true
    inlined_as_list: true

```
</details>

### Induced

<details>
```yaml
name: CellType
description: The cell type from which the sample was derived.
from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
attributes:
  name:
    name: name
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:cell_name
    alias: name
    owner: CellType
    domain_of:
    - Author
    - Annotator
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
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:cell_type_id
    alias: id
    owner: CellType
    domain_of:
    - Tissue
    - CellType
    - CellStrain
    - CellComponent
    - AnnotationObject
    range: string
    inlined: true
    inlined_as_list: true

```
</details>