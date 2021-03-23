# Import models
from mmic_optim.models.input import OptimInput
from ..models import GmxComputeInput

# Import components
from mmic.components.blueprints import SpecificComponent

from typing import List, Tuple, Optional, Set


__all__ = ["GmxPreProcessComponent"]


class GmxPreProcessComponent(SpecificComponent):
    """
    Prepares input for running gmx energy minimization.
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

        # Parse GMX input params from inputs and create GmxComputeInput object
        gmx_compute = GmxComputeInput(inputs=..., ...)
        return True, GmxComputeInput(**gmx_compute)
