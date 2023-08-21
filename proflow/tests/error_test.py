
import pytest
from vendor.helpers.list_helpers import flatten_list
from proflow.ProcessRunnerCls import ProcessRunner
from proflow.ProcessRunner import I, Process, Run_Process_Error
from proflow.tests.mocks import Mock_Config_Shape, Mock_External_State_Shape, \
    Mock_Model_State_Shape, Mock_Parameters_Shape


def process_add(x, y):
    return x + y


process_runner = ProcessRunner(
    Mock_Config_Shape(), Mock_External_State_Shape(), Mock_Parameters_Shape())


def test_process_error():
    state = Mock_Model_State_Shape(a=2.1, b=4.1)
    processes = flatten_list([
        Process(
            func=process_add,
            additional_inputs=lambda: [
                I(None, as_='x'),
                I(4, as_='y'),
            ],
            state_outputs=lambda result: [
                (result, 'c'),
            ],
        ),
    ])
    process_runner.DEBUG_MODE = True
    run_processes = process_runner.initialize_processes(processes)
    with pytest.raises(Run_Process_Error) as exc:
        run_processes(initial_state=state)
    assert exc.value.message == 'Failed to run "process_add"'
    assert exc.value.state == state


def test_process_error_with_comment():
    state = Mock_Model_State_Shape(a=2.1, b=4.1)
    processes = flatten_list([
        Process(
            func=process_add,
            comment="Demo Process",
            additional_inputs=lambda: [
                I(None, as_='x'),
                I(4, as_='y'),
            ],
            state_outputs=lambda result: [
                (result, 'c'),
            ],
        ),
    ])
    process_runner.DEBUG_MODE = True
    run_processes = process_runner.initialize_processes(processes)
    with pytest.raises(Run_Process_Error) as exc:
        run_processes(initial_state=state)
    assert exc.value.message == 'Failed to run "Demo Process"'

    # with pytest.raises(TypeError) as exc:
    #     run_processes(initial_state=state)
    # print(exc._excinfo[1].__repr__())
    # print(exc._excinfo[1])
    # assert list(exc.__dict__.values())[0][1] == "hello"


def test_process_error_string():
    state = Mock_Model_State_Shape(a=2.1, b=4.1)
    processes = flatten_list([
        Process(
            func=process_add,
            comment="Demo Process",
            additional_inputs=lambda: [
                I(None, as_='x'),
                I(4, as_='y'),
            ],
            state_outputs=lambda result: [
                (result, 'c'),
            ],
        ),
    ])
    process_runner.DEBUG_MODE = True
    run_processes = process_runner.initialize_processes(processes)
    with pytest.raises(Run_Process_Error) as exc:
        run_processes(initial_state=state)
    assert """kwargs:
           -------
           {
               "x": null,
               "y": 4
           }
     """.replace('\n', ' ').replace(' ', '') in str(exc.value).replace('\n', ' ').replace(' ', '')
