import warnings
from my_visitor import NodeVisitor
from my_symbol_table import VarSymbol
from my_symbol_table import FuncSymbol
from my_symbol_table import SymbolTable
from my_ast import VarDecl, ControlStructure
from my_ast import Return
from my_grammar import *

def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
	return 'Warning: {}\n'.format(message)

warnings.formatwarning = warning_on_one_line


class SymbolTableBuilder(NodeVisitor):
	def __init__(self):
		self.symtab = SymbolTable()

	def build(self, node):
		self.visit(node)
		warnings.warn('Unused variables ({})'.format(','.join(sym_name for sym_name in self.symtab.unvisited_symbols)))

	def visit_program(self, node):
		self.visit(node.block)

	def visit_block(self, node):
		for declaration in node.declarations:
			self.visit(declaration)
		self.visit(node.compound_statement)

	def visit_binop(self, node):
		if node.op.value == CAST:
			self.symtab.lookup(node.left.value).accessed = True
			return self.symtab.infer_type(node.right)
		else:
			left = self.visit(node.left)
			right = self.visit(node.right)
			left_type = self.symtab.infer_type(left)
			right_type = self.symtab.infer_type(right)
			any_type = self.symtab.lookup(ANY)
			if right_type is left_type or left_type is any_type or right_type is any_type:
				return left_type
			else:
				raise TypeError

	def visit_controlstructure(self, node):
		self.visit(node.comp)

	def visit_constant(self, node):
		if node.value == TRUE or node.value == FALSE:
			return self.symtab.lookup(BOOL)
		elif node.value == NAN or node.value == INF or node.value == NEGATIVE_INF:
			return self.symtab.lookup(DEC)
		else:
			return NotImplementedError

	def visit_num(self, node):
		return self.symtab.infer_type(node.value)

	def visit_str(self, node):
		return self.symtab.infer_type(node.value)

	@staticmethod
	def visit_type(node):
		return node.value

	def visit_assign(self, node):
		if isinstance(node.left, VarDecl):
			var_name = node.left.var_node.value
			value = self.symtab.infer_type(node.left.type_node)
		else:
			var_name = node.left.value
			value = self.visit(node.right)
		lookup_var = self.symtab.lookup(var_name)
		if not lookup_var:
			var_sym = VarSymbol(var_name, value)
			var_sym.val_assigned = True
			self.symtab.define(var_sym)
		else:
			if (value.type and lookup_var.type is not value.type) or lookup_var.type is not value:
				raise TypeError

	def visit_opassign(self, node):
		left = self.visit(node.left)
		right = self.visit(node.right)
		left_type = self.symtab.infer_type(left)
		right_type = self.symtab.infer_type(right)
		any_type = self.symtab.lookup(ANY)
		if right_type is left_type or left_type is any_type or right_type is any_type:
			return left_type
		else:
			raise TypeError

	def visit_var(self, node):
		var_name = node.value
		val = self.symtab.lookup(var_name)
		if val is None:
			raise NameError(repr(var_name))
		else:
			if not val.val_assigned:
				raise SyntaxError('{} is being accessed while not yet defined'.format(var_name))
			val.accessed = True
			return val

	def visit_unaryop(self, node):
		self.visit(node.expr)

	def visit_compound(self, node):
		for child in node.children:
			self.visit(child)

	def visit_funcdecl(self, node):
		func_name = node.name.value
		return_type = node.return_type.value
		func_type = self.symtab.lookup(return_type)
		stb = SymbolTableBuilder()
		for k, v in node.parameters.items():
			var_sym = VarSymbol(k, stb.symtab.lookup(v.value))
			var_sym.val_assigned = True
			stb.symtab.define(var_sym)
		func_symbol = FuncSymbol(func_name, func_type, node.parameters, node.body, stb)
		for child in func_symbol.body.children:
			if isinstance(child, Return):
				if child.value.token.type == NUMBER:
					return_var_type = self.symtab.infer_type(child.value.value)
				else:
					return_var_type = func_symbol.symtab_builder.symtab.lookup(child.value.value).type
				if return_var_type is not func_symbol.type:
					raise TypeError('The actual return type does not match the declared return type')
			elif isinstance(child, ControlStructure):
				res = stb.visit(child)
				print(res) #TODO: this is not inspecting code recursivly, ignores inner blocks. NOT GOOD!
		self.symtab.define(func_symbol)

	def visit_funccall(self, node):
		func_name = node.name.value
		func = self.symtab.lookup(func_name)
		if func is None:
			raise NameError(repr(func_name))
		else:
			func.accessed = True
			return func

	@staticmethod
	def visit_return(node):
		return

	def visit_noop(self, node):
		pass

	def visit_vardecl(self, node):
		type_name = node.type_node.value
		type_symbol = self.symtab.lookup(type_name)
		var_name = node.var_node.value
		var_symbol = VarSymbol(var_name, type_symbol)
		self.symtab.define(var_symbol)