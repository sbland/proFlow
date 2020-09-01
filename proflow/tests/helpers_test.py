import pytest
from ..ProcessRunner import get_key_values, I


def test_get_key_values():
    data = {'key_from': 123}
    def process_str_fn(x): return x
    k_vs = get_key_values(process_str_fn, data, [I('key_from', as_='key_to')])
    assert k_vs == ([('key_to', 123)], [])
    k_vs = get_key_values(process_str_fn, data, [I('key_from')])
    assert k_vs == ([], [123])


def test_get_key_values_assert_required():
    """Asserts that a required value in the input_keys is not None."""
    data = {'key_from': 123, 'key_from_missing': None}
    def process_str_fn(x): return x

    # does not fail if not required or not Debug mode
    k_vs = get_key_values(process_str_fn, data, [I('key_from_missing', as_='key_to')])
    assert k_vs == ([('key_to', None)], [])
    k_vs = get_key_values(process_str_fn, data, [I('key_from_missing', as_='key_to')], DEBUG=True)
    assert k_vs == ([('key_to', None)], [])
    k_vs = get_key_values(process_str_fn,
                          data,
                          [I('key_from_missing', as_='key_to', required=True)],
                          )
    assert k_vs == ([('key_to', None)], [])

    # fails if required and debug mode
    with pytest.raises(ValueError) as exc:
        get_key_values(process_str_fn,
                       data,
                       [I('key_from_missing', as_='key_to', required=True)],
                       DEBUG=True)
    assert 'Input is required: key_from_missing' in str(exc)
