

# Class: Organism


_The species from which the sample was derived._





URI: [cdp-meta:Organism](metadataOrganism)






```mermaid
 classDiagram
    class Organism
    click Organism href "../Organism"
      Organism : name
        
      Organism : taxonomy_id
        
      
```




<!-- no inheritance hierarchy -->


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [name](name.md) | 0..1 <br/> [String](String.md) |  | direct |
| [taxonomy_id](taxonomy_id.md) | 0..1 _recommended_ <br/> [Integer](Integer.md) | NCBI taxonomy identifier for the organism, e | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [ExperimentalMetadata](ExperimentalMetadata.md) | [organism](organism.md) | range | [Organism](Organism.md) |
| [Dataset](Dataset.md) | [organism](organism.md) | range | [Organism](Organism.md) |






## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:Organism |
| native | cdp-meta:Organism |







## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Organism
description: The species from which the sample was derived.
from_schema: metadata
attributes:
  name:
    name: name
    from_schema: metadata
    exact_mappings:
    - cdp-common:organism_name
    alias: name
    owner: Organism
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
  taxonomy_id:
    name: taxonomy_id
    description: NCBI taxonomy identifier for the organism, e.g. 9606
    from_schema: metadata
    exact_mappings:
    - cdp-common:organism_taxid
    rank: 1000
    alias: taxonomy_id
    owner: Organism
    domain_of:
    - Organism
    range: integer
    recommended: true
    inlined: true
    inlined_as_list: true
    minimum_value: 1

```
</details>

### Induced

<details>
```yaml
name: Organism
description: The species from which the sample was derived.
from_schema: metadata
attributes:
  name:
    name: name
    from_schema: metadata
    exact_mappings:
    - cdp-common:organism_name
    alias: name
    owner: Organism
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
  taxonomy_id:
    name: taxonomy_id
    description: NCBI taxonomy identifier for the organism, e.g. 9606
    from_schema: metadata
    exact_mappings:
    - cdp-common:organism_taxid
    rank: 1000
    alias: taxonomy_id
    owner: Organism
    domain_of:
    - Organism
    range: integer
    recommended: true
    inlined: true
    inlined_as_list: true
    minimum_value: 1

```
</details>