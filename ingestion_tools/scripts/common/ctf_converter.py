import math

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
    """Parser for IMOD ``.defocus`` files (ctfphaseflip / ctfplotter output).

    Every data row begins with ``startView endView startTilt endTilt`` followed by a
    defocus payload whose shape is determined by a bit ``flag``:

    ====  ============================================  ===================================
    bit   meaning                                       effect on the payload
    ====  ============================================  ===================================
    1     astigmatism values present                    ``defU defV azimuth`` (3 cols) vs a
                                                         single ``defocus`` (1 col)
    2     astigmatism axis angle is in radians          azimuth read as radians, not degrees
    4     phase shift present                           +1 column
    8     phase shift is in radians                     phase read as radians, not degrees
    16    tilt angles need inverting                    no effect on the values we emit
    32    cut-on frequency present                      +1 column (ignored)
    ====  ============================================  ===================================

    The flag is read from a version-3 header line (``<flag> 0 0.0 0.0 0.0 <version>``) when one
    is present. Files without a header (the original single-defocus layout, optionally with a
    trailing version number on the first row) are treated as ``flag == 0``. Defocus values are
    nm in the file and converted to Angstrom; azimuth is emitted in degrees and phase shift in
    radians, matching :class:`CTFInfo`.
    """

    ASTIGMATISM = 1
    ASTIGMATISM_RADIANS = 2
    PHASE_SHIFT = 4
    PHASE_SHIFT_RADIANS = 8
    CUT_ON_FREQUENCY = 32

    def get_ctf_info(self) -> list[CTFInfo]:
        local_path = self.config.fs.localreadable(self.path)
        with open(local_path, "r") as f:
            lines = [ln for ln in (raw.strip() for raw in f) if ln]
        if not lines:
            return []

        flag, data_lines = self._read_flag(lines)
        expected = self._column_indices(flag)["min_columns"]
        for n, ln in enumerate(data_lines):
            width = len(ln.split())
            # Tolerate a trailing version number on the first row of a header-less file.
            allowed = {expected, expected + 1} if n == 0 else {expected}
            if width not in allowed:
                raise ValueError(
                    f"IMOD defocus row has {width} columns, expected {expected} for flag {flag} "
                    f"(a header-less astigmatism file would land here): {ln!r}",
                )
        # Modern IMOD numbers views 1-based; a minimum view of 0 means the pre-IMOD-4.1 off-by-one
        # bug (views written from 0). Fail loudly rather than silently shift every section's CTF.
        if min(int(float(ln.split()[0])) for ln in data_lines) == 0:
            raise ValueError(
                "IMOD defocus file uses 0-based view numbers (pre-IMOD-4.1 off-by-one bug); "
                "regenerate it with a current IMOD so views are 1-based.",
            )
        return [self.from_str(ln, flag=flag) for ln in data_lines]

    @classmethod
    def _is_header(cls, parts: list[str]) -> bool:
        # Version-3 header "<flag> 0 0.0 0.0 0.0 <version>": fields 2-5 (view/tilt/defocus) are 0.
        return len(parts) >= 6 and all(float(parts[i]) == 0.0 for i in (1, 2, 3, 4))

    @classmethod
    def _read_flag(cls, lines: list[str]) -> tuple[int, list[str]]:
        """Return ``(flag, data_lines)``, reading the flag from a version-3 header if present."""
        first = lines[0].split()
        if cls._is_header(first):
            return int(float(first[0])), lines[1:]
        # No header: original single-defocus layout (a trailing version number on the first row
        # is tolerated as an extra column). This corresponds to flag 0.
        return 0, lines

    @classmethod
    def _column_indices(cls, flag: int) -> dict[str, int]:
        """Map payload fields to column indices for the given flag."""
        idx: dict[str, int] = {}
        if flag & cls.ASTIGMATISM:
            idx["defocus_1"], idx["defocus_2"], idx["azimuth"] = 4, 5, 6
            nxt = 7
        else:
            idx["defocus_1"] = idx["defocus_2"] = 4
            nxt = 5
        if flag & cls.PHASE_SHIFT:
            idx["phase_shift"] = nxt
            nxt += 1
        if flag & cls.CUT_ON_FREQUENCY:
            nxt += 1  # cut-on frequency column is present but unused
        idx["min_columns"] = nxt
        return idx

    @classmethod
    def from_str(cls, line: str, flag: int = 0) -> CTFInfo:
        parts = line.split()
        idx = cls._column_indices(flag)
        if len(parts) < idx["min_columns"]:
            raise ValueError(
                f"IMOD defocus row has {len(parts)} columns, expected >= {idx['min_columns']} "
                f"for flag {flag}: {line!r}",
            )

        defocus_1_nm = float(parts[idx["defocus_1"]])
        defocus_2_nm = float(parts[idx["defocus_2"]])

        azimuth = 0.0
        if flag & cls.ASTIGMATISM:
            azimuth = float(parts[idx["azimuth"]])
            if flag & cls.ASTIGMATISM_RADIANS:
                azimuth = math.degrees(azimuth)  # CTFInfo.azimuth is degrees

        phase_shift = 0.0
        if flag & cls.PHASE_SHIFT:
            phase_shift = float(parts[idx["phase_shift"]])
            if not flag & cls.PHASE_SHIFT_RADIANS:
                phase_shift = math.radians(phase_shift)  # IMOD default is degrees; CTFInfo is radians

        return CTFInfo(
            section=int(float(parts[0])),
            defocus_1=defocus_1_nm * 10.0,  # nm -> A
            defocus_2=defocus_2_nm * 10.0,
            azimuth=azimuth,
            phase_shift=phase_shift,
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
