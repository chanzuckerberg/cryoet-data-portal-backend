# Slot: related_database_entries


_Comma-separated list of related database entries for the dataset._



URI: [cdp-meta:related_database_entries](metadatarelated_database_entries)



<!-- no inheritance hierarchy -->




## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
[CrossReferences](CrossReferences.md) | A set of cross-references to other databases and publications |  no  |







## Properties

* Range: [EMPIAREMDBPDBLIST](EMPIAREMDBPDBLIST.md)

* Recommended: True

* Regex pattern: `(^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8}))*$)|(^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8}))*$)`





## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## LinkML Source

<details>
```yaml
name: related_database_entries
description: Comma-separated list of related database entries for the dataset.
from_schema: metadata
rank: 1000
alias: related_database_entries
owner: CrossReferences
domain_of:
- CrossReferences
range: EMPIAR_EMDB_PDB_LIST
recommended: true
inlined: true
inlined_as_list: true
pattern: (^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8}))*$)|(^(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8})(\s*,\s*(EMPIAR-[0-9]{5}|EMD-[0-9]{4,5}|pdb[0-9a-zA-Z]{4,8}))*$)

```
</details>