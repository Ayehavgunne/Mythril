import warnings
from my_visitor import NodeVisitor, StructSymbol
from my_visitor import VarSymbol
from my_visitor import CollectionSymbol
from my_visitor import FuncSymbol
from my_visitor import AliasSymbol
from my_ast import VarDecl, DotAccess, CollectionAccess
from my_ast import Var
from my_ast import Collection
from my_grammar import *


def flatten(container):
	for i in container:
		if isinstance(i, (list, tuple)):
			for j in flatten(i):
				if j:
					yield j
		else:
			if i:
				yield i


# noinspection PyUnusedLocal
def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
	return 'Warning {}\n'.format(message)

warnings.formatwarning = warning_on_one_line


class Preprocessor(NodeVisitor):
	def __init__(self, file_name=None):
		super().__init__()
		self.file_name = file_name
		self.warnings = False
		self.return_flag = False
		# self.num_types = (
		# 	self.search_scopes(BOOL),
		# 	self.search_scopes(INT),
		# 	self.search_scopes(INT8),
		# 	self.search_scopes(INT32),
		# 	self.search_scopes(INT128),
		# 	self.search_scopes(DEC),
		# 	self.search_scopes(FLOAT)
		# )

	def check(self, node):
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
			elem_type = self.visit(node.iterator)
			if isinstance(elem_type, CollectionSymbol):
				elem_type = elem_type.item_types
			var_sym = VarSymbol(element.value, elem_type)
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
		field_assignment = None
		collection_assignment = None
		if isinstance(node.left, VarDecl):
			var_name = node.left.value.value
			value = self.infer_type(node.left.type)
			value.accessed = True
		elif isinstance(node.right, Collection):
			var_name = node.left.value
			value, collection_type = self.visit(node.right)
		elif isinstance(node.left, DotAccess):
			field_assignment = True
			var_name = self.visit(node.left)
			value = self.visit(node.right)
		elif isinstance(node.left, CollectionAccess):
			collection_assignment = True
			var_name = node.left.collection.value
			# key = node.left.key.value
			value = self.visit(node.right)
		else:
			var_name = node.left.value
			value = self.visit(node.right)
			if isinstance(value, VarSymbol):
				value = value.type
		lookup_var = self.search_scopes(var_name)
		if not lookup_var:
			if collection_type:
				col_sym = CollectionSymbol(var_name, value, collection_type)
				col_sym.val_assigned = True
				self.define(var_name, col_sym)
			elif field_assignment:
				if var_name is value:
					return
				else:
					warnings.warn('file={} line={} Type Error: What are you trying to do?!?! (fix this message)'.format(self.file_name, node.line_num))
					self.warnings = True
			elif isinstance(value, FuncSymbol):
				value.name = var_name
				self.define(var_name, value)
			elif value.name == FUNC:
				var = self.visit(node.right)
				if isinstance(var, FuncSymbol):
					self.define(var_name, var)
				else:
					# noinspection PyUnresolvedReferences
					val_info = self.search_scopes(node.right.value)
					func_sym = FuncSymbol(var_name, val_info.type.return_type, val_info.parameters, val_info.body, val_info.parameter_defaults)
					self.define(var_name, func_sym)
			else:
				var_sym = VarSymbol(var_name, value, node.left.read_only)
				var_sym.val_assigned = True
				self.define(var_name, var_sym)
		else:
			if collection_assignment:
				if lookup_var.item_types == value:
					return
			if lookup_var.read_only:
				warnings.warn('file={} line={}: Cannot change the value of a variable declared constant: {}'.format(self.file_name, var_name, node.line_num))
				self.warnings = True
			lookup_var.val_assigned = True
			if lookup_var.type in (self.search_scopes(DEC), self.search_scopes(FLOAT)):
				if value in (self.search_scopes(INT), self.search_scopes(DEC), self.search_scopes(FLOAT)):
					return
			if lookup_var.type is value:
				return
			if lookup_var.type is value.type:
				return
			if isinstance(value, AliasSymbol):
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

	def visit_fieldassignment(self, node):
		obj = self.search_scopes(node.obj)
		return self.visit(obj.type.fields[node.field])

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
		if node.op == CAST:
			self.visit(node.left)
			return self.infer_type(self.visit(node.right))
		else:
			left = self.visit(node.left)
			right = self.visit(node.right)
			left_type = self.infer_type(left)
			right_type = self.infer_type(right)
			any_type = self.search_scopes(ANY)
			# if left_type in self.num_types:
			# 	if right_type in self.num_types:
			# 		return left_type
			if right_type is left_type or left_type is any_type or right_type is any_type:
				return left_type
			else:
				warnings.warn('file={} line={}: types do not match for operation {}, got {} : {}'.format(self.file_name, node.line_num, node.op, left, right))
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
		typ = AliasSymbol(node.name.value, typs)
		self.define(typ.name, typ)

	def visit_funcdecl(self, node):
		func_name = node.name
		func_type = self.search_scopes(node.return_type.value)
		if func_type and func_type.name == FUNC:
			func_type.return_type = self.visit(node.return_type.func_ret_type)
		self.define(func_name, FuncSymbol(func_name, func_type, node.parameters, node.body, node.parameter_defaults))
		self.new_scope()
		if node.varargs:
			varargs_type = self.search_scopes(ARRAY)
			varargs_type.type = node.varargs[1].value
			varargs = CollectionSymbol(node.varargs[0], varargs_type, self.search_scopes(node.varargs[1].value))
			varargs.val_assigned = True
			self.define(varargs.name, varargs)
		for k, v in node.parameters.items():
			var_type = self.search_scopes(v.value)
			if var_type is self.search_scopes(FUNC):
				sym = FuncSymbol(k, v.func_ret_type, None, None)
			elif isinstance(var_type, AliasSymbol):
				var_type.accessed = True
				if var_type.type is self.search_scopes(FUNC):
					sym = FuncSymbol(k, var_type.type.return_type, None, None)
				else:
					raise NotImplementedError
			else:
				sym = VarSymbol(k, var_type)
			sym.val_assigned = True
			self.define(sym.name, sym)
		return_types = self.visit(node.body)
		return_types = list(flatten(return_types))
		if self.return_flag:
			self.return_flag = False
			for ret_type in return_types:
				infered_type = self.infer_type(ret_type)
				if infered_type is not func_type:
					warnings.warn('file={} line={}: The actual return type does not match the declared return type: {}'.format(self.file_name, node.line_num, func_name))
					self.warnings = True
		elif func_type != VOID:
			warnings.warn('file={} line={}: No return value was specified for function: {}'.format(self.file_name, node.line_num, func_name))
			self.warnings = True
		func_symbol = FuncSymbol(func_name, func_type, node.parameters, node.body, node.parameter_defaults)
		self.define(func_name, func_symbol, 1)
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
		return func_symbol

	def visit_funccall(self, node):
		func_name = node.name
		func = self.search_scopes(func_name)
		for x, param in enumerate(func.parameters.values()):
			if x < len(node.arguments):
				var = self.visit(node.arguments[x])
				param_ss = self.search_scopes(param.value)
				# if param_ss in self.num_types and (var in self.num_types or var.type in self.num_types):
				# 	continue
				if param_ss != self.search_scopes(ANY) and param.value != var.name and param.value != var.type.name:
					raise TypeError
			else:
				func_param_keys = list(func.parameters.keys())
				if func_param_keys[x] not in node.named_arguments.keys() and func_param_keys[x] not in func.parameter_defaults.keys():
					warnings.warn('file={} line={}: Missing arguments to function: {}'.format(self.file_name, node.line_num, repr(func_name)))
					self.warnings = True
				else:
					if func_param_keys[x] in node.named_arguments.keys():
						if param.value != self.visit(node.named_arguments[func_param_keys[x]]).name:
							raise TypeError
		if func is None:
			warnings.warn('file={} line={}: Name Error: {}'.format(self.file_name, node.line_num, repr(func_name)))
			self.warnings = True
		else:
			func.accessed = True
			return func.type

	def visit_methodcall(self, node):  # Not done here!
		method_name = node.name
		obj = self.search_scopes(node.obj)
		method = self.search_scopes(method_name)
		for x, param in enumerate(method.parameters.values()):
			if x < len(node.arguments):
				var = self.visit(node.arguments[x])
				param_ss = self.search_scopes(param.value)
				# if param_ss in self.num_types and (var in self.num_types or var.type in self.num_types):
				# 	continue
				if param_ss != self.search_scopes(ANY) and param.value != var.name and param.value != var.type.name:
					raise TypeError
			else:
				method_param_keys = list(method.parameters.keys())
				if method_param_keys[x] not in node.named_arguments.keys() and method_param_keys[x] not in method.parameter_defaults.keys():
					raise TypeError('Missing arguments to method')
				else:
					if method_param_keys[x] in node.named_arguments.keys():
						if param.value != self.visit(node.named_arguments[method_param_keys[x]]).name:
							raise TypeError
		if method is None:
			warnings.warn('file={} line={}: Name Error: {}'.format(self.file_name, node.line_num, repr(method_name)))
			self.warnings = True
		else:
			method.accessed = True
			return method.type

	def visit_structdeclaration(self, node):
		sym = StructSymbol(node.name, node.fields)
		self.define(sym.name, sym)

	def visit_return(self, node):
		res = self.visit(node.value)
		self.return_flag = True
		return res

	def visit_pass(self, node):
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

	def visit_dotaccess(self, node):
		obj = self.search_scopes(node.obj)
		obj.accessed = True
		return self.visit(obj.type.fields[node.field])

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
		if collection.type is self.search_scopes(ARRAY) or collection.type is self.search_scopes(LIST) or collection.type is self.search_scopes(SET):
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
		if node.value:
			self.visit(node.value)

	def visit_input(self, node):
		self.visit(node.value)

if __name__ == '__main__':
	from my_lexer import Lexer
	from my_parser import Parser
	f = 'test.my'
	code = open(f).read()
	lexer = Lexer(code, f)
	parser = Parser(lexer)
	tree = parser.parse()
	symtab_builder = Preprocessor(parser.file_name)
	symtab_builder.check(tree)
	if not symtab_builder.warnings:
		print('Looks good!')
