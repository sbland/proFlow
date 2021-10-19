"""Tests for the process inspector."""

import pytest
from proflow.process_inspector import(
    ProflowParsingLineError,
    inspect_process,
    parse_outputs,
    parse_outputs_to_interface,
    split_trailing_and_part,
    parse_inputs,
    extract_inputs_lines,
    split_from_and_as,
    parse_key,
    inspect_process_to_interfaces,
    extract_output_lines,
    strip_out_comments,
)

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


class TestExtractOutputLines:

    def test_extract_output_lines(self):
        """Test parse_inputs returns correct value."""
        DEMO_OUTPUTS = lambda result: [  # noqa: E731
            (result.a.foo.bar, 'x'),
            (result.a.foo[0], 'y'),
        ]
        out = list(extract_output_lines(DEMO_OUTPUTS))
        assert out == ["result.a.foo.bar, 'x'", "result.a.foo[0], 'y'"]



    def test_extract_output_lines_dict_result(self):
        """Test parse_inputs returns correct value."""
        iLC = 0

        DEMO_OUTPUTS = lambda result: [  # noqa: E731
            (result['a'], 'a'),
            (result['b'], 'b'),
        ]
        out = list(extract_output_lines(DEMO_OUTPUTS))
        print(out)
        assert out == ["result['a'], 'a'", "result['b'], 'b'"]



    def test_extract_output_lines_with_copy(self):
        """Test parse_inputs returns correct value."""
        deepcopy = lambda: None
        DEMO_OUTPUTS = lambda result: [
            (deepcopy(result['a']), 'a'),
            (deepcopy(result['b']), 'b'),
        ]
        out = list(extract_output_lines(DEMO_OUTPUTS))
        print(out)
        assert out == ["deepcopy(result['a']), 'a'", "deepcopy(result['b']), 'b'"]


    def test_extract_output_lines_complex_01(self):
        """Test parse_inputs returns correct value."""
        DEMO_OUTPUTS = lambda result: [  # noqa E731
                [(result[iL][iLC], f'foo.{iL}.{iLC}.bar')
                    for iL in range(3) for iLC in range(3)],
                (result.a.foo.bar, 'x'),
            ]
        out = list(extract_output_lines(DEMO_OUTPUTS))
        # TODO: We are stripping out the for loop here. Can we include it
        assert out == ["result[iL][iLC], f'foo.{iL}.{iLC}.bar'", "result.a.foo.bar, 'x'"]


    def test_extract_output_lines_complex_02(self):
        """Test parse_inputs returns correct value."""
        DEMO_OUTPUTS = lambda result: [(result['hr'], 'temporal.hr')]
        out = list(extract_output_lines(DEMO_OUTPUTS))
        # TODO: We are stripping out the for loop here. Can we include it
        assert out == ["result['hr'], 'temporal.hr'"]



    def test_extract_output_lines_with_star(self):
        """Test parse_inputs returns correct value."""
        deepcopy = lambda: None
        DEMO_OUTPUTS = lambda result: [
            *[('a', 'b') for _ in range(3)],
        ]
        out = list(extract_output_lines(DEMO_OUTPUTS))
        print(out)
        assert out == ["a, b", "a, b", "a, b"]


def test_strip_out_comments():
    out = strip_out_comments("""
# noqa E731
# other comment
usefulinfo
    """)
    assert out == "\n\n\nusefulinfo\n    "


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
    DEMO_INPUTS = lambda config: [  # noqa: E731
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


def test_parse_outputs_complex_02():
    """Test parse_outputs returns correct value."""
    iLC = 0
    DEMO_OUTPUTS = lambda result, iLC=iLC: [  # noqa: E731
            (result[iL][iLC], f'foo.{iL}.{iLC}.bar')
            for iL in range(3)
        ]
    out = parse_outputs(DEMO_OUTPUTS)
    assert out == {"result.[iL].[iLC]": "state.f'foo.{iL}.{iLC}.bar"}


def test_parse_outputs_complex_03():
    """Test parse_outputs returns correct output."""
    deepcopy = lambda: None
    DEMO_OUTPUTS = lambda result: [
        (deepcopy(result['a']), 'a'),
    ]
    out = parse_outputs(DEMO_OUTPUTS)
    print(out)
    assert out == {'deepcopy(result.a.)': 'state.a'}

# TODO: Test inputs with == : state.a.foo == 1, as_="is_bool"
class TestParseOutputs:
    def test_parse_outputs_to_interface(self):
        DEMO_OUTPUTS = lambda result: [
            (result['a'], 'a'),
        ]

        output_interface = list(parse_outputs_to_interface(DEMO_OUTPUTS))
        assert len(output_interface) == 1
        assert output_interface[0].from_ == "result['a']"
        assert output_interface[0].as_ == "state.a"

    def test_parse_outputs_throws_error_for_unknown_input(self):
        DEMO_OUTPUTS = lambda result: [
            # Multiple commas currently causes an error
            (['some info', ['other into']], 'a'),
        ]
        with pytest.raises(ProflowParsingLineError) as e:
            output_interface = list(parse_outputs_to_interface(DEMO_OUTPUTS, allow_errors=False))

        assert repr(e) == f"<ExceptionInfo Proflow parsing line error: Failed to parse output line \n ['some info', ['other into']], 'a' tblen=5>"

    def test_parse_outputs_returns_invalid_for_unknown_input(self):
        DEMO_OUTPUTS = lambda result: [
            # Multiple commas currently causes an error
            (['some info', ['other into']], 'a'),
        ]

        output_interface = list(parse_outputs_to_interface(DEMO_OUTPUTS))
        assert len(output_interface) == 1
        assert output_interface[0].from_ == "UNKNOWN"
        assert output_interface[0].as_ == "UNKNOWN"

    def test_parse_with_star_arg(self):
        nP = 3
        DEMO_OUTPUTS = lambda result: [
            *[(result, iP) for iP in range(nP)],
        ]

        output_interface = list(parse_outputs_to_interface(DEMO_OUTPUTS))
        assert len(output_interface) == nP
        assert output_interface[0].from_ == "result['a']"
        assert output_interface[0].as_ == "state.a"
