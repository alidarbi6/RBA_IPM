"""Registry of PROSPER choke models.

The tag names come from IPM_var.txt (Prosper.ANL.CHK.Choke / Method / Data[i]).
That file lists tag names only, NOT the numeric code of each model nor the
Data[] index of each extra input. Fill `code` / `data_index` below
(run `python -m choke_ipm.discover_models` on the PROSPER machine to find them).
"""
from dataclasses import dataclass, field

TAG_CHOKE_MODEL = "Prosper.ANL.CHK.Choke"
TAG_METHOD = "Prosper.ANL.CHK.Method"
TAG_CALC = "Prosper.ANL.CHK.CALC"
METHOD_PREDICT_RATE = 0

# Common inputs shared by every model: key -> Prosper tag
COMMON_INPUT_TAGS = {
    "Pin": "Prosper.ANL.CHK.Data[0]",
    "Tin": "Prosper.ANL.CHK.Data[1]",
    "Pout": "Prosper.ANL.CHK.Data[2]",
    "Choke": "Prosper.ANL.CHK.Data[4]",
    "GOR": "Prosper.ANL.CHK.Data[16]",
    "WaterCut": "Prosper.ANL.CHK.Data[17]",
}
# Outputs
OUTPUT_TAGS = {
    "Liquid_Rate": "Prosper.ANL.CHK.Data[5]",
    "Mass_Flow": "Prosper.ANL.CHK.Data[6]",
}


@dataclass
class ExtraInput:
    name: str
    data_index: int | None = None     # Prosper.ANL.CHK.Data[<index>]
    unit: str = ""

    @property
    def tag(self) -> str:
        if self.data_index is None:
            raise ValueError(f"Data index of extra input '{self.name}' is not set in models.py")
        return f"Prosper.ANL.CHK.Data[{self.data_index}]"


@dataclass
class ChokeModel:
    name: str
    label: str
    code: int | None                  # value written to Prosper.ANL.CHK.Choke
    default_on: bool = False
    extra_inputs: list[ExtraInput] = field(default_factory=list)


# ELF / PE codes are taken from the notebook (Choke=4 was the working setting,
# "VALVE=0  # ELF"): VERIFY with discover_models.py before trusting them.
MODELS: dict[str, ChokeModel] = {m.name: m for m in [
    ChokeModel("ELF", "ELF", code=0, default_on=True),
    ChokeModel("PETROLEUM_EXPERTS", "Petroleum Experts", code=4, default_on=True),
    # ---- optional models: set `code` (+ extra inputs' data_index) before enabling
    ChokeModel("GILBERT", "Gilbert", code=None,
               extra_inputs=[ExtraInput("Discharge coefficient", None, "-")]),
    ChokeModel("ROS", "Ros", code=None),
    ChokeModel("BAXENDELL", "Baxendell", code=None),
    ChokeModel("ACHONG", "Achong", code=None),
    ChokeModel("PILEHVARI", "Pilehvari", code=None),
    ChokeModel("OMANA", "Omana", code=None),
]}


def resolve_extra_inputs(model: ChokeModel, supplied: dict, prompt: bool = True) -> dict:
    """Return {input name: value} for a model, asking the user for missing ones."""
    values = dict(supplied.get(model.name, {}))
    for extra in model.extra_inputs:
        if extra.name in values:
            continue
        if not prompt:
            raise ValueError(f"Model {model.name} needs extra input '{extra.name}'")
        values[extra.name] = float(input(f"[{model.label}] enter '{extra.name}' ({extra.unit}): "))
    return values
