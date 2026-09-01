from prettyprinter import pprint

import grammar
import my_ast
from grammar import LexerType, TokenType
from lexer import Lexer, Token


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.file_name = lexer.file_name
        self.current_token = Token(TokenType.PROGRAM_START, "", 0, 0)
        self._indent_level = 0
        self.next_token()
        self.user_types = []
        self.eof = False
        self.in_class = False
        self.in_constructor = False

    @property
    def line_num(self) -> int:
        return self.current_token.line_num

    def next_token(self) -> Token:
        token = self.current_token
        self.current_token = self.lexer.get_next_token()
        return token

    @property
    def indent_level(self):
        return self._indent_level

    def decriment_indent_level(self):
        self._indent_level -= 1
        if self._indent_level < 0:
            raise ParserError("Indent should not be negative")
        return self._indent_level

    def increment_indent_level(self):
        self._indent_level += 1
        return self._indent_level

    def compare_indent(self) -> bool:
        if self.current_token.token_type == TokenType.NEWLINE:
            look_ahead = 1
            preview_token = self.preview(look_ahead)
            while preview_token.token_type == TokenType.NEWLINE:
                look_ahead += 1
                preview_token = self.preview(look_ahead)
            return preview_token.indent_level == self.indent_level
        return self.current_token.indent_level == self.indent_level

    def eat_type(self, *token_types: grammar.TokenType) -> None:
        if self.current_token.token_type in token_types:
            self.next_token()
        else:
            raise SyntaxError(
                f"Line {self.line_num}: {self.current_token.token_type} not in {token_types}"
            )

    def eat_value(self, *token_value: str) -> None:
        if self.current_token.value in token_value:
            self.next_token()
        else:
            raise SyntaxError(
                f"'{self.current_token.value.replace('\n', '\\n')}' not in {token_value} Line {self.line_num}"
            )

    def preview(self, num: int = 1) -> Token | None:
        return self.lexer.preview_token(num)

    def program(self) -> my_ast.Program:
        root = my_ast.Compound()
        while self.current_token.token_type != TokenType.EOF:
            comp = self.compound_statement()
            root.children.extend(comp.children)
        return my_ast.Program(block=root)

    def struct_declaration(self) -> my_ast.StructDeclaration:
        self.eat_value(grammar.STRUCT)
        name = self.next_token()
        self.user_types.append(name.value)
        self.eat_type(TokenType.NEWLINE)
        self.increment_indent_level()
        fields = {}
        while self.current_token.indent_level > name.indent_level:
            self.field_definition(fields)
        self.decriment_indent_level()
        return my_ast.StructDeclaration(
            name=name.value,
            instance_fields=fields,
            static_fields={},
            line_num=self.line_num,
        )

    def field_definition(self, fields: dict[str, my_ast.Type]) -> None:
        field = self.next_token().value
        self.eat_value(grammar.TYPE_DELIMETER)
        field_type = self.type_spec()
        fields[field] = field_type
        self.eat_type(TokenType.NEWLINE)

    def class_declaration(self) -> my_ast.ClassDeclaration:
        self.in_class = True
        self.next_token()
        class_name = self.current_token
        self.user_types.append(class_name.value)
        self.eat_type(TokenType.NAME)
        if self.current_token.value == grammar.LPAREN:
            raise NotImplementedError  # TODO impliment inheritance
        base = my_ast.NotDoneYet()
        self.eat_type(TokenType.NEWLINE)
        self.increment_indent_level()
        constructor = None
        methods = []
        static_fields = {}
        instance_fields = {}
        while self.compare_indent():
            if self.current_token.value == grammar.NEW:
                constructor = self.constructor_declaration(class_name.value)
            elif self.current_token.value == grammar.STATIC:
                self.next_token()
                self.field_definition(static_fields)
            elif self.current_token.token_type == TokenType.NAME:
                self.field_definition(instance_fields)
            elif self.current_token.value == grammar.FUNC_DEFINITION:
                methods.append(self.function_declaration())
            elif self.current_token.token_type == TokenType.NEWLINE:
                self.next_token()
            else:
                print("missed something")
        self.decriment_indent_level()
        self.in_class = False
        return my_ast.ClassDeclaration(
            name=class_name.value,
            base=base,
            constructor=constructor,
            methods=methods,
            static_fields=static_fields,
            instance_fields=instance_fields,
            line_num=self.line_num,
        )

    def class_self(self) -> my_ast.Expression:
        line_num = self.line_num
        token = self.next_token()
        if self.current_token.value != grammar.DOT:
            return my_ast.Self(line_num=line_num)
        access = self.dot_access(token)
        if self.current_token.value == grammar.ASSIGN:
            return self.field_assignment(self.next_token(), access)
        return access

    def variable_declaration(self, token: Token) -> my_ast.Var | my_ast.Assign:
        var_node = my_ast.Var(value=token.value, line_num=self.line_num)
        self.eat_value(grammar.TYPE_DELIMETER)
        type_node = self.type_spec()
        var = my_ast.VarDecl(value=var_node, type=type_node, line_num=self.line_num)
        if self.current_token.value == grammar.ASSIGN:
            var = self.assignment_statement(self.next_token(), var)
        return var

    def alias_declaration(self) -> my_ast.AliasDeclaration:
        self.eat_value(grammar.ALIAS)
        name = self.next_token()
        self.user_types.append(name.value)
        self.eat_value(grammar.ASSIGN)
        return my_ast.AliasDeclaration(
            name=name.value, collection=(self.type_spec(),), line_num=self.line_num
        )

    def function_declaration(self) -> my_ast.FuncDecl | my_ast.AnonymousFunc:
        self.eat_value(grammar.FUNC_DEFINITION)
        if self.current_token.value == grammar.LPAREN:
            name = LexerType.ANON
        else:
            name = self.next_token()
        self.eat_value(grammar.LPAREN)
        params = {}
        param_defaults = {}
        varargs = []
        while self.current_token.value != grammar.RPAREN:
            self.param_definition(params, param_defaults, varargs)
        self.eat_value(grammar.RPAREN)
        self.eat_value(grammar.ARROW)
        if self.current_token.value == LexerType.VOID:
            return_type = my_ast.Void(line_num=self.line_num)
            self.next_token()
        else:
            return_type = self.type_spec()
        self.eat_type(TokenType.NEWLINE)
        self.increment_indent_level()
        stmts = self.compound_statement()
        self.decriment_indent_level()
        if name == LexerType.ANON:
            return my_ast.AnonymousFunc(
                return_type=return_type,
                parameters=params,
                body=stmts,
                line_num=self.line_num,
                parameter_defaults=param_defaults,
                varargs=varargs,
            )
        else:
            return my_ast.FuncDecl(
                name=name.value,
                return_type=return_type,
                parameters=params,
                body=stmts,
                line_num=self.line_num,
                parameter_defaults=param_defaults,
                varargs=varargs,
            )

    def param_definition(
        self, params: dict, param_defaults: dict, varargs: list
    ) -> None:
        if self.current_token.token_type == TokenType.NAME:
            param_var = self.variable(self.current_token)
            self.eat_type(TokenType.NAME)
        else:
            raise NotImplementedError
        self.eat_value(grammar.TYPE_DELIMETER)
        params[param_var.value] = self.type_spec()
        # param_type = params[param_var.value]
        if self.current_token.value != grammar.RPAREN:
            if self.current_token.value == grammar.ASSIGN:
                self.eat_value(grammar.ASSIGN)
                param_defaults[param_var.value] = self.expr()
            if self.current_token.value == grammar.ELLIPSIS:
                key, value = params.popitem()
                varargs.append(key)
                varargs.append(value)
                self.eat_value(grammar.ELLIPSIS)
                return
            if self.current_token.value != grammar.RPAREN:
                self.eat_value(grammar.COMMA)

    def constructor_declaration(self, class_name: str) -> my_ast.FuncDecl:
        self.in_constructor = True
        self.eat_value(grammar.NEW)
        self.eat_value(grammar.LPAREN)
        params = {}
        param_defaults = {}
        varargs = []
        while self.current_token.value != grammar.RPAREN:
            self.param_definition(params, param_defaults, varargs)
        self.eat_value(grammar.RPAREN)
        self.eat_type(TokenType.NEWLINE)
        self.increment_indent_level()
        stmts = self.compound_statement()
        self.decriment_indent_level()
        self.in_constructor = False
        return my_ast.FuncDecl(
            name=f"{class_name}",
            return_type=my_ast.Void(line_num=self.line_num),
            parameters=params,
            body=stmts,
            line_num=self.line_num,
            parameter_defaults=param_defaults,
            varargs=varargs,
            constructor=True,
        )

    def bracket_literal(self) -> my_ast.Expression:
        token = self.next_token()
        if token.value == grammar.LCURLYBRACKET:
            return self.curly_bracket_expression(token)
        elif token.value == grammar.LPAREN:
            return self.list_expression(token)
        else:
            return self.square_bracket_expression(token)

    def function_call(self, token: Token) -> my_ast.FuncCall:
        self.eat_value(grammar.LPAREN)
        args = []
        named_args = {}
        preview_token = self.preview()
        while self.current_token.value != grammar.RPAREN:
            while self.current_token.token_type == TokenType.NEWLINE:
                self.eat_type(TokenType.NEWLINE)
            if self.current_token.value in grammar.LBRACKETS:
                args.append(self.bracket_literal())
            elif (preview_token.value if preview_token else "") == grammar.ASSIGN:
                name = self.expr().value
                self.eat_value(grammar.ASSIGN)
                named_args[name] = self.expr()
            else:
                args.append(self.expr())
            while self.current_token.token_type == TokenType.NEWLINE:
                self.eat_type(TokenType.NEWLINE)
            if self.current_token.value != grammar.RPAREN:
                self.eat_value(grammar.COMMA)
        func = my_ast.FuncCall(
            name=token.value,
            arguments=args,
            line_num=self.line_num,
            named_arguments=named_args,
        )
        self.next_token()
        return func

    def type_spec(self) -> my_ast.Type:
        token = self.current_token
        if token.value == grammar.VOID:
            line_num = self.line_num
            self.next_token()
            return my_ast.Void(line_num=line_num)
        if token.value in self.user_types:
            self.eat_type(TokenType.NAME)
            return my_ast.Type(value=token.value, line_num=self.line_num)
        self.eat_type(TokenType.TYPE)
        type_spec = my_ast.Type(value=token.value, line_num=self.line_num)
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

    def compound_statement(self) -> my_ast.Compound:
        nodes = self.statement_list()
        root = my_ast.Compound()
        for node in nodes:
            root.children.append(node)
        return root

    def statement_list(self) -> list[my_ast.Statement]:
        node = self.statement()
        if isinstance(node, my_ast.Return):
            return [node]
        results = [node]
        while self.compare_indent() and results[-1] != my_ast.Eof():
            results.append(self.statement())
        return results

    def statement(self) -> my_ast.Statement:
        if self.current_token.value == grammar.IF:
            node = self.if_statement()
        elif self.current_token.value == grammar.ELSE_IF:
            node = self.else_if_statement()
        elif self.current_token.value == grammar.ELSE:
            node = self.else_statement()
        elif self.current_token.value == grammar.WHILE:
            node = self.while_statement()
        elif self.current_token.value == grammar.FOR:
            node = self.for_statement()
        elif self.current_token.value == grammar.BREAK:
            self.next_token()
            node = my_ast.Break(line_num=self.line_num)
        elif self.current_token.value == grammar.CONTINUE:
            self.next_token()
            node = my_ast.Continue(line_num=self.line_num)
        elif self.current_token.value == grammar.PASS:
            self.next_token()
            node = my_ast.Pass(line_num=self.line_num)
        elif self.current_token.value == grammar.CONST:
            node = self.assignment_statement(self.current_token)
        elif self.current_token.value == grammar.RETURN:
            node = self.return_statement()
        elif self.current_token.value in self.user_types:
            node = self.variable_declaration()
        elif self.current_token.token_type == TokenType.NAME:
            preview_token = self.preview()
            if (preview_token.value if preview_token else "") == grammar.DOT:
                node = self.property_or_method(self.next_token())
            elif (
                preview_token.value if preview_token else ""
            ) == grammar.LCURLYBRACKET:
                node = self.struct_creation(self.next_token())
            else:
                node = self.name_statement()
        # elif self.current_token.value == grammar.LCURLYBRACKET:
        #     preview_token = self.preview(-1)
        #     print(self.current_token)
        elif self.current_token.value == grammar.FUNC_DEFINITION:
            node = self.function_declaration()
        elif self.current_token.value == grammar.ALIAS:
            node = self.alias_declaration()
        elif self.current_token.value == grammar.STRUCT:
            node = self.struct_declaration()
        elif self.current_token.token_type == TokenType.TYPE:
            node = self.variable_declaration()
        elif self.current_token.value == grammar.CLASS:
            node = self.class_declaration()
        elif self.in_class and self.current_token.value == grammar.SELF:
            node = self.class_self()
        elif self.current_token.value == LexerType.EOF:
            self.eof = True
            node = my_ast.Eof()
        else:
            if self.current_token.value == grammar.NEWLINE:
                self.eat_type(TokenType.NEWLINE)
            else:
                print(f"This should not happen. Token: {self.current_token}")
                self.next_token()
            node = self.statement()
        return node

    def square_bracket_expression(self, token: Token) -> my_ast.Expression:
        if token.value == grammar.LSQUAREBRACKET:
            items = []
            while self.current_token.value != grammar.RSQUAREBRACKET:
                items.append(self.expr())
                if self.current_token.value == grammar.COMMA:
                    self.next_token()
                else:
                    break
            self.eat_value(grammar.RSQUAREBRACKET)
            return my_ast.Collection(
                type=grammar.LIST, line_num=self.line_num, read_only=False, items=items
            )
        elif self.current_token.token_type == TokenType.TYPE:
            type_token = self.next_token()
            if self.current_token.value == grammar.COMMA:
                return self.dictionary_assignment(token)
            elif self.current_token.value == grammar.RSQUAREBRACKET:
                self.next_token()
                return self.collection_expression(token, type_token)
        elif self.current_token.token_type == TokenType.NUMBER:
            tok = self.expr()
            if self.current_token.value == grammar.COMMA:
                return self.slice_expression(tok)
            else:
                self.eat_value(grammar.RSQUAREBRACKET)
                access = self.access_collection(token, tok, grammar.LIST)
                if self.current_token.value in grammar.ASSIGNMENT_OP:
                    op = self.current_token
                    self.next_token()
                    right = self.expr()
                    if op.value == grammar.ASSIGN:
                        return my_ast.Assign(
                            left=access,
                            op=op.value,
                            right=right,
                            line_num=self.line_num,
                        )
                    else:
                        return my_ast.OpAssign(
                            left=access,
                            op=op.value,
                            right=right,
                            line_num=self.line_num,
                        )
                return access
        elif token.token_type == TokenType.NAME:
            self.eat_value(grammar.LSQUAREBRACKET)
            tok = self.expr()
            if self.current_token.value == grammar.COMMA:
                return self.slice_expression(tok)
            else:
                self.eat_value(grammar.RSQUAREBRACKET)
                return self.access_collection(token, tok, grammar.LIST)
        raise SyntaxError

    def slice_expression(self, _: my_ast.Expression) -> my_ast.Expression:
        raise NotImplementedError

    def curly_bracket_expression(
        self, token: Token
    ) -> my_ast.Dict | my_ast.StructLiteral:
        dict_or_struct = None
        if token.value == grammar.LCURLYBRACKET:
            pairs = {}
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
                return my_ast.Dict(items=pairs, line_num=self.line_num)
            elif dict_or_struct == grammar.STRUCT:
                return my_ast.StructLiteral(fields=pairs, line_num=self.line_num)
        raise SyntaxError("Wait... what?")

    def list_expression(self, token: Token) -> my_ast.Collection:
        if token.value == grammar.LPAREN:
            items = []
            while self.current_token.value != grammar.RPAREN:
                items.append(self.expr())
                if self.current_token.value == grammar.COMMA:
                    self.next_token()
                else:
                    break
            self.eat_value(grammar.RPAREN)
            return my_ast.Collection(
                type=grammar.LIST, line_num=self.line_num, read_only=False, items=items
            )
        raise SyntaxError

    def struct_creation(self, token: Token) -> my_ast.StructCreation:
        self.next_token()
        self.eat_value(grammar.LCURLYBRACKET)
        args = []
        named_args = {}
        preview_token = self.preview()
        while self.current_token.value != grammar.RCURLYBRACKET:
            while self.current_token.token_type == TokenType.NEWLINE:
                self.eat_type(TokenType.NEWLINE)
            if self.current_token.value in grammar.LBRACKETS:
                args.append(self.bracket_literal())
            elif (preview_token.value if preview_token else "") == grammar.ASSIGN:
                name = self.expr().value
                self.eat_value(grammar.ASSIGN)
                named_args[name] = self.expr()
            else:
                args.append(self.expr())
            while self.current_token.token_type == TokenType.NEWLINE:
                self.eat_type(TokenType.NEWLINE)
            if self.current_token.value != grammar.RCURLYBRACKET:
                self.eat_value(grammar.COMMA)
        self.eat_value(grammar.RCURLYBRACKET)
        return my_ast.StructCreation(
            name=token.value,
            arguments=args,
            line_num=self.line_num,
            named_arguments=named_args,
        )

    def collection_expression(
        self, token: Token, type_token: Token
    ) -> my_ast.Collection:
        if self.current_token.value == grammar.ASSIGN:
            return self.list_of_type_assignment(token, type_token)
        else:
            raise NotImplementedError

    def access_collection(
        self, token: Token, key: my_ast.Node, collection_type: str
    ) -> my_ast.CollectionAccess:
        return my_ast.CollectionAccess(
            name=token.value, type=collection_type, key=key, line_num=self.line_num
        )

    def list_of_type_assignment(self, _: Token, __: Token) -> my_ast.Collection:
        raise NotImplementedError

    def dot_access(self, token: Token) -> my_ast.DotAccess:
        self.eat_value(grammar.DOT)
        field = self.current_token.value
        self.next_token()
        if token.value == grammar.SELF:
            obj = my_ast.Self(line_num=self.line_num)
        else:
            obj = self.variable(token)
        access = my_ast.DotAccess(obj=obj, field=field, line_num=token.line_num)
        if self.current_token.value == grammar.LPAREN:
            return self.method_call(self.current_token, access)
        return access

    # def self_access(self, token: Token) -> my_ast.Self:
    #     return my_ast.Self(line_num=token.line_num)

    def name_statement(self) -> my_ast.Statement:
        token = self.next_token()
        if token.value == grammar.PRINT or token.value == grammar.OPEN:
            # node = my_ast.Print(
            #     name=grammar.PRINT, arguments=[self.expr()], line_num=self.line_num
            # )
            node = self.function_call(token)
        elif token.value == grammar.INPUT:
            node = my_ast.Input(
                name=grammar.INPUT, arguments=[self.expr()], line_num=self.line_num
            )
        elif self.current_token.value == grammar.LPAREN:
            node = self.function_call(token)
        elif self.current_token.value == grammar.LSQUAREBRACKET:
            self.next_token()
            node = self.square_bracket_expression(token)
        elif self.current_token.value in grammar.ASSIGNMENT_OP:
            node = self.assignment_statement(token)
        elif self.current_token.value == grammar.TYPE_DELIMETER:
            # self.eat_value(grammar.TYPE_DELIMETER)
            node = self.variable_declaration(token)
        elif self.in_constructor:
            node = self.variable(token)
        else:
            raise SyntaxError(
                f"Line {self.line_num} name {token.value} not implimented"
            )
        return node

    def property_or_method(
        self, token: Token
    ) -> my_ast.Assign | my_ast.OpAssign | my_ast.MethodCall:
        self.eat_value(grammar.DOT)
        field = self.current_token.value
        self.next_token()
        left = my_ast.DotAccess(obj=token.value, field=field, line_num=self.line_num)
        token = self.next_token()
        if token.value in grammar.ASSIGNMENT_OP:
            return self.field_assignment(token, left)
        else:
            return self.method_call(token, left)

    def method_call(self, _: Token, left: my_ast.DotAccess) -> my_ast.MethodCall:
        args = []
        named_args = {}
        if self.current_token.value == grammar.LPAREN:
            self.next_token()
        preview_token = self.preview()
        while self.current_token.value != grammar.RPAREN:
            while self.current_token.token_type == TokenType.NEWLINE:
                self.eat_type(TokenType.NEWLINE)
            if self.current_token.value in grammar.LBRACKETS:
                args.append(self.bracket_literal())
            elif (preview_token.value if preview_token else "") == grammar.ASSIGN:
                name = self.expr().value
                self.eat_value(grammar.ASSIGN)
                named_args[name] = self.expr()
            else:
                args.append(self.expr())
            while self.current_token.token_type == TokenType.NEWLINE:
                self.eat_type(TokenType.NEWLINE)
            if self.eof:
                break
            if self.current_token.value != grammar.RPAREN:
                self.eat_value(grammar.COMMA)
        method = my_ast.MethodCall(
            obj=left.obj,
            name=left.field,
            arguments=args,
            line_num=self.line_num,
            named_arguments=named_args,
        )
        self.next_token()
        return method

    def field_assignment(
        self, token: Token, left: my_ast.DotAccess
    ) -> my_ast.Assign | my_ast.OpAssign:
        if token.value == grammar.ASSIGN:
            right = self.expr()
            node = my_ast.Assign(
                left=left, op=token.value, right=right, line_num=self.line_num
            )
        elif token.value in grammar.ARITHMETIC_ASSIGNMENT_OP:
            right = self.expr()
            node = my_ast.OpAssign(
                left=left, op=token.value, right=right, line_num=self.line_num
            )
        else:
            raise SyntaxError(f"Unknown assignment operator: {token.value}")
        return node

    def dictionary_assignment(self, _: Token) -> my_ast.Dict:
        raise NotImplementedError

    def return_statement(self) -> my_ast.Return:
        self.next_token()
        return my_ast.Return(value=self.expr(), line_num=self.line_num)

    def if_statement(self) -> my_ast.If:
        self.next_token()
        comps = [self.expr()]
        self.increment_indent_level()
        comp = my_ast.If(
            comps=comps,
            block=self.compound_statement(),
            indent_level=self.indent_level,
            line_num=self.line_num,
        )
        self.decriment_indent_level()
        return comp

    def else_if_statement(self) -> my_ast.ElseIf:
        self.next_token()
        comps = [self.expr()]
        self.increment_indent_level()
        comp = my_ast.ElseIf(
            comps=comps,
            block=self.compound_statement(),
            indent_level=self.indent_level,
            line_num=self.line_num,
        )
        self.decriment_indent_level()
        return comp

    def else_statement(self) -> my_ast.Else:
        self.next_token()
        self.increment_indent_level()
        comp = my_ast.Else(
            block=self.compound_statement(),
            indent_level=self.indent_level,
            line_num=self.line_num,
        )
        self.decriment_indent_level()
        return comp

    def while_statement(self) -> my_ast.While:
        token = self.next_token()
        comps = [self.expr()]
        self.increment_indent_level()
        comp = my_ast.While(
            op=token.value,
            comp=comps,
            block=self.loop_block(),
            line_num=self.line_num,
        )
        self.decriment_indent_level()
        return comp

    def for_statement(self) -> my_ast.For:
        self.next_token()
        elements = []
        while self.current_token.value != grammar.IN:
            elements.append(self.expr())
            if self.current_token.value == grammar.COMMA:
                self.eat_value(grammar.COMMA)
        self.eat_value(grammar.IN)
        iterator = self.expr()
        if self.current_token.value == grammar.NEWLINE:
            self.eat_type(TokenType.NEWLINE)
        self.increment_indent_level()
        block = self.loop_block()
        loop = my_ast.For(
            iterator=iterator, block=block, elements=elements, line_num=self.line_num
        )
        self.decriment_indent_level()
        return loop

    def loop_block(self) -> my_ast.LoopBlock:
        nodes = self.statement_list()
        root = my_ast.LoopBlock()
        for node in nodes:
            root.children.append(node)
        return root

    def assignment_statement(
        self, token: Token, var: my_ast.Expression | None = None
    ) -> my_ast.Assign | my_ast.OpAssign:
        if token.value == grammar.CONST:
            read_only = True
            self.next_token()
            token = self.current_token
            self.next_token()
        else:
            read_only = False
        if var is None:
            left = self.variable(token, read_only)
            token = self.next_token()
        else:
            if isinstance(var.value, my_ast.Self):
                left = var
            else:
                left = my_ast.Var(
                    value=var.value.value, type=var.type, line_num=var.line_num
                )
        if token.value == grammar.ASSIGN:
            right = self.expr()
            node = my_ast.Assign(
                left=left, op=token.value, right=right, line_num=self.line_num
            )
        elif token.value in grammar.ARITHMETIC_ASSIGNMENT_OP:
            right = self.expr()
            node = my_ast.OpAssign(
                left=left, op=token.value, right=right, line_num=self.line_num
            )
        else:
            raise SyntaxError(f"Unknown assignment operator: {token.value}")
        return node

    def variable(self, token: Token, read_only: bool = False) -> my_ast.Var:
        return my_ast.Var(
            value=token.value, line_num=self.line_num, read_only=read_only
        )

    def constant(self, token: Token) -> my_ast.Constant:
        return my_ast.Constant(value=token.value, line_num=self.line_num)

    def factor(self) -> my_ast.Expression:
        token = self.current_token
        preview_token = self.preview()
        preview_token_value = preview_token.value if preview_token else ""
        if preview_token_value == grammar.DOT:
            self.next_token()
            return self.dot_access(token)
        elif token.value in (grammar.PLUS, grammar.MINUS):
            self.next_token()
            return my_ast.UnaryOp(
                op=self.operator(token), expr=self.factor(), line_num=self.line_num
            )
        elif (
            token.value in self.user_types
            and preview_token_value == grammar.LCURLYBRACKET
        ):
            return self.struct_creation(token)
        elif token.value in grammar.COMPARISON_OP:
            self.next_token()
            return my_ast.BinOp(
                left=self.factor(),
                op=self.operator(token),
                right=self.expr(),
                line_num=self.line_num,
            )
        elif token.value == grammar.NOT:
            token = self.next_token()
            return my_ast.UnaryOp(
                op=self.operator(token), expr=self.factor(), line_num=self.line_num
            )
        elif token.token_type == TokenType.NUMBER:
            self.next_token()
            return my_ast.Num(
                value=token.value, val_type=token.value_type, line_num=self.line_num
            )
        elif token.token_type == TokenType.STRING:
            self.next_token()
            return my_ast.Str(value=token.value, line_num=self.line_num)
        elif token.value == grammar.FUNC_DEFINITION:
            return self.function_declaration()
        elif token.token_type == TokenType.TYPE:
            return self.type_spec()
        elif token.value == grammar.LPAREN:
            if preview_token_value == grammar.RPAREN:
                return my_ast.Collection(
                    type=grammar.TUPLE,
                    line_num=self.line_num,
                    read_only=False,
                    items=[],
                )
            else:
                self.next_token()
                node = self.expr()
                if self.current_token.token_type == TokenType.NEWLINE:
                    self.next_token()
                if (
                    isinstance(node, my_ast.DotAccess)
                    and self.current_token.value == grammar.LPAREN
                ):
                    node = self.method_call(self.current_token, node)
                self.eat_value(grammar.RPAREN)
                return node
        elif preview_token_value == grammar.LPAREN:
            self.next_token()
            return self.function_call(token)
        elif (
            preview_token_value == grammar.LSQUAREBRACKET
            or token.value == grammar.LSQUAREBRACKET
        ):
            self.next_token()
            return self.square_bracket_expression(token)
        elif token.value == grammar.LCURLYBRACKET:
            self.next_token()
            return self.curly_bracket_expression(token)
        elif token.token_type == TokenType.NAME:
            self.next_token()
            return self.variable(token)
        elif token.token_type == TokenType.CONSTANT:
            self.next_token()
            return self.constant(token)
        elif token.token_type == TokenType.NEWLINE:
            self.next_token()
            return self.factor()
        elif token.token_type == TokenType.EOF:
            self.eof = True
            return
        else:
            raise SyntaxError

    def term(self) -> my_ast.Expression:
        node = self.factor()
        if self.eof:
            return
        while self.current_token.value in grammar.TERM_OPS:
            token = self.next_token()
            if token.value in grammar.LOGICAL_OP or token.value in grammar.BINARY_OP:
                node = my_ast.BinOp(
                    left=node,
                    op=self.operator(token),
                    right=self.expr(),
                    line_num=self.line_num,
                )
            elif token.value == grammar.RANGE:
                node = my_ast.Range(
                    left=node, right=self.expr(), line_num=self.line_num
                )
            else:
                node = my_ast.BinOp(
                    left=node,
                    op=self.operator(token),
                    right=self.factor(),
                    line_num=self.line_num,
                )
        return node

    def expr(self) -> my_ast.Expression:
        node = self.term()
        if self.eof:
            return
        while self.current_token.value in (grammar.PLUS, grammar.MINUS):
            token = self.next_token()
            node = my_ast.BinOp(
                left=node,
                op=self.operator(token),
                right=self.term(),
                line_num=self.line_num,
            )
        return node

    def operator(self, token: Token) -> my_ast.Operator:
        return my_ast.Operator(value=token.value, line_num=token.line_num)

    def parse(self) -> my_ast.Program:
        node = self.program()
        if self.current_token.token_type != TokenType.EOF:
            raise SyntaxError("Unexpected end of program")
        return node


if __name__ == "__main__":
    from prettyprinter import install_extras
    from lexer import Lexer

    install_extras(include=["dataclasses"])

    file = "test.my"
    with open(file) as my_file:
        l = Lexer(my_file.read(), file)
        parser = Parser(l)
        tree = parser.parse()
        pprint(tree)
