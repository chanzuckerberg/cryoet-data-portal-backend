

# Slot: id

URI: [cdp-meta:id](metadataid)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [CellComponent](CellComponent.md) | The cellular component from which the sample was derived |  no  |
| [Tissue](Tissue.md) | The type of tissue from which the sample was derived |  no  |
| [CellType](CellType.md) | The cell type from which the sample was derived |  no  |
| [AnnotationObject](AnnotationObject.md) | Metadata describing the object being annotated |  no  |
| [CellStrain](CellStrain.md) | The strain or cell line from which the sample was derived |  no  |







## Properties

* Range: [String](String.md)





## Identifier and Mapping Information








## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:id |
| native | cdp-meta:id |




## LinkML Source

<details>
```yaml
name: id
alias: id
domain_of:
- Tissue
- CellType
- CellStrain
- CellComponent
- AnnotationObject
range: string

```
</details>
