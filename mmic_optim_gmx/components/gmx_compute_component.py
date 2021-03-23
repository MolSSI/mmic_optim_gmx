# Import models
from mmelemental.models.util.output import FileOutput
from mmelemental.models import Molecule, Trajectory
from ..models import GmxComputeInput, GmxComputeOutput

# Import components
from mmic.components.blueprints import SpecificComponent

from typing import Dict, Any, List, Tuple, Optional


class PostComponent(SpecificComponent):
    @classmethod
    def input(cls):
        return GmxComputeInput

    @classmethod
    def output(cls):
        return GmxComputeOutput

    def execute(
        self,
        inputs: GmxComputeOutput,
        extra_outfiles: Optional[List[str]] = None,
        extra_commands: Optional[List[str]] = None,
        scratch_name: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Tuple[bool, GmxComputeOutput]:

        # Call gmx pdb2gmx, mdrun, etc. here

        mol = ...  # path to output structure file, minimized
        traj = ...  # path to output traj file

        return True, GmxComputeOutput(
            proc_input=inputs.proc_input,
            molecule=mol,
            trajectory=traj,
        )
