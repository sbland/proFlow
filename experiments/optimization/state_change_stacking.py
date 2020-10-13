
# %%
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
    matrix: List[List[Nest]] = field(default_factory=lambda: [[Nest(i, j)
                                                               for i in range(2)] for j in range(2)])


state = State()


# %%
# Convert config to a flat numpy matrix


# expected_output = [
#     'foo',
#     1.2,
#     1,
#     2,
#     ...
# ]

state_map = {
    'foo': 0,
    'bar': 1,
    'nested.na': 2,
    'nested.nb': 3,
    'matrix.0.0.na': 4,
    'matrix.0.0.nb': 5,
    'matrix.0.1.na': 6,
    'matrix.0.1.nb': 7,
    'matrix.1.0.na': 8,
    'matrix.1.0.nb': 9,
    'matrix.1.1.na': 10,
    'matrix.1.1.nb': 11,
}

state_flat = [
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

state_flat[state_map['matrix.0.0.nb']]
# %%
state.matrix[0][0].nb

# %%
# Changing state
# When we change the state we simply append to the end of the state list and update the mapping

state_flat.append(5)
state_map['matrix.0.1.na'] = len(state_flat) - 1

[state_flat[i] for i in state_map.values()]

# to rewind state
