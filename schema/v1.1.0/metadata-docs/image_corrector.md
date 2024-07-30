

# Slot: image_corrector


_Image corrector setup_



URI: [cdp-meta:image_corrector](metadataimage_corrector)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MicroscopeOpticalSetup](MicroscopeOpticalSetup.md) | The optical setup of the microscope used to collect the tilt series |  no  |







## Properties

* Range: [String](String.md)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:image_corrector |
| native | cdp-meta:image_corrector |
| exact | cdp-common:tiltseries_microscope_image_corrector |




## LinkML Source

<details>
```yaml
name: image_corrector
description: Image corrector setup
from_schema: metadata
exact_mappings:
- cdp-common:tiltseries_microscope_image_corrector
rank: 1000
alias: image_corrector
owner: MicroscopeOpticalSetup
domain_of:
- MicroscopeOpticalSetup
range: string
inlined: true
inlined_as_list: true

```
</details>
