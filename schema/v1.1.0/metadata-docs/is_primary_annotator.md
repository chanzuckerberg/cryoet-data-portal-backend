# Slot: is_primary_annotator


_Whether the author is a primary author._



URI: [cdp-meta:is_primary_annotator](https://cryoetdataportal.czscience.com/schema/metadata/is_primary_annotator)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[Annotator](Annotator.md) | Annotator of a scientific data entity |  no  |







## Properties

* Range: [xsd:boolean](http://www.w3.org/2001/XMLSchema#boolean)





## Identifier and Mapping Information







### Schema Source


* from schema: https://cryoetdataportal.czscience.com/schema-docs/metadata




## LinkML Source

<details>
```yaml
name: is_primary_annotator
description: Whether the author is a primary author.
from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
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

```
</details>