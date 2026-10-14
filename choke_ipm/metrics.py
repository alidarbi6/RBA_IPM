"""Error statistics of each model against measured liquid rate."""
import numpy as np
import pandas as pd


def model_metrics(df: pd.DataFrame, model_names: list[str]) -> pd.DataFrame:
    rows = []
    for name in model_names:
        d = df[["Measured_Liquid", f"{name}_Liquid"]].dropna()
        d = d[d["Measured_Liquid"] > 0]
        if d.empty:
            rows.append({"Model": name, "N": 0})
            continue
        err = d[f"{name}_Liquid"] - d["Measured_Liquid"]
        ss_res = (err ** 2).sum()
        ss_tot = ((d["Measured_Liquid"] - d["Measured_Liquid"].mean()) ** 2).sum()
        rows.append({
            "Model": name, "N": len(d),
            "MAE": err.abs().mean(),
            "RMSE": float(np.sqrt((err ** 2).mean())),
            "MAPE_%": (err.abs() / d["Measured_Liquid"]).mean() * 100,
            "Bias": err.mean(),
            "R2": 1 - ss_res / ss_tot if ss_tot > 0 else np.nan,
        })
    return pd.DataFrame(rows)
