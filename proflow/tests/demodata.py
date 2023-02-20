from proflow.Objects.Interface import I
from proflow.Objects.Process import Process

DEMO_PROCESSES = [
    Process(
        func=lambda x, y, z: x + y + z,
        comment="Demo process a",
        config_inputs=lambda config: [
            I(config.foo.bar, as_='x'),
        ],
        state_inputs=lambda state: [
            I(state.info.today, as_='y'),
            I(state.info.hour, as_='z')
        ],
        state_outputs=lambda result: [
            (result, 'info.tomorrow'),
        ]
    ),
    Process(
        func=lambda x, y: x + y,
        comment="Demo process b",
        config_inputs=lambda config: [
            I(config.foo.bar, as_='x'),
        ],
        state_inputs=lambda state: [
            I(state.info.tomorrow, as_='y'),
        ],
        state_outputs=lambda result: [
            (result, 'info.today'),
        ]
    ),
    Process(
        func=lambda x, y: x + y,
        comment="Demo process c",
        config_inputs=lambda config: [
            I(config.foo.bar, as_='x'),
        ],
        state_inputs=lambda state: [
            I(state.info.tomorrow, as_='y'),
        ],
        state_outputs=lambda result: [
            (result, 'info.today'),
        ]
    ),
    Process(
        func=lambda x, y: x + y,
        comment="Demo process d",
        config_inputs=lambda config: [
            I(config.foo.bar, as_='x'),
        ],
        state_inputs=lambda state: [
            I(state.info.today, as_='y'),
        ],
        state_outputs=lambda result: [
            (result, 'info.tomorrow'),
        ]
    ),
]
