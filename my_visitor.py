class NodeVisitor(object):
	def visit(self, node):
		method_name = 'visit_' + type(node).__name__.lower()
		visitor = getattr(self, method_name, self.generic_visit)
		return visitor(node)

	@staticmethod
	def generic_visit(node):
		raise Exception('No visit_{} method'.format(type(node).__name__.lower()))