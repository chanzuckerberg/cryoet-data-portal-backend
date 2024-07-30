

# Slot: is_aligned


_Whether this tilt series is aligned_



URI: [cdp-meta:is_aligned](metadatais_aligned)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [Boolean](Boolean.md)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:is_aligned |
| native | cdp-meta:is_aligned |
| exact | cdp-common:tiltseries_is_aligned |




## LinkML Source

<details>
```yaml
name: is_aligned
description: Whether this tilt series is aligned
from_schema: metadata
exact_mappings:
- cdp-common:tiltseries_is_aligned
rank: 1000
alias: is_aligned
owner: TiltSeries
domain_of:
- TiltSeries
range: boolean
required: true
inlined: true
inlined_as_list: true

```
</details>
