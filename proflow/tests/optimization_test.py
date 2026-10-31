from copy import deepcopy
from timeit import repeat
from unittest.mock import patch

import pytest
from data_helpers.list_helpers import flatten_list

from proflow.helpers import rgetattr
from proflow.process_ins_and_outs import get_inputs_from_process, map_result_to_state
from proflow.process_runner import ProcessRunner
from proflow.tests.mocks import (
    Mock_Config_Shape,
    Mock_External_State_Shape,
    Mock_Model_State_Shape,
    Mock_Parameters_Shape,
)

from ..objects.interface import I
from ..objects.process import Process


def process_add(x, y):
    return x + y


process_runner = ProcessRunner(
    Mock_Config_Shape(), Mock_External_State_Shape(), Mock_Parameters_Shape()
)


@pytest.fixture(scope="module", autouse=True)
def _():
    with patch(
        "proflow.process_runner.Model_State_Shape", side_effect=Mock_Model_State_Shape
    ) as Mocked_State_Shape:
        Mocked_State_Shape.__annotations__ = Mock_Model_State_Shape.__annotations__
        yield Mocked_State_Shape


@pytest.fixture(scope="module", autouse=True)
def __():
    with patch("proflow.process_runner.Config_Shape", return_value=Mock_Config_Shape) as _fixture:
        yield _fixture


@pytest.fixture(scope="module", autouse=True)
def ____():
    with patch(
        "proflow.process_runner.Parameters_Shape", return_value=Mock_Parameters_Shape
    ) as _fixture:
        yield _fixture


@pytest.fixture(scope="module", autouse=True)
def ______():
    with patch(
        "proflow.process_runner.External_State_Shape", return_value=Mock_External_State_Shape
    ) as _fixture:
        yield _fixture


def test_process_runner_time():
    state = Mock_Model_State_Shape(a=2.1, b=4.1)
    processes = flatten_list(
        [
            Process(
                func=lambda x, y: x + y,
                config_inputs=lambda config: [
                    I(config.foo, as_="x"),
                    I(config.bar, as_="y"),
                ],
                state_outputs=lambda result: [
                    (result, "c"),
                ],
            ),
            Process(
                func=lambda x, y: x + y,
                config_inputs=lambda config: [
                    I(config.foo, as_="x"),
                ],
                state_inputs=lambda state: [
                    I(rgetattr(state.matrix[0], state.ind), as_="y"),
                ],
                state_outputs=lambda result: [
                    (result, "c"),
                ],
            ),
            [
                Process(
                    func=lambda x, y: x + y,
                    config_inputs=lambda config: [
                        I(config.foo, as_="x"),
                    ],
                    additional_inputs=lambda i=i: [
                        I(i, as_="y"),
                    ],
                    state_outputs=lambda result: [
                        (result, "d"),
                    ],
                )
                for i in range(5)
            ],
        ]
    )
    run_processes = process_runner.initialize_processes(processes)

    time = min(repeat(lambda: run_processes(initial_state=state), number=2000, repeat=5))
    # assert 0.220 < time < 0.26 # Times with old method
    assert 0.01 < time < 0.08


@pytest.mark.parametrize("debug_mode", [False, True])
def test_immutable_mode_preserves_input_state_and_shares_untouched_fields(debug_mode):
    state = Mock_Model_State_Shape(a=2.1, b=4.1)
    process = Process(
        func=lambda value: value + 1,
        state_inputs=lambda state: [I(state.a, as_="value")],
        state_outputs=lambda result: [(result, "nested.na")],
    )
    process_runner = ProcessRunner(
        Mock_Config_Shape(),
        Mock_External_State_Shape(),
        Mock_Parameters_Shape(),
        DEBUG_MODE=debug_mode,
        IMMUTABLE_MODE=True,
    )

    updated_state = process_runner.initialize_processes([process])(initial_state=state)

    assert updated_state is not state
    assert updated_state.nested is not state.nested
    assert updated_state.nested.na == 3.1
    assert state.nested.na == 7
    assert updated_state.matrix is state.matrix
    assert updated_state.logs is state.logs


def test_immutable_mode_runs_faster_than_copying_the_entire_state():
    state = Mock_Model_State_Shape(a=2.1, b=4.1)
    state.logs = [{"index": i, "values": [i, i + 1]} for i in range(10_000)]
    process = Process(
        func=lambda value: value + 1,
        state_inputs=lambda state: [I(state.a, as_="value")],
        state_outputs=lambda result: [(result, "a")],
    )
    process_runner = ProcessRunner(
        Mock_Config_Shape(),
        Mock_External_State_Shape(),
        Mock_Parameters_Shape(),
        IMMUTABLE_MODE=True,
    )
    run_optimized = process_runner.initialize_processes([process])

    def run_with_full_state_copy():
        modified_state = deepcopy(state)
        args, kwargs = get_inputs_from_process(
            process,
            modified_state,
            process_runner.config,
            process_runner.parameters,
            process_runner.external_state,
            process_runner.tm.row_index,
        )
        result = process.func(*args, **kwargs)
        return map_result_to_state(modified_state, process.state_outputs, result)

    optimized_time = min(repeat(lambda: run_optimized(initial_state=state), number=5, repeat=3))
    full_copy_time = min(repeat(run_with_full_state_copy, number=5, repeat=3))

    assert optimized_time < full_copy_time / 2


def test_immutable_mode_speed_compared_to_mutable_mode():
    def make_state():
        state = Mock_Model_State_Shape(a=0, b=0)
        state.logs = [{"index": i, "values": [i, i + 1]} for i in range(10_000)]
        return state

    process = Process(
        func=lambda: 1,
        state_outputs=lambda result: [(result, "a")],
    )
    immutable_runner = ProcessRunner(
        Mock_Config_Shape(),
        Mock_External_State_Shape(),
        Mock_Parameters_Shape(),
        IMMUTABLE_MODE=True,
    ).initialize_processes([process])
    mutable_runner = ProcessRunner(
        Mock_Config_Shape(),
        Mock_External_State_Shape(),
        Mock_Parameters_Shape(),
        IMMUTABLE_MODE=False,
    ).initialize_processes([process])
    immutable_state = make_state()
    mutable_state = make_state()

    assert immutable_runner(initial_state=immutable_state).a == 1
    assert mutable_runner(initial_state=mutable_state).a == 1
    assert immutable_state.a == 0
    assert mutable_state.a == 1

    immutable_time = min(
        repeat(lambda: immutable_runner(initial_state=immutable_state), number=1_000, repeat=5)
    )
    mutable_time = min(
        repeat(lambda: mutable_runner(initial_state=mutable_state), number=1_000, repeat=5)
    )

    assert mutable_time < immutable_time / 2, (
        f"mutable mode took {mutable_time:.6f}s; immutable mode took {immutable_time:.6f}s"
    )


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
