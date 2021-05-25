from mmelemental.models.base import ProtoModel
from mmic_optim.models import OptimInput
from pydantic import Field

__all__ = ["GmxComputeOutput"]


class GmxComputeOutput(ProtoModel):
    proc_input: OptimInput = Field(..., description="Procedure input schema.")
    molecule: str = Field(..., description="Molecule file string object")
    trajectory: str = Field(..., description="Trajectory file string object.")
