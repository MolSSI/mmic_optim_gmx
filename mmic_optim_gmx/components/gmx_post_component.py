# Import models
from mmic_optim.models.output import OptimOutput
from mmelemental.models import Molecule, Trajectory
from ..models import GmxComputeOutput

# Import components
from mmic_util.components import CmdComponent
from mmic.components.blueprints import SpecificComponent

from typing import Dict, Any, List, Tuple, Optional
import os


class GmxPostComponent(SpecificComponent):
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

        clean_files = []
        # get trajs from traj output file
        traj_file = inputs.trajectory  # split trajs into multiple files
        trajs_files = {"em_traj": traj_file}
        traj = {
            key: Trajectory.from_file(trajs_files[key])
            for key in inputs.proc_input.trajectory
        }
        clean_files.append(traj_file)

        # get mols from parsing struct output file
        mol_file = (
            inputs.molecule
        )  # split mols into multiple files. This line might be deleted later
        mol_files = {}  # abspath for split molecules

        # Start to split the gro file by molecules
        for key in inputs.proc_input.molecule:
            input_model = {
                "molname": key,
                "gro_fname": mol_file,  # May be replaced by inputs.molecule
            }
            cmd_input = self.build_input(input_model)
            CmdComponent.compute(cmd_input)
            #CmdComponent.compute(self.build_input(input_model))
            mol_files[key] = os.path.abspath(key + ".gro")
            clean_files.append(mol_files[key])

        mol = {
            key: Molecule.from_file(mols_files[key])
            for key in inputs.proc_input.molecule
        }

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

        def build_input(
            self,
            inputs: Dict[str, Any],
            config: Optional["TaskConfig"] = None,
            template: Optional[str] = None,
        ) -> Dict[str, Any]:

            gro_fname = inputs["gro_fname"]  # The gro file containing all molecules
            mol_fname = inputs["molname"] + ".gro"

            env = os.environ.copy()

            if config:
                env["MKL_NUM_THREADS"] = str(config.ncores)
                env["OMP_NUM_THREADS"] = str(config.ncores)

            scratch_directory = config.scratch_directory if config else None

            return {
                "command": [
                    "grep",
                    "-c",
                    inputs["molname"],
                    gro_fname,
                    ">>",
                    mol_fname,
                    "|",
                    "grep",
                    inputs["molname"],
                    gro_fname,
                    ">>",
                    mol_fname,
                ],
                "outfiles": [mol_fname],
                "scratch_directory": scratch_directory,
                "environment": env,
            }
