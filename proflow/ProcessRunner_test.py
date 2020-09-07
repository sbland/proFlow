import pytest
import numpy as np

from proflow.tests.mocks import Mock_Config_Shape, Mock_External_State_Shape, \
    Mock_Model_State_Shape, Mock_Nested_State, Mock_Parameters_Shape
from proflow.ProcessRunnerCls import ProcessRunner
from unittest.mock import MagicMock, patch
from vendor.helpers.list_helpers import flatten_list, filter_none

from .ProcessRunner import Process, I


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
    with patch('proflow.ProcessRunner.External_State_Shape', return_value=Mock_External_State_Shape) \
            as _fixture:
        yield _fixture


def test_procces_runner():
    state = Mock_Model_State_Shape(a=2.1, b=4.1)
    processes = flatten_list([
        Process(
            func=process_add,
            config_inputs=[
                I('foo', as_='x'),
                I('bar', as_='y'),
            ],
            state_outputs=[
                I('result', as_='c'),
            ],
        ),
        Process(
            func=process_add,
            config_inputs=[
                I('foo', as_='x'),
            ],
            state_inputs=[
                I('a', as_='y'),
            ],
            state_outputs=[
                I('result', as_='d'),
            ],
        ),
    ])
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.c == 4
    assert state_2.d == 3.1


def test_procces_runner_nested_args():
    state = Mock_Model_State_Shape(a=2.1, b=4.1)

    processes = flatten_list([
        Process(
            func=process_add,
            config_inputs=[
                I('roo.abc', as_='x'),
            ],
            state_inputs=[
                I('a', as_='y'),
            ],
            state_outputs=[
                I('result', as_='a'),
            ],
        ),
    ])
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.a == 7.1


def test_procces_runner_nested_args_out():
    state = Mock_Model_State_Shape(a=2.1, b=4.1)

    processes = flatten_list([
        Process(
            func=process_add,
            config_inputs=[
                I('roo.abc', as_='x'),
            ],
            state_inputs=[
                I('a', as_='y'),
            ],
            state_outputs=[
                I('result', as_='nested.na'),
            ],
        ),
    ])
    state_2 = process_runner.initialize_processes(processes)(initial_state=state)
    assert state_2.nested.na == 7.1


def test_procces_runner_nested_args_list():
    state = Mock_Model_State_Shape(a=2.1, b=4.1)

    processes = flatten_list([
        Process(
            func=process_add,
            config_inputs=[
                I('roo.abc', as_='x'),
            ],
            state_inputs=[
                I('a', as_='y'),
            ],
            state_outputs=[
                I('result', as_='a'),
            ],
        ),
    ])
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.a == 7.1


def test_procces_runner_nested_args_list_out():
    state = Mock_Model_State_Shape(a=2.1, b=4.1, lst=[1, 2, 3])
    processes = flatten_list([
        Process(
            func=lambda i, j: [i, j],
            config_inputs=[
                I('foo', as_='i'),
            ],
            state_inputs=[
                I('a', as_='j'),
            ],
            state_outputs=[
                I('0', as_='lst.0'),
                I('1', as_='lst.1'),
            ],
        ),
    ])
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.lst[0] == process_runner.config.foo
    assert state_2.lst[1] == state.a


def test_procces_runner_nested_args_matrix_out():
    state = Mock_Model_State_Shape(a=2.1, b=4.1, lst=[1, 2, 3])
    processes = flatten_list([
        Process(
            func=lambda i, j, k: [[i, j], [k, k]],
            config_inputs=[
                I('foo', as_='i'),
            ],
            state_inputs=[
                I('a', as_='j'),
                I('b', as_='k'),
            ],
            state_outputs=[
                I('0.1', as_='lst.0'),
                I('1.0', as_='lst.1'),
            ],
        ),
    ])
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.lst[0] == state.a
    assert state_2.lst[1] == state.b


def test_procces_runner_nested():
    state = Mock_Model_State_Shape(a=2.1, b=4.1)

    processes = flatten_list([
        [Process(
            func=process_add,
            config_inputs=[
                I('bar', as_='y'),
            ],
            additional_inputs=[
                I('x', i),
            ],
            state_outputs=[
                I('result', as_='c'),
            ],
        ) for i in range(10)],
        Process(
            func=process_add,
            config_inputs=[
                I('foo', as_='x'),
            ],
            state_inputs=[
                I('a', as_='y'),
            ],
            state_outputs=[
                I('result', as_='d'),
            ],
        ),
    ])
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.c == 12
    assert state_2.d == 3.1


def test_procces_b_optional():
    state = Mock_Model_State_Shape(a=2.1, b=4.1)

    config_do_this = True
    config_dont_do_this = False

    processes = filter_none(flatten_list([
        Process(
            func=process_add,
            additional_inputs=[
                I('x', 10),
            ],
            state_inputs=[
                I('a', as_='y'),
            ],
            state_outputs=[
                I('result', as_='c'),
            ],
        ) if config_do_this else None,
        Process(
            func=process_add,
            additional_inputs=[
                I('x', 100),
            ],
            state_inputs=[
                I('a', as_='y'),
            ],
            state_outputs=[
                I('result', as_='d'),
            ],
        )if config_dont_do_this else None,
    ]))
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.c == 12.1
    assert state_2.d == 0


def test_procces_b_complex():
    state = Mock_Model_State_Shape(a=2.1, b=4.1)

    processes = filter_none(flatten_list([
        [
            Process(
                func=process_add,
                additional_inputs=[
                    I('x', i),
                ],
                state_inputs=[
                    I('a', as_='y'),
                ],
                state_outputs=[
                    I('result', as_='a'),
                ],
            ) if i < 4 else
            Process(
                func=process_add,
                additional_inputs=[
                    I('x', 100),
                ],
                state_inputs=[
                    I('a', as_='y'),
                ],
                state_outputs=[
                    I('result', as_='a'),
                ],
            ) if i < 8 else None
            for i in range(10)
        ],
        Process(
            func=lambda x: {'out': x},
            state_inputs=[
                I('a', as_='x'),
            ],
            state_outputs=[
                I('out', as_='b'),
            ],
        ),
        Process(
            func=lambda x: {'out': x * 2},
            state_inputs=[
                I('b', as_='x'),
            ],
            state_outputs=[
                I('out', as_='b'),
            ],
        )
    ]))
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.a == 408.1
    assert state_2.b == 816.2


def test_procces_b_complex_02():
    state = Mock_Model_State_Shape(a=2.1, b=4.1, c=1)

    def function_with_lots_of_args(
            season_Astart, Tleaf_C, c_a, e_a, Q, g_bl,
            g_sto_0, m, V_cmax_25, J_max_25, D_0, O3, O3up_acc, td, dd, hr
    ):
        return {
            'gsto_final': 1,
            'A_n_final': 1,
            'A_c_final': 1,
            'A_j_final': 1,
            'A_p_final': 1,
            'R_d': 1,
            'O3up_out': 1,
            'O3up_acc_out': 1,
            'fO3_h_out': 1,
            'fO3_d_out': 1,
        }

    def translate_unit(val, rate):
        return {
            'result': val * rate,
        }

    gsto_processes = [
        Process(
            func=function_with_lots_of_args,
            config_inputs=[
                I('foo', as_='season_Astart'),
                I('foo', as_='Tleaf_C'),
                I('foo', as_='c_a'),
                I('foo', as_='e_a'),
                I('bar', as_='Q'),
                I('bar', as_='g_bl'),
                I('bar', as_='g_sto_0'),
                I('bar', as_='m'),
            ],
            state_inputs=[
                I('a', as_='V_cmax_25'),
                I('a', as_='J_max_25'),
                I('a', as_='D_0'),
                I('a', as_='O3'),
                I('a', as_='O3up_acc'),
                I('a', as_='td'),
                I('a', as_='dd'),
                I('a', as_='hr'),
            ],
            state_outputs=[
                I('gsto_final', as_='b'),
                I('A_n_final', as_='b'),
                I('A_c_final', as_='b'),
                I('A_j_final', as_='b'),
                I('A_p_final', as_='b'),
                I('R_d', as_='b'),
                I('O3up_out', as_='b'),
                I('O3up_acc_out', as_='b'),
                I('fO3_h_out', as_='b'),
                I('fO3_d_out', as_='b'),
            ],
        ),
        Process(
            func=translate_unit,
            state_inputs=[
                I('b', as_='val'),
            ],
            additional_inputs=[
                I('rate', 0.1),
            ],
            state_outputs=[
                I('result', as_='b')
            ]
        ),
        Process(
            func=lambda x: {'result': x * 2},
            state_inputs=[
                I('c', as_='x'),
            ],
            state_outputs=[
                I('result', as_='c')
            ],
        ),
    ]

    end_process = Process(
        func=lambda x: {'result': x * 2},
        state_inputs=[
            I('b', as_='x'),
        ],
        state_outputs=[
            I('result', as_='b')
        ]
    )

    processes = filter_none(flatten_list([
        [gsto_processes for i in range(3)],
        end_process,
    ]))
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.a == 2.1
    assert state_2.b == 0.2
    assert state_2.c == 8


def test_annual_cycle():
    hourly_processes = [
        Process(
            func=process_add,
            state_inputs=[
                I('a', as_='x'),
            ],
            additional_inputs=[
                I('y', 1),
            ],
            state_outputs=[
                I('result', as_='a')
            ]
        ),
    ]
    daily_start_processes = [
        Process(
            func=process_add,
            state_inputs=[
                I('b', as_='x'),
            ],
            additional_inputs=[
                I('y', 1),
            ],
            state_outputs=[
                I('result', as_='b')
            ]
        ),
        Process(
            func=lambda x: {'result': x},
            state_inputs=[
                I('a', as_='x'),
            ],
            state_outputs=[
                I('result', as_='c')
            ]
        ),
    ]
    daily_end_processes = [
        Process(
            func=lambda x: {'result': x},
            state_inputs=[
                I('a', as_='x'),
            ],
            state_outputs=[
                I('result', as_='d')
            ]
        ),
    ]

    daily_process_list = [
        daily_start_processes,
        [hourly_processes for i in range(24)],
        daily_end_processes,
    ]

    daily_processes = flatten_list(daily_process_list)

    state = Mock_Model_State_Shape(a=0, b=0)

    run_processes = process_runner.initialize_processes(daily_processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.a == 24  # hours ran
    assert state_2.b == 1  # days ran
    assert state_2.c == 0  # hour value at start
    assert state_2.d == 24  # hour value at end

    annual_processes = flatten_list([
        daily_process_list for d in range(365)
    ])

    run_processes = process_runner.initialize_processes(annual_processes)
    state_end_of_year = run_processes(initial_state=state)
    assert state_end_of_year.a == 8760  # hours ran
    assert state_end_of_year.b == 365  # days ran


def test_process_with_string_literals():
    """We can use string literals to insert variables into our target"""
    state = Mock_Model_State_Shape(a=1, b=2, nested=Mock_Nested_State(3, 1003), target="na")
    processes = flatten_list([
        Process(
            func=process_add,
            state_inputs=[
                I('a', as_='x'),
                # uses the target from additional inputs to define the nested prop to use
                I('nested.{state.target}', as_='y'),
            ],
            state_outputs=[
                I('result', as_='c'),
            ],
        ),
        Process(
            func=lambda x: {'out': x},

            additional_inputs=[
                I('x', 'nab'),
            ],
            state_outputs=[
                I('out', as_='target')
            ]
        ),
        Process(
            func=process_add,
            state_inputs=[
                I('a', as_='x'),
                # uses the target from additional inputs to define the nested prop to use
                I('nested.{state.target}', as_='y'),
            ],
            state_outputs=[
                I('result', as_='d'),
            ],
        ),
    ])
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.c == 4
    assert state_2.d == 1004


def test_procces_runner_list_result():
    state = Mock_Model_State_Shape(a=2.1, b=4.1)

    processes = flatten_list([
        Process(
            func=lambda: [1, 2, 3],
            comment="initialize with lists",
            state_outputs=[
                I('_list', as_='lst')
            ]
        )
    ])
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.lst == [1, 2, 3]


def test_setup_parameters():
    """Test that we can initialize the parameters"""
    parameters = Mock_Parameters_Shape()
    processes = flatten_list([
        Process(
            func=process_add,
            external_state_inputs=[
                I('data_a', as_='x'),
            ],
            additional_inputs=[
                I('y', 10),
            ],
            state_outputs=[
                I('result', as_='foo'),
            ],
        ),
    ])
    run_processes = process_runner.initialize_processes(processes)
    parameters_initialized = run_processes(initial_state=parameters)
    assert parameters_initialized.foo == 11


def test_process_using_gate():
    state = Mock_Model_State_Shape(a=2.1, b=4.1)
    fn_1 = MagicMock()
    fn_2 = MagicMock()
    processes = flatten_list([
        Process(
            func=fn_1,
            gate=1 == 2,  # False
        ),
        Process(
            func=fn_2,
            gate=2 == 2,  # True
        ),
    ])
    run_processes = process_runner.initialize_processes(processes)
    run_processes(initial_state=state)

    assert not fn_1.called
    assert fn_2.called


def test_process_runner_using_wildcard_list_index():
    state = Mock_Model_State_Shape(a=2.1, b=4.1, matrix=[[1, 2, 3], [4, 5, 6]])
    processes = flatten_list([
        Process(
            func=lambda values: values,
            state_inputs=[
                I('matrix._.1')
            ],
            state_outputs=[
                I('_result', as_='c'),
            ],
        ),
    ])
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.c == [2, 5]


def test_process_runner_using_wildcard_list_obj():
    state = Mock_Model_State_Shape(a=2.1, b=4.1, matrix=[[1, 2, 3], [4, 5, 6]])
    processes = flatten_list([
        Process(
            func=lambda out: out,
            state_inputs=[
                I('nested_lst_obj._.na'),
            ],
            state_outputs=[
                I('_result', as_='d')
            ]
        )
    ])
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.d == [1, 3]


def test_process_runner_using_wildcard_multiple():
    state = Mock_Model_State_Shape(a=2.1, b=4.1, matrix=[[1, 2, 3], [4, 5, 6]])
    processes = flatten_list([
        Process(
            func=lambda values: values,
            state_inputs=[
                I('matrix._._')
            ],
            state_outputs=[
                I('_result', as_='c'),
            ],
        ),
    ])
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.c == [[1, 2, 3], [4, 5, 6]]


def test_process_runner_using_wildcard_nparray():
    state = Mock_Model_State_Shape(a=2.1, b=4.1, matrix=np.array([[1, 2, 3], [4, 5, 6]]))
    processes = flatten_list([
        Process(
            func=lambda values: values,
            state_inputs=[
                I('matrix._.1')
            ],
            state_outputs=[
                I('_result', as_='c'),
            ],
        ),
    ])
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.c == [2, 5]
