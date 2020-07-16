from collections import namedtuple
import numpy as np
import pytest

from . import fill_np_array


def test_get_numpy_element_count():
    shape = (1, 2, 3,)
    count = fill_np_array.get_np_element_count(shape)
    assert count == 6


def test_fill_np_array():
    cls = namedtuple('clstest', 'a b c')
    filled_matrix = fill_np_array.fill_np_array_with_cls((2, 3, ), cls, a=1, b=2, c=3)
    assert filled_matrix[0][0] == cls(a=1, b=2, c=3)
    assert filled_matrix.shape == (2, 3, )


def test_filled_array_is_immutable():
    cls = namedtuple('clstest', 'a b c')
    filled_matrix = fill_np_array.fill_np_array_with_cls((2, 3, ), cls, a=1, b=2, c=3)
    assert filled_matrix[0][0] == cls(a=1, b=2, c=3)
    altered_matrix = filled_matrix
    with pytest.raises(Exception):
        altered_matrix[0][0] = cls(a=2, b=2, c=3)
    altered_matrix_as_copy = np.array(filled_matrix)
    altered_matrix_as_copy[0][0] = cls(a=2, b=2, c=3)
    assert altered_matrix_as_copy[0][0] == cls(a=2, b=2, c=3)
    assert filled_matrix[0][0] == cls(a=1, b=2, c=3)
