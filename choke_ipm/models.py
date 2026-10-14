"""The two PROSPER choke models that are compared.

Tag names come from IPM_var.txt (Prosper.ANL.CHK.Choke / Method / Data[i]).
The numeric model codes below come from the old notebook; verify them once with
`python -m choke_ipm.discover_models` on the PROSPER machine.
"""
from dataclasses import dataclass

TAG_CHOKE_MODEL = "Prosper.ANL.CHK.Choke"
TAG_METHOD = "Prosper.ANL.CHK.Method"
TAG_CALC = "Prosper.ANL.CHK.CALC"
METHOD_PREDICT_RATE = 0

# input key -> Prosper tag
COMMON_INPUT_TAGS = {
    "Pin": "Prosper.ANL.CHK.Data[0]",
    "Tin": "Prosper.ANL.CHK.Data[1]",
    "Pout": "Prosper.ANL.CHK.Data[2]",
    "Choke": "Prosper.ANL.CHK.Data[4]",
    "GOR": "Prosper.ANL.CHK.Data[16]",
    "WaterCut": "Prosper.ANL.CHK.Data[17]",
}
OUTPUT_TAGS = {
    "Liquid_Rate": "Prosper.ANL.CHK.Data[5]",
    "Mass_Flow": "Prosper.ANL.CHK.Data[6]",
}


@dataclass(frozen=True)
class ChokeModel:
    name: str
    label: str
    code: int          # value written to Prosper.ANL.CHK.Choke


MODELS: dict[str, ChokeModel] = {m.name: m for m in [
    ChokeModel("ELF", "ELF", code=0),
    ChokeModel("PETROLEUM_EXPERTS", "Petroleum Experts", code=4),
]}
