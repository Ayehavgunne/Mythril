import os
import subprocess
import sys
from collections.abc import Generator
from contextlib import contextmanager, suppress
from tempfile import NamedTemporaryFile
from time import sleep

import my_ast
import my_types
from lexer import Lexer
from parser import Parser
import grammar
from visitor import NodeVisitor, VarSymbol
from validator import Validator


class BuilderError(Exception):
    pass


@contextmanager
def preamble(my_prog: NamedTemporaryFile) -> Generator[None]:
    my_prog.write('#pragma clang diagnostic ignored "-Wparentheses-equality"\n')
    my_prog.write("#include <iostream>\n")
    my_prog.write("#include <vector>\n")
    my_prog.write("using namespace std;\n")
    my_prog.write("int main(void) {\n")
    yield
    my_prog.write("return 0;\n")
    my_prog.write("}\n")


class Builder(NodeVisitor):
    def __init__(self, file_name=None):
        super().__init__()
        self.file_name = file_name

    def visit_assign(self, node: my_ast.Assign) -> str:
        visited_left = self.visit(node.left)
        visited_right = self.visit(node.right)
        match node.right:
            case my_ast.Num(val_type=val_type):
                var_sym = VarSymbol(
                    name=node.left.value,
                    type=my_types.type_map[val_type.lower()],
                    val_assigned=True,
                    read_only=node.left.read_only,
                )
            case my_ast.Str():
                var_sym = VarSymbol(
                    name=node.left.value,
                    type=grammar.STR.lower(),
                    val_assigned=True,
                    read_only=node.left.read_only,
                )
            case my_ast.Var(value=value):
                scoped_val = self.search_scopes(value)
                var_sym = VarSymbol(
                    name=scoped_val.name,
                    type=my_types.type_map[scoped_val.type],
                    val_assigned=True,
                    read_only=node.left.read_only,
                )
            case my_ast.Collection(type=collection_type, items=items):
                if collection_type == 'List':
                    collection_type = items[0].val_type.lower()
                var_sym = VarSymbol(
                    name=node.left.value,
                    type=f'{collection_type}',
                    val_assigned=True,
                    read_only=node.left.read_only,
                )
                self.define(node.left.value, var_sym)
                return f"vector<{var_sym.type}> {visited_left} {node.op} {visited_right};\n"
            case _:
                raise BuilderError(f'Assignment of type {node.right.__class__.__name__} not implimented')
        self.define(node.left.value, var_sym)
        return f"{var_sym.type} {visited_left} {node.op} {visited_right};\n"

    def visit_bin_op(self, node: my_ast.BinOp) -> str:
        visited_left = self.visit(node.left)
        visited_op = self.visit(node.op)
        visited_right = self.visit(node.right)
        return f"({visited_left} {visited_op} {visited_right})"

    def visit_operator(self, node: my_ast.Operator) -> str:
        match node.value:
            case 'and':
                return '&&'
            case 'or':
                return '||'
            case _:
                return node.value

    def visit_if(self, node: my_ast.If) -> str:
        comps = []
        for comp in node.comps:
            comps.append(self.visit(comp))
        block = []
        for line in node.block.children:
            block.append(self.visit(line))
        return f"if ( {' '.join(comps)} ) {{\n{'\n'.join(block)}\n}}"

    def visit_else_if(self, node: my_ast.ElseIf) -> str:
        comps = []
        for comp in node.comps:
            comps.append(self.visit(comp))
        block = []
        for line in node.block.children:
            block.append(self.visit(line))
        return f" else if ( {' '.join(comps)} ) {{\n{'\n'.join(block)}\n}}"

    def visit_else(self, node: my_ast.Else) -> str:
        block = []
        for line in node.block.children:
            block.append(self.visit(line))
        return f" else {{\n{'\n'.join(block)}\n}}"

    def visit_compound(self, node: my_ast.Compound) -> str:
        result = []
        for child in node.children:
            result.append(self.visit(child))
        return " ".join(result)

    def visit_var(self, node: my_ast.Var) -> str:
        return node.value

    def visit_num(self, node: my_ast.Num) -> str:
        return node.value

    def visit_str(self, node: my_ast.Str) -> str:
        return f'"{node.value}"'

    def visit_collection(self, node: my_ast.Collection) -> str:
        items = []
        for item in node.items:
            items.append(self.visit(item))
        open_bracket = ''
        close_bracket = ''
        match node.type:
            case grammar.LIST:
                open_bracket = '{'
                close_bracket = '}'
        return f"{open_bracket}{', '.join(items)}{close_bracket}"

    def visit_for(self, node: my_ast.For) -> str:
        elements = []
        for element in node.elements:
            elements.append(self.visit(element))
        iterator = self.visit(node.iterator)
        searched_scope = self.search_scopes(iterator)
        my_type = searched_scope.type.replace('*', '').lower()
        self.define(
            elements[0],
            VarSymbol(
                name=elements[0],
                type=my_type,
                val_assigned=True,
                read_only=False,
            )
        )
        block = []
        for line in node.block.children:
            block.append(self.visit(line))
        return f"for ( {my_type} {elements[0]} : {iterator} ) {{\n{'\n'.join(block)}\n}}"

    def visit_pass(self, _: my_ast.Pass) -> str:
        return '(void)0;'

    def visit_print(self, node: my_ast.Print) -> str:
        result = []
        for arg in node.arguments:
            result.append(self.visit(arg))
        return f'cout << {' << '.join(result)} << "\\n";'

    def visit_eof(self, node: my_ast.Eof) -> str:
        return ""


def emit(tree: my_ast.Program, my_prog: NamedTemporaryFile) -> str:
    builder = Builder()
    with preamble(my_prog):
        for node in tree.block.children:
            my_prog.write(builder.visit(node))
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
        validator = Validator(parser.file_name)
        validator.check(tree)
        if validator.warnings:
            sys.exit(1)
        with NamedTemporaryFile(mode="+r", suffix=".cpp", delete=False) as my_prog:
            emit(tree, my_prog)
            with suppress(FileNotFoundError):
                os.remove(f"{out_path}")
            if print_out:
                with open(my_prog.name) as my_prog_file:
                    print(my_prog_file.read())
            subprocess.Popen(
                f"clang++ -Iinclude {my_prog.name} -o {out_path} && rm {my_prog.name}", shell=True
            )
        if run:
            sleep(0.1)
            subprocess.Popen(out_path, shell=True)
