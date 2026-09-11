from dataclasses import dataclass
from io import StringIO
import os
from pathlib import Path
import re
import subprocess
import sys
from contextlib import suppress
from tempfile import NamedTemporaryFile
from typing import IO
from types import SimpleNamespace

import my_ast
from my_types import TYPE_MAP, PointerType
import my_types
from lexer import Lexer
from parser import Parser
import grammar
from preamble import Preamble
from visitor import (
    NodeVisitor,
    Scope,
)
from validator import Validator


class BuilderError(Exception):
    pass


def bigint_to_int(num: str) -> str:
    if "BigInt::bigint" in num:
        return num.replace('BigInt::bigint("', "")[:-2]
    return num


class Builder(NodeVisitor):
    def __init__(self, file_path: str, preamble: Preamble, is_root: bool = False):
        super().__init__()
        self.file_path = Path(file_path).absolute().resolve()
        self.preamble = preamble
        self.is_root = is_root
        self.in_class = False
        self.in_constructor = False
        self.classes = {}
        self.enums = {}
        self.structs = {}
        self.funcs = {}
        self.func_defs = {}

    @staticmethod
    def get_obj_prop(
        node: my_ast.StructDeclaration, prop_name: str
    ) -> my_ast.Node | None:
        obj = node.static_fields.get(prop_name)
        if obj is None:
            obj = node.instance_fields.get(prop_name)
            if obj is None:
                if isinstance(node, my_ast.ClassDeclaration):
                    obj = node.methods.get(prop_name)
        return obj

    def visit_void(self, _: my_ast.Void) -> str:
        return ""

    def visit_assign(self, node: my_ast.Assign) -> str:
        left = self.visit(node.left)
        right = self.visit(node.right)
        match node.right:
            case my_ast.Type(val_type=val_type):
                scoped_var = self.search_scopes(val_type)
                return f"auto {left}({scoped_var.pointer.make(right)});"
            case my_ast.Collection(items=items):
                sym_type = my_ast.get_collection_type(node.right)
                if sym_type == grammar.DICT:
                    item = list(items.items())[0]
                else:
                    item = items[0]
                sym = self.build_symbol(
                    name=left,
                    node=node.right,
                    symbol_type=sym_type,
                    symbol_subtype=item,
                    define=True,
                )
                result = f"{sym.pointer.destination_type} {left}(new {sym.pointer.subtype.destination_type}({right}));"
                return result
        return f"auto {left}({right});"
        # visited_left = self.visit(node.left)
        # if isinstance(node.left, my_ast.Var) and node.left.type is not None:
        #     if hasattr(node.right, "val_type"):
        #         node.right.val_type = node.left.type.name
        # visited_right = self.visit(node.right)
        # if isinstance(node.left, my_ast.DotAccess):
        #     with suppress(Exception):
        #         scoped_var = self.search_scopes(node.left.obj.value)
        #         scoped_var = self.search_scopes(scoped_var.type.name)
        #         method = scoped_var.methods.get(node.left.field)
        #         if method.type == my_ast.FuncType.SETTER:
        #             return f"{visited_left}({visited_right})"
        #     return f"{visited_left} {node.op} {visited_right};\n"
        # match node.right:
        #     case my_ast.Num(val_type=val_type):
        #         var_sym = self.build_symbol(
        #             name=visited_left,
        #             node=node.right,
        #             subtype=TYPE_MAP[val_type](),
        #         )
        #     case my_ast.Str():
        #         var_sym = self.build_symbol(
        #             name=visited_left,
        #             node=node.right,
        #             subtype=TYPE_MAP[grammar.STR](),
        #         )
        #     case my_ast.Var(value=value):
        #         scoped_val = self.search_scopes(value)
        #         var_sym = self.build_symbol(
        #             name=scoped_val.name,
        #             node=node.right,
        #             subtype=scoped_val.type,
        #         )
        #     case my_ast.Constant(value=value):
        #         scoped_val = self.search_scopes(value)
        #         var_sym = self.build_symbol(
        #             name=scoped_val.name,
        #             node=node.right,
        #             subtype=scoped_val.type,
        #         )
        #     case my_ast.Collection(type=collection_type, items=items):
        #         if collection_type == grammar.LIST:
        #             var_sym = self.build_symbol(
        #                 name=visited_left,
        #                 node=node.right,
        #                 subtype=TYPE_MAP[collection_type](
        #                     subtype=TYPE_MAP[items[0].val_type]()
        #                 ),
        #             )
        #         elif collection_type == grammar.TUPLE:
        #             var_sym = self.build_symbol(
        #                 name=visited_left,
        #                 node=node.right,
        #                 subtype=TYPE_MAP[collection_type](
        #                     subtypes=[TYPE_MAP[item.val_type]() for item in items]
        #                 ),
        #             )
        #         elif collection_type == grammar.SET:
        #             var_sym = self.build_symbol(
        #                 name=visited_left,
        #                 node=node.right,
        #                 subtype=TYPE_MAP[collection_type](
        #                     subtype=TYPE_MAP[items[0].val_type]()
        #                 ),
        #             )
        #             print()
        #         else:
        #             raise NotImplementedError
        #     case my_ast.Dict(items=items):
        #         var_sym = self.build_symbol(
        #             name=visited_left,
        #             node=node.right,
        #             subtype=TYPE_MAP[grammar.DICT](
        #                 left=TYPE_MAP[list(items.keys())[0].val_type](),
        #                 right=TYPE_MAP[list(items.values())[0].val_type](),
        #             ),
        #         )
        #     case my_ast.BinOp(right=right):
        #         scoped_val = self.search_scopes(right.value)
        #         if scoped_val is None:
        #             scoped_val = self.search_scopes(right.val_type)
        #         var_sym = self.build_symbol(
        #             name=visited_left,
        #             node=node.right,
        #             subtype=scoped_val.type,
        #         )
        #     case my_ast.FuncCall(name=name, arguments=args):
        #         scoped_val = self.search_scopes(name)
        #         if scoped_val.name == grammar.INPUT:
        #             left_type = self.infer_type(grammar.STR)
        #             var_sym = self.build_symbol(
        #                 name=visited_left,
        #                 node=node.right,
        #                 subtype=left_type,
        #             )
        #             assigned = self.search_scopes(
        #                 node.left.name
        #                 if hasattr(node.left, "name")
        #                 else node.left.value
        #             )
        #             if assigned is None:
        #                 self.define(visited_left, var_sym)
        #             arg = self.visit(args[0])
        #             return (
        #                 f";{left_type.destination_type} {visited_left};\n"
        #                 f"cout << {arg} << '\\n';\ncin >> {visited_left};\n"
        #             )
        #         if scoped_val.name == grammar.OPEN:
        #             scoped_val = self.search_scopes("File")
        #         var_sym = self.build_symbol(
        #             name=visited_left,
        #             node=node.right,
        #             subtype=scoped_val.type,
        #         )
        #     case my_ast.StructCreation(name=name):
        #         scoped_val = self.search_scopes(name)
        #         var_sym = self.build_symbol(
        #             name=visited_left,
        #             node=node.right,
        #             subtype=scoped_val.type,
        #         )
        #     case my_ast.DotAccess(obj=obj, field=field):
        #         scoped_val = self.search_scopes(obj.value)
        #         if scoped_val is None:
        #             scoped_val = self.search_scopes(f"{obj.value}.{field}")
        #         if isinstance(scoped_val.type, Class):
        #             scoped_val_name = scoped_val.type.name
        #             scoped_val = self.search_scopes(scoped_val_name)
        #             if scoped_val is None:
        #                 scoped_val = self.search_scopes(
        #                     f"{obj.value}.{scoped_val_name}"
        #                 )
        #             field_type = scoped_val.fields.get(field)
        #             if field_type is None:
        #                 field_type = TYPE_MAP[
        #                     scoped_val.methods[field].return_type.value
        #                 ]()
        #         else:
        #             field_type = scoped_val.type
        #         var_sym = self.build_symbol(
        #             name=visited_left,
        #             node=node.right,
        #             subtype=field_type,
        #         )
        #     case my_ast.MethodCall(obj=obj, name=name):
        #         scoped_val = self.search_scopes(obj.value)
        #         if scoped_val is None:
        #             scoped_val = self.search_scopes(name)
        #         if scoped_val is None:
        #             scoped_val = self.search_scopes(f"{obj.value}.{name}")
        #         if isinstance(scoped_val.type, Class):
        #             scoped_val = self.search_scopes(scoped_val.type.name)
        #             return_type = TYPE_MAP[scoped_val.methods[name].return_type.value]()
        #         else:
        #             return_type = scoped_val.type
        #         var_sym = self.build_symbol(
        #             name=visited_left,
        #             node=node.right,
        #             subtype=return_type,
        #         )
        #     case my_ast.Slice(left=left, right=right, item=item):
        #         scoped_val = self.search_scopes(item)
        #         if scoped_val is None:
        #             scoped_val = self.search_scopes(right.val_type)
        #         var_sym = self.build_symbol(
        #             name=visited_left,
        #             node=node.right,
        #             subtype=my_types.Auto(),
        #         )
        #     case _:
        #         raise BuilderError(
        #             f"Assignment of type {node.right.__class__.__name__} not implimented"
        #         )
        # assigned = self.search_scopes(
        #     node.left.name
        #     if hasattr(node.left, "name")
        #     else node.left.value
        #     if hasattr(node.left, "value")
        #     else ""
        # )
        # if visited_left.startswith("self."):
        #     visited_left = visited_left.replace("self.", "this->")
        # visited_right = f"{var_sym.pointer.make(visited_right)}"
        # if assigned is None:
        #     self.define(visited_left, var_sym)
        #     return f";{var_sym.pointer.destination_type} {visited_left} {node.op} {visited_right};\n"
        # else:
        #     return f";{visited_left} {node.op} {visited_right};\n"

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
        scoped_var = self.search_scopes(node.name)
        if scoped_var is None:
            return "Any"
        return scoped_var.pointer.destination_type

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
        with self.create_scope():
            for line in node.block.children:
                block.append(self.visit(line))
        return f";if ( {' '.join(comps)} ) {{\n{'\n'.join(block)}}}\n"

    def visit_else_if(self, node: my_ast.ElseIf) -> str:
        comps = []
        for comp in node.comps:
            comps.append(self.visit(comp))
        block = []
        with self.create_scope():
            for line in node.block.children:
                block.append(self.visit(line))
        return f"else if ( {' '.join(comps)} ) {{\n{'\n'.join(block)}}}\n"

    def visit_else(self, node: my_ast.Else) -> str:
        block = []
        with self.create_scope():
            for line in node.block.children:
                block.append(self.visit(line))
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
            return f'BigInt::bigint("{node.name}")'
        return node.name

    def visit_str(self, node: my_ast.Str) -> str:
        value = node.name
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

    def visit_dict(self, node: my_ast.Dict) -> str:
        self.preamble.map = True
        items = {
            self.visit(key): self.visit(node.items[key]) for key in node.items.keys()
        }
        items = [f"{{{key}, {value}}}" for key, value in items.items()]
        return f"{{ {', '.join(items)} }}"

    # def visit_collection(self, node: my_ast.Collection) -> str:
    #     items = []
    #     for item in node.items:
    #         items.append(self.visit(item))
    #     # scoped_val = self.infer_type(items[0])
    #     open_bracket = ""
    #     close_bracket = ""
    #     match node.type:
    #         case grammar.LIST:
    #             self.preamble.list = True
    #             open_bracket = "{"
    #             close_bracket = "}"
    #         case grammar.TUPLE:
    #             return f"make_tuple({', '.join(items)})"
    #         # case grammar.SET:
    #         #     self.preamble.set = True
    #         #     return f'make_set<{scoped_val.destination_type}>();\n{"\n".join(items)}'
    #     return f"{open_bracket}{', '.join(items)}{close_bracket}"

    def visit_list(self, node: my_ast.List) -> str:
        self.preamble.list = True
        open_bracket = "{"
        close_bracket = "}"
        items = []
        for item in node.items:
            items.append(self.visit(item))
        return f"{open_bracket}{', '.join(items)}{close_bracket}"

    def visit_collection_access(self, node: my_ast.CollectionAccess) -> str:
        scoped_val = self.search_scopes(node.name)
        key = self.visit(node.key)
        match scoped_val.type:
            case my_types.List():
                key = bigint_to_int(key)
                return f"{node.name}[{key}]"
            case my_types.Tuple():
                key = bigint_to_int(key)
                return f"get<{key}>({node.name})"
            case my_types.Str():
                key = bigint_to_int(key)
                return f"{node.name}[{key}]"
            case my_types.Dict():
                key = bigint_to_int(key)
                return f"{node.name}[{key}]"
        raise NotImplementedError

    def visit_for(self, node: my_ast.For) -> str:
        elements = []
        for element in node.elements:
            elements.append(self.visit(element))
        elem_str = f"[{', '.join(elements)}]" if len(elements) > 1 else elements[0]
        iterator = self.visit(node.iterator)
        iterator_sym = self.search_scopes(iterator)
        if iterator_sym is None:
            iterator_sym = SimpleNamespace()
            iterator_sym.node = node.iterator
        with self.create_scope():
            match iterator_sym.node:
                case my_ast.Range():
                    self.build_symbol(
                        name=elements[0],
                        node=node.elements[0],
                        symbol_type=my_types.Int(),
                        pointer_type=PointerType.none,
                        define=True,
                    )
                    block = []
                    for line in node.block.children:
                        block.append(self.visit(line))
                    return f";for ( auto &{elem_str} : {iterator} ) {{\n{''.join(block)}}}\n"
                case my_ast.List():
                    my_type = iterator_sym.node.items[0]
                    self.build_symbol(
                        name=elements[0],
                        node=node.elements[0],
                        symbol_type=my_type,
                        pointer_type=PointerType.none,
                        define=True,
                    )
                case my_ast.Dict():
                    my_type = list(iterator_sym.node.items.keys())[0]
                    for visited_element, element in zip(elements, node.elements, strict=True):
                        self.build_symbol(
                            name=visited_element,
                            node=element,
                            symbol_type=my_type,
                            pointer_type=PointerType.none,
                            define=True,
                        )
                case my_ast.MethodCall(obj=obj):
                    scoped_var = self.search_scopes(obj.value)
                    items = scoped_var.node.items.items()
                    for visited_element, element, item in zip(elements, node.elements, list(items)[0], strict=True):
                        self.build_symbol(
                            name=visited_element,
                            node=element,
                            symbol_type=item.val_type,
                            pointer_type=PointerType.none,
                            define=True,
                        )
                    block = []
                    for line in node.block.children:
                        block.append(self.visit(line))
                    return f";for ( auto &{elem_str} : {iterator} ) {{\n{''.join(block)}}}\n"
                case _:
                    my_type = iterator_sym.node.type
                    self.build_symbol(
                        name=elements[0],
                        node=node.elements[0],
                        symbol_type=my_type,
                        pointer_type=PointerType.none,
                        define=True,
                    )
            block = []
            for line in node.block.children:
                block.append(self.visit(line))
        return f";for ( auto &{elem_str} : {iterator_sym.pointer.dereference}{iterator} ) {{\n{''.join(block)}}}\n"

    def visit_while(self, node: my_ast.While) -> str:
        comps = []
        block = []
        for comp in node.comp:
            comps.append(self.visit(comp))
        with self.create_scope():
            for line in node.block.children:
                block.append(self.visit(line))
        return f";while ( {' '.join(comps)} ) {{\n{''.join(block)}}}\n"

    def visit_continue(self, _: my_ast.Continue) -> str:
        return ";continue;"

    def visit_break(self, _: my_ast.Break) -> str:
        return ";break;"

    def visit_range(self, node: my_ast.Range) -> str:
        self.preamble.range = True
        visited_left = self.visit(node.left)
        visited_right = self.visit(node.right)
        return f'range({visited_left}, {visited_right}, BigInt::bigint("1"))'

    def visit_pass(self, _: my_ast.Pass) -> str:
        return "(void)0;"

    def visit_func_decl(self, node: my_ast.FuncDecl) -> str:
        name = node.name
        if name in (grammar.ENTER, grammar.EXIT):
            name = f"__{name}"
        return_type = self.search_scopes(node.return_type.name)
        if return_type is not None:
            return_type = return_type.type
        else:
            return_type = self.infer_type(node.return_type.name)
        if return_type is None:
            return_type = my_types.Void()
        params = []
        func_symbol = self.build_symbol(
            name=name,
            node=node,
            symbol_type=return_type,
        )
        if not self.in_class:
            self.define(name, func_symbol)
        with self.create_scope():
            for param, param_type in node.parameters.items():
                infered_param_type = self.infer_type(param_type)
                params.append(f"{infered_param_type.destination_type} {param}")
                self.build_symbol(
                    name=param,
                    node=param_type,
                    symbol_type=infered_param_type,
                    define=True,
                )
            self.in_constructor = node.type == my_ast.FuncType.CONSTRUCTOR
            body = self.visit(node.body)
            self.in_constructor = False
        if node.type == my_ast.FuncType.CONSTRUCTOR:
            return f"{name} ({', '.join(params)}) {{\n{body};}}\n"
        if return_type.destination_type == grammar.VOID:
            decl = f"{return_type.destination_type} {name} ({', '.join(params)})"
        else:
            decl = f"{return_type.destination_type} {name} ({', '.join(params)})"
        static = "static " if node.static else ""
        result = f"{static}{decl} {{\n{body};}}\n"
        if self.in_class:
            return f"{result}"
        else:
            if self.is_root:
                self.funcs[name] = result
                self.func_defs[name] = decl
            else:
                my_import = self.import_manager.get_import_by_path(self.file_path)
                if my_import is not None:
                    my_import.body.funcs[name] = result
                    my_import.body.func_defs[name] = decl
        return ""

    def visit_return(self, node: my_ast.Return) -> str:
        return_val = self.visit(node.value)
        return f"return {return_val};\n"

    def visit_func_call(self, node: my_ast.FuncCall) -> str:
        func = self.search_scopes(node.name)
        if func is not None:
            if func.name == grammar.PRINT:
                return self.visit_print(func.node)
            if func.name == grammar.OPEN:
                return self.visit_open(node)
            # if func.name == grammar.INPUT:
            #     return self.visit_input(func.node)
        params = list(
            func.node.parameters.keys()
            if hasattr(func.node, "parameters")
            else func.node.arguments.keys()
        )
        args = self.get_args(
            arguments=node.arguments,
            parameters=params,
            named_arguments=node.named_arguments,
            parameter_defaults=func.node.parameter_defaults,
        )
        return f"{func.name}({', '.join(args)})"

    def visit_method_call(self, node: my_ast.MethodCall) -> str:
        sep = "."
        visited_obj = self.visit(node.obj)
        if self.in_class:
            self_obj = self.search_scopes(grammar.SELF)
            obj_type = self.get_obj_prop(self_obj.node, visited_obj)
            scoped_obj = self.search_scopes(obj_type.name)
        else:
            scoped_obj = self.search_scopes(
                visited_obj, default=self.search_scopes(node.name)
            )
            if isinstance(scoped_obj.node, my_ast.Enum):
                sep = "::"
        if scoped_obj.pointer.type != PointerType.none:
            sep = "->"
        class_name = scoped_obj.node.__class__.__name__
        func = self.search_scopes(class_name)
        if func is None:
            if isinstance(scoped_obj.node, my_ast.FuncDecl):
                func = scoped_obj.node
            elif isinstance(scoped_obj.node, my_ast.Var):
                func = self.search_scopes(scoped_obj.type.name)
                func = self.get_obj_prop(func.node, node.name)
            else:
                func = scoped_obj.node.methods[node.name]
        else:
            func = func.node.methods[node.name]
        args = self.get_args(
            arguments=node.arguments,
            parameters=func.parameters,
            named_arguments=node.named_arguments,
            parameter_defaults=func.parameter_defaults,
        )
        if visited_obj in self.import_names:
            visited_obj = ""
            sep = ""
        return f"{visited_obj}{sep}{node.name}({', '.join(args)})"

    def get_args(
        self,
        arguments: list[my_ast.Expression],
        parameters: list[my_ast.Expression],
        named_arguments: dict[str, my_ast.Expression],
        parameter_defaults: dict[str, my_ast.Node],
    ) -> list[str]:
        args = []
        args_visited = 0
        for arg in arguments:
            args.append(self.visit(arg))
            args_visited += 1
        for name in parameters:
            if name in named_arguments:
                args.append(self.visit(named_arguments[name]))
                args_visited += 1
        if len(parameters) > args_visited:
            for arg in list(parameters.keys())[args_visited:]:
                if arg in parameter_defaults:
                    args.append(self.visit(parameter_defaults[arg]))
        return args

    def visit_class_declaration(self, node: my_ast.ClassDeclaration) -> str:
        name = node.name
        node_constructor = node.constructor
        lower_name = name.lower()
        instance_fields = []
        static_fields = []
        print_fields = []
        methods = []
        for field, field_type in node.static_fields.items():
            scoped_field_type = self.infer_type(field_type.name)
            static_fields.append(f"static {scoped_field_type.destination_type} {field}")
            # print_fields.append(f'"    {field}: " << {name}.{field}')
        for field, field_type in node.instance_fields.items():
            scoped_field_type = self.search_scopes(field_type.name)
            instance_fields.append(
                f"{scoped_field_type.pointer.destination_type} {field}"
            )
            print_fields.append(f'"    {field}: " << {lower_name}.{field}')
        self.in_class = True
        class_sym = self.build_symbol(
            name=name,
            node=node,
            symbol_type=TYPE_MAP[grammar.CLASS](name=name),
            define=True,
        )
        with self.temp_define(key=grammar.SELF, value=class_sym):
            for method in node.methods.values():
                methods.append(self.visit(method))
            constructor: str = (
                self.visit(node_constructor)
                if node_constructor is not None
                else self.build_default_constructor(node)
            )
        self.in_class = False
        #         overload = f"""ostream & operator << (ostream & outs, const {name} & {lower_name}) {{
        # return outs << "{name} {{\\n" << {' << "\\n" << '.join(print_fields)} << "\\n}}";
        # }}"""
        result = (
            f"struct {name} {{\n"
            f"{';\n'.join(static_fields)};\n"
            f"{';\n'.join(instance_fields)};\n"
            f"{constructor}\n"
            f"{'\n'.join(methods)}\n"
            f"}};\n"
            # f"{overload}\n"
        )
        if self.is_root:
            self.classes[name] = result
        else:
            my_import = self.import_manager.get_import_by_path(self.file_path)
            if my_import is not None:
                my_import.body.classes[name] = result
        return ""

    def build_default_constructor(self, node: my_ast.ClassDeclaration) -> str:
        name = node.name
        params = []
        body = []
        for field, field_type in node.instance_fields.items():
            visited_field_type = self.visit(field_type)
            params.append(f"{visited_field_type} {field}")
            body.append(f"this->{field} = {field};")
        return f"{name}({', '.join(params)}) {{\n{'\n'.join(body)}\n}}"

    def visit_self(self, _: my_ast.Self) -> str:
        return f"this->"

    def visit_struct_declaration(self, node: my_ast.StructDeclaration) -> str:
        name = node.name
        lower_name = name.lower()
        fields = []
        print_fields = []
        for field, field_type in node.instance_fields.items():
            scoped_field_type = self.infer_type(field_type.name)
            fields.append(f"{scoped_field_type.destination_type} {field}")
            print_fields.append(f'"    {field}: " << {lower_name}.{field}')
        self.build_symbol(
            name=name,
            node=node,
            symbol_type=TYPE_MAP[grammar.STRUCT](name=name),
            define=True,
        )
        overload = f"""ostream & operator << (ostream & outs, const {name} & {lower_name}) {{
return outs << "{name} {{\\n" << {' << "\\n" << '.join(print_fields)} << "\\n}}";
}}"""
        result = f"struct {name} {{\n{';\n'.join(fields)};\n}};\n{overload}\n"
        if self.is_root:
            self.structs[name] = result
        else:
            my_import = self.import_manager.get_import_by_path(self.file_path)
            if my_import is not None:
                my_import.body.structs[name] = result
        return ""

    def visit_enum(self, node: my_ast.Enum) -> str:
        name = node.name
        fields = []
        methods = []
        subtype = self.visit(node.subtype)
        self.in_class = True
        index = 0
        for field in node.fields:
            visited_field = self.visit(field)
            if node.subtype.name == grammar.STR:
                fields.append(
                    f'inline static const {subtype} {visited_field} = "{visited_field}";'
                )
            else:
                fields.append(
                    f"inline static const {subtype} {visited_field} = {index};"
                )
                index += 1
        enum_sym = self.build_symbol(
            name=name,
            node=node,
            symbol_type=TYPE_MAP[grammar.ENUM](name=name),
            define=True,
        )
        with self.temp_define(key=grammar.SELF, value=enum_sym):
            for method in node.methods.values():
                methods.append(self.visit(method))
        self.in_class = False
        result = (
            f"class {name} {{\npublic:\n{'\n'.join(fields)}\n{'\n'.join(methods)}\n}}"
        )
        if self.is_root:
            self.enums[name] = result
        else:
            my_import = self.import_manager.get_import_by_path(self.file_path)
            if my_import is not None:
                my_import.body.enums[name] = result
        return ""

    def visit_struct_creation(self, node: my_ast.StructCreation) -> str:
        obj = self.search_scopes(node.name)
        params = list(
            obj.node.constructor.parameters.keys()
            if hasattr(obj.node, "constructor") and obj.node.constructor is not None
            else obj.node.instance_fields.keys()
        )
        args = self.get_args(
            arguments=node.arguments,
            parameters=params,
            named_arguments=node.named_arguments,
            parameter_defaults=obj.node.constructor.parameter_defaults,
        )
        return f"{{ {', '.join(args)} }}"

    def visit_with(self, node: my_ast.With) -> str:
        expr = self.visit(node.expr)
        var = self.visit(node.var)
        if isinstance(node.expr, my_ast.StructCreation):
            expr_scope = self.search_scopes(node.expr.name)
            enter_func = expr_scope.node.methods[grammar.ENTER]
            return_type = self.search_scopes(enter_func.return_type.name)
            ec_dest = expr_scope.pointer.destination_type
            rt_dest = return_type.pointer.destination_type
            ex_ent = expr.replace(grammar.LCURLYBRACKET, "", count=1)[::-1].replace(
                grammar.RCURLYBRACKET, "", count=1
            )[::-1]
            expr = (
                f"shared_ptr<{ec_dest}> __tmp = make_shared<{ec_dest}>({ex_ent});\n"
                f"shared_ptr<{rt_dest}> {var} = make_shared<{rt_dest}>(__tmp->__{grammar.ENTER}());"
            )
            enter_return_type = self.search_scopes(enter_func.return_type.name)
            with self.create_scope():
                self.build_symbol(
                    name=var,
                    node=node.var,
                    symbol_type=enter_return_type.type,
                    define=True,
                )
                body = self.visit(node.body)
            return f"{{\n{expr}\n{body}\n__tmp->__{grammar.EXIT}();\n}}"
        elif isinstance(node.expr, my_ast.FuncCall):
            print(node)
            return ""

    def visit_slice(self, node: my_ast.Slice) -> str:
        item = node.item
        if isinstance(node.left, my_ast.Void):
            left = 0
        else:
            left = bigint_to_int(self.visit(node.left))
        if isinstance(node.right, my_ast.Void):
            right = f"size({item})"
        else:
            right = bigint_to_int(self.visit(node.right))
        return f"slice({item}, {left}, {right})"

    def visit_dot_access(self, node: my_ast.DotAccess) -> str:
        visited_obj = self.visit(node.obj)
        with suppress(Exception):
            scoped_var = self.search_scopes(visited_obj)
            scoped_var = self.search_scopes(scoped_var.type.name)
            method = scoped_var.methods.get(node.field)
            if method.type == my_ast.FuncType.GETTER:
                return f"{visited_obj}.{node.field}()"
        if isinstance(node.obj, my_ast.Self):
            if isinstance(node.field, str):
                return f"{visited_obj}{node.field}"
            if isinstance(node.field, my_ast.MethodCall):
                # scoped_val = self.search_scopes(node.obj.value)
                visited_field_obj = self.visit(node.field.obj)
                field_type = self.search_scopes(visited_field_obj)
                with self.temp_define(
                    key=visited_field_obj,
                    value=self.build_symbol(
                        name=visited_field_obj, node=node.field, symbol_type=field_type
                    ),
                ):
                    field = self.visit(node.field)
            else:
                field = self.visit(node.field)
            return f"{visited_obj}{field}"
        scoped_var = self.search_scopes(visited_obj)
        if isinstance(scoped_var.node, my_ast.Enum):
            return f"{visited_obj}::{node.field}"
        return f"{visited_obj}.{node.field}"

    def visit_print(self, node: my_ast.Print) -> str:
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
            if isinstance(s.pointer.subtype, my_types.Bool):
                result.append(f"bool_to_str({s.pointer.dereference}{self.visit(arg)})")
                continue
            result.append(f"{s.pointer.dereference}{self.visit(arg)}")
        end = self.visit(node.named_arguments["end"])
        sep = self.visit(node.named_arguments["sep"])
        if not result:
            return f";cout << {end};\n"
        return f";cout << {f" << {sep} << ".join(result)} << {end};\n"

    def visit_input(self, node: my_ast.Input) -> str:
        args = []
        for arg in node.arguments:
            args.append(self.visit(arg))
        return f";cout << {' <<  " " << '.join(args)};\ncin >> {node.name};\n"

    def visit_open(self, node: my_ast.FuncCall) -> str:
        visited_args = [self.visit(arg) for arg in node.arguments]
        return f"open({', '.join(visited_args)})"

    def visit_import(self, node: my_ast.Import) -> str:
        import_name = node.name
        self.import_manager.create_import(
            name=import_name, path=node.path, parent=self.file_path
        )
        tree = parse(node.path)
        my_prog = StringIO()
        sub_prog = emit(
            file_path=node.path,
            tree=tree,
            my_prog=my_prog,
            parent_preamble=self.preamble,
        )
        self.top_scope.update(
            {f"{import_name}.{name}": var for name, var in sub_prog.scope.items()}
        )
        self.structs.update(sub_prog.structs)
        self.classes.update(sub_prog.classes)
        self.enums.update(sub_prog.enums)
        self.funcs.update(sub_prog.funcs)
        self.import_names.append(import_name)
        return ""

    def visit_eof(self, _: my_ast.Eof) -> str:
        return ""


@dataclass
class ProgramInfo:
    body: str
    scope: Scope | None
    structs: dict[str, str]
    classes: dict[str, str]
    enums: dict[str, str]
    funcs: dict[str, str]


def emit(
    file_path: str,
    tree: my_ast.Program,
    my_prog: IO[str],
    parent_preamble: Preamble | None = None,
) -> ProgramInfo:
    preamble = parent_preamble or Preamble(my_prog)
    builder = Builder(
        file_path=file_path, preamble=preamble, is_root=parent_preamble is None
    )
    body = []
    for node in tree.block.children:
        body.append(builder.visit(node))
    if parent_preamble is None:
        preamble.write()
        for my_import in builder.import_manager:
            if my_import:
                for func_def in my_import.body.func_defs.values():
                    my_prog.write(f"{func_def};\n")
        for func_def in builder.func_defs.values():
            my_prog.write(f"{func_def};\n")
        for my_import in builder.import_manager:
            if my_import:
                my_prog.write(f"{my_import.body.to_str()}\n")
        for func in builder.funcs.values():
            if func:
                my_prog.write(f"{func}\n")
        for struct in builder.structs.values():
            if struct:
                my_prog.write(f"{struct};\n")
        for _class in builder.classes.values():
            if _class:
                my_prog.write(f"{_class};\n")
        for enum in builder.enums.values():
            if enum:
                my_prog.write(f"{enum};\n")
    if parent_preamble is None:
        my_prog.write("int main(int argc, char * argv[]) {\n")
        # my_prog.write('copy(argv, argv + argc, ostream_iterator<char *>(cout, "\\n"))\n')
        # my_prog.write("int main(int argc, char * arg1[], char * arg2[]) {\n")
        # my_prog.write('cout << argc << " " << *arg1 << " " << *arg2 << "\\n";\n')
    if parent_preamble is None:
        for line in body:
            if line:
                my_prog.write(f"{line};\n")
        my_prog.write("return 0;\n")
        my_prog.write("}\n")
    my_prog.seek(0)
    return ProgramInfo(
        body=my_prog.read(),
        scope=builder.top_scope,
        structs=builder.structs,
        classes=builder.classes,
        enums=builder.enums,
        funcs=builder.funcs,
    )


def parse(source_file: str) -> my_ast.Program:
    with open(source_file) as my_file:
        code = my_file.read()
        lexer = Lexer(code, source_file)
        parser = Parser(lexer)
        return parser.parse()


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
    tree = parse(source_file)
    if not ignore_warnings:
        validator = Validator(source_file)
        validator.check(tree)
        if validator.warnings:
            sys.exit(1)
    my_str = StringIO()
    program = emit(source_file, tree, my_str).body
    with NamedTemporaryFile(mode="+r", suffix=".cpp", delete=False) as my_prog:
        program = program.replace("\n;\n", "\n")
        my_prog.write(program)
        with suppress(FileNotFoundError):
            os.remove(out_path)
        if print_out:
            with suppress(FileNotFoundError):
                proc = subprocess.Popen(
                    f"clang-format",
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                proc_result = proc.communicate(input=program.encode("utf-8"))
                print(proc_result[0].decode())
    p = subprocess.Popen(
        (
            f"clang++ -Iinclude -std=c++23 {optimization_level} "
            f"{my_prog.name} -o {out_path} && rm {my_prog.name}"
        ),
        shell=True,
    )
    result = p.wait()
    if run and result == 0:
        print("Running", end="\n\n")
        p = subprocess.Popen(out_path, shell=True)
        result = p.wait()
    sys.exit(result)
