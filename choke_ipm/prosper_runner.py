"""Run choke models in PROSPER through OpenServer (Windows + PROSPER only)."""
import numpy as np
import pandas as pd

from .data_prep import INPUT_COLS, usable_rows
from .models import (COMMON_INPUT_TAGS, METHOD_PREDICT_RATE, OUTPUT_TAGS, TAG_CALC,
                     TAG_CHOKE_MODEL, TAG_METHOD, ChokeModel)

EMPTY = 1e30   # PROSPER returns ~3.4e35 for "empty"


def _start_session(prosper_file: str, pvt: dict):
    from openserver import OpenServer          # imported lazily: only exists with PROSPER
    c = OpenServer()
    c.connect()
    c.DoCmd("PROSPER.START()")
    c.DoCmd(f'PROSPER.OPENFILE("{prosper_file}")')
    for tag, value in pvt.items():
        c.DoSet(tag, float(value))
    return c


def _select_model(c, model: ChokeModel, extra_values: dict):
    if model.code is None:
        raise ValueError(f"Model {model.name} has no PROSPER code in models.py")
    c.DoSet(TAG_METHOD, METHOD_PREDICT_RATE)
    c.DoSet(TAG_CHOKE_MODEL, model.code)
    for extra in model.extra_inputs:
        c.DoSet(extra.tag, float(extra_values[extra.name]))


def run_model(well_df: pd.DataFrame, model: ChokeModel, extra_values: dict,
              prosper_file: str, pvt: dict) -> pd.DataFrame:
    """Return well_df with `<model>_Liquid` and `<model>_Mass` columns."""
    out = well_df.copy()
    liq, mass = f"{model.name}_Liquid", f"{model.name}_Mass"
    out[liq] = np.nan
    out[mass] = np.nan
    ok = usable_rows(out)

    def start():
        c = _start_session(prosper_file, pvt)
        _select_model(c, model, extra_values)
        return c

    c = start()
    try:
        for idx in out.index[ok]:
            try:
                for key in INPUT_COLS:
                    c.DoSet(COMMON_INPUT_TAGS[key], float(out.at[idx, key]))
                c.DoCmd(TAG_CALC)
                for col, key in ((liq, "Liquid_Rate"), (mass, "Mass_Flow")):
                    v = float(c.DoGet(OUTPUT_TAGS[key]))
                    out.at[idx, col] = np.nan if v > EMPTY else v
            except Exception as exc:           # restart the session after a PROSPER error
                print(f"  [{model.name}] row {idx}: {exc}")
                try:
                    c.disconnect()
                except Exception:
                    pass
                c = start()
    finally:
        try:
            c.disconnect()
        except Exception:
            pass
    return out
