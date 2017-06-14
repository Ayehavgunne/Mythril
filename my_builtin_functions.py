from llvmlite import ir
from compiler import type_map
from my_grammar import *

ARRAY_INITIAL_CAPACITY = 100


def define_printd(the_module):  # TODO: Change to an Int -> Str function
	# function start
	func_type = ir.FunctionType(type_map[VOID], [type_map[INT]])
	func = ir.Function(the_module, func_type, 'printd')
	entry_block = func.append_basic_block('entry')
	builder = ir.IRBuilder(entry_block)
	exit_block = func.append_basic_block('exit')
	n_addr = builder.alloca(type_map[INT], name='n')
	builder.store(func.args[0], n_addr)
	x_addr = builder.alloca(type_map[INT32], name='x')

	# function body
	int_zero = ir.Constant(type_map[INT32], 0)
	int_one = ir.Constant(type_map[INT32], 1)
	int_two = ir.Constant(type_map[INT32], 2)
	int_three = ir.Constant(type_map[INT32], 3)
	int_four = ir.Constant(type_map[INT32], 4)
	int_five = ir.Constant(type_map[INT32], 5)
	int_six = ir.Constant(type_map[INT32], 6)
	int_seven = ir.Constant(type_map[INT32], 7)
	int_eight = ir.Constant(type_map[INT32], 8)
	int_nine = ir.Constant(type_map[INT32], 9)
	int_ten = ir.Constant(type_map[INT32], 10)
	int_fourtyeight = ir.Constant(type_map[INT32], 48)
	int_fourtynine = ir.Constant(type_map[INT32], 49)
	int_fifty = ir.Constant(type_map[INT32], 50)
	int_fiftyone = ir.Constant(type_map[INT32], 51)
	int_fiftytwo = ir.Constant(type_map[INT32], 52)
	int_fiftythree = ir.Constant(type_map[INT32], 53)
	int_fiftyfour = ir.Constant(type_map[INT32], 54)
	int_fiftyfive = ir.Constant(type_map[INT32], 55)
	int_fiftysix = ir.Constant(type_map[INT32], 56)
	int_fiftyseven = ir.Constant(type_map[INT32], 57)

	div_ten = builder.udiv(builder.load(n_addr), builder.zext(int_ten, type_map[INT]), 'divten')
	greater_than_zero = builder.icmp_unsigned('>', div_ten, int_zero, 'greaterthanzero')
	mod_ten = builder.urem(builder.trunc(builder.load(n_addr), type_map[INT32]), int_ten, 'modten')
	builder.store(mod_ten, x_addr)

	with builder.if_then(greater_than_zero):
		builder.call(the_module.get_global('printd'), [div_ten])

	case_0 = func.append_basic_block('case')
	case_1 = func.append_basic_block('case')
	case_2 = func.append_basic_block('case')
	case_3 = func.append_basic_block('case')
	case_4 = func.append_basic_block('case')
	case_5 = func.append_basic_block('case')
	case_6 = func.append_basic_block('case')
	case_7 = func.append_basic_block('case')
	case_8 = func.append_basic_block('case')
	case_9 = func.append_basic_block('case')
	default = func.append_basic_block('default')

	switch = builder.switch(builder.load(x_addr), default)
	switch.add_case(int_zero, case_0)
	switch.add_case(int_one, case_1)
	switch.add_case(int_two, case_2)
	switch.add_case(int_three, case_3)
	switch.add_case(int_four, case_4)
	switch.add_case(int_five, case_5)
	switch.add_case(int_six, case_6)
	switch.add_case(int_seven, case_7)
	switch.add_case(int_eight, case_8)
	switch.add_case(int_nine, case_9)

	builder.position_at_start(case_0)
	builder.call(the_module.get_global('putchar'), [int_fourtyeight])
	builder.branch(exit_block)

	builder.position_at_start(case_1)
	builder.call(the_module.get_global('putchar'), [int_fourtynine])
	builder.branch(exit_block)

	builder.position_at_start(case_2)
	builder.call(the_module.get_global('putchar'), [int_fifty])
	builder.branch(exit_block)

	builder.position_at_start(case_3)
	builder.call(the_module.get_global('putchar'), [int_fiftyone])
	builder.branch(exit_block)

	builder.position_at_start(case_4)
	builder.call(the_module.get_global('putchar'), [int_fiftytwo])
	builder.branch(exit_block)

	builder.position_at_start(case_5)
	builder.call(the_module.get_global('putchar'), [int_fiftythree])
	builder.branch(exit_block)

	builder.position_at_start(case_6)
	builder.call(the_module.get_global('putchar'), [int_fiftyfour])
	builder.branch(exit_block)

	builder.position_at_start(case_7)
	builder.call(the_module.get_global('putchar'), [int_fiftyfive])
	builder.branch(exit_block)

	builder.position_at_start(case_8)
	builder.call(the_module.get_global('putchar'), [int_fiftysix])
	builder.branch(exit_block)

	builder.position_at_start(case_9)
	builder.call(the_module.get_global('putchar'), [int_fiftyseven])
	builder.branch(exit_block)

	builder.position_at_start(default)
	builder.branch(exit_block)

	# function close
	builder.position_at_end(exit_block)
	builder.ret_void()


def define_int_to_str(the_module):
	# function start
	func_type = ir.FunctionType(ir.VoidType(), [type_map[INT]])
	func = ir.Function(the_module, func_type, 'int_to_str')
	entry_block = func.append_basic_block('entry')
	builder = ir.IRBuilder(entry_block)
	exit_block = func.append_basic_block('exit')
	n_addr = builder.alloca(type_map[INT], name='n')
	builder.store(func.args[0], n_addr)
	x_addr = builder.alloca(type_map[INT32], name='x')

	# function body
	int_zero = ir.Constant(type_map[INT32], 0)
	int_one = ir.Constant(type_map[INT32], 1)
	int_two = ir.Constant(type_map[INT32], 2)
	int_three = ir.Constant(type_map[INT32], 3)
	int_four = ir.Constant(type_map[INT32], 4)
	int_five = ir.Constant(type_map[INT32], 5)
	int_six = ir.Constant(type_map[INT32], 6)
	int_seven = ir.Constant(type_map[INT32], 7)
	int_eight = ir.Constant(type_map[INT32], 8)
	int_nine = ir.Constant(type_map[INT32], 9)
	int_ten = ir.Constant(type_map[INT32], 10)
	int_fourtyeight = ir.Constant(type_map[INT32], 48)
	int_fourtynine = ir.Constant(type_map[INT32], 49)
	int_fifty = ir.Constant(type_map[INT32], 50)
	int_fiftyone = ir.Constant(type_map[INT32], 51)
	int_fiftytwo = ir.Constant(type_map[INT32], 52)
	int_fiftythree = ir.Constant(type_map[INT32], 53)
	int_fiftyfour = ir.Constant(type_map[INT32], 54)
	int_fiftyfive = ir.Constant(type_map[INT32], 55)
	int_fiftysix = ir.Constant(type_map[INT32], 56)
	int_fiftyseven = ir.Constant(type_map[INT32], 57)

	div_ten = builder.udiv(builder.load(n_addr), builder.zext(int_ten, type_map[INT]), 'divten')
	greater_than_zero = builder.icmp_unsigned('>', div_ten, int_zero, 'greaterthanzero')
	mod_ten = builder.urem(builder.trunc(builder.load(n_addr), type_map[INT32]), int_ten, 'modten')
	builder.store(mod_ten, x_addr)

	with builder.if_then(greater_than_zero):
		builder.call(the_module.get_global('int_to_str'), [div_ten])

	case_0 = func.append_basic_block('case')
	case_1 = func.append_basic_block('case')
	case_2 = func.append_basic_block('case')
	case_3 = func.append_basic_block('case')
	case_4 = func.append_basic_block('case')
	case_5 = func.append_basic_block('case')
	case_6 = func.append_basic_block('case')
	case_7 = func.append_basic_block('case')
	case_8 = func.append_basic_block('case')
	case_9 = func.append_basic_block('case')
	default = func.append_basic_block('default')

	switch = builder.switch(builder.load(x_addr), default)
	switch.add_case(int_zero, case_0)
	switch.add_case(int_one, case_1)
	switch.add_case(int_two, case_2)
	switch.add_case(int_three, case_3)
	switch.add_case(int_four, case_4)
	switch.add_case(int_five, case_5)
	switch.add_case(int_six, case_6)
	switch.add_case(int_seven, case_7)
	switch.add_case(int_eight, case_8)
	switch.add_case(int_nine, case_9)

	builder.position_at_start(case_0)
	builder.call(the_module.get_global('putchar'), [int_fourtyeight])
	builder.branch(exit_block)

	builder.position_at_start(case_1)
	builder.call(the_module.get_global('putchar'), [int_fourtynine])
	builder.branch(exit_block)

	builder.position_at_start(case_2)
	builder.call(the_module.get_global('putchar'), [int_fifty])
	builder.branch(exit_block)

	builder.position_at_start(case_3)
	builder.call(the_module.get_global('putchar'), [int_fiftyone])
	builder.branch(exit_block)

	builder.position_at_start(case_4)
	builder.call(the_module.get_global('putchar'), [int_fiftytwo])
	builder.branch(exit_block)

	builder.position_at_start(case_5)
	builder.call(the_module.get_global('putchar'), [int_fiftythree])
	builder.branch(exit_block)

	builder.position_at_start(case_6)
	builder.call(the_module.get_global('putchar'), [int_fiftyfour])
	builder.branch(exit_block)

	builder.position_at_start(case_7)
	builder.call(the_module.get_global('putchar'), [int_fiftyfive])
	builder.branch(exit_block)

	builder.position_at_start(case_8)
	builder.call(the_module.get_global('putchar'), [int_fiftysix])
	builder.branch(exit_block)

	builder.position_at_start(case_9)
	builder.call(the_module.get_global('putchar'), [int_fiftyseven])
	builder.branch(exit_block)

	builder.position_at_start(default)
	builder.branch(exit_block)

	# function close
	builder.position_at_end(exit_block)
	builder.ret_void()


def define_printb(the_module):
	# function start
	func_type = ir.FunctionType(type_map[VOID], [type_map[BOOL]])
	func = ir.Function(the_module, func_type, 'printb')
	entry_block = func.append_basic_block('entry')
	builder = ir.IRBuilder(entry_block)
	exit_block = func.append_basic_block('exit')

	# function body
	equalszero = builder.icmp_unsigned('==', func.args[0], ir.Constant(type_map[BOOL], 0), 'equalszero')

	with builder.if_else(equalszero) as (then, otherwise):
		with then:
			builder.call(the_module.get_global('putchar'), [ir.Constant(type_map[INT32], 102)])
			builder.call(the_module.get_global('putchar'), [ir.Constant(type_map[INT32], 97)])
			builder.call(the_module.get_global('putchar'), [ir.Constant(type_map[INT32], 108)])
			builder.call(the_module.get_global('putchar'), [ir.Constant(type_map[INT32], 115)])
			builder.call(the_module.get_global('putchar'), [ir.Constant(type_map[INT32], 101)])
			builder.branch(exit_block)
		with otherwise:
			builder.call(the_module.get_global('putchar'), [ir.Constant(type_map[INT32], 116)])
			builder.call(the_module.get_global('putchar'), [ir.Constant(type_map[INT32], 114)])
			builder.call(the_module.get_global('putchar'), [ir.Constant(type_map[INT32], 117)])
			builder.call(the_module.get_global('putchar'), [ir.Constant(type_map[INT32], 101)])
			builder.branch(exit_block)

	builder.branch(exit_block)

	# function close
	builder.position_at_end(exit_block)
	builder.ret_void()


def define_dynamic_array(compiler):
	# define a struct dynamic_array
	# 0: int size
	# 1: int capacity
	# 2: int *data  TODO: make this a void pointer to allow any kind of data
	dyn_array_struct = ir.LiteralStructType([type_map[INT], type_map[INT], type_map[INT].as_pointer()])
	compiler.define('Dynamic_Array', dyn_array_struct)
	dyn_array_struct_ptr = dyn_array_struct.as_pointer()

	# function init array start
	dyn_array_init_type = ir.FunctionType(type_map[VOID], [dyn_array_struct_ptr])
	dyn_array_init = ir.Function(compiler.module, dyn_array_init_type, 'dyn_array_init')
	dyn_array_entry = dyn_array_init.append_basic_block('entry')
	builder = ir.IRBuilder(dyn_array_entry)
	dyn_array_exit = dyn_array_init.append_basic_block('exit')
	builder.position_at_end(dyn_array_entry)
	array_ptr = builder.alloca(dyn_array_struct_ptr, name='array_ptr')
	builder.store(dyn_array_init.args[0], array_ptr)

	zero = ir.Constant(type_map[INT], 0)
	array_init_capacity = ir.Constant(type_map[INT], ARRAY_INITIAL_CAPACITY)

	zero_32 = ir.Constant(type_map[INT32], 0)
	one_32 = ir.Constant(type_map[INT32], 1)
	two_32 = ir.Constant(type_map[INT32], 2)

	# function init array body
	size_ptr = builder.gep(builder.load(array_ptr), [zero_32, zero_32], inbounds=True)
	builder.store(zero, size_ptr)

	capacity_ptr = builder.gep(builder.load(array_ptr), [zero_32, one_32], inbounds=True)
	builder.store(array_init_capacity, capacity_ptr)

	data_ptr = builder.gep(builder.load(array_ptr), [zero_32, two_32], inbounds=True)
	mem_alloc = builder.call(compiler.module.get_global('malloc'), [builder.load(capacity_ptr)])
	mem_alloc = builder.bitcast(mem_alloc, type_map[INT].as_pointer())
	builder.store(mem_alloc, data_ptr)

	builder.branch(dyn_array_exit)

	# function close
	builder.position_at_end(dyn_array_exit)
	builder.ret_void()
