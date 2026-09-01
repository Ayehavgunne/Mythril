import os
import re
import subprocess
import sys
from contextlib import suppress
from tempfile import NamedTemporaryFile
from time import sleep
from typing import IO

import my_ast
from my_types import TYPE_MAP, Bool, Class
from lexer import Lexer
from parser import Parser
import grammar
from preamble import Preamble
from visitor import (
    BuiltinFuncSymbol,
    ClassSymbol,
    NodeVisitor,
    VarSymbol,
    FuncSymbol,
    StructSymbol,
)
from validator import Validator


class BuilderError(Exception):
    pass


class Builder(NodeVisitor):
    def __init__(self, preamble: Preamble):
        super().__init__()
        self.preamble = preamble
        self.in_class = False
        self.in_constructor = False

    def visit_assign(self, node: my_ast.Assign) -> str:
        visited_left = self.visit(node.left)
        if isinstance(node.left, my_ast.Var) and node.left.type is not None:
            if hasattr(node.right, "val_type"):
                node.right.val_type = node.left.type.value
        visited_right = self.visit(node.right)
        if isinstance(node.left, my_ast.DotAccess):
            return f"{visited_left} {node.op} {visited_right};\n"
        if not hasattr(node.left, "read_only"):
            read_only = False
        else:
            read_only = node.left.read_only
        match node.right:
            case my_ast.Num(val_type=val_type):
                var_sym = VarSymbol(
                    name=visited_left,
                    type=TYPE_MAP[val_type](),
                    val_assigned=True,
                    read_only=read_only,
                )
            case my_ast.Str():
                var_sym = VarSymbol(
                    name=visited_left,
                    type=TYPE_MAP[grammar.STR](),
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
            case my_ast.Constant(value=value):
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
                    type=TYPE_MAP[collection_type](
                        subtype=TYPE_MAP[items[0].val_type]()
                    ),
                    val_assigned=True,
                    read_only=read_only,
                )
                self.define(visited_left, var_sym)
                return f"vector<{var_sym.type.subtype.destination_type}> {visited_left} {node.op} {visited_right};\n"
            case my_ast.BinOp(right=right):
                scoped_val = self.search_scopes(right.value)
                if scoped_val is None:
                    scoped_val = self.search_scopes(right.val_type)
                var_sym = VarSymbol(
                    name=visited_left,
                    type=scoped_val.type,
                    val_assigned=True,
                    read_only=read_only,
                )
            case my_ast.FuncCall(name=name, arguments=args):
                scoped_val = self.search_scopes(name)
                if scoped_val.name == grammar.INPUT:
                    left_type = self.infer_type(node.left.type)
                    var_sym = VarSymbol(
                        name=visited_left,
                        type=left_type,
                        val_assigned=True,
                        read_only=read_only,
                    )
                    assigned = self.search_scopes(
                        node.left.name
                        if hasattr(node.left, "name")
                        else node.left.value
                    )
                    if assigned is None:
                        self.define(visited_left, var_sym)
                    arg = self.visit(args[0])
                    return f";{left_type.destination_type} {visited_left};\ncout << {arg} << '\\n';\ncin >> {visited_left};\n"
                if scoped_val.name == grammar.OPEN:
                    scoped_val = self.search_scopes("File")
                var_sym = VarSymbol(
                    name=visited_left,
                    type=scoped_val.type,
                    val_assigned=True,
                    read_only=read_only,
                )
            case my_ast.StructCreation(name=name):
                scoped_val = self.search_scopes(name)
                var_sym = VarSymbol(
                    name=visited_left,
                    type=scoped_val.type,
                    val_assigned=True,
                    read_only=read_only,
                )
            case my_ast.DotAccess(obj=obj, field=field):
                scoped_val = self.search_scopes(obj.value)
                if isinstance(scoped_val.type, Class):
                    scoped_val = self.search_scopes(scoped_val.type.name)
                    field_type = scoped_val.fields.get(field)
                    if field_type is None:
                        field_type = TYPE_MAP[
                            scoped_val.methods[field].return_type.value
                        ]()
                else:
                    field_type = scoped_val.type
                var_sym = VarSymbol(
                    name=visited_left,
                    type=field_type,
                    val_assigned=True,
                    read_only=read_only,
                )
            case my_ast.MethodCall(obj=obj, name=name):
                scoped_val = self.search_scopes(obj.value)
                if isinstance(scoped_val.type, Class):
                    scoped_val = self.search_scopes(scoped_val.type.name)
                    return_type = TYPE_MAP[scoped_val.methods[name].return_type.value]()
                else:
                    return_type = scoped_val.type
                var_sym = VarSymbol(
                    name=visited_left,
                    type=return_type,
                    val_assigned=True,
                    read_only=read_only,
                )
            case _:
                raise BuilderError(
                    f"Assignment of type {node.right.__class__.__name__} not implimented"
                )
        assigned = self.search_scopes(
            node.left.name
            if hasattr(node.left, "name")
            else node.left.value
            if hasattr(node.left, "value")
            else ""
        )
        if visited_left.startswith("self."):
            visited_left = visited_left.replace("self.", "this->")
        if visited_right.endswith(";"):
            visited_right = visited_right[:-1]
        if assigned is None:
            self.define(visited_left, var_sym)
            return f";{var_sym.type.destination_type} {visited_left} {node.op} {visited_right};\n"
        else:
            return f";{visited_left} {node.op} {visited_right};\n"

    def visit_op_assign(self, node: my_ast.OpAssign) -> str:
        visited_left = self.visit(node.left)
        visited_right = self.visit(node.right)
        return f";{visited_left} {node.op} {visited_right};\n"

    def visit_bin_op(self, node: my_ast.BinOp) -> str:
        visited_left = self.visit(node.left)
        visited_op = self.visit(node.op)
        visited_right = self.visit(node.right)
        if visited_op == grammar.CAST:
            return f"({visited_right}){visited_left}"
        if visited_op == grammar.IN:
            return f"contains({visited_right}, {visited_left})"
        if visited_op == grammar.NOT_IN:
            return f"!contains({visited_right}, {visited_left})"
        return f"({visited_left} {visited_op} {visited_right})"

    def visit_unary_op(self, node: my_ast.UnaryOp) -> str:
        visited_op = self.visit(node.op)
        visited_exrp = self.visit(node.expr)
        return f"{visited_op} {visited_exrp}"

    def visit_type(self, node: my_ast.Type) -> str:
        return self.search_scopes(node.value).type.destination_type

    def visit_operator(self, node: my_ast.Operator) -> str:
        match node.value:
            case "and":
                return "&&"
            case "or":
                return "||"
            case "not":
                return "!"
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
        return f";if ( {' '.join(comps)} ) {{\n{'\n'.join(block)}}}\n"

    def visit_else_if(self, node: my_ast.ElseIf) -> str:
        comps = []
        for comp in node.comps:
            comps.append(self.visit(comp))
        block = []
        self.new_scope()
        for line in node.block.children:
            block.append(self.visit(line))
        self.pop_scope()
        return f"else if ( {' '.join(comps)} ) {{\n{'\n'.join(block)}}}\n"

    def visit_else(self, node: my_ast.Else) -> str:
        block = []
        self.new_scope()
        for line in node.block.children:
            block.append(self.visit(line))
        self.pop_scope()
        return f"else {{\n{'\n'.join(block)}}}\n"

    def visit_compound(self, node: my_ast.Compound) -> str:
        result = []
        for child in node.children:
            result.append(self.visit(child))
        return "".join(result)

    def visit_var(self, node: my_ast.Var) -> str:
        return node.value

    def visit_constant(self, node: my_ast.Constant) -> str:
        return node.value

    def visit_num(self, node: my_ast.Num) -> str:
        if node.val_type == grammar.INT:
            return f'BigInt::bigint("{node.value}")'
        return node.value

    def visit_str(self, node: my_ast.Str) -> str:
        value = node.value
        if "{" in value:
            self.preamble.format = True
            pattern = re.compile(r"\{(.*?)\}")
            matches = pattern.findall(value)
            final_matches = []
            for match in matches:
                value = value.replace(f"{{{match}}}", "{}")
                if "self." in match:
                    match = match.replace("self.", "this->")
                final_matches.append(f"string({match})")
            return f'format("{value}", {", ".join(final_matches)})'
        return f'"{value}"'

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
        return f";for ( auto {elements[0]} : {iterator} ) {{\n{''.join(block)}}}\n"

    def visit_while(self, node: my_ast.While) -> str:
        comps = []
        block = []
        for comp in node.comp:
            comps.append(self.visit(comp))
        self.new_scope()
        for line in node.block.children:
            block.append(self.visit(line))
        self.pop_scope()
        return f";while ( {' '.join(comps)} ) {{\n{''.join(block)}}}\n"

    def visit_continue(self, node: my_ast.Continue) -> str:
        return "continue;"

    def visit_break(self, node: my_ast.Break) -> str:
        return "break;"

    def visit_range(self, node: my_ast.Range) -> str:
        self.preamble.range = True
        visited_left = self.visit(node.left)
        if "BigInt::bigint(" in visited_left:
            # temp hack to deal with bigint incompatibility with iota
            visited_left = visited_left.replace('BigInt::bigint("', "")[:-2]
        visited_right = self.visit(node.right)
        return f"views::iota({visited_left}, {visited_right})"

    def visit_pass(self, _: my_ast.Pass) -> str:
        return "(void)0;"

    def visit_func_decl(self, node: my_ast.FuncDecl) -> str:
        name = node.name
        return_type = self.infer_type(node.return_type.value)
        params = []
        func_symbol = FuncSymbol(
            name=name,
            type=return_type,
            parameters=node.parameters,
            parameter_defaults=node.parameter_defaults,
        )
        if not self.in_class:
            self.define(name, func_symbol)
        self.new_scope()
        for param, param_type in node.parameters.items():
            infered_param_type = self.infer_type(param_type)
            params.append(f"{infered_param_type.destination_type} {param}")
            self.define(param, VarSymbol(name=param, type=infered_param_type))
        self.in_constructor = node.constructor
        body = self.visit(node.body)
        self.pop_scope()
        self.in_constructor = False
        if node.constructor:
            return f"{name} ({', '.join(params)}) {{\n{body};}}\n"
        return f"{return_type.destination_type} {name} ({', '.join(params)}) {{\n{body};}}\n"

    def visit_return(self, node: my_ast.Return) -> str:
        return_val = self.visit(node.value)
        return f";return {return_val};\n"

    def visit_func_call(self, node: my_ast.FuncCall) -> str:
        func = self.search_scopes(node.name)
        args = []
        if isinstance(func, BuiltinFuncSymbol):
            if func.name == grammar.PRINT:
                return self.visit_print(node)
            if func.name == grammar.OPEN:
                return self.visit_open(node)
            # if func.name == grammar.INPUT:
            #     return self.visit_input(node)
        args_visited = 0
        for arg in node.arguments:
            args.append(self.visit(arg))
            args_visited += 1
        for name in func.parameters:
            if name in node.named_arguments:
                args.append(self.visit(node.named_arguments[name]))
                args_visited += 1
        if len(func.parameters) > args_visited:
            for arg in list(func.parameters.keys())[args_visited:]:
                args.append(self.visit(func.parameter_defaults[arg]))
        return f"{func.name}({', '.join(args)})"

    def visit_method_call(self, node: my_ast.MethodCall) -> str:
        obj = node.obj
        if not isinstance(obj, str):
            obj = self.visit(obj)
        func = self.search_scopes(obj)
        func = self.search_scopes(func.type.name)
        func = func.methods[node.name]
        if isinstance(node.obj, my_ast.Node):
            obj = self.visit(node.obj)
        else:
            obj = node.obj
        args = []
        args_visited = 0
        for arg in node.arguments:
            args.append(self.visit(arg))
            args_visited += 1
        for name in func.parameters:
            if name in node.named_arguments:
                args.append(self.visit(node.named_arguments[name]))
                args_visited += 1
        if len(func.parameters) > args_visited:
            for arg in list(func.parameters.keys())[args_visited:]:
                if arg in func.parameter_defaults:
                    args.append(self.visit(func.parameter_defaults[arg]))
        return f"{obj}.{func.name}({', '.join(args)})"

    def visit_print(self, node: my_ast.FuncCall) -> str:
        result = []
        self.preamble.print = True
        for arg in node.arguments:
            s = (
                self.search_scopes(arg.value)
                if hasattr(arg, "value")
                else self.search_scopes(grammar.INT)
            )
            if s is None:
                s = self.search_scopes(grammar.INT)
            if isinstance(s.type, Bool):
                result.append(f"bool_to_str({self.visit(arg)})")
                continue
            result.append(self.visit(arg))
        return f';cout << {" << ' ' << ".join(result)} << "\\n";\n'

    def visit_open(self, node: my_ast.FuncCall) -> str:
        visited_args = [self.visit(arg) for arg in node.arguments]
        return f"open({', '.join(visited_args)})"

    # def visit_input(self, node: my_ast.Input) -> str:
    #     args = []
    #     for arg in node.arguments:
    #         args.append(self.visit(arg))
    #     return f'cout << {' <<  " " << '.join(args)};\ncin >> {node.name};\n'

    def visit_class_declaration(self, node: my_ast.ClassDeclaration) -> str:
        name = node.name
        lower_name = name.lower()
        instance_fields = []
        static_fields = []
        print_fields = []
        methods = []
        for field, field_type in node.static_fields.items():
            scoped_field_type = self.infer_type(field_type.value)
            static_fields.append(
                f"static {scoped_field_type.destination_type} {field};"
            )
            # print_fields.append(f'"    {field}: " << {name}.{field}')
        for field, field_type in node.instance_fields.items():
            scoped_field_type = self.infer_type(field_type.value)
            instance_fields.append(f"{scoped_field_type.destination_type} {field};")
            print_fields.append(f'"    {field}: " << {lower_name}.{field}')
        self.in_class = True
        for method in node.methods:
            methods.append(self.visit(method))
        constructor: str = self.visit(node.constructor)
        self.in_class = False
        self.define(
            name,
            ClassSymbol(
                name=name,
                type=TYPE_MAP[grammar.CLASS](name=name),
                fields=node.instance_fields,
                parameters=node.constructor.parameters,
                parameter_defaults=node.constructor.parameter_defaults,
                methods={method.name: method for method in node.methods},
            ),
        )
        overload = f"""ostream & operator << (ostream & outs, const {name} & {lower_name}) {{
return outs << "{name} {{\\n" << {' << "\\n" << '.join(print_fields)} << "\\n}}";
}}"""
        return f";struct {name} {{\n{'\n'.join(static_fields)}\n{'\n'.join(instance_fields)}\n{constructor}\n{'\n'.join(methods)}\n}};\n{overload}\n"

    def visit_self(self, _: my_ast.Self) -> str:
        return f"this->"

    def visit_struct_declaration(self, node: my_ast.StructDeclaration) -> str:
        name = node.name
        lower_name = name.lower()
        fields = []
        print_fields = []
        for field, field_type in node.instance_fields.items():
            scoped_field_type = self.infer_type(field_type.value)
            fields.append(f"{scoped_field_type.destination_type} {field};")
            print_fields.append(f'"    {field}: " << {lower_name}.{field}')
        self.define(
            name,
            StructSymbol(
                name=name,
                type=TYPE_MAP[grammar.STRUCT](name=name),
                fields=node.instance_fields,
            ),
        )
        overload = f"""ostream & operator << (ostream & outs, const {name} & {lower_name}) {{
return outs << "{name} {{\\n" << {' << "\\n" << '.join(print_fields)} << "\\n}}";
}}"""
        return f";struct {name} {{\n{'\n'.join(fields)}\n}};\n{overload}\n"

    def visit_struct_creation(self, node: my_ast.StructCreation) -> str:
        obj = self.search_scopes(node.name)
        args = []
        args_visited = 0
        for arg in node.arguments:
            args.append(f"{self.visit(arg)}")
            args_visited += 1
        for name in obj.parameters:
            if name in node.named_arguments:
                args.append(self.visit(node.named_arguments[name]))
                args_visited += 1
        if len(obj.parameters) > args_visited:
            for arg in list(obj.parameters.keys())[args_visited:]:
                args.append(self.visit(obj.parameter_defaults[arg]))
        return f"{{ {', '.join(args)} }}"

    def visit_dot_access(self, node: my_ast.DotAccess) -> str:
        visited_obj = self.visit(node.obj)
        if isinstance(node.obj, my_ast.Self):
            return f"{visited_obj}{node.field}"
        return f"{visited_obj}.{node.field}"

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
    my_prog.write("int main(int argc, char * argv[]) {\n")
    # my_prog.write('copy(argv, argv + argc, ostream_iterator<char *>(cout, "\\n"))\n')
    # my_prog.write("int main(int argc, char * arg1[], char * arg2[]) {\n")
    # my_prog.write('cout << argc << " " << *arg1 << " " << *arg2 << "\\n";\n')
    for line in main:
        my_prog.write(f"{line};\n")
    my_prog.write("\n;return 0;\n")
    my_prog.write("}\n")
    my_prog.seek(0)


def build_prog(
    source_file: str,
    out_path: str = "",
    run: bool = False,
    print_out: bool = False,
    optimization_level: str = "-O0",
    ignore_warnings: bool = False,
):
    o = source_file.replace(".my", "")
    if not out_path:
        out_path = o
    with open(source_file) as my_file:
        code = my_file.read()
        lexer = Lexer(code, source_file)
        parser = Parser(lexer)
        tree = parser.parse()
        if not ignore_warnings:
            validator = Validator(parser.file_name)
            validator.check(tree)
            if validator.warnings:
                sys.exit(1)
        with NamedTemporaryFile(mode="+r", suffix=".cpp", delete=False) as my_prog:
            emit(tree, my_prog)
            with suppress(FileNotFoundError):
                os.remove(out_path)
            if print_out:
                with open(my_prog.name) as my_prog_file:
                    print(my_prog_file.read())
            subprocess.Popen(
                f"clang++ -Iinclude -std=c++23 {optimization_level} {my_prog.name} -o {out_path} && rm {my_prog.name}",
                shell=True,
            )
        if run:
            sleep(0.1)
            subprocess.Popen(out_path, shell=True)
