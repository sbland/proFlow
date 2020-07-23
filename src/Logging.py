from typing import List
from .Objects import Process, I


def logger_add_row_process() -> Process:
    return Process(
        func=lambda logs: logs + [{}],
        state_inputs=[
            I('logs', as_='logs'),
        ],
        state_outputs=[I('_result', as_='logs')]
    )


def log_values(row_id: int, state_inputs: List[I], additional_inputs: List[I] = []):
    return Process(
        func=lambda logs, index, **kwargs: {**logs[index], **kwargs},
        state_inputs=[
            I('logs', as_='logs'),
        ] + state_inputs,
        additional_inputs=[
            I('index', row_id),
        ] + additional_inputs,
        state_outputs=[I('_result', as_=f'logs.{row_id}')]
    )
