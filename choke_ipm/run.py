"""Main entry point.

Examples
  python -m choke_ipm.run                          # settings from config.py
  python -m choke_ipm.run --wells SPH-02 SPH-03    # list of wells
  python -m choke_ipm.run --all-wells
  python -m choke_ipm.run --plots-only             # re-plot from saved csv (no PROSPER)
"""
import argparse
import pandas as pd

from . import config as cfg
from .data_prep import load_well_inputs
from .metrics import model_metrics
from .models import MODELS
from .plots import plot_all_wells, plot_well


KINDS = ("Liquid", "Oil")   # rates compared with the measured data


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--wells", nargs="+", help="well names (default: config.WELLS)")
    p.add_argument("--all-wells", action="store_true", help="every well in the period")
    p.add_argument("--start", default=cfg.START_DATE)
    p.add_argument("--end", default=cfg.END_DATE)
    p.add_argument("--plots-only", action="store_true", help="reuse saved csv instead of running PROSPER")
    return p.parse_args()


def main():
    a = parse_args()
    out_dir = cfg.OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    names = cfg.MODELS_TO_RUN
    models = [MODELS[n] for n in names]

    wells = None if a.all_wells else (a.wells or cfg.WELLS or None)
    data = load_well_inputs(cfg.WELL_FILE, cfg.GOR_FILE, a.start, a.end, wells)
    print(f"{len(data)} well(s), models: {names}")

    summary = []
    for well, df in data.items():
        csv = out_dir / f"{well}_results.csv"
        if a.plots_only:
            df = pd.read_csv(csv, parse_dates=["Date"])
        else:
            from .prosper_runner import run_model
            print(f"Running {well} ...")
            for m in models:
                df = run_model(df, m, cfg.PROSPER_FILE, cfg.PVT)
            df.to_csv(csv, index=False)
        for kind in KINDS:
            metrics = model_metrics(df, names, kind)
            metrics.insert(0, "Well", well)
            summary.append(metrics)
            print(metrics.to_string(index=False))
            plot_well(df.dropna(subset=[f"Measured_{kind}"]), well, names, metrics,
                      out_dir / "plots", kind)

    summary = pd.concat(summary, ignore_index=True)
    summary.to_csv(out_dir / "metrics_summary.csv", index=False)
    if summary["Well"].nunique() > 1:
        for kind in KINDS:
            part = summary[summary["Rate"] == kind].dropna(subset=["MAPE_%"])
            plot_all_wells(part, names, out_dir / "plots", kind)


if __name__ == "__main__":
    main()
