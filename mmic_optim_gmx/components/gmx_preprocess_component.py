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
        
        mols = inputs.molecule #Dict[str, Molecule]
        pdb_fname = "GMX_pre.pdb"
        
        for mol_name in mols.keys():
            mols[mol_name].to_file(file_name = pdb_fname,
                                   mode = "a"
                                  )#Molecule.to_file. Mode is "a" to add to the end of pdb file
        
        mdp_fname = "em.mdp"
        mdp_inputs = {"integrator":inputs.method, 
                      "emtol":inouts.tol,
                      "emstep":inputs.step_size,
                      "nsteps":inputs.max_steps,
                      "pbc":inputs.boundary
                     }
        
        if (mdp_inputs["integrator"] == None) : mdp_inputs["integrator"] = "steep"
        if (mdp_inputs["emtol"] == None) : mdp_inputs["emtol"] = "1000"
        if (mdp_inputs["emstep"] == None) : mdp_inputs["emstep"] = "0.01" #The unit here is nm
        if (mdp_inputs["emstep"] == None) : mdp_inputs["emstep"] = "0.01"
        
        #Translate boundary str tuple to a string e.g. xy
        pbc_dict = dict(zip(["x","y","z"],list(mdp_inputs["pbc"])))
        
        for dim in list(pbc_dict.keys()):
            if pbc_dict[dim] != "periodic":
                continue
            else:
                pbc = pbc + dim
                
        mdp_inputs["pbc"] = pbc
         
        #Write .mdp file
        str = " = "
        with open(pdb_fname, 'w') as inp:
            for i in range(0,len(list(list(mdp_inputs.items())))):
                par = list(list(mdp_input.items())[i])
                inp.write(str.join(par+"\n")
                          
        #build pdb2gmx inputs
        fs = inputs.forcefield
        ff_name, ff = list(fs.items()).pop()
        input_model =  {"pdb_fname":pdb_fname, "ff_name":ff_name, "engine":"gmx"}
                          
        cmd_input = self.build_input(input_model)
        CmdComponent.compute(cmd_input)                  
            
        # Parse GMX input params from inputs and create GmxComputeInput object
        gmx_compute = GmxComputeInput(
            proc_input=inputs,
            mdp_file=mdp_fname,
            struct_file="topol.top"
            coord_file="conf.gro"
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
        """
                      
        #assert inputs["engine"] == "gmx", "Engine must be gmx (Gromacs)!"
        
        with FileOutput(path=pdb_fname) as fp:                       
            pdb_fpath = fp.abs_path
         
        #Is this part necessary?
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
                pdb_fpath,
                "-ff",
                inputs["ff_name"],
                "-water",
                "none",
            ],
            "infiles": [pdb_fpath],
            "outfiles": ["conf.gro", "topol.top", "posre.itp"],
            "scratch_directory": scratch_directory,
            "environment": env,
        }

