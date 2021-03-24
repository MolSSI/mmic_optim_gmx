from mmelemental.models.base import ProtoModel
from pydantic import Field


class GmxComputeInput(ProtoModel):
    proc_input: "ProcInput"
    mdp_file: str = Field(..., description="The file used for specifying the parameters. Should be a .mdp file")
    struct_file: str = Field(..., description="The file of the system structure. Should be a .top file")
