# Slot: deposition_types


_Type of data in the deposition (e.g. dataset, annotation, tomogram)_



URI: [cdp-meta:deposition_types](metadatadeposition_types)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[Deposition](Deposition.md) | Metadata describing a deposition |  no  |







## Properties

* Range: [DepositionTypesEnum](DepositionTypesEnum.md)

* Multivalued: True

* Required: True

* Regex pattern: `(^annotation$)|(^dataset$)|(^tomogram$)`





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## LinkML Source

<details>
```yaml
name: deposition_types
description: Type of data in the deposition (e.g. dataset, annotation, tomogram)
from_schema: metadata
exact_mappings:
- cdp-common:deposition_types
rank: 1000
multivalued: true
alias: deposition_types
owner: Deposition
domain_of:
- Deposition
range: deposition_types_enum
required: true
inlined: true
inlined_as_list: true
pattern: (^annotation$)|(^dataset$)|(^tomogram$)

```
</details>