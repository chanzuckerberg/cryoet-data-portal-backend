

# Class: CrossReferencedEntity


_An entity with associated cross-references to other databases and publications._





URI: [cdp-meta:CrossReferencedEntity](metadataCrossReferencedEntity)






```mermaid
 classDiagram
    class CrossReferencedEntity
    click CrossReferencedEntity href "../CrossReferencedEntity"
      CrossReferencedEntity <|-- Dataset
        click Dataset href "../Dataset"
      CrossReferencedEntity <|-- Deposition
        click Deposition href "../Deposition"
      
      CrossReferencedEntity : cross_references
        
          
    
    
    CrossReferencedEntity --> "0..1" CrossReferences : cross_references
    click CrossReferences href "../CrossReferences"

        
      
```




<!-- no inheritance hierarchy -->


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [cross_references](cross_references.md) | 0..1 <br/> [CrossReferences](CrossReferences.md) | A set of cross-references to other databases and publications | direct |



## Mixin Usage

| mixed into | description |
| --- | --- |
| [Dataset](Dataset.md) | High-level description of a cryoET dataset |
| [Deposition](Deposition.md) | Metadata describing a deposition |








## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:CrossReferencedEntity |
| native | cdp-meta:CrossReferencedEntity |







## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: CrossReferencedEntity
description: An entity with associated cross-references to other databases and publications.
from_schema: metadata
mixin: true
attributes:
  cross_references:
    name: cross_references
    description: A set of cross-references to other databases and publications.
    from_schema: metadata
    rank: 1000
    alias: cross_references
    owner: CrossReferencedEntity
    domain_of:
    - CrossReferencedEntity
    - Dataset
    - Deposition
    range: CrossReferences
    inlined: true
    inlined_as_list: true

```
</details>

### Induced

<details>
```yaml
name: CrossReferencedEntity
description: An entity with associated cross-references to other databases and publications.
from_schema: metadata
mixin: true
attributes:
  cross_references:
    name: cross_references
    description: A set of cross-references to other databases and publications.
    from_schema: metadata
    rank: 1000
    alias: cross_references
    owner: CrossReferencedEntity
    domain_of:
    - CrossReferencedEntity
    - Dataset
    - Deposition
    range: CrossReferences
    inlined: true
    inlined_as_list: true

```
</details>