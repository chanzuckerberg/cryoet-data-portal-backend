from typing import Dict


def basic_metadata_check(metadata: Dict):
    """Check the basic metadata fields for depositions, datasets, annotations, and tomograms (not tiltseries)."""
    assert metadata["deposition_id"]
    assert isinstance(metadata["authors"], list)
    assert len(metadata["authors"]) >= 1
    assert all(isinstance(author, dict) for author in metadata["authors"])
    assert all(author["name"] for author in metadata["authors"])
    assert any(author.get("corresponding_author_status", False) for author in metadata["authors"])
    assert any(
        author.get("primary_author_status", False) or author.get("primary_annotator_status", False)
        for author in metadata["authors"]
    )
