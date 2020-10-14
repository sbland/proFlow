import pytest
import numpy as np

from proflow.helpers import rgetattr
from proflow.tests.mocks import Mock_Config_Shape, Mock_External_State_Shape, \
    Mock_Model_State_Shape, Mock_Nested_State, Mock_Parameters_Shape
from proflow.ProcessRunnerCls import ProcessRunner, advance_time_step_process
from unittest.mock import MagicMock, patch
from vendor.helpers.list_helpers import flatten_list, filter_none

from .Objects.Interface import I
from .Objects.Process import Process


def process_add(x, y):
    return x + y


process_runner = ProcessRunner(
    Mock_Config_Shape(), Mock_External_State_Shape(), Mock_Parameters_Shape())


# @pytest.fixture(scope="module", autouse=True)
# def _():
#     with patch('proflow.ProcessRunner.Model_State_Shape', side_effect=Mock_Model_State_Shape) \
#             as Mocked_State_Shape:
#         Mocked_State_Shape.__annotations__ = Mock_Model_State_Shape.__annotations__
#         yield Mocked_State_Shape


@pytest.fixture(scope="module", autouse=True)
def __():
    with patch('proflow.ProcessRunnerCls.Config_Shape', return_value=Mock_Config_Shape) as _fixture:
        yield _fixture


@pytest.fixture(scope="module", autouse=True)
def ____():
    with patch('proflow.ProcessRunnerCls.Parameters_Shape', return_value=Mock_Parameters_Shape) \
            as _fixture:
        yield _fixture


@pytest.fixture(scope="module", autouse=True)
def ______():
    with patch('proflow.ProcessRunnerCls.External_State_Shape',
               return_value=Mock_External_State_Shape) \
            as _fixture:
        yield _fixture


def test_procces_runner_simple():
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
            func=process_add,
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
    assert state_2.d == 3.1


def test_procces_runner_nested_args():
    state = Mock_Model_State_Shape(a=2.1, b=4.1)

    processes = flatten_list([
        Process(
            func=process_add,
            config_inputs=lambda config: [
                I(config.roo['abc'], as_='x'),
            ],
            state_inputs=lambda state: [
                I(state.a, as_='y'),
            ],
            state_outputs=lambda result: [
                (result, 'a'),
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
            config_inputs=lambda config: [
                I(config.roo['abc'], as_='x'),
            ],
            state_inputs=lambda state: [
                I(state.a, as_='y'),
            ],
            state_outputs=lambda result: [
                (result, 'nested.na'),
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
            config_inputs=lambda config: [
                I(config.roo['abc'], as_='x'),
            ],
            state_inputs=lambda state: [
                I(state.a, as_='y'),
            ],
            state_outputs=lambda result: [
                (result, 'a'),
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
            config_inputs=lambda config: [
                I(config.foo, as_='i'),
            ],
            state_inputs=lambda state: [
                I(state.a, as_='j'),
            ],
            state_outputs=lambda result: [
                (result[0], 'lst.0'),
                (result[1], 'lst.1'),
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
            config_inputs=lambda config: [
                I(config.foo, as_='i'),
            ],
            state_inputs=lambda state: [
                I(state.a, as_='j'),
                I(state.b, as_='k'),
            ],
            state_outputs=lambda result: [
                (result[0][1], 'lst.0'),
                (result[1][0], 'lst.1'),
            ],
        ),
    ])
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.lst[0] == state.a
    assert state_2.lst[1] == state.b


def test_procces_runner_nested_simple():
    state = Mock_Model_State_Shape(a=2.1, b=4.1)

    processes = flatten_list([
        [Process(
            func=process_add,
            comment="tag me",
            config_inputs=lambda config: [
                I(config.bar, as_='y'),
            ],
            additional_inputs=lambda: [
                I(i, as_='x'),
            ],
            state_outputs=lambda result: [
                (result, 'c'),
            ],
        ) for i in range(10)],
        Process(
            func=process_add,
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
    assert state_2.c == 12
    assert state_2.d == 3.1


def test_procces_b_optional():
    state = Mock_Model_State_Shape(a=2.1, b=4.1)

    config_do_this = True
    config_dont_do_this = False

    processes = filter_none(flatten_list([
        Process(
            func=process_add,
            additional_inputs=lambda: [
                I(10, as_='x'),
            ],
            state_inputs=lambda state: [
                I(state.a, as_='y'),
            ],
            state_outputs=lambda result: [
                (result, 'c'),
            ],
        ) if config_do_this else None,
        Process(
            func=process_add,
            additional_inputs=lambda: [
                I(100, as_='x'),
            ],
            state_inputs=lambda state: [
                I(state.a, as_='y'),
            ],
            state_outputs=lambda result: [
                (result, 'd'),
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
                # Note: i=i ensures that we pass i into lambda scope
                # Otherwise i would = i at the end of the scope
                additional_inputs=lambda i=i: [
                    I(i, as_='x'),
                ],
                state_inputs=lambda state: [
                    I(state.a, as_='y'),
                ],
                state_outputs=lambda result: [
                    (result, 'a'),
                ],
            ) if i < 4 else
            Process(
                func=process_add,
                additional_inputs=lambda: [
                    I(100, as_='x'),
                ],
                state_inputs=lambda state: [
                    I(state.a, as_='y'),
                ],
                state_outputs=lambda result: [
                    (result, 'a'),
                ],
            ) if i < 8 else None
            for i in range(10)
        ],
        Process(
            func=lambda x: {'out': x},
            state_inputs=lambda state: [
                I(state.a, as_='x'),
            ],
            state_outputs=lambda result: [
                (result['out'], 'b'),
            ],
        ),
        Process(
            func=lambda x: {'out': x * 2},
            state_inputs=lambda state: [
                I(state.b, as_='x'),
            ],
            state_outputs=lambda result: [
                (result['out'], 'b'),
            ],
        ),
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
            'out': val * rate,
        }

    gsto_processes = [
        Process(
            func=function_with_lots_of_args,
            config_inputs=lambda config: [
                I(config.foo, as_='season_Astart'),
                I(config.foo, as_='Tleaf_C'),
                I(config.foo, as_='c_a'),
                I(config.foo, as_='e_a'),
                I(config.bar, as_='Q'),
                I(config.bar, as_='g_bl'),
                I(config.bar, as_='g_sto_0'),
                I(config.bar, as_='m'),
            ],
            state_inputs=lambda state: [
                I(state.a, as_='V_cmax_25'),
                I(state.a, as_='J_max_25'),
                I(state.a, as_='D_0'),
                I(state.a, as_='O3'),
                I(state.a, as_='O3up_acc'),
                I(state.a, as_='td'),
                I(state.a, as_='dd'),
                I(state.a, as_='hr'),
            ],
            state_outputs=lambda result: [
                (result['gsto_final'], 'b'),
                (result['A_n_final'], 'b'),
                (result['A_c_final'], 'b'),
                (result['A_j_final'], 'b'),
                (result['A_p_final'], 'b'),
                (result['R_d'], 'b'),
                (result['O3up_out'], 'b'),
                (result['O3up_acc_out'], 'b'),
                (result['fO3_h_out'], 'b'),
                (result['fO3_d_out'], 'b'),
            ],
        ),
        Process(
            func=translate_unit,
            state_inputs=lambda state: [
                I(state.b, as_='val'),
            ],
            additional_inputs=lambda: [
                I(0.1, as_='rate'),
            ],
            state_outputs=lambda result: [
                (result['out'], 'b')
            ],
        ),
        Process(
            func=lambda x: {'out': x * 2},
            state_inputs=lambda state: [
                I(state.c, as_='x'),
            ],
            state_outputs=lambda result: [
                (result['out'], 'c')
            ],
        ),
    ]

    end_process = Process(
        func=lambda x: {'out': x * 2},
        state_inputs=lambda state: [
            I(state.b, as_='x'),
        ],
        state_outputs=lambda result: [
            (result['out'], 'b')
        ],
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
            state_inputs=lambda state: [
                I(state.a, as_='x'),
            ],
            additional_inputs=lambda: [
                I(1, as_='y'),
            ],
            state_outputs=lambda result: [
                (result, 'a')
            ],
        ),
    ]
    daily_start_processes = [
        Process(
            func=process_add,
            state_inputs=lambda state: [
                I(state.b, as_='x'),
            ],
            additional_inputs=lambda: [
                I(1, as_='y'),
            ],
            state_outputs=lambda result: [
                (result, 'b')
            ],
        ),
        Process(
            func=lambda x: {'out': x},
            state_inputs=lambda state: [
                I(state.a, as_='x'),
            ],
            state_outputs=lambda result: [
                (result['out'], 'c')
            ],
        ),
    ]
    daily_end_processes = [
        Process(
            func=lambda x: {'out': x},
            state_inputs=lambda state: [
                I(state.a, as_='x'),
            ],
            state_outputs=lambda result: [
                (result['out'], 'd')
            ],
        ),
    ]

    daily_process_list = [
        daily_start_processes,
        [hourly_processes for i in range(24)],
        daily_end_processes,
    ]

    daily_processes = flatten_list(daily_process_list)

    state = Mock_Model_State_Shape(a=0, b=0)
    assert state.a == 0

    run_processes = process_runner.initialize_processes(daily_processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.a == 24  # hours ran
    assert state_2.b == 1  # days ran
    assert state_2.c == 0  # hour value at start
    assert state_2.d == 24  # hour value at end

    # default mode mutates state
    state_2 = run_processes(initial_state=state)
    assert state_2.a == 48  # hours ran
    assert state_2.b == 2  # days ran
    assert state_2.c == 24  # hour value at start
    assert state_2.d == 48  # hour value at end

    annual_processes = flatten_list([
        daily_process_list for d in range(365)
    ])

    state = Mock_Model_State_Shape(a=0, b=0)
    run_processes = process_runner.initialize_processes(annual_processes)
    state_end_of_year = run_processes(initial_state=state)
    assert state_end_of_year.a == 8760  # hours ran
    assert state_end_of_year.b == 365  # days ran


def test_process_with_string_literals():
    """Use rgetattr to use state as target.

    We can use string literals to insert variables into our target

    """
    state = Mock_Model_State_Shape(a=1, b=2, nested=Mock_Nested_State(3, 1003), target="na")
    processes = flatten_list([
        Process(
            func=process_add,
            state_inputs=lambda state: [
                I(state.a, as_='x'),
                # uses the target from additional inputs to define the nested prop to use
                I(rgetattr(state, f'nested.{state.target}'), as_='y'),
            ],
            state_outputs=lambda result: [
                (result, 'c'),
            ],
        ),
        Process(
            func=lambda x: {'out': x},

            additional_inputs=lambda: [
                I('nab', as_='x'),
            ],
            state_outputs=lambda result: [
                (result['out'], 'target')
            ],
        ),
        Process(
            func=process_add,
            state_inputs=lambda state: [
                I(state.a, as_='x'),
                # uses the target from additional inputs to define the nested prop to use
                I(rgetattr(state, f'nested.{state.target}'), as_='y'),
            ],
            state_outputs=lambda result: [
                (result, 'd'),
            ],
        ),
    ])
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.c == 4
    assert state_2.d == 1004

# TODO: Below is no longer supported
# def test_process_with_string_literal_output():
#     """We can use string literals to target output state base on input state variable."""
#     state = Mock_Model_State_Shape(a=1, b=2, nested=Mock_Nested_State(3, 1003), target="na")
#     processes = flatten_list([
#         Process(
#             func=lambda x: {'out': x},
#             additional_inputs=lambda: [
#                 I('nab', as_='x'),
#             ],
#             state_outputs=lambda result: [
#                 (result['out'], 'target')
#             ]
#         ],
#         Process(
#             func=lambda x: x,
#             state_inputs=lambda state: [
#                 I(state.a, as_='x'),
#             ],
#             state_outputs=lambda result: [
#                 (result, 'nested.{state.target}'),
#             ],
#         ],
#     ])
#     run_processes = process_runner.initialize_processes(processes)
#     state_2 = run_processes(initial_state=state)
#     assert state_2.nested.nab == 1


def test_procces_runner_list_result():
    state = Mock_Model_State_Shape(a=2.1, b=4.1)

    processes = flatten_list([
        Process(
            func=lambda: [1, 2, 3],
            comment="initialize with lists",
            state_outputs=lambda result: [
                (result, 'lst')
            ],
        ),
    ])
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.lst == [1, 2, 3]


def test_use_external_state():
    state = Mock_Model_State_Shape(a=2.1, b=4.1)
    process = Process(
        func=process_add,
        external_state_inputs=lambda e_state, row_index: [
            I(e_state.data_a[row_index], as_='x'),
        ],
        additional_inputs=lambda: [
            I(10, as_='y'),
        ],
        state_outputs=lambda result: [
            (result, 'a'),
        ],
    )
    run_processes = process_runner.initialize_processes([process])
    state_2 = run_processes(initial_state=state)
    assert state_2.a == 11


def test_setup_parameters():
    """Test that we can initialize the parameters"""
    parameters = Mock_Parameters_Shape()
    processes = flatten_list([
        Process(
            func=process_add,
            external_state_inputs=lambda e_state, row_index: [
                I(e_state.data_a[row_index], as_='x'),
            ],
            additional_inputs=lambda: [
                I(10, as_='y'),
            ],
            state_outputs=lambda result: [
                (result, 'foo'),
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
            func=lambda input: input,
            state_inputs=lambda state: [
                # TODO: can we abstract this to make it readable?
                I([state.matrix[i][1] for i in range(len(state.matrix))], as_='input')
            ],
            state_outputs=lambda result: [
                (result, 'c'),
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
            func=lambda input: input,
            state_inputs=lambda state: [
                I([state.nested_lst_obj[i].na for i in range(len(state.nested_lst_obj))],
                  as_='input'),
            ],
            state_outputs=lambda result: [
                (result, 'd')
            ],
        ),
    ])
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.d == [1, 3]


def test_process_runner_using_wildcard_multiple():
    state = Mock_Model_State_Shape(a=2.1, b=4.1, matrix=[[1, 2, 3], [4, 5, 6]])
    processes = flatten_list([
        Process(
            func=lambda input: input,
            state_inputs=lambda state: [
                I([[state.matrix[i][j] for j in range(len(state.matrix[i]))]
                   for i in range(len(state.matrix))], as_='input')
            ],
            state_outputs=lambda result: [
                (result, 'c'),
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
            func=lambda input: input,
            state_inputs=lambda state: [
                I([state.matrix[i][1] for i in range(len(state.matrix))], as_='input'),
            ],
            state_outputs=lambda result: [
                (result, 'c'),
            ],
        ),
    ])
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.c == [2, 5]


def test_immutable_mode_0():
    processes = [
        Process(
            func=process_add,
            state_inputs=lambda state: [
                I(state.a, as_='x'),
            ],
            additional_inputs=lambda: [
                I(1, as_='y'),
            ],
            state_outputs=lambda result: [
                (result, 'a')
            ],
        ),
    ]

    state = Mock_Model_State_Shape(a=0, b=0)
    assert state.a == 0

    run_processes = process_runner.initialize_processes(processes)
    # Checks that state is immutable
    state_2 = run_processes(initial_state=state)
    assert state.a == 1
    assert state_2.a == 1  # hours ran
    state_2 = run_processes(initial_state=state)
    assert state.a == 2
    assert state_2.a == 2  # hours ran


def test_appending_to_state_list():
    """We can use '.+' to append to a list.

    This requires the process to set the format_output flag to true.
    """
    existing_logs = [
        {'a': 1, 'foo': 'bar'},
        {'a': 2, 'foo': 'barh'},
        {'a': 3, 'foo': 'barhum'},
        {'a': 4, 'foo': 'barhumb'},
    ]
    state = Mock_Model_State_Shape(
        1.1,
        2.2,
        logs=existing_logs,
    )
    new_log = {'a': 5, 'foo': 'barhumbug'},
    processes = [Process(
        func=lambda: new_log,
        # We have to use format output flag to enable this
        format_output=True,
        state_outputs=lambda result: [(result, 'logs.+')]
    )]
    process_runner = ProcessRunner()
    state_out = process_runner.run_processes(processes, state)
    assert state_out.logs[4] == new_log

def test_advance_time_step():
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
        advance_time_step_process(),
        Process(
            func=process_add,
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
    process_runner.DEBUG_MODE = True
    assert process_runner.tm.row_index == 0
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.c == 4
    assert state_2.d == 3.1
    assert process_runner.tm.row_index == 1

def test_reset_process_runner():
    process_runner.reset()
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
        advance_time_step_process(),
        Process(
            func=process_add,
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
    assert process_runner.tm.row_index == 0
    run_processes = process_runner.initialize_processes(processes)
    state_2 = run_processes(initial_state=state)
    assert state_2.c == 4
    assert state_2.d == 3.1
    assert process_runner.tm.row_index == 1
    process_runner.reset()
    assert process_runner.tm.row_index == 0
