from collections import OrderedDict
from my_ast import *
from my_grammar import *


class Parser(object):
	def __init__(self, lexer):
		self.lexer = lexer
		self.current_token = None
		self.indent_level = 0
		self.next_token()

	def next_token(self):
		self.current_token = self.lexer.get_next_token()
		# print(self.current_token)

	def eat_type(self, *token_type):
		if self.current_token.type in token_type:
			self.next_token()
		else:
			raise SyntaxError

	def eat_value(self, *token_value):
		if self.current_token.value in token_value:
			self.next_token()
		else:
			raise SyntaxError

	def preview(self, num=1):
		return self.lexer.preview_token(num)

	def program(self):
		root = Compound()
		while self.current_token.type != EOF:
			comp = self.compound_statement()
			root.children.extend(comp.children)
		return Program(root)

	def variable_declaration(self):
		type_node = self.type_spec()
		var_node = Var(self.current_token)
		self.eat_type(NAME)
		ret = VarDecl(var_node, type_node)
		if self.current_token.value == ASSIGN:
			ret = self.variable_declaration_assignment(ret)
		return ret

	def variable_declaration_assignment(self, declaration):
		token = self.current_token
		self.next_token()
		return Assign(declaration, token, self.expr())

	def function_declaration(self):
		if self.current_token.value == VOID:
			return_type = Void()
			self.next_token()
		else:
			return_type = self.type_spec()
		if self.current_token.value == LPAREN:
			name = ANON
		else:
			name = self.current_token
			self.next_token()
		self.eat_value(LPAREN)
		params = OrderedDict()
		while self.current_token.value != RPAREN:
			param_type = self.type_spec()
			params[self.current_token.value] = param_type
			self.eat_type(NAME)
			if self.current_token.value != RPAREN:
				self.eat_value(COMMA)
		self.eat_value(RPAREN)
		self.eat_type(NEWLINE)
		self.indent_level += 1
		stmts = self.compound_statement()
		self.indent_level -= 1
		if name == ANON:
			return AnonymousFunc(return_type, params, stmts)
		else:
			return FuncDecl(name, return_type, params, stmts)

	def bracket_literal(self):
		token = self.current_token
		self.next_token()
		if token.value == LCURLYBRACKET:
			return self.curly_bracket_expression(token)
		elif token.value == LPAREN:
			return self.tuple_expression(token)
		else:
			return self.square_bracket_expression(token)

	def function_call(self, token):
		self.eat_value(LPAREN)
		args = []
		while self.current_token.value != RPAREN:
			while self.current_token.type == NEWLINE:
				self.eat_type(NEWLINE)
			if self.current_token.value in (LPAREN, LSQUAREBRACKET, LCURLYBRACKET):
				args.append(self.bracket_literal())
			else:
				args.append(self.expr())
			while self.current_token.type == NEWLINE:
				self.eat_type(NEWLINE)
			if self.current_token.value != RPAREN:
				self.eat_value(COMMA)
		func = FuncCall(token, args)
		self.next_token()
		return func

	def type_spec(self):
		token = self.current_token
		self.eat_type(TOKEN_TYPE)
		type_spec = Type(token)
		if self.current_token.value == LPAREN and token.value == FUNC:
			self.next_token()
			func_ret_type = self.type_spec()
			type_spec.func_ret_type = func_ret_type
			self.eat_value(RPAREN)
		return type_spec

	def compound_statement(self):
		nodes = self.statement_list()
		root = Compound()
		for node in nodes:
			root.children.append(node)
		return root

	def statement_list(self):
		node = self.statement()
		if self.current_token.type == NEWLINE:
			self.next_token()
		if isinstance(node, Return):
			return [node]
		results = [node]
		while self.current_token.indent_level == self.indent_level:
			results.append(self.statement())
			if self.current_token.type == NEWLINE:
				self.next_token()
			elif self.current_token.type == EOF:
				break
		return results

	def statement(self):
		if self.current_token.value == IF:
			node = self.if_statement()
		elif self.current_token.value == WHILE:
			node = self.while_statement()
		elif self.current_token.value == FOR:
			node = self.for_statement()
		elif self.current_token.value == BREAK:
			self.next_token()
			node = Break()
		elif self.current_token.value == CONTINUE:
			self.next_token()
			node = Continue()
		elif self.current_token.value == PASS:
			self.next_token()
			node = Pass()
		elif self.current_token.value == CONST:
			node = self.assignment_statement(self.current_token)
		elif self.current_token.value == SWITCH:
			self.next_token()
			node = self.switch_statement()
		elif self.current_token.value == RETURN:
			node = self.return_statement()
		elif self.current_token.type == NAME:
			node = self.name_statement()
		elif self.current_token.type == TOKEN_TYPE or self.current_token.value == VOID:
			if self.preview(2).value[0] == LPAREN:
				node = self.function_declaration()
			else:
				node = self.variable_declaration()
		else:
			node = self.empty()
		return node

	def square_bracket_expression(self, token):
		if token.value == LSQUAREBRACKET:
			items = []
			while self.current_token.value != RSQUAREBRACKET:
				items.append(self.expr())
				if self.current_token.value == COMMA:
					self.next_token()
				else:
					break
			self.eat_value(RSQUAREBRACKET)
			return Collection(token, False, *items)
		elif self.current_token.type == TOKEN_TYPE:
			type_token = self.current_token
			self.next_token()
			if self.current_token.value == COMMA:
				return self.dictionary_assignment(token)
			elif self.current_token.value == RSQUAREBRACKET:
				self.next_token()
				return self.collection_expression(token, type_token)
		elif token.type == NAME:
			self.eat_value(LSQUAREBRACKET)
			tok = self.expr()
			# self.next_token()
			if self.current_token.value == COMMA:
				return self.slice_expression(tok)
			else:
				self.eat_value(RSQUAREBRACKET)
				return self.access_collection(token, tok)
		else:
			raise SyntaxError

	def slice_expression(self, token):
		pass

	def curly_bracket_expression(self, token):
		if token.value == LCURLYBRACKET:
			pairs = {}
			while self.current_token.value != RCURLYBRACKET:
				key = self.expr()
				self.eat_value(COLON)
				pairs[key.value] = self.expr()
				if self.current_token.value == COMMA:
					self.next_token()
				else:
					break
			self.eat_value(RCURLYBRACKET)
			return HashMap(token, pairs)

	def tuple_expression(self, token):
		if token.value == LPAREN:
			items = []
			while self.current_token.value != RPAREN:
				items.append(self.expr())
				if self.current_token.value == COMMA:
					self.next_token()
				else:
					break
			self.eat_value(RPAREN)
			return Collection(token, True, *items)

	def collection_expression(self, token, type_token):
		if self.current_token.value == ASSIGN:
			return self.array_of_type_assignment(token, type_token)
		else:
			raise NotImplementedError

	@staticmethod
	def access_collection(collection, key):
		return CollectionAccess(collection, key)

	def array_of_type_assignment(self, token, type_token):
		raise NotImplementedError

	def name_statement(self):
		token = self.current_token
		self.next_token()
		if self.current_token.value == LPAREN:
			node = self.function_call(token)
		elif self.current_token.value == LSQUAREBRACKET:
			self.next_token()
			node = self.square_bracket_expression(token)
		elif self.current_token.value in (ASSIGN, PLUS_ASSIGN, MINUS_ASSIGN, MUL_ASSIGN, DIV_ASSIGN, FLOORDIV_ASSIGN, MOD_ASSIGN, POWER_ASSIGN):
			node = self.assignment_statement(token)
		else:
			raise SyntaxError
		return node

	def dictionary_assignment(self, token):
		raise NotImplementedError

	def return_statement(self):
		self.next_token()
		return Return(self.expr())

	def if_statement(self):
		self.indent_level += 1
		token = self.current_token
		self.next_token()
		comp = If(token, [self.expr()], [self.compound_statement()])
		if self.current_token.indent_level < comp.op.indent_level:
			self.indent_level -= 1
			return comp
		while self.current_token.value == ELSE_IF:
			self.next_token()
			comp.comps.append(self.expr())
			comp.blocks.append(self.compound_statement())
		if self.current_token.value == ELSE:
			self.next_token()
			comp.comps.append(Else())
			comp.blocks.append(self.compound_statement())
		self.indent_level -= 1
		return comp

	def while_statement(self):
		self.indent_level += 1
		token = self.current_token
		self.next_token()
		comp = While(token, self.expr(), self.loop_block())
		self.indent_level -= 1
		return comp

	def for_statement(self):
		self.indent_level += 1
		self.next_token()
		elements = []
		while self.current_token.value != IN:
			elements.append(self.expr())
			if self.current_token.value == COMMA:
				self.eat_value(COMMA)
		self.eat_value(IN)
		iterator = self.expr()
		self.eat_type(NEWLINE)
		block = self.loop_block()
		loop = For(iterator, block, elements)
		self.indent_level -= 1
		return loop

	def switch_statement(self):
		self.indent_level += 1
		value = self.expr()
		switch = Switch(value, [])
		if self.current_token.type == NEWLINE:
			self.next_token()
		while self.current_token.indent_level == self.indent_level:
			switch.cases.append(self.case_statement())
			if self.current_token.type == NEWLINE:
				self.next_token()
			elif self.current_token.type == EOF:
				return
		self.indent_level -= 1
		return switch

	def case_statement(self):
		self.indent_level += 1
		if self.current_token.value == CASE:
			self.next_token()
			value = self.expr()
		elif self.current_token.value == DEFAULT:
			self.next_token()
			value = DEFAULT
		else:
			raise SyntaxError
		block = self.compound_statement()
		self.indent_level -= 1
		return Case(value, block)

	def loop_block(self):
		nodes = self.statement_list()
		root = LoopBlock()
		for node in nodes:
			root.children.append(node)
		return root

	def assignment_statement(self, token):
		if token.value == CONST:
			read_only = True
			self.next_token()
			token = self.current_token
			self.next_token()
		else:
			read_only = False
		left = self.variable(token, read_only)
		token = self.current_token
		if token.value == ASSIGN:
			self.next_token()
			right = self.expr()
			node = Assign(left, token, right)
		elif token.value in (PLUS_ASSIGN, MINUS_ASSIGN, MUL_ASSIGN, DIV_ASSIGN, FLOORDIV_ASSIGN, MOD_ASSIGN, POWER_ASSIGN):
			self.next_token()
			right = self.expr()
			node = OpAssign(left, token, right)
		else:
			raise SyntaxError('Unknown assignment operator: {}'.format(token.value))
		return node

	@staticmethod
	def variable(token, read_only=False):
		return Var(token, read_only)

	@staticmethod
	def constant(token):
		return Constant(token)

	@staticmethod
	def empty():
		return NoOp()

	def factor(self):
		token = self.current_token
		preview = self.preview()
		if token.value == PLUS:  # TODO: PLUS, MINUS and NOT can be combined
			self.next_token()
			return UnaryOp(token, self.factor())
		elif token.value == MINUS:
			self.next_token()
			return UnaryOp(token, self.factor())
		elif token.value == NOT:
			self.next_token()
			return UnaryOp(token, self.expr())
		elif token.type == NUMBER:
			self.next_token()
			return Num(token)
		elif token.type == STRING:
			self.next_token()
			return Str(token)
		elif token.type == TOKEN_TYPE:
			if preview.value == LPAREN:
				return self.function_declaration()
			return self.type_spec()
		elif token.value == LPAREN:
			self.next_token()
			node = self.expr()
			self.eat_value(RPAREN)
			return node
		elif preview.value == LPAREN:
			self.next_token()
			return self.function_call(token)
		elif preview.value == LSQUAREBRACKET:
			self.next_token()
			return self.square_bracket_expression(token)
		elif token.value == LSQUAREBRACKET:
			self.next_token()
			return self.square_bracket_expression(token)
		elif token.value == LCURLYBRACKET:
			self.next_token()
			return self.curly_bracket_expression(token)
		elif token.type == NAME:
			self.next_token()
			return self.variable(token)
		elif token.type == CONSTANT:
			self.next_token()
			return self.constant(token)
		else:
			raise SyntaxError

	def term(self):
		node = self.factor()
		ops = (MUL, DIV, FLOORDIV, MOD, POWER, CAST, RANGE) + COMPARISON_OP + LOGICAL_OP
		while self.current_token.value in ops:
			token = self.current_token
			self.next_token()
			if token.value in COMPARISON_OP or token.value in LOGICAL_OP:
				node = BinOp(left=node, op=token, right=self.expr())
			elif token.value == RANGE:
				node = Range(left=node, op=token, right=self.expr())
			else:
				node = BinOp(left=node, op=token, right=self.factor())
		return node

	def expr(self):
		node = self.term()
		while self.current_token.value in (PLUS, MINUS):
			token = self.current_token
			self.next_token()
			node = BinOp(left=node, op=token, right=self.term())
		return node

	def parse(self):
		node = self.program()
		if self.current_token.type != EOF:
			raise SyntaxError('Unexpected end of program')
		return node

if __name__ == '__main__':
	from my_lexer import Lexer
	l = Lexer(open('math.my').read())
	parser = Parser(l)
	tree = parser.parse()
	print(tree)