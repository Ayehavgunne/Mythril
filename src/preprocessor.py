import warnings

import grammar
import my_ast
from grammar import LexerType
from visitor import (
    AliasSymbol,
    CollectionSymbol,
    FuncSymbol,
    NodeVisitor,
    StructSymbol,
    VarSymbol,
)


def flatten(container):
    for i in container:
        if isinstance(i, (list, tuple)):
            for j in flatten(i):
                if j:
                    yield j
        else:
            if i:
                yield i


# noinspection PyUnusedLocal
def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return f"Warning {message}\n"


warnings.formatwarning = warning_on_one_line


class Preprocessor(NodeVisitor):
    def __init__(self, file_name=None):
        super().__init__()
        self.file_name = file_name
        self.warnings = False
        self.return_flag = False
        # self.num_types = (
        # 	self.search_scopes(BOOL),
        # 	self.search_scopes(INT),
        # 	self.search_scopes(INT8),
        # 	self.search_scopes(INT32),
        # 	self.search_scopes(INT128),
        # 	self.search_scopes(DEC),
        # 	self.search_scopes(FLOAT)
        # )

    def check(self, node: my_ast.Program):
        res = self.visit(node)
        if self.unvisited_symbols:
            warnings.warn(
                f"Unused variables ({','.join(sym_name for sym_name in self.unvisited_symbols)})"
            )
        return res

    def visit_program(self, node: my_ast.Program):
        return self.visit(node.block)

    def visit_if(self, node: my_ast.If):
        blocks = []
        for x, block in enumerate(node.blocks):
            self.visit(node.comps[x])
            blocks.append(self.visit(block))
        return blocks

    def visit_else(self, _: my_ast.Else):
        pass

    def visit_while(self, node: my_ast.While):
        self.visit(node.comp)
        self.visit(node.block)

    def visit_for(self, node: my_ast.For):
        for element in node.elements:
            elem_type = self.visit(node.iterator)
            if isinstance(elem_type, CollectionSymbol):
                elem_type = elem_type.item_types
            var_sym = VarSymbol(name=element.value, type=elem_type)
            var_sym.val_assigned = True
            self.define(var_sym.name, var_sym)
        self.visit(node.block)

    def visit_loop_block(self, node: my_ast.LoopBlock):
        results = []
        for child in node.children:
            results.append(self.visit(child))
        return results

    def visit_break(self, _: my_ast.Break):
        pass

    def visit_continue(self, _: my_ast.Continue):
        pass

    def visit_constant(self, node: my_ast.Constant):
        if node.value == grammar.TRUE or node.value == grammar.FALSE:
            return self.search_scopes(grammar.BOOL)
        elif (
            node.value == grammar.NAN
            or node.value == grammar.INF
            or node.value == grammar.NEGATIVE_INF
        ):
            return self.search_scopes(grammar.DEC)
        else:
            return NotImplementedError

    def visit_num(self, node: my_ast.Num):
        return self.infer_type(node.value)

    def visit_str(self, node: my_ast.Str):
        return self.infer_type(node.value)

    def visit_type(self, node: my_ast.Type):
        typ = self.search_scopes(node.value)
        if typ is self.search_scopes(grammar.FUNC):
            typ.return_type = self.visit(node.func_ret_type)
        return typ

    def visit_assign(
        self, node: my_ast.Assign
    ):  # TODO clean up this mess of a function, Match statement!
        collection_type = None
        field_assignment = None
        collection_assignment = None
        if isinstance(node.left, my_ast.VarDecl):
            var_name = node.left.value.value
            value = self.infer_type(node.left.type)
            value.accessed = True
        elif isinstance(node.right, my_ast.Collection):
            var_name = node.left.value
            value, collection_type = self.visit(node.right)
        elif isinstance(node.left, my_ast.DotAccess):
            field_assignment = True
            var_name = self.visit(node.left)
            value = self.visit(node.right)
        elif isinstance(node.left, my_ast.CollectionAccess):
            collection_assignment = True
            var_name = node.left.collection.value
            # key = node.left.key.value
            value = self.visit(node.right)
        else:
            var_name = node.left.value
            value = self.visit(node.right)
            if isinstance(value, VarSymbol):
                value = value.type
        lookup_var = self.search_scopes(var_name)
        if not lookup_var:
            if collection_type:
                col_sym = CollectionSymbol(
                    name=var_name, type=value, item_types=collection_type
                )
                col_sym.val_assigned = True
                self.define(var_name, col_sym)
            elif field_assignment:
                if var_name is value:
                    return
                else:
                    warnings.warn(
                        f"file={self.file_name} line={node.line_num} Type Error: What are you trying to do?!?! (fix this message)"
                    )
                    self.warnings = True
            elif isinstance(value, FuncSymbol):
                value.name = var_name
                self.define(var_name, value)
            elif value.name == grammar.FUNC:
                var = self.visit(node.right)
                if isinstance(var, FuncSymbol):
                    self.define(var_name, var)
                else:
                    val_info = self.search_scopes(node.right.value)
                    func_sym = FuncSymbol(
                        name=var_name,
                        type=val_info.type.return_type,
                        parameters=val_info.parameters,
                        body=val_info.body,
                        parameter_defaults=val_info.parameter_defaults,
                    )
                    self.define(var_name, func_sym)
            else:
                var_sym = VarSymbol(
                    name=var_name, type=value, read_only=node.left.read_only
                )
                var_sym.val_assigned = True
                self.define(var_name, var_sym)
        else:
            if collection_assignment and lookup_var.item_types == value:
                return
            if lookup_var.read_only:
                warnings.warn(
                    f"file={self.file_name} line={var_name}: Cannot change the value of a variable declared constant: {node.line_num}"
                )
                self.warnings = True
            lookup_var.val_assigned = True
            if lookup_var.type in (
                self.search_scopes(grammar.DEC),
                self.search_scopes(grammar.FLOAT),
            ) and value in (
                self.search_scopes(grammar.INT),
                self.search_scopes(grammar.DEC),
                self.search_scopes(grammar.FLOAT),
            ):
                return
            if lookup_var.type is value:
                return
            if lookup_var.type is value.type:
                return
            if isinstance(value, AliasSymbol):
                value.accessed = True
                if (
                    value.type is self.search_scopes(grammar.FUNC)
                    and value.type.return_type == lookup_var.type
                ):
                    return
            if hasattr(value, "value") and value.value == lookup_var.type.name:
                return
            warnings.warn(
                f"file={self.file_name} line={node.line_num} Type Error: Not good things happening (fix this message)"
            )
            self.warnings = True

    def visit_op_assign(self, node: my_ast.OpAssign):
        left = self.visit(node.left)
        right = self.visit(node.right)
        left_type = self.infer_type(left)
        right_type = self.infer_type(right)
        any_type = self.search_scopes(grammar.ANY)
        if left_type in (
            self.search_scopes(grammar.DEC),
            self.search_scopes(grammar.FLOAT),
        ) and right_type in (
            self.search_scopes(grammar.INT),
            self.search_scopes(grammar.DEC),
            self.search_scopes(grammar.FLOAT),
        ):  # TODO: implicit type conversion needs an expanded official solution
            return left_type
        if right_type is left_type or left_type is any_type or right_type is any_type:
            return left_type
        else:
            warnings.warn(
                f"file={self.file_name} line={node.line_num}: Things that should not be happening ARE happening (fix this message)"
            )
            self.warnings = True

    # def visit_field_assignment(self, node):
    #     obj = self.search_scopes(node.obj)
    #     return self.visit(obj.type.fields[node.field])

    def visit_var(self, node: my_ast.Var):
        var_name = node.value
        val = self.search_scopes(var_name)
        if val is None:
            warnings.warn(
                f"file={self.file_name} line={node.line_num}: Name Error: {var_name!r}"
            )
            self.warnings = True
        else:
            if not val.val_assigned:
                warnings.warn(
                    f"file={self.file_name} line={var_name}: {node.line_num} is being accessed before it was defined"
                )
                self.warnings = True
            val.accessed = True
            return val

    def visit_bin_op(self, node: my_ast.BinOp):
        if node.op == grammar.CAST:
            self.visit(node.left)
            return self.infer_type(self.visit(node.right))
        else:
            left = self.visit(node.left)
            right = self.visit(node.right)
            left_type = self.infer_type(left)
            right_type = self.infer_type(right)
            any_type = self.search_scopes(grammar.ANY)
            # if left_type in self.num_types:
            # 	if right_type in self.num_types:
            # 		return left_type
            if (
                right_type is left_type
                or left_type is any_type
                or right_type is any_type
            ):
                return left_type
            else:
                warnings.warn(
                    f"file={self.file_name} line={node.line_num}: types do not match for operation {node.op}, got {left} : {right}"
                )
                self.warnings = True

    def visit_unary_op(self, node: my_ast.UnaryOp):
        return self.visit(node.expr)

    def visit_range(self, node: my_ast.Range):
        left = self.visit(node.left)
        right = self.visit(node.right)
        left_type = self.infer_type(left)
        right_type = self.infer_type(right)
        any_type = self.search_scopes(grammar.ANY)
        if left_type in (
            self.search_scopes(grammar.INT),
            self.search_scopes(grammar.DEC),
            self.search_scopes(grammar.FLOAT),
        ) and right_type in (
            self.search_scopes(grammar.INT),
            self.search_scopes(grammar.DEC),
            self.search_scopes(grammar.FLOAT),
        ):
            return left_type
        if right_type is left_type or left_type is any_type or right_type is any_type:
            return left_type
        else:
            warnings.warn(
                f"file={self.file_name} line={node.line_num}: Please don't do what you just did there ever again. It bad (fix this message)"
            )
            self.warnings = True

    def visit_compound(self, node: my_ast.Compound):
        results = []
        for child in node.children:
            result = self.visit(child)
            if result:
                results.append(result)
        return results

    # def visit_type_declaration(self, node):
    #     typs = []
    #     for t in node.collection:
    #         typs.append(self.visit(t))
    #     if len(typs) == 1:
    #         typs = typs[0]
    #     else:
    #         typs = tuple(typs)
    #     typ = AliasSymbol(name=node.name.value, type=typs)
    #     self.define(typ.name, typ)

    def visit_func_decl(self, node: my_ast.FuncDecl):
        func_name = node.name
        func_type = self.search_scopes(node.return_type.value)
        if func_type and func_type.name == grammar.FUNC:
            func_type.return_type = self.visit(node.return_type.func_ret_type)
        self.define(
            func_name,
            FuncSymbol(
                name=func_name,
                type=func_type,
                parameters=node.parameters,
                body=node.body,
                parameter_defaults=node.parameter_defaults,
            ),
        )
        self.new_scope()
        if node.varargs:
            varargs_type = self.search_scopes(grammar.LIST)
            varargs_type.type = node.varargs[1].value
            varargs = CollectionSymbol(
                node.varargs[0], varargs_type, self.search_scopes(node.varargs[1].value)
            )
            varargs.val_assigned = True
            self.define(varargs.name, varargs)
        for k, v in node.parameters.items():
            var_type = self.search_scopes(v.value)
            if var_type is self.search_scopes(grammar.FUNC):
                sym = FuncSymbol(k, v.func_ret_type, None, None)
            elif isinstance(var_type, AliasSymbol):
                var_type.accessed = True
                if var_type.type is self.search_scopes(grammar.FUNC):
                    sym = FuncSymbol(k, var_type.type.return_type, None, None)
                else:
                    raise NotImplementedError
            else:
                sym = VarSymbol(k, var_type)
            sym.val_assigned = True
            self.define(sym.name, sym)
        return_types = self.visit(node.body)
        return_types = list(flatten(return_types))
        if self.return_flag:
            self.return_flag = False
            for ret_type in return_types:
                infered_type = self.infer_type(ret_type)
                if infered_type is not func_type:
                    warnings.warn(
                        f"file={self.file_name} line={node.line_num}: The actual return type does not match the declared return type: {func_name}"
                    )
                    self.warnings = True
        elif func_type != "void":  # TODO: void no longer a thing
            warnings.warn(
                f"file={self.file_name} line={node.line_num}: No return value was specified for function: {func_name}"
            )
            self.warnings = True
        func_symbol = FuncSymbol(
            func_name, func_type, node.parameters, node.body, node.parameter_defaults
        )
        self.define(func_name, func_symbol, 1)
        self.drop_top_scope()

    def visit_anonymous_func(self, node: my_ast.AnonymousFunc):
        func_type = self.search_scopes(node.return_type.value)
        self.new_scope()
        for k, v in node.parameters.items():
            var_type = self.search_scopes(v.value)
            if var_type is self.search_scopes(grammar.FUNC):
                sym = FuncSymbol(
                    name=k, type=v.func_ret_type, parameters=None, body=None
                )
            else:
                sym = VarSymbol(name=k, type=var_type)
            sym.val_assigned = True
            self.define(sym.name, sym)
        func_symbol = FuncSymbol(
            name=LexerType.ANON,
            type=func_type,
            parameters=node.parameters,
            body=node.body,
        )
        return_var_type = self.visit(func_symbol.body)
        return_var_type = list(flatten(return_var_type))
        for ret_type in return_var_type:
            if self.infer_type(ret_type) is not func_type:
                warnings.warn(
                    f"file={self.file_name} line={node.line_num}: The actual return type does not match the declared return type"
                )
                self.warnings = True
        self.drop_top_scope()
        return func_symbol

    def visit_func_call(self, node: my_ast.FuncCall):
        func_name = node.name
        func = self.search_scopes(func_name)
        for x, param in enumerate(func.parameters.values()):
            if x < len(node.arguments):
                var = self.visit(node.arguments[x])
                param_ss = self.search_scopes(param.value)
                # if param_ss in self.num_types and (var in self.num_types or var.type in self.num_types):
                # 	continue
                if (
                    param_ss != self.search_scopes(grammar.ANY)
                    and param.value != var.name
                    and param.value != var.type.name
                ):
                    raise TypeError
            else:
                func_param_keys = list(func.parameters.keys())
                if (
                    func_param_keys[x] not in node.named_arguments
                    and func_param_keys[x] not in func.parameter_defaults
                ):
                    warnings.warn(
                        f"file={self.file_name} line={node.line_num}: Missing arguments to function: {func_name!r}"
                    )
                    self.warnings = True
                else:
                    if func_param_keys[x] in node.named_arguments and (
                        param.value
                        != self.visit(node.named_arguments[func_param_keys[x]]).name
                    ):
                        raise TypeError
        if func is None:
            warnings.warn(
                f"file={self.file_name} line={node.line_num}: Name Error: {func_name!r}"
            )
            self.warnings = True
        else:
            func.accessed = True
            return func.type

    def visit_method_call(self, node: my_ast.MethodCall):  # Not done here!
        method_name = node.name
        _ = self.search_scopes(node.obj)
        method = self.search_scopes(method_name)
        for x, param in enumerate(method.parameters.values()):
            if x < len(node.arguments):
                var = self.visit(node.arguments[x])
                param_ss = self.search_scopes(param.value)
                # if param_ss in self.num_types and (var in self.num_types or var.type in self.num_types):
                # 	continue
                if (
                    param_ss != self.search_scopes(grammar.ANY)
                    and param.value != var.name
                    and param.value != var.type.name
                ):
                    raise TypeError
            else:
                method_param_keys = list(method.parameters.keys())
                if (
                    method_param_keys[x] not in node.named_arguments
                    and method_param_keys[x] not in method.parameter_defaults
                ):
                    raise TypeError("Missing arguments to method")
                else:
                    if method_param_keys[x] in node.named_arguments and (
                        param.value
                        != self.visit(node.named_arguments[method_param_keys[x]]).name
                    ):
                        raise TypeError
        if method is None:
            warnings.warn(
                f"file={self.file_name} line={node.line_num}: Name Error: {method_name!r}"
            )
            self.warnings = True
        else:
            method.accessed = True
            return method.type

    def visit_struct_declaration(self, node: my_ast.StructDeclaration):
        sym = StructSymbol(name=node.name, fields=node.fields)
        self.define(sym.name, sym)

    def visit_return(self, node: my_ast.Return):
        res = self.visit(node.value)
        self.return_flag = True
        return res

    def visit_pass(self, _: my_ast.Pass):
        pass  # HA!

    def visit_var_decl(self, node: my_ast.VarDecl):
        type_name = node.type_node.value
        type_symbol = self.search_scopes(type_name)
        var_name = node.var_node.value
        var_symbol = VarSymbol(name=var_name, type=type_symbol)
        self.define(var_symbol.name, var_symbol)

    def visit_collection(self, node: my_ast.Collection):
        types = []
        for item in node.items:
            types.append(self.visit(item))
        # if types[1:] == types[:-1]:
        # 	return self.search_scopes(ARRAY), types[0]
        # else:
        return self.search_scopes(grammar.LIST), self.search_scopes(grammar.ANY)

    def visit_dot_access(self, node: my_ast.DotAccess):
        obj = self.search_scopes(node.obj)
        obj.accessed = True
        return self.visit(obj.type.fields[node.field])

    def visit_dict(self, node: my_ast.Dict):
        for key in node.items:
            value = self.search_scopes(key)
            if value:
                value.accessed = True
        return self.search_scopes(grammar.DICT)

    def visit_collection_access(self, node: my_ast.Collection):
        collection = self.search_scopes(node.collection.value)
        collection.accessed = True
        if isinstance(node.key, my_ast.Var):
            key = self.infer_type(node.key.value)
        else:
            key = self.visit(node.key)
        if collection.type is self.search_scopes(
            grammar.LIST
        ) or collection.type is self.search_scopes(grammar.SET):
            if key is not self.search_scopes(
                grammar.INT
            ) and key.type is not self.search_scopes(grammar.INT):
                warnings.warn(
                    f"file={self.file_name} line={node.line_num}: Something something error... huh? (fix this message)"
                )
                self.warnings = True
            return collection.item_types
        elif collection.type is self.search_scopes(
            grammar.DICT
        ) or collection.type is self.search_scopes(grammar.ENUM):
            if key is not self.search_scopes(
                grammar.STR
            ) and key.type is not self.search_scopes(grammar.STR):
                warnings.warn(
                    f"file={self.file_name} line={node.line_num}: Dude....... don't (fix this message)"
                )
                self.warnings = True
            return self.search_scopes(grammar.ANY)
        else:
            warnings.warn(
                f"file={self.file_name} line={node.line_num}: WHY? (fix this message)"
            )
            self.warnings = True

    def visit_print(self, node: my_ast.Print):
        if node.value:
            self.visit(node.value)

    def visit_input(self, node: my_ast.Input):
        self.visit(node.value)


if __name__ == "__main__":
    from lexer import Lexer
    from parser import Parser

    f = "test.my"
    with open(f) as my_file:
        code = my_file.read()
        lexer = Lexer(code, f)
        parser = Parser(lexer)
        tree = parser.parse()
        symtab_builder = Preprocessor(parser.file_name)
        symtab_builder.check(tree)
        if not symtab_builder.warnings:
            print("Looks good!")
