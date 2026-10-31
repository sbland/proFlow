from copy import deepcopy
from timeit import repeat
from unittest.mock import patch

import numpy as np

from proflow.process_state_modifiers import (
    build_up_args,
    get_new_val_fn,
    map_result_to_state_fn,
    replace_state_val,
)

from ..objects.interface import I
from ..objects.process import Process
from .mocks import Mock_Model_State_Shape


def test_get_new_val():
    prev_state = Mock_Model_State_Shape(a=2.1, b=4.1)
    attr = prev_state.nested
    new_val = 99
    acc = {"na": new_val}
    new_obj = get_new_val_fn(attr, acc)
    assert new_obj.na == new_val
    assert prev_state.nested.na != new_val


def test_get_new_val_numpy():
    attr = np.arange(5)
    new_val = 99
    acc = {"3": new_val}
    new_obj = get_new_val_fn(attr, acc)
    assert new_obj[3] == new_val
    assert attr[3] != new_val


def test_get_new_val_list_append():
    attr = [1, 2, 3, 4]
    new_val = 99
    acc = {"+": new_val}
    new_obj = get_new_val_fn(attr, acc)
    assert new_obj[4] == new_val
    assert len(attr) < len(new_obj)


def test_build_up_args():
    state = {
        "abc": {
            "def": {
                "ghi": 1,
            },
        },
    }
    nxt = build_up_args(
        acc={"ghi": 3},
        i=1,
        target_split=["abc", "def", "ghi"],
        initial_state=state,
    )
    assert nxt == {
        "def": {
            "ghi": 3,
        },
    }

    nxt = build_up_args(
        acc={
            "def": {
                "ghi": 3,
            },
        },
        i=0,
        target_split=["abc", "def", "ghi"],
        initial_state=state,
    )

    assert nxt == {
        "abc": {
            "def": {
                "ghi": 3,
            },
        },
    }


def test_replace_state_val():
    prev_state = Mock_Model_State_Shape(a=2.1, b=4.1)
    new_val = 99
    new_state = replace_state_val(prev_state, "nested.na", new_val)
    assert new_state.nested.na == new_val
    assert prev_state.nested.na == 7


def test_map_result_to_state_fn():
    # def assign_result(prev_state, result):
    #     prev_state.nested.na = result['out']
    process = Process(
        func=lambda: {"out": "zzz"},
        config_inputs=lambda config: [
            I(config.foo, as_="x"),
        ],
        state_inputs=lambda state: [
            I(state.b),
            I(state.a, as_="y"),
        ],
        state_outputs=lambda result: [
            (result["out"], "nested.na"),
        ],
    )

    result = {"out": "zzz"}

    prev_state = Mock_Model_State_Shape(a=2.1, b=4.1)
    state_out = map_result_to_state_fn(
        prev_state,
        process.state_outputs,
        result,
    )

    # assert prev_state.nested.na == Mock_Model_State_Shape(a=2.1, b=4.1).nested.na
    # assert prev_state.nested.na == 7
    assert state_out.nested.na == "zzz"


def test_map_result_to_state_fn_copies_nested_list_once_for_sibling_updates():
    prev_state = Mock_Model_State_Shape(a=2.1, b=4.1)
    prev_state.logs = [{"value": 1}, {"value": 2}]
    updates = [
        (10, "logs.0.value"),
        (20, "logs.1.value"),
    ]

    with patch(
        "proflow.process_state_modifiers.deepcopy",
        wraps=deepcopy,
    ) as deepcopy_mock:
        state_out = map_result_to_state_fn(prev_state, lambda result: result, updates)

    assert deepcopy_mock.call_count == 1
    assert state_out.logs == [{"value": 10}, {"value": 20}]
    assert prev_state.logs == [{"value": 1}, {"value": 2}]
    assert state_out.logs is not prev_state.logs


def test_map_result_to_state_fn_copies_nested_dict_once_for_sibling_updates():
    prev_state = {"settings": {"left": 1, "right": 2}}
    updates = [
        (10, "settings.left"),
        (20, "settings.right"),
    ]

    with patch(
        "proflow.process_state_modifiers.deepcopy",
        wraps=deepcopy,
    ) as deepcopy_mock:
        state_out = map_result_to_state_fn(prev_state, lambda result: result, updates)

    assert deepcopy_mock.call_count == 1
    assert state_out == {"settings": {"left": 10, "right": 20}}
    assert prev_state == {"settings": {"left": 1, "right": 2}}


def test_batched_nested_updates_run_faster_than_sequential_copies():
    prev_state = {"entries": [{"value": i, "metadata": [i, i + 1]} for i in range(1_000)]}
    updates = [(i + 1, f"entries.{i}.value") for i in range(40)]

    def run_sequential_updates():
        state = prev_state
        for value, target in updates:
            state = replace_state_val(state, target, value)
        return state

    def run_batched_updates():
        return map_result_to_state_fn(prev_state, lambda result: result, updates)

    assert run_batched_updates() == run_sequential_updates()
    assert prev_state["entries"][0]["value"] == 0

    batched_time = min(repeat(run_batched_updates, number=2, repeat=3))
    sequential_time = min(repeat(run_sequential_updates, number=2, repeat=3))

    assert batched_time < sequential_time / 2, (
        f"batched updates took {batched_time:.6f}s; sequential updates took {sequential_time:.6f}s"
    )
