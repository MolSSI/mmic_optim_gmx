from mmelemental.models.base import ProtoModel


class GmxComputeOutput(ProtoModel):
    proc_input: "ProcInput"
    molecule: str
    trajectory: str