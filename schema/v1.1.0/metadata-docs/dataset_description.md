

# Slot: dataset_description


_A short description of a CryoET dataset, similar to an abstract for a journal article or dataset._



URI: [cdp-meta:dataset_description](metadatadataset_description)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Dataset](Dataset.md) | High-level description of a cryoET dataset |  no  |







## Properties

* Range: [String](String.md)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:dataset_description |
| native | cdp-meta:dataset_description |
| exact | cdp-common:dataset_description |




## LinkML Source

<details>
```yaml
name: dataset_description
description: A short description of a CryoET dataset, similar to an abstract for a
  journal article or dataset.
from_schema: metadata
exact_mappings:
- cdp-common:dataset_description
rank: 1000
alias: dataset_description
owner: Dataset
domain_of:
- Dataset
range: string
required: true
inlined: true
inlined_as_list: true

```
</details>