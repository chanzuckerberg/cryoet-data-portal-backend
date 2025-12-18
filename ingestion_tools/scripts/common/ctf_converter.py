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
        self,
        section: int,
        defocus_1: float,
        defocus_2: float,
        azimuth: float,
        phase_shift: float,
        cross_correlation: float,
        max_resolution: float,
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


class GctfCTF(BaseCTFConverter):
    def get_ctf_info(self) -> list[CTFInfo]:
        local_path = self.config.fs.localreadable(self.path)
        infos: list[CTFInfo] = []
        with open(local_path, "r") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith(("#", ";", "%")):
                    continue
                infos.append(self.from_str(line))
        return infos

    @classmethod
    def from_str(cls, line: str) -> CTFInfo:
        parts = line.split()
        if len(parts) not in (6, 7):
            raise ValueError(f"Gctf summary row must have 6 or 7 columns (got {len(parts)}): {line}")

        section = int(round(float(parts[0])))
        defocus_1 = float(parts[1])
        defocus_2 = float(parts[2])
        azimuth = float(parts[3])

        if len(parts) == 7:
            # 7-col: idx, defU, defV, angle, phaseShift, CC, resolution
            phase_shift = float(parts[4])
            cross_correlation = float(parts[5])
            max_resolution = float(parts[6])
        else:
            # 6-col: idx, defU, defV, angle, CC, resolution (no phase shift provided)
            phase_shift = 0.0
            cross_correlation = float(parts[4])
            max_resolution = float(parts[5])

        return CTFInfo(
            section=section,
            defocus_1=defocus_1,
            defocus_2=defocus_2,
            azimuth=azimuth,
            phase_shift=phase_shift,
            cross_correlation=cross_correlation,
            max_resolution=max_resolution,
        )


class IMODCTF(BaseCTFConverter):
    def get_ctf_info(self) -> list[CTFInfo]:
        local_path = self.config.fs.localreadable(self.path)
        infos: list[CTFInfo] = []
        with open(local_path, "r") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith(("#", ";", "%")):
                    continue
                parts = line.split()
                # Header/flag line typically has fewer than 7 columns
                if len(parts) < 7:
                    continue
                infos.append(self.from_str(line))
        return infos

    @classmethod
    def from_str(cls, line: str) -> CTFInfo:
        parts = line.split()
        # IMOD defocus file: startView endView startTilt endTilt defU[nm] defV[nm] azimuth[deg] ...
        section = int(parts[0])
        defocus_1_nm = float(parts[4])
        defocus_2_nm = float(parts[5])
        azimuth = float(parts[6])

        return CTFInfo(
            section=section,
            defocus_1=defocus_1_nm * 10.0,  # nm → A
            defocus_2=defocus_2_nm * 10.0,
            azimuth=azimuth,
            phase_shift=0.0,
            cross_correlation=0.0,
            max_resolution=0.0,
        )


def ctf_converter_factory(metadata: dict, config: DepositionImportConfig, path: str) -> BaseCTFConverter:
    ctf_format = (metadata.get("format") or "").upper()
    if ctf_format == "GCTF":
        return GctfCTF(config, path)
    if ctf_format == "CTFFIND":
        return AreTomo3CTF(config, path)
    if ctf_format == "IMOD":
        return IMODCTF(config, path)
    return BaseCTFConverter(config, path)
