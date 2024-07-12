# Class: MicroscopeDetails


_The microscope used to collect the tilt series._





URI: [cdp-meta:MicroscopeDetails](metadataMicroscopeDetails)




```mermaid
 classDiagram
    class MicroscopeDetails
      MicroscopeDetails : manufacturer

      MicroscopeDetails : model


```




<!-- no inheritance hierarchy -->


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [manufacturer](manufacturer.md) | 1..1 <br/> [String](String.md) | Name of the microscope manufacturer | direct |
| [model](model.md) | 1..1 <br/> [String](String.md) | Microscope model name | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [TiltSeries](TiltSeries.md) | [microscope](microscope.md) | range | [MicroscopeDetails](MicroscopeDetails.md) |






## Identifier and Mapping Information







### Schema Source


* from schema: metadata





## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:MicroscopeDetails |
| native | cdp-meta:MicroscopeDetails |





## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: MicroscopeDetails
description: The microscope used to collect the tilt series.
from_schema: metadata
attributes:
  manufacturer:
    name: manufacturer
    description: Name of the microscope manufacturer
    from_schema: metadata
    exact_mappings:
    - cdp-common:tiltseries_microscope_manufacturer
    alias: manufacturer
    owner: MicroscopeDetails
    domain_of:
    - CameraDetails
    - MicroscopeDetails
    range: string
    required: true
    inlined: true
    inlined_as_list: true
  model:
    name: model
    description: Microscope model name
    from_schema: metadata
    exact_mappings:
    - cdp-common:tiltseries_microscope_model
    alias: model
    owner: MicroscopeDetails
    domain_of:
    - CameraDetails
    - MicroscopeDetails
    range: string
    required: true
    inlined: true
    inlined_as_list: true

```
</details>

### Induced

<details>
```yaml
name: MicroscopeDetails
description: The microscope used to collect the tilt series.
from_schema: metadata
attributes:
  manufacturer:
    name: manufacturer
    description: Name of the microscope manufacturer
    from_schema: metadata
    exact_mappings:
    - cdp-common:tiltseries_microscope_manufacturer
    alias: manufacturer
    owner: MicroscopeDetails
    domain_of:
    - CameraDetails
    - MicroscopeDetails
    range: string
    required: true
    inlined: true
    inlined_as_list: true
  model:
    name: model
    description: Microscope model name
    from_schema: metadata
    exact_mappings:
    - cdp-common:tiltseries_microscope_model
    alias: model
    owner: MicroscopeDetails
    domain_of:
    - CameraDetails
    - MicroscopeDetails
    range: string
    required: true
    inlined: true
    inlined_as_list: true

```
</details>
