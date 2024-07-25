

# Slot: affine_transformation_matrix


_A placeholder for any type of data._



URI: [cdp-meta:affine_transformation_matrix](metadataaffine_transformation_matrix)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Tomogram](Tomogram.md) | Metadata describing a tomogram |  no  |







## Properties

* Range: [Any](Any.md)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:affine_transformation_matrix |
| native | cdp-meta:affine_transformation_matrix |




## LinkML Source

<details>
```yaml
name: affine_transformation_matrix
description: A placeholder for any type of data.
from_schema: metadata
rank: 1000
array:
  exact_number_dimensions: 2
  dimensions:
  - exact_cardinality: 4
  - exact_cardinality: 4
alias: affine_transformation_matrix
owner: Tomogram
domain_of:
- Tomogram
range: Any
inlined: true
inlined_as_list: true

```
</details>