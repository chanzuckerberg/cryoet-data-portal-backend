# Slot: deposition_identifier


_An identifier for a CryoET deposition, assigned by the Data Portal. Used to identify the deposition the entity is a part of._



URI: [cdp-meta:deposition_identifier](metadatadeposition_identifier)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[Deposition](Deposition.md) | Metadata describing a deposition |  no  |







## Properties

* Range: [Integer](Integer.md)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## LinkML Source

<details>
```yaml
name: deposition_identifier
description: An identifier for a CryoET deposition, assigned by the Data Portal. Used
  to identify the deposition the entity is a part of.
from_schema: metadata
exact_mappings:
- cdp-common:deposition_identifier
rank: 1000
alias: deposition_identifier
owner: Deposition
domain_of:
- Deposition
range: integer
required: true
inlined: true
inlined_as_list: true

```
</details>