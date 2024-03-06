# Class: DatestampedEntity


_An entity with associated deposition, release and last modified dates._




* __NOTE__: this is an abstract class and should not be instantiated directly


URI: [cdp-meta:DatestampedEntity](metadataDatestampedEntity)




```mermaid
 classDiagram
    class DatestampedEntity
      DatestampedEntity <|-- Dataset
      DatestampedEntity <|-- Annotation
      
      DatestampedEntity : dates
        
          DatestampedEntity --> DateStamp : dates
        
      
```




<!-- no inheritance hierarchy -->


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [dates](dates.md) | 1..1 <br/> [DateStamp](DateStamp.md) | A set of dates at which a data item was deposited, published and last modifie... | direct |









## Identifier and Mapping Information







### Schema Source


* from schema: metadata





## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:DatestampedEntity |
| native | cdp-meta:DatestampedEntity |





## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: DatestampedEntity
description: An entity with associated deposition, release and last modified dates.
from_schema: metadata
abstract: true
attributes:
  dates:
    name: dates
    description: A set of dates at which a data item was deposited, published and
      last modified.
    from_schema: metadata
    rank: 1000
    alias: dates
    owner: DatestampedEntity
    domain_of:
    - DatestampedEntity
    - Dataset
    - Annotation
    range: DateStamp
    required: true
    inlined: true
    inlined_as_list: true

```
</details>

### Induced

<details>
```yaml
name: DatestampedEntity
description: An entity with associated deposition, release and last modified dates.
from_schema: metadata
abstract: true
attributes:
  dates:
    name: dates
    description: A set of dates at which a data item was deposited, published and
      last modified.
    from_schema: metadata
    rank: 1000
    alias: dates
    owner: DatestampedEntity
    domain_of:
    - DatestampedEntity
    - Dataset
    - Annotation
    range: DateStamp
    required: true
    inlined: true
    inlined_as_list: true

```
</details>