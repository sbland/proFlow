"""Tests for the process inspector."""

from proflow.process_inspector import inspect_process, split_trailing_and_part, \
    parse_inputs, extract_inputs_lines, split_from_and_as, parse_key

from proflow.Objects.Interface import I
from proflow.Objects.Process import Process


def DEMO_FUNC(x, y, z):
    return x + y + z


DEMO_PROCESS = Process(
    func=DEMO_FUNC,
    comment="This is the process comment",
    gate=True,
    config_inputs=lambda config: [
            I(config.a, as_='x'),
    ],
    state_inputs=lambda state: [
        I(state.a, as_='y'),
    ],
    additional_inputs=lambda: [
        I(10, as_='z'),
    ],
    state_outputs=[
        I('_result', as_='x'),
    ]
)


def test_inspect_process(snapshot):
    process_inputs = inspect_process(DEMO_PROCESS)
    assert process_inputs == {
        'additional_inputs': {
            '10': 'z'
        },
        'config_inputs': {
            'config.a': 'x'
        },
        'parameter_inputs': {
            'state.a': 'y'
        },
        'state_inputs': {
            'state.a': 'y'
        },
        'state_outputs': {
            '_result': 'state.x'
        }
    }
    snapshot.assert_match(process_inputs, 'process_inputs')


def test_inspect_process_empty(snapshot):
    def test_func(x, y, z):
        return x + y + z

    demo_process = Process(
        func=test_func,
        comment="This is the process comment",
        gate=True,
        config_inputs=lambda config: [
        ],
        state_inputs=lambda state: [
        ],
        additional_inputs=lambda: [
        ],
        state_outputs=[
            I('_result', as_='x'),
        ]
    )
    process_inputs = inspect_process(demo_process)
    snapshot.assert_match(process_inputs, 'process_inputs')


def test_split_trailing_and_part():
    """Test split_trailing_and_part returns correct value."""
    out = split_trailing_and_part("state['foo']['bar'][0][i] + 1")
    assert out == [
        {'target': 'state', 'value': "['foo']['bar'][0][i]"},
        {'target': 'trailing', 'value': ' + 1'}]


def test_extract_input_lines():
    """Test parse_inputs returns correct value."""
    def DEMO_INPUTS(config): return [
        I(config.a.foo.bar, as_='x'),
        I(config.a.foo[0], as_='x'),
    ]
    out = list(extract_inputs_lines(DEMO_INPUTS))
    assert out == ["config.a.foo.bar, as_='x'", "config.a.foo[0], as_='x'"]


def test_split_from_and_as():
    """Test split_from_and_as returns correct value."""
    out = split_from_and_as("config.a.foo.bar, as_='x'")
    assert list(out.args) == ["config.a.foo.bar"]
    assert out.kwargs == {"as_": "x"}


def test_parse_key():
    """Test parse_key returns correct value."""
    out = parse_key("config.a.foo[0][var]['bar']'")
    assert out == 'config.a.foo.0.[var].bar'


def test_parse_inputs():
    """Test parse_inputs returns correct value."""
    def DEMO_INPUTS(config): return [
        I(config.a.foo.bar, as_='x'),
        I(config.a.foo[0], as_='y'),
    ]
    out = parse_inputs(DEMO_INPUTS)
    # assert out == ["config.a.foo.bar, as_='x'", "config.a.foo[0], as_='x'"]
    assert out == {"config.a.foo.bar": "x", "config.a.foo.0": "y"}
