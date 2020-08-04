from .ProcessRunner import Process


def switch(
        gate: str,
        comment: str = None,
        options={},
        default_option=None,
        **kwargs
) -> Process:
    options = {**options, **kwargs}
    return options.get(gate, default_option) \
        if default_option is not None else options[gate]


__s__ = switch
