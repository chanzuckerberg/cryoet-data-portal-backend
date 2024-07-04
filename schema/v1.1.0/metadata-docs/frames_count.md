

# Slot: frames_count


_Number of frames associated with this tiltseries_



URI: [cdp-meta:frames_count](metadataframes_count)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [Integer](Integer.md)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:frames_count |
| native | cdp-meta:frames_count |
| exact | cdp-common:tiltseries_frames_count |




## LinkML Source

<details>
```yaml
name: frames_count
description: Number of frames associated with this tiltseries
from_schema: metadata
exact_mappings:
- cdp-common:tiltseries_frames_count
rank: 1000
alias: frames_count
owner: TiltSeries
domain_of:
- TiltSeries
range: integer
inlined: true
inlined_as_list: true

```
</details>