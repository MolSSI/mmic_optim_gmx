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
        mols.to_file(pdb_fname)
        
        mdp_fname = "em.mdp"
        
        # Parse GMX input params from inputs and create GmxComputeInput object
        gmx_compute = GmxComputeInput(
            proc_input=inputs,
            mdp_file=...,
            struct_file=...
        )
                      
        return True, GmxComputeInput(**gmx_compute)
    
    def build_input(
        self,
        inputs: Dict[str, Any],
        pdb_fname: str,
        config: Optional["TaskConfig"] = None,
        template: Optional[str] = None,
    ) -> Dict[str, Any]:
        
        assert inputs["engine"] == "gmx", "Engine must be gmx (Gromacs)!"
        
