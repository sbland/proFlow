from dataclasses import dataclass, field
from typing import List


@dataclass
class Mock_Nested_State:
    na: int = 7
    nab: int = 7


@dataclass
class Mock_Model_State_Shape:
    a: float
    b: float
    c: float = 0
    d: float = 0
    ind: int = 0
    target: str = "a"
    lst: list = None
    nested: Mock_Nested_State = Mock_Nested_State()
    matrix: List[List] = field(default_factory=lambda: [[1, 2, 3], [4, 5, 6]])
    nested_lst_obj: List[Mock_Nested_State] = field(default_factory=lambda: [Mock_Nested_State(1,2), Mock_Nested_State(3,4)])


@dataclass
class Mock_Config_Shape:
    foo: int = 1
    bar: int = 3
    roo: dict = field(default_factory=lambda: {
        'abc': 5
    })
    arr: list = field(default_factory=lambda: [1, 2, 3])


@dataclass
class Mock_Parameters_Shape:
    foo: int = 1
    bar: int = 3
    roo: dict = field(default_factory=lambda: {
        'abc': 5
    })
    arr: list = field(default_factory=lambda: [1, 2, 3])


@dataclass
class Mock_External_State_Shape:
    data_a: int = 1
    data_b: int = 5
