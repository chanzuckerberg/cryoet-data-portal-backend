

# Slot: min


_Minimal tilt angle in degrees_



URI: [cdp-meta:min](metadatamin)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [TiltRange](TiltRange.md) | The range of tilt angles in the tilt series |  no  |







## Properties

* Range: [Float](Float.md)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:min |
| native | cdp-meta:min |
| exact | cdp-common:tiltseries_tilt_min |




## LinkML Source

<details>
```yaml
name: min
description: Minimal tilt angle in degrees
from_schema: metadata
exact_mappings:
- cdp-common:tiltseries_tilt_min
rank: 1000
alias: min
owner: TiltRange
domain_of:
- TiltRange
range: float
required: true
inlined: true
inlined_as_list: true
unit:
  symbol: °
  descriptive_name: degrees

```
</details>
