# Import models
from mmic_optim.models.input import OptimInput
from mmic_optim_gmx.models import GmxComputeInput
from mmelemental.models.util import FileOutput
from mmelemental.util.files import random_file

# Import components
from mmic_cmd.components import CmdComponent
from mmic.components.blueprints import GenericComponent

from typing import Any, Dict, List, Tuple, Optional, Set
import os

__all__ = ["GmxPreProcessComponent"]
_supported_solvents = ("spc", "tip3p", "tip4p")


class GmxPreProcessComponent(GenericComponent):
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
        return GmxComputeInput

    def execute(
        self,
        inputs: OptimInput,
        extra_outfiles: Optional[List[str]] = None,
        extra_commands: Optional[List[str]] = None,
        scratch_name: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Tuple[bool, GmxComputeInput]:

        if isinstance(inputs, dict):
            inputs = self.input()(**inputs)

        mdp_inputs = {
            "integrator": inputs.method,
            "emtol": inputs.tol,
            "emstep": inputs.step_size,
            "nsteps": inputs.max_steps,
            "pbc": inputs.boundary,
            "cut_off": inputs.cut_off,
            "coulomb_type": inputs.coulomb_type,
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
        if mdp_inputs["cut_off"] is None:
            mdp_inputs["cut_off"] = "Verlet"
        if mdp_inputs["coulomb_type"] is None:
            mdp_inputs["coulomb_type"] = "PME"

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

        ff_name, ff = list(fs.items()).pop()  # Here ff_name gets actually the related mol name, but it will not be used
        mol_name, mol = list(mols.items()).pop()

        gro_file = random_file(suffix=".gro")  # output gro
        top_file = random_file(suffix=".top")

        mol.to_file(gro_file)
        ff.to_file(top_file)

        gmx_compute = GmxComputeInput(
            proc_input=inputs,
            mdp_file=mdp_file,
            forcefield=top_file,
            molecule=gro_file,
        )

        return True, gmx_compute


"""
    def build_input(
        self,
        inputs: Dict[str, Any],
        pdb_fname: str,
        config: Optional["TaskConfig"] = None,
        template: Optional[str] = None,
    ) -> Dict[str, Any]:
 
        assert inputs["proc_input"].engine == "gmx", "Engine must be gmx (Gromacs)!"#inputs["proc_input"].engine = OptimInput.engine
        clean_files = []

        #for key in inputs["proc_input"].molecule.keys():# OptimInput.molecule.keys()
        #    inputs["proc_input"].molecule[key].to_file(
        #        file_name=fname, mode="a"
        #        )

        clean_files.append(inputs["gro_file"])
        clean_files.append(inputs["mdp_file"])

        env = os.environ.copy()

        if config:
            env["MKL_NUM_THREADS"] = str(config.ncores)
            env["OMP_NUM_THREADS"] = str(config.ncores)

        scratch_directory = config.scratch_directory if config else None

        tpr_file = random_file(suffix=".tpr")

        cmd = [
            inputs["proc_input"].engine,
            "grompp",
            "-v -f",
            inputs["mdp_file"],
            "-c",
            inputs["gro_file"],
            "-p",
            inputs["top_file"],
            "-o",
            tpr_file,
        ]
        outfiles = [tpr_file]        

        # For extra args
        if inputs["proc_input"].kwargs:
            for key, val in inputs["proc_input"].kwargs.items():
                if val:
                    cmd.extend([key, val])
                else:
                    cmd.extend([key])        

        return clean_files, {
            "command": cmd,
            "infiles": [inputs["mdp_file"], inputs["gro_file"]],
            "outfiles": outfiles,
            "outfiles_load": True,
            "scratch_directory": scratch_directory,
            "environment": env,
        }

    def parse_output(
        self, mdp_file: str, output: Dict[str, str], inputs: Dict[str, Any]
        ) -> GmxComputeInput
        stdout = output["stdout"]
        stderr = output["stderr"]
        outfiles = output["outfiles"]

        if len(outfiles) == 3: # gro top itp
            conf, top, _ = outfiles.values()  # posre = outfiles["posre.itp"]
        elif len(outfiles) == 2:# gro top
            conf, top = outfiles.values()
        else:
            raise ValueError(
                "The number of output files should be either 2 (.gro, .top) or 3 (.gro, .top, .itp)"
            )

        return self.output()(
            mdp_file = mdp_file,
            proc_input=inputs,
            molecule=conf,
            forcefield=top,
            stdout=stdout,
            stderr=stderr,
        )
"""
