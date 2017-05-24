from llvmlite import ir
import llvmlite.binding as llvm
import ctypes

# calls a python method from within llvm ir

i128_ty = ir.IntType(128)
cb_func_ty = ir.FunctionType(i128_ty, [i128_ty, i128_ty])
cb_func_ptr_ty = cb_func_ty.as_pointer()


def create_addrcaller(m, addr):
	# define i64 @addrcaller(i64 %a, i64 %b) #0 {
	# entry:
	#   %f = inttoptr i64% ADDR to i64 (i64, i64)*
	#   %call = tail call i64 %f(i64 %a, i64 %b)
	#   ret i64 %call
	# }
	addrcaller_func_ty = ir.FunctionType(i128_ty, [i128_ty, i128_ty])
	addrcaller_func = ir.Function(m, addrcaller_func_ty, name='addrcaller')
	a = addrcaller_func.args[0]
	a.name = 'a'
	b = addrcaller_func.args[1]
	b.name = 'b'
	irbuilder = ir.IRBuilder(addrcaller_func.append_basic_block('entry'))
	f = irbuilder.inttoptr(ir.Constant(i128_ty, addr), cb_func_ptr_ty, name='f')
	call = irbuilder.call(f, [a, b])
	irbuilder.ret(call)


def myfunc(a, b):
	print('I was called with {0} and {1}'.format(a, b))
	return a * b


def main():
	cbfuncty = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int)

	cb_myfunc = cbfuncty(myfunc)
	cb_addr = ctypes.cast(cb_myfunc, ctypes.c_void_p).value
	print('Callback address is 0x{0:x}'.format(cb_addr))

	ir_module = ir.Module()
	create_addrcaller(ir_module, cb_addr)
	print(ir_module)

	llvm.initialize()
	llvm.initialize_native_target()
	llvm.initialize_native_asmprinter()

	llvm_module = llvm.parse_assembly(str(ir_module))

	tm = llvm.Target.from_default_triple().create_target_machine()

	with llvm.create_mcjit_compiler(llvm_module, tm) as ee:
		ee.finalize_object()
		print('Calling "addrcaller"')
		addrcaller = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int)(
			ee.get_pointer_to_function(llvm_module.get_function('addrcaller')))
		res = addrcaller(10555, 23556)
		print('  The result is', res)

if __name__ == '__main__':
	main()
