# Fix Duplicate Annotations During Re-ingestion

## Problem Summary

Re-running ingestion creates duplicate annotations due to inadequate uniqueness determination during both data transformation and database import. The current uniqueness check in the database importer does not include `s3_metadata_path`, which is the actual unique identifier for each annotation metadata file.

### Root Cause

**During Data Transformation (V1 ingestion):**
- `AnnotationIdentifierHelper._generate_hash_key()` includes: `container_key`, `deposition_id`, `object_description`, `object_name`, `annotation_method`, `object_state`, `alignment_metadata_path`

**During Database Import (V2):**
- `AnnotationItem.id_fields` includes: `run_id`, `deposition_id`, `annotation_method`, `object_name`, `object_description`, `object_state`
- **Missing:** `s3_metadata_path` (the unique identifier for the metadata file)

When the same annotation metadata file is processed again, the importer cannot find the existing record because `s3_metadata_path` is not part of the uniqueness check, leading to duplicate creation.

## Solution

Add `s3_metadata_path` to `AnnotationItem.id_fields` to ensure each unique metadata file creates/updates only one annotation record.

## Work Breakdown

### Phase 1: Pre-Implementation Analysis

#### Task 1.1: Identify Existing Duplicates
**Priority:** High
**Estimated Time:** 1-2 hours
**Owner:** Data Team / Backend Team

**Actions:**
1. Run SQL query to identify true duplicates (same `s3_metadata_path`):
   ```sql
   SELECT s3_metadata_path, COUNT(*) as count,
          STRING_AGG(id::text, ', ') as annotation_ids
   FROM annotation
   GROUP BY s3_metadata_path
   HAVING COUNT(*) > 1;
   ```

2. Run SQL query to identify potential duplicates (same old `id_fields` but different `s3_metadata_path`):
   ```sql
   SELECT run_id, deposition_id, annotation_method, object_name,
          object_description, object_state, COUNT(*) as count,
          STRING_AGG(s3_metadata_path, ' | ') as paths
   FROM annotation
   GROUP BY run_id, deposition_id, annotation_method, object_name,
            object_description, object_state
   HAVING COUNT(*) > 1;
   ```

3. Document findings:
   - Number of true duplicates
   - Number of potential duplicates
   - Affected datasets/runs
   - Impact assessment

**Deliverable:** Report of duplicate analysis

#### Task 1.2: Verify Data Integrity
**Priority:** High
**Estimated Time:** 30 minutes
**Owner:** Backend Team

**Actions:**
1. Verify `s3_metadata_path` is always populated:
   - Check that `get_s3_url()` always returns a value
   - Verify `self.input_data["file"]` is always present in the importer
   - Review error handling in `load_computed_fields()`

2. Check for any NULL values in existing data:
   ```sql
   SELECT COUNT(*) FROM annotation WHERE s3_metadata_path IS NULL;
   ```

**Deliverable:** Verification report

### Phase 2: Implementation

#### Task 2.1: Update AnnotationItem.id_fields
**Priority:** Critical
**Estimated Time:** 15 minutes
**Owner:** Backend Developer

**File:** `apiv2/db_import/importers/annotation.py`

**Change:**
```python
# Line 10: Update id_fields to include s3_metadata_path
id_fields = ["run_id", "deposition_id", "annotation_method", "object_name", "object_description", "object_state", "s3_metadata_path"]
```

**Code Review Checklist:**
- [ ] Verify `s3_metadata_path` is computed before `_get_identifiers()` is called
- [ ] Confirm no breaking changes to child entities
- [ ] Check that database column exists and is non-nullable

**Deliverable:** Code change with PR

#### Task 2.2: Add Documentation/Comments
**Priority:** Low
**Estimated Time:** 10 minutes
**Owner:** Backend Developer

**Actions:**
1. Add inline comment explaining why `s3_metadata_path` is in `id_fields`:
   ```python
   # id_fields uniquely identify an annotation record. s3_metadata_path is included
   # because it uniquely identifies the metadata file, preventing duplicates when
   # re-running ingestion on the same data.
   id_fields = [...]
   ```

**Deliverable:** Updated code with comments

### Phase 3: Testing

#### Task 3.1: Unit Tests
**Priority:** High
**Estimated Time:** 1-2 hours
**Owner:** Backend Developer

**Actions:**
1. Run existing annotation import tests:
   ```bash
   pytest apiv2/db_import/tests/test_db_annotation_import.py -v
   ```

2. Verify all tests pass:
   - `test_import_annotations`
   - `test_import_annotation_authors`
   - `test_import_annotation_method_links`
   - `test_import_annotation_authors_removes_stale`
   - `test_import_annotation_method_links_removes_stale`

**Deliverable:** Test results report

#### Task 3.2: Integration Test - Re-ingestion Scenario
**Priority:** High
**Estimated Time:** 2-3 hours
**Owner:** Backend Developer / QA

**Actions:**
1. Create test scenario:
   - Import a dataset with annotations
   - Verify annotations are created correctly
   - Re-run ingestion on the same dataset
   - Verify annotations are **updated** (not duplicated)

2. Test cases:
   - Same metadata file, same content → should update
   - Same metadata file, different content → should update
   - New metadata file → should create new annotation
   - Removed metadata file → should remain (cleanup disabled)

**Test Script:**
```python
# Pseudo-code for test
def test_re_ingestion_no_duplicates():
    # First ingestion
    import_dataset(dataset_id="test-001")
    initial_count = count_annotations(dataset_id="test-001")

    # Re-ingestion
    import_dataset(dataset_id="test-001")
    final_count = count_annotations(dataset_id="test-001")

    assert initial_count == final_count, "Duplicates created during re-ingestion"

    # Verify annotations were updated, not duplicated
    for annotation in get_annotations(dataset_id="test-001"):
        duplicates = find_duplicates_by_s3_path(annotation.s3_metadata_path)
        assert len(duplicates) == 1, f"Found duplicates for {annotation.s3_metadata_path}"
```

**Deliverable:** Integration test results

#### Task 3.3: Edge Case Testing
**Priority:** Medium
**Estimated Time:** 1 hour
**Owner:** Backend Developer

**Test Cases:**
1. Annotation with NULL `object_description` → should work
2. Annotation with NULL `object_state` → should work
3. Annotation with NULL `deposition_id` → should work (if allowed)
4. Very long `s3_metadata_path` → should work
5. Special characters in `s3_metadata_path` → should work

**Deliverable:** Edge case test results

### Phase 4: Data Cleanup (If Needed)

#### Task 4.1: Create Deduplication Script
**Priority:** Medium (Only if duplicates found in Task 1.1)
**Estimated Time:** 4-6 hours
**Owner:** Backend Developer / Data Engineer

**Actions:**
1. Create script to identify true duplicates (same `s3_metadata_path`)
2. Determine which record to keep (e.g., most recent `last_modified_date`)
3. Update foreign keys in child tables:
   - `annotation_shape.annotation_id`
   - `annotation_file.annotation_shape_id` (via shape)
   - `annotation_author.annotation_id`
   - `annotation_method_link.annotation_id`
4. Delete duplicate annotation records
5. Verify data integrity after cleanup

**Script Structure:**
```python
def deduplicate_annotations(session):
    # Find duplicates
    duplicates = find_duplicate_annotations(session)

    for s3_path, annotations in duplicates.items():
        # Keep the most recent one
        keep = max(annotations, key=lambda a: a.last_modified_date)
        remove = [a for a in annotations if a.id != keep.id]

        # Update foreign keys
        for annotation in remove:
            update_child_records(session, annotation.id, keep.id)
            session.delete(annotation)

    session.commit()
```

**Deliverable:** Deduplication script with tests

#### Task 4.2: Execute Data Cleanup
**Priority:** Medium (Only if duplicates found)
**Estimated Time:** 2-4 hours
**Owner:** Data Team / DevOps

**Actions:**
1. Backup database before cleanup
2. Run deduplication script in staging environment
3. Verify results
4. Run in production (during maintenance window)
5. Monitor for issues

**Deliverable:** Cleanup execution report

### Phase 5: Deployment

#### Task 5.1: Code Review
**Priority:** High
**Estimated Time:** 1 hour
**Owner:** Backend Team Lead

**Review Checklist:**
- [ ] Code change is minimal and focused
- [ ] Tests pass
- [ ] No breaking changes identified
- [ ] Documentation updated
- [ ] Cascading dependencies reviewed

**Deliverable:** Approved PR

#### Task 5.2: Staging Deployment
**Priority:** High
**Estimated Time:** 1 hour
**Owner:** DevOps / Backend Team

**Actions:**
1. Deploy to staging
2. Run test ingestion on staging data
3. Verify no duplicates created
4. Monitor logs for errors

**Deliverable:** Staging deployment report

#### Task 5.3: Production Deployment
**Priority:** High
**Estimated Time:** 1-2 hours
**Owner:** DevOps / Backend Team

**Actions:**
1. Schedule deployment window
2. Deploy code change
3. Monitor for errors
4. Run test ingestion on small dataset
5. Verify results

**Deliverable:** Production deployment report

### Phase 6: Monitoring & Validation

#### Task 6.1: Post-Deployment Monitoring
**Priority:** High
**Estimated Time:** Ongoing (first week)
**Owner:** Backend Team

**Actions:**
1. Monitor ingestion logs for errors
2. Check for new duplicate annotations
3. Verify annotation counts are stable
4. Monitor database performance (query time for annotation lookups)

**Metrics to Track:**
- Number of annotations created per ingestion run
- Number of duplicate detection errors (should be zero)
- Query performance for annotation lookups

**Deliverable:** Monitoring dashboard/report

#### Task 6.2: Validation Query
**Priority:** Medium
**Estimated Time:** 30 minutes
**Owner:** Backend Team

**Actions:**
1. Run validation query after first production ingestion:
   ```sql
   -- Should return 0 rows (no duplicates with same s3_metadata_path)
   SELECT s3_metadata_path, COUNT(*) as count
   FROM annotation
   GROUP BY s3_metadata_path
   HAVING COUNT(*) > 1;
   ```

**Deliverable:** Validation report

## Timeline Estimate

| Phase | Tasks | Estimated Time | Dependencies |
|-------|-------|----------------|--------------|
| Phase 1: Analysis | 1.1, 1.2 | 2-3 hours | None |
| Phase 2: Implementation | 2.1, 2.2 | 30 minutes | Phase 1 |
| Phase 3: Testing | 3.1, 3.2, 3.3 | 4-6 hours | Phase 2 |
| Phase 4: Data Cleanup | 4.1, 4.2 | 6-10 hours | Phase 1 (if needed) |
| Phase 5: Deployment | 5.1, 5.2, 5.3 | 3-4 hours | Phase 3 |
| Phase 6: Monitoring | 6.1, 6.2 | Ongoing | Phase 5 |

**Total Estimated Time:** 15-23 hours (excluding data cleanup if not needed)

## Risk Assessment

### Low Risk
- Code change is minimal and isolated
- No database schema changes required
- No breaking changes to child entities
- Tests can validate behavior

### Medium Risk
- Existing duplicates may need cleanup
- Query performance impact (minimal - just adding one field to WHERE clause)

### Mitigation
- Thorough testing before production
- Data backup before any cleanup
- Gradual rollout (staging → production)
- Monitoring after deployment

## Success Criteria

1. ✅ No duplicate annotations created during re-ingestion
2. ✅ All existing tests pass
3. ✅ Integration test confirms updates instead of duplicates
4. ✅ No performance degradation
5. ✅ No data loss or corruption
6. ✅ Existing duplicates cleaned up (if any found)

## Related Issues

- Consider aligning V1 transformation uniqueness logic (separate task)
- Review if `clean_up_siblings = False` should remain disabled for annotations

## References

- Issue: Re-running ingestion creates duplicate annotations
- Files:
  - `apiv2/db_import/importers/annotation.py` (main change)
  - `apiv2/db_import/importers/base.py` (uniqueness logic)
  - `ingestion_tools/scripts/importers/annotation.py` (V1 transformation)
- Documentation:
  - `docs/data_ingestion.md`
  - `docs/architecture.md`
