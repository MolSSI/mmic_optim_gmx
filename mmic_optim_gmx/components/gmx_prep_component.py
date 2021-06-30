# Import models
from mmic_optim.models.input import OptimInput
from mmic_optim_gmx.models import ComputeGmxInput
from mmelemental.util.files import random_file

# Import components
from mmic_cmd.components import CmdComponent
from mmic.components.blueprints import GenericComponent

from typing import Any, Dict, List, Tuple, Optional
import os

__all__ = ["PrepGmxComponent"]
_supported_solvents = ("spc", "tip3p", "tip4p")


class PrepGmxComponent(GenericComponent):
    """
    Prepares input for running gmx energy minimization.
    The Molecule object from MMIC schema will be
    converted to a .pdb file here.
    .mdp and .top files will also be constructed
    according to the info in MMIC schema.
    """

    @classmethod
    def input(cls):
        return OptimInput

    @classmethod
    def output(cls):
        return ComputeGmxInput

    def execute(
        self,
        inputs: OptimInput,
        extra_outfiles: Optional[List[str]] = None,
        extra_commands: Optional[List[str]] = None,
        scratch_name: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Tuple[bool, ComputeGmxInput]:

        if isinstance(inputs, dict):
            inputs = self.input()(**inputs)

        mdp_inputs = {
            "integrator": inputs.method,
            "emtol": inputs.tol,
            "emstep": inputs.step_size,
            "nsteps": inputs.max_steps,
            "pbc": inputs.boundary,
            "vdwtype": inputs.short_forces.method,
            "coulombtype": inputs.long_forces.method,
        }

        # The following part is ugly and may be
        # improved in the future
        # Translate the method
        if "steep" in mdp_inputs["integrator"]:
            mdp_inputs["integrator"] = "steep"
        if "conjugate" in mdp_inputs["integrator"]:
            mdp_inputs["integrator"] = "cg"

        if mdp_inputs["integrator"] is None:
            mdp_inputs["integrator"] = "steep"
        if mdp_inputs["emtol"] is None:
            mdp_inputs["emtol"] = "1000"
        if mdp_inputs["emstep"] is None:
            mdp_inputs["emstep"] = "0.01"  # The unit here is nm
        if mdp_inputs["emstep"] is None:
            mdp_inputs["emstep"] = "0.01"
        # if mdp_inputs["cutoff-scheme"] is None:
        #    mdp_inputs["cutoff-scheme"] = "Verlet"
        if mdp_inputs["coulombtype"] is None:
            mdp_inputs["coulombtype"] = "PME"

        # Translate boundary str tuple (perodic,perodic,perodic) to a string e.g. xyz
        pbc_dict = dict(zip(["x", "y", "z"], list(mdp_inputs["pbc"])))
        pbc = ""
        for dim in list(pbc_dict.keys()):
            if pbc_dict[dim] != "periodic":
                continue
            else:
                pbc = pbc + dim  # pbc is a str, may need to be initiated elsewhere
        mdp_inputs["pbc"] = pbc

        # Write .mdp file
        mdp_file = random_file(suffix=".mdp")
        with open(mdp_file, "w") as inp:
            for key, val in mdp_inputs.items():
                inp.write(f"{key} = {val}\n")

        fs = inputs.forcefield
        mols = inputs.molecule

        ff_name, ff = list(
            fs.items()
        ).pop()  # Here ff_name gets actually the related mol name, but it will not be used
        mol_name, mol = list(mols.items()).pop()

        gro_file = random_file(suffix=".gro")  # output gro
        top_file = random_file(suffix=".top")
        boxed_gro_file = random_file(suffix=".gro")

        mol.to_file(gro_file, translator="mmic_parmed")
        ff.to_file(top_file, translator="mmic_parmed")

        input_model = {
            "gro_file": gro_file,
            "proc_input": inputs,
            "boxed_gro_file": boxed_gro_file,
        }
        clean_files, cmd_input = self.build_input(input_model)
        rvalue = CmdComponent.compute(cmd_input)
        boxed_gro_file = str(rvalue.outfiles[boxed_gro_file])
        scratch_dir = str(rvalue.scratch_directory)
        self.cleanup(clean_files)  # Del the gro in the working dir

        gmx_compute = ComputeGmxInput(
            proc_input=inputs,
            mdp_file=mdp_file,
            forcefield=top_file,
            molecule=boxed_gro_file,
            scratch_dir=scratch_dir,
        )

        return True, gmx_compute

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

        assert inputs["proc_input"].engine == "gmx", "Engine must be gmx (Gromacs)!"
        clean_files = []

        boxed_gro_file = inputs["boxed_gro_file"]
        clean_files.append(inputs["gro_file"])

        env = os.environ.copy()

        if config:
            env["MKL_NUM_THREADS"] = str(config.ncores)
            env["OMP_NUM_THREADS"] = str(config.ncores)

        scratch_directory = config.scratch_directory if config else None

        cmd = [
            inputs["proc_input"].engine,
            "editconf",
            "-f",
            inputs["gro_file"],
            "-d",
            "2",
            "-o",
            boxed_gro_file,
        ]
        outfiles = [boxed_gro_file]

        return clean_files, {
            "command": cmd,
            "infiles": [inputs["gro_file"]],
            "outfiles": outfiles,
            "outfiles_track": outfiles,
            "scratch_directory": scratch_directory,
            "environment": env,
            "scratch_messy": True,
        }
