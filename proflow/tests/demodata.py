from proflow.Objects import Process, I

DEMO_PROCESSES = [

    Process(
        func=lambda x, y, z: x + y + z,
        comment="Demo process a",
        config_inputs=[
            I('foo.bar', as_='x'),
        ],
        state_inputs=[
            I('info.today', as_='y'),
            I('info.hour', as_='z')
        ],
        state_outputs=[
            I('_result', as_='info.tomorrow'),
        ]
    ),
    Process(
        func=lambda x, y: x + y,
        comment="Demo process b",
        config_inputs=[
            I('foo.bar', as_='x'),
        ],
        state_inputs=[
            I('info.tomorrow', as_='y'),
        ],
        state_outputs=[
            I('_result', as_='info.today'),
        ]
    ),
    Process(
        func=lambda x, y: x + y,
        comment="Demo process c",
        config_inputs=[
            I('foo.bar', as_='x'),
        ],
        state_inputs=[
            I('info.tomorrow', as_='y'),
        ],
        state_outputs=[
            I('_result', as_='info.today'),
        ]
    ),
    Process(
        func=lambda x, y: x + y,
        comment="Demo process d",
        config_inputs=[
            I('foo.bar', as_='x'),
        ],
        state_inputs=[
            I('info.today', as_='y'),
        ],
        state_outputs=[
            I('_result', as_='info.tomorrow'),
        ]
    ),
]
