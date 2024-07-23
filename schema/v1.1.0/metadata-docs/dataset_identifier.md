# Slot: dataset_identifier


_An identifier for a CryoET dataset, assigned by the Data Portal. Used to identify the dataset as the directory name in data tree._



URI: [cdp-meta:dataset_identifier](metadatadataset_identifier)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[Dataset](Dataset.md) | High-level description of a cryoET dataset |  no  |







## Properties

* Range: [Integer](Integer.md)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## LinkML Source

<details>
```yaml
name: dataset_identifier
description: An identifier for a CryoET dataset, assigned by the Data Portal. Used
  to identify the dataset as the directory name in data tree.
from_schema: metadata
exact_mappings:
- cdp-common:dataset_identifier
rank: 1000
alias: dataset_identifier
owner: Dataset
domain_of:
- Dataset
range: integer
required: true
inlined: true
inlined_as_list: true

```
</details>