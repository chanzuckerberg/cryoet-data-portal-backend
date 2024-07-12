

# Slot: min


_Minimal tilt angle in degrees_



URI: [cdp-meta:min](metadatamin)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [TiltRange](TiltRange.md) | The range of tilt angles in the tilt series |  no  |







## Properties

* Range: [String](String.md)&nbsp;or&nbsp;<br />[Float](Float.md)&nbsp;or&nbsp;<br />[FloatFormattedString](FloatFormattedString.md)

* Required: True

* Minimum Value: -90

* Maximum Value: 90

* Regex pattern: `^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$`





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:min |
| native | cdp-meta:min |
| exact | cdp-common:tiltseries_tilt_min |




## LinkML Source

<details>
```yaml
name: min
description: Minimal tilt angle in degrees
from_schema: metadata
exact_mappings:
- cdp-common:tiltseries_tilt_min
rank: 1000
alias: min
owner: TiltRange
domain_of:
- TiltRange
range: string
required: true
inlined: true
inlined_as_list: true
minimum_value: -90
maximum_value: 90
pattern: ^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$
unit:
  symbol: °
  descriptive_name: degrees
any_of:
- range: float
  minimum_value: -90
  maximum_value: 90
- range: FloatFormattedString

```
</details>
