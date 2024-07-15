

# Slot: authors

URI: [cdp-meta:authors](metadataauthors)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Dataset](Dataset.md) | High-level description of a cryoET dataset |  no  |
| [Tomogram](Tomogram.md) | Metadata describing a tomogram |  no  |
| [AuthoredEntity](AuthoredEntity.md) | An entity with associated authors |  no  |
| [Annotation](Annotation.md) | Metadata describing an annotation |  no  |







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
- Tomogram
- Annotation
range: string

```
</details>
