from ast import *

class Parser(object):
	def __init__(self, lex):
		self.lexer = lex
		self.current_token = self.lexer.get_next_token()

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

	def program(self):
		program_node = Program(self.compound_statement())
		return program_node

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

	def compound_statement(self):
		nodes = self.statement_list()
		root = Compound()
		for node in nodes:
			root.children.append(node)
		return root

	def statement_list(self):
		node = self.statement()
		results = [node]
		while self.current_token.type == NEWLINE:
			self.eat_type(NEWLINE)
			results.append(self.statement())
		return results

	def statement(self):
		if self.current_token.type == BEGIN:
			node = self.compound_statement()
		elif self.current_token.type == NAME:
			node = self.assignment_statement()
		elif self.current_token.type == TYPE:
			node = self.variable_declaration()
		else:
			node = self.empty()
		return node

	def assignment_statement(self):
		left = self.variable()
		token = self.current_token
		self.eat_value(ASSIGN)
		right = self.expr()
		node = Assign(left, token, right)
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
		while self.current_token.value in (MUL, DIV, FLOORDIV, CAST):
			token = self.current_token
			if token.value == MUL:
				self.eat_value(MUL)
			elif token.value == DIV:
				self.eat_value(DIV)
			elif token.value == FLOORDIV:
				self.eat_value(FLOORDIV)
			elif token.value == CAST:
				self.eat_value(CAST)
			node = BinOp(left=node, op=token, right=self.factor())
		return node

	def expr(self):
		node = self.term()
		while self.current_token.value in (PLUS, MINUS):
			token = self.current_token
			if token.value == PLUS:
				self.eat_value(PLUS)
			elif token.value == MINUS:
				self.eat_value(MINUS)
			node = BinOp(left=node, op=token, right=self.term())
		return node

	def parse(self):
		node = self.program()
		if self.current_token.type != EOF:
			raise SyntaxError

		return node

if __name__ == '__main__':
	from lexer import Lexer
	lexer = Lexer(open('math.my').read())
	parser = Parser(lexer)
	tree = parser.parse()
	print(tree)