
from typing import Callable, List

from .internal_state import Model_State_Shape
from .Objects import I, Process


def merge_logs(logs, index, **kwargs):
    if index < len(logs):
        return {**logs[index], **kwargs}
    else:
        return {**kwargs}


def log_values(
    state_inputs: Callable[[Model_State_Shape], List[I]],
    additional_inputs: Callable[[List[I]], None] = lambda: []
):
    return Process(
        func=merge_logs,
        comment="Logging Values",
        state_inputs=lambda state: [
            I(state.temporal.row_index, 'index'),
            I(state.logs, as_='logs'),
        ] + state_inputs(state),
        additional_inputs=lambda: additional_inputs(),
        state_outputs=[I('_result', as_='logs.+')]
    )


# TODO: Implement adding row approach
def logger_add_row() -> Process:
    raise DeprecationWarning()
    return Process(
        func=lambda logs: logs + [{}],
        comment="Adding row to logs",
        state_inputs=lambda state: [
            I(state.logs, as_='logs'),
        ],
        state_outputs=[I('_result', as_='logs')]
    )
