

# Slot: affine_transformation_matrix


_The flip or rotation transformation of this author submitted tomogram is indicated here_



URI: [cdp-meta:affine_transformation_matrix](metadataaffine_transformation_matrix)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Tomogram](Tomogram.md) | Metadata describing a tomogram |  no  |







## Properties

* Range: [Float](Float.md)





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
description: The flip or rotation transformation of this author submitted tomogram
  is indicated here
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
range: float
inlined: true
inlined_as_list: true

```
</details>
