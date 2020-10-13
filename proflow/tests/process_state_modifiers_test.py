from timeit import repeat
import numpy as np

from .mocks import Mock_Model_State_Shape
from ..Objects.Interface import I
from ..Objects.Process import Process
from proflow.process_state_modifiers import build_up_args, get_new_val_fn, replace_state_val, \
    map_result_to_state_fn


def test_get_new_val():
    prev_state = Mock_Model_State_Shape(a=2.1, b=4.1)
    attr = prev_state.nested
    new_val = 99
    acc = {'na': new_val}
    new_obj = get_new_val_fn(attr, acc)
    assert new_obj.na == new_val
    assert prev_state.nested.na != new_val


def test_get_new_val_numpy():
    attr = np.arange(5)
    new_val = 99
    acc = {'3': new_val}
    new_obj = get_new_val_fn(attr, acc)
    assert new_obj[3] == new_val
    assert attr[3] != new_val


def test_get_new_val_list_append():
    attr = [1, 2, 3, 4]
    new_val = 99
    acc = {'+': new_val}
    new_obj = get_new_val_fn(attr, acc)
    assert new_obj[4] == new_val
    assert len(attr) < len(new_obj)


def test_build_up_args():
    state = {
        'abc': {
            'def': {
                'ghi': 1,
            },
        },
    }
    nxt = build_up_args(
        acc={'ghi': 3},
        i=1,
        target_split='abc.def.ghi'.split('.'),
        initial_state=state,
    )
    assert nxt == {
        'def': {
            'ghi': 3,
        },
    }

    nxt = build_up_args(
        acc={
            'def': {
                'ghi': 3,
            },
        },
        i=0,
        target_split='abc.def.ghi'.split('.'),
        initial_state=state,
    )

    assert nxt == {
        'abc': {
            'def': {
                'ghi': 3,
            },
        },
    }


def test_replace_state_val():
    prev_state = Mock_Model_State_Shape(a=2.1, b=4.1)
    new_val = 99
    new_state = replace_state_val(prev_state, 'nested.na', new_val)
    assert new_state.nested.na == new_val
    assert prev_state.nested.na == 7


def test_map_result_to_state_fn():
    # def assign_result(prev_state, result):
    #     prev_state.nested.na = result['out']
    process = Process(
        func=lambda: {'out': 'zzz'},
        config_inputs=lambda config: [
            I(config.foo, as_='x'),
        ],
        state_inputs=lambda state: [
            I(state.b),
            I(state.a, as_='y'),
        ],
        state_outputs=lambda result: [
            (result['out'], 'nested.na'),
        ],
    )

    result = {'out': 'zzz'}

    prev_state = Mock_Model_State_Shape(a=2.1, b=4.1)
    state_out = map_result_to_state_fn(
        prev_state,
        process.state_outputs,
        result,
    )

    # assert prev_state.nested.na == Mock_Model_State_Shape(a=2.1, b=4.1).nested.na
    # assert prev_state.nested.na == 7
    assert state_out.nested.na == 'zzz'
