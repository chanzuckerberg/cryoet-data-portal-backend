

# Slot: binning_from_frames


_Describes the binning factor from frames to tilt series file_



URI: [cdp-meta:binning_from_frames](metadatabinning_from_frames)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [Float](Float.md)

* Minimum Value: 0





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:binning_from_frames |
| native | cdp-meta:binning_from_frames |
| exact | cdp-common:tiltseries_binning_from_frames |




## LinkML Source

<details>
```yaml
name: binning_from_frames
description: Describes the binning factor from frames to tilt series file
from_schema: metadata
exact_mappings:
- cdp-common:tiltseries_binning_from_frames
rank: 1000
ifabsent: float(1)
alias: binning_from_frames
owner: TiltSeries
domain_of:
- TiltSeries
range: float
inlined: true
inlined_as_list: true
minimum_value: 1.0e-09

```
</details>
