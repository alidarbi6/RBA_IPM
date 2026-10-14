"""Load the Excel files and build per-well choke inputs."""
import pandas as pd

# column in output -> description
INPUT_COLS = ["Pin", "Tin", "Pout", "Choke", "GOR", "WaterCut"]


def load_well_inputs(well_file, gor_file, start, end, wells=None) -> dict[str, pd.DataFrame]:
    """Return {well: DataFrame} with choke inputs and measured rates.

    Units: pressures psig, Tin deg F (from UCT in deg C), Choke inch (1/64 in / 64),
    WaterCut fraction = BSW / (Oil + BSW) where BSW is the water rate,
    Measured_Liquid = Oil + BSW (bbl/d).
    """
    raw = pd.read_excel(well_file)
    raw["Date"] = pd.to_datetime(raw["Date"])
    raw = raw[(raw["Date"] >= start) & (raw["Date"] < end)]

    liquid = raw["Oil"] + raw["BSW"]
    df = pd.DataFrame({
        "Well": raw["WellId"],
        "Date": raw["Date"],
        "Pin": raw["FTHP"],
        "Pout": raw["FLP"],
        "Tin": raw["UCT"] * 9 / 5 + 32,
        "Choke": raw["Choke"] / 64,
        "WaterCut": raw["BSW"] / liquid.where(liquid > 0),
        "Measured_Oil": raw["Oil"],
        "Measured_Liquid": liquid,
    })

    last_gor = (pd.read_excel(gor_file).dropna(subset=["GOR"])
                .groupby("WellId")["GOR"].last())
    df["GOR"] = df["Well"].map(last_gor)

    if wells:
        df = df[df["Well"].isin(wells)]
    return {w: g.drop(columns="Well").reset_index(drop=True) for w, g in df.groupby("Well")}


def usable_rows(df: pd.DataFrame) -> pd.Series:
    """Rows with all inputs present and a positive choke / flow."""
    return df[INPUT_COLS].notna().all(axis=1) & (df["Choke"] > 0) & (df["Pin"] > df["Pout"])
