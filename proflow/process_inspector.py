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

NEXT_ID = -1
MAX_AST_DUMP_LENGTH = 1000


def get_id():
    global NEXT_ID
    NEXT_ID += 1
    return NEXT_ID


def reset_id():
    global NEXT_ID
    NEXT_ID = -1


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
        try:
            source_code = textwrap.dedent(inspect.getsource(func))
            ast_tree = ast.parse(source_code)
            ast_dump = ast.dump(ast_tree)
        except Exception:
            ast_dump = "Failed to dump ast!"

        self.full_message = f"""Proflow parsing function error: {self.message}
         {self.source}
         AST:
         {ast_dump}
"""
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
        ast_dump = ast.dump(failed_ast)[0:MAX_AST_DUMP_LENGTH]
        message = f'{message} \n ======= ast.dump: \n {ast_dump} \n ==='
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
    outputs_source = None
    try:
        outputs_source = strip_out_comments(inspect.getsource(map_inputs_fn))
        if outputs_source[0:len("def GET_INPUT_FACTORY_INNER")] == "def GET_INPUT_FACTORY_INNER":
            return []

        r_list = re.compile(r'lambda result.*?:.*?\[(?P<con>.*)\]', re.DOTALL | re.MULTILINE)
        output_map_raw = r_list.search(outputs_source).groups()[0]
        # Get lines
        r = re.compile(r'(?: |\[|^)\((.*?)\)(?:,|$)$', re.DOTALL | re.MULTILINE)
        matches = r.finditer(output_map_raw)
        lines = (g for match in matches if match is not None for g in match.groups())
        return lines
    except AttributeError as error:
        warnings.warn(Warning(f"""Failed to parse output lines

Error
=====
{error}

Source
======
{outputs_source}

                              """))
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
        # warnings.warn(Warning(e.message))
        # warnings.warn(Warning(e.source))
        if not allow_errors:
            raise e from e
        return [I(from_='UNKNOWN', as_='UNKNOWN')]
    except TypeError:
        # warnings.warn(Warning(e))
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
        # warnings.warn(Warning(e.message))
        # warnings.warn(Warning(e.source))
        if not allow_errors:
            raise e from e
        return [I(from_='UNKNOWN', as_='UNKNOWN')]
    except ProflowParsingAstError as e:
        # warnings.warn(Warning(e.message))
        # warnings.warn(Warning(e.ast))
        if not allow_errors:
            raise e from e
        return [I(from_='UNKNOWN', as_='UNKNOWN')]


def get_inputs_list_from_lambda_fn(input_tree: ast.Assign) -> ast.List:
    if isinstance(input_tree.value, ast.Tuple):
        return input_tree.value.elts[0].body
    elif isinstance(input_tree.value, ast.Lambda):
        return input_tree.value.body
    else:
        raise ProflowParsingAstError(
            f"Unexpected AST type: {type(input_tree.value)}", input_tree)


def get_inputs_list_from_function_def(input_tree: ast.FunctionDef) -> ast.List:
    try:
        return input_tree.body[0].value
    except Exception as e:
        warnings.warn(Warning(e))
        raise ProflowParsingAstError(
            f"Failed to get Process inputs from function: {ast.dump(input_tree)}", input_tree)


def get_inputs_list(input_tree: Union[ast.Assign, ast.FunctionDef]) -> ast.List:
    if isinstance(input_tree, ast.Assign):
        return get_inputs_list_from_lambda_fn(input_tree)
    elif isinstance(input_tree, ast.FunctionDef):
        return get_inputs_list_from_function_def(input_tree)
    else:
        raise ProflowParsingAstError(
            f"Unexpected AST type: {type(input_tree)}", input_tree)


def parse_unary_op(v: ast.UnaryOp):
    if isinstance(v.op, ast.USub):
        arg, argMap = parse_arg_val(v.operand)
        return ["-" + str(arg), argMap]
    else:
        raise ProflowParsingAstError(f"AST UnaryOp type not implemented: {type(v.op)}", v)


def parse_bin_op(attr: ast.BinOp):
    additional_args = {}
    arg_list = []
    parsed_arg_left, _additional_args = parse_arg(attr.left)
    additional_args = {**additional_args, **_additional_args}
    parsed_arg_right, _additional_args = parse_arg(attr.right)
    additional_args = {**additional_args, **_additional_args}
    lhs = '.'.join(map(str, reversed(parsed_arg_left)))
    rhs = '.'.join(map(str, reversed(parsed_arg_right)))
    # TODO: Should we include op here?
    arg_list.append(f"{lhs},{rhs}")
    return arg_list, additional_args


def parse_arg_val(v: ast.Index) -> Tuple[str, ArgMap]:
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
    elif isinstance(v, ast.BinOp):
        return parse_bin_op(v)
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


def parse_arg_index(i: Union[ast.Index, ast.Slice]) -> Tuple[str, ArgMap]:
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
    return parse_arg(i)
    # if isinstance(i, ast.Slice):
    #     [top], _additional_args_top = parse_arg(i.upper)
    #     [bottom], _additional_args_bottom = parse_arg(i.lower)
    #     step, _additional_args_step = parse_arg(i.step)if i.step else [None, {}]
    #     out = f"{bottom}:{top}" + (f":{step}" if step else "")
    #     out_args = {**_additional_args_top, **_additional_args_bottom, **_additional_args_step}
    #     return out, out_args
    # elif isinstance(i, ast.Index):
    #     if isinstance(i.value, ast.Constant):
    #         return [i.value.value, {}]
    #     elif isinstance(i, ast.Index):
    #         return parse_arg_val(i.value)
    #     else:
    #         raise ProflowParsingAstError(f"AST index type not implemented: {type(i)}", i)
    # else:
    #     raise ProflowParsingAstError(f"AST index type not implemented: {type(i)}", i)


def parse_list_comp(attr: ast.ListComp):
    additional_args = {}
    # [ELT for KEYS in GEN]

    # ELT
    elt_arg, _additional_args = parse_arg(attr.elt)
    additional_args = {**additional_args, **_additional_args}
    ELT_ID = "ELT"
    ELT = ".".join(reversed(elt_arg))
    additional_args[ELT_ID] = ELT
    list_comp_ids = []
    for i, comprehension in enumerate(attr.generators):
        # KEYS
        # comprehension = attr.generators[0]
        key_arg, _additional_args = parse_arg(comprehension.target)
        additional_args = {**additional_args, **_additional_args}

        # GEN
        # assert isinstance(
        #     comprehension.iter, ast.Call
        # ) and comprehension.iter.func.id == "range", "Only Range comprehension is implemented"
        gen_arg, _additional_args = parse_arg(comprehension.iter)
        additional_args = {**additional_args, **_additional_args}

        GEN_ID = f"GEN_{i}"
        for k in key_arg:
            additional_args[k] = GEN_ID

        additional_args[GEN_ID] = ".".join(reversed(gen_arg))

        # for k in elt_arg:
        #     additional_args[k] = "ELT"
        list_comp_id = f"LIST_COMP(list_comp_{i})"  # TODO: Randomly gen id
        additional_args[list_comp_id] = f"{ELT_ID}.{i}"
        list_comp_ids.append(list_comp_id)
    return ["(" + ",".join(list_comp_ids) + ")"], additional_args


def parse_list(attr: ast.List) -> Tuple[List[str], dict]:
    out = ""
    for i, elt in enumerate(attr.elts):
        parsed_arg, _additional_args = parse_arg(elt)
        out = out + ".".join(reversed([str(v) for v in parsed_arg]))
        if i != len(attr.elts) - 1:
            out = out + ","
    return out, _additional_args


def parse_fn_getattr(attr: ast.Call) -> Tuple[List[str], dict]:
    key = attr.args[0].id
    args, additional_args = parse_arg(attr.args[1])
    return [[*args, key], additional_args]


def parse_fn_len(attr: ast.Call) -> Tuple[List[str], dict]:
    return parse_arg(attr.args[0])


def parse_fn(attr: ast.Call) -> Tuple[List[str], dict]:
    arg_list = []
    additional_args = {}
    if attr.func.id == "getattr":
        parsed_args, _additional_args = parse_fn_getattr(attr)
        additional_args = {**additional_args, **_additional_args}
        arg_list = arg_list + parsed_args
    elif attr.func.id == "asdict":
        parsed_args, _additional_args = parse_arg(attr.args[0])
        additional_args = {**additional_args, **_additional_args}
        arg_list = arg_list + parsed_args
    elif attr.func.id == "len":
        parsed_args, _additional_args = parse_fn_len(attr)
        additional_args = {**additional_args, **_additional_args}
        arg_list = arg_list + parsed_args
    elif attr.func.id == "lget":
        parsed_arg_1, _additional_args = parse_arg(attr.args[1])
        additional_args = {**additional_args, **_additional_args}
        parsed_arg_0, _additional_args = parse_arg(attr.args[0])
        additional_args = {**additional_args, **_additional_args}
        arg_list = arg_list + parsed_arg_1 + parsed_arg_0
    elif attr.func.id == "list":
        # NOTE: We disregard that list function is called and just parse contents
        parsed_args, _additional_args = parse_arg(attr.args[0])
        additional_args = {**additional_args, **_additional_args}
        arg_list = arg_list + parsed_args
    elif attr.func.id == "dict":
        raise NotImplementedError("Dict not implemented")
    elif attr.func.id == "sum":
        assert len(attr.args) == 1, "Sum only implemented when arg length is 1"
        parsed_arg, _additional_args = parse_arg(attr.args[0])
        additional_args = {**additional_args, **_additional_args}
        arg_list = ["_SUM()"] + arg_list + parsed_arg
    elif attr.func.id == "max":
        assert len(attr.args) == 1, "Max only implemented when arg length is 1"
        parsed_arg, _additional_args = parse_arg(attr.args[0])
        additional_args = {**additional_args, **_additional_args}
        arg_list = ["_MAX()"] + arg_list + parsed_arg
    elif attr.func.id == "min":
        assert len(attr.args) == 1, "Min only implemented when arg length is 1"
        parsed_arg, _additional_args = parse_arg(attr.args[0])
        additional_args = {**additional_args, **_additional_args}
        arg_list = ["_MIN()"] + arg_list + parsed_arg
    elif attr.func.id == "range":
        RANGE_ARG_ID = f"RANGE_ARG_{get_id()}"
        out = f"{RANGE_ARG_ID}._RANGE()"
        for i, arg in enumerate(attr.args):
            # assert len(attr.args) == 1, "Range only implemented when arg length is 1"
            ARG_ID = f"{RANGE_ARG_ID}.{i}"  # TODO: Generate this
            parsed_arg, _additional_args = parse_arg(arg)
            additional_args = {**additional_args, **_additional_args}
            additional_args[ARG_ID] = ".".join(reversed([str(a) for a in parsed_arg]))
        arg_list.append(out)
    elif attr.func.id == "reversed":
        REVERSED_ARG_ID = f"REVERSED_ARG_{get_id()}"
        out = f"{REVERSED_ARG_ID}._REVERSED()"
        for i, arg in enumerate(attr.args):
            # assert len(attr.args) == 1, "REVERSED only implemented when arg length is 1"
            ARG_ID = f"{REVERSED_ARG_ID}.{i}"  # TODO: Generate this
            parsed_arg, _additional_args = parse_arg(arg)
            additional_args = {**additional_args, **_additional_args}
            additional_args[ARG_ID] = ".".join(reversed([str(a) for a in parsed_arg]))
        arg_list.append(out)
    else:
        warnings.warn(Warning(f"Parsing for func: {attr.func.id} has not been implemented"))
        arg_list += [parse_arg(a) for a in attr.args]
        # TODO: Parse kwargs!
        if len(attr.keywords) > 0:
            raise NotImplementedError("Kwargs not implemented")
    return arg_list, additional_args


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
        parsed_arg, _additional_args = parse_arg_val(attr.value)
        arg_list.append(parsed_arg)
        additional_args = {**additional_args, **_additional_args}
    elif isinstance(attr, ast.Subscript):
        index, _additional_args = parse_arg_index(attr.slice)
        additional_args = {**additional_args, **_additional_args}
        arg_list = arg_list + index
        # arg_list.append(index)
        parsed_arg, _additional_args = parse_arg(attr.value)
        arg_list = arg_list + parsed_arg
        additional_args = {**additional_args, **_additional_args}
    elif isinstance(attr, ast.ListComp):
        parsed_arg, _additional_args = parse_list_comp(attr)
        arg_list = arg_list + parsed_arg
        additional_args = {**additional_args, **_additional_args}
    elif isinstance(attr, ast.BinOp):
        parsed_args, _additional_args = parse_bin_op(attr)
        arg_list = arg_list + parsed_args
        additional_args = {**additional_args, **_additional_args}
    elif isinstance(attr, ast.BoolOp):
        _addtional_args_op = {
            "op": attr.op.__class__.__name__,
        }
        additional_args = {**additional_args, **_addtional_args_op}
        parsed_arg_left, _additional_args = parse_arg(attr.values[0])
        additional_args = {**additional_args, **_additional_args}
        parsed_arg_right, _additional_args = parse_arg(attr.values[1])
        additional_args = {**additional_args, **_additional_args}
        lhs = '.'.join(map(str, reversed(parsed_arg_left)))
        rhs = '.'.join(map(str, reversed(parsed_arg_right)))
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
    elif isinstance(attr, ast.Slice):
        # TODO: Check this ok
        [top], _additional_args_top = parse_arg(attr.upper)
        [bottom], _additional_args_bottom = parse_arg(attr.lower)
        step, _additional_args_step = parse_arg(attr.step)if attr.step else [None, {}]
        index = f"{bottom}:{top}" + (f":{step}" if step else "")
        _additional_args = {**_additional_args_top, **
                            _additional_args_bottom, **_additional_args_step}
        arg_list.append(index)
        additional_args = {**additional_args, **_additional_args}
    elif isinstance(attr, ast.Call):
        parsed_args, _additional_args = parse_fn(attr)
        arg_list = arg_list + parsed_args
        additional_args = {**additional_args, **_additional_args}
    elif isinstance(attr, ast.IfExp):
        # TODO: Implement this
        arg_list.append("AST PARSE NOT_IMPLEMENTED")
    elif isinstance(attr, ast.Tuple):
        for elt in attr.elts:
            parsed_arg, _additional_args = parse_arg(elt)
            additional_args = {**additional_args, **_additional_args}
            arg_list = arg_list + parsed_arg

    elif isinstance(attr, ast.List):  # NOTE: Not currently supported
        for elt in attr.elts:
            parsed_arg, _additional_args = parse_arg(elt)
            additional_args = {**additional_args, **_additional_args}
            arg_list = arg_list + parsed_arg
            # # TODO: Fix this
            # parsed_arg, _additional_args = parse_arg(elt)
            # arg_list.append(parse_list(attr))
            # arg_list = arg_list + parse_arg(attr.value)
    else:
        warnings.warn("Failed to parse args")
        # warnings.warn(ast.dump(attr))
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
    if isinstance(inp, ast.Starred):
        return [], {}
        # TODO: Should throw an error!
        raise NotImplementedError("Starred not implemented")
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

    if isinstance(inp, ast.Starred):
        return ""
        # TODO: Should throw an error!
        raise NotImplementedError("Starred not implemented")
    assert len(inp.keywords) >= 0 and inp.keywords[0].arg == "as_", "first keyword should be as_"
    as_arg = inp.keywords[0]
    return parse_as_arg(as_arg.value)


def get_inputs(input_list: ast.List) -> ArgMap:
    input_mapping = {}
    for i in input_list.elts:
        in_args, additional_mappings = parse_input_element(i)
        assert in_args is not None, "Could not get input args!"
        k = parse_input_map_to_arg(i)
        map_from = '.'.join(map(str, in_args))
        input_mapping[k] = map_from
        input_mapping = {**input_mapping, **additional_mappings}
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


def parse_inputs(
    map_inputs_fn: Callable[[any], List[I]], allow_errors: bool = True, silent=False,
) -> dict:
    source_code = textwrap.dedent(inspect.getsource(map_inputs_fn))
    ast_tree = ast.parse(source_code)
    if source_code[0:5] == "field":
        return {}  # input function is not set
    try:
        inputs_list = get_inputs_list(ast_tree.body[0])
        inputs_map = get_inputs(inputs_list)
        return inputs_map
    except ProflowParsingError as e:
        if not silent:
            print("ProFlowParsingError\n==================")
            print(e)
        if not allow_errors:
            raise e from e
        else:

            return {}
    except ProflowParsingLineError as e:
        if not silent:
            print("ProFlowParsingLineError\n==================")
            print(e)
        if not allow_errors:
            raise e from e
        else:
            return {}
    except ProflowParsingAstError as e:
        if not silent:
            print("ProFlowParsingAstError\n==================")
            print(e)
        if not allow_errors:
            raise e from e
        else:
            return {}
    except Exception as e:
        if not allow_errors:
            print("ProFlowParsingFunctionError\n==================")
            print(source_code)
            print("============")
            print(ast.dump(ast_tree))
            print("==========end====")
            raise e from e
            print("ProFlowParsingFunctionError\n==================")
            print(e)
            print(ast.dump(ast_tree))
            raise ProflowParsingFunctionError(
                "Failed to get inputs for source", map_inputs_fn) from e
        else:
            # raise e
            # return str(e)
            # print(e)
            return "FAILED_TO_PARSE_PROCESS"


def parse_outputs_b(map_inputs_fn: Callable[[any], List[I]]) -> dict:
    source_code = textwrap.dedent(inspect.getsource(map_inputs_fn))
    try:
        ast_tree = ast.parse(source_code)
        inputs_list = get_inputs_list(ast_tree.body[0])
        inputs_map = get_outputs_from_lambda_body(inputs_list)
        return inputs_map
    except Exception as e:
        raise e from e


def parse_outputs(
    map_outputs_fn: Callable[[any], List[I]], allow_errors: bool = True, silent=True,
) -> dict:
    try:
        output_lines = parse_outputs_to_interface(map_outputs_fn, allow_errors)
        outputs_map = {
            parse_key(i.from_): f'{rm_inv_comma(i.as_.strip())}'
            for i in output_lines}
        return outputs_map
    except Exception as e:
        if not silent:
            warnings.warn("Error parsing outputs")
            warnings.warn(inspect.getsource(map_outputs_fn))
        if not allow_errors:
            raise e from e
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
