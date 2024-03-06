# Slot: dataset_identifier


_An identifier for a CryoET dataset, assigned by the Data Portal. Used to identify the dataset as the directory  name in data tree._



URI: [cdp-meta:dataset_identifier](https://cryoetdataportal.czscience.com/schema/metadata/dataset_identifier)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[Dataset](Dataset.md) | High-level description of a cryoET dataset |  no  |







## Properties

* Range: [xsd:integer](http://www.w3.org/2001/XMLSchema#integer)





## Identifier and Mapping Information







### Schema Source


* from schema: https://cryoetdataportal.czscience.com/schema-docs/metadata




## LinkML Source

<details>
```yaml
name: dataset_identifier
description: An identifier for a CryoET dataset, assigned by the Data Portal. Used
  to identify the dataset as the directory  name in data tree.
from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
exact_mappings:
- cdp-common:dataset_identifier
rank: 1000
alias: dataset_identifier
owner: Dataset
domain_of:
- Dataset
range: integer
inlined: true
inlined_as_list: true

```
</details>