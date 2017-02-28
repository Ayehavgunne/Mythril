# from llvmlite import ir
# from my_grammar import *
#
# # TODO: temorarily making Decimal a DoubleType till find (or make) a better representation
# type_map = {INT: ir.IntType, DEC: ir.DoubleType, FLOAT: ir.FloatType}
#
#
# class CodegenError(BaseException):
# 	pass
#
#
# class LLVMCodeGenerator(object):
# 	def __init__(self):
# 		self.module = ir.Module()
# 		self.builder = None
# 		self.func_symtab = {}
#
# 	def generate_code(self, node):
# 		return self.codegen(node)
#
# 	def codegen(self, node):
# 		method = 'codegen_' + node.__class__.__name__.lower()
# 		return getattr(self, method)(node)
#
# 	@staticmethod
# 	def codegen_num(node):
# 		return ir.Constant(type_map[node.type](), node.value)
#
# 	def codegen_binop(self, node):
# 		left = self.codegen(node.left)
# 		right = self.codegen(node.right)
#
# 		if node.op == '+':
# 			return self.builder.fadd(left, right, 'addtmp')
# 		elif node.op == '-':
# 			return self.builder.fsub(left, right, 'subtmp')
# 		elif node.op == '*':
# 			return self.builder.fmul(left, right, 'multmp')
# 		elif node.op == '<':
# 			cmp = self.builder.fcmp_unordered('<', left, right, 'cmptmp')
# 			return self.builder.uitofp(cmp, ir.DoubleType(), 'booltmp')
# 		else:
# 			raise CodegenError('Unknown binary operator', node.op)

from llvmlite import ir
import llvmlite.binding as llvm
from ctypes import CFUNCTYPE, c_int64

# Create a 64bit wide int type
int_type = ir.IntType(64)
# Create a int -> int function
fn_int_to_int_type = ir.FunctionType(int_type, [int_type])

module = ir.Module(name='my_fibonacci_example')

# Create the Fibonacci function and block
fn_fib = ir.Function(module, fn_int_to_int_type, name='fn_fib')
fn_fib_block = fn_fib.append_basic_block(name='fn_fib_entry')

# Create the builder for the fibonacci code block
builder = ir.IRBuilder(fn_fib_block)

# Access the function argument
fn_fib_n, = fn_fib.args
# Const values for int(1) and int(2)
const_0 = ir.Constant(int_type, 0)
const_1 = ir.Constant(int_type, 1)
const_2 = ir.Constant(int_type, 2)

# Create inequality comparison instruction
fn_fib_n_lteq_0 = builder.icmp_signed(cmpop='==', lhs=fn_fib_n, rhs=const_0)
fn_fib_n_lteq_1 = builder.icmp_signed(cmpop='==', lhs=fn_fib_n, rhs=const_1)

with builder.if_then(fn_fib_n_lteq_0):
	# Simply return 0 if n == 0
	builder.ret(const_0)

with builder.if_then(fn_fib_n_lteq_1):
	# Simply return 1 if n == 1
	builder.ret(const_1)

# This is where the recursive case is created
# _temp1= n - 1
fn_fib_n_minus_1 = builder.sub(fn_fib_n, const_1)
# _temp2 = n - 2
fn_fib_n_minus_2 = builder.sub(fn_fib_n, const_2)

# Call fibonacci( n - 1 )
# arguments in a list, in positional order
call_fn_fib_n_minus_1 = builder.call(fn_fib, [fn_fib_n_minus_1])
# Call fibonacci( n - 2 )
call_fn_fib_n_minus_2 = builder.call(fn_fib, [fn_fib_n_minus_2])

fn_fib_rec_res = builder.add(call_fn_fib_n_minus_1, call_fn_fib_n_minus_2)

builder.ret(fn_fib_rec_res)

# print(module)

llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()

target = llvm.Target.from_default_triple()
target_machine = target.create_target_machine()

backing_mod = llvm.parse_assembly('')
engine = llvm.create_mcjit_compiler(backing_mod, target_machine)

mod = llvm.parse_assembly(str(module))
mod.verify()

engine.add_module(mod)
engine.finalize_object()

func_ptr = engine.get_function_address('fn_fib')

c_fn_fib = CFUNCTYPE(c_int64, c_int64)(func_ptr)

print(c_fn_fib(50))

# from datetime import datetime
#
# start = datetime.now()
# y = 40
# for x in range(y + 1):
# 	print('{} {}'.format(x, c_fn_fib(x)))
#
# print(datetime.now() - start)
