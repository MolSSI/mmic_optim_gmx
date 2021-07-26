# from mmelemental.models.base import ProtoModel
from cmselemental.models.base import ProtoModel
from mmic_optim.models import OptimInput
from pydantic import Field


__all__ = ["ComputeGmxOutput"]


class ComputeGmxOutput(ProtoModel):
    proc_input: OptimInput = Field(..., description="Procedure input schema.")
    molecule: str = Field(..., description="Molecule file string object")
    trajectory: str = Field(..., description="Trajectory file string object.")
    scratch_dir: str = Field(
        ..., description="The dir containing the traj file and the mold file"
    )
