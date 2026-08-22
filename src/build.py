import os
import subprocess
import sys
from collections.abc import Generator
from contextlib import contextmanager, suppress
from tempfile import NamedTemporaryFile
from time import sleep

import my_ast
from lexer import Lexer
from parser import Parser
from preprocessor import Preprocessor


@contextmanager
def preamble(my_prog: NamedTemporaryFile) -> Generator[None]:
    my_prog.write("#include <stdlib.h>\n")
    my_prog.write("#include <stdio.h>\n")
    my_prog.write("int main(void) {\n")
    yield
    my_prog.write("return 0;\n")
    my_prog.write("}\n")


def visit(node: my_ast.AST) -> str:
    match node:
        case my_ast.Assign(left, op, right):
            visited_left = visit(left)
            visited_right = visit(right)
            return f"{right.val_type.lower()} {visited_left} {op} {visited_right};\n"
        case my_ast.Print(value):
            printf_str = r'printf("%d\n", '
            result = visit(value)
            return f"{printf_str}{result});\n"
        case my_ast.BinOp(left, op, right):
            visited_left = visit(left)
            visited_right = visit(right)
            return f"{visited_left} {op} {visited_right}"
        case my_ast.Var(value):
            return value
        case my_ast.Num(value):
            return value
        case my_ast.Str(value):
            return value


def emit(tree: my_ast.Program, my_prog: NamedTemporaryFile) -> str:
    with preamble(my_prog):
        for node in tree.block.children:
            my_prog.write(visit(node))
    my_prog.seek(0)


def build_prog(
    source_file: str, out_path: str = "", run: bool = False, print_out: bool = False
):
    o = source_file.replace(".my", "")
    if not out_path:
        out_path = o
    with open(source_file) as my_file:
        code = my_file.read()
        lexer = Lexer(code, source_file)
        parser = Parser(lexer)
        tree = parser.parse()
        symtab_builder = Preprocessor(parser.file_name)
        symtab_builder.check(tree)
        if symtab_builder.warnings:
            sys.exit(1)
        with NamedTemporaryFile(mode="+r", suffix=".c", delete=False) as my_prog:
            emit(tree, my_prog)
            with suppress(FileNotFoundError):
                os.remove(f"{out_path}")
            if print_out:
                with open(my_prog.name) as my_prog_file:
                    print(my_prog_file.read())
            subprocess.Popen(
                f"clang {my_prog.name} -o {out_path} && rm {my_prog.name}", shell=True
            )
        if run:
            sleep(0.1)
            subprocess.Popen(out_path, shell=True)
