from typing import Dict


def point_count_consistent(
    annotations: Dict[str, Dict[str, Dict]],
    annotation_metadata: Dict[str, Dict],
):
    """Check that the number of annotations is consistent between the metadata and the ndjson file."""

    for base in annotations:
        metadata = annotation_metadata[base]
        print(f"Annotation Object: {base}")

        files = annotations[base]
        for filename, data in files.items():
            print(f"\tFile: {filename}")
            assert len(data) == metadata["object_count"]


def contained_in_tomo(
    annotations: Dict[str, Dict[str, Dict]],
    canonical_tomogram_metadata: Dict,
):
    """Check that all points are contained within the tomogram dimensions."""

    for base, annotation in annotations.items():
        print(f"Annotation Object: {base}")
        for filename, points in annotation.items():
            print(f"\tFile: {filename}")
            for ann in points:
                assert 0 <= ann["location"]["x"] <= canonical_tomogram_metadata["size"]["x"] - 1
                assert 0 <= ann["location"]["y"] <= canonical_tomogram_metadata["size"]["y"] - 1
                assert 0 <= ann["location"]["z"] <= canonical_tomogram_metadata["size"]["z"] - 1
