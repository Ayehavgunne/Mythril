import os
import subprocess
import sys
from contextlib import suppress
from tempfile import NamedTemporaryFile
from time import sleep
from typing import IO

import my_ast
from my_types import type_map
from lexer import Lexer
from parser import Parser
import grammar
from preamble import Preamble
from visitor import ClassSymbol, NodeVisitor, VarSymbol, FuncSymbol, StructSymbol
from validator import Validator


class BuilderError(Exception):
    pass


class Builder(NodeVisitor):
    def __init__(self, preamble: Preamble):
        super().__init__()
        self.preamble = preamble

    def visit_assign(self, node: my_ast.Assign) -> str:
        visited_left = self.visit(node.left)
        visited_right = self.visit(node.right)
        if isinstance(node.left, my_ast.CollectionAccess):
            read_only = False
        else:
            read_only = node.left.read_only
        match node.right:
            case my_ast.Num(val_type=val_type):
                var_sym = VarSymbol(
                    name=visited_left,
                    type=type_map[val_type](),
                    val_assigned=True,
                    read_only=read_only,
                )
            case my_ast.Str():
                var_sym = VarSymbol(
                    name=visited_left,
                    type=type_map[grammar.STR](),
                    val_assigned=True,
                    read_only=read_only,
                )
            case my_ast.Var(value=value):
                scoped_val = self.search_scopes(value)
                var_sym = VarSymbol(
                    name=scoped_val.name,
                    type=scoped_val.type,
                    val_assigned=True,
                    read_only=read_only,
                )
            case my_ast.Collection(type=collection_type, items=items):
                var_sym = VarSymbol(
                    name=visited_left,
                    type=type_map[collection_type](
                        subtype=type_map[items[0].val_type]()
                    ),
                    val_assigned=True,
                    read_only=read_only,
                )
                self.define(visited_left, var_sym)
                return f"vector<{var_sym.type.subtype.destination_type}> {visited_left} {node.op} {visited_right};\n"
            case my_ast.BinOp(right=right):
                scoped_val = self.search_scopes(right.value)
                var_sym = VarSymbol(
                    name=visited_left,
                    type=scoped_val.type,
                    val_assigned=True,
                    read_only=read_only,
                )
            case my_ast.FuncCall(name=name):
                scoped_val = self.search_scopes(name)
                var_sym = VarSymbol(
                    name=visited_left,
                    type=scoped_val.type,
                    val_assigned=True,
                    read_only=read_only,
                )
            case my_ast.StructCreation(
                name=name, arguments=args, named_arguments=named_args
            ):
                scoped_val = self.search_scopes(name)
                var_sym = VarSymbol(
                    name=visited_left,
                    type=scoped_val.type,
                    val_assigned=True,
                    read_only=read_only,
                )
            case _:
                raise BuilderError(
                    f"Assignment of type {node.right.__class__.__name__} not implimented"
                )
        assigned = self.search_scopes(node.left.name if hasattr(node.left, 'name') else node.left.value)
        if assigned is None:
            self.define(visited_left, var_sym)
            return f"{var_sym.type.destination_type} {visited_left} {node.op} {visited_right};\n"
        else:
            return f"{visited_left} {node.op} {visited_right};\n"

    def visit_bin_op(self, node: my_ast.BinOp) -> str:
        visited_left = self.visit(node.left)
        visited_op = self.visit(node.op)
        visited_right = self.visit(node.right)
        return f"({visited_left} {visited_op} {visited_right})"

    def visit_operator(self, node: my_ast.Operator) -> str:
        match node.value:
            case "and":
                return "&&"
            case "or":
                return "||"
            case _:
                return node.value

    def visit_if(self, node: my_ast.If) -> str:
        comps = []
        for comp in node.comps:
            comps.append(self.visit(comp))
        block = []
        self.new_scope()
        for line in node.block.children:
            block.append(self.visit(line))
        self.pop_scope()
        return f"if ( {' '.join(comps)} ) {{\n{'\n'.join(block)}\n}}\n"

    def visit_else_if(self, node: my_ast.ElseIf) -> str:
        comps = []
        for comp in node.comps:
            comps.append(self.visit(comp))
        block = []
        self.new_scope()
        for line in node.block.children:
            block.append(self.visit(line))
        self.pop_scope()
        return f" else if ( {' '.join(comps)} ) {{\n{'\n'.join(block)}\n}}\n"

    def visit_else(self, node: my_ast.Else) -> str:
        block = []
        self.new_scope()
        for line in node.block.children:
            block.append(self.visit(line))
        self.pop_scope()
        return f" else {{\n{'\n'.join(block)}\n}}\n"

    def visit_compound(self, node: my_ast.Compound) -> str:
        result = []
        for child in node.children:
            result.append(self.visit(child))
        return "".join(result)

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
        open_bracket = ""
        close_bracket = ""
        match node.type:
            case grammar.LIST:
                self.preamble.list = True
                open_bracket = "{"
                close_bracket = "}"
        return f"{open_bracket}{', '.join(items)}{close_bracket}"

    def visit_collection_access(self, node: my_ast.CollectionAccess) -> str:
        key = self.visit(node.key)
        if node.type == grammar.LIST:
            return f"{node.name}[{key}]"
        raise NotImplementedError

    def visit_for(self, node: my_ast.For) -> str:
        elements = []
        for element in node.elements:
            elements.append(self.visit(element))
        iterator = self.visit(node.iterator)
        self.new_scope()
        if not isinstance(node.iterator, my_ast.Range):
            searched_scope = self.search_scopes(iterator)
            my_type = searched_scope.type
            self.define(
                elements[0],
                VarSymbol(
                    name=elements[0],
                    type=my_type,
                    val_assigned=True,
                    read_only=False,
                ),
            )
        else:
            self.preamble.range = True
            left = self.visit(node.iterator.left)
            right = self.visit(node.iterator.right)
            left_scope = self.search_scopes(left)
            right_scope = self.search_scopes(right)
            if left_scope is not None:
                my_type = left_scope.type
            elif right_scope is not None:
                my_type = right_scope.type
            else:
                infered_left = self.infer_type(left)
                infered_right = self.infer_type(right)
                if infered_left is not None:
                    my_type = infered_left
                elif infered_right is not None:
                    my_type = infered_right
                else:
                    raise BuilderError
        block = []
        for elem in node.elements:
            self.define(elem.value, VarSymbol(name=elem.value, type=my_type))
        for line in node.block.children:
            block.append(self.visit(line))
        self.pop_scope()
        return f"for ( auto {elements[0]} : {iterator} ) {{\n{''.join(block)}}}\n"

    def visit_continue(self, node: my_ast.Continue) -> str:
        return "continue;"

    def visit_break(self, node: my_ast.Break) -> str:
        return "break;"

    def visit_range(self, node: my_ast.Range) -> str:
        visited_left = self.visit(node.left)
        visited_right = self.visit(node.right)
        return f"views::iota({visited_left}, {visited_right})"

    def visit_pass(self, _: my_ast.Pass) -> str:
        return "(void)0;"

    def visit_func_decl(self, node: my_ast.FuncDecl) -> str:
        name = node.name
        return_type = self.infer_type(node.return_type.value)()
        params = []
        func_symbol = FuncSymbol(
            name=name, type=return_type, parameters=node.parameters
        )
        self.define(name, func_symbol)
        self.new_scope()
        for param, param_type in node.parameters.items():
            infered_param_type = self.infer_type(param_type)()
            params.append(f"{infered_param_type.destination_type} {param}")
            self.define(param, VarSymbol(name=param, type=infered_param_type))
        body = self.visit(node.body)
        self.pop_scope()
        return f"{return_type.destination_type} {name} ({', '.join(params)}) {{\n{body}}}\n"

    def visit_return(self, node: my_ast.Return) -> str:
        return_val = self.visit(node.value)
        return f"return {return_val};\n"

    def visit_func_call(self, node: my_ast.FuncCall) -> str:
        func = self.search_scopes(node.name)
        args = []
        for arg in node.arguments:
            args.append(self.visit(arg))
        return f"{func.name}({', '.join(args)})"

    def visit_method_call(self, node: my_ast.MethodCall) -> str:
        func = self.search_scopes(node.name)
        obj = node.obj
        args = []
        for arg in node.arguments:
            if arg is not None:
                args.append(self.visit(arg))
        return f"{obj}.{func.name}({', '.join(args)});"

    def visit_print(self, node: my_ast.Print) -> str:
        result = []
        self.preamble.print = True
        for arg in node.arguments:
            result.append(self.visit(arg))
        return f'cout << {" << ".join(result)} << "\\n";\n'

    def visit_class_declaration(self, node: my_ast.ClassDeclaration) -> str:
        name = node.name
        lower_name = name.lower()
        instance_fields = []
        static_fields = []
        print_fields = []
        methods = []
        for field, field_type in node.static_fields.items():
            scoped_field_type = self.infer_type(field_type.value)()
            static_fields.append(f"static {scoped_field_type.destination_type} {field};")
            # print_fields.append(f'"    {field}: " << {name}.{field}')
        for field, field_type in node.instance_fields.items():
            scoped_field_type = self.infer_type(field_type.value)()
            instance_fields.append(f"{scoped_field_type.destination_type} {field};")
            print_fields.append(f'"    {field}: " << {lower_name}.{field}')
        for method in node.methods:
            methods.append(self.visit(method))
        constructor = self.visit(node.constructor)
        self.define(
            name,
            ClassSymbol(
                name=name, type=type_map[grammar.CLASS](name=name), fields=node.instance_fields
            ),
        )
        overload = f"""ostream & operator << (ostream & outs, const {name} & {lower_name}) {{
return outs << "{name} {{\\n" << {' << "\\n" << '.join(print_fields)} << "\\n}}";
}}"""
        return f"struct {name} {{\n{'\n'.join(static_fields)}\n{'\n'.join(instance_fields)}\n{'\n'.join(methods)}\n}};\n{overload}\n"

    def visit_self(self, node: my_ast.Self) -> str:
        return f'this->{node.field}'

    def visit_struct_declaration(self, node: my_ast.StructDeclaration) -> str:
        name = node.name
        lower_name = name.lower()
        fields = []
        print_fields = []
        for field, field_type in node.fields.items():
            scoped_field_type = self.infer_type(field_type.value)()
            fields.append(f"{scoped_field_type.destination_type} {field};")
            print_fields.append(f'"    {field}: " << {lower_name}.{field}')
        self.define(
            name,
            StructSymbol(
                name=name, type=type_map[grammar.STRUCT](name=name), fields=node.fields
            ),
        )
        overload = f"""ostream & operator << (ostream & outs, const {name} & {lower_name}) {{
return outs << "{name} {{\\n" << {' << "\\n" << '.join(print_fields)} << "\\n}}";
}}"""
        return f"struct {name} {{\n{'\n'.join(fields)}\n}};\n{overload}\n"

    def visit_struct_creation(self, node: my_ast.StructCreation) -> str:
        args = []
        for arg in node.arguments:
            args.append(f"{self.visit(arg)}")
        return f"{{ {', '.join(args)} }}"

    def visit_dot_access(self, node: my_ast.DotAccess) -> str:
        return f"{node.obj}.{node.field}"

    def visit_eof(self, _: my_ast.Eof) -> str:
        return ""


def emit(tree: my_ast.Program, my_prog: IO[str]) -> str:
    preamble = Preamble(my_prog)
    builder = Builder(preamble)
    funcs = []
    structs = []
    main = []
    for node in tree.block.children:
        if isinstance(node, my_ast.FuncDecl):
            funcs.append(builder.visit(node))
        elif isinstance(node, my_ast.StructDeclaration):
            structs.append(builder.visit(node))
        else:
            main.append(builder.visit(node))
    preamble.write()
    for func in funcs:
        my_prog.write(f"{func}\n")
    for struct in structs:
        my_prog.write(f"{struct}\n")
    my_prog.write("int main(void) {\n")
    for line in main:
        my_prog.write(line)
    my_prog.write("\nreturn 0;\n")
    my_prog.write("}\n")
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
                f"clang++ -Iinclude -std=c++23 {my_prog.name} -o {out_path} && rm {my_prog.name}",
                shell=True,
            )
        if run:
            sleep(0.1)
            subprocess.Popen(out_path, shell=True)
