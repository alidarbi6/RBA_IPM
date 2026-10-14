# Choke model comparison (PROSPER / OpenServer)

Runs PROSPER choke models on daily well data, compares them with measured liquid rate
(Oil + BSW) and saves PNG plots + CSV.

```
python -m choke_ipm.run                              # settings in choke_ipm/config.py
python -m choke_ipm.run --wells SPH-02 SPH-03        # list of wells
python -m choke_ipm.run --all-wells
python -m choke_ipm.run --models ELF PETROLEUM_EXPERTS GILBERT   # extra model -> asks for its inputs
python -m choke_ipm.run --plots-only                 # re-plot from results/*.csv
python -m choke_ipm.discover_models                  # find Choke codes / Data[] indices in PROSPER
```

Files: `config.py` (settings) · `models.py` (model registry) · `data_prep.py` · `prosper_runner.py`
· `metrics.py` · `plots.py` · `run.py`.

**Before first real run:** `IPM_var.txt` lists tag names only. The `code` of each model and the
`data_index` of extra inputs in `models.py` must be verified/filled (ELF=0, Petroleum Experts=4 are
taken from the old notebook; optional models are `None`). Use `discover_models`.
Output goes to `results/` (plots in `results/plots/`).
