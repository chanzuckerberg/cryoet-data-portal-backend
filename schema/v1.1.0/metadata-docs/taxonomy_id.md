# Slot: taxonomy_id


_NCBI taxonomy identifier for the organism, e.g. 9606_



URI: [cdp-meta:taxonomy_id](metadatataxonomy_id)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[Organism](Organism.md) | The species from which the sample was derived |  no  |







## Properties

* Range: [xsd:string](http://www.w3.org/2001/XMLSchema#string)





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## LinkML Source

<details>
```yaml
name: taxonomy_id
description: NCBI taxonomy identifier for the organism, e.g. 9606
from_schema: metadata
exact_mappings:
- cdp-common:organism_taxid
rank: 1000
alias: taxonomy_id
owner: Organism
domain_of:
- Organism
range: string
inlined: true
inlined_as_list: true

```
</details>