from timeit import repeat
import numpy as np

from ..helpers import rsetattr
from ..process_ins_and_outs import get_inputs_from_process, \
    map_result_to_state
from ..Objects.Interface import I
from ..Objects.Process import Process
from .mocks import Mock_Config_Shape, Mock_External_State_Shape, \
    Mock_Model_State_Shape, Mock_Parameters_Shape


def test_get_inputs_from_process():
    process = Process(
        func=lambda: [1, 2, 3],
        config_inputs=lambda config: [
            I(config.foo, as_='x'),
        ],
        state_inputs=lambda state: [
            I(state.b),
            I(state.a, as_='y'),
        ],
        external_state_inputs=lambda e_state, row_index: [
            I(e_state.data_a[row_index], as_='z'),
        ],
        state_outputs=lambda prev_state, result: [
            rsetattr(prev_state, 'nested.na', result[0]),
        ],
        args=[1, 2, 3]
    )

    args, kwargs = get_inputs_from_process(
        process,
        Mock_Model_State_Shape(a=2.1, b=4.1),
        Mock_Config_Shape(),
        Mock_Parameters_Shape(),
        Mock_External_State_Shape(),
        0,
    )

    assert args == [1, 2, 3, 4.1]
    assert kwargs == {'x': 1, 'y': 2.1, 'z': 1}


def test_map_result_to_state():
    process = Process(
        func=lambda: {'out': 'zzz'},
        config_inputs=lambda config: [
            I(config.foo, as_='x'),
        ],
        state_inputs=lambda state: [
            I(state.b),
            I(state.a, as_='y'),
        ],
        state_outputs=lambda result: (
            (result['out'], 'nested.na'),
        )
    )

    result = {'out': 'zzz'}

    prev_state = Mock_Model_State_Shape(a=2.1, b=4.1)
    state_out = map_result_to_state(
        prev_state,
        process.state_outputs,
        result,
    )

    assert state_out.nested.na == 'zzz'


# def test_map_result_to_state_timeit():
#     process = Process(
#         func=lambda: {'out': 'zzz'},
#         config_inputs=lambda config: [
#             I(config.foo, as_='x'),
#         ],
#         state_inputs=lambda state: [
#             I(state.b),
#             I(state.a, as_='y'),
#         ],
#         state_outputs=[
#             I('out', as_='nested.na'),
#         ],
#     )

#     result = {'out': 'zzz'}

#     prev_state = Mock_Model_State_Shape(a=2.1, b=4.1)
#     t1 = min(repeat(lambda: map_result_to_state(
#         prev_state,
#         process.state_outputs,
#         result,
#     ), number=1000, repeat=20))

#     assert 0.00159 < t1 < 0.008


# def test_map_result_to_state_numpy_datatype():
#     process = Process(
#         func=lambda: 3,
#         config_inputs=lambda config: [
#             I(config.foo, as_='x'),
#         ],
#         state_inputs=lambda state: [
#             I(state.b),
#             I(state.a, as_='y'),
#         ],
#         state_outputs=[
#             I('_result', as_='1'),
#         ],
#     )

#     result = 3

#     prev_state = np.arange(5)
#     state_out = map_result_to_state(
#         prev_state,
#         process.state_outputs,
#         result,
#     )

#     assert state_out[1] == result
