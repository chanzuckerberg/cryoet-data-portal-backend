

# Slot: binning_from_frames


_Describes the binning factor from frames to tilt series file_



URI: [cdp-meta:binning_from_frames](metadatabinning_from_frames)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [String](String.md)&nbsp;or&nbsp;<br />[Float](Float.md)&nbsp;or&nbsp;<br />[FloatFormattedString](FloatFormattedString.md)

* Minimum Value: 0

* Regex pattern: `^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$`





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:binning_from_frames |
| native | cdp-meta:binning_from_frames |




## LinkML Source

<details>
```yaml
name: binning_from_frames
description: Describes the binning factor from frames to tilt series file
from_schema: metadata
rank: 1000
ifabsent: float(1)
alias: binning_from_frames
owner: TiltSeries
domain_of:
- TiltSeries
range: string
inlined: true
inlined_as_list: true
minimum_value: 0
pattern: ^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$
any_of:
- range: float
  minimum_value: 0
- range: FloatFormattedString

```
</details>