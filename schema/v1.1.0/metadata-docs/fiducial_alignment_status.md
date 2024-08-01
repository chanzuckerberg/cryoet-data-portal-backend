

# Slot: fiducial_alignment_status


_Whether the tomographic alignment was computed based on fiducial markers._



URI: [cdp-meta:fiducial_alignment_status](metadatafiducial_alignment_status)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Tomogram](Tomogram.md) | Metadata describing a tomogram |  no  |







## Properties

* Range: [String](String.md)&nbsp;or&nbsp;<br />[FiducialAlignmentStatusEnum](FiducialAlignmentStatusEnum.md)&nbsp;or&nbsp;<br />[StringFormattedString](StringFormattedString.md)

* Regex pattern: `(^FIDUCIAL$)|(^NON_FIDUCIAL$)|(^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$)`





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:fiducial_alignment_status |
| native | cdp-meta:fiducial_alignment_status |




## LinkML Source

<details>
```yaml
name: fiducial_alignment_status
description: Whether the tomographic alignment was computed based on fiducial markers.
from_schema: metadata
rank: 1000
alias: fiducial_alignment_status
owner: Tomogram
domain_of:
- Tomogram
range: string
inlined: true
inlined_as_list: true
pattern: (^FIDUCIAL$)|(^NON_FIDUCIAL$)|(^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$)
any_of:
- range: fiducial_alignment_status_enum
- range: StringFormattedString

```
</details>