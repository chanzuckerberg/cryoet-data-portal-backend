

# Slot: acquire_mode


_Camera acquisition mode_



URI: [cdp-meta:acquire_mode](metadataacquire_mode)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Camera](Camera.md) | The camera used to collect the tilt series |  no  |







## Properties

* Range: [String](String.md)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:acquire_mode |
| native | cdp-meta:acquire_mode |
| exact | cdp-common:tiltseries_camera_acquire_mode |




## LinkML Source

<details>
```yaml
name: acquire_mode
description: Camera acquisition mode
from_schema: metadata
exact_mappings:
- cdp-common:tiltseries_camera_acquire_mode
rank: 1000
alias: acquire_mode
owner: Camera
domain_of:
- Camera
range: string
inlined: true
inlined_as_list: true

```
</details>