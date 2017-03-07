from ctypes import CFUNCTYPE
from ctypes import c_void_p
from llvmlite import ir
import llvmlite.binding as llvm
from my_builtin_functions import define_printd
# from my_builtin_functions import define_prints
from my_visitor import NodeVisitor
from my_ast import Num, Str
from my_grammar import *

RET_VAR = 'ret_var'
INT8 = 'int8'
# TODO: temorarily making Decimal a DoubleType till find (or make) a better representation
type_map = {BOOL: lambda: ir.IntType(1), INT: lambda: ir.IntType(64), INT8: lambda: ir.IntType(8), DEC: ir.DoubleType, FLOAT: ir.FloatType, VOID: ir.VoidType}


class CodeGenerator(NodeVisitor):
	def __init__(self, file_name):
		super().__init__()
		self.file_name = file_name
		self.module = ir.Module()
		func_ty = ir.FunctionType(ir.VoidType(), [])
		func = ir.Function(self.module, func_ty, '__main__')
		bb_entry = func.append_basic_block('entry')
		self.function = func
		self.main_function = func
		self.builder = ir.IRBuilder(bb_entry)
		self.main_builder = self.builder
		self.exit_block = None
		llvm.initialize()
		llvm.initialize_native_target()
		llvm.initialize_native_asmprinter()
		self.target = llvm.Target.from_default_triple()
		self._add_builtins()

	def visit_program(self, node):
		self.visit(node.block)
		self.builder.ret_void()

	@staticmethod
	def visit_num(node):
		return ir.Constant(type_map[node.token.value_type](), node.value)

	def visit_var(self, node):
		return self.load(node.value)

	def visit_binop(self, node):
		op = node.op.value
		left = self.visit(node.left)
		right = self.visit(node.right)
		if op == PLUS:
			return self.builder.add(left, right, 'addtmp')
		elif op == MINUS:
			return self.builder.sub(left, right, 'subtmp')
		elif op == MUL:
			return self.builder.mul(left, right, 'multmp')
		elif op == DIV:
			return self.builder.udiv(left, right, 'divtmp')
		elif op == MOD:
			return self.builder.urem(left, right, 'modtmp')
		elif op in (EQUALS, NOT_EQUALS, LESS_THAN, LESS_THAN_OR_EQUAL_TO, GREATER_THAN, GREATER_THAN_OR_EQUAL_TO):
			cmp = self.builder.icmp_unsigned(op, left, right, 'cmptmp')
			return self.builder.uitofp(cmp, type_map[BOOL](), 'booltmp')
		else:
			raise SyntaxError('Unknown binary operator', node.op)
		# 	elif op == FLOORDIV:
		# 		return left // right
		# 	elif op == POWER:
		# 		return left ** right
		# 	elif op == AND:
		# 		return left and right
		# 	elif op == OR:
		# 		return left or right
		# 	elif op == CAST:
		# 		cast_type = node.right.value
		# 		if cast_type == INT:
		# 			return int(left)
		# 		elif cast_type == DEC:
		# 			return Decimal(left)
		# 		elif cast_type == FLOAT:
		# 			return float(left)
		# 		elif cast_type == COMPLEX:
		# 			return complex(left)
		# 		elif cast_type == STR:
		# 			return str(left)
		# 		elif cast_type == BOOL:
		# 			return bool(left)
		# 		elif cast_type == BYTES:
		# 			return bytes(left)
		# 		elif cast_type == LIST:
		# 			return list(left)
		# 		elif cast_type == TUPLE:
		# 			return tuple(left)
		# 		elif cast_type == DICT:
		# 			return dict(left)
		# 		elif cast_type == ENUM:
		# 			return Enum(left.value, left)
		# 		elif cast_type in (ANY, FUNC, NULL):
		# 			raise TypeError('file={} line={}: Cannot cast to type {}'.format(self.file_name, node.line_num, cast_type))

	def visit_funcdecl(self, node):
		self.start_function(node.name.value, node.return_type, node.parameters)
		for i, arg in enumerate(self.function.args):
			arg.name = list(node.parameters.keys())[i]
			var_addr = self.builder.alloca(arg.type, name=arg.name)
			self.define(arg.name, var_addr)
			self.builder.store(arg, var_addr)
		if self.function.function_type.return_type != type_map[VOID]():
			ret_var_addr = self.builder.alloca(self.function.function_type.return_type, name=RET_VAR)
			self.define(RET_VAR, ret_var_addr)
		self.visit(node.body)
		self.end_function()
		return self.function

	def visit_funccall(self, node):
		return self.call(node.name.value, [self.visit(arg) for arg in node.arguments])

	def visit_compound(self, node):
		ret = None
		for child in node.children:
			temp = self.visit(child)
			if temp:
				ret = temp
		return ret

	def visit_typedeclaration(self, node):
		raise NotImplementedError

	def visit_vardecl(self, node):
		var_addr = self.builder.alloca(type_map[node.type_node.value](), name=node.var_node.value)
		self.define(node.var_node.value, var_addr)
		self.store(self.visit(node.var_node), node.var_node.value)

	def visit_type(self, node):
		raise NotImplementedError

	def visit_noop(self, node):
		pass

	def visit_if(self, node):
		cond_val = self.visit(node.comps.pop(0))
		with self.builder.if_else(cond_val) as (then, otherwise):
			with then:
				self.visit(node.blocks.pop(0))
			with otherwise:
				if node.blocks:
					self.visit(node.blocks.pop(0))

	def visit_else(self, node):
		pass

	def visit_while(self, node):
		raise NotImplementedError

	def visit_for(self, node):
		init_block = self.add_block('for.init')
		test_block = self.add_block('for.cond')
		body_block = self.add_block('for.body')
		end_block = self.add_block('for.end')
		self.branch(init_block)
		self.position_at_end(init_block)
		loop_range = self.visit(node.iterator)
		start = self.const(loop_range[0])
		stop = self.const(loop_range[-1])
		step = self.const(1)
		varname = node.elements[0].value
		self.allocate(start, varname, type_map[INT]())
		self.branch(test_block)
		self.position_at_end(test_block)
		cond = self.builder.icmp_unsigned(LESS_THAN, self.load(varname), stop)
		self.cbranch(cond, body_block, end_block)
		self.position_at_end(body_block)
		self.visit(node.block)
		succ = self.builder.add(step, self.load(varname))
		self.store(varname, succ)
		self.branch(test_block)
		self.position_at_end(end_block)

	def visit_loopblock(self, node):
		for child in node.children:
			temp = self.visit(child)
			if temp == CONTINUE or temp == BREAK:
				return temp

	def visit_switch(self, node):
		raise NotImplementedError

	def visit_case(self, node):
		raise NotImplementedError

	@staticmethod
	def visit_break(_):
		return BREAK

	@staticmethod
	def visit_continue(_):
		return CONTINUE

	@staticmethod
	def visit_pass(_):
		return

	def visit_unaryop(self, node):
		raise NotImplementedError

	def visit_range(self, node):
		left = self.visit(node.left)
		right = self.visit(node.right)
		return range(left.constant, right.constant)

	def visit_assign(self, node):
		self.allocate(self.visit(node.right), node.left.value, type_map[INT]())

	def visit_opassign(self, node):
		raise NotImplementedError

	def visit_anonymousfunc(self, node):
		raise NotImplementedError

	def visit_return(self, node):
		val = self.visit(node.value)
		if val.type != ir.VoidType():
			self.store(RET_VAR, val)
		self.branch(self.exit_block)

	def visit_constant(self, node):
		raise NotImplementedError

	def visit_str(self, node):
		return self.stringz(node.value)

	def visit_collection(self, node):
		raise NotImplementedError

	def visit_hashmap(self, node):
		raise NotImplementedError

	def visit_collectionaccess(self, node):
		raise NotImplementedError

	def visit_print(self, node):
		if isinstance(node.value, Num):
			val = self.visit(node.value)
			if isinstance(val.constant, bytearray):
				chars = val.constant
			else:
				chars = self.stringz(str(val.constant)).constant
			chars.pop(-1)
			for char in chars:
				self.call('print', [ir.Constant(type_map[INT](), char)])
		elif isinstance(node.value, Str):
			val = self.visit(node.value)
			chars = val.constant
			chars.pop(-1)
			for char in chars:
				self.call('print', [ir.Constant(type_map[INT](), char)])
		else:
			self.call('print', [self.visit(node.value)])
		self.call('print', [ir.Constant(type_map[INT](), 10)])

	def start_function(self, name, return_type, parameters):
		self.new_scope()
		func_type = ir.FunctionType(type_map[return_type.value](), [type_map[param.value]() for param in parameters.values()])
		function = ir.Function(self.module, func_type, name)
		self.function = function
		self.new_builder(self.add_block('entry'))
		self.exit_block = self.add_block('exit')

	def end_function(self):
		self.position_at_end(self.exit_block)
		if self.function.function_type.return_type != type_map[VOID]():
			retval = self.builder.load(self.search_scopes(RET_VAR))
			self.builder.ret(retval)
		else:
			self.builder.ret_void()
		self.builder = self.main_builder
		self.function = self.main_function

	def new_builder(self, block):
		self.builder = ir.IRBuilder(block)
		return self.builder

	def add_block(self, name):
		return self.function.append_basic_block(name)

	def position_at_end(self, block):
		self.builder.position_at_end(block)

	def cbranch(self, cond, true_block, false_block):
		self.builder.cbranch(cond, true_block, false_block)

	def branch(self, block):
		self.builder.branch(block)

	def const(self, val):
		if isinstance(val, int):
			return ir.Constant(type_map[INT](), val)
		elif isinstance(val, float):
			return ir.Constant(type_map[DEC], val)
		elif isinstance(val, bool):
			return ir.Constant(type_map[INT](), int(val))
		elif isinstance(val, str):
			return self.stringz(val)
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
		builder = ir.IRBuilder()
		builder.position_at_start(self.builder.function.entry_basic_block)
		return builder.alloca(typ, size=None, name=name)

	def _add_builtins(self):
		putchar_ty = ir.FunctionType(type_map[INT](), [type_map[INT]()])
		putchar = ir.Function(self.module, putchar_ty, 'putchar')

		define_printd(ir, self.module)
		# define_prints(ir, self.module)

		print_ty = ir.FunctionType(type_map[VOID](), [type_map[INT]()])
		print_func = ir.Function(self.module, print_ty, 'print')
		irbuilder = ir.IRBuilder(print_func.append_basic_block('entry'))
		irbuilder.call(putchar, [print_func.args[0]])
		irbuilder.ret_void()

	@staticmethod
	def stringz_type(string):
		return ir.ArrayType(type_map[INT](), len(string) + 1)

	@staticmethod
	def stringz_pntr_type(string):
		return ir.ArrayType(type_map[INT]().as_pointer(), len(string) + 1).as_pointer()

	@staticmethod
	def stringz(string):
		n = len(string) + 1
		buf = bytearray((' ' * n).encode('ascii'))
		buf[-1] = 0
		buf[:-1] = string.encode('utf-8')
		return ir.Constant(ir.ArrayType(type_map[INT](), n), buf)

	@staticmethod
	def stringz_pntr(string):
		n = len(string) + 1
		buf = bytearray((' ' * n).encode('ascii'))
		buf[-1] = 0
		buf[:-1] = string.encode('utf-8')
		return ir.Constant(ir.ArrayType(type_map[INT]().as_pointer(), n).as_pointer(), buf)

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
			fptr = CFUNCTYPE(c_void_p)(ee.get_function_address('__main__'))
			fptr()

if __name__ == '__main__':
	from my_lexer import Lexer
	from my_parser import Parser
	from my_symbol_table_builder import SymbolTableBuilder
	file = 'math.my'
	code = open(file).read()
	lexer = Lexer(code, file)
	parser = Parser(lexer)
	t = parser.parse()
	symtab_builder = SymbolTableBuilder(parser.file_name)
	symtab_builder.build(t)
	if not symtab_builder.warnings:
		generator = CodeGenerator(parser.file_name)
		generator.generate_code(t)
		generator.evaluate(True, True)
	else:
		print('Did not run')