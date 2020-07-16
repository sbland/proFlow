def check_types(self):
    """ Checks all input types are correct. Raises Exception if not"""
    for field, field_type in self.__annotations__.items():
        actual_field_type = getattr(self, field)
        if actual_field_type is not None and not isinstance(actual_field_type, field_type):
            raise TypeError('{} must be {} but is {}'
                            .format(field, field_type, actual_field_type))
    return self
