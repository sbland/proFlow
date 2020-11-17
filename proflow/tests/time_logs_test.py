import pytest

from proflow.tests.mocks import Mock_Config_Shape, Mock_External_State_Shape, \
    Mock_Model_State_Shape, Mock_Parameters_Shape
from proflow.ProcessRunnerCls import ProcessRunner
from unittest.mock import patch
from vendor.helpers.list_helpers import flatten_list

from ..Objects.Process import Process
from ..Objects.Interface import I


def process_add(x, y):
    return x + y


def process_add_complex(x, y, *args, **kwargs):
    total = 0
    for i in range(10000):
        total += x + y + i
    return total


process_runner = ProcessRunner(
    Mock_Config_Shape(),
    Mock_External_State_Shape(),
    Mock_Parameters_Shape(),
    DEBUG_MODE=True,
)


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


def test_that_processRunnerCls_logs_time_for_each_process():
    process_runner.reset_logs()
    state = Mock_Model_State_Shape(a=2.1, b=4.1)
    processes = flatten_list([
        Process(
            func=process_add,
            config_inputs=lambda config: [
                I(config.foo, as_='x'),
                I(config.bar, as_='y'),
            ],
            state_outputs=lambda result: [
                (result, 'c'),
            ],
        ),
        Process(
            func=process_add_complex,
            config_inputs=lambda config: [
                I(config.foo, as_='x'),
            ],
            state_inputs=lambda state: [
                I(state.a, as_='y'),
            ],
            state_outputs=lambda result: [
                (result, 'd'),
            ],
        ),
    ])
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.c == 4
    assert state_2.d == 50026000.00000531
    time_logs = dict(process_runner.time_logs)
    print(time_logs)
    assert time_logs['process_add'] < time_logs['process_add_complex']


def test_that_processRunnerCls_debug_logs_time_for_each_process(benchmark_fixture):
    process_runner.reset_logs()
    state = Mock_Model_State_Shape(a=2.1, b=4.1)
    processes = flatten_list([
        Process(
            func=process_add,
            config_inputs=lambda config: [
                I(config.foo, as_='x'),
                I(config.bar, as_='y'),
            ],
            state_outputs=lambda result: [
                (result, 'c'),
            ],
        ),
        Process(
            func=process_add_complex,
            config_inputs=lambda config: [
                I(config.foo, as_='x'),
                I(config.foo, as_='x'),
            ],
            state_inputs=lambda state: [
                I(state.a, as_='y'),
                I(state.nested.na, as_='y1'),
                I(state.nested.na, as_='y2'),
                I(state.nested.na, as_='y3'),
                I(state.nested.na, as_='y4'),
                I(state.nested.na, as_='y5'),
                I(state.nested.na, as_='y6'),
                I(state.nested.na, as_='y7'),
                I(state.nested.na, as_='y8'),
                I(state.nested.na, as_='y9'),
                I(state.nested.na, as_='y10'),
                I(state.nested.na, as_='y11'),
                I(state.nested.na, as_='y12'),
                I(state.nested.na, as_='y13'),
                I(state.nested.na, as_='y14'),
                I(state.nested.na, as_='y15'),
                I(state.nested.na, as_='y16'),
                I(state.nested.na, as_='y17'),
                I(state.nested.na, as_='y18'),
                I(state.nested.na, as_='y19'),
                I(state.nested.na, as_='y110'),
                I(state.nested.na, as_='y111'),
                I(state.nested.na, as_='y112'),
                I(state.nested.na, as_='y113'),
                I(state.nested.na, as_='y114'),
                I(state.nested.na, as_='y115'),
                I(state.nested.na, as_='y116'),
                I(state.nested.na, as_='y117'),
                I(state.nested.na, as_='y118'),
                I(state.nested.na, as_='y119'),
                I(state.nested.na, as_='y120'),
                I(state.nested.na, as_='y121'),
            ],
            state_outputs=lambda result: [
                (result, 'nested.na'),
                (result, 'nested.na'),
                (result, 'nested.na'),
                (result, 'nested.na'),
                (result, 'nested.na'),
                (result, 'nested.na'),
                (result, 'nested.na'),
                (result, 'nested.na'),
                (result, 'nested.na'),
                (result, 'nested.na'),
                (result, 'nested.na'),
                (result, 'nested.na'),
                (result, 'nested.na'),
                (result, 'nested.na'),
                (result, 'nested.na'),
                (result, 'nested.na'),
                (result, 'nested.na'),
                (result, 'nested.na'),
            ],
        ),
    ])
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.c == 4
    debug_time_logs = process_runner.debug_time_logs
    assert debug_time_logs[1]['input_time'] < 0.083/benchmark_fixture
    assert debug_time_logs[1]['output_time'] < 0.21/benchmark_fixture
