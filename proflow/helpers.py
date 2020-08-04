from .Objects import Process


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
