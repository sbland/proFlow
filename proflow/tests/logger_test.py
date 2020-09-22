from proflow.Objects.Interface import I
from proflow.Objects.Process import Process
from proflow.logger import log_values
from proflow.tests.mocks import Mock_Model_State_Shape, Mock_Temporal_State
from proflow.ProcessRunnerCls import ProcessRunner


def test_log_values():
    existing_logs = [
        {'a': 1, 'foo': 'bar'},
        {'a': 2, 'foo': 'barh'},
        {'a': 3, 'foo': 'barhum'},
        {'a': 4, 'foo': 'barhumb'},
    ]
    state = Mock_Model_State_Shape(
        1.1,
        2.2,
        target='humbug',
        logs=existing_logs,
        temporal=Mock_Temporal_State(4, 0, 4)
    )
    log_process = log_values(
        state_inputs=lambda state: [
            I(state.a, as_='a'),
            I(state.target, as_='foo'),
        ],
    )
    assert type(log_process) == Process
    prunner = ProcessRunner()
    state_out = prunner.run_processes([log_process], state)
    assert state_out.logs[4] == {'a': 1.1, 'foo': 'humbug'}
