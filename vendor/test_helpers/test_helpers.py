"""Various helper functions and decorators for pytest."""
from functools import wraps
import pytest
from timeit import repeat

benchmark_time = None


def get_benchmark_time():
    """Get a benchmark processing speed for current machine.

    The higher the value the faster the machine"""
    def run_me():
        for i in range(100000):
            return i * 10
    return 0.003 / min(repeat(run_me, number=15000, repeat=5))


@pytest.fixture(scope="session", autouse=True)
def benchmark_fixture():
    global benchmark_time
    if benchmark_time is None:
        benchmark_time = get_benchmark_time()
    yield benchmark_time


def use_benchmark_time(func):
    global benchmark_time
    if benchmark_time is None:
        benchmark_time = get_benchmark_time()

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(benchmark_time=benchmark_time, *args, **kwargs)
    return wrapper
