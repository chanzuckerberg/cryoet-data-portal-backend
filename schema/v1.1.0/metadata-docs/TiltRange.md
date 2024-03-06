# Class: TiltRange


_The range of tilt angles in the tilt series._





URI: [cdp-meta:TiltRange](https://cryoetdataportal.czscience.com/schema/metadata/TiltRange)




```mermaid
 classDiagram
    class TiltRange
      TiltRange : max
        
          TiltRange --> float : max
        
      TiltRange : min
        
          TiltRange --> float : min
        
      
```




<!-- no inheritance hierarchy -->


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [min](min.md) | 0..1 <br/> [xsd:float](http://www.w3.org/2001/XMLSchema#float) | Minimal tilt angle in degrees | direct |
| [max](max.md) | 0..1 <br/> [xsd:float](http://www.w3.org/2001/XMLSchema#float) | Maximal tilt angle in degrees | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [TiltSeries](TiltSeries.md) | [tilt_range](tilt_range.md) | range | [TiltRange](TiltRange.md) |






## Identifier and Mapping Information







### Schema Source


* from schema: https://cryoetdataportal.czscience.com/schema-docs/metadata





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
from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
attributes:
  min:
    name: min
    description: Minimal tilt angle in degrees
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:tiltseries_tilt_min
    rank: 1000
    alias: min
    owner: TiltRange
    domain_of:
    - TiltRange
    range: float
    inlined: true
    inlined_as_list: true
  max:
    name: max
    description: Maximal tilt angle in degrees
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:tiltseries_tilt_max
    rank: 1000
    alias: max
    owner: TiltRange
    domain_of:
    - TiltRange
    range: float
    inlined: true
    inlined_as_list: true

```
</details>

### Induced

<details>
```yaml
name: TiltRange
description: The range of tilt angles in the tilt series.
from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
attributes:
  min:
    name: min
    description: Minimal tilt angle in degrees
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:tiltseries_tilt_min
    rank: 1000
    alias: min
    owner: TiltRange
    domain_of:
    - TiltRange
    range: float
    inlined: true
    inlined_as_list: true
  max:
    name: max
    description: Maximal tilt angle in degrees
    from_schema: https://cryoetdataportal.czscience.com/schema-docs/metadata
    exact_mappings:
    - cdp-common:tiltseries_tilt_max
    rank: 1000
    alias: max
    owner: TiltRange
    domain_of:
    - TiltRange
    range: float
    inlined: true
    inlined_as_list: true

```
</details>