from .time_data import get_row


def test_get_row():
    row_index = get_row(0, 0)
    assert row_index == 0
    row_index = get_row(0, 1)
    assert row_index == 1
    row_index = get_row(1, 0)
    assert row_index == 24
    row_index = get_row(1, 1)
    assert row_index == 25
