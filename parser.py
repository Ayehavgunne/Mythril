from tokenizer import tokenize


class AST(object):
	pass


class BinOp(AST):
	def __init__(self, left, op, right, precedence):
		pass


class Parser(object):
	def __init__(self, string):
		self.lexer = tokenize(string)
		self.current_token = next(self.lexer)

	def parse(self):
		pass
