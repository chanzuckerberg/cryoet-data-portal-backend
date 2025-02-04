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
    def __init__(
            self, section: int, defocus_1: float, defocus_2: float, azimuth: float, phase_shift: float, cross_correlation: float, max_resolution: float,
    ):
        self.section = section
        self.defocus_1 = defocus_1
        self.defocus_2 = defocus_2
        self.azimuth = azimuth
        self.phase_shift = phase_shift
        self.cross_correlation = cross_correlation
        self.max_resolution = max_resolution


class BaseCTFConverter:
    def __init__(self, config: DepositionImportConfig, path: str):
        self.path = path
        self.config = config

    @classmethod
    def get_ctf_info(cls) -> list[CTFInfo]:
        return []


class AreTomo3CTF(BaseCTFConverter):
    CtfValues: list[CTFInfo]

    def get_ctf_info(self) -> list[CTFInfo]:
        local_path = self.config.fs.localreadable(self.path)
        with open(local_path, "r") as f:
            text = f.read()
        lines = text.strip().splitlines()
        lines.pop(0)
        return [self.from_str(line) for line in lines]

    @classmethod
    def from_str(cls, line: str):
        parts = line.split()
        return CTFInfo(
            section=int(parts[0]),
            defocus_1=float(parts[1]),
            defocus_2=float(parts[2]),
            azimuth=float(parts[3]),
            phase_shift=float(parts[4]),
            cross_correlation=float(parts[5]),
            max_resolution=float(parts[6]),
        )

def ctf_converter_factory(metadata: dict, config: DepositionImportConfig, path: str) -> BaseCTFConverter:
    ctf_format = metadata.get("format")
    if ctf_format == "CTFFIND":
        return AreTomo3CTF(config, path)
    return BaseCTFConverter(config, path)
