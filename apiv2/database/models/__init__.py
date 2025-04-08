"""
Make database models importable

Auto-generated by running 'make codegen'. Do not edit.
Make changes to the template codegen/templates/database/models/__init__.py.j2 instead.
"""

# isort: skip_file

from sqlalchemy.orm import configure_mappers

from platformics.database.models import Base, meta  # noqa: F401
from database.models.gain_file import GainFile  # noqa: F401
from database.models.frame_acquisition_file import FrameAcquisitionFile  # noqa: F401
from database.models.alignment import Alignment  # noqa: F401
from database.models.annotation_author import AnnotationAuthor  # noqa: F401
from database.models.annotation_file import AnnotationFile  # noqa: F401
from database.models.annotation_shape import AnnotationShape  # noqa: F401
from database.models.annotation import Annotation  # noqa: F401
from database.models.dataset_author import DatasetAuthor  # noqa: F401
from database.models.dataset_funding import DatasetFunding  # noqa: F401
from database.models.dataset import Dataset  # noqa: F401
from database.models.deposition_author import DepositionAuthor  # noqa: F401
from database.models.deposition import Deposition  # noqa: F401
from database.models.deposition_type import DepositionType  # noqa: F401
from database.models.frame import Frame  # noqa: F401
from database.models.per_section_alignment_parameters import PerSectionAlignmentParameters  # noqa: F401
from database.models.per_section_parameters import PerSectionParameters  # noqa: F401
from database.models.run import Run  # noqa: F401
from database.models.tiltseries import Tiltseries  # noqa: F401
from database.models.tomogram_author import TomogramAuthor  # noqa: F401
from database.models.tomogram_voxel_spacing import TomogramVoxelSpacing  # noqa: F401
from database.models.tomogram import Tomogram  # noqa: F401
from database.models.annotation_method_link import AnnotationMethodLink  # noqa: F401

configure_mappers()
