from collections import namedtuple
from typing import List, Tuple, TYPE_CHECKING, Callable, Union, Dict
import inspect
import re
import warnings
import ast
import textwrap

from proflow.Objects.Interface import I

if TYPE_CHECKING:
    from proflow.Objects.Process import Process


class ProflowParsingError(Exception):
    def __init__(self, message, process: "Process"):
        self.message = message
        self.process = process
        # self.source = inspect.getsource(process)
        self.full_message = f"""Failed to parse the Proflow Process: \n
Process name: {process.comment or process.func.__name__} \n
Message: "{message}"
        """
        super().__init__(self.full_message)


class ProflowParsingFunctionError(Exception):
    def __init__(self, message, func):
        self.message = message
        self.source = inspect.getsource(func)
        self.full_message = f'Proflow parsing function error: {self.message} \n {self.source}'
        super().__init__(self.full_message)

    def __repr__(self):
        return f'Proflow parsing function error: {self.message} \n {self.source}'


class ProflowParsingLineError(Exception):
    def __init__(self, message, failed_line: str):
        self.message = message
        self.source = failed_line
        super().__init__(self.message)

    def __repr__(self):
        return f'Proflow parsing line error: {self.message} \n {self.source}'


class ProflowParsingAstError(Exception):
    def __init__(self, message, failed_ast):
        message = f'{message} \n ======= ast.dump: \n {ast.dump(failed_ast)} \n ==='
        self.message = message
        self.ast = failed_ast
        super().__init__(self.message)

    def __repr__(self):
        return f'Proflow parsing line error: {self.message}'


#: Mapping of argument to the value
ArgMap = Dict[str, str]


def strip_out_comments(string: str) -> str:
    r = re.compile(r'#.*?$', re.MULTILINE)
    return r.sub('', string)


def extract_output_lines(map_inputs_fn: Callable[[object], List[str]]) -> List[str]:
    inputs_source = None
    try:
        inputs_source = strip_out_comments(inspect.getsource(map_inputs_fn))
        r_list = re.compile(r'lambda result.*?:.*?\[(?P<con>.*)\]', re.DOTALL | re.MULTILINE)
        output_map_raw = r_list.search(inputs_source).groups()[0]
        # Get lines
        r = re.compile(r'(?: |\[|^)\((.*?)\)(?:,|$)$', re.DOTALL | re.MULTILINE)
        matches = r.finditer(output_map_raw)
        lines = (g for match in matches if match is not None for g in match.groups())
        return lines
    except AttributeError as error:
        warnings.warn(Warning('Failed to parse output lines'))
        warnings.warn(Warning(inputs_source))
        warnings.warn(Warning(error))
        return []


def remove_inverted_commas_from_arg(arg: str) -> str:
    """Remove surrounding '' from string."""
    if arg[0] == "'" and arg[-1] == "'":
        return arg[1:-1]
    else:
        return arg


def parse_key(k: str) -> str:
    """Convert a input key to dot notation.

    Parameters
    ----------
    k : str
        example: config.a.foo[0][var]

    Returns
    -------
    str
        example: config.a.foo.0.[var]
    """

    def replace_var_fn(x):
        if x.groups()[0] is not None:
            return f'.{x.groups()[0]}.'
        elif x.groups()[1] is not None:
            return f'.{x.groups()[1]}.'
        elif x.groups()[2] is not None:
            return f'.[{x.groups()[2]}].'
        else:
            return 'zzz'
    # step 1. Find state or config
    find_square_brackets = r'\[(\d*?)\]|\[\'(\D*?)\'\]|\[(\D*?)\]'
    r = re.compile(find_square_brackets, re.DOTALL)
    # print(list(r.finditer(k)))
    replaced_parts = re.sub(r, replace_var_fn, k)
    replaced_double_dots = re.sub(r'\.\.+', '.', replaced_parts)
    out = re.sub(r'^\'|\'$|\.$|^\.|\.\'$', '', replaced_double_dots)
    return out


def rm_inv_comma(string: str):
    return re.sub('^\'|\'$', '', string)


def parse_inputs_to_interface(
    process_inputs: Callable[[any], List[I]],
    allow_errors=True,
) -> List[I]:
    try:
        inputs_map = parse_inputs(process_inputs)
        input_objects = [I(v, as_=k) for k, v in inputs_map.items()]
    except ProflowParsingLineError as e:
        warnings.warn(Warning(e.message))
        warnings.warn(Warning(e.source))
        if not allow_errors:
            raise e
        return [I(from_='UNKNOWN', as_='UNKNOWN')]
    except TypeError as e:
        warnings.warn(Warning(e))
        return [I(from_='ERROR', as_='ERROR')]
    return input_objects


def parse_output_line(output_line: str) -> List[str]:
    output_args = output_line.split(',')
    if len(output_args) != 2:
        raise ProflowParsingLineError('Failed to parse output line', output_line)
    return output_args


def parse_outputs_to_interface(
    process_outputs: Callable[[any], List[I]],
    allow_errors=True,
) -> List[I]:
    output_lines_row = None
    try:
        parse_outputs_b(process_outputs)
        output_lines_row = extract_output_lines(process_outputs)
        args_and_kwargs = [parse_output_line(line) for line in output_lines_row]
        output_objects = [
            I(from_=args[0], as_=f'state.{rm_inv_comma(args[1].strip())}')
            for args in args_and_kwargs]
        return output_objects
    except ProflowParsingLineError as e:
        warnings.warn(Warning(e.message))
        warnings.warn(Warning(e.source))
        if not allow_errors:
            raise e
        return [I(from_='UNKNOWN', as_='UNKNOWN')]
    except ProflowParsingAstError as e:
        warnings.warn(Warning(e.message))
        warnings.warn(Warning(e.ast))
        if not allow_errors:
            raise e
        return [I(from_='UNKNOWN', as_='UNKNOWN')]


def get_lambda_func(input_tree: ast.Assign) -> ast.Lambda:
    if isinstance(input_tree.value, ast.Tuple):
        return input_tree.value.elts[0]
    elif isinstance(input_tree.value, ast.Lambda):
        return input_tree.value
    else:
        raise ProflowParsingAstError(f"Unexpected AST type: {type(input_tree.value)}", input_tree)


def parse_unary_op(v: ast.UnaryOp):
    if isinstance(v.op, ast.USub):
        arg, argMap = parse_arg_val(v.operand)
        return ["-" + str(arg), argMap]
    else:
        raise ProflowParsingAstError(f"AST UnaryOp type not implemented: {type(v.op)}", v)


def parse_arg_val(v) -> Tuple[str, ArgMap]:
    """Parse a argument.

    Parameters
    ----------
    v : _type_
        _description_

    Returns
    -------
    str
        _description_

    Raises
    ------
    ProflowParsingAstError
        _description_
    """
    if isinstance(v, ast.UnaryOp):
        return parse_unary_op(v)
    elif isinstance(v, ast.Name):
        return [v.id, {}]
    elif isinstance(v, ast.Constant):
        return [v.value, {}]
    elif isinstance(v, ast.Attribute):
        # If index is a attribute then we need to also store the mapping of
        # the variable to the index
        parsed_arg, argmap = parse_arg(v)
        in_args = ".".join(list(reversed(parsed_arg)))
        refKey = "*X"  # TODO: Randomly generate this so no clashes
        argmap[refKey] = in_args
        # return f"*{v.value.id}.{v.attr}"
        # raise Exception("STOP")
        return ["*X", argmap]
        # return out
    else:
        raise ProflowParsingAstError(f"AST value type not implemented: {type(v)}", v)


def parse_arg_index(i: ast.Index) -> Tuple[str, ArgMap]:
    """Parse an ast Index.

    If the index is a constant value it just returns it as a string.
    E.g. data[1] returns "1"

    If the index is a variable it returns the index as a reference along with the parsed index
    E.g. data[config.a] returns "X123" and {"config.a": "X123"}

    Parameters
    ----------
    i : ast.Index
        _description_

    Returns
    -------
    Tuple[str, dict]
        _description_

    Raises
    ------
    ProflowParsingAstError
        _description_
    """
    if isinstance(i.value, ast.Constant):
        return [i.value.value, {}]
    elif isinstance(i, ast.Index):
        return parse_arg_val(i.value)
    else:
        raise ProflowParsingAstError(f"AST index type not implemented: {type(i)}", i)


def parse_list_comp(attr: ast.ListComp):
    additional_args = {}
    # [ELT for KEYS in GEN]

    # ELT
    elt_arg, _additional_args = parse_arg(attr.elt)
    additional_args = {**additional_args, **_additional_args}

    # KEYS
    assert len(attr.generators) == 1, "list comp with more than 1 generator is not implemented"
    comprehension = attr.generators[0]
    key_arg, _additional_args = parse_arg(comprehension.target)
    additional_args = {**additional_args, **_additional_args}

    # GEN
    gen_arg, _additional_args = parse_arg(comprehension.iter)
    additional_args = {**additional_args, **_additional_args}

    for k in key_arg:
        additional_args[k] = "GEN"

    additional_args["GEN"] = gen_arg

    ELT = ".".join(reversed(elt_arg))
    # for k in elt_arg:
    #     additional_args[k] = "ELT"
    additional_args["ELT"] = ELT
    list_comp_id = "LIST_COMP(list_comp_id)"  # TODO: Randomly gen id
    additional_args[list_comp_id] = "ELT"
    return [list_comp_id], additional_args


def parse_arg(attr: ast.Attribute) -> Tuple[List[str], ArgMap]:
    """Takes a parameter path such as config.a.b and recursively pulls out the string rep.

    E.g.
    I(config.a.foo.bar, as_='x') returns [['config', 'a', 'foo', 'bar'], None]
    I(config.a.[config.b].bar, as_='x') returns [['config', 'a', '*X', 'bar'], {"config.b": "*X"}]

    """
    arg_list = []
    additional_args = {}
    if isinstance(attr, ast.Attribute):
        arg_list.append(attr.attr)
        parsed_arg, _additional_args = parse_arg(attr.value)
        additional_args = {**additional_args, **_additional_args}
        arg_list = arg_list + parsed_arg
    elif isinstance(attr, ast.Name):
        arg_list.append(attr.id)
    elif isinstance(attr, ast.Constant):
        arg_list.append(attr.value)
    elif isinstance(attr, ast.Index):
        arg_list.append(attr.value.id)
    elif isinstance(attr, ast.Subscript):
        index, _additional_args = parse_arg_index(attr.slice)
        additional_args = {**additional_args, **_additional_args}
        arg_list.append(index)
        parsed_arg, _additional_args = parse_arg(attr.value)
        arg_list = arg_list + parsed_arg
        additional_args = {**additional_args, **_additional_args}
    elif isinstance(attr, ast.ListComp):
        parsed_arg, _additional_args = parse_list_comp(attr)
        arg_list = arg_list + parsed_arg
        additional_args = {**additional_args, **_additional_args}
    elif isinstance(attr, ast.BinOp):
        parsed_arg_left, _additional_args = parse_arg(attr.left)
        additional_args = {**additional_args, **_additional_args}
        parsed_arg_right, _additional_args = parse_arg(attr.right)
        additional_args = {**additional_args, **_additional_args}
        lhs = '.'.join(reversed(parsed_arg_left))
        rhs = '.'.join(reversed(parsed_arg_right))
        arg_list.append(f"{lhs},{rhs}")
    elif isinstance(attr, ast.Compare):
        parsed_arg_left, _additional_args = parse_arg(attr.left)
        additional_args = {**additional_args, **_additional_args}
        lhs = '.'.join(reversed(parsed_arg_left))
        parsed_arg_comparator, _additional_args = parse_arg(attr.comparators[0])
        additional_args = {**additional_args, **_additional_args}

        # TODO: Check this handles all comparitors
        rhs = '.'.join(reversed(parsed_arg_comparator))
        arg_list.append(f"{lhs},{rhs}")
    elif isinstance(attr, ast.Call):
        if attr.func.id == "lget":
            parsed_arg_1, _additional_args = parse_arg(attr.args[1])
            additional_args = {**additional_args, **_additional_args}
            parsed_arg_0, _additional_args = parse_arg(attr.args[0])
            additional_args = {**additional_args, **_additional_args}
            arg_list = arg_list + parsed_arg_1 + parsed_arg_0
        elif attr.func.id == "sum":
            print(ast.dump(attr))
            assert len(attr.args) == 1, "Sum only implemented when arg length is 1"
            parsed_arg, _additional_args = parse_arg(attr.args[0])
            additional_args = {**additional_args, **_additional_args}
            arg_list = ["_SUM()"] + arg_list + parsed_arg
        elif attr.func.id == "range":
            arg_list.append("RANGE PLACEHOLDER")
        else:
            raise ProflowParsingAstError(
                f"Parsing for func: {attr.func.id} has not been implemented", attr)
    elif isinstance(attr, ast.Tuple):
        for elt in attr.elts:
            parsed_arg, _additional_args = parse_arg(elt)
            additional_args = {**additional_args, **_additional_args}
            arg_list = arg_list + parsed_arg

    # elif isinstance(attr, ast.List): # NOTE: Not currently supported
    #     arg_list.append(parse_arg_index(attr.slice))
    #     arg_list = arg_list + parse_arg(attr.value)
    else:
        print("Failed to parse args")
        print(ast.dump(attr))
        raise ProflowParsingAstError(f"AST type parse arg not implemented: {type(attr)}", attr)
    return arg_list, additional_args


def parse_input_element(inp: ast.Call) -> Tuple[List[str], ArgMap]:
    """Pull input string from an I object.

    E.g
    I(config.a.foo.bar, as_='x') will return "config.a.foo.bar".

    Parameters
    ----------
    inp : ast.Call
        _description_

    Returns
    -------
    _type_
        _description_
    """
    assert inp.func.id == "I", "input must be instance of a I object"
    in_arg_tree: ast.Attribute = inp.args[0]
    args_out, additional_argmap = parse_arg(in_arg_tree)
    in_args = list(reversed(args_out))
    return in_args, additional_argmap


def parse_output_element(inp):
    in_args = list(reversed(parse_arg(inp)))
    return in_args


def parse_as_arg(v):
    if isinstance(v, ast.Constant):
        return v.value
    raise ProflowParsingAstError(f"Value type parsing not implemented: {type(v)}", v)


def parse_input_map_to_arg(inp: ast.Call) -> str:
    """Get the _as value from an I object instance.


    E.g.
    I(config.a.foo.bar, as_='x') will return "x".


    Parameters
    ----------
    inp : ast.Call
        _description_

    Returns
    -------
    str
        _description_
    """
    as_arg = inp.keywords[0]
    assert as_arg.arg == "as_", "first keyword should be as_"
    return parse_as_arg(as_arg.value)


def get_inputs(input_list: ast.List) -> ArgMap:
    input_mapping = {}
    for i in input_list.elts:
        in_args, additional_mappings = parse_input_element(i)
        assert in_args, "Could not get input args!"
        k = parse_input_map_to_arg(i)
        map_from = '.'.join(map(str, in_args))
        print("in as arg: ", map_from)
        input_mapping[k] = map_from
        input_mapping = {**input_mapping, **additional_mappings}
    print(input_mapping)
    return input_mapping


def parse_output_target(out_el):
    if isinstance(out_el, ast.Constant):
        return out_el.value
    if isinstance(out_el, ast.FormattedValue):
        return f"{{{out_el.value.id}}}"
    elif isinstance(out_el, ast.JoinedStr):
        elts = list(map(parse_output_target, out_el.values))
        return '.'.join(elts)
    else:
        raise NotImplementedError(f"Ast type not implemented: {type(out_el)}")


def parse_output(inp: ast.Tuple) -> Tuple[str, str]:
    assert isinstance(inp, ast.Tuple)
    assert len(inp.elts) == 2, f"Expected only 2 elements in tuple but got {len(inp.elts)}"
    result, target = inp.elts
    result_arg = parse_output_element(result)
    out_as_arg = parse_output_target(target)
    return result_arg, out_as_arg


def get_outputs_from_lambda_body(input_list: ast.List):
    input_mapping = {}
    if isinstance(input_list, ast.List):
        for i in input_list.elts:
            in_args, out_as_arg = parse_output(i)
            assert in_args, "Could not get input args!"
            assert out_as_arg, "Could not get input args!"
            k = '.'.join(map(str, in_args))
            input_mapping[k] = out_as_arg
    elif isinstance(input_list, ast.ListComp):
        # For now we just treat a list comp as a single output
        in_args, out_as_arg = parse_output(input_list.elt)
        assert in_args, "Could not get input args!"
        assert out_as_arg, "Could not get input args!"
        k = '.'.join(map(str, in_args))
        input_mapping[k] = out_as_arg
    else:
        raise NotImplementedError(f"Ast type not implemented: {type(input_list)}")
    return input_mapping


def parse_inputs(map_inputs_fn: Callable[[any], List[I]], allow_errors: bool = True) -> dict:
    source_code = textwrap.dedent(inspect.getsource(map_inputs_fn))
    if source_code[0:5] == "field":
        return {}  # input function is not set
    try:
        ast_tree = ast.parse(source_code)
        lambda_fn = get_lambda_func(ast_tree.body[0])
        inputs_list = lambda_fn.body
        inputs_map = get_inputs(inputs_list)
        return inputs_map
    except Exception as e:
        if not allow_errors:
            print(e)
            raise ProflowParsingFunctionError("Failed to get inputs for source", map_inputs_fn)
        else:
            return str(e)
            # print(e)
            # return "UNKNOWN"


def parse_outputs_b(map_inputs_fn: Callable[[any], List[I]]) -> dict:
    source_code = textwrap.dedent(inspect.getsource(map_inputs_fn))
    try:
        ast_tree = ast.parse(source_code)
        lambda_fn = get_lambda_func(ast_tree.body[0])
        inputs_list = lambda_fn.body
        inputs_map = get_outputs_from_lambda_body(inputs_list)
        return inputs_map
    except Exception as e:
        raise e


def parse_outputs(map_outputs_fn: Callable[[any], List[I]], allow_errors: bool = True) -> dict:
    try:
        output_lines = parse_outputs_to_interface(map_outputs_fn, allow_errors)
        outputs_map = {
            parse_key(i.from_): f'{rm_inv_comma(i.as_.strip())}'
            for i in output_lines}
        return outputs_map
    except Exception as e:
        if not allow_errors:
            raise e
        else:
            return "UNKNOWN"


def fieldNotEmpty(f: Union[any, Callable]) -> bool:
    return f and callable(f)


def inspect_process(process: 'Process'):
    Parsed = namedtuple(
        'Parsed', 'config_inputs state_inputs parameter_inputs additional_inputs state_outputs')
    try:
        return Parsed(
            config_inputs=fieldNotEmpty(
                process.config_inputs) and parse_inputs(process.config_inputs),
            state_inputs=fieldNotEmpty(process.state_inputs) and parse_inputs(process.state_inputs),
            parameter_inputs=fieldNotEmpty(
                process.state_inputs) and parse_inputs(process.state_inputs),
            additional_inputs=fieldNotEmpty(
                process.additional_inputs) and parse_inputs(process.additional_inputs),
            state_outputs=fieldNotEmpty(
                process.state_outputs) and parse_outputs(process.state_outputs),
        )
    except Exception as e:
        raise ProflowParsingError(str(e), process)


def inspect_process_to_interfaces(process: 'Process'):
    Parsed = namedtuple(
        'Parsed', 'config_inputs state_inputs parameter_inputs additional_inputs state_outputs')
    try:
        return Parsed(
            config_inputs=fieldNotEmpty(
                process.config_inputs) and parse_inputs_to_interface(process.config_inputs),
            state_inputs=fieldNotEmpty(
                process.state_inputs) and parse_inputs_to_interface(process.state_inputs),
            parameter_inputs=fieldNotEmpty(
                process.state_inputs) and parse_inputs_to_interface(process.state_inputs),
            additional_inputs=fieldNotEmpty(
                process.additional_inputs) and parse_inputs_to_interface(process.additional_inputs),
            state_outputs=fieldNotEmpty(
                process.state_outputs) and parse_outputs_to_interface(process.state_outputs),
        )
    except Exception as e:
        raise ProflowParsingError(str(e), process)
