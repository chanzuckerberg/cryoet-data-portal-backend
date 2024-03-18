# Slot: is_primary_author


_Whether the author is a primary author._



URI: [cdp-meta:is_primary_author](metadatais_primary_author)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[Author](Author.md) | Author of a scientific data entity |  no  |







## Properties

* Range: [xsd:boolean](http://www.w3.org/2001/XMLSchema#boolean)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## LinkML Source

<details>
```yaml
name: is_primary_author
description: Whether the author is a primary author.
from_schema: metadata
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

```
</details>