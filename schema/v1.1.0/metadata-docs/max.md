

# Slot: max


_Maximal tilt angle in degrees_



URI: [cdp-meta:max](metadatamax)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [TiltRange](TiltRange.md) | The range of tilt angles in the tilt series |  no  |







## Properties

* Range: [Float](Float.md)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## LinkML Source

<details>
```yaml
name: max
description: Maximal tilt angle in degrees
from_schema: metadata
exact_mappings:
- cdp-common:tiltseries_tilt_max
rank: 1000
alias: max
owner: TiltRange
domain_of:
- TiltRange
range: float
inlined: true
inlined_as_list: true

```
</details>