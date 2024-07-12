# Slot: fiducial_alignment_status


_Whether the tomographic alignment was computed based on fiducial markers._



URI: [cdp-meta:fiducial_alignment_status](metadatafiducial_alignment_status)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[Tomogram](Tomogram.md) | Metadata describing a tomogram |  no  |







## Properties

* Range: [FiducialAlignmentStatusEnum](FiducialAlignmentStatusEnum.md)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## LinkML Source

<details>
```yaml
name: fiducial_alignment_status
description: Whether the tomographic alignment was computed based on fiducial markers.
from_schema: metadata
exact_mappings:
- cdp-common:tomogram_fiducial_alignment_status
rank: 1000
alias: fiducial_alignment_status
owner: Tomogram
domain_of:
- Tomogram
range: fiducial_alignment_status_enum
required: true
inlined: true
inlined_as_list: true

```
</details>
