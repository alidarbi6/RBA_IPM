"""Comparison plots; every figure is saved as PNG."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

COLORS = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e", "#8c564b", "#17becf", "#7f7f7f"]


def _save(fig, path: Path):
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print("  saved", path)


def plot_well(df: pd.DataFrame, well: str, models: list[str], metrics: pd.DataFrame, out: Path,
              kind: str = "Liquid"):
    """Time series, cross-plot, error bars and metric bars for one well.

    kind = "Liquid" or "Oil": which measured rate is compared with the models.
    """
    out.mkdir(parents=True, exist_ok=True)
    M = f"Measured_{kind}"
    tag = f"{well}_{kind.lower()}"
    colors = {m: COLORS[i % len(COLORS)] for i, m in enumerate(models)}

    # 1) time series: measured vs models
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(df["Date"], df[M], "k-o", ms=4, lw=2, label="Measured")
    for m in models:
        ax.plot(df["Date"], df[f"{m}_{kind}"], "--s", ms=3, color=colors[m], label=m)
    ax.set(title=f"{well} - {kind.lower()} rate", xlabel="Date", ylabel=f"{kind} rate (bbl/d)")
    ax.grid(alpha=.3); ax.legend(); fig.autofmt_xdate()
    _save(fig, out / f"{tag}_timeseries.png")

    # 2) cross-plot predicted vs measured
    fig, ax = plt.subplots(figsize=(6, 6))
    hi = np.nanmax(df[["Measured_Liquid"] + [f"{m}_{kind}" for m in models]].to_numpy())
    ax.plot([0, hi], [0, hi], "k-", lw=1, label="1:1")
    for m in models:
        ax.scatter(df[M], df[f"{m}_{kind}"], s=20, color=colors[m], label=m)
    ax.set(title=f"{well} - predicted vs measured", xlabel="Measured (bbl/d)", ylabel="Predicted (bbl/d)")
    ax.grid(alpha=.3); ax.legend()
    _save(fig, out / f"{tag}_crossplot.png")

    # 3) mean rate bar chart
    means = {"Measured": df[M].mean()}
    means.update({m: df[f"{m}_{kind}"].mean() for m in models})
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(means.keys(), means.values(), color=["k"] + [colors[m] for m in models])
    ax.bar_label(bars, fmt="%.0f")
    ax.set(title=f"{well} - mean {kind.lower()} rate", ylabel="bbl/d"); ax.grid(axis="y", alpha=.3)
    _save(fig, out / f"{tag}_mean_rate_bar.png")

    # 4) daily error bars per model
    fig, ax = plt.subplots(figsize=(11, 5))
    w = 0.8 / max(len(models), 1)
    x = np.arange(len(df))
    for i, m in enumerate(models):
        ax.bar(x + i * w, df[f"{m}_{kind}"] - df[M], w, color=colors[m], label=m)
    ax.axhline(0, color="k", lw=.8)
    ax.set_xticks(x + w * (len(models) - 1) / 2)
    ax.set_xticklabels(df["Date"].dt.strftime("%d"), fontsize=7)
    ax.set(title=f"{well} - daily error (model - measured)", xlabel="Day", ylabel="bbl/d")
    ax.grid(axis="y", alpha=.3); ax.legend()
    _save(fig, out / f"{tag}_daily_error_bar.png")

    # 5) metric bars
    _metric_bars(metrics, f"{well} - {kind.lower()} error metrics", out / f"{tag}_metrics_bar.png", colors)


def _metric_bars(metrics: pd.DataFrame, title: str, path: Path, colors: dict):
    cols = [c for c in ("MAE", "RMSE", "MAPE_%", "R2") if c in metrics]
    fig, axes = plt.subplots(1, len(cols), figsize=(4 * len(cols), 4.5))
    for ax, col in zip(np.atleast_1d(axes), cols):
        bars = ax.bar(metrics["Model"], metrics[col], color=[colors.get(m, "gray") for m in metrics["Model"]])
        ax.bar_label(bars, fmt="%.2f"); ax.set_title(col); ax.grid(axis="y", alpha=.3)
        ax.tick_params(axis="x", rotation=30)
    fig.suptitle(title)
    _save(fig, path)


def plot_all_wells(summary: pd.DataFrame, models: list[str], out: Path, kind: str = "Liquid"):
    """Grouped bars: MAPE per well and model, plus overall mean."""
    out.mkdir(parents=True, exist_ok=True)
    pivot = summary.pivot(index="Well", columns="Model", values="MAPE_%")[models]
    fig, ax = plt.subplots(figsize=(max(8, 0.8 * len(pivot)), 5))
    pivot.plot.bar(ax=ax, color=[COLORS[i % len(COLORS)] for i in range(len(models))])
    ax.set(title=f"MAPE by well and model ({kind.lower()} rate)", ylabel="MAPE (%)"); ax.grid(axis="y", alpha=.3)
    _save(fig, out / f"all_wells_{kind.lower()}_mape_bar.png")
