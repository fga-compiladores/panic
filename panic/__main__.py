from pprint import pprint
import click
from .compiler import panic, parse, internal_representation


@click.command("panic")
@click.argument("file", type=click.File())
@click.option("--debug", "-d", is_flag=True, help="Run panic in debug mode")
def main(file, debug):
    """
    Read and run the given panic file. 
    """
    src = file.read()
    if debug:
        ast = parse(src)
        print(ast.pretty())
        ir = internal_representation(ast) 
        pprint(ir)
    else:
        panic(src, {})

if __name__ == "__main__":
    main()