# Technical Specification: Modular Visualization State Generation

## Executive Summary

This specification addresses the problem where visualization state (Neuroglancer config) generation runs only during full dataset ingestion rather than being modular by entity type. This requires unnecessary re-ingestion jobs when annotation depositions are added to existing datasets. The solution makes visualization config generation work from both tomogram and annotation contexts, enabling automatic regeneration when annotations are added without requiring full dataset re-ingestion.

## Problem Statement

### Current State

- `VisualizationConfigImporter` is only a child of `TomogramImporter` in the dependency tree
- Visualization configs include annotation layers via `get_annotation_layer_info()`
- When annotation-only depositions are ingested, visualization configs are not regenerated
- This forces full dataset re-ingestion to update visualization states, which is inefficient and time-consuming

### Impact

- **Operational Inefficiency**: Annotation depositions require full dataset re-ingestion to update visualization configs
- **Resource Waste**: Re-processing entire datasets (tomograms, tiltseries, etc.) when only annotations changed
- **Time Delays**: Full re-ingestion takes significantly longer than just processing annotations
- **User Experience**: New annotations don't appear in visualization until full re-ingestion completes

### Root Cause

The visualization config generation is tightly coupled to tomogram processing in the dependency tree:

```python
# Current structure in utils.py
TomogramImporter: {
    VisualizationConfigImporter: {},  # Only runs when tomograms are processed
    KeyImageImporter: {},
}
```

When annotations are added via annotation depositions, the `VisualizationConfigImporter` is never invoked because:
1. Annotation depositions don't trigger tomogram processing
2. The dependency tree doesn't connect annotations to visualization config generation
3. Visualization configs need to be regenerated to include new annotation layers

## Solution Overview

### Approach: Dual-Context Visualization Config Generation

Make `VisualizationConfigImporter` work from both tomogram and annotation contexts by:

1. **Adding to Annotation Dependency Tree**: Make `VisualizationConfigImporter` a child of `AnnotationImporter` in addition to `TomogramImporter`
2. **Context-Aware Processing**: Modify `VisualizationConfigImporter` to detect its context and handle both scenarios:
   - **Tomogram Context** (existing): Called from `TomogramImporter`, has tomogram in parents
   - **Annotation Context** (new): Called from `AnnotationImporter`, needs to find related tomograms
3. **Tomogram Discovery**: When called from annotation context, find all tomograms that share the annotation's alignment metadata path
4. **Deduplication**: Ensure configs aren't regenerated multiple times for the same tomogram when multiple annotations trigger it

## Implementation Details

### Phase 1: Update Dependency Tree

**File**: `ingestion_tools/scripts/importers/utils.py`

**Change**: Add `VisualizationConfigImporter` as a child of `AnnotationImporter`:

```python
IMPORTER_DEP_TREE = {
    DepositionImporter: {
        DatasetImporter: {
            RunImporter: {
                ...
                VoxelSpacingImporter: {
                    AnnotationImporter: {
                        AnnotationVisualizationImporter: {},
                        VisualizationConfigImporter: {},  # ADD THIS
                    },
                    TomogramImporter: {
                        VisualizationConfigImporter: {},  # KEEP EXISTING
                        KeyImageImporter: {},
                    },
                },
            },
        },
    },
}
```

**Rationale**: This allows visualization configs to be generated when annotations are processed, in addition to when tomograms are processed.

### Phase 2: Modify VisualizationConfigImporter for Dual Context

**File**: `ingestion_tools/scripts/importers/visualization_config.py`

#### 2.1: Add Context Detection Method

Add a method to detect whether the importer is being called from tomogram or annotation context:

```python
def _get_context(self) -> Literal["tomogram", "annotation"]:
    """
    Detect whether this importer is being called from tomogram or annotation context.

    Returns:
        "tomogram" if called from TomogramImporter context
        "annotation" if called from AnnotationImporter context
    """
    if "tomogram" in self.parents:
        return "tomogram"
    elif "annotation" in self.parents:
        return "annotation"
    else:
        # Default to tomogram for backward compatibility
        return "tomogram"
```

#### 2.2: Add Method to Find Tomograms from Annotation Context

Add a method to find all tomograms that share an annotation's alignment metadata path:

```python
def _find_tomograms_by_alignment_path(self, alignment_metadata_path: str) -> list[TomogramImporter]:
    """
    Find all tomograms that share the given alignment metadata path.

    This is used when visualization config is generated from annotation context.

    Args:
        alignment_metadata_path: The alignment metadata path to match

    Returns:
        List of TomogramImporter instances that use this alignment
    """
    tomograms = []
    voxel_spacing = self.get_voxel_spacing()
    run = self.get_run()

    # Use the tomogram finder to get all tomograms for this run/voxel spacing
    from importers.tomogram import TomogramImporter

    for tomogram in TomogramImporter.finder(
        self.config,
        deposition=self.get_deposition(),
        dataset=self.get_dataset(),
        run=run,
        voxel_spacing=voxel_spacing,
    ):
        # Check if this tomogram uses the same alignment metadata path
        tomogram_alignment_path = self.config.to_formatted_path(tomogram.alignment_metadata_path)
        if tomogram_alignment_path == alignment_metadata_path:
            tomograms.append(tomogram)

    return tomograms
```

#### 2.3: Modify import_item() for Context-Aware Processing

Update `import_item()` to handle both contexts:

```python
def import_item(self) -> None:
    if not self.is_import_allowed():
        print(f"Skipping import of {self.name}")
        return

    context = self._get_context()

    if context == "tomogram":
        # Existing behavior: called from tomogram context
        tomogram = self.get_tomogram()
        ng_contents = self._create_config(tomogram.alignment_metadata_path)
        meta = NeuroglancerMetadata(self.config.fs, self.get_deposition().name, ng_contents)
        meta.write_metadata(self.get_output_path())

    elif context == "annotation":
        # New behavior: called from annotation context
        annotation = self.get_annotation()
        alignment_metadata_path = annotation.alignment_metadata_path

        # Find all tomograms that use this alignment
        tomograms = self._find_tomograms_by_alignment_path(alignment_metadata_path)

        if not tomograms:
            print(f"No tomograms found for alignment {alignment_metadata_path}, skipping visualization config generation")
            return

        # Regenerate config for each tomogram
        for tomogram in tomograms:
            # Create a temporary VisualizationConfigImporter instance for this tomogram
            # to reuse existing logic
            viz_config = VisualizationConfigImporter(
                config=self.config,
                metadata={},
                name=None,
                path=None,
                parents={
                    "deposition": self.get_deposition(),
                    "dataset": self.get_dataset(),
                    "run": self.get_run(),
                    "voxel_spacing": self.get_voxel_spacing(),
                    "tomogram": tomogram,
                },
                allow_imports=self.allow_imports,
            )

            # Generate and write the config
            ng_contents = viz_config._create_config(alignment_metadata_path)
            output_path = viz_config.get_output_path()
            meta = NeuroglancerMetadata(self.config.fs, self.get_deposition().name, ng_contents)
            meta.write_metadata(output_path)
            print(f"Regenerated visualization config for tomogram {tomogram.name} due to annotation changes")
```

#### 2.4: Add Helper Method to Get Annotation

Add a method to safely get the annotation from parents:

```python
def get_annotation(self) -> "AnnotationImporter":
    """Get the annotation from parents (when called from annotation context)."""
    if "annotation" not in self.parents:
        raise ValueError("Annotation not found in parents. This method should only be called from annotation context.")
    return self.parents["annotation"]
```

### Phase 3: Add Deduplication Logic

To prevent regenerating the same config multiple times when multiple annotations trigger it:

**File**: `ingestion_tools/scripts/importers/visualization_config.py`

Add class-level tracking:

```python
class VisualizationConfigImporter(BaseImporter):
    # Track which tomogram configs have been regenerated in this ingestion run
    _regenerated_configs: set[str] = set()

    @classmethod
    def _mark_config_regenerated(cls, tomogram_id: str, alignment_path: str) -> bool:
        """
        Mark a config as regenerated and return True if it was already regenerated.

        Args:
            tomogram_id: The tomogram identifier
            alignment_path: The alignment metadata path

        Returns:
            True if this config was already regenerated, False otherwise
        """
        key = f"{tomogram_id}:{alignment_path}"
        if key in cls._regenerated_configs:
            return True
        cls._regenerated_configs.add(key)
        return False

    @classmethod
    def _reset_regeneration_tracking(cls):
        """Reset the regeneration tracking (useful for testing)."""
        cls._regenerated_configs.clear()
```

Update `import_item()` to use deduplication:

```python
def import_item(self) -> None:
    # ... existing code ...

    elif context == "annotation":
        annotation = self.get_annotation()
        alignment_metadata_path = annotation.alignment_metadata_path
        tomograms = self._find_tomograms_by_alignment_path(alignment_metadata_path)

        if not tomograms:
            print(f"No tomograms found for alignment {alignment_metadata_path}, skipping visualization config generation")
            return

        for tomogram in tomograms:
            # Check if we've already regenerated this config
            if self._mark_config_regenerated(tomogram.identifier, alignment_metadata_path):
                print(f"Skipping duplicate visualization config regeneration for tomogram {tomogram.name}")
                continue

            # ... rest of regeneration logic ...
```

### Phase 4: Update BaseImporter if Needed

**File**: `ingestion_tools/scripts/importers/base_importer.py`

Ensure that `VisualizationConfigImporter` can access annotation from parents. The existing `parent_getter` mechanism should work, but verify:

```python
# This should already exist and work
def get_annotation(self) -> "AnnotationImporter":
    return self.parent_getter("annotation")
```

## Testing Strategy

### Unit Tests

**File**: `ingestion_tools/scripts/tests/s3_import/test_visualization_config.py`

#### Test 1: Context Detection
```python
def test_visualization_config_detects_tomogram_context():
    """Test that context detection works for tomogram context."""
    # Setup tomogram context
    # Verify _get_context() returns "tomogram"

def test_visualization_config_detects_annotation_context():
    """Test that context detection works for annotation context."""
    # Setup annotation context
    # Verify _get_context() returns "annotation"
```

#### Test 2: Tomogram Discovery
```python
def test_find_tomograms_by_alignment_path():
    """Test finding tomograms by alignment metadata path."""
    # Create test data with multiple tomograms, some sharing alignment path
    # Verify correct tomograms are found
```

#### Test 3: Annotation-Triggered Config Generation
```python
def test_visualization_config_from_annotation_context():
    """Test that visualization config is generated when called from annotation context."""
    # Create annotation with alignment path
    # Create tomogram with same alignment path
    # Trigger visualization config from annotation context
    # Verify config is generated and includes annotation layers
```

#### Test 4: Deduplication
```python
def test_visualization_config_deduplication():
    """Test that configs aren't regenerated multiple times."""
    # Create multiple annotations with same alignment path
    # Trigger visualization config generation
    # Verify config is only generated once per tomogram
```

### Integration Tests

#### Test 1: Annotation Deposition Workflow
```python
def test_annotation_deposition_regenerates_visualization_configs():
    """Test that ingesting annotation deposition regenerates visualization configs."""
    # Ingest a dataset with tomograms
    # Add annotation deposition
    # Verify visualization configs are regenerated
    # Verify new annotations appear in configs
```

#### Test 2: Multiple Annotations Same Tomogram
```python
def test_multiple_annotations_same_tomogram():
    """Test that multiple annotations for same tomogram only regenerate config once."""
    # Create tomogram
    # Add multiple annotations with same alignment path
    # Verify config is regenerated only once
    # Verify all annotations appear in final config
```

### Regression Tests

Ensure existing tests still pass:
- `test_viz_config_with_only_tomogram`
- `test_viz_config_with_tomogram_and_annotation`
- All existing visualization config tests

## Edge Cases and Error Handling

### Edge Case 1: No Tomograms Found
**Scenario**: Annotation is added but no tomograms share its alignment path
**Handling**: Skip visualization config generation with informative message
**Code**: Already handled in `import_item()` with early return

### Edge Case 2: Multiple Tomograms Same Alignment
**Scenario**: Multiple tomograms share the same alignment metadata path
**Handling**: Regenerate config for each tomogram (this is expected behavior)
**Code**: Loop through all found tomograms

### Edge Case 3: Annotation Without Alignment Path
**Scenario**: Annotation doesn't have alignment_metadata_path set
**Handling**: Should not occur in normal flow, but add validation
**Code**: Add check in `_find_tomograms_by_alignment_path()`

### Edge Case 4: Circular Dependencies
**Scenario**: Visualization config generation somehow triggers itself
**Handling**: Deduplication logic prevents infinite loops
**Code**: `_mark_config_regenerated()` prevents duplicate work

## Performance Considerations

### Optimization 1: Batch Processing
If multiple annotations are processed in the same ingestion run, the deduplication logic ensures each tomogram's config is only regenerated once, even if multiple annotations trigger it.

### Optimization 2: Lazy Tomogram Discovery
Only discover tomograms when actually needed (annotation context), not during tomogram context processing.

### Optimization 3: Caching
Consider caching tomogram lookups if performance becomes an issue, but start without caching to keep implementation simple.

## Migration and Rollout

### Phase 1: Development and Testing
1. Implement changes in feature branch
2. Write comprehensive tests
3. Run existing test suite to ensure no regressions
4. Test with sample annotation depositions

### Phase 2: Staging Deployment
1. Deploy to staging environment
2. Test with real annotation deposition data
3. Verify visualization configs are regenerated correctly
4. Monitor for performance issues

### Phase 3: Production Deployment
1. Deploy to production
2. Monitor ingestion logs for visualization config generation
3. Verify annotation depositions now trigger config regeneration
4. Document the change for users

## Rollback Plan

If issues are discovered:

1. **Immediate**: Revert dependency tree change in `utils.py` to remove `VisualizationConfigImporter` from `AnnotationImporter`
2. **Code**: The existing tomogram-based flow remains unchanged, so reverting only affects annotation-triggered generation
3. **Data**: No data migration needed - existing configs remain valid

## Success Criteria

1. ✅ Annotation depositions trigger visualization config regeneration
2. ✅ No full dataset re-ingestion required for annotation-only depositions
3. ✅ All existing tests pass
4. ✅ New tests for annotation-triggered generation pass
5. ✅ No performance degradation
6. ✅ Visualization configs correctly include new annotation layers
7. ✅ Deduplication prevents redundant config generation

## Timeline Estimate

| Phase | Tasks | Estimated Time | Dependencies |
|-------|-------|----------------|--------------|
| Phase 1: Dependency Tree | Update `IMPORTER_DEP_TREE` | 15 minutes | None |
| Phase 2: Dual Context Support | Modify `VisualizationConfigImporter` | 4-6 hours | Phase 1 |
| Phase 3: Deduplication | Add tracking logic | 1-2 hours | Phase 2 |
| Phase 4: Testing | Unit and integration tests | 4-6 hours | Phase 2, 3 |
| Phase 5: Documentation | Update docs, code comments | 1 hour | Phase 2 |
| **Total** | | **10-15 hours** | |

## Risk Assessment

### Low Risk
- Existing tomogram-based flow remains unchanged
- Changes are additive, not replacing existing functionality
- Deduplication prevents performance issues
- Rollback is straightforward

### Medium Risk
- Finding tomograms from annotation context may have edge cases
- Need to ensure alignment path matching is correct
- Multiple tomograms with same alignment need proper handling

### Mitigation
- Comprehensive testing before deployment
- Staging environment validation
- Monitor logs after deployment
- Clear error messages for debugging

## Related Issues

- Consider if other entity types (e.g., tomograms) should also trigger visualization config regeneration when they change
- Review if visualization config generation should be further modularized into a separate service
- Consider adding configuration flag to enable/disable annotation-triggered generation

## References

- Issue: Visualization state generation runs only during dataset ingestion rather than being modular by entity type
- Files:
  - `ingestion_tools/scripts/importers/utils.py` (dependency tree)
  - `ingestion_tools/scripts/importers/visualization_config.py` (main implementation)
  - `ingestion_tools/scripts/importers/annotation.py` (annotation importer)
  - `ingestion_tools/scripts/importers/tomogram.py` (tomogram importer)
- Documentation:
  - `docs/data_ingestion.md`
  - `docs/architecture.md`
