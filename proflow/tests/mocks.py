from dataclasses import dataclass, field
from typing import List


@dataclass
class Mock_Nested_State:
    na: int = 7
    nab: int = 7


# @dataclass
# class Mock_Temporal_State:
#     hr: int = 0
#     dd: int = 0
#     row_index: int = 0


@dataclass
class Mock_Model_State_Shape:
    a: float
    b: float
    # temporal: Mock_Temporal_State = field(default_factory=lambda: Mock_Temporal_State())
    c: float = 0
    d: float = 0
    ind: int = 0
    target: str = "a"
    lst: List[str] = None
    nested: Mock_Nested_State = field(default_factory=lambda: Mock_Nested_State())
    matrix: List[List[float]] = field(default_factory=lambda: [[1, 2, 3], [4, 5, 6]])
    nested_lst_obj: List[Mock_Nested_State] = field(
        default_factory=lambda: [Mock_Nested_State(1, 2), Mock_Nested_State(3, 4)])

    logs: List[dict] = field(default_factory=lambda: [])


@dataclass
class Mock_Config_Shape:
    foo: int = 1
    bar: int = 3
    roo: dict = field(default_factory=lambda: {
        'abc': 5
    })
    arr: List[int] = field(default_factory=lambda: [1, 2, 3])


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
    data_a: List[int] = field(default_factory=lambda: [1, 1, 2, 3])
    data_b: List[int] = field(default_factory=lambda: [5, 1, 2, 3])
