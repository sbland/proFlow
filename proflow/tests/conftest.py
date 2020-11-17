import pytest
from vendor.test_helpers import benchmark_time, get_benchmark_time


def test_setup():
    print('SETUP')
    assert False


@pytest.fixture(scope="session", autouse=True)
def benchmark_fixture():
    print('Using benchmark time')
    global benchmark_time
    if benchmark_time is None:
        benchmark_time = get_benchmark_time()
    yield benchmark_time
