# Import models
from mmic_optim.models.output import OptimOutput
from mmelemental.models import Molecule, Trajectory
from ..models import GmxComputeOutput

# Import components
from mmic_cmd.components import CmdComponent
from mmelemental.util.files import random_file
from mmic.components.blueprints import GenericComponent

from typing import Dict, Any, List, Tuple, Optional
import os


class GmxPostComponent(GenericComponent):
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

        """
        This method translate the output of em
        to mmic schema. But right now it can only
        be applied to single molecule conditions
        """

        clean_files = []

        traj_file = inputs.trajectory  
        traj_name = list(inputs.proc_input.trajectory)[0]
        trajs_files = {traj_name: traj_file}
        traj = {
            key: Trajectory.from_file(trajs_files[key])
            for key in inputs.proc_input.trajectory
        }
        clean_files.append(traj_file)


        mol_file = inputs.molecule
        mol_name = list(inputs.proc_input.molecule)[0]  
        mol_files = {mol_name: mol_file} 
        mol = {
            key: Molecule.from_file(mols_files[key])
            for key in inputs.proc_input.molecule
        }        
        clean_files.append(mol_file)

        self.cleanup(clean_files)


        return True, OptimOutput(
            proc_input=inputs.proc_input, molecule=mol, trajectory=traj
        )

    @staticmethod
    def cleanup(remove: List[str]):
        for item in remove:
            if os.path.isdir(item):
                shutil.rmtree(item)
            elif os.path.isfile(item):
                os.remove(item)


