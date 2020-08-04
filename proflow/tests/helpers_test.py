from ..ProcessRunner import get_key_values, I


def test_get_key_values():
    data = {'key_from': 123}
    process_str_fn = lambda x: x
    k_vs = get_key_values(process_str_fn, data, [I('key_from', as_='key_to')])
    assert k_vs == ([('key_to', 123)], [])
    k_vs = get_key_values(process_str_fn, data, [I('key_from')])
    assert k_vs == ([], [123])
