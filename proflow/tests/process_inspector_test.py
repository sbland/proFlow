"""Tests for the process inspector."""

import pytest
from proflow.process_inspector import (
    ProflowParsingAstError,
    inspect_process,
    parse_outputs,
    parse_outputs_to_interface,
    parse_inputs,
    parse_key,
    inspect_process_to_interfaces,
    extract_output_lines,
    strip_out_comments,
)

from proflow.Objects.Interface import I
from proflow.Objects.Process import Process
from proflow.helpers import lget


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
    ],
)


def test_inspect_process():
    process_inputs = inspect_process(DEMO_PROCESS)
    # assert process_inputs.additional_inputs == {'10': 'z'}
    # assert process_inputs.config_inputs == {'config.a': 'x'}
    # assert process_inputs.parameter_inputs == {'state.a': 'y'}
    # assert process_inputs.state_inputs == {'state.a': 'y'}
    # assert process_inputs.state_outputs == {'result': 'state.x'}
    assert process_inputs.additional_inputs == {'z': '10'}
    assert process_inputs.config_inputs == {'x': 'config.a'}
    assert process_inputs.parameter_inputs == {'y': 'state.a'}
    assert process_inputs.state_inputs == {'y': 'state.a'}
    assert process_inputs.state_outputs == {'result': 'state.x'}


def test_inspect_process_to_interfaces():
    process_inputs = inspect_process_to_interfaces(DEMO_PROCESS)
    assert list(process_inputs.additional_inputs) == [I('10', as_='z')]
    assert list(process_inputs.config_inputs) == [I('config.a', as_='x')]
    assert list(process_inputs.parameter_inputs) == [I('state.a', as_='y')]
    assert list(process_inputs.state_inputs) == [I('state.a', as_='y')]
    assert list(process_inputs.state_outputs) == [I('result', as_='state.x')]


def test_inspect_process_empty():
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


def test_inspect_process_unassigned(snapshot):
    def test_func(x, y, z):
        return x + y + z

    demo_process = Process(
        func=test_func,
        comment="This is the process comment",
        gate=True,
        state_outputs=lambda result: [
            (result, 'x'),
        ]
    )

    process_inputs = inspect_process(demo_process)
    print(process_inputs.additional_inputs)
    assert list(process_inputs.additional_inputs) == []
    assert list(process_inputs.config_inputs) == []
    assert list(process_inputs.parameter_inputs) == []
    assert list(process_inputs.state_inputs) == []
    assert list(process_inputs.state_outputs) == ['result']


class TestParseInputs:

    def test_parse(self):
        DEMO_INPUTS = lambda config: [  # noqa: E731
            I(config.a.foo.bar, as_='x'),
            I(config.a.foo[0], as_='y'),
            I(config.a.foo[-1], as_='z'),
        ]
        out = parse_inputs(DEMO_INPUTS, False)
        # Should we retain some info on the [0] here?
        assert out == {"x": "config.a.foo.bar", "y": "config.a.foo.0", "z": "config.a.foo.-1"}

    def test_parse_lget(self):
        DEMO_INPUTS = lambda e_state: [  # noqa: E731
            I(lget(e_state.foo, 1, "missing"), as_='y'),
        ]
        out = parse_inputs(DEMO_INPUTS, False)
        assert out == {"y": "e_state.foo.1"}

    def test_parse_sum(self):
        DEMO_INPUTS = lambda e_state: [  # noqa: E731
            I(sum(e_state.foo), as_='y'),
        ]
        out = parse_inputs(DEMO_INPUTS, False)
        # TODO: should store "sum" somewhere
        assert out == {"y": "e_state.foo._SUM()"}

    def test_parse_binop(self):
        DEMO_INPUTS = lambda state: [  # noqa: E731
            I(state.a.foo - state.a.bar, as_='x'),
        ]
        out = parse_inputs(DEMO_INPUTS, False)
        assert out == {"x": "state.a.foo,state.a.bar"}

    def test_parse_compare(self):
        DEMO_INPUTS = lambda state: [  # noqa: E731
            I(state.a.foo > state.a.bar, as_='x'),
        ]
        out = parse_inputs(DEMO_INPUTS, False)
        assert out == {"x": "state.a.foo,state.a.bar"}

    def test_parse_listcomp(self):
        iLC = 1
        nP = 3
        DEMO_INPUTS = lambda state, iLC=iLC: [
            I([state.foo[iLC][iP].a for iP in range(nP)], as_='x'),
        ]

        out = parse_inputs(DEMO_INPUTS, False)
        assert out == {
            'x': 'LIST_COMP(list_comp_id)',
            'iP': 'GEN',
            'GEN': ['RANGE PLACEHOLDER'],
            'ELT': 'state.foo.iLC.iP.a',
            'LIST_COMP(list_comp_id)': 'ELT'
        }

    def test_parse_param_as_index(self):
        DEMO_INPUTS = lambda config: [
            I(config.foo[config.bar].a,
              as_='x')
        ]

        out = parse_inputs(DEMO_INPUTS, False)
        assert out == {"x": "config.foo.*X.a", "*X": "config.bar"}

    def test_parse_inputs_sum_of_listcomp(self):
        # iL = 1
        # nLC = 3
        # nL = 2
        # DEMO_INPUTS = lambda state, iL=iL: [
        #     # We calculate cumulative Lai here
        #     I(sum([state.canopy_layer_component[jL][jLC].SAI for jLC in range(nLC)
        #            for jL in range(iL + 1, nL)]), as_='LAI_c'),
        # ]
        DEMO_INPUTS = lambda config: [
            I(sum([i + v for i, v in range(config.bar)]), as_='x'),
        ]

        out = parse_inputs(DEMO_INPUTS, False)
        assert out == {
            'x': 'LIST_COMP(list_comp_id)._SUM()',
            'i': 'GEN',
            'v': 'GEN',
            'GEN': ['RANGE PLACEHOLDER'],
            'ELT': 'i,v',
            'LIST_COMP(list_comp_id)': 'ELT',
        }


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
        DEMO_OUTPUTS = lambda result: [  # noqa: E731
            (result['a'], 'a'),
            (result['b'], 'b'),
        ]
        out = list(extract_output_lines(DEMO_OUTPUTS))
        print(out)
        assert out == ["result['a'], 'a'", "result['b'], 'b'"]

    @pytest.mark.skip("Not currently supported")
    def test_extract_output_lines_with_copy(self):
        deepcopy = lambda: None
        DEMO_OUTPUTS = lambda result: [
            (deepcopy(result['a']), 'a'),
            (deepcopy(result['b']), 'b'),
        ]
        out = list(extract_output_lines(DEMO_OUTPUTS))
        assert out == ["deepcopy(result['a']", "deepcopy(result['b']"]

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

    @pytest.mark.skip(reason="Star not implemented")
    def test_extract_output_lines_with_star(self):
        """Test parse_inputs returns correct value."""
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


def test_parse_key():
    """Test parse_key returns correct value."""
    out = parse_key("config.a.foo[0][var]['bar']'")
    assert out == 'config.a.foo.0.[var].bar'


def test_parse_outputs():
    """Test parse_outputs returns correct value."""
    DEMO_OUTPUTS = lambda result: [  # noqa: E731
        (result.a.foo.bar, 'x'),
        (result.a.foo[0], 'y'),
    ]
    out = parse_outputs(DEMO_OUTPUTS)
    assert out == {"result.a.foo.bar": "state.x", "result.a.foo.0": "state.y"}


def test_parse_outputs_list_comprehension():
    """Test parse_outputs returns correct value."""
    DEMO_OUTPUTS = lambda result: [  # noqa: E731
        (result[iL][iLC], f'foo.{iL}.{iLC}.bar')
        for iL in range(3) for iLC in range(3)
    ]
    out = parse_outputs(DEMO_OUTPUTS)
    assert out == {"result.[iL].[iLC]": "state.f'foo.{iL}.{iLC}.bar"}


def test_parse_outputs_list_comprehension_inputed_index():
    """Test parse_outputs returns correct value."""
    iLC = 0
    DEMO_OUTPUTS = lambda result, iLC=iLC: [  # noqa: E731
        (result[iL][iLC], f'foo.{iL}.{iLC}.bar')
        for iL in range(3)
    ]
    out = parse_outputs(DEMO_OUTPUTS, False)
    assert out == {"result.[iL].[iLC]": "state.f'foo.{iL}.{iLC}.bar"}


@pytest.mark.skip(reason="functions in output section not currently supported")
def test_parse_outputs_deep_copy():
    """Test parse_outputs returns correct output."""
    deepcopy = lambda: None
    DEMO_OUTPUTS = lambda result: [
        (deepcopy(result['a']), 'a'),
    ]
    out = parse_outputs(DEMO_OUTPUTS, False)
    assert out == {'deepcopy(result.a.)': 'state.a'}


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
            (['some info', ['other into']], 'a'),
        ]
        with pytest.raises(ProflowParsingAstError) as e:
            output_interface = list(parse_outputs_to_interface(DEMO_OUTPUTS, allow_errors=False))
        assert "AST type parse arg not implemented: <class '_ast.List'>" in repr(
            e)

    def test_parse_outputs_returns_invalid_for_unknown_input(self):
        DEMO_OUTPUTS = lambda result: [
            # This setup is not valid
            (['some info', ['other into']], 'a'),
        ]

        output_interface = list(parse_outputs_to_interface(DEMO_OUTPUTS))
        assert len(output_interface) == 1
        assert output_interface[0].from_ == "UNKNOWN"
        assert output_interface[0].as_ == "UNKNOWN"

    @pytest.mark.skip(reason="Not implemented")
    def test_parse_with_star_arg(self):
        nP = 3
        DEMO_OUTPUTS = lambda result: [
            *[(result, iP) for iP in range(nP)],
        ]

        output_interface = list(parse_outputs_to_interface(DEMO_OUTPUTS))
        assert len(output_interface) == nP
        assert output_interface[0].from_ == "result['a']"
        assert output_interface[0].as_ == "state.a"
