

# Class: TiltRange


_The range of tilt angles in the tilt series._





URI: [cdp-meta:TiltRange](metadataTiltRange)






```mermaid
 classDiagram
    class TiltRange
    click TiltRange href "../TiltRange"
      TiltRange : max

      TiltRange : min


```




<!-- no inheritance hierarchy -->


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [min](min.md) | 1 <br/> [Float](Float.md) | Minimal tilt angle in degrees | direct |
| [max](max.md) | 1 <br/> [Float](Float.md) | Maximal tilt angle in degrees | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [TiltSeries](TiltSeries.md) | [tilt_range](tilt_range.md) | range | [TiltRange](TiltRange.md) |






## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:TiltRange |
| native | cdp-meta:TiltRange |







## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: TiltRange
description: The range of tilt angles in the tilt series.
from_schema: metadata
attributes:
  min:
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
    range: float
    required: true
    inlined: true
    inlined_as_list: true
    minimum_value: -90
    unit:
      symbol: °
      descriptive_name: degrees
  max:
    name: max
    description: Maximal tilt angle in degrees
    from_schema: metadata
    exact_mappings:
    - cdp-common:tiltseries_tilt_max
    rank: 1000
    alias: max
    owner: TiltRange
    domain_of:
    - TiltRange
    range: float
    required: true
    inlined: true
    inlined_as_list: true
    minimum_value: -90
    maximum_value: 90
    unit:
      symbol: °
      descriptive_name: degrees

```
</details>

### Induced

<details>
```yaml
name: TiltRange
description: The range of tilt angles in the tilt series.
from_schema: metadata
attributes:
  min:
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
    range: float
    required: true
    inlined: true
    inlined_as_list: true
    minimum_value: -90
    unit:
      symbol: °
      descriptive_name: degrees
  max:
    name: max
    description: Maximal tilt angle in degrees
    from_schema: metadata
    exact_mappings:
    - cdp-common:tiltseries_tilt_max
    rank: 1000
    alias: max
    owner: TiltRange
    domain_of:
    - TiltRange
    range: float
    required: true
    inlined: true
    inlined_as_list: true
    minimum_value: -90
    maximum_value: 90
    unit:
      symbol: °
      descriptive_name: degrees

```
</details>
