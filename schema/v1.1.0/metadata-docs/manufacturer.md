

# Slot: manufacturer

URI: [cdp-meta:manufacturer](metadatamanufacturer)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MicroscopeDetails](MicroscopeDetails.md) | The microscope used to collect the tilt series |  no  |
| [CameraDetails](CameraDetails.md) | The camera used to collect the tilt series |  no  |







## Properties

* Range: [String](String.md)





## Identifier and Mapping Information








## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:manufacturer |
| native | cdp-meta:manufacturer |




## LinkML Source

<details>
```yaml
name: manufacturer
alias: manufacturer
domain_of:
- CameraDetails
- MicroscopeDetails
range: string

```
</details>