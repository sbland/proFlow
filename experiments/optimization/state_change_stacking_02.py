
# %%
from timeit import repeat
from random import randint
from dataclasses import dataclass, field
from typing import List


@dataclass
class Nest:
    na: int = 1
    nb: int = 2


@dataclass
class State:
    foo: str = 'foo'
    bar: float = 1.2
    nested: Nest = field(default_factory=lambda: Nest())
    matrix: List[List[Nest]] = field(
        default_factory=lambda: [[Nest(i, j)
                                  for i in range(2)] for j in range(2)])


state = State()


# %%
# Convert config to a flat numpy matrix

def first_substring(strings, substring):
    return next(i for i, string in enumerate(strings) if substring in string)


def last_substring(strings, substring):
    return next(i for i, string in enumerate(reversed(strings)) if substring in string)


state_map_initial = [
    'foo',
    'bar',
    'nested.na',
    'nested.nb',
    'matrix.0.0.na',
    'matrix.0.0.nb',
    'matrix.0.1.na',
    'matrix.0.1.nb',
    'matrix.1.0.na',
    'matrix.1.0.nb',
    'matrix.1.1.na',
    'matrix.1.1.nb',
]

state_flat_initial = [
    'foo',
    1.2,
    1,
    2,
    0,
    0,
    0,
    1,
    1,
    0,
    1,
    1,
]

# %%

state_flat_initial[first_substring(state_map, 'matrix.0.1.nb')]
# %%
state.matrix[0][1].nb

# %%
# Changing state
# When we change the state we simply append to the end of the state list and update the mapping

# state_flat_initial.append(5)
# state_map.append('matrix.0.1.nb')

# # %%
# index = len(state_map) - last_substring(state_map, 'matrix.0.1.nb') - 1
# index
# # %%
# last_substring(state_map, 'matrix.0.1.nb')
# # %%
# state_flat[index]

# %%


def write_to_state(st, mp, key, value):
    st.append(value)
    mp.append(key)


def read_from_state(st, mp, key):
    index = len(mp) - last_substring(mp, key) - 1
    return st[index]


# %%
# Setup data
state_out = state_flat_initial
state_map_in = state_map_initial
for i in range(100):
    k = randint(0, len(state_map_in) - 1)
    write_to_state(state_out, state_map_in, state_map_in[k], value=randint(0, 40))

# %%

read_from_state(state_out, state_map_in, 'matrix.0.1.nb')

# %%

# Read time


def read_run():
    for i in range(len(state_map_initial) - 1):
        read_from_state(state_out, state_map_in, state_map_initial[i])


# %%
t_read = min(repeat(lambda: read_run(), number=1000, repeat=40))
t_read


# %%
# standard read time
def read_run_standard():
    state.foo
    state.bar
    state.nested.na
    state.nested.nb
    state.matrix[0][0].na
    state.matrix[0][0].nb
    state.matrix[0][1].na
    state.matrix[0][1].nb
    state.matrix[1][0].na
    state.matrix[1][0].nb
    state.matrix[1][1].na
    state.matrix[1][1].nb

t_read = min(repeat(lambda: read_run_standard(), number=1000, repeat=40))
t_read