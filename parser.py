from ast import *

class Parser(object):
	def __init__(self, lexer):
		self.lexer = lexer
		self.current_token = self.lexer.get_next_token()
		self.indent_level = 0

	def eat_type(self, token_type):
		if self.current_token.type == token_type:
			self.current_token = self.lexer.get_next_token()
		else:
			raise SyntaxError

	def eat_value(self, token_value):
		if self.current_token.value == token_value:
			self.current_token = self.lexer.get_next_token()
		else:
			raise SyntaxError

	def next_token(self):
		self.current_token = self.lexer.get_next_token()

	def program(self):
		root = Compound()
		# program_node = Program(self.compound_statement(0))
		while self.current_token.type != EOF:
			comp = self.compound_statement(0)
			root.children.extend(comp.children)
		return Program(root)

	def variable_declaration(self):
		type_node = self.type_spec()
		var_node = Var(self.current_token)
		self.eat_type('NAME')
		return VarDecl(var_node, type_node)

	def type_spec(self):
		token = self.current_token
		if self.current_token.type == TYPE:
			self.eat_type(TYPE)
		node = Type(token)
		return node

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
			self.eat_type(NEWLINE)
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
		elif self.current_token.type == NAME:
			node = self.assignment_statement()
		elif self.current_token.type == TYPE:
			node = self.variable_declaration()
		else:
			node = self.empty()
		return node

	def comparison_statement(self, indent_level):
		token = self.current_token
		self.next_token()
		comp = self.expr()
		return Comparison(token, comp, self.compound_statement(indent_level))

	def assignment_statement(self):
		left = self.variable()
		token = self.current_token
		if token.value == ASSIGN:
			self.eat_value(ASSIGN)
			right = self.expr()
			node = Assign(left, token, right)
		elif token.value in (PLUS_ASSIGN, MINUS_ASSIGN, MUL_ASSIGN, DIV_ASSIGN, FLOORDIV_ASSIGN, MOD_ASSIGN, POWER_ASSIGN):
			self.next_token()
			right = self.expr()
			node = OpAssign(left, token, right)
		else:
			raise SyntaxError('Unknown assignment operator: {}'.format(token.value))
		return node

	def variable(self):
		node = Var(self.current_token)
		self.eat_type(NAME)
		return node

	@staticmethod
	def empty():
		return NoOp()

	def factor(self):
		token = self.current_token
		if token.value == PLUS:
			self.eat_value(PLUS)
			node = UnaryOp(token, self.factor())
			return node
		elif token.value == MINUS:
			self.eat_value(MINUS)
			node = UnaryOp(token, self.factor())
			return node
		elif token.type == NUMBER:
			self.eat_type(NUMBER)
			return Num(token)
		elif token.type == TYPE:
			self.eat_type(TYPE)
			return Type(token)
		elif token.value == LPAREN:
			self.eat_value(LPAREN)
			node = self.expr()
			self.eat_value(RPAREN)
			return node
		else:
			node = self.variable()
			return node

	def term(self):
		node = self.factor()
		while self.current_token.value in (MUL, DIV, FLOORDIV, MOD, POWER, CAST) or self.current_token.value in COMP_OP:
			token = self.current_token
			self.next_token()
			if token.value in COMP_OP:
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
			raise SyntaxError

		return node

if __name__ == '__main__':
	from lexer import Lexer
	l = Lexer(open('math.my').read())
	parser = Parser(l)
	tree = parser.parse()
	print(tree)