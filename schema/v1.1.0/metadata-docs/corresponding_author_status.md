

# Slot: corresponding_author_status


_Whether the author is a corresponding author._



URI: [cdp-meta:corresponding_author_status](metadatacorresponding_author_status)



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




## LinkML Source

<details>
```yaml
name: corresponding_author_status
description: Whether the author is a corresponding author.
from_schema: metadata
exact_mappings:
- cdp-common:author_corresponding_author_status
rank: 1000
ifabsent: 'False'
alias: corresponding_author_status
owner: Author
domain_of:
- Author
range: boolean
inlined: true
inlined_as_list: true

```
</details>