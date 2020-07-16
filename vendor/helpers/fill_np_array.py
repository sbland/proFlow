from functools import reduce
import numpy as np


def product(a, b):
    return a * b


def get_np_element_count(shape: tuple):
    return reduce(product, shape)


def fill_np_array_with_cls(shape: tuple, cls: type, read_only: bool = True, *args, **kwargs) -> np.ndarray:
    """Takes a class and length and fills a 1d numpy array"""
    shape_b = shape if isinstance(shape, tuple) else (shape, )
    flattened_length = get_np_element_count(shape_b)
    list_flat = np.empty(flattened_length, cls)
    list_flat[:] = [cls(*args, **kwargs) for i in range(flattened_length)]
    list_out = list_flat.reshape(shape_b)
    if read_only:
        list_out.flags.writeable = False
    return list_out
