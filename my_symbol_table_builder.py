import warnings
from my_visitor import NodeVisitor
from my_visitor import VarSymbol
from my_visitor import NULLTYPE_BUILTIN
from my_visitor import CollectionSymbol
from my_visitor import FuncSymbol
from my_visitor import TypeSymbol
from my_ast import VarDecl
from my_ast import Var
from my_ast import Collection
from my_grammar import *


def flatten(container):
	for i in container:
		if isinstance(i, (list, tuple)):
			for j in flatten(i):
				if j and j is not NULLTYPE_BUILTIN:
					yield j
		else:
			if i and i is not NULLTYPE_BUILTIN:
				yield i


# noinspection PyUnusedLocal
def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
	return 'Warning {}\n'.format(message)

warnings.formatwarning = warning_on_one_line


class SymbolTableBuilder(NodeVisitor):
	def __init__(self, file_name=None):
		super().__init__()
		self.file_name = file_name
		self.warnings = False

	def build(self, node):
		res = self.visit(node)
		if self.unvisited_symbols:
			warnings.warn('Unused variables ({})'.format(','.join(sym_name for sym_name in self.unvisited_symbols)))
		return res

	def visit_program(self, node):
		return self.visit(node.block)

	def visit_if(self, node):
		blocks = []
		for x, block in enumerate(node.blocks):
			self.visit(node.comps[x])
			blocks.append(self.visit(block))
		return blocks

	def visit_else(self, node):
		pass

	def visit_while(self, node):
		self.visit(node.comp)
		self.visit(node.block)

	def visit_for(self, node):
		for element in node.elements:
			var_sym = VarSymbol(element.value, self.visit(node.iterator))
			var_sym.val_assigned = True
			self.define(var_sym.name, var_sym)
		self.visit(node.block)

	def visit_loopblock(self, node):
		results = []
		for child in node.children:
			results.append(self.visit(child))
		return results

	def visit_switch(self, node):
		switch_var = self.visit(node.value)
		for case in node.cases:
			case_type = self.visit(case)
			if case_type != DEFAULT and case_type is not switch_var.type:
				warnings.warn('file={} line={}: Types in switch do not match case'.format(self.file_name, node.line_num))
				self.warnings = True

	def visit_case(self, node):
		if node.value == DEFAULT:
			case_type = DEFAULT
		else:
			case_type = self.visit(node.value)
		self.visit(node.block)
		return case_type

	def visit_break(self, node):
		pass

	def visit_continue(self, node):
		pass

	def visit_constant(self, node):
		if node.value == TRUE or node.value == FALSE:
			return self.search_scopes(BOOL)
		elif node.value == NAN or node.value == INF or node.value == NEGATIVE_INF:
			return self.search_scopes(DEC)
		else:
			return NotImplementedError

	def visit_num(self, node):
		return self.infer_type(node.value)

	def visit_str(self, node):
		return self.infer_type(node.value)

	def visit_type(self, node):
		typ = self.search_scopes(node.value)
		if typ is self.search_scopes(FUNC):
			typ.return_type = self.visit(node.func_ret_type)
		return typ

	def visit_assign(self, node):  # TODO clean up this mess of a function
		collection_type = None
		if isinstance(node.left, VarDecl):
			var_name = node.left.var_node.value
			value = self.infer_type(node.left.type_node)
		elif isinstance(node.right, Collection):
			var_name = node.left.value
			value, collection_type = self.visit(node.right)
		else:
			var_name = node.left.value
			value = self.visit(node.right)
		lookup_var = self.search_scopes(var_name)
		if not lookup_var:
			if collection_type:
				col_sym = CollectionSymbol(var_name, value, collection_type)
				col_sym.val_assigned = True
				self.define(var_name, col_sym)
			else:
				var_sym = VarSymbol(var_name, value, node.left.read_only)
				var_sym.val_assigned = True
				self.define(var_name, var_sym)
		else:
			if lookup_var.read_only:
				warnings.warn('file={} line={}: Cannot change the value of a variable declared constant: {}'.format(self.file_name, var_name, node.line_num))
				self.warnings = True
			lookup_var.val_assigned = True
			if lookup_var.type in (self.search_scopes(DEC), self.search_scopes(FLOAT)):
				if value in (self.search_scopes(INT), self.search_scopes(DEC), self.search_scopes(FLOAT)):
					return
			if lookup_var.type is value:
				return
			if isinstance(value, TypeSymbol):
				value.accessed = True
				if value.type is self.search_scopes(FUNC):
					if value.type.return_type == lookup_var.type:
						return
			if hasattr(value, 'value'):
				if value.value == lookup_var.type.name:
					return
			warnings.warn('file={} line={} Type Error: Not good things happening (fix this message)'.format(self.file_name, node.line_num))
			self.warnings = True

	def visit_opassign(self, node):
		left = self.visit(node.left)
		right = self.visit(node.right)
		left_type = self.infer_type(left)
		right_type = self.infer_type(right)
		any_type = self.search_scopes(ANY)
		if left_type in (self.search_scopes(DEC), self.search_scopes(FLOAT)):  # TODO: implicit type conversion needs an expanded official solution
			if right_type in (self.search_scopes(INT), self.search_scopes(DEC), self.search_scopes(FLOAT)):
				return left_type
		if right_type is left_type or left_type is any_type or right_type is any_type:
			return left_type
		else:
			warnings.warn('file={} line={}: Things that should not be happening ARE happening (fix this message)'.format(self.file_name, node.line_num))
			self.warnings = True

	def visit_var(self, node):
		var_name = node.value
		val = self.search_scopes(var_name)
		if val is None:
			warnings.warn('file={} line={}: Name Error: {}'.format(self.file_name, node.line_num, repr(var_name)))
			self.warnings = True
		else:
			if not val.val_assigned:
				warnings.warn('file={} line={}: {} is being accessed before it was defined'.format(self.file_name, var_name, node.line_num))
				self.warnings = True
			val.accessed = True
			return val

	def visit_binop(self, node):
		if node.op.value == CAST:
			self.visit(node.left)
			return self.infer_type(self.visit(node.right))
		else:
			left = self.visit(node.left)
			right = self.visit(node.right)
			left_type = self.infer_type(left)
			right_type = self.infer_type(right)
			any_type = self.search_scopes(ANY)
			if left_type in (self.search_scopes(INT), self.search_scopes(DEC), self.search_scopes(FLOAT)):
				if right_type in (self.search_scopes(INT), self.search_scopes(DEC), self.search_scopes(FLOAT)):
					return left_type
			if right_type is left_type or left_type is any_type or right_type is any_type:
				return left_type
			else:
				warnings.warn('file={} line={}: Oh noez, it is bwoken (fix this message)'.format(self.file_name, node.line_num))
				self.warnings = True

	def visit_unaryop(self, node):
		return self.visit(node.expr)

	def visit_range(self, node):
		left = self.visit(node.left)
		right = self.visit(node.right)
		left_type = self.infer_type(left)
		right_type = self.infer_type(right)
		any_type = self.search_scopes(ANY)
		if left_type in (self.search_scopes(INT), self.search_scopes(DEC), self.search_scopes(FLOAT)):
			if right_type in (self.search_scopes(INT), self.search_scopes(DEC), self.search_scopes(FLOAT)):
				return left_type
		if right_type is left_type or left_type is any_type or right_type is any_type:
			return left_type
		else:
			warnings.warn('file={} line={}: Please don\'t do what you just did there ever again. It bad (fix this message)'.format(self.file_name, node.line_num))
			self.warnings = True

	def visit_compound(self, node):
		results = []
		for child in node.children:
			result = self.visit(child)
			if result:
				results.append(result)
		return results

	def visit_typedeclaration(self, node):
		typs = []
		for t in node.collection:
			typs.append(self.visit(t))
		if len(typs) == 1:
			typs = typs[0]
		else:
			typs = tuple(typs)
		typ = TypeSymbol(node.name.value, typs)
		self.define(typ.name, typ)

	def visit_funcdecl(self, node):
		func_name = node.name.value
		func_type = self.search_scopes(node.return_type.value)
		self.new_scope()
		for k, v in node.parameters.items():
			var_type = self.search_scopes(v.value)
			if var_type is self.search_scopes(FUNC):
				sym = FuncSymbol(k, v.func_ret_type, None, None)
			elif isinstance(var_type, TypeSymbol):
				var_type.accessed = True
				if var_type.type is self.search_scopes(FUNC):
					sym = FuncSymbol(k, var_type.type.return_type, None, None)
				else:
					raise NotImplementedError
			else:
				sym = VarSymbol(k, var_type)
			sym.val_assigned = True
			self.define(sym.name, sym)
		func_symbol = FuncSymbol(func_name, func_type, node.parameters, node.body)
		self.define(func_name, func_symbol, 1)
		return_types = self.visit(func_symbol.body)
		return_types = list(flatten(return_types))
		for ret_type in return_types:
			if self.infer_type(ret_type) is not func_type:
				warnings.warn('file={} line={}: The actual return type does not match the declared return type: {}'.format(self.file_name, node.line_num, func_name))
				self.warnings = True
		self.drop_top_scope()

	def visit_anonymousfunc(self, node):
		func_type = self.search_scopes(node.return_type.value)
		self.new_scope()
		for k, v in node.parameters.items():
			var_type = self.search_scopes(v.value)
			if var_type is self.search_scopes(FUNC):
				sym = FuncSymbol(k, v.func_ret_type, None, None)
			else:
				sym = VarSymbol(k, var_type)
			sym.val_assigned = True
			self.define(sym.name, sym)
		func_symbol = FuncSymbol(ANON, func_type, node.parameters, node.body)
		return_var_type = self.visit(func_symbol.body)
		return_var_type = list(flatten(return_var_type))
		for ret_type in return_var_type:
			if self.infer_type(ret_type) is not func_type:
				warnings.warn('file={} line={}: The actual return type does not match the declared return type'.format(self.file_name, node.line_num))
				self.warnings = True
		self.drop_top_scope()

	def visit_funccall(self, node):
		func_name = node.name.value
		func = self.search_scopes(func_name)
		for arg in node.arguments:
			self.visit(arg)
		if func is None:
			warnings.warn('file={} line={}: Name Error: {}'.format(self.file_name, node.line_num, repr(func_name)))
			self.warnings = True
		else:
			func.accessed = True
			return func.type

	def visit_return(self, node):
		res = self.visit(node.value)
		return res

	def visit_pass(self, node):
		pass

	def visit_noop(self, node):
		pass

	def visit_vardecl(self, node):
		type_name = node.type_node.value
		type_symbol = self.search_scopes(type_name)
		var_name = node.var_node.value
		var_symbol = VarSymbol(var_name, type_symbol)
		self.define(var_symbol.name, var_symbol)

	def visit_collection(self, node):
		types = []
		for item in node.items:
			types.append(self.visit(item))
		if types[1:] == types[:-1]:
			return self.search_scopes(ARRAY), types[0]
		else:
			return self.search_scopes(LIST), self.search_scopes(ANY)

	def visit_hashmap(self, node):
		for key in node.items.keys():
			value = self.search_scopes(key)
			if value:
				value.accessed = True
		return self.search_scopes(DICT)

	def visit_collectionaccess(self, node):
		collection = self.search_scopes(node.collection.value)
		collection.accessed = True
		if isinstance(node.key, Var):
			key = self.infer_type(node.key.value)
		else:
			key = self.visit(node.key)
		if collection.type is self.search_scopes(ARRAY) or collection.type is self.search_scopes(LIST) or collection.type is self.search_scopes(TUPLE) or collection.type is self.search_scopes(SET):
			if key is not self.search_scopes(INT) and key.type is not self.search_scopes(INT):
				warnings.warn('file={} line={}: Something something error... huh? (fix this message)'.format(self.file_name, node.line_num))
				self.warnings = True
			return collection.item_types
		elif collection.type is self.search_scopes(DICT) or collection.type is self.search_scopes(ENUM):
			if key is not self.search_scopes(STR) and key.type is not self.search_scopes(STR):
				warnings.warn('file={} line={}: Dude....... don\'t (fix this message)'.format(self.file_name, node.line_num))
				self.warnings = True
			return self.search_scopes(ANY)
		else:
			warnings.warn('file={} line={}: WHY? (fix this message)'.format(self.file_name, node.line_num))
			self.warnings = True

	def visit_print(self, node):
		self.visit(node.value)

if __name__ == '__main__':
	from my_lexer import Lexer
	from my_parser import Parser
	f = 'math.my'
	code = open(f).read()
	lexer = Lexer(code, f)
	parser = Parser(lexer)
	tree = parser.parse()
	symtab_builder = SymbolTableBuilder(parser.file_name)
	symtab_builder.build(tree)
	if not symtab_builder.warnings:
		print('Looks good!')