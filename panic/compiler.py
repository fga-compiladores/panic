from lark import Lark, Tree, Transformer, v_args
from pathlib import Path
from typing import Dict, List, Tuple, Union
import operator as op

AST = Tree
SExpr = Union[List, str, int]
FuncDef = Tuple[Tuple[str], SExpr]
IR = Dict[str, FuncDef]

GRAMMAR_PATH = Path(__file__).parent / "grammar.lark"
GRAMMAR_SRC = GRAMMAR_PATH.read_text()
GRAMMAR = Lark(GRAMMAR_SRC)
GLOBAL_ENV = {
    "+": op.add,
    "-": op.sub,
    "*": op.mul,
    "/": op.truediv,
    "<": lambda x, y: int(x < y),
    ">": lambda x, y: int(x > y),
    "=": lambda x, y: int(x == y),
    "|": op.or_,
    "&": op.and_,
}

def panic(src: str, env: dict):
    ast = parse(src)
    ir = internal_representation(ast)
    env.update(GLOBAL_ENV)
    
    main_args = None
    for fname, (args, body) in ir.items():
        if fname == "main":
            main_args = [int(input(f'{arg}: ')) for arg in args]
        env[fname] = make_function(args, body, env)

    print(env["main"](*main_args))


def parse(src: str) -> AST:
    return GRAMMAR.parse(src)


def internal_representation(ast: Tree) -> IR:
    transformer = IRTransformer()
    return transformer.transform(ast)


def run(sexpr: SExpr, env: dict):
    if isinstance(sexpr, int):
        return sexpr
    elif isinstance(sexpr, str):
        return env[sexpr]

    head, *args = sexpr
    if head == "if":
        cond, then, other = args
        if run(cond, env):
            return run(then, env)
        else:
            return run(other, env)

    fn = env[head]
    argvalues = [run(arg, env) for arg in args]
    return fn(*argvalues)


def make_function(argnames, body, env):
    def fn(*argvalues):
        local_env = env.copy()
        for name, value in zip(argnames, argvalues):
            local_env[name] = value
        return run(body, local_env)

    return fn


@v_args(inline=True)
class IRTransformer(Transformer):
    def NAME(self, tk):
        return str(tk)

    def INT(self, tk):
        return int(tk)

    def OP(self, tk):
        return str(tk)

    def start(self, *funcs):
        return dict(funcs)

    def cond(self, cond, then, other):
        return ["if", cond, then, other]

    def op(self, *children):
        if len(children) == 3:
            x, op, y = children
            return [op, x, y]
        *start, op, rhs = children
        return [op, self.op(start), rhs]

    def call(self, name, args):
        return [name, *args]

    def args(self, *args):
        return args

    def argn(self, *args):
        return [str(x) for x in args]

    def func(self, name, args, body):
        return str(name), (args, body)