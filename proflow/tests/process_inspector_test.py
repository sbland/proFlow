"""Tests for the process inspector."""


from proflow.process_inspector import inspect_process_inputs
from proflow.Objects import I, Process


def test_inspect_process_inputs(snapshot):
    def test_func(x, y, z):
        return x + y + z

    demo_process = Process(
        func=test_func,
        comment="This is the process comment",
        gate=True,
        config_inputs=lambda config: [
            I(config.a, as_='x'),
        ],
        state_inputs=lambda state: [
            I(state.a, as_='y'),
        ],
        additional_inputs=lambda: [
            I(10, as_='z'),
        ],
        state_outputs=[
            I('_result', as_='x'),
        ]
    )
    process_inputs = inspect_process_inputs(demo_process)
    snapshot.assert_match(process_inputs, 'process_inputs')


def test_inspect_process_inputs_empty(snapshot):
    def test_func(x, y, z):
        return x + y + z

    demo_process = Process(
        func=test_func,
        comment="This is the process comment",
        gate=True,
        config_inputs=lambda config: [
        ],
        state_inputs=lambda state: [
        ],
        additional_inputs=lambda: [
        ],
        state_outputs=[
            I('_result', as_='x'),
        ]
    )
    process_inputs = inspect_process_inputs(demo_process)
    snapshot.assert_match(process_inputs, 'process_inputs')
