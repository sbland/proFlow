
# %%
from dataclasses import astuple, dataclass
from collections import namedtuple
from functools import reduce
from timeit import repeat
print('------------------------------------------')
@dataclass(frozen=True)
class I:  # noqa: E742
    """interface Named Tuple"""
    from_: any
    as_: str = None
    required: bool = False  # If true then is asserted != null on debug mode
    u_from: str = None
    u_as: str = None

    def __repr__(self) -> str:
        return f'I(from_="{self.from_}" as_="{self.as_}")'

    def asdict(self):
        out = {}
        out[self.as_] = self.from_
        return out


config = {
    'hello': {
        'world': 'abc',
        'val': 3
    }
}
# %%
config_args = [
    I(config['hello']['val'], as_='y', u_from='nmol', u_as='mmol'),
]

state_args = [
    I(config['hello']['val'], as_='x', u_from='nmol', u_as='mmol'),
]

method_a = lambda: dict((i.as_, i.from_) for i in config_args + state_args)
t1 = min(repeat(method_a))
print('method_a', method_a())
t1

# %%
config_args = [
    I(config['hello']['val'], as_='y', u_from='nmol', u_as='mmol'),
]

state_args = [
    I(config['hello']['val'], as_='x', u_from='nmol', u_as='mmol'),
]

def addToDict(acc, v):
    acc[v.as_] = v.from_
    return acc
method_b = lambda: reduce(addToDict, config_args + state_args, {})
t1 = min(repeat(method_b))
print('method_b', method_b())
t1

# %%
config_args = [
    I(config['hello']['val'], as_='y', u_from='nmol', u_as='mmol'),
]


state_args = [
    I(config['hello']['val'], as_='x', u_from='nmol', u_as='mmol'),
]

method_c = lambda: {i.as_: i.from_ for i in config_args + state_args}
t1 = min(repeat(method_c))
print('method_c', method_c())
t1


#############################################################
# %%

config_args= {
    'y': config['hello']['val'],
}

state_args= {
    'x': config['hello']['val'],
}


method_d = lambda: {**config_args, **state_args} # fastest method
t2= min(repeat(method_d))
print('method_d', method_d())
t2

# %%
config_args = [
    ('y', config['hello']['val'], 'nmol', 'mmol'),
]
state_args = [
    ('x', config['hello']['val'], 'nmol', 'mmol'),
]

method_e = lambda: {k: v for k, v, x, y in config_args + state_args}
t1 = min(repeat(method_e))
print('method_e', method_e())
t1
# %%
IB = namedtuple('a', 'as_ from_ unit_as unit_from')
config_args = [
    IB(as_='y', from_=config['hello']['val'], unit_as='nmol', unit_from='mmol'),
]
state_args = [
    IB(as_='x', from_=config['hello']['val'], unit_as='nmol', unit_from='mmol'),
]

method_f = lambda: {k: v for k, v, x, y in config_args + state_args}
t1 = min(repeat(method_f))
print('method_f', method_f())
t1
