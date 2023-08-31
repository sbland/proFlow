"""Tests associated with the Objects.py file."""

from proflow.Objects.Interface import I
from proflow.Objects.Process import Process


def test_Process_object(snapshot):
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
        state_outputs=lambda result: [
            (result, 'x'),
        ]
    )
    snapshot.assert_match(demo_process, 'demo_process')


def test_process_object_human(snapshot):
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
        state_outputs=lambda result: [
            (result, 'x'),
        ]
    )

    snapshot.assert_match(demo_process.human(), 'demo_process_human')
