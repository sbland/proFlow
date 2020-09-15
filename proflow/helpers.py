from .Objects import Process
from typing import Union, List
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

    Properties
    ----------
    obj: object  [description]
    attr: OneOf[str, List[str]]  Either a dot notation string or list of strings
    """
    def _getattr(obj, attr):
        return obj[attr] if (isinstance(obj, list) or isinstance(obj, dict)) \
            else getattr(obj, attr, *args)
    attr_list = attr if isinstance(attr, list) else attr.split(
        '.') if isinstance(attr, str) else [attr]
    return reduce(_getattr, [obj] + attr_list)
