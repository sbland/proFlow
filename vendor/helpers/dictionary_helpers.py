from dataclasses import is_dataclass
from functools import reduce

import numpy as np

from .comparisons import isNamedTuple


def get_nested_arg_from_dict(data: dict, location_str: str):
    """ Helper function to get a value from a dictionary
    when given a dot notation string

    e.g.

    ```
    data = {
        'foo': 1,
        'bar': {
            'roo': 4,
            'ree': {
                'sow': 10,
                }
            },
        'arr': [1, 2, 3],
        'a': A(),
        }
    ```

    ```
    result = get_nested_arg_from_dict(data, 'bar.ree.sow')
    assert result == 10
    result = get_nested_arg_from_dict(data, 'arr.1')
    assert result == 2
    ```
    """
    location = location_str.split('.')

    def get_val(acc, k):
        val = None
        val = acc[k] if isinstance(acc, dict) else val
        val = acc[int(k)] if isinstance(acc, list) else val
        val = acc[int(k)] if isinstance(acc, np.ndarray) else val
        val = acc._asdict()[k] if isNamedTuple(acc) else val
        val = getattr(acc, k) if is_dataclass(acc) else val
        if val is None:
            print(acc)
            raise ValueError('Value not found in object')
        return val
        # TODO: Optimize
    result = reduce(get_val, location, data)
    return result
