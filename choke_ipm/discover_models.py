"""Helper (run on the PROSPER machine): find which Choke code and Data[] indices
respond, so models.py can be filled in. Prints the non-empty Data[] values per code."""
from . import config as cfg
from .models import TAG_CALC, TAG_CHOKE_MODEL, TAG_METHOD
from .prosper_runner import EMPTY, _start_session

SAMPLE = {0: 1191.0, 1: 204.8, 2: 866.0, 4: 0.625, 16: 1596.0, 17: 0.16}


def main(max_code: int = 15):
    c = _start_session(cfg.PROSPER_FILE, cfg.PVT)
    try:
        for code in range(max_code + 1):
            try:
                c.DoSet(TAG_METHOD, 0)
                c.DoSet(TAG_CHOKE_MODEL, code)
                for i, v in SAMPLE.items():
                    c.DoSet(f"Prosper.ANL.CHK.Data[{i}]", v)
                c.DoCmd(TAG_CALC)
                vals = {i: float(c.DoGet(f"Prosper.ANL.CHK.Data[{i}]")) for i in range(29)}
                print(f"code {code}:", {i: round(v, 3) for i, v in vals.items() if abs(v) < EMPTY})
            except Exception as exc:
                print(f"code {code}: error {exc}")
    finally:
        c.disconnect()


if __name__ == "__main__":
    main()
