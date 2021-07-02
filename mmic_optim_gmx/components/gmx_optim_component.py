# Import schema models for energy optim
from mmic_optim.models import OptimInput, OptimOutput

# Import subcomponents for running energy min with GMX
from .gmx_prep_component import PrepGmxComponent
from .gmx_compute_component import ComputeGmxComponent
from .gmx_post_component import PostGmxComponent

from mmic.components.blueprints import TacticComponent
from typing import Optional, Tuple, List, Any

__all__ = ["OptimGmxComponent"]


class OptimGmxComponent(TacticComponent):
    """Main entry component for running FF assignment."""

    @classmethod
    def input(cls):
        return OptimInput

    @classmethod
    def output(cls):
        return OptimOutput

    def execute(
        self,
        inputs: OptimInput,
        extra_outfiles: Optional[List[str]] = None,
        extra_commands: Optional[List[str]] = None,
        scratch_name: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Tuple[bool, OptimOutput]:

        computeInput = PrepGmxComponent.compute(inputs)
        computeOutput = ComputeGmxComponent.compute(computeInput)
        optimOutput = PostGmxComponent.compute(computeOutput)
        return True, optimOutput

    def get_version(cls) -> str:
        """Finds program, extracts version, returns normalized version string.
        Returns
        -------
        str
            Return a valid, safe python version string.
        """
        raise NotImplementedError

    @classmethod
    def strategy_comp(cls) -> Any:
        """Returns the strategy component this (tactic) component belongs to.
        Returns
        -------
        Any
        """
        return set(mmic_optim.components.OptimComponent)
