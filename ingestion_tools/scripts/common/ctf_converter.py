from common.config import DepositionImportConfig


class CTFInfo:
    """CTF information for a single section of a tilt series.
    Attributes:
        section (int): Section number (1-based).
        defocus_1 (float): Defocus value 1 (A).
        defocus_2 (float): Defocus value 2 (A).
        azimuth (float): Azimuth of astigmatism (deg).
        phase_shift (float): Additional phase shift (radians).
        cross_correlation (float): Cross correlation value.
        max_resolution (float): Maximum resolution (A).
    """
    section: int = None
    defocus_1: float = None
    defocus_2: float = None
    azimuth: float = None
    phase_shift: float = None
    cross_correlation: float = None
    max_resolution: float = None


class BaseCTFConverter:
    def __init__(self, config: DepositionImportConfig, path: str):
        self.path = path
        self.config = config

    @classmethod
    def get_ctf_info(cls) -> list[CTFInfo]:
        return []


class AreTomo3CTF(BaseCTFConverter):
    # TODO: Add parser
    @classmethod
    def get_ctf_info(cls) -> list[CTFInfo]:
        return []

def ctf_converter_factory(metadata: dict, config: DepositionImportConfig, path: str) -> BaseCTFConverter:
    ctf_format = metadata.get("format")
    if ctf_format == "CTFFIND":
        return AreTomo3CTF(config, path)
    return BaseCTFConverter(config, path)
