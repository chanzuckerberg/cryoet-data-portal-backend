# Technical Specification: Stale Annotation Cleanup

## Executive Summary

This specification addresses the problem of stale annotation entries in the database that accumulate due to disabled cleanup functionality after the V2 Platformics migration in early 2025. The solution combines two complementary approaches:

1. **Short-term**: Manual cleanup script to resolve existing inconsistencies
2. **Long-term**: Re-enable automatic stale deletion during ingestion

## Problem Statement

### Current State
- `AnnotationImporter` has `clean_up_siblings = False`, preventing automatic deletion of stale annotations during re-ingestion
- Test `test_import_annotations_files_removes_stale` is skipped with reason: "Cleaning up stale annotations is currently disabled"
- Re-running ingestion creates duplicate annotations because stale entries are never removed
- The TODO comment in `annotation.py` indicates this should be re-enabled but requires proper filter logic

### Impact
- Database inconsistencies accumulate over time
- Duplicate annotations appear when re-ingesting datasets
- Data integrity issues that require manual intervention
- Increased storage and query complexity

### Root Cause
The migration from V1 (Hasura) to V2 (Platformics) introduced a new import system (`IntegratedDBImporter`) that requires explicit filter criteria to identify stale records. The `AnnotationImporter` was disabled because:
1. Annotations are scoped to both `run_id` and `tomogram_voxel_spacing_id` (via annotation files)
2. The filter logic was not properly implemented to handle this dual scoping
3. Risk of accidentally deleting valid annotations from other runs/voxel spacings

## Solution Overview

### Phase 1: Manual Cleanup Script (Immediate)
Create a standalone script to identify and remove existing stale annotations.

### Phase 2: Re-enable Automatic Cleanup (Long-term)
Fix the filter logic and re-enable `clean_up_siblings` in `AnnotationImporter`.

## Phase 1: Manual Cleanup Script

### Objectives
- Identify stale annotations that no longer exist in S3
- Safely delete stale annotations and their related entities
- Provide dry-run mode for safety
- Support scoped cleanup (by dataset, run, or voxel spacing)

### Implementation

#### File Location
`apiv2/scripts/cleanup_stale_annotations.py`

#### Script Interface
```python
@click.command()
@click.option("--dataset-id", type=int, help="Cleanup annotations for specific dataset")
@click.option("--run-id", type=int, help="Cleanup annotations for specific run")
@click.option("--voxel-spacing-id", type=int, help="Cleanup annotations for specific voxel spacing")
@click.option("--dry-run", is_flag=True, default=True, help="Show what would be deleted without deleting")
@click.option("--db-uri", type=str, help="Database URI (optional)")
@click.option("--s3-bucket", type=str, required=True, help="S3 bucket to check for files")
@click.option("--s3-prefix", type=str, default="", help="S3 prefix")
@click.option("--anonymous", is_flag=True, default=False, help="Use anonymous S3 access")
def cleanup_stale_annotations(
    dataset_id: int | None,
    run_id: int | None,
    voxel_spacing_id: int | None,
    dry_run: bool,
    db_uri: str | None,
    s3_bucket: str,
    s3_prefix: str,
    anonymous: bool,
):
    """
    Identify and delete stale annotations whose metadata files no longer exist in S3.
    """
```

#### Algorithm

1. **Query Annotations**
   - Filter by provided scope (dataset_id, run_id, voxel_spacing_id)
   - If no scope provided, process all annotations (with warning)

2. **Check S3 Existence**
   - For each annotation, check if `s3_metadata_path` file exists in S3
   - Convert S3 path format if needed (handle both `s3://` and relative paths)

3. **Identify Stale Annotations**
   - Annotations whose metadata files don't exist in S3 are considered stale
   - Group by scope for reporting

4. **Handle Foreign Key Relationships**
   - Annotation deletion cascades to:
     - `AnnotationShape` (cascade="all, delete-orphan")
     - `AnnotationAuthor` (cascade="all, delete-orphan")
     - `AnnotationMethodLink` (cascade="all, delete-orphan")
     - `AnnotationFile` (via `AnnotationShape.annotation_files`)
   - SQLAlchemy cascade handles child deletions automatically

5. **Delete or Report**
   - If `dry_run=True`: Report what would be deleted
   - If `dry_run=False`: Delete stale annotations and commit

#### Safety Features

- **Dry-run by default**: Requires explicit `--no-dry-run` flag to actually delete
- **Scoped operations**: Limit cleanup to specific datasets/runs to reduce risk
- **Detailed logging**: Log all operations for audit trail
- **Confirmation prompt**: If not dry-run, prompt for confirmation before deletion
- **Backup recommendation**: Warn user to backup database before running

#### Example Usage

```bash
# Dry run (default) - see what would be deleted
python -m apiv2.scripts.cleanup_stale_annotations \
    --run-id 123 \
    --s3-bucket cryoet-data-portal-staging \
    --s3-prefix "s3://cryoet-data-portal-staging/"

# Actual deletion (requires confirmation)
python -m apiv2.scripts.cleanup_stale_annotations \
    --run-id 123 \
    --s3-bucket cryoet-data-portal-staging \
    --s3-prefix "s3://cryoet-data-portal-staging/" \
    --no-dry-run
```

#### Output Format

```
Found 15 stale annotations:
  Run ID 123: 5 annotations
    - Annotation ID 456: s3://bucket/path/to/missing.json
    - Annotation ID 457: s3://bucket/path/to/missing2.json
    ...
  Run ID 124: 10 annotations
    ...

Dry run mode: No deletions performed.
Run with --no-dry-run to perform deletions.
```

### Testing

1. **Unit Tests**: Test S3 path conversion, query filtering, stale detection logic
2. **Integration Tests**: Test with mock S3 client and database
3. **Manual Testing**: Run on staging environment with known stale data

### Dependencies

- `boto3` for S3 access
- `click` for CLI interface
- `sqlalchemy` for database access
- Existing `platformics.database.connect` utilities

## Phase 2: Re-enable Automatic Cleanup

### Objectives
- Re-enable `clean_up_siblings = True` in `AnnotationImporter`
- Implement proper `get_filters()` method to scope cleanup correctly
- Ensure no valid annotations are accidentally deleted

### Current Implementation Analysis

#### Current Code (`apiv2/db_import/importers/annotation.py`)

```python
class AnnotationImporter(IntegratedDBImporter):
    finder = MetadataFileFinder
    row_importer = AnnotationItem
    clean_up_siblings = False  # Currently disabled

    def get_filters(self) -> dict[str, Any]:
        raise NotImplementedError("This method should not be called, since annotations don't support sibling cleanup")
```

#### Problem
- Annotations are imported within the context of a `run` and `tomogram_voxel_spacing`
- The importer finds annotations in: `{tomogram_voxel_spacing.s3_prefix}/Annotations/`
- But annotations only have `run_id` in the database, not `tomogram_voxel_spacing_id`
- Need to filter by both `run_id` AND annotations that belong to the current voxel spacing

### Solution Design

#### Option A: Filter by Run ID Only (Simpler, Less Precise)
- Filter annotations by `run_id` only
- Risk: If multiple voxel spacings in the same run have annotations, we might delete annotations from other voxel spacings
- Mitigation: Only enable if annotations are unique per run (not per voxel spacing)

#### Option B: Filter by Run ID + Voxel Spacing (More Precise, Complex)
- Filter annotations by `run_id`
- Additionally filter by checking if annotation files reference the current `tomogram_voxel_spacing_id`
- More complex but safer

#### Recommended: Option B with Validation

### Implementation

#### Step 1: Update `AnnotationImporter.get_filters()`

```python
class AnnotationImporter(IntegratedDBImporter):
    finder = MetadataFileFinder
    row_importer = AnnotationItem
    clean_up_siblings = True  # Re-enable cleanup

    def __init__(self, config, run: models.Run, tomogram_voxel_spacing: models.TomogramVoxelSpacing, **unused_parents):
        self.run = run
        self.tomogram_voxel_spacing = tomogram_voxel_spacing
        self.config = config
        self.parents = {"run": run, "tomogram_voxel_spacing": tomogram_voxel_spacing}

    def get_filters(self) -> dict[str, Any]:
        """
        Filter annotations by run_id. Annotations are scoped to runs, and within a run,
        they are further scoped by the tomogram_voxel_spacing via their annotation files.

        Note: We filter by run_id only because:
        1. Annotations don't have a direct tomogram_voxel_spacing_id foreign key
        2. The relationship is indirect via AnnotationFile -> AnnotationShape -> Annotation
        3. During import, we only process annotations for the current voxel spacing,
           so any annotation with this run_id that wasn't imported must be stale for this scope
        """
        return {"run_id": self.run.id}
```

#### Step 2: Enhanced Cleanup Logic

The current `cleanup_unused_items` in `IntegratedDBImporter` compares imported objects to existing objects by ID. However, we need to be more careful with annotations because:

1. Annotations from the same run but different voxel spacings might exist
2. We only want to delete annotations that belong to the current voxel spacing

**Enhanced Approach**: Modify `cleanup_unused_items` to also check if annotation files reference the current voxel spacing:

```python
def cleanup_unused_items(self, session, imported_objects):
    """
    Enhanced cleanup for annotations: only delete annotations whose files
    reference the current tomogram_voxel_spacing.
    """
    if not self.clean_up_siblings:
        return

    existing_objs = self.get_existing_objects(session)
    keep_row_ids = [row.id for row in imported_objects]

    # For annotations, we need to be more careful
    if self.row_importer.model_class == models.Annotation:
        # Only consider annotations that have files referencing current voxel spacing
        rows_to_delete = []
        for id, row in existing_objs.items():
            if id not in keep_row_ids:
                # Check if this annotation has any files for the current voxel spacing
                has_files_for_voxel_spacing = any(
                    file.tomogram_voxel_spacing_id == self.tomogram_voxel_spacing.id
                    for shape in row.annotation_shapes
                    for file in shape.annotation_files
                )
                if has_files_for_voxel_spacing:
                    rows_to_delete.append(row)
    else:
        # Standard cleanup for other entities
        rows_to_delete = [row for id, row in existing_objs.items() if id not in keep_row_ids]

    for row in rows_to_delete:
        session.delete(row)
```

**Alternative Simpler Approach**: Since annotations are imported per voxel spacing, and the finder only finds annotations in `{voxel_spacing.s3_prefix}/Annotations/`, we can safely assume that any annotation with the same `run_id` that wasn't imported in this batch is stale for this voxel spacing context. However, this requires that:

1. Annotations are never shared across voxel spacings
2. The import process is atomic per voxel spacing

#### Step 3: Update Test

Re-enable the skipped test and update it:

```python
def test_import_annotations_files_removes_stale(
    sync_db_session: Session,
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[Base, dict[str, Any]], None],
    expected_annotations: list[dict[str, Any]],
    expected_annotation_files: list[dict[str, Any]],
) -> None:
    # Test that stale annotations are removed during re-ingestion
    populate_annotation_files(sync_db_session)
    populate_stale_annotation_files(sync_db_session)
    sync_db_session.commit()
    verify_dataset_import(import_annotations=True)
    # ... rest of test
```

### Validation Strategy

1. **Unit Tests**: Test filter logic, cleanup logic with various scenarios
2. **Integration Tests**: Test full import cycle with stale data
3. **Staging Validation**:
   - Run on staging with known stale annotations
   - Verify only expected annotations are deleted
   - Verify no valid annotations are affected
4. **Monitoring**: Add logging to track cleanup operations

### Rollout Plan

1. **Development**: Implement and test locally
2. **Staging**: Deploy to staging, run manual cleanup script first
3. **Staging Validation**: Run test ingestion, verify cleanup works correctly
4. **Production**:
   - Run manual cleanup script first to clean existing stale data
   - Deploy code changes
   - Monitor first few ingestion runs closely

## Database Schema Considerations

### Current Relationships

```
Annotation
  ├── run_id (FK to Run)
  ├── deposition_id (FK to Deposition)
  ├── annotation_shapes (1:N, cascade delete)
  │     └── annotation_files (1:N, cascade delete)
  │           └── tomogram_voxel_spacing_id (FK)
  ├── authors (1:N, cascade delete)
  └── method_links (1:N, cascade delete)
```

### Key Points
- Annotations don't have direct `tomogram_voxel_spacing_id`
- Relationship is indirect: `Annotation -> AnnotationShape -> AnnotationFile -> TomogramVoxelSpacing`
- Cascade deletes handle child entities automatically

## Risk Assessment

### Phase 1 (Manual Cleanup Script)
- **Low Risk**: Dry-run by default, scoped operations, explicit confirmation
- **Mitigation**: Always test on staging first, backup database before running

### Phase 2 (Automatic Cleanup)
- **Medium Risk**: Could accidentally delete valid annotations if filter logic is wrong
- **Mitigation**:
  - Thorough testing in staging
  - Gradual rollout (enable for one dataset first)
  - Comprehensive logging
  - Ability to disable quickly if issues arise

## Success Criteria

### Phase 1
- ✅ Script successfully identifies stale annotations
- ✅ Dry-run mode works correctly
- ✅ Actual deletion works without errors
- ✅ No valid annotations are deleted
- ✅ All related entities are properly cleaned up

### Phase 2
- ✅ `clean_up_siblings = True` is enabled
- ✅ Stale annotations are automatically removed during ingestion
- ✅ No valid annotations are deleted
- ✅ Test `test_import_annotations_files_removes_stale` passes
- ✅ No performance degradation
- ✅ Existing duplicates are cleaned up

## Timeline Estimate

| Phase | Task | Estimated Time |
|-------|------|----------------|
| Phase 1 | Design and implement cleanup script | 4-6 hours |
| Phase 1 | Testing and validation | 2-3 hours |
| Phase 1 | Documentation | 1 hour |
| Phase 2 | Design filter logic | 2-3 hours |
| Phase 2 | Implement and test | 4-6 hours |
| Phase 2 | Staging validation | 2-3 hours |
| Phase 2 | Production rollout | 1-2 hours |
| **Total** | | **16-24 hours** |

## Dependencies

- Access to staging and production databases
- S3 access for file existence checks
- Understanding of annotation import flow
- Coordination with data team for testing

## Related Documentation

- `docs/fix_duplicate_annotations.md` - Related issue with duplicate annotations
- `docs/data_ingestion.md` - Data ingestion process overview
- `apiv2/db_import/README.md` - Database import documentation
- `apiv2/db_import/importers/annotation.py` - Current annotation importer implementation

## Open Questions

1. **Are annotations ever shared across voxel spacings?**
   - If yes, we need more sophisticated filtering
   - If no, simple `run_id` filter may be sufficient

2. **What is the expected behavior if an annotation file is removed from S3 but metadata still exists?**
   - Should we delete the annotation?
   - Or mark it as incomplete?

3. **Should we add a `tomogram_voxel_spacing_id` directly to Annotation model?**
   - Would simplify filtering logic
   - Requires schema migration
   - May not be necessary if current approach works

## Future Enhancements

1. **Soft Delete**: Instead of hard deletion, mark annotations as deleted with timestamp
2. **Audit Trail**: Log all cleanup operations for compliance
3. **Automated Cleanup Job**: Schedule periodic cleanup runs
4. **Metrics**: Track cleanup statistics (counts, timing, etc.)
