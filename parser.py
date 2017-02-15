from ast import *

INTEGER, PLUS, MINUS, MUL, DIV, LPAREN, RPAREN, EOF = (
    'NUMBER', '+', '-', '*', '/', '(', ')', 'END'
)

class Parser(object):
	def __init__(self, lex):
		self.lexer = lex
		self.current_token = self.lexer.get_next_token()

	def eat(self, token_type=None, token_value=None):
		if token_type and self.current_token.type == token_type:
			self.current_token = self.lexer.get_next_token()
		elif token_value and self.current_token.value == token_value:
			self.current_token = self.lexer.get_next_token()
		else:
			raise SyntaxError

	def factor(self):
		token = self.current_token
		if token.type == INTEGER:
			self.eat(INTEGER)
			return Num(token)
		elif token.value == LPAREN:
			self.eat(token_value=LPAREN)
			node = self.expr()
			self.eat(token_value=RPAREN)
			return node

	def term(self):
		node = self.factor()

		while self.current_token.type in (MUL, DIV):
			token = self.current_token
			if token.type == MUL:
				self.eat(token_value=MUL)
			elif token.type == DIV:
				self.eat(token_value=DIV)

			node = BinOp(left=node, op=token, right=self.factor())

		return node

	def expr(self):
		node = self.term()

		while self.current_token.type == 'OP':
			token = self.current_token
			if token.value == PLUS:
				self.eat(token_value=PLUS)
			elif token.type == MINUS:
				self.eat(token_value=MINUS)

			node = BinOp(left=node, op=token, right=self.term())

		return node

	def parse(self):
		return self.expr()

if __name__ == '__main__':
	from lexer import Lexer
	lexer = Lexer(open('math.my').read())
	parser = Parser(lexer)
	tree = parser.parse()
	print(tree)