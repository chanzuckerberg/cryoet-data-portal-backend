

# Slot: authors

URI: [cdp-meta:authors](metadataauthors)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Tomogram](Tomogram.md) | Metadata describing a tomogram |  no  |
| [Dataset](Dataset.md) | High-level description of a cryoET dataset |  no  |
| [Annotation](Annotation.md) | Metadata describing an annotation |  no  |
| [AuthoredEntity](AuthoredEntity.md) | An entity with associated authors |  no  |
| [Deposition](Deposition.md) | Metadata describing a deposition |  no  |







## Properties

* Range: [String](String.md)





## Identifier and Mapping Information








## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | cdp-meta:authors |
| native | cdp-meta:authors |




## LinkML Source

<details>
```yaml
name: authors
alias: authors
domain_of:
- AuthoredEntity
- Dataset
- Deposition
- Tomogram
- Annotation
range: string

```
</details>
