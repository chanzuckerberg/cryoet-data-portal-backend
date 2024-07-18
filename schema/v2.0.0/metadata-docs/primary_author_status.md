

# Slot: primary_author_status


_Whether the author is a primary author._



URI: [cdp-meta:primary_author_status](metadataprimary_author_status)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Author](Author.md) | Author of a scientific data entity |  no  |







## Properties

* Range: [Boolean](Boolean.md)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:primary_author_status |
| native | cdp-meta:primary_author_status |
| exact | cdp-common:author_primary_author_status |




## LinkML Source

<details>
```yaml
name: primary_author_status
description: Whether the author is a primary author.
from_schema: metadata
exact_mappings:
- cdp-common:author_primary_author_status
rank: 1000
ifabsent: 'False'
alias: primary_author_status
owner: Author
domain_of:
- Author
range: boolean
inlined: true
inlined_as_list: true

```
</details>
