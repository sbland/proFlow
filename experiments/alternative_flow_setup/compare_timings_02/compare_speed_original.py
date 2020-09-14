

# %%


import os
import sys
print(os.path)
module_path = os.path.abspath(os.path.join('../../'))
if module_path not in sys.path:
    sys.path.append(module_path)
# %%
# Allow relative import
from proflow.ProcessRunner import run_process
from proflow.Objects import Process, I
import numpy as np
import pytest

# %%

def process_add(x, y):
    return x + y


# %%
state = {
    'foo': {
        'bar': 123,
        "roo": 456,
        "lst": [1,2,3,4]
    },
}
config = {
    'hello': {
        'world': 'abc',
        'val': 3,
        "nested": {
            "really": {
                "deep": 9,
            }
        }
    }
}

# %%

demo_process = Process(
    func=process_add,
    gate=True,
    config_inputs=[
        I('hello.nested.really.deep', as_='y'),
    ],
    state_inputs=[
        I('foo.lst.1', as_='x'),
    ],
    state_outputs=[
        I('_result', as_='foo.bar'),
    ],
)


# %%
state_out = run_process(state, demo_process, config, None, None)

print(state_out)

# %%

# Compare timeings
from timeit import repeat


t1 = min(repeat(lambda: run_process(state, demo_process, config, None, None)))
print(t1)
#25.077121043999796
