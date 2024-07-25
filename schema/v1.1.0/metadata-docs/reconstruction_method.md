

# Slot: reconstruction_method


_Describe reconstruction method (WBP, SART, SIRT)_



URI: [cdp-meta:reconstruction_method](metadatareconstruction_method)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Tomogram](Tomogram.md) | Metadata describing a tomogram |  no  |







## Properties

* Range: [String](String.md)&nbsp;or&nbsp;<br />[TomogromReconstructionMethodEnum](TomogromReconstructionMethodEnum.md)&nbsp;or&nbsp;<br />[StringFormattedString](StringFormattedString.md)

* Regex pattern: `^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$`





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:reconstruction_method |
| native | cdp-meta:reconstruction_method |




## LinkML Source

<details>
```yaml
name: reconstruction_method
description: Describe reconstruction method (WBP, SART, SIRT)
from_schema: metadata
rank: 1000
alias: reconstruction_method
owner: Tomogram
domain_of:
- Tomogram
range: string
inlined: true
inlined_as_list: true
pattern: ^[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$
any_of:
- range: tomogrom_reconstruction_method_enum
- range: StringFormattedString

```
</details>