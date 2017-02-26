from llvmlite import ir
from my_grammar import *

#TODO: temorarily making Decimal a DoubleType till find (or make) a better representation
type_map = {INT: ir.IntType, DEC: ir.DoubleType, FLOAT: ir.FloatType}

class CodegenError(BaseException): pass

class LLVMCodeGenerator(object):
	def __init__(self):
		self.module = ir.Module()
		self.builder = None
		self.func_symtab = {}

	def generate_code(self, node):
		return self.codegen(node)

	def codegen(self, node):
		method = 'codegen_' + node.__class__.__name__.lower()
		return getattr(self, method)(node)

	@staticmethod
	def codegen_num(node):
		return ir.Constant(type_map[node.type](), node.value)

	def codegen_binop(self, node):
		left = self.codegen(node.left)
		right = self.codegen(node.right)

		if node.op == '+':
			return self.builder.fadd(left, right, 'addtmp')
		elif node.op == '-':
			return self.builder.fsub(left, right, 'subtmp')
		elif node.op == '*':
			return self.builder.fmul(left, right, 'multmp')
		elif node.op == '<':
			cmp = self.builder.fcmp_unordered('<', left, right, 'cmptmp')
			return self.builder.uitofp(cmp, ir.DoubleType(), 'booltmp')
		else:
			raise CodegenError('Unknown binary operator', node.op)