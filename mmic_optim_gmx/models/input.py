from mmelemental.models.base import ProtoModel #Is this line necessary?
from mmelemental.models.proc.base import ProcInput
from mmic_optim.models import OptimInput
from pydantic import Field


class GmxComputeInput(ProcInput):
    proc_input: OptimInput = Field(..., description="Procedure input schema.")
    mdp_file: str = Field(..., description="The file used for specifying the parameters. Should be a .mdp file.")
    struct_file: str = Field(..., description="The file of the system structure. Should be a .top file.")
