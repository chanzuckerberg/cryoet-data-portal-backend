

# Slot: camera


_The camera used to collect the tilt series._



URI: [cdp-meta:camera](metadatacamera)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [CameraDetails](CameraDetails.md)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:camera |
| native | cdp-meta:camera |




## LinkML Source

<details>
```yaml
name: camera
description: The camera used to collect the tilt series.
from_schema: metadata
rank: 1000
alias: camera
owner: TiltSeries
domain_of:
- TiltSeries
range: CameraDetails
required: true
inlined: true
inlined_as_list: true

```
</details>