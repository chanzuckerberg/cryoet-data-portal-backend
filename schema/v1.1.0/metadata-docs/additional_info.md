

# Slot: additional_info


_Other microscope optical setup information, in addition to energy filter, phase plate and image corrector_



URI: [cdp-meta:additional_info](metadataadditional_info)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Microscope](Microscope.md) | The microscope used to collect the tilt series |  no  |







## Properties

* Range: [String](String.md)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:additional_info |
| native | cdp-meta:additional_info |
| exact | cdp-common:tiltseries_microscope_additional_info |




## LinkML Source

<details>
```yaml
name: additional_info
description: Other microscope optical setup information, in addition to energy filter,
  phase plate and image corrector
from_schema: metadata
exact_mappings:
- cdp-common:tiltseries_microscope_additional_info
rank: 1000
alias: additional_info
owner: Microscope
domain_of:
- Microscope
range: string
inlined: true
inlined_as_list: true

```
</details>
