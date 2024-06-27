

# Class: Annotator


_Annotator of a scientific data entity._





URI: [cdp-meta:Annotator](metadataAnnotator)






```mermaid
 classDiagram
    class Annotator
    click Annotator href "../Annotator"
      Annotator : affiliation_address
        
          
    
    
    Annotator --> "0..1" String : affiliation_address
    click String href "../String"

        
      Annotator : affiliation_identifier
        
          
    
    
    Annotator --> "0..1 _recommended_" String : affiliation_identifier
    click String href "../String"

        
      Annotator : affiliation_name
        
          
    
    
    Annotator --> "0..1" String : affiliation_name
    click String href "../String"

        
      Annotator : email
        
          
    
    
    Annotator --> "0..1" String : email
    click String href "../String"

        
      Annotator : is_corresponding
        
          
    
    
    Annotator --> "0..1" String : is_corresponding
    click String href "../String"

        
      Annotator : is_primary_annotator
        
          
    
    
    Annotator --> "0..1" Boolean : is_primary_annotator
    click Boolean href "../Boolean"

        
      Annotator : name
        
          
    
    
    Annotator --> "0..1" String : name
    click String href "../String"

        
      Annotator : ORCID
        
          
    
    
    Annotator --> "0..1 _recommended_" String : ORCID
    click String href "../String"

        
      
```




<!-- no inheritance hierarchy -->


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [name](name.md) | 0..1 <br/> [xsd:string](http://www.w3.org/2001/XMLSchema#string) |  | direct |
| [email](email.md) | 0..1 <br/> [xsd:string](http://www.w3.org/2001/XMLSchema#string) |  | direct |
| [affiliation_name](affiliation_name.md) | 0..1 <br/> [xsd:string](http://www.w3.org/2001/XMLSchema#string) |  | direct |
| [affiliation_address](affiliation_address.md) | 0..1 <br/> [xsd:string](http://www.w3.org/2001/XMLSchema#string) |  | direct |
| [affiliation_identifier](affiliation_identifier.md) | 0..1 _recommended_ <br/> [xsd:string](http://www.w3.org/2001/XMLSchema#string) |  | direct |
| [is_corresponding](is_corresponding.md) | 0..1 <br/> [xsd:string](http://www.w3.org/2001/XMLSchema#string) |  | direct |
| [is_primary_annotator](is_primary_annotator.md) | 0..1 <br/> [xsd:boolean](http://www.w3.org/2001/XMLSchema#boolean) | Whether the author is a primary author | direct |
| [ORCID](ORCID.md) | 0..1 _recommended_ <br/> [xsd:string](http://www.w3.org/2001/XMLSchema#string) |  | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [AnnotatoredEntity](AnnotatoredEntity.md) | [authors](authors.md) | range | [Annotator](Annotator.md) |
| [Annotation](Annotation.md) | [authors](authors.md) | range | [Annotator](Annotator.md) |






## Identifier and Mapping Information







### Schema Source


* from schema: metadata





## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:Annotator |
| native | cdp-meta:Annotator |





## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Annotator
description: Annotator of a scientific data entity.
from_schema: metadata
attributes:
  name:
    name: name
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_name
    alias: name
    owner: Annotator
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
  email:
    name: email
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_email
    alias: email
    owner: Annotator
    domain_of:
    - Author
    - Annotator
    range: string
    inlined: true
    inlined_as_list: true
  affiliation_name:
    name: affiliation_name
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_affiliation_name
    alias: affiliation_name
    owner: Annotator
    domain_of:
    - Author
    - Annotator
    range: string
    inlined: true
    inlined_as_list: true
  affiliation_address:
    name: affiliation_address
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_affiliation_address
    alias: affiliation_address
    owner: Annotator
    domain_of:
    - Author
    - Annotator
    range: string
    inlined: true
    inlined_as_list: true
  affiliation_identifier:
    name: affiliation_identifier
    from_schema: metadata
    exact_mappings:
    - cdp-common:affiliation_identifier
    alias: affiliation_identifier
    owner: Annotator
    domain_of:
    - Author
    - Annotator
    range: string
    recommended: true
    inlined: true
    inlined_as_list: true
  is_corresponding:
    name: is_corresponding
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_corresponding_author_status
    alias: is_corresponding
    owner: Annotator
    domain_of:
    - Author
    - Annotator
    range: string
    inlined: true
    inlined_as_list: true
  is_primary_annotator:
    name: is_primary_annotator
    description: Whether the author is a primary author.
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_primary_author_status
    rank: 1000
    alias: is_primary_annotator
    owner: Annotator
    domain_of:
    - Annotator
    range: boolean
    inlined: true
    inlined_as_list: true
  ORCID:
    name: ORCID
    from_schema: metadata
    exact_mappings:
    - cdp-common:orcid
    alias: ORCID
    owner: Annotator
    domain_of:
    - Author
    - Annotator
    range: string
    recommended: true
    inlined: true
    inlined_as_list: true

```
</details>

### Induced

<details>
```yaml
name: Annotator
description: Annotator of a scientific data entity.
from_schema: metadata
attributes:
  name:
    name: name
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_name
    alias: name
    owner: Annotator
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
  email:
    name: email
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_email
    alias: email
    owner: Annotator
    domain_of:
    - Author
    - Annotator
    range: string
    inlined: true
    inlined_as_list: true
  affiliation_name:
    name: affiliation_name
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_affiliation_name
    alias: affiliation_name
    owner: Annotator
    domain_of:
    - Author
    - Annotator
    range: string
    inlined: true
    inlined_as_list: true
  affiliation_address:
    name: affiliation_address
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_affiliation_address
    alias: affiliation_address
    owner: Annotator
    domain_of:
    - Author
    - Annotator
    range: string
    inlined: true
    inlined_as_list: true
  affiliation_identifier:
    name: affiliation_identifier
    from_schema: metadata
    exact_mappings:
    - cdp-common:affiliation_identifier
    alias: affiliation_identifier
    owner: Annotator
    domain_of:
    - Author
    - Annotator
    range: string
    recommended: true
    inlined: true
    inlined_as_list: true
  is_corresponding:
    name: is_corresponding
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_corresponding_author_status
    alias: is_corresponding
    owner: Annotator
    domain_of:
    - Author
    - Annotator
    range: string
    inlined: true
    inlined_as_list: true
  is_primary_annotator:
    name: is_primary_annotator
    description: Whether the author is a primary author.
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_primary_author_status
    rank: 1000
    alias: is_primary_annotator
    owner: Annotator
    domain_of:
    - Annotator
    range: boolean
    inlined: true
    inlined_as_list: true
  ORCID:
    name: ORCID
    from_schema: metadata
    exact_mappings:
    - cdp-common:orcid
    alias: ORCID
    owner: Annotator
    domain_of:
    - Author
    - Annotator
    range: string
    recommended: true
    inlined: true
    inlined_as_list: true

```
</details>