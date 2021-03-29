from mmelemental.models.base import ProtoModel


class GmxComputeOutput(ProtoModel):
    proc_input: OptimInput = Field(..., description="Procedure input schema.")
    molecule: str = Field(..., description="File name of the molecule file")
    trajectory: str = Field(..., description="File name of the trajectory file")