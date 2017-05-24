from llvmlite import ir


def create_dynamic_array(ir_module, array_type):
	builder = ir.IRBuilder()
	array_size = ir.Constant(ir.IntType(64), 10)
	dyn_array = ir.LiteralStructType((ir.ArrayType(array_type, array_size), array_size))