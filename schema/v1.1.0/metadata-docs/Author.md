# Class: Author


_Author of a scientific data entity._





URI: [cdp-meta:Author](https://cryoetdataportal.czscience.com/schema/metadata/Author)




```mermaid
 classDiagram
    class Author
      Author : affiliation_address
        
          Author --> string : affiliation_address
        
      Author : affiliation_identifier
        
          Author --> string : affiliation_identifier
        
      Author : affiliation_name
        
          Author --> string : affiliation_name
        
      Author : email
        
          Author --> string : email
        
      Author : is_corresponding
        
          Author --> boolean : is_corresponding
        
      Author : is_primary_author
        
          Author --> boolean : is_primary_author
        
      Author : name
        
          Author --> string : name
        
      Author : ORCID
        
          Author --> string : ORCID
        
      
```




<!-- no inheritance hierarchy -->


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [name](name.md) | 0..1 <br/> [xsd:string](http://www.w3.org/2001/XMLSchema#string) | The full name of the author | direct |
| [email](email.md) | 0..1 <br/> [xsd:string](http://www.w3.org/2001/XMLSchema#string) | The email address of the author | direct |
| [affiliation_name](affiliation_name.md) | 0..1 <br/> [xsd:string](http://www.w3.org/2001/XMLSchema#string) | The name of the author's affiliation | direct |
| [affiliation_address](affiliation_address.md) | 0..1 <br/> [xsd:string](http://www.w3.org/2001/XMLSchema#string) | The address of the author's affiliation | direct |
| [affiliation_identifier](affiliation_identifier.md) | 0..1 _recommended_ <br/> [xsd:string](http://www.w3.org/2001/XMLSchema#string) | A Research Organization Registry (ROR) identifier | direct |
| [is_corresponding](is_corresponding.md) | 0..1 <br/> [xsd:boolean](http://www.w3.org/2001/XMLSchema#boolean) | Whether the author is a corresponding author | direct |
| [is_primary_author](is_primary_author.md) | 0..1 <br/> [xsd:boolean](http://www.w3.org/2001/XMLSchema#boolean) | Whether the author is a primary author | direct |
| [ORCID](ORCID.md) | 0..1 _recommended_ <br/> [xsd:string](http://www.w3.org/2001/XMLSchema#string) | A unique, persistent identifier for researchers, provided by ORCID | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [AuthoredEntity](AuthoredEntity.md) | [authors](authors.md) | range | [Author](Author.md) |
| [Dataset](Dataset.md) | [authors](authors.md) | range | [Author](Author.md) |
| [Tomogram](Tomogram.md) | [authors](authors.md) | range | [Author](Author.md) |






## Identifier and Mapping Information







### Schema Source


* from schema: https://cryoetdataportal.czscience.com/schema-docs/metadata





## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:Author |
| native | cdp-meta:Author |





## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Author
description: Author of a scientific data entity.
from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
attributes:
  name:
    name: name
    description: The full name of the author.
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:author_name
    rank: 1000
    alias: name
    owner: Author
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
    description: The email address of the author.
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:author_email
    rank: 1000
    alias: email
    owner: Author
    domain_of:
    - Author
    - Annotator
    range: string
    inlined: true
    inlined_as_list: true
  affiliation_name:
    name: affiliation_name
    description: The name of the author's affiliation.
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:author_affiliation_name
    rank: 1000
    alias: affiliation_name
    owner: Author
    domain_of:
    - Author
    - Annotator
    range: string
    inlined: true
    inlined_as_list: true
  affiliation_address:
    name: affiliation_address
    description: The address of the author's affiliation.
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:author_affiliation_address
    rank: 1000
    alias: affiliation_address
    owner: Author
    domain_of:
    - Author
    - Annotator
    range: string
    inlined: true
    inlined_as_list: true
  affiliation_identifier:
    name: affiliation_identifier
    description: A Research Organization Registry (ROR) identifier.
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:affiliation_identifier
    rank: 1000
    alias: affiliation_identifier
    owner: Author
    domain_of:
    - Author
    - Annotator
    range: string
    recommended: true
    inlined: true
    inlined_as_list: true
    pattern: ^0[a-hj-km-np-tv-z|0-9]{6}[0-9]{2}$
  is_corresponding:
    name: is_corresponding
    description: Whether the author is a corresponding author.
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:author_corresponding_author_status
    rank: 1000
    alias: is_corresponding
    owner: Author
    domain_of:
    - Author
    - Annotator
    range: boolean
    inlined: true
    inlined_as_list: true
  is_primary_author:
    name: is_primary_author
    description: Whether the author is a primary author.
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:author_primary_author_status
    rank: 1000
    alias: is_primary_author
    owner: Author
    domain_of:
    - Author
    range: boolean
    inlined: true
    inlined_as_list: true
  ORCID:
    name: ORCID
    description: A unique, persistent identifier for researchers, provided by ORCID.
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:orcid
    rank: 1000
    alias: ORCID
    owner: Author
    domain_of:
    - Author
    - Annotator
    range: string
    recommended: true
    inlined: true
    inlined_as_list: true
    pattern: '[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$'

```
</details>

### Induced

<details>
```yaml
name: Author
description: Author of a scientific data entity.
from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
attributes:
  name:
    name: name
    description: The full name of the author.
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:author_name
    rank: 1000
    alias: name
    owner: Author
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
    description: The email address of the author.
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:author_email
    rank: 1000
    alias: email
    owner: Author
    domain_of:
    - Author
    - Annotator
    range: string
    inlined: true
    inlined_as_list: true
  affiliation_name:
    name: affiliation_name
    description: The name of the author's affiliation.
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:author_affiliation_name
    rank: 1000
    alias: affiliation_name
    owner: Author
    domain_of:
    - Author
    - Annotator
    range: string
    inlined: true
    inlined_as_list: true
  affiliation_address:
    name: affiliation_address
    description: The address of the author's affiliation.
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:author_affiliation_address
    rank: 1000
    alias: affiliation_address
    owner: Author
    domain_of:
    - Author
    - Annotator
    range: string
    inlined: true
    inlined_as_list: true
  affiliation_identifier:
    name: affiliation_identifier
    description: A Research Organization Registry (ROR) identifier.
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:affiliation_identifier
    rank: 1000
    alias: affiliation_identifier
    owner: Author
    domain_of:
    - Author
    - Annotator
    range: string
    recommended: true
    inlined: true
    inlined_as_list: true
    pattern: ^0[a-hj-km-np-tv-z|0-9]{6}[0-9]{2}$
  is_corresponding:
    name: is_corresponding
    description: Whether the author is a corresponding author.
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:author_corresponding_author_status
    rank: 1000
    alias: is_corresponding
    owner: Author
    domain_of:
    - Author
    - Annotator
    range: boolean
    inlined: true
    inlined_as_list: true
  is_primary_author:
    name: is_primary_author
    description: Whether the author is a primary author.
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:author_primary_author_status
    rank: 1000
    alias: is_primary_author
    owner: Author
    domain_of:
    - Author
    range: boolean
    inlined: true
    inlined_as_list: true
  ORCID:
    name: ORCID
    description: A unique, persistent identifier for researchers, provided by ORCID.
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:orcid
    rank: 1000
    alias: ORCID
    owner: Author
    domain_of:
    - Author
    - Annotator
    range: string
    recommended: true
    inlined: true
    inlined_as_list: true
    pattern: '[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$'

```
</details>