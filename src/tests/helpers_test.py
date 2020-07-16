from ..ProcessRunner import get_key_values, I


def test_get_key_values():
    k_vs = get_key_values(lambda x: x, lambda k: k, [I('key_from', as_='key_to')])
    assert k_vs == ([('key_to', 'key_from')], [])
    k_vs = get_key_values(lambda x: x, lambda k: k, [I('key_from')])
    assert k_vs == ([], [('key_from')])
