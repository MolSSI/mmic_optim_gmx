# from mmelemental.models.base import ProtoModel  # Is this line necessary?
from mmelemental.models.proc.base import ProcInput
from mmic_optim.models import OptimInput
from pydantic import Field

__all__ = ["GmxComputeInput"]


class GmxComputeInput(ProcInput):
    proc_input: OptimInput = Field(..., description="Procedure input schema.")
    mdp_file: str = Field(
        ...,
        description="The file used for specifying the parameters. Should be a .mdp file.",
    )
    forcefield: str = Field(
        ..., description="The file of the system structure. Should be a .top file."
    )
    molecule: str = Field(
        ...,
        description="The file of the coordinates of the atoms in the system. Should be a .gro file.",
    )
    
    scratch_dir: str = Field(
        ...,
        description="The path to the directory where the temporary files are written. Generally it's a directory in /tmp"
    )
