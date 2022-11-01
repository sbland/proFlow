# %%
import ast
# %%
tree = ast.parse("a = \"hello\"")
tree
# %%
ast.dump(tree)

# %%
class FuncLister(ast.NodeVisitor):
    def visit_FunctionDef(self, node):
        print(node.name)
        self.generic_visit(node)

    def visit_Constant(self, node):
        print(node.value)
        self.generic_visit(node)

    def visit_Lambda(self, node):
        print("Lambda: ", node.args.args[0].arg, node.body.elts[0].elts[0].value.id)
        self.generic_visit(node)

FuncLister().visit(tree)
# %%
code = """
lambda result: [  # noqa: E731
            (result['a'], 'a'),
            (result['b'], 'b'),
        ]
"""
tree = ast.parse(code)
ast.dump(tree)
# %%
FuncLister().visit(tree)

# %%
code = """lambda config: [
            I(config.a.b, as_='x'),
    ]"""

tree = ast.parse(code)
ast.dump(tree)
# assert out == ["config.a.foo.bar, as_='x'", "config.a.foo[0], as_='y'"]


tree.body[0].value.args.args[0].arg
inputs = tree.body[0].value.body.elts
for inp in inputs:
    assert inp.func.id == "I"
    assert inp.args[0].value.value.id == "config"
    assert inp.args[0].value.attr == "a"
    assert inp.args[0].attr == "b"
    from_ = inp.args[0]
    as_ = inp.keywords[0].arg
    print(inp.args[0].attr)

# %%

def custom_eval(node_or_string):
    """
    Safely evaluate an expression node or a string containing a Python
    expression.  The string or node provided may only consist of the following
    Python literal structures: strings, bytes, numbers, tuples, lists, dicts,
    sets, booleans, and None.
    """
    if isinstance(node_or_string, str):
        node_or_string = ast.parse(node_or_string, mode='eval')
    if isinstance(node_or_string, ast.Expression):
        node_or_string = node_or_string.body
    def _raise_malformed_node(node):
        raise ValueError(f'malformed node or string: {node!r}')
    def _convert_num(node):
        if not isinstance(node, ast.Constant) or type(node.value) not in (int, float, complex):
            _raise_malformed_node(node)
        return node.value
    def _convert_signed_num(node):
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            operand = _convert_num(node.operand)
            if isinstance(node.op, ast.UAdd):
                return + operand
            else:
                return - operand
        return _convert_num(node)
    def _convert(node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Tuple):
            return tuple(map(_convert, node.elts))
        elif isinstance(node, ast.List):
            return list(map(_convert, node.elts))
        elif isinstance(node, ast.Set):
            return set(map(_convert, node.elts))
        elif isinstance(node, ast.Dict):
            if len(node.keys) != len(node.values):
                _raise_malformed_node(node)
            return dict(zip(map(_convert, node.keys),
                            map(_convert, node.values)))
        elif isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub)):
            left = _convert_signed_num(node.left)
            right = _convert_num(node.right)
            if isinstance(left, (int, float)) and isinstance(right, complex):
                if isinstance(node.op, ast.Add):
                    return left + right
                else:
                    return left - right
        elif isinstance(node, ast.Lambda):
            pass
        return "UNKNOWN"
        # return _convert_signed_num(node)
    return _convert(node_or_string)

custom_eval(code)
# %%

code = """lambda config: [
            I(config.a.b, as_='x'),
            I(config.c, as_='x'),
    ]"""
tree = ast.parse(code)

def get_lambda_body(node):
    return node.body

def get_lambda_root(tree):
    return tree.body[0].value

def parse_arg(attr: ast.Attribute):
    arg_list = []
    if isinstance(attr, ast.Attribute):
        arg_list.append(attr.attr)
        arg_list = arg_list + parse_arg(attr.value)
    elif isinstance(attr, ast.Name):
        arg_list.append(attr.id)
    return arg_list

def parse_input_element(inp: ast.Call):
    assert inp.func.id == "I", "inputs must be list of I()"
    print("\n\nel----\n")
    in_arg_tree: ast.Attribute = inp.args[0]
    in_args = list(reversed(parse_arg(in_arg_tree)))
    return in_args

def parse_as_arg(v):
    if isinstance(v, ast.Constant):
        return v.value
    raise ValueError(f"Value type parsing not implemented: {type(v)}")


def parse_input_map_args(inp: ast.Call):
    as_arg = inp.keywords[0]
    assert as_arg.arg == "as_", "first keyword should be as_"
    return parse_as_arg(as_arg.value)


def get_inputs(input_list: ast.List):
    for i in input_list.elts:
        in_args = parse_input_element(i)
        in_as_args = parse_input_map_args(i)
        print(in_args, f"-> \"{in_as_args}\"")

def parse_process_inputs(tree: ast.Module):
    if isinstance(tree, ast.Lambda):
        body = get_lambda_body(tree)
        assert isinstance(body, ast.List), "Lambda must return list"
        print(ast.dump(body))
        return get_inputs(body)
    return "UNKNOWN"

parse_process_inputs(tree.body[0].value)

# %%
foo = lambda config: [
    (1, 2),
]
import inspect
inputs_source = inspect.getsource(foo)
ast.dump(ast.parse(inputs_source))