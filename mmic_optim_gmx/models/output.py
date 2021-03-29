from mmelemental.models.base import ProtoModel


class GmxComputeOutput(ProtoModel):
    proc_input: OptimInput = Field(..., description="Procedure input schema.")
    molecule: str = Field(..., description="Trajectory file string object")
    trajectory: str = Field(..., description="Molecule file string object.")