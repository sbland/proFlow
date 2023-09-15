from .Objects.Process import Process
from typing import Any, Union, List, Optional
from functools import reduce


def check_types(self):
    """ Checks all input types are correct. Raises Exception if not"""
    for field, field_type in self.__annotations__.items():
        actual_field_type = getattr(self, field)
        if actual_field_type is not None and not isinstance(actual_field_type, field_type):
            raise TypeError('{} must be {} but is {}'
                            .format(field, field_type, actual_field_type))
    return self


def assert_defined(val):
    assert val is not None


def skip():
    pass


def NOT_IMPLEMENTED_PROCESS(message: str):
    return Process(
        func=lambda: NotImplementedError(message),
        comment=message,
    )


def set_value(**kwargs) -> dict:
    '''A simple helper function to use in process runner to set a value
    It works by returning th input value within a dict'''
    return kwargs


def log_value(*args, **kwargs) -> dict:
    '''A simple helper function to use in process runner to log a value'''
    print(*args, *kwargs.values())
    return None


def print_process(**kwargs) -> Process:
    return Process(
        func=log_value,
        **kwargs
    )


def rgetattr(obj: object, attr: Union[str, List[str]], *args):
    """Get nested properties with dot notation or list of string path.

    https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-subobjects-chained-properties

    Properties
    ----------
    obj: object  [description]
    attr: OneOf[str, List[str]]  Either a dot notation string or list of strings
    """
    def _getattr(obj, attr):
        return obj[int(attr)] if isinstance(obj, list) \
            else obj[int(attr)] if type(obj).__module__ == 'numpy' \
            else obj[attr] if isinstance(obj, dict) \
            else getattr(obj, attr, *args)
    attr_list = attr if isinstance(attr, list) else attr.split(
        '.') if isinstance(attr, str) else [attr]
    return reduce(_getattr, [obj] + attr_list)


def rsetattr(obj: object, attr: Union[str, List[str]], val: Any):
    """Set nested attributes with dot string path or string list

    https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-subobjects-chained-properties

    Properties
    ----------
    obj: object  [description]
    attr: OneOf[str, List[str]]  Either a dot notation string or list of strings
    val: any
    """
    # obj_copy = deepcopy(obj) # deep copy takes 10 times as long!
    obj_copy = obj
    pre, _, post = [attr[0], '.', '.'.join(attr[1:])] if isinstance(attr, list) \
        else attr.rpartition('.') if isinstance(attr, str) else [None, None, attr]
    # target = deepcopy(rgetattr(obj, pre) if pre else obj)
    target = rgetattr(obj_copy, pre) if pre else obj_copy
    if isinstance(target, list):
        target[int(post)] = val
    elif isinstance(target, dict):
        target[post] = val
    else:
        setattr(target, post, val)
    return obj_copy


def lget(v: Optional[List[any]], i: int, fallback_value=None) -> any:
    """Safely get a value from a list with index and fallback value.

    Parameters
    ----------
    v : Optional[List[any]]
        Input list may be null
    i : int
        Index
    fallback_value : [type], optional
        Value to use if v is null, by default None

    Returns
    -------
    any
        Return value

    """
    try:
        return v[i]
    except (TypeError, IndexError):
        return fallback_value


def nullop():
    return None


def tag_process(comment):
    return Process(
        func=nullop,
        comment=comment,
    )


def perNlc(nLC, fn, *args, **kwargs):
    return [fn(iLC, *args, **kwargs) for iLC in range(nLC)],


def raise_error(e):
    """Allow raising an error in a lambda function."""
    raise e from e


def accumulate(**kwargs):
    out = sum(kwargs.values())
    return out
