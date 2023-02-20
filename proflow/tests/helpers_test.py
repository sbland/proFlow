from dataclasses import dataclass, field
from vendor.test_helpers import use_benchmark_time
import numpy as np
from timeit import repeat
from ..helpers import rgetattr, rsetattr


# def test_get_key_values():
#     data = {'key_from': 123}
#     def process_str_fn(x): return x
#     k_vs = get_key_values(process_str_fn, data, [I('key_from', as_='key_to')])
#     assert k_vs == ([('key_to', 123)], [])
#     k_vs = get_key_values(process_str_fn, data, [I('key_from')])
#     assert k_vs == ([], [123])


# def test_get_key_values_assert_required():
#     """Asserts that a required value in the input_keys is not None."""
#     data = {'key_from': 123, 'key_from_missing': None}
#     def process_str_fn(x): return x

#     # does not fail if not required or not Debug mode
#     k_vs = get_key_values(process_str_fn, data, [I('key_from_missing', as_='key_to')])
#     assert k_vs == ([('key_to', None)], [])
#     k_vs = get_key_values(process_str_fn, data, [I('key_from_missing', as_='key_to')], DEBUG=True)
#     assert k_vs == ([('key_to', None)], [])
#     k_vs = get_key_values(process_str_fn,
#                           data,
#                           [I('key_from_missing', as_='key_to', required=True)],
#                           )
#     assert k_vs == ([('key_to', None)], [])

#     # fails if required and debug mode
#     with pytest.raises(ValueError) as exc:
#         get_key_values(process_str_fn,
#                        data,
#                        [I('key_from_missing', as_='key_to', required=True)],
#                        DEBUG=True)
#     assert 'Input is required: key_from_missing' in str(exc)


def test_rgetattr():
    v = rgetattr([1, 2, 3], 0)
    assert v == 1
    v = rgetattr({'foo': {'bar': 3}}, 'foo.bar')
    assert v == 3
    v = rgetattr({'foo': {'bar': 3}}, ['foo', 'bar'])
    assert v == 3


def test_rgetattr_numpy():
    v = rgetattr(np.arange(5), 3)
    assert v == 3


def test_rgetattr_convert_str_index():
    v = rgetattr([[1, 2, 3], [4, 5, 6]], '1.2')
    assert v == 6


def test_rsetattr():
    v = rsetattr([1, 2, 3], 0, 7)
    assert v == [7, 2, 3]
    v = rsetattr({'foo': {'bar': 3}}, 'foo', 'zzz')
    assert v == {'foo': 'zzz'}
    v = rsetattr({'foo': {'bar': 3}}, 'foo.bar', 'zzz')
    assert v == {'foo': {'bar': 'zzz'}}
    v = rsetattr({'foo': {'bar': 3}}, ['foo', 'bar'], 'zzz')
    assert v == {'foo': {'bar': 'zzz'}}


def test_rsetattr_with_dataclass():
    @dataclass
    class Nested:
        roo: int = 99

    @dataclass
    class Foo:
        bar: int = 0
        nest: Nested = field(default_factory=lambda: Nested())

    v = rsetattr(Foo(), 'nest.roo', 4)
    assert v.nest.roo == 4


def test_rsetattr_time(benchmark_fixture):
    obj = {'foo': {'bar': 3}}
    t1 = min(repeat(lambda: rsetattr(obj, 'foo', 'zzz')))
    assert t1 < 0.4/benchmark_fixture

# TODO: Can we implement a version that does not mutate
# def test_rsetattr_mutation():
#     obj = {'foo': {'bar': [1, 2, 3]}}
#     v = rsetattr(obj, 'foo.bar.1', 99)
#     assert v == {'foo': {'bar': [1, 99, 3]}}
#     assert obj == {'foo': {'bar': [1, 2, 3]}}
