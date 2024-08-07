

# Slot: tilt_step


_Tilt step in degrees_



URI: [cdp-meta:tilt_step](metadatatilt_step)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [TiltSeries](TiltSeries.md) | Metadata describing a tilt series |  no  |







## Properties

* Range: [Any](Any.md)&nbsp;or&nbsp;<br />[Float](Float.md)&nbsp;or&nbsp;<br />[FloatFormattedString](FloatFormattedString.md)

* Minimum Value: 0

* Maximum Value: 90

* Regex pattern: `^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$`





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:tilt_step |
| native | cdp-meta:tilt_step |




## LinkML Source

<details>
```yaml
name: tilt_step
description: Tilt step in degrees
from_schema: metadata
rank: 1000
alias: tilt_step
owner: TiltSeries
domain_of:
- TiltSeries
range: Any
inlined: true
inlined_as_list: true
minimum_value: 0
maximum_value: 90
pattern: ^float[ ]*\{[a-zA-Z0-9_-]+\}[ ]*$
unit:
  symbol: °
  descriptive_name: degrees
any_of:
- range: float
  minimum_value: 0
  maximum_value: 90
- range: FloatFormattedString

```
</details>
