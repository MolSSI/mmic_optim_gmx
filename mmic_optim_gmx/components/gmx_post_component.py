# Import models
from mmic_optim.models.output import OptimOutput
from mmelemental.models import Molecule, Trajectory
from ..models import GmxComputeOutput

# Import components
from mmic.components.blueprints import SpecificComponent

from typing import Dict, Any, List, Tuple, Optional


class PostComponent(SpecificComponent):
    @classmethod
    def input(cls):
        return GmxComputeOutput

    @classmethod
    def output(cls):
        return OptimOutput

    def execute(
        self,
        inputs: GmxComputeOutput,
        extra_outfiles: Optional[List[str]] = None,
        extra_commands: Optional[List[str]] = None,
        scratch_name: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Tuple[bool, OptimOutput]:

        # get trajs from traj output file
        traj_file = inputs.trajectory  # split trajs into multiple files
        trajs_files = ...
        traj = {
            key: Trajectory.from_file(trajs_files[key])
            for key in inputs.proc_input.trajectory
        }

        # get mols from parsing struct output file
        mol_file = inputs.molecule  # split mols into multiple files
        mols_files = ...
        mol = {
            key: Molecule.from_file(mols_files[key]) for key in inputs.proc_input.mol
        }

        return True, OptimOutput(procInput=inputs.input, molecule=mol, trajectory=traj)
