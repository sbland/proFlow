import pytest
from timeit import repeat

from proflow.helpers import rgetattr

from proflow.tests.mocks import Mock_Config_Shape, Mock_External_State_Shape, \
    Mock_Model_State_Shape, Mock_Parameters_Shape
from proflow.ProcessRunnerCls import ProcessRunner
from unittest.mock import patch
from vendor.helpers.list_helpers import flatten_list

from ..Objects.Process import Process
from ..Objects.Interface import I


def process_add(x, y):
    return x + y


process_runner = ProcessRunner(
    Mock_Config_Shape(), Mock_External_State_Shape(), Mock_Parameters_Shape())


@pytest.fixture(scope="module", autouse=True)
def _():
    with patch('proflow.ProcessRunner.Model_State_Shape', side_effect=Mock_Model_State_Shape) \
            as Mocked_State_Shape:
        Mocked_State_Shape.__annotations__ = Mock_Model_State_Shape.__annotations__
        yield Mocked_State_Shape


@pytest.fixture(scope="module", autouse=True)
def __():
    with patch('proflow.ProcessRunner.Config_Shape', return_value=Mock_Config_Shape) as _fixture:
        yield _fixture


@pytest.fixture(scope="module", autouse=True)
def ____():
    with patch('proflow.ProcessRunner.Parameters_Shape', return_value=Mock_Parameters_Shape) \
            as _fixture:
        yield _fixture


@pytest.fixture(scope="module", autouse=True)
def ______():
    with patch('proflow.ProcessRunner.External_State_Shape',
               return_value=Mock_External_State_Shape) \
            as _fixture:
        yield _fixture


def test_process_runner_time():
    state = Mock_Model_State_Shape(a=2.1, b=4.1)
    processes = flatten_list([
        Process(
            func=lambda x, y: x + y,
            config_inputs=lambda config: [
                I(config.foo, as_='x'),
                I(config.bar, as_='y'),
            ],
            state_outputs=lambda result: [
                (result, 'c'),
            ],
        ),
        Process(
            func=lambda x, y: x + y,
            config_inputs=lambda config: [
                I(config.foo, as_='x'),
            ],
            state_inputs=lambda state: [
                I(rgetattr(state.matrix[0], state.ind), as_='y'),
            ],
            state_outputs=lambda result: [
                (result, 'c'),
            ],
        ),
        [Process(
            func=lambda x, y: x + y,
            config_inputs=lambda config: [
                I(config.foo, as_='x'),
            ],
            additional_inputs=lambda i=i: [
                I(i, as_='y'),
            ],
            state_outputs=lambda result: [
                (result, 'd'),
            ],
        ) for i in range(5)],
    ])
    run_processes = process_runner.initialize_processes(processes)

    time = min(repeat(lambda: run_processes(initial_state=state), number=2000, repeat=5))
    # assert 0.220 < time < 0.26 # Times with old method
    assert 0.04 < time < 0.08

# TODO: Below is depreciated
# def test_get_process_inputs_time():
#     state = Mock_Model_State_Shape(a=2.1, b=4.1)
#     process = Process(
#         func=lambda x, y: x + y,
#         config_inputs=lambda config: [
#             I(config.foo, as_='x'),
#             I(config.bar, as_='y'),
#         ],
#         state_outputs=lambda result: [
#             (result, 'c'),
#         ],
#     )
#     config = Mock_Config_Shape()
#     get_process_inputs_fn = partial(get_process_inputs,
#                                     process=process,
#                                     prev_state=state,
#                                     config=config,
#                                     parameters=Mock_Parameters_Shape(),
#                                     external_state=Mock_External_State_Shape(),
#                                     )
#     time = min(repeat(get_process_inputs_fn, number=20000, repeat=25))
#     print(1 - (time / 0.15))
#     assert 0.110 < time < 0.135


# def test_get_key_values_time():
#     data = {
#         "foo": "hello",
#         "bar": "world",
#         "nested": {
#             "hello": "world"
#         }
#     }
#     input_keys = [
#         I(from_='foo', as_='target_A'),
#         I(from_='bar', as_='target_B'),
#         I(from_='nested.hello', as_='target_C'),
#     ]
#     get_process_inputs_fn = partial(get_key_values,
#                                     f=lambda x: x,
#                                     data=data,
#                                     input_keys=input_keys,
#                                     )
#     time = min(repeat(get_process_inputs_fn, number=80000, repeat=5))
#     print(1 - (time / 0.210))
#     assert 0.200 < time < 0.230
