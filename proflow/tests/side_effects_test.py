from proflow.ProcessRunnerCls import ProcessRunner
from unittest.mock import MagicMock, patch
import pytest
from vendor.helpers.list_helpers import flatten_list
from proflow.tests.mocks import Mock_Config_Shape, Mock_External_State_Shape, \
    Mock_Model_State_Shape, Mock_Parameters_Shape
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


def test_side_effect_arg():
    state = Mock_Model_State_Shape(a=2.1, b=4.1)
    fn = MagicMock()
    processes = flatten_list([
        Process(
            func=fn,
            args=['hello'],
        ),
    ])
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    fn.assert_called_with('hello')
    assert state_2.a == 2.1
    assert state_2.b == 4.1


def test_side_effect_state_arg():
    state = Mock_Model_State_Shape(a=2.1, b=4.1)
    fn = MagicMock()
    processes = flatten_list([
        Process(
            func=fn,
            comment="fn",
            state_inputs=lambda state: [
                I(state.a, as_='input'),
            ],
        ),
    ])
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    fn.assert_called_with(input=2.1)
    assert state_2.a == 2.1
    assert state_2.b == 4.1
