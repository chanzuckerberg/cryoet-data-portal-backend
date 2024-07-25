

# Class: AuthorMixin


_An entity with author data_





URI: [cdp-meta:AuthorMixin](metadataAuthorMixin)






```mermaid
 classDiagram
    class AuthorMixin
    click AuthorMixin href "../AuthorMixin"
      AuthorMixin <|-- Author
        click Author href "../Author"
      
      AuthorMixin : affiliation_address
        
      AuthorMixin : affiliation_identifier
        
      AuthorMixin : affiliation_name
        
      AuthorMixin : corresponding_author_status
        
      AuthorMixin : email
        
      AuthorMixin : name
        
      AuthorMixin : primary_author_status
        
      
```




<!-- no inheritance hierarchy -->


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [name](name.md) | 1 <br/> [String](String.md) | The full name of the author | direct |
| [email](email.md) | 0..1 <br/> [String](String.md) | The email address of the author | direct |
| [affiliation_name](affiliation_name.md) | 0..1 <br/> [String](String.md) | The name of the author's affiliation | direct |
| [affiliation_address](affiliation_address.md) | 0..1 <br/> [String](String.md) | The address of the author's affiliation | direct |
| [affiliation_identifier](affiliation_identifier.md) | 0..1 _recommended_ <br/> [String](String.md) | A Research Organization Registry (ROR) identifier | direct |
| [corresponding_author_status](corresponding_author_status.md) | 0..1 <br/> [Boolean](Boolean.md) | Whether the author is a corresponding author | direct |
| [primary_author_status](primary_author_status.md) | 0..1 <br/> [Boolean](Boolean.md) | Whether the author is a primary author | direct |



## Mixin Usage

| mixed into | description |
| --- | --- |
| [Author](Author.md) | Author of a scientific data entity |








## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:AuthorMixin |
| native | cdp-meta:AuthorMixin |







## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: AuthorMixin
description: An entity with author data
from_schema: metadata
mixin: true
attributes:
  name:
    name: name
    description: The full name of the author.
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_name
    alias: name
    owner: AuthorMixin
    domain_of:
    - AuthorMixin
    - AnnotationMethodLinks
    - OrganismDetails
    - TissueDetails
    - CellType
    - CellStrain
    - CellComponent
    - AnnotationObject
    - Author
    range: string
    required: true
    inlined: true
    inlined_as_list: true
  email:
    name: email
    description: The email address of the author.
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_email
    alias: email
    owner: AuthorMixin
    domain_of:
    - AuthorMixin
    - Author
    range: string
    inlined: true
    inlined_as_list: true
  affiliation_name:
    name: affiliation_name
    description: The name of the author's affiliation.
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_affiliation_name
    alias: affiliation_name
    owner: AuthorMixin
    domain_of:
    - AuthorMixin
    - Author
    range: string
    inlined: true
    inlined_as_list: true
  affiliation_address:
    name: affiliation_address
    description: The address of the author's affiliation.
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_affiliation_address
    alias: affiliation_address
    owner: AuthorMixin
    domain_of:
    - AuthorMixin
    - Author
    range: string
    inlined: true
    inlined_as_list: true
  affiliation_identifier:
    name: affiliation_identifier
    description: A Research Organization Registry (ROR) identifier.
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_affiliation_identifier
    alias: affiliation_identifier
    owner: AuthorMixin
    domain_of:
    - AuthorMixin
    - Author
    range: string
    recommended: true
    inlined: true
    inlined_as_list: true
  corresponding_author_status:
    name: corresponding_author_status
    description: Whether the author is a corresponding author.
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_corresponding_author_status
    ifabsent: 'False'
    alias: corresponding_author_status
    owner: AuthorMixin
    domain_of:
    - AuthorMixin
    - Author
    range: boolean
    inlined: true
    inlined_as_list: true
  primary_author_status:
    name: primary_author_status
    description: Whether the author is a primary author.
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_primary_author_status
    ifabsent: 'False'
    alias: primary_author_status
    owner: AuthorMixin
    domain_of:
    - AuthorMixin
    - Author
    range: boolean
    inlined: true
    inlined_as_list: true

```
</details>

### Induced

<details>
```yaml
name: AuthorMixin
description: An entity with author data
from_schema: metadata
mixin: true
attributes:
  name:
    name: name
    description: The full name of the author.
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_name
    alias: name
    owner: AuthorMixin
    domain_of:
    - AuthorMixin
    - AnnotationMethodLinks
    - OrganismDetails
    - TissueDetails
    - CellType
    - CellStrain
    - CellComponent
    - AnnotationObject
    - Author
    range: string
    required: true
    inlined: true
    inlined_as_list: true
  email:
    name: email
    description: The email address of the author.
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_email
    alias: email
    owner: AuthorMixin
    domain_of:
    - AuthorMixin
    - Author
    range: string
    inlined: true
    inlined_as_list: true
  affiliation_name:
    name: affiliation_name
    description: The name of the author's affiliation.
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_affiliation_name
    alias: affiliation_name
    owner: AuthorMixin
    domain_of:
    - AuthorMixin
    - Author
    range: string
    inlined: true
    inlined_as_list: true
  affiliation_address:
    name: affiliation_address
    description: The address of the author's affiliation.
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_affiliation_address
    alias: affiliation_address
    owner: AuthorMixin
    domain_of:
    - AuthorMixin
    - Author
    range: string
    inlined: true
    inlined_as_list: true
  affiliation_identifier:
    name: affiliation_identifier
    description: A Research Organization Registry (ROR) identifier.
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_affiliation_identifier
    alias: affiliation_identifier
    owner: AuthorMixin
    domain_of:
    - AuthorMixin
    - Author
    range: string
    recommended: true
    inlined: true
    inlined_as_list: true
  corresponding_author_status:
    name: corresponding_author_status
    description: Whether the author is a corresponding author.
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_corresponding_author_status
    ifabsent: 'False'
    alias: corresponding_author_status
    owner: AuthorMixin
    domain_of:
    - AuthorMixin
    - Author
    range: boolean
    inlined: true
    inlined_as_list: true
  primary_author_status:
    name: primary_author_status
    description: Whether the author is a primary author.
    from_schema: metadata
    exact_mappings:
    - cdp-common:author_primary_author_status
    ifabsent: 'False'
    alias: primary_author_status
    owner: AuthorMixin
    domain_of:
    - AuthorMixin
    - Author
    range: boolean
    inlined: true
    inlined_as_list: true

```
</details>