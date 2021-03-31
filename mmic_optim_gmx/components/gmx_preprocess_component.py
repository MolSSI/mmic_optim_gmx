# Import models
from mmelemental.models.util.output import FileOutput
from mmic_optim.models.input import OptimInput
from ..models import GmxComputeInput

# Import components
from mmic_util.components import CmdComponent
from mmic.components.blueprints import SpecificComponent

from typing import List, Tuple, Optional, Set
import os

__all__ = ["GmxPreProcessComponent"]


class GmxPreProcessComponent(SpecificComponent):
    """
    Prepares input for running gmx energy minimization.
    The Molecule object will be converted to a .pdb file here.
    .mdp and .top files will be constructed.
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
        }

        if mdp_inputs["integrator"] == None:
            mdp_inputs["integrator"] = "steep"
        if mdp_inputs["emtol"] == None:
            mdp_inputs["emtol"] = "1000"
        if mdp_inputs["emstep"] == None:
            mdp_inputs["emstep"] = "0.01"  # The unit here is nm
        if mdp_inputs["emstep"] == None:
            mdp_inputs["emstep"] = "0.01"

        # Translate boundary str tuple (perodic,perodic,perodic) to a string e.g. xyz
        pbc_dict = dict(zip(["x", "y", "z"], list(mdp_inputs["pbc"])))

        for dim in list(pbc_dict.keys()):
            if pbc_dict[dim] != "periodic":
                continue
            else:
                pbc = pbc + dim
        mdp_inputs["pbc"] = pbc

        # Write .mdp file
        str = " = "
        with open(mdp_fname, "w") as inp:
            for key, val in mdp_inputs.items():
                inp.write(f"{key} = {val}\n")

        # Get the abspath of .pdbb and .mdp files
        pdb_fname = os.path.abspath(pdb_fname)
        mdp_fname = os.path.abspath(mdp_fname)

        # build pdb2gmx inputs
        fs = inputs.forcefield
        ff_name, ff = list(fs.items()).pop()
        input_model = {
            "pdb_fname": pdb_fname,
            "ff_name": ff_name,
            "engine": inputs.proc_input.engine,
        }

        cmd_input = self.build_input(input_model)
        CmdComponent.compute(cmd_input)

        top_fname = os.path.abspath("topol.top")
        gro_fname = os.path.abspath("conf.gro")

        os.remove(pdb_fname)

        gmx_compute = GmxComputeInput(
            proc_input=inputs,
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

        return {
            "command": [
                inputs["engine"],
                "pdb2gmx",
                "-f",
                pdb_fname,
                "-ff",
                inputs["ff_name"],
                "-water",
                "none",
            ],
            "infiles": [pdb_fname],
            "outfiles": ["conf.gro", "topol.top", "posre.itp"],
            "scratch_directory": scratch_directory,
            "environment": env,
        }
