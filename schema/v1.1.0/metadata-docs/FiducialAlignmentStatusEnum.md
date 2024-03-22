# Enum: FiducialAlignmentStatusEnum




_Fiducial Alignment method_



URI: [FiducialAlignmentStatusEnum](FiducialAlignmentStatusEnum.md)

## Permissible Values

| Value | Meaning | Description |
| --- | --- | --- |
| FIDUCIAL | None | Alignment computed based on fiducial markers |
| NON_FIDUCIAL | None | Alignment computed without fiducial markers |




## Slots

| Name | Description |
| ---  | --- |
| [fiducial_alignment_status](fiducial_alignment_status.md) | Whether the tomographic alignment was computed based on fiducial markers |






## Identifier and Mapping Information







### Schema Source


* from schema: metadata




## LinkML Source

<details>
```yaml
name: fiducial_alignment_status_enum
description: Fiducial Alignment method
from_schema: metadata
rank: 1000
permissible_values:
  FIDUCIAL:
    text: FIDUCIAL
    description: Alignment computed based on fiducial markers
  NON_FIDUCIAL:
    text: NON_FIDUCIAL
    description: Alignment computed without fiducial markers

```
</details>
