"""Main entry point.

Examples
  python -m choke_ipm.run                          # settings from config.py
  python -m choke_ipm.run --wells SPH-02 SPH-03    # list of wells
  python -m choke_ipm.run --all-wells
  python -m choke_ipm.run --models ELF PETROLEUM_EXPERTS GILBERT
  python -m choke_ipm.run --plots-only             # re-plot from saved csv (no PROSPER)
"""
import argparse
import pandas as pd

from . import config as cfg
from .data_prep import load_well_inputs
from .metrics import model_metrics
from .models import MODELS, resolve_extra_inputs
from .plots import plot_all_wells, plot_well


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--wells", nargs="+", help="well names (default: config.WELLS)")
    p.add_argument("--all-wells", action="store_true", help="every well in the period")
    p.add_argument("--models", nargs="+", help="model names (default: config.ENABLED_MODELS)")
    p.add_argument("--start", default=cfg.START_DATE)
    p.add_argument("--end", default=cfg.END_DATE)
    p.add_argument("--no-prompt", action="store_true", help="never ask for extra inputs")
    p.add_argument("--plots-only", action="store_true", help="reuse saved csv instead of running PROSPER")
    return p.parse_args()


def main():
    a = parse_args()
    out_dir = cfg.OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    names = a.models or cfg.ENABLED_MODELS
    models = [MODELS[n] for n in names]
    extras = {m.name: resolve_extra_inputs(m, cfg.EXTRA_INPUTS, not a.no_prompt) for m in models}

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
                df = run_model(df, m, extras[m.name], cfg.PROSPER_FILE, cfg.PVT)
            df.to_csv(csv, index=False)
        metrics = model_metrics(df, names)
        metrics.insert(0, "Well", well)
        summary.append(metrics)
        print(metrics.to_string(index=False))
        plot_well(df.dropna(subset=["Measured_Liquid"]), well, names, metrics, out_dir / "plots")

    summary = pd.concat(summary, ignore_index=True)
    summary.to_csv(out_dir / "metrics_summary.csv", index=False)
    if summary["Well"].nunique() > 1:
        plot_all_wells(summary.dropna(subset=["MAPE_%"]), names, out_dir / "plots")


if __name__ == "__main__":
    main()
