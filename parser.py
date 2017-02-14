from lexer import analyze


class Parser(object):
	def __init__(self, string):
		self.lexer = analyze(string)
		self.current_token = None

	def expression(self, rbp=0):
		t = self.current_token
		self.next()
		left = t.nud(self)
		while rbp < self.current_token.lbp:
			t = self.current_token
			self.next()
			left = t.led(left, self)
		return left

	def next(self):
		self.current_token = next(self.lexer)

	def advance(self, value=None):
		if value and self.current_token.value != value:
			raise SyntaxError('Expected "{}"'.format(value))
		self.next()

	def parse(self):
		self.next()
		return self.expression()


if __name__ == '__main__':
	p = Parser(open('math.dm').read())
	tree = p.parse()
	print(tree)
