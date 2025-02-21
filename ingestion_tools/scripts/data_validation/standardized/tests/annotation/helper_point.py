from typing import Dict, List


def point_count_consistent(
    annotations: Dict[str, List[Dict]],
    annotation_metadata: Dict[str, Dict],
    annotation_file_to_metadata_file: Dict[str, str],
):
    """Check that the number of annotations is consistent between the metadata and the ndjson file."""

    for annotation_filename, annotation_data in annotations.items():
        print(f"Annotation Object: {annotation_filename}")
        metadata_file = annotation_file_to_metadata_file[annotation_filename]
        metadata = annotation_metadata[metadata_file]

        assert len(annotation_data) == metadata["object_count"]


def contained_in_tomo(
    annotations: Dict[str, List[Dict]],
    annotation_metadata_files: Dict,
    all_vs_tomogram_metadata: Dict,
):
    """Check that all points are contained within the tomogram dimensions."""

    def get_tomo_metadata(anno_metadata: Dict) -> Dict:
        for tomo in all_vs_tomogram_metadata:
            if tomo["alignment_metadata_path"] == anno_metadata["alignment_metadata_path"]:
                return tomo

    for annotation_filename, points in annotations.items():
        anno_metadata = annotation_metadata_files[annotation_filename]
        tomo_metadata = get_tomo_metadata(anno_metadata)
        print(f"\tFile: {annotation_filename}")
        for point in points:
            assert 0 <= point["location"]["x"] <= tomo_metadata["size"]["x"] - 1
            assert 0 <= point["location"]["y"] <= tomo_metadata["size"]["y"] - 1
            assert 0 <= point["location"]["z"] <= tomo_metadata["size"]["z"] - 1
