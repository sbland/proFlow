from dataclasses import dataclass, field
from typing import Callable, List
import pytest
from copy import copy

from src.ProcessRunnerCls import ProcessRunner
from unittest.mock import patch
from vendor.helpers.list_helpers import flatten_list
from src.tests.mocks import Mock_Config_Shape, Mock_External_State_Shape, \
    Mock_Model_State_Shape, Mock_Parameters_Shape
from ..ProcessRunner import Process, I


def add_to_logs(logs, **kwargs):
    logs_c = copy(logs)
    for k, v in kwargs.items():
        logs_c[k] = logs_c[k] + [v]
    return logs_c

@dataclass(frozen=True)
class Logger(Process):
    func: Callable = add_to_logs
    state_outputs: List[I] = field(default_factory=lambda: [I('_result', as_='logs')])


process_runner = ProcessRunner(
    Mock_Config_Shape(), Mock_External_State_Shape(), Mock_Parameters_Shape())


@pytest.fixture(scope="module", autouse=True)
def _():
    with patch('src.ProcessRunner.Model_State_Shape', side_effect=Mock_Model_State_Shape) \
            as Mocked_State_Shape:
        Mocked_State_Shape.__annotations__ = Mock_Model_State_Shape.__annotations__
        yield Mocked_State_Shape


@pytest.fixture(scope="module", autouse=True)
def __():
    with patch('src.ProcessRunner.Config_Shape', return_value=Mock_Config_Shape) as _fixture:
        yield _fixture


@pytest.fixture(scope="module", autouse=True)
def ____():
    with patch('src.ProcessRunner.Parameters_Shape', return_value=Mock_Parameters_Shape) \
            as _fixture:
        yield _fixture


@pytest.fixture(scope="module", autouse=True)
def ______():
    with patch('src.ProcessRunner.External_State_Shape', return_value=Mock_External_State_Shape) \
            as _fixture:
        yield _fixture


def test_logging():
    state = Mock_Model_State_Shape(a=2.1, b=4.1, logs={'a': [], 'b': [], 't': []})

    processes = flatten_list([[
        Process(
            func=add_to_logs,
            state_inputs=[
                I('logs', as_='logs'),
                I('a', as_='a'),
                I('b', as_='b'),
            ],
            additional_inputs=[
                I('t', i),
            ],
            state_outputs=[I('_result', as_='logs')]
        ),
        Process(
            func=lambda x: x + 1,
            state_inputs=[I('a', as_='x')],
            state_outputs=[I('_result', as_='a')],
        ),

    ] for i in range(3)])
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    print(state_2.logs)
    assert state_2.logs['a'][0] == 2.1
    assert state_2.logs['a'][1] == 3.1
    assert state_2.logs['t'] == [0, 1, 2]


def test_logging_class():
    state = Mock_Model_State_Shape(a=2.1, b=4.1, logs={'a': [], 'b': [], 't': []})

    processes = flatten_list([[
        Logger(
            state_inputs=[
                I('logs', as_='logs'),
                I('a', as_='a'),
                I('b', as_='b'),
            ],
            additional_inputs=[
                I('t', i),
            ],
        ),
        Process(
            func=lambda x: x + 1,
            state_inputs=[I('a', as_='x')],
            state_outputs=[I('_result', as_='a')],
        ),

    ] for i in range(3)])
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    print(state_2.logs)
    assert state_2.logs['a'][0] == 2.1
    assert state_2.logs['a'][1] == 3.1
    assert state_2.logs['t'] == [0, 1, 2]
