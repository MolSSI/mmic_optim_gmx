# Import models
from mmelemental.models.util.output import FileOutput
from mmelemental.models import Molecule, Trajectory
from ..models import GmxComputeInput, GmxComputeOutput

# Import components
from mmic_cmd.components import CmdComponent
from mmelemental.util.files import random_file
from mmic.components.blueprints import GenericComponent

from typing import Dict, Any, List, Tuple, Optional
import os


class GmxComputeComponent(GenericComponent):
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

        proc_input, mdp_file, gro_file, top_file = (
            inputs.proc_input,
            inputs.mdp_file,
            inputs.molecule,
            inputs.forcefield,
        )

        tpr_file = random_file(suffix=".tpr")
        input_model = {
            "proc_input": proc_input,
            "mdp_file": mdp_file,
            "gro_file": gro_file,
            "top_file": top_file,
            "tpr_file": tpr_file,
        }

        clean_files, cmd_input_grompp = self.build_input_grompp(input_model)
        rvalue = CmdComponent.compute(cmd_input_grompp)
        self.cleanup(clean_files)
        tpr_file = str(rvalue.outfiles[tpr_file])
        print(tpr_file)

        input_model = {"proc_input": proc_input, "tpr_file": tpr_file}

        clean_files = []
        clean_files, cmd_input_mdrun = self.build_input_mdrun(input_model)
        rvalue = CmdComponent.compute(cmd_input_mdrun)
        self.cleanup(clean_files)

        return True, self.parse_output(
            rvalue.dict(),
            proc_input,
        )

    @staticmethod
    def cleanup(remove: List[str]):
        for item in remove:
            if os.path.isdir(item):
                shutil.rmtree(item)
            elif os.path.isfile(item):
                os.remove(item)

    def build_input_grompp(
        self,
        inputs: Dict[str, Any],
        config: Optional["TaskConfig"] = None,
        template: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Build the input for grompp
        """
        assert inputs["proc_input"].engine == "gmx", "Engine must be gmx (Gromacs)!"

        env = os.environ.copy()

        if config:
            env["MKL_NUM_THREADS"] = str(config.ncores)
            env["OMP_NUM_THREADS"] = str(config.ncores)

        scratch_directory = config.scratch_directory if config else None

        tpr_file = inputs["tpr_file"]

        clean_files = []
        clean_files.append(inputs["mdp_file"])
        clean_files.append(inputs["gro_file"])
        clean_files.append(inputs["top_file"])

        cmd = [
            inputs["proc_input"].engine,
            "grompp",
            "-f",
            inputs["mdp_file"],
            "-c",
            inputs["gro_file"],
            "-p",
            inputs["top_file"],
            "-o",
            tpr_file,
            "-maxwarn",
            "-1",
        ]
        outfiles = [tpr_file]

        return clean_files, {
            "command": cmd,
            "infiles": [inputs["mdp_file"], inputs["gro_file"], inputs["top_file"]],
            "outfiles": outfiles,
            "outfiles_load": False,
            "scratch_directory": scratch_directory,
            "environment": env,
            "scratch_messy": True,
        }

    def build_input_mdrun(
        self,
        inputs: Dict[str, Any],
        config: Optional["TaskConfig"] = None,
        template: Optional[str] = None,
    ) -> Dict[str, Any]:

        env = os.environ.copy()

        if config:
            env["MKL_NUM_THREADS"] = str(config.ncores)
            env["OMP_NUM_THREADS"] = str(config.ncores)

        scratch_directory = config.scratch_directory if config else None

        clean_files = []

        log_file = random_file(suffix=".log")
        trr_file = random_file(suffix=".trr")
        edr_file = random_file(suffix=".edr")
        gro_file = random_file(suffix=".gro")
        mdp_file = "mdout.mdp"

        clean_files = [log_file, edr_file, mdp_file]

        cmd = [
            inputs["proc_input"].engine,  # Should here be gmx_mpi?
            "mdrun",
            "-s",
            inputs["tpr_file"],
            "-o",
            trr_file,
            "-c",
            gro_file,
            "-e",
            edr_file,
            "-g",
            log_file,
        ]
        outfiles = [trr_file, gro_file]

        # For extra args
        if inputs["proc_input"].kwargs:
            for key, val in inputs["proc_input"].kwargs.items():
                if val:
                    cmd.extend([key, val])
                else:
                    cmd.extend([key])

        return clean_files, {
            "command": cmd,
            "as_binary": [inputs["tpr_file"]],
            "outfiles": outfiles,
            "outfiles_load": False,
            "scratch_directory": scratch_directory,
            "environment": env,
            "scratch_messy": True,
        }

    def parse_output(
        self, output: Dict[str, str], inputs: Dict[str, Any]
    ) -> GmxComputeInput:
        stdout = output["stdout"]
        stderr = output["stderr"]
        outfiles = output["outfiles"]

        traj, conf = outfiles.values()
        traj = str(traj)
        conf = str(conf)
        print(traj)
        print(conf)

        return self.output()(
            proc_input=inputs,
            molecule=conf,
            trajectory=traj,
            # stdout=stdout,
            # stderr=stderr,
        )
