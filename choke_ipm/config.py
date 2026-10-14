"""All user-editable settings live here (paths, PVT, period, enabled models)."""
from pathlib import Path

# ---------------------------------------------------------------- files
BASE_DIR = Path(__file__).resolve().parent.parent
WELL_FILE = BASE_DIR / "well.xlsx"          # daily well data
GOR_FILE = BASE_DIR / "GOR.xlsx"            # well-test GOR data
PROSPER_FILE = r"C:\Users\abolf\OneDrive\Desktop\prosper\well_pvt.Out"
OUTPUT_DIR = BASE_DIR / "results"           # plots + csv are saved here

# ---------------------------------------------------------------- period
START_DATE = "2026-05-01"
END_DATE = "2026-06-01"                     # exclusive

# ---------------------------------------------------------------- wells
# Empty list -> every well found in the period.
WELLS: list[str] = ["SPH-02"]

# ---------------------------------------------------------------- PVT (written into PROSPER)
PVT = {
    "Prosper.PVT.Input.Solgor": 1700,
    "Prosper.PVT.Input.Api": 42,
    "Prosper.PVT.Input.Grvgas": 0.75,
    "Prosper.PVT.Input.Watsal": 143000,
    "Prosper.PVT.Input.H2s": 0.02,
    "Prosper.PVT.Input.Co2": 0.02,
    "Prosper.PVT.Input.N2": 0,
}

# ---------------------------------------------------------------- models
MODELS_TO_RUN = ["ELF", "PETROLEUM_EXPERTS"]
