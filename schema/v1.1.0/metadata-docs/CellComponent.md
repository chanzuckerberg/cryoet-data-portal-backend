

# Class: CellComponent


_The cellular component from which the sample was derived._





URI: [cdp-meta:CellComponent](metadataCellComponent)






```mermaid
 classDiagram
    class CellComponent
    click CellComponent href "../CellComponent"
      CellComponent : id

      CellComponent : name


```




<!-- no inheritance hierarchy -->


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [name](name.md) | 1 <br/> [String](String.md) | Name of the cellular component | direct |
| [id](id.md) | 0..1 _recommended_ <br/> [GOID](GOID.md) | The GO identifier for the cellular component | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [ExperimentalMetadata](ExperimentalMetadata.md) | [cell_component](cell_component.md) | range | [CellComponent](CellComponent.md) |
| [Dataset](Dataset.md) | [cell_component](cell_component.md) | range | [CellComponent](CellComponent.md) |






## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:CellComponent |
| native | cdp-meta:CellComponent |







## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: CellComponent
description: The cellular component from which the sample was derived.
from_schema: metadata
attributes:
  name:
    name: name
    description: Name of the cellular component.
    from_schema: metadata
    exact_mappings:
    - cdp-common:cell_component_name
    alias: name
    owner: CellComponent
    domain_of:
    - Author
    - Organism
    - Tissue
    - CellType
    - CellStrain
    - CellComponent
    - AnnotationObject
    range: string
    required: true
    inlined: true
    inlined_as_list: true
  id:
    name: id
    description: The GO identifier for the cellular component.
    from_schema: metadata
    exact_mappings:
    - cdp-common:cell_component_id
    alias: id
    owner: CellComponent
    domain_of:
    - Tissue
    - CellType
    - CellStrain
    - CellComponent
    - AnnotationObject
    range: GO_ID
    recommended: true
    inlined: true
    inlined_as_list: true
    pattern: (?i)^GO:[0-9]{7}$

```
</details>

### Induced

<details>
```yaml
name: CellComponent
description: The cellular component from which the sample was derived.
from_schema: metadata
attributes:
  name:
    name: name
    description: Name of the cellular component.
    from_schema: metadata
    exact_mappings:
    - cdp-common:cell_component_name
    alias: name
    owner: CellComponent
    domain_of:
    - Author
    - Organism
    - Tissue
    - CellType
    - CellStrain
    - CellComponent
    - AnnotationObject
    range: string
    required: true
    inlined: true
    inlined_as_list: true
  id:
    name: id
    description: The GO identifier for the cellular component.
    from_schema: metadata
    exact_mappings:
    - cdp-common:cell_component_id
    alias: id
    owner: CellComponent
    domain_of:
    - Tissue
    - CellType
    - CellStrain
    - CellComponent
    - AnnotationObject
    range: GO_ID
    recommended: true
    inlined: true
    inlined_as_list: true
    pattern: (?i)^GO:[0-9]{7}$

```
</details>
