import ast
from collections import OrderedDict

import grammar
from grammar import LexerType


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.file_name = lexer.file_name
        self.current_token = None
        self.next_token()
        self.user_types = []
        self.in_class = False

    @property
    def line_num(self):
        return self.current_token.line_num

    def next_token(self):
        token = self.current_token
        self.current_token = self.lexer.get_next_token()
        # print(self.current_token)
        return token

    def eat_type(self, *token_type):
        if self.current_token.type in token_type:
            self.next_token()
        else:
            raise SyntaxError(f"Line {self.line_num}")

    def eat_value(self, *token_value):
        if self.current_token.value in token_value:
            self.next_token()
        else:
            raise SyntaxError

    def preview(self, num=1):
        return self.lexer.preview_token(num)

    def program(self):
        root = ast.Compound()
        while self.current_token.type != LexerType.EOF:
            comp = self.compound_statement()
            root.children.extend(comp.children)
        return ast.Program(root)

    def struct_declaration(self):
        self.eat_value(grammar.STRUCT)
        name = self.next_token()
        self.user_types.append(name.value)
        self.eat_type(grammar.NEWLINE)
        fields = OrderedDict()
        while (
            self.current_token.indent_level > name.indent_level
        ):  # TODO: remove indent stuff
            field_type = self.type_spec()
            field = self.next_token().value
            fields[field] = field_type
            self.eat_type(grammar.NEWLINE)
        return ast.StructDeclaration(name.value, fields, self.line_num)

    def class_declaration(self):
        base = None
        constructor = None
        methods = None
        class_fields = None
        instance_fields = None
        self.in_class = True
        self.next_token()
        class_name = self.current_token
        self.eat_type(LexerType.NAME)
        if self.current_token.value == grammar.LPAREN:
            pass  # TODO impliment inheritance
        self.eat_type(grammar.NEWLINE)
        # self.indent_level += 1
        while self.current_token.indent_level == self.indent_level:
            if self.current_token.value == grammar.NEW:
                constructor = self.constructor_declaration(class_name)
        # self.indent_level -= 1
        self.in_class = False
        return ast.ClassDeclaration(
            class_name.value,
            base=base,
            constructor=constructor,
            methods=methods,
            class_fields=class_fields,
            instance_fields=instance_fields,
        )

    def variable_declaration(self):
        type_node = self.type_spec()
        var_node = ast.Var(self.current_token.value, self.line_num)
        self.eat_type(LexerType.NAME)
        var = ast.VarDecl(var_node, type_node, self.line_num)
        if self.current_token.value == grammar.ASSIGN:
            var = self.variable_declaration_assignment(var)
        return var

    def variable_declaration_assignment(self, declaration):
        return ast.Assign(
            declaration, self.next_token().value, self.expr(), self.line_num
        )

    def alias_declaration(self):
        self.eat_value(grammar.ALIAS)
        name = self.next_token()
        self.user_types.append(name.value)
        self.eat_value(grammar.ASSIGN)
        return ast.AliasDeclaration(name.value, (self.type_spec(),), self.line_num)

    def function_declaration(self):
        self.eat_value(grammar.FUNC_DEFINITION)
        if self.current_token.value == grammar.LPAREN:
            name = LexerType.ANON
        else:
            name = self.next_token()
        self.eat_value(grammar.LPAREN)
        params = OrderedDict()
        param_defaults = {}
        vararg = None
        while self.current_token.value != grammar.RPAREN:
            if self.current_token.type == LexerType.NAME:
                param_type = self.variable(self.current_token)
                self.eat_type(LexerType.NAME)
            else:
                param_type = self.type_spec()
            params[self.current_token.value] = param_type
            param_name = self.current_token.value
            self.eat_type(LexerType.NAME)
            if self.current_token.value != grammar.RPAREN:
                if self.current_token.value == grammar.ASSIGN:
                    self.eat_value(grammar.ASSIGN)
                    param_defaults[param_name] = self.expr()
                if self.current_token.value == grammar.ELLIPSIS:
                    key, value = params.popitem()
                    if not vararg:
                        vararg = []
                    vararg.append(key)
                    vararg.append(value)
                    self.eat_value(grammar.ELLIPSIS)
                    break
                if self.current_token.value != grammar.RPAREN:
                    self.eat_value(grammar.COMMA)
        self.eat_value(grammar.RPAREN)
        self.eat_value(grammar.ARROW)
        if self.current_token.value == LexerType.VOID:
            return_type = ast.Void()
            self.next_token()
        else:
            return_type = self.type_spec()
        self.eat_type(grammar.NEWLINE)
        # self.indent_level += 1
        stmts = self.compound_statement()
        # self.indent_level -= 1
        if name == LexerType.ANON:
            return ast.AnonymousFunc(
                return_type, params, stmts, self.line_num, param_defaults, vararg
            )
        else:
            return ast.FuncDecl(
                name.value,
                return_type,
                params,
                stmts,
                self.line_num,
                param_defaults,
                vararg,
            )

    def constructor_declaration(self, class_name):
        self.eat_value(grammar.NEW)
        self.eat_value(grammar.LPAREN)
        params = OrderedDict()
        param_defaults = {}
        vararg = None
        while self.current_token.value != grammar.RPAREN:
            if self.current_token.type == LexerType.NAME:
                param_type = self.variable(self.current_token)
                self.eat_type(LexerType.NAME)
            else:
                param_type = self.type_spec()
            params[self.current_token.value] = param_type
            param_name = self.current_token.value
            self.eat_type(LexerType.NAME)
            if self.current_token.value != grammar.RPAREN:
                if self.current_token.value == grammar.ASSIGN:
                    self.eat_value(grammar.ASSIGN)
                    param_defaults[param_name] = self.expr()
                if self.current_token.value == grammar.ELLIPSIS:
                    key, value = params.popitem()
                    if not vararg:
                        vararg = []
                    vararg.append(key)
                    vararg.append(value)
                    self.eat_value(grammar.ELLIPSIS)
                    break
                if self.current_token.value != grammar.RPAREN:
                    self.eat_value(grammar.COMMA)
        self.eat_value(grammar.RPAREN)
        self.eat_type(grammar.NEWLINE)
        # self.indent_level += 1
        stmts = self.compound_statement()
        # self.indent_level -= 1
        return ast.FuncDecl(
            f"{class_name}.constructor",
            ast.Void(),
            params,
            stmts,
            self.line_num,
            param_defaults,
            vararg,
        )

    def bracket_literal(self):
        token = self.next_token()
        if token.value == grammar.LCURLYBRACKET:
            return self.curly_bracket_expression(token)
        elif token.value == grammar.LPAREN:
            return self.list_expression(token)
        else:
            return self.square_bracket_expression(token)

    def function_call(self, token):
        if token.value == grammar.INPUT:
            return ast.Input(self.expr(), self.line_num)
        self.eat_value(grammar.LPAREN)
        args = []
        named_args = {}
        while self.current_token.value != grammar.RPAREN:
            while self.current_token.type == grammar.NEWLINE:
                self.eat_type(grammar.NEWLINE)
            if self.current_token.value in grammar.LBRACKETS:
                args.append(self.bracket_literal())
            elif self.preview().value == grammar.ASSIGN:
                name = self.expr().value
                self.eat_value(grammar.ASSIGN)
                named_args[name] = self.expr()
            else:
                args.append(self.expr())
            while self.current_token.type == grammar.NEWLINE:
                self.eat_type(grammar.NEWLINE)
            if self.current_token.value != grammar.RPAREN:
                self.eat_value(grammar.COMMA)
        func = ast.FuncCall(token.value, args, self.line_num, named_args)
        self.next_token()
        return func

    def type_spec(self):
        token = self.current_token
        if token.value in self.user_types:
            self.eat_type(LexerType.NAME)
            return ast.Type(token.value, self.line_num)
        self.eat_type(LexerType.TYPE)
        type_spec = ast.Type(token.value, self.line_num)
        func_ret_type = None
        if (
            self.current_token.value == grammar.LSQUAREBRACKET
            and token.value == grammar.FUNC
        ):
            self.next_token()
            func_ret_type = self.type_spec()
            self.eat_value(grammar.RSQUAREBRACKET)
        if func_ret_type:
            type_spec.func_ret_type = func_ret_type
        return type_spec

    def compound_statement(self):
        nodes = self.statement_list()
        root = ast.Compound()
        for node in nodes:
            root.children.append(node)
        return root

    def statement_list(self):
        node = self.statement()
        if self.current_token.type == grammar.NEWLINE:
            self.next_token()
        if isinstance(node, ast.Return):
            return [node]
        results = [node]
        while self.current_token.indent_level == self.indent_level:
            results.append(self.statement())
            if self.current_token.type == grammar.NEWLINE:
                self.next_token()
            elif self.current_token.type == LexerType.EOF:
                results = [x for x in results if x is not None]
                break
        return results

    def statement(self):
        if self.current_token.value == grammar.IF:
            node = self.if_statement()
        elif self.current_token.value == grammar.WHILE:
            node = self.while_statement()
        elif self.current_token.value == grammar.FOR:
            node = self.for_statement()
        elif self.current_token.value == grammar.BREAK:
            self.next_token()
            node = ast.Break(self.line_num)
        elif self.current_token.value == grammar.CONTINUE:
            self.next_token()
            node = ast.Continue(self.line_num)
        elif self.current_token.value == grammar.PASS:
            self.next_token()
            node = ast.Pass(self.line_num)
        elif self.current_token.value == grammar.CONST:
            node = self.assignment_statement(self.current_token)
        elif self.current_token.value == grammar.RETURN:
            node = self.return_statement()
        elif self.current_token.value in self.user_types:
            node = self.variable_declaration()
        elif self.current_token.type == LexerType.NAME:
            if self.preview().value == grammar.DOT:
                node = self.property_or_method(self.next_token())
            else:
                node = self.name_statement()
        elif self.current_token.value == grammar.FUNC_DEFINITION:
            node = self.function_declaration()
        elif self.current_token.value == grammar.ALIAS:
            node = self.alias_declaration()
        elif self.current_token.type == LexerType.TYPE:
            if self.current_token.value == grammar.STRUCT:
                node = self.struct_declaration()
            else:
                node = self.variable_declaration()
        elif self.current_token.value == grammar.CLASS:
            node = self.class_declaration()
        elif self.current_token.value == LexerType.EOF:
            return
        else:
            self.next_token()
            node = self.statement()
        return node

    def square_bracket_expression(self, token):
        if token.value == grammar.LSQUAREBRACKET:
            items = []
            while self.current_token.value != grammar.RSQUAREBRACKET:
                items.append(self.expr())
                if self.current_token.value == grammar.COMMA:
                    self.next_token()
                else:
                    break
            self.eat_value(grammar.RSQUAREBRACKET)
            return ast.Collection(grammar.LIST, self.line_num, False, *items)
        elif self.current_token.type == LexerType.TYPE:
            type_token = self.next_token()
            if self.current_token.value == grammar.COMMA:
                return self.dictionary_assignment(token)
            elif self.current_token.value == grammar.RSQUAREBRACKET:
                self.next_token()
                return self.collection_expression(token, type_token)
        elif self.current_token.type == LexerType.NUMBER:
            tok = self.expr()
            if self.current_token.value == grammar.COMMA:
                return self.slice_expression(tok)
            else:
                self.eat_value(grammar.RSQUAREBRACKET)
                access = self.access_collection(token, tok)
                if self.current_token.value in grammar.ASSIGNMENT_OP:
                    op = self.current_token
                    self.next_token()
                    right = self.expr()
                    if op.value == grammar.ASSIGN:
                        return ast.Assign(access, op.value, right, self.line_num)
                    else:
                        return ast.OpAssign(access, op.value, right, self.line_num)
                return access
        elif token.type == LexerType.NAME:
            self.eat_value(grammar.LSQUAREBRACKET)
            tok = self.expr()
            if self.current_token.value == grammar.COMMA:
                return self.slice_expression(tok)
            else:
                self.eat_value(grammar.RSQUAREBRACKET)
                return self.access_collection(token, tok)
        else:
            raise SyntaxError

    def slice_expression(self, token):
        pass

    def curly_bracket_expression(self, token):
        dict_or_struct = None
        if token.value == grammar.LCURLYBRACKET:
            pairs = OrderedDict()
            while self.current_token.value != grammar.RCURLYBRACKET:
                key = self.expr()
                if self.current_token.value == grammar.COLON:
                    dict_or_struct = grammar.DICT
                    self.eat_value(grammar.COLON)
                else:
                    dict_or_struct = grammar.STRUCT
                    self.eat_value(grammar.ASSIGN)
                pairs[key.value] = self.expr()
                if self.current_token.value == grammar.COMMA:
                    self.next_token()
                else:
                    break
            self.eat_value(grammar.RCURLYBRACKET)
            if dict_or_struct == grammar.DICT:
                return ast.Dict(pairs, self.line_num)
            elif dict_or_struct == grammar.STRUCT:
                return ast.StructLiteral(pairs, self.line_num)
        else:
            raise SyntaxError("Wait... what?")

    def list_expression(self, token):
        if token.value == grammar.LPAREN:
            items = []
            while self.current_token.value != grammar.RPAREN:
                items.append(self.expr())
                if self.current_token.value == grammar.COMMA:
                    self.next_token()
                else:
                    break
            self.eat_value(grammar.RPAREN)
            return ast.Collection(grammar.LIST, self.line_num, False, *items)

    def collection_expression(self, token, type_token):
        if self.current_token.value == grammar.ASSIGN:
            return self.list_of_type_assignment(token, type_token)
        else:
            raise NotImplementedError

    def access_collection(self, collection, key):
        return ast.CollectionAccess(collection, key, self.line_num)

    def list_of_type_assignment(self, token, type_token):
        raise NotImplementedError

    def dot_access(self, token):
        self.eat_value(grammar.DOT)
        field = self.current_token.value
        self.next_token()
        return ast.DotAccess(token.value, field, self.line_num)

    def name_statement(self):
        token = self.next_token()
        if token.value == grammar.PRINT:
            node = ast.Print(self.expr(), self.line_num)
        elif token.value == grammar.INPUT:
            node = ast.Input(self.expr(), self.line_num)
        elif self.current_token.value == grammar.LPAREN:
            node = self.function_call(token)
        elif self.current_token.value == grammar.LSQUAREBRACKET:
            self.next_token()
            node = self.square_bracket_expression(token)
        elif self.current_token.value in grammar.ASSIGNMENT_OP:
            node = self.assignment_statement(token)
        else:
            raise SyntaxError(f"Line {self.line_num}")
        return node

    def property_or_method(self, token):
        self.eat_value(grammar.DOT)
        field = self.current_token.value
        self.next_token()
        left = ast.DotAccess(token.value, field, self.line_num)
        token = self.next_token()
        if token.value in grammar.ASSIGNMENT_OP:
            return self.field_assignment(token, left)
        else:
            return self.method_call(token, left)

    def method_call(self, token, left):
        args = []
        named_args = {}
        while self.current_token.value != grammar.RPAREN:
            while self.current_token.type == grammar.NEWLINE:
                self.eat_type(grammar.NEWLINE)
            if self.current_token.value in grammar.LBRACKETS:
                args.append(self.bracket_literal())
            elif self.preview().value == grammar.ASSIGN:
                name = self.expr().value
                self.eat_value(grammar.ASSIGN)
                named_args[name] = self.expr()
            else:
                args.append(self.expr())
            while self.current_token.type == grammar.NEWLINE:
                self.eat_type(grammar.NEWLINE)
            if self.current_token.value != grammar.RPAREN:
                self.eat_value(grammar.COMMA)
        method = ast.MethodCall(left.obj, left.field, args, self.line_num, named_args)
        self.next_token()
        return method

    def field_assignment(self, token, left):
        if token.value == grammar.ASSIGN:
            right = self.expr()
            node = ast.Assign(left, token.value, right, self.line_num)
        elif token.value in grammar.ARITHMETIC_ASSIGNMENT_OP:
            right = self.expr()
            node = ast.OpAssign(left, token.value, right, self.line_num)
        else:
            raise SyntaxError(f"Unknown assignment operator: {token.value}")
        return node

    def dictionary_assignment(self, token):
        raise NotImplementedError

    def return_statement(self):
        self.next_token()
        return ast.Return(self.expr(), self.line_num)

    def if_statement(self):
        # self.indent_level += 1
        token = self.next_token()
        comp = ast.If(
            token.value,
            [self.expr()],
            [self.compound_statement()],
            self.line_num,
        )
        if self.current_token.indent_level < comp.indent_level:
            # self.indent_level -= 1
            return comp
        while self.current_token.value == grammar.ELSE_IF:
            self.next_token()
            comp.comps.append(self.expr())
            comp.blocks.append(self.compound_statement())
        if self.current_token.value == grammar.ELSE:
            self.next_token()
            comp.comps.append(ast.Else())
            comp.blocks.append(self.compound_statement())
        # self.indent_level -= 1
        return comp

    def while_statement(self):
        # self.indent_level += 1
        token = self.next_token()
        comp = ast.While(token.value, self.expr(), self.loop_block(), self.line_num)
        # self.indent_level -= 1
        return comp

    def for_statement(self):
        # self.indent_level += 1
        self.next_token()
        elements = []
        while self.current_token.value != grammar.IN:
            elements.append(self.expr())
            if self.current_token.value == grammar.COMMA:
                self.eat_value(grammar.COMMA)
        self.eat_value(grammar.IN)
        iterator = self.expr()
        if self.current_token.value == grammar.NEWLINE:
            self.eat_type(grammar.NEWLINE)
        block = self.loop_block()
        loop = ast.For(iterator, block, elements, self.line_num)
        # self.indent_level -= 1
        return loop

    def loop_block(self):
        nodes = self.statement_list()
        root = ast.LoopBlock()
        for node in nodes:
            root.children.append(node)
        return root

    def assignment_statement(self, token):
        if token.value == grammar.CONST:
            read_only = True
            self.next_token()
            token = self.current_token
            self.next_token()
        else:
            read_only = False
        left = self.variable(token, read_only)
        token = self.next_token()
        if token.value == grammar.ASSIGN:
            right = self.expr()
            node = ast.Assign(left, token.value, right, self.line_num)
        elif token.value in grammar.ARITHMETIC_ASSIGNMENT_OP:
            right = self.expr()
            node = ast.OpAssign(left, token.value, right, self.line_num)
        else:
            raise SyntaxError(f"Unknown assignment operator: {token.value}")
        return node

    def variable(self, token, read_only=False):
        return ast.Var(token.value, self.line_num, read_only)

    def constant(self, token):
        return ast.Constant(token.value, self.line_num)

    def factor(self):
        token = self.current_token
        preview = self.preview()
        if preview.value == grammar.DOT:
            self.next_token()
            return self.dot_access(token)
        elif token.value in (grammar.PLUS, grammar.MINUS):
            self.next_token()
            return ast.UnaryOp(token.value, self.factor(), self.line_num)
        elif token.value == grammar.NOT:
            self.next_token()
            return ast.UnaryOp(token.value, self.expr(), self.line_num)
        elif token.type == LexerType.NUMBER:
            self.next_token()
            return ast.Num(token.value, token.value_type, self.line_num)
        elif token.type == LexerType.STRING:
            self.next_token()
            return ast.Str(token.value, self.line_num)
        elif token.value == grammar.FUNC_DEFINITION:
            return self.function_declaration()
        elif token.type == LexerType.TYPE:
            return self.type_spec()
        elif token.value == grammar.LPAREN:
            if preview.value == grammar.RPAREN:
                return []
            else:
                self.next_token()
                node = self.expr()
                self.eat_value(grammar.RPAREN)
                return node
        elif preview.value == grammar.LPAREN:
            self.next_token()
            return self.function_call(token)
        elif (
            preview.value == grammar.LSQUAREBRACKET
            or token.value == grammar.LSQUAREBRACKET
        ):
            self.next_token()
            return self.square_bracket_expression(token)
        elif token.value == grammar.LCURLYBRACKET:
            self.next_token()
            return self.curly_bracket_expression(token)
        elif token.type == LexerType.NAME:
            self.next_token()
            return self.variable(token)
        elif token.type == LexerType.CONSTANT:
            self.next_token()
            return self.constant(token)
        else:
            raise SyntaxError

    def term(self):
        node = self.factor()
        while self.current_token.value in grammar.TERM_OPS:
            token = self.next_token()
            if (
                token.value in grammar.COMPARISON_OP
                or token.value in grammar.LOGICAL_OP
                or token.value in grammar.BINARY_OP
            ):
                node = ast.BinOp(node, token.value, self.expr(), self.line_num)
            elif token.value == grammar.RANGE:
                node = ast.Range(node, self.expr(), self.line_num)
            else:
                node = ast.BinOp(node, token.value, self.factor(), self.line_num)
        return node

    def expr(self):
        node = self.term()
        while self.current_token.value in (grammar.PLUS, grammar.MINUS):
            token = self.next_token()
            node = ast.BinOp(node, token.value, self.term(), self.line_num)
        return node

    def parse(self):
        node = self.program()
        if self.current_token.type != LexerType.EOF:
            raise SyntaxError("Unexpected end of program")
        return node


if __name__ == "__main__":
    from lexer import Lexer

    file = "test.my"
    with open(file) as my_file:
        l = Lexer(my_file.read(), file)
        parser = Parser(l)
        tree = parser.parse()
        print(tree)
