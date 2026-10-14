# ELF vs Petroleum Experts choke models (PROSPER / OpenServer)

Runs the two PROSPER choke models on the daily well data (`well.xlsx`, `GOR.xlsx`) and compares
them with the measured production rates in the Excel file:
- **Oil** rate (`Oil` column) vs model liquid x (1 - water cut)
- **Liquid** rate (`Oil` + `BSW`) vs model liquid rate

```
python -m choke_ipm.run                          # wells from choke_ipm/config.py
python -m choke_ipm.run --wells SPH-02 SPH-03    # list of wells
python -m choke_ipm.run --all-wells
python -m choke_ipm.run --plots-only             # re-plot from results/*.csv (no PROSPER)
python -m choke_ipm.discover_models              # check model codes inside PROSPER
```

Output: `results/<well>_results.csv`, `results/metrics_summary.csv` and PNG plots in `results/plots/`
(time series, cross-plot, mean-rate bars, daily-error bars, metric bars, all-wells MAPE bars).

Files: `config.py` · `models.py` · `data_prep.py` · `prosper_runner.py` · `metrics.py` · `plots.py` · `run.py`.
Model codes in `models.py` (ELF=0, Petroleum Experts=4) come from the old notebook - verify once with `discover_models`.
