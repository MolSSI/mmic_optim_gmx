# Import models
from mmelemental.models.util.output import FileOutput
from mmelemental.models import Molecule, Trajectory
from ..models import GmxComputeInput, GmxComputeOutput

# Import components
from mmic_util.components import CmdComponent
from mmic.components.blueprints import SpecificComponent

from typing import Dict, Any, List, Tuple, Optional
import os


class GmxComputeComponent(SpecificComponent):
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
        if isinstance(inputs, dict):
            inputs = self.input()(**inputs)

        mdp_fname, gro_fname, top_fname = (
            inputs.mdp_file,
            inputs.coord_file,
            inputs.struct_file,
        )
        tpr_fname = "em.tpr"
        assert os.path.exists(mdp_fname), "No .mdp file found"
        assert os.path.exists(gro_fname), "No .gro file found"
        assert os.path.exists(top_fname), "No .top file found"

        # mol = os.path.abspath('mdp_fname') + "/minimized_struct"  # path to output structure file, minimized
        # traj = os.path.abspath('mdp_fname') + "/traj"  # path to output traj file
        # Is Gromacs able to output files to specific locations?

        input_model = {
            "mdp_fname": mdp_fname,
            "gro_fname": gro_fname,
            "top_fname": top_fname,
            "engine": inputs.proc_input.engine,
            "tpr_fname": tpr_fname,
        }

        cmd_input_grompp = self.build_input(input_model)
        CmdComponent.compute(cmd_input_grompp)

        tpr_fname = os.path.abspath(tpr_fname)

        cmd_input_mdrun = {
            "command": [
                inputs.proc_input.engine,
                "mdrun",
                "-s",
                tpr_fname,
                "-deffnm",
                "em",
            ],
            "outfiles": ["em.trr", "em.gro"],
        }
        CmdComponent.compute(cmd_input_mdrun)

        # clean_files = [mdp_fname, gro_fname, tpr_fname, "mdout.mdp"]
        cwd = os.getcwd()
        f_path = os.listdir(cwd)
        for i in f_path:
            if os.path.splitext(i)[1] in {
                ".log",
                ".tpr",
                ".pdb",
                ".mdp",
                ".edr",
                ".err",
            }:
                clean_files.append(i)

        self.cleanup(clean_files)

        mol = os.path.abspath("em.gro")
        traj = os.path.abspath("em.trr")

        return True, GmxComputeOutput(
            proc_input=inputs.proc_input,
            molecule=mol,
            trajectory=traj,
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
        """
        Build the input for grompp
        """
        assert inputs["engine"] == "gmx", "Engine must be gmx (Gromacs)!"

        tpr_fname = inputs["tpr_fname"]

        # Is this part necessary?
        env = os.environ.copy()

        if config:
            env["MKL_NUM_THREADS"] = str(config.ncores)
            env["OMP_NUM_THREADS"] = str(config.ncores)

        scratch_directory = config.scratch_directory if config else None

        return {
            "command": [
                inputs["engine"],
                "grompp",
                "-v -f",
                inouts["mdp_fname"],
                "-c",
                inputs["gro_fname"],
                "-p",
                inputs["top_fname"],
                "-o",
                tpr_fname,
            ],
            "outfiles": [tpr_fname],
            "scratch_directory": scratch_directory,
            "environment": env,
        }
