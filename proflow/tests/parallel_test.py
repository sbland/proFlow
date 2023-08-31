from proflow.Objects.Interface import I
from proflow.Objects.Process import Process
from dataclasses import dataclass, field

import pickle


def example_func(x, y, z):
    return x + y + z


def GET_STANDARD_TYPE_FACTORY():
    return "hello"


@dataclass
class DemoClass:
    a: int
    b: int
    ptype: str = field(default_factory=GET_STANDARD_TYPE_FACTORY)


class TestRunningInParallel:
    def test_should_pickle_process_object(self):

        pickled_class = pickle.dumps(DemoClass(1, 2))
        assert pickle.loads(pickled_class) == DemoClass(1, 2)

        demo_process = Process(
            func=example_func,
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
        pickled_process = pickle.dumps(demo_process)
        loaded_pickled_process = pickle.loads(pickled_process)
        assert loaded_pickled_process.human() == demo_process.human()
