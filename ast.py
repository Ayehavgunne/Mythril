class AST(object):
	def __init__(self):
		self.left = None
		self.token = self.op = None
		self.right = None
		self.value = None

	def __str__(self):
		out = [self.token.type, self.left, self.right, self.value]
		out = map(str, filter(None, out))
		return "(" + " ".join(out) + ")"

	def __repr__(self):
		return self.__str__()


class BinOp(AST):
	def __init__(self, left, op, right):
		self.left = left
		self.token = self.op = op
		self.right = right


class Num(AST):
	def __init__(self, token):
		self.token = token
		self.value = token.value


class Str(AST):
	def __init__(self, token):
		self.token = token
		self.value = token.value