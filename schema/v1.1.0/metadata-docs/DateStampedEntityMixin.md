

# Class: DateStampedEntityMixin


_A set of dates at which a data item was deposited, published and last modified._





URI: [cdp-meta:DateStampedEntityMixin](metadataDateStampedEntityMixin)






```mermaid
 classDiagram
    class DateStampedEntityMixin
    click DateStampedEntityMixin href "../DateStampedEntityMixin"
      DateStampedEntityMixin <|-- DateStamp
        click DateStamp href "../DateStamp"
      
      DateStampedEntityMixin : deposition_date
        
      DateStampedEntityMixin : last_modified_date
        
      DateStampedEntityMixin : release_date
        
      
```




<!-- no inheritance hierarchy -->


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [deposition_date](deposition_date.md) | 1 <br/> [Date](Date.md) | The date a data item was received by the cryoET data portal | direct |
| [release_date](release_date.md) | 1 <br/> [Date](Date.md) | The date a data item was received by the cryoET data portal | direct |
| [last_modified_date](last_modified_date.md) | 1 <br/> [Date](Date.md) | The date a piece of data was last modified on the cryoET data portal | direct |



## Mixin Usage

| mixed into | description |
| --- | --- |
| [DateStamp](DateStamp.md) | A set of dates at which a data item was deposited, published and last modifie... |








## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:DateStampedEntityMixin |
| native | cdp-meta:DateStampedEntityMixin |







## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: DateStampedEntityMixin
description: A set of dates at which a data item was deposited, published and last
  modified.
from_schema: metadata
mixin: true
attributes:
  deposition_date:
    name: deposition_date
    description: The date a data item was received by the cryoET data portal.
    from_schema: metadata
    exact_mappings:
    - cdp-common:deposition_date
    alias: deposition_date
    owner: DateStampedEntityMixin
    domain_of:
    - DateStampedEntityMixin
    - DateStamp
    range: date
    required: true
    inlined: true
    inlined_as_list: true
  release_date:
    name: release_date
    description: The date a data item was received by the cryoET data portal.
    from_schema: metadata
    exact_mappings:
    - cdp-common:release_date
    alias: release_date
    owner: DateStampedEntityMixin
    domain_of:
    - DateStampedEntityMixin
    - DateStamp
    range: date
    required: true
    inlined: true
    inlined_as_list: true
  last_modified_date:
    name: last_modified_date
    description: The date a piece of data was last modified on the cryoET data portal.
    from_schema: metadata
    exact_mappings:
    - cdp-common:last_modified_date
    alias: last_modified_date
    owner: DateStampedEntityMixin
    domain_of:
    - DateStampedEntityMixin
    - DateStamp
    range: date
    required: true
    inlined: true
    inlined_as_list: true

```
</details>

### Induced

<details>
```yaml
name: DateStampedEntityMixin
description: A set of dates at which a data item was deposited, published and last
  modified.
from_schema: metadata
mixin: true
attributes:
  deposition_date:
    name: deposition_date
    description: The date a data item was received by the cryoET data portal.
    from_schema: metadata
    exact_mappings:
    - cdp-common:deposition_date
    alias: deposition_date
    owner: DateStampedEntityMixin
    domain_of:
    - DateStampedEntityMixin
    - DateStamp
    range: date
    required: true
    inlined: true
    inlined_as_list: true
  release_date:
    name: release_date
    description: The date a data item was received by the cryoET data portal.
    from_schema: metadata
    exact_mappings:
    - cdp-common:release_date
    alias: release_date
    owner: DateStampedEntityMixin
    domain_of:
    - DateStampedEntityMixin
    - DateStamp
    range: date
    required: true
    inlined: true
    inlined_as_list: true
  last_modified_date:
    name: last_modified_date
    description: The date a piece of data was last modified on the cryoET data portal.
    from_schema: metadata
    exact_mappings:
    - cdp-common:last_modified_date
    alias: last_modified_date
    owner: DateStampedEntityMixin
    domain_of:
    - DateStampedEntityMixin
    - DateStamp
    range: date
    required: true
    inlined: true
    inlined_as_list: true

```
</details>