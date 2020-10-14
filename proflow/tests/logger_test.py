from proflow.Objects.Interface import I
from proflow.Objects.Process import Process
from proflow.logger import log_values
from proflow.tests.mocks import Mock_Model_State_Shape
from proflow.ProcessRunnerCls import ProcessRunner


def test_log_values():
    state = Mock_Model_State_Shape(
        a=1.1,
        b=2.2,
        target='humbug',
    )
    log_process = log_values(
        state_inputs=lambda state: [
            I(state.a, as_='a'),
            I(state.target, as_='foo'),
        ],
    )
    processes = [log_process]
    assert type(log_process) == Process
    process_runner = ProcessRunner()
    assert len(process_runner.state_logs) == 1
    process_runner.run_processes(processes, state)
    assert len(process_runner.state_logs) == 1
    assert process_runner.state_logs[0] == {'a': 1.1, 'foo': 'humbug'}

def test_log_multiple_values():
    state = Mock_Model_State_Shape(
        a=1.1,
        b=2.2,
        target='humbug',
    )
    log_process = log_values(
        state_inputs=lambda state: [
            I(state.a, as_='a'),
            I(state.target, as_='foo'),
        ],
    )
    processes = [log_process]
    process_runner = ProcessRunner()
    process_runner.run_processes(processes, state)

    # run 2
    log_process = log_values(
        state_inputs=lambda state: [
            I(state.a, as_='bar'),
            I(state.target, as_='zed'),
        ],
    )
    processes = [log_process]

    process_runner.run_processes(processes, state)
    assert len(process_runner.state_logs) == 1
    assert process_runner.state_logs[0] == {'a': 1.1, 'foo': 'humbug', 'bar': 1.1, 'zed': 'humbug'}

def test_log_next_row():
    state = Mock_Model_State_Shape(
        a=1.1,
        b=2.2,
        target='humbug',
    )
    log_process = log_values(
        state_inputs=lambda state: [
            I(state.a, as_='a'),
            I(state.target, as_='foo'),
        ],
    )
    processes = [log_process]
    process_runner = ProcessRunner()
    process_runner.run_processes(processes, state)

    # Add next row
    process_runner.tm.advance_row()
    log_process = log_values(
        state_inputs=lambda state: [
            I(state.a, as_='a'),
            I(state.target, as_='foo'),
        ],
    )
    processes = [log_process]
    process_runner.run_processes(processes, state)
    assert len(process_runner.state_logs) == 2
    assert process_runner.state_logs[0] == {'a': 1.1, 'foo': 'humbug'}
    assert process_runner.state_logs[1] == {'a': 1.1, 'foo': 'humbug'}

def test_log_skip_row():
    state = Mock_Model_State_Shape(
        a=1.1,
        b=2.2,
        target='humbug',
    )
    log_process = log_values(
        state_inputs=lambda state: [
            I(state.a, as_='a'),
            I(state.target, as_='foo'),
        ],
    )
    processes = [log_process]
    process_runner = ProcessRunner()
    process_runner.run_processes(processes, state)

    # Progress 2 time steps without logging
    process_runner.tm.advance_row()
    process_runner.tm.advance_row()
    log_process = log_values(
        state_inputs=lambda state: [
            I(state.a, as_='a'),
            I(state.target, as_='foo'),
        ],
    )
    processes = [log_process]
    process_runner.run_processes(processes, state)
    assert len(process_runner.state_logs) == 3
    assert process_runner.state_logs[0] == {'a': 1.1, 'foo': 'humbug'}
    assert process_runner.state_logs[1] == {}
    assert process_runner.state_logs[2] == {'a': 1.1, 'foo': 'humbug'}
