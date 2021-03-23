from mmelemental.models.base import ProtoModel


class GmxComputeInput(ProtoModel):
    proc_input: "ProcInput"
    mdp_file: str
    struct_file: str
