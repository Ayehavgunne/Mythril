from time import sleep
from time import time
from ctypes import CFUNCTYPE
from ctypes import c_void_p

from decimal import Decimal
from llvmlite import ir
import llvmlite.binding as llvm
from my_builtin_functions import define_printd
# from my_builtin_functions import define_print128
from my_builtin_functions import define_printb
# from my_custom_llvm_types import create_dynamic_array
from my_visitor import NodeVisitor
from my_ast import StructLiteral
from my_ast import DotAccess
from my_ast import Input
from my_ast import VarDecl
from my_grammar import *
from compiler import type_map
from compiler import RET_VAR
from compiler.operations import operations


class CodeGenerator(NodeVisitor):
	def __init__(self, file_name):
		super().__init__()
		self.file_name = file_name
		self.module = ir.Module()
		func_ty = ir.FunctionType(ir.VoidType(), [])
		func = ir.Function(self.module, func_ty, 'main')
		entry_block = func.append_basic_block('entry')
		self.function = func
		self.main_function = func
		self.builder = ir.IRBuilder(entry_block)
		self.main_builder = self.builder
		self.exit_block = None
		self.loop_test_blocks = []
		self.loop_end_blocks = []
		self.is_break = False
		llvm.initialize()
		llvm.initialize_native_target()
		llvm.initialize_native_asmprinter()
		self.target = llvm.Target.from_default_triple()
		self.anon_counter = 0
		self._add_builtins()

	def __str__(self):
		return str(self.module)

	def visit_program(self, node):
		self.visit(node.block)
		self.builder.ret_void()

	@staticmethod
	def visit_num(node):
		return ir.Constant(type_map[node.token.value_type], node.value)

	def visit_var(self, node):
		return self.load(node.value)

	def visit_binop(self, node):
		return operations(self, node)

	def visit_anonymousfunc(self, node):
		self.anon_counter += 1
		return self.funcdecl('anon{}'.format(self.anon_counter), node)

	def visit_funcdecl(self, node):
		return self.funcdecl(node.name.value, node)

	def funcdecl(self, name, node):
		self.start_function(name, node.return_type, node.parameters, node.parameter_defaults, node.varargs)
		for i, arg in enumerate(self.function.args):
			arg.name = list(node.parameters.keys())[i]
			var_addr = self.builder.alloca(arg.type, name=arg.name)
			self.define(arg.name, var_addr)
			self.builder.store(arg, var_addr)
		if self.function.function_type.return_type != type_map[VOID]:
			ret_var_addr = self.builder.alloca(self.function.function_type.return_type, name=RET_VAR)
			self.define(RET_VAR, ret_var_addr)
		ret = self.visit(node.body)
		func = self.function
		self.end_function(ret)
		return func

	def visit_funccall(self, node):
		func_type = self.search_scopes(node.name.value)
		if isinstance(func_type, ir.Function):
			func_type = func_type.type.pointee
			name = self.search_scopes(node.name.value)
			name = name.name
		else:
			name = node.name.value
		if len(node.arguments) < len(func_type.args):
			args = []
			args_supplied = []
			for x, arg in enumerate(func_type.arg_order):
				if x < len(node.arguments):
					args.append(self.visit(node.arguments[x]))
				else:
					if node.named_arguments and arg in node.named_arguments:
						args.append(self.visit(node.named_arguments[arg]))
					else:
						if set(node.named_arguments.keys()) & set(args_supplied):
							raise TypeError('got multiple values for argument(s) {}'.format(set(node.named_arguments.keys()) & set(args_supplied)))
						args.append(self.visit(func_type.parameter_defaults[arg]))
				args_supplied.append(arg)
		elif len(node.arguments) + len(node.named_arguments) > len(func_type.args):
			raise SyntaxError('Unexpected arguments')
		else:
			args = [self.visit(arg) for arg in node.arguments]
		return self.call(name, args)

	def visit_compound(self, node):
		ret = None
		for child in node.children:
			temp = self.visit(child)
			if temp:
				ret = temp
		return ret

	def visit_structdeclaration(self, node):
		fields = []
		for field in node.fields.values():
			if field.value == STR:
				fields.append(str)
			else:
				fields.append(type_map[field.value])
		struct = ir.LiteralStructType(fields)
		struct.fields = [field for field in node.fields.keys()]
		self.define(node.name.value, struct)

	def visit_typedeclaration(self, node):
		raise NotImplementedError

	def visit_vardecl(self, node):
		var_addr = self.builder.alloca(type_map[node.type_node.value], name=node.var_node.value)
		self.define(node.var_node.value, var_addr)
		self.store(self.visit(node.var_node), node.var_node.value)

	@staticmethod
	def visit_type(node):
		return type_map[node.value]

	def visit_noop(self, node):
		pass

	def visit_if(self, node):
		start_block = self.add_block('if.start')
		end_block = self.add_block('if.end')
		self.builder.branch(start_block)
		self.builder.position_at_end(start_block)
		for x, comp in enumerate(node.comps):
			if_true_block = self.add_block('if.true.{}'.format(x))
			if x + 1 < len(node.comps):
				if_false_block = self.add_block('if.false.{}'.format(x))
			else:
				if_false_block = end_block
			cond_val = self.visit(comp)
			self.builder.cbranch(cond_val, if_true_block, if_false_block)
			self.builder.position_at_end(if_true_block)
			ret = self.visit(node.blocks[x])
			if not ret:
				self.branch(end_block)
			self.builder.position_at_end(if_false_block)
		self.position_at_end(end_block)

	def visit_else(self, _):
		return self.builder.icmp_unsigned(EQUALS, self.const(1), self.const(1), 'cmptmp')

	def visit_while(self, node):
		test_block = self.add_block('while.cond')
		body_block = self.add_block('while.body')
		end_block = self.add_block('while.end')
		self.loop_test_blocks.append(test_block)
		self.loop_end_blocks.append(end_block)
		self.branch(test_block)
		self.position_at_end(test_block)
		cond = self.visit(node.comp)
		self.cbranch(cond, body_block, end_block)
		self.position_at_end(body_block)
		self.visit(node.block)
		if not self.is_break:
			self.branch(test_block)
		else:
			self.is_break = False
		self.position_at_end(end_block)
		self.loop_test_blocks.pop()
		self.loop_end_blocks.pop()

	def visit_for(self, node):
		init_block = self.add_block('for.init')
		test_block = self.add_block('for.cond')
		body_block = self.add_block('for.body')
		end_block = self.add_block('for.end')
		self.loop_test_blocks.append(test_block)
		self.loop_end_blocks.append(end_block)
		self.branch(init_block)
		self.position_at_end(init_block)
		loop_range = self.visit(node.iterator)
		start = loop_range[0]
		stop = loop_range[-1]
		step = self.const(1)
		varname = node.elements[0].value
		self.allocate(start, varname, type_map[INT])
		self.branch(test_block)
		self.position_at_end(test_block)
		cond = self.builder.icmp_unsigned(LESS_THAN, self.load(varname), stop)
		self.cbranch(cond, body_block, end_block)
		self.position_at_end(body_block)
		self.visit(node.block)
		succ = self.builder.add(step, self.load(varname))
		self.store(varname, succ)
		if not self.is_break:
			self.branch(test_block)
		else:
			self.is_break = False
		self.position_at_end(end_block)
		self.loop_test_blocks.pop()
		self.loop_end_blocks.pop()

	def visit_loopblock(self, node):
		for child in node.children:
			temp = self.visit(child)
			if temp:
				return temp

	def visit_switch(self, node):
		default_exists = False
		switch_end_block = self.add_block('switch_end')
		default_block = self.add_block('default')
		switch = self.switch(self.visit(node.value), default_block)
		cases = []
		for case in node.cases:
			if case.value == DEFAULT:
				cases.append(default_block)
				default_exists = True
			else:
				cases.append(self.add_block('case'))
		if not default_exists:
			self.position_at_start(default_block)
			self.branch(switch_end_block)
		for x, case in enumerate(node.cases):
			self.position_at_start(cases[x])
			break_ = self.visit(case.block)
			if break_ == BREAK:
				self.branch(switch_end_block)
			else:
				if x == len(node.cases) - 1:
					self.branch(switch_end_block)
				else:
					self.branch(cases[x + 1])
			if case.value != DEFAULT:
				switch.add_case(self.visit(case.value), cases[x])
		self.position_at_end(switch_end_block)

	def visit_break(self, _):
		if 'case' in self.builder.block.name:
			return BREAK
		else:
			self.is_break = True
			return self.builder.branch(self.loop_end_blocks[-1])

	def visit_continue(self, _):
		return self.builder.branch(self.loop_test_blocks[-1])

	@staticmethod
	def visit_pass(_):
		return

	def visit_unaryop(self, node):
		op = node.op.value
		expr = self.visit(node.expr)
		if op == PLUS:
			return expr
		elif op == MINUS:
			return self.builder.neg(expr)
		elif op == NOT:
			return self.builder.not_(expr)

	def visit_range(self, node):
		left = self.visit(node.left)
		right = self.visit(node.right)
		return left, right

	def visit_assign(self, node):
		if isinstance(node.right, StructLiteral):
			self.struct_assign(node)
		else:
			if isinstance(node.right, Input):
				node.right.type = node.left.type_node.value
			var = self.visit(node.right)
			if isinstance(node.left, VarDecl):
				var_name = node.left.var_node.value
				if node.left.type_node.value == FLOAT:
					node.right.value = float(node.right.value)
				self.allocate(var, var_name, var.type)
			elif isinstance(node.left, DotAccess):
				obj = self.search_scopes(node.left.obj)
				obj_type = self.search_scopes(obj.struct_name)
				new_obj = self.builder.insert_value(self.load(obj.name), self.visit(node.right), obj_type.fields.index(node.left.field))
				struct_ptr = self.builder.alloca(obj_type, name=obj.name)
				self.builder.store(new_obj, struct_ptr)
				struct_ptr.struct_name = obj.struct_name
				self.define(obj.name, struct_ptr)
			else:
				var_name = node.left.value
				var_value = self.top_scope.get(var_name)
				if var_value:
					if isinstance(var_value, float):
						node.right.value = float(node.right.value)
					self.store(var_name, var)
				elif isinstance(var, ir.Function):
					self.define(var_name, var)
				else:
					self.allocate(var, var_name, var.type)

	def visit_fieldassignment(self, node):
		obj = self.search_scopes(node.obj)
		obj_type = self.search_scopes(obj.struct_name)
		return self.builder.extract_value(self.load(node.obj), obj_type.fields.index(node.field))

	def struct_assign(self, node):
		struct_type = self.search_scopes(node.left.type_node.value)
		name = node.left.var_node.value
		fields = []
		for field in node.right.fields.values():
			fields.append(self.visit(field))
		struct = struct_type(fields)
		struct_ptr = self.builder.alloca(struct_type, name=name)
		self.builder.store(struct, struct_ptr)
		struct_ptr.struct_name = node.left.type_node.value
		self.define(name, struct_ptr)

	def visit_dotaccess(self, node):
		obj = self.search_scopes(node.obj)
		obj_type = self.search_scopes(obj.struct_name)
		return self.builder.extract_value(self.load(node.obj), obj_type.fields.index(node.field))

	def visit_opassign(self, node):
		var_name = node.left.value
		op = node.op.value
		right = self.visit(node.right)
		if isinstance(self.search_scopes(var_name).type.pointee, ir.IntType):
			if op == PLUS_ASSIGN:
				res = self.builder.add(self.load(var_name), right)
			elif op == MINUS_ASSIGN:
				res = self.builder.sub(self.load(var_name), right)
			elif op == MUL_ASSIGN:
				res = self.builder.mul(self.load(var_name), right)
			elif op == FLOORDIV_ASSIGN:
				res = self.builder.sdiv(self.load(var_name), right)
			elif op == DIV_ASSIGN:
				res = self.builder.fdiv(self.load(var_name), right)
			elif op == MOD_ASSIGN:
				res = self.builder.srem(self.load(var_name), right)
			elif op == POWER_ASSIGN:
				temp = self.builder.alloca(type_map[INT])
				self.builder.store(self.load(var_name), temp)
				for _ in range(node.right.value - 1):
					res = self.builder.mul(self.builder.load(temp), self.load(var_name))
					self.builder.store(res, temp)
				res = self.builder.load(temp)
			else:
				raise NotImplementedError()
		else:
			if op == PLUS_ASSIGN:
				res = self.builder.fadd(self.load(var_name), right)
			elif op == MINUS_ASSIGN:
				res = self.builder.fsub(self.load(var_name), right)
			elif op == MUL_ASSIGN:
				res = self.builder.fmul(self.load(var_name), right)
			elif op == FLOORDIV_ASSIGN:
				res = self.builder.sdiv(self.builder.fptosi(self.load(var_name), ir.IntType(64)), self.builder.fptosi(right, ir.IntType(64)))
			elif op == DIV_ASSIGN:
				res = self.builder.fdiv(self.load(var_name), right)
			elif op == MOD_ASSIGN:
				res = self.builder.frem(self.load(var_name), right)
			elif op == POWER_ASSIGN:
				temp = self.builder.alloca(type_map[DEC])
				self.builder.store(self.load(var_name), temp)
				for _ in range(node.right.value - 1):
					res = self.builder.fmul(self.builder.load(temp), self.load(var_name))
					self.builder.store(res, temp)
				res = self.builder.load(temp)
			else:
				raise NotImplementedError()
		self.store(var_name, res)

	def visit_return(self, node):
		val = self.visit(node.value)
		if val.type != ir.VoidType():
			self.store(RET_VAR, val)
		self.branch(self.exit_block)
		return True

	def visit_constant(self, node):
		if node.value == TRUE:
			return self.const(1, 1)
		elif node.value == FALSE:
			return self.const(0, 1)
		else:
			raise NotImplementedError('file={} line={}'.format(self.file_name, node.line_num))

	def visit_str(self, node):
		string = self.stringz(node.value)
		percent_ptr = self.builder.alloca(ir.ArrayType(string.type.element, string.type.count), name='var_ptr')
		self.builder.store(string, percent_ptr)
		percent_ptr_gep = self.builder.gep(percent_ptr, [self.const(0), self.const(0)])
		return percent_ptr_gep

	def visit_collection(self, node):
		elements = []
		for item in node.items:
			elements.append(self.visit(item))
		elem_types = [item.type for item in elements]
		if node.type == LIST:
			if elem_types[1:] == elem_types[:-1]:
				return self.define_array(node, elements)
			else:
				return self.define_list(node, elements)
		else:
			raise NotImplementedError

	@staticmethod
	def define_array(node, elements):
		array_type = ir.ArrayType(elements[0].type, len(elements))
		array = array_type(elements)
		return array

	def define_list(self, node, elements):
		raise NotImplementedError

	def visit_hashmap(self, node):
		raise NotImplementedError

	def visit_collectionaccess(self, node):
		key = node.key.value
		collection = self.search_scopes(node.collection.value)
		return self.builder.extract_value(self.load(collection.name), [key])

	def visit_print(self, node):
		if node.value:
			val = self.visit(node.value)
		else:
			self.call('putchar', [ir.Constant(type_map[INT32], 10)])
			return
		if isinstance(val.type, ir.IntType):
			# noinspection PyUnresolvedReferences
			if val.type.width == 1:
				self.call('printb', [val])
			# elif val.type.width == 128:
			# 	self.call('print128', [val])
			else:
				self.call('printd', [val])
		elif isinstance(val.type, (ir.FloatType, ir.DoubleType)):
			percent_f = self.stringz('%f')
			percent_f_ptr = self.builder.alloca(ir.ArrayType(percent_f.type.element, percent_f.type.count), name='var_ptr')
			self.builder.store(percent_f, percent_f_ptr)
			var_ptr_gep = self.builder.gep(percent_f_ptr, [self.const(0), self.const(0)])
			var_ptr_gep = self.builder.bitcast(var_ptr_gep, type_map[INT8].as_pointer())
			self.call('printf', [var_ptr_gep, val])
		elif isinstance(val.type, ir.ArrayType):  # TODO: This assumes an array of characters, make it not assume
			val_ptr = self.builder.alloca(ir.ArrayType(val.type.element, val.type.count), name='var_ptr')
			self.builder.store(val, val_ptr)
			var_ptr_gep = self.builder.gep(val_ptr, [self.const(0), self.const(0)])
			var_ptr_gep = self.builder.bitcast(var_ptr_gep, ir.IntType(32).as_pointer())
			self.call('puts', [var_ptr_gep])
			return
		elif isinstance(val, (ir.LoadInstr, ir.GEPInstr)):
			val = self.builder.bitcast(val, type_map[INT32].as_pointer())
			self.call('puts', [val])
			return
		self.call('putchar', [ir.Constant(type_map[INT32], 10)])

	def visit_input(self, node):
		var_ptr = self.builder.alloca(ir.ArrayType(type_map[INT8], len(node.value.value) + 1), name='var_ptr')
		self.builder.store(self.stringz(node.value.value), var_ptr)
		var_ptr_gep = self.builder.gep(var_ptr, [self.const(0), self.const(0)])
		var_ptr_gep = self.builder.bitcast(var_ptr_gep, type_map[INT32].as_pointer())
		self.call('puts', [var_ptr_gep])
		percent_d = self.stringz('%d')
		int_ptr = self.builder.alloca(type_map[INT], name='var_ptr')
		percent_ptr = self.builder.alloca(ir.ArrayType(percent_d.type.element, percent_d.type.count), name='var_ptr')
		self.builder.store(percent_d, percent_ptr)
		percent_ptr_gep = self.builder.gep(percent_ptr, [self.const(0), self.const(0)])
		percent_ptr_gep = self.builder.bitcast(percent_ptr_gep, type_map[INT8].as_pointer())
		return self.call('scanf', [percent_ptr_gep, int_ptr])

	# noinspection PyUnusedLocal
	def start_function(self, name, return_type, parameters, parameter_defaults=None, varargs=None):
		self.new_scope()
		ret_type = type_map[return_type.value]
		args = [type_map[param.value] for param in parameters.values()]
		arg_keys = [key for key in parameters.keys()]
		func_type = ir.FunctionType(ret_type, args)
		if parameter_defaults:
			func_type.parameter_defaults = parameter_defaults
		func_type.arg_order = arg_keys
		if return_type.func_ret_type:
			func_type.return_type = func_type.return_type(type_map[return_type.func_ret_type.value], [return_type.func_ret_type.value]).as_pointer()
		func = ir.Function(self.module, func_type, name)
		self.define(name, func_type, 1)
		self.function = func
		entry = self.add_block('entry')
		self.exit_block = self.add_block('exit')
		self.builder.position_at_start(entry)

	def end_function(self, returned=False):
		if not returned:
			self.branch(self.exit_block)
		self.position_at_end(self.exit_block)
		if self.function.function_type.return_type != type_map[VOID]:
			retval = self.builder.load(self.search_scopes(RET_VAR))
			self.builder.ret(retval)
		else:
			self.builder.ret_void()
		self.builder.position_at_end(self.main_function.entry_basic_block)
		self.function = self.main_function
		self.drop_top_scope()

	def new_builder(self, block):
		self.builder = ir.IRBuilder(block)
		return self.builder

	def add_block(self, name):
		return self.function.append_basic_block(name)

	def position_at_start(self, block):
		self.builder.position_at_start(block)

	def position_at_end(self, block):
		self.builder.position_at_end(block)

	def cbranch(self, cond, true_block, false_block):
		self.builder.cbranch(cond, true_block, false_block)

	def branch(self, block):
		self.builder.branch(block)

	def switch(self, value, default):
		return self.builder.switch(value, default)

	def const(self, val, width=None):
		if isinstance(val, int):
			if width:
				return ir.Constant(ir.IntType(width), val)
			else:
				return ir.Constant(type_map[INT], val)
		elif isinstance(val, (float, Decimal)):
			return ir.Constant(type_map[DEC], val)
		elif isinstance(val, bool):
			return ir.Constant(type_map[BOOL], bool(val))
		elif isinstance(val, str):
			return self.stringz(val)
		else:
			raise NotImplementedError

	def const_as_pointer(self, val, width=None):
		if isinstance(val, int):
			if width:
				return ir.Constant(ir.IntType(width).as_pointer(), val)
			else:
				return ir.Constant(type_map[INT].as_pointer(), val)
		elif isinstance(val, float):
			return ir.Constant(type_map[DEC].as_pointer(), val)
		elif isinstance(val, bool):
			return ir.Constant(type_map[BOOL].as_pointer(), bool(val))
		elif isinstance(val, str):
			return self.stringz_pntr(val)
		else:
			raise NotImplementedError

	def allocate(self, val, name, typ):
		saved_block = self.builder.block
		var_addr = self.create_entry_block_alloca(name, typ)
		self.define(name, var_addr)
		self.builder.position_at_end(saved_block)
		self.builder.store(val, var_addr)

	def store(self, name, value):
		self.builder.store(value, self.search_scopes(name))

	def load(self, name):
		return self.builder.load(self.search_scopes(name))

	def call(self, name, args):
		return self.builder.call(self.module.get_global(name), args)

	def create_entry_block_alloca(self, name, typ):
		self.builder.position_at_start(self.builder.function.entry_basic_block)
		return self.builder.alloca(typ, size=None, name=name)

	def _add_builtins(self):
		malloc_ty = ir.FunctionType(type_map[INT8].as_pointer(), [type_map[INT]])
		ir.Function(self.module, malloc_ty, 'malloc')

		free_ty = ir.FunctionType(type_map[VOID], [type_map[INT8].as_pointer()])
		ir.Function(self.module, free_ty, 'free')

		putchar_ty = ir.FunctionType(type_map[INT32], [type_map[INT32]])
		ir.Function(self.module, putchar_ty, 'putchar')

		printf_ty = ir.FunctionType(type_map[INT32], [type_map[INT8].as_pointer()], var_arg=True)
		ir.Function(self.module, printf_ty, 'printf')

		scanf_ty = ir.FunctionType(type_map[INT], [type_map[INT8].as_pointer(), type_map[INT].as_pointer()], var_arg=True)
		ir.Function(self.module, scanf_ty, 'scanf')

		getchar_ty = ir.FunctionType(ir.IntType(4), [])
		ir.Function(self.module, getchar_ty, 'getchar')

		puts_ty = ir.FunctionType(type_map[INT32], [type_map[INT32].as_pointer()])
		ir.Function(self.module, puts_ty, 'puts')

		define_printd(self.module)
		# define_print128(self.module)
		define_printb(self.module)

	@staticmethod
	def stringz_type(string):
		return ir.ArrayType(type_map[INT8], len(string) + 1)

	@staticmethod
	def stringz_pntr_type(string):
		return ir.ArrayType(type_map[INT8], len(string) + 1).as_pointer()

	@staticmethod
	def stringz(string):
		n = len(string) + 1
		buf = bytearray((' ' * n).encode('ascii'))
		buf[-1] = 0
		buf[:-1] = string.encode('utf-8')
		return ir.Constant(ir.ArrayType(type_map[INT8], n), buf)

	@staticmethod
	def stringz_pntr(string):
		n = len(string) + 1
		buf = bytearray((' ' * n).encode('ascii'))
		buf[-1] = 0
		buf[:-1] = string.encode('utf-8')
		return ir.Constant(ir.ArrayType(type_map[INT8], n).as_pointer(), buf)

	def generate_code(self, node):
		return self.visit(node)

	def evaluate(self, optimize=True, llvmdump=False):
		if llvmdump:
			print('======== Unoptimized LLVM IR')
			print(str(self.module))
		llvmmod = llvm.parse_assembly(str(self.module))
		if optimize:
			pmb = llvm.create_pass_manager_builder()
			pmb.opt_level = 2
			pm = llvm.create_module_pass_manager()
			pmb.populate(pm)
			pm.run(llvmmod)
			if llvmdump:
				print('======== Optimized LLVM IR')
				print(str(llvmmod))
		target_machine = self.target.create_target_machine()
		with llvm.create_mcjit_compiler(llvmmod, target_machine) as ee:
			ee.finalize_object()
			fptr = CFUNCTYPE(c_void_p)(ee.get_function_address('main'))
			start_time = time()
			fptr()
			end_time = time()
			print('\n{:f} sec'.format(end_time - start_time))

	def compile(self, filename, optimize=True, run=False):
		import os
		import subprocess
		program_string = llvm.parse_assembly(str(self.module))
		if optimize:
			pmb = llvm.create_pass_manager_builder()
			pmb.opt_level = 2
			pm = llvm.create_module_pass_manager()
			pmb.populate(pm)
			pm.run(program_string)
		cwd = os.getcwd()
		program_string = str(program_string).replace('source_filename = "<string>"', '')
		program_string = str(program_string).replace('target triple = "unknown-unknown-unknown"', '')
		program_string = str(program_string).replace('local_unnamed_addr', '')
		with open(cwd + '/' + filename + '.ll', 'w') as output:
			output.write(program_string)
		os.popen('llc -filetype=obj {0}.ll -march=x86-64 -o {0}.o'.format(filename))
		sleep(.1)
		os.popen('gcc {0}.o -o {0}.bin'.format(filename))
		if run:
			sleep(.1)
			start_time = time()
			output = subprocess.run('./{}.bin'.format(filename), stdout=subprocess.PIPE)
			end_time = time()
			print(output.stdout.decode('utf-8'))
			print('{:f} sec'.format(end_time - start_time))

# if __name__ == '__main__':
# 	from my_lexer import Lexer
# 	from my_parser import Parser
# 	from my_symbol_table_builder import SymbolTableBuilder
# 	file = 'test.my'
# 	code = open(file).read()
# 	lexer = Lexer(code, file)
# 	parser = Parser(lexer)
# 	t = parser.parse()
# 	symtab_builder = SymbolTableBuilder(parser.file_name)
# 	symtab_builder.build(t)
# 	if not symtab_builder.warnings:
# 		generator = CodeGenerator(parser.file_name)
# 		generator.generate_code(t)
# 		# generator.evaluate(True, True)
# 		# generator.evaluate(True, False)
# 		generator.evaluate(False, True)
# 		# generator.evaluate(False, False)
# 		#
# 		# generator.compile(file[:-3], True, True)
# 	else:
# 		print('Did not run')
