from decimal import Decimal

class Token(object):
	def __init__(self, token_type, value, line_num):
		self.type = token_type
		self.value = value
		self.cast()
		self.line_num = line_num

	def cast(self):
		if self.type == 'NUMBER':
			try:
				self.value = int(self.value)
			except ValueError:
				try:
					self.value = Decimal(self.value)
				except ValueError:
					pass

	def __str__(self):
		return 'Token(type={type}, value={value}, line_num={line_num})'.format(
			type=self.type,
			value=repr(self.value),
			line_num=self.line_num
		)

	__repr__ = __str__