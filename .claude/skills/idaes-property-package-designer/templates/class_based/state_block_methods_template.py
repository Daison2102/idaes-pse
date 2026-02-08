"""Template: class-based StateBlock methods."""

from idaes.core import StateBlock
from idaes.core.util.initialization import fix_state_vars, revert_state_vars
from idaes.core.util.model_statistics import degrees_of_freedom
import idaes.logger as idaeslog


class _TemplateStateBlock(StateBlock):
    """Methods applied across indexed state blocks."""

    def initialize(
        blk,
        state_args=None,
        state_vars_fixed=False,
        hold_state=False,
        outlvl=idaeslog.NOTSET,
        solver=None,
        optarg=None,
    ):
        if state_args is None:
            state_args = {}

        if not state_vars_fixed:
            flags = fix_state_vars(blk, state_args)
        else:
            for b in blk.values():
                if degrees_of_freedom(b) != 0:
                    raise RuntimeError("State vars fixed but DOF is not zero.")
            flags = None

        # Add custom staged initialization logic here.

        if not state_vars_fixed and not hold_state:
            blk.release_state(flags)

        if hold_state:
            return flags

    def release_state(blk, flags, outlvl=idaeslog.NOTSET):
        if flags is None:
            return
        revert_state_vars(blk, flags)
