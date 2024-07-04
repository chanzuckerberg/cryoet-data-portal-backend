

# Slot: tilt_step


_Tilt step in degrees_



URI: [cdp-meta:tilt_step](metadatatilt_step)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [Float](Float.md)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:tilt_step |
| native | cdp-meta:tilt_step |
| exact | cdp-common:tiltseries_tilt_step |




## LinkML Source

<details>
```yaml
name: tilt_step
description: Tilt step in degrees
from_schema: metadata
exact_mappings:
- cdp-common:tiltseries_tilt_step
rank: 1000
alias: tilt_step
owner: TiltSeries
domain_of:
- TiltSeries
range: float
required: true
inlined: true
inlined_as_list: true
unit:
  symbol: °
  descriptive_name: degrees

```
</details>