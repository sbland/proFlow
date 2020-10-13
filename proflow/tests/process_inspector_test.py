"""Tests for the process inspector."""

from proflow.process_inspector import inspect_process, parse_outputs, split_trailing_and_part, \
    parse_inputs, extract_inputs_lines, split_from_and_as, parse_key, inspect_process_to_interfaces, \
    extract_output_lines, strip_out_comments

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
    state_outputs=lambda result: [
        (result, 'x'),
    ]
)


def test_inspect_process(snapshot):
    process_inputs = inspect_process(DEMO_PROCESS)
    assert process_inputs.additional_inputs == {'10': 'z'}
    assert process_inputs.config_inputs == {'config.a': 'x'}
    assert process_inputs.parameter_inputs == {'state.a': 'y'}
    assert process_inputs.state_inputs == {'state.a': 'y'}
    assert process_inputs.state_outputs == {'result': 'state.x'}


def test_inspect_process_to_interfaces(snapshot):
    process_inputs = inspect_process_to_interfaces(DEMO_PROCESS)
    assert list(process_inputs.additional_inputs) == [I('10', as_='z')]
    assert list(process_inputs.config_inputs) == [I('config.a', as_='x')]
    assert list(process_inputs.parameter_inputs) == [I('state.a', as_='y')]
    assert list(process_inputs.state_inputs) == [I('state.a', as_='y')]
    assert list(process_inputs.state_outputs) == [I('result', as_='state.x')]


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
        state_outputs=lambda result: [
            (result, 'x'),
        ]
    )

    process_inputs = inspect_process(demo_process)
    assert list(process_inputs.additional_inputs) == []
    assert list(process_inputs.config_inputs) == []
    assert list(process_inputs.parameter_inputs) == []
    assert list(process_inputs.state_inputs) == []
    assert list(process_inputs.state_outputs) == ['result']


def test_split_trailing_and_part():
    """Test split_trailing_and_part returns correct value."""
    out = split_trailing_and_part("state['foo']['bar'][0][i] + 1")
    assert out == [
        {'target': 'state', 'value': "['foo']['bar'][0][i]"},
        {'target': 'trailing', 'value': ' + 1'}]


def test_extract_input_lines():
    """Test parse_inputs returns correct value =."""
    def DEMO_INPUTS(config): return [  # noqa E731
        I(config.a.foo.bar, as_='x'),
        I(config.a.foo[0], as_='y'),
    ]
    out = list(extract_inputs_lines(DEMO_INPUTS))
    assert out == ["config.a.foo.bar, as_='x'", "config.a.foo[0], as_='y'"]


def test_extract_output_lines():
    """Test parse_inputs returns correct value."""
    DEMO_OUTPUTS = lambda result: [  # noqa E731
        (result.a.foo.bar, 'x'),
        (result.a.foo[0], 'y'),
    ]
    out = list(extract_output_lines(DEMO_OUTPUTS))
    assert out == ["result.a.foo.bar, 'x'", "result.a.foo[0], 'y'"]


def test_strip_out_comments():
    out = strip_out_comments("""
# noqa E731
# other comment
usefulinfo
    """)
    assert out == "\n\n\nusefulinfo\n    "


def test_extract_output_lines_complex_01():
    """Test parse_inputs returns correct value."""
    DEMO_OUTPUTS = lambda result: [  # noqa E731
            [(result[iL][iLC], f'foo.{iL}.{iLC}.bar')
                for iL in range(3) for iLC in range(3)],
            (result.a.foo.bar, 'x'),
        ]
    out = list(extract_output_lines(DEMO_OUTPUTS))
    # TODO: We are stripping out the for loop here. Can we include it
    assert out == ["result[iL][iLC], f'foo.{iL}.{iLC}.bar'", "result.a.foo.bar, 'x'"]


def test_extract_output_lines_complex_02():
    """Test parse_inputs returns correct value."""
    DEMO_OUTPUTS = lambda result:[(result['hr'], 'temporal.hr')]
    out = list(extract_output_lines(DEMO_OUTPUTS))
    # TODO: We are stripping out the for loop here. Can we include it
    assert out == ["result['hr'], 'temporal.hr'"]


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


def test_parse_outputs():
    """Test parse_outputs returns correct value."""
    DEMO_OUTPUTS = lambda result: [  # noqa: E731
        (result.a.foo.bar, 'x'),
        (result.a.foo[0], 'y'),
    ]
    out = parse_outputs(DEMO_OUTPUTS)
    assert out == {"result.a.foo.bar": "state.x", "result.a.foo.0": "state.y"}


def test_parse_outputs_complex_01():
    """Test parse_outputs returns correct value."""
    DEMO_OUTPUTS = lambda result: [  # noqa: E731
            (result[iL][iLC], f'foo.{iL}.{iLC}.bar')
            for iL in range(3) for iLC in range(3)
        ]
    out = parse_outputs(DEMO_OUTPUTS)
    assert out == {"result.[iL].[iLC]": "state.f'foo.{iL}.{iLC}.bar"}
