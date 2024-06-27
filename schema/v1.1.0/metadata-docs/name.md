

# Slot: name

URI: [cdp-meta:name](metadataname)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Author](Author.md) | Author of a scientific data entity |  no  |
| [CellStrain](CellStrain.md) | The strain or cell line from which the sample was derived |  no  |
| [CellType](CellType.md) | The cell type from which the sample was derived |  no  |
| [Annotator](Annotator.md) | Annotator of a scientific data entity |  no  |
| [Tissue](Tissue.md) | The type of tissue from which the sample was derived |  no  |
| [Organism](Organism.md) | The species from which the sample was derived |  no  |
| [AnnotationObject](AnnotationObject.md) | Metadata describing the object being annotated |  no  |
| [CellComponent](CellComponent.md) | The cellular component from which the sample was derived |  no  |







## Properties

* Range: [xsd:string](http://www.w3.org/2001/XMLSchema#string)





## Identifier and Mapping Information








## LinkML Source

<details>
```yaml
name: name
alias: name
domain_of:
- Author
- Annotator
- Organism
- Tissue
- CellType
- CellStrain
- CellComponent
- AnnotationObject
range: string

```
</details>