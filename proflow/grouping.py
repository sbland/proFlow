from typing import List, Callable
from .Objects.Process import Process


def group(name: str) -> Callable[[List[Process]], List[Process]]:
    """Decorator to group processes returned by a function."""

    def decorator(fn):
        def wrapped_fn(*args, **kwargs):
            processes_out = fn(*args, **kwargs)
            # Below required if process class is frozen
            # processes_grouped = [Process(**{**p.__dict__, **{'group': name}})
            #                      for p in processes_out]
            for p in processes_out:
                p.group = name

            return processes_out
        return wrapped_fn
    return decorator
