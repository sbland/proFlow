from .process_runner import Process


def switch(
    gate: str, comment: str | None = None, options=None, default_option=None, **kwargs
) -> Process:
    if options is None:
        options = {}
    options = {**options, **kwargs}
    try:
        return options.get(gate, default_option) if default_option is not None else options[gate]
    except KeyError:
        raise KeyError(f'"{gate}" is not an option in "{comment}" switch')


__s__ = switch
