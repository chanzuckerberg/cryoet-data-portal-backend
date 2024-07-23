# Slot: deposition_description


_A short description of the deposition, similar to an abstract for a journal article or dataset._



URI: [cdp-meta:deposition_description](metadatadeposition_description)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[Deposition](Deposition.md) | Metadata describing a deposition |  no  |







## Properties

* Range: [String](String.md)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## LinkML Source

<details>
```yaml
name: deposition_description
description: A short description of the deposition, similar to an abstract for a journal
  article or dataset.
from_schema: metadata
exact_mappings:
- cdp-common:deposition_description
rank: 1000
alias: deposition_description
owner: Deposition
domain_of:
- Deposition
range: string
required: true
inlined: true
inlined_as_list: true

```
</details>