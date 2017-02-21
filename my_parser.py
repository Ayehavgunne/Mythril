from collections import OrderedDict
from my_ast import *
from my_grammar import *

class Parser(object):
	def __init__(self, lexer):
		self.lexer = lexer
		self.current_token = None
		self.indent_level = 0
		self.next_token()

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

	def next_token(self):
		self.current_token = self.lexer.get_next_token()

	def preview(self, num=1):
		return self.lexer.preview_token(num)

	def program(self):
		root = Compound()
		while self.current_token.type != EOF:
			comp = self.compound_statement(0)
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
		return_type = self.type_spec()
		name = self.current_token
		self.next_token()
		self.eat_value(LPAREN)
		params = OrderedDict()
		while self.current_token.value != RPAREN:
			param_type = self.current_token
			self.eat_type(TOKEN_TYPE)
			params[self.current_token.value] = param_type
			self.eat_type(NAME)
			if self.current_token.value != RPAREN:
				self.eat_value(COMMA)
		self.eat_value(RPAREN)
		self.eat_type(NEWLINE)
		self.eat_type(INDENT)
		self.indent_level += 1
		stmts = self.compound_statement(self.indent_level)
		return FuncDecl(name, return_type, params, stmts)

	def function_call(self, token):
		self.eat_value(LPAREN)
		args = []
		while self.current_token.value != RPAREN:
			while self.current_token.type == NEWLINE:
				self.eat_type(NEWLINE)
			args.append(self.current_token)
			self.eat_type(NAME, NUMBER, STRING, TOKEN_TYPE, CONSTANT)
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
		return Type(token)

	def compound_statement(self, indent_level):
		nodes = self.statement_list(indent_level)
		root = Compound()
		for node in nodes:
			root.children.append(node)
		return root

	def statement_list(self, indent_level):
		node = self.statement()
		results = [node]
		while self.current_token.type == NEWLINE:
			indents = 0
			self.next_token()
			while self.current_token.type == INDENT:
				self.next_token()
				indents += 1
			if indents < indent_level:
				self.indent_level -= 1
				return results
			results.append(self.statement())
		return results

	def statement(self):
		if self.current_token.value in (IF, WHILE):
			self.indent_level += 1
			node = self.comparison_statement(self.indent_level)
		elif self.current_token.value == RETURN:
			node = self.return_statement()
		elif self.current_token.type == NAME:
			node = self.name_statement()
		elif self.current_token.type == TOKEN_TYPE:
			if self.preview(2).value[0] == LPAREN:
				node = self.function_declaration()
			else:
				node = self.variable_declaration()
		else:
			node = self.empty()
		return node

	def square_bracket_expression(self, token):
		if self.current_token.type == TOKEN_TYPE:
			type_token = self.current_token
			self.next_token()
			if self.current_token.value == COMMA:
				return self.dictionary_assignment(token)
			elif self.current_token.value == RSQUAREBRACKET:
				self.next_token()
				return self.collection_expression(token, type_token)
		elif self.current_token.type == NAME:
			raise NotImplementedError

	def collection_expression(self, token, type_token):
		if self.current_token.value == ASSIGN:
			return self.array_of_type_assignment(token, type_token)
		else:
			return self.collection_call()

	def collection_call(self):
		raise NotImplementedError

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
		token = self.expr()
		if isinstance(token, AST):
			ret = Return(token)
		elif token.type == NAME:
			ret = Return(self.variable(token))
		elif token.type == NUMBER:
			ret = Return(Num(token))
		elif token.type == STRING:
			ret = Return(Str(token))
		else:
			raise SyntaxError
		return ret

	def comparison_statement(self, indent_level):
		token = self.current_token
		self.next_token()
		comp = ControlStructure(token, self.expr(), self.compound_statement(indent_level))
		if self.current_token.value == ELSE:
			self.next_token()
			comp.alt_block = self.compound_statement(indent_level)
		return comp

	def assignment_statement(self, token):
		left = self.variable(token)
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
	def variable(token):
		return Var(token)

	@staticmethod
	def constant(token):
		return Constant(token)

	@staticmethod
	def empty():
		return NoOp()

	def factor(self):
		token = self.current_token
		preview = self.preview()
		if token.value == PLUS:
			self.next_token()
			node = UnaryOp(token, self.factor())
			return node
		elif token.value == MINUS:
			self.next_token()
			node = UnaryOp(token, self.factor())
			return node
		elif token.type == NUMBER:
			self.next_token()
			return Num(token)
		elif token.type == STRING:
			self.next_token()
			return Str(token)
		elif token.type == TOKEN_TYPE:
			return self.type_spec()
		elif token.value == LPAREN:
			self.next_token()
			node = self.expr()
			self.eat_value(RPAREN)
			return node
		elif preview and preview.value and preview.value[0] == LPAREN:
			self.next_token()
			node = self.function_call(token)
			return node
		elif token.type == NAME:
			self.next_token()
			node = self.variable(token)
			return node
		elif token.type == CONSTANT:
			self.next_token()
			return self.constant(token)
		else:
			raise SyntaxError

	def term(self):
		node = self.factor()
		while self.current_token.value in (MUL, DIV, FLOORDIV, MOD, POWER, CAST) or self.current_token.value in COMPARISON_OP:
			token = self.current_token
			self.next_token()
			if token.value in COMPARISON_OP:
				node = BinOp(left=node, op=token, right=self.expr())
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