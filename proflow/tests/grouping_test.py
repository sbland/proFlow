from proflow.grouping import group
from proflow.Objects import I, Process


def test_can_group_processes():
    demo_processes = [
        Process(
            func=lambda x: x + 1,
            comment="A demo process A",
            config_inputs=[
                I('a', as_='x'),
            ],
            state_outputs=[
                I('_result', as_='y'),
            ]
        ),
        Process(
            func=lambda x: x + 1,
            comment="A demo process B",
            config_inputs=[
                I('y', as_='x'),
            ],
            state_outputs=[
                I('_result', as_='b'),
            ]
        ),
    ]
    grouped_processes = group('group a')(lambda: demo_processes)()
    assert len(grouped_processes) == len(demo_processes)
    assert all([p.group == 'group a' for p in grouped_processes])
