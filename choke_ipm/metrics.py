"""Error statistics of each model against the measured rate."""
import numpy as np
import pandas as pd


def model_metrics(df: pd.DataFrame, model_names: list[str], kind: str = "Liquid") -> pd.DataFrame:
    """kind = "Liquid" (Oil + BSW) or "Oil"; measured column is Measured_<kind>."""
    measured = f"Measured_{kind}"
    rows = []
    for name in model_names:
        d = df[[measured, f"{name}_{kind}"]].dropna()
        d = d[d[measured] > 0]
        if d.empty:
            rows.append({"Model": name, "Rate": kind, "N": 0})
            continue
        err = d[f"{name}_{kind}"] - d[measured]
        ss_tot = ((d[measured] - d[measured].mean()) ** 2).sum()
        rows.append({
            "Model": name, "Rate": kind, "N": len(d),
            "MAE": err.abs().mean(),
            "RMSE": float(np.sqrt((err ** 2).mean())),
            "MAPE_%": (err.abs() / d[measured]).mean() * 100,
            "Bias": err.mean(),
            "R2": 1 - (err ** 2).sum() / ss_tot if ss_tot > 0 else np.nan,
        })
    return pd.DataFrame(rows)
