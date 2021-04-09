# Import models
from mmic_optim.models.input import OptimInput
from ..models import GmxComputeInput

# Import components
from mmic_util.components import CmdComponent
from mmic.components.blueprints import SpecificComponent

from typing import List, Tuple, Optional, Set
import os

__all__ = ["GmxPreProcessComponent"]
_supported_solvents = ("spc", "tip3p", "tip4p")


class GmxPreProcessComponent(SpecificComponent):
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

        mols = inputs.molecule  # Dict[str, Molecule]
        pdb_fname = "GMX_pre.pdb"

        # Write the .pdb file
        for mol_name in mols.keys():
            mols[mol_name].to_file(
                file_name=pdb_fname, mode="a"
            )  # Molecule.to_file. Mode is "a" to add to the end of pdb file

        mdp_fname = "em.mdp"
        mdp_inputs = {
            "integrator": inputs.method,
            "emtol": inouts.tol,
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

        if mdp_inputs["integrator"] == None:
            mdp_inputs["integrator"] = "steep"
        if mdp_inputs["emtol"] == None:
            mdp_inputs["emtol"] = "1000"
        if mdp_inputs["emstep"] == None:
            mdp_inputs["emstep"] = "0.01"  # The unit here is nm
        if mdp_inputs["emstep"] == None:
            mdp_inputs["emstep"] = "0.01"
        if mdp_inputs["cut_off"] == None:
            mdp_inputs["cut_off"] = "Verlet"
        if mdp_inputs["coulomb_type"] == None:
            mdp_inputs["coulomb_type"] = "PME"

        # Translate boundary str tuple (perodic,perodic,perodic) to a string e.g. xyz
        pbc_dict = dict(zip(["x", "y", "z"], list(mdp_inputs["pbc"])))

        for dim in list(pbc_dict.keys()):
            if pbc_dict[dim] != "periodic":
                continue
            else:
                pbc = pbc + dim  # pbc is a str, may need to be initiated elsewhere
        mdp_inputs["pbc"] = pbc

        # Write .mdp file
        # str = " = "
        with open(mdp_fname, "w") as inp:
            for key, val in mdp_inputs.items():
                inp.write(f"{key} = {val}\n")

        # Get the abspath of .pdb and .mdp files
        pdb_fname = os.path.abspath(pdb_fname)
        mdp_fname = os.path.abspath(mdp_fname)

        # build pdb2gmx inputs
        fs = inputs.forcefield
        for sol in _supported_solvents:
            if sol in fs:
                sol_ffname = sol
                del fs[sol]
            else:
                sol_ffname = None

        ff_name, ff = list(fs.items()).pop()  # Take the only one left in it
        input_model = {
            "pdb_fname": pdb_fname,
            "ff_name": ff_name,
            "engine": inputs.proc_input.engine,
            "sol_ff": sol_ffname,
        }

        cmd_input = self.build_input(input_model)
        CmdComponent.compute(cmd_input)

        top_fname = os.path.abspath("topol.top")
        gro_fname = os.path.abspath("conf.gro")

        os.remove(pdb_fname)

        gmx_compute = GmxComputeInput(
            proc_input=inputs.proc_input,
            mdp_file=mdp_fname,
            struct_file=top_fname,
            coord_file=gro_fname,
        )

        return True, GmxComputeInput(**gmx_compute)

    def build_input(
        self,
        inputs: Dict[str, Any],
        pdb_fname: str,
        config: Optional["TaskConfig"] = None,
        template: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Build the input for pdb2gmx command to produce .top file

        Parameters
        ----------
        inputs : dict
            The dict of file paths in the command
        pdb_fname : str
            The abspath of the .pdb file
        config : str optional
            Find the scratch file path if necessary
        template : str optional
            NEED TO BE UPDATED
        """

        assert inputs["engine"] == "gmx", "Engine must be gmx (Gromacs)!"

        # Is this part necessary?
        env = os.environ.copy()

        if config:
            env["MKL_NUM_THREADS"] = str(config.ncores)
            env["OMP_NUM_THREADS"] = str(config.ncores)

        scratch_directory = config.scratch_directory if config else None

        if inputs["sol_ff"] == None:
            cmd = [
                inputs["engine"],
                "pdb2gmx",
                "-f",
                pdb_fname,
                "-ff",
                inputs["ff_name"],
                "-water",
                "none",
            ]
        else:
            cmd = [
                inputs["engine"],
                "pdb2gmx",
                "-f",
                pdb_fname,
                "-ff",
                inputs["ff_name"],
                "-water",
                inputs["sol_ff"],
                "-ignh",
            ]

        return {
            "command": cmd,
            "infiles": [pdb_fname],
            "outfiles": ["conf.gro", "topol.top", "posre.itp"],
            "scratch_directory": scratch_directory,
            "environment": env,
        }
