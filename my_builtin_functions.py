from llvmlite import ir
from compiler import type_map
from my_grammar import *

ARRAY_INITIAL_CAPACITY = 100
zero = ir.Constant(type_map[INT], 0)
one = ir.Constant(type_map[INT], 1)
two = ir.Constant(type_map[INT], 2)
eight = ir.Constant(type_map[INT], 8)
zero_32 = ir.Constant(type_map[INT32], 0)
one_32 = ir.Constant(type_map[INT32], 1)
two_32 = ir.Constant(type_map[INT32], 2)


def define_dynamic_array(compiler):
	# define a struct dynamic_array
	# 0: int size
	# 1: int capacity
	# 2: int *data  TODO: make this a void pointer to allow any kind of data
	dyn_array_struct = ir.LiteralStructType([type_map[INT], type_map[INT], type_map[INT].as_pointer()])
	compiler.define('Dynamic_Array', dyn_array_struct)
	dyn_array_struct_ptr = dyn_array_struct.as_pointer()

	dynamic_array_init(compiler, dyn_array_struct_ptr)
	dynamic_array_double_if_full(compiler, dyn_array_struct_ptr)
	dynamic_array_append(compiler, dyn_array_struct_ptr)
	dynamic_array_get(compiler, dyn_array_struct_ptr)
	dynamic_array_set(compiler, dyn_array_struct_ptr)
	dynamic_array_length(compiler, dyn_array_struct_ptr)
	define_create_range(compiler, dyn_array_struct_ptr)


def define_create_range(compiler, dyn_array_struct_ptr):
	create_range_type = ir.FunctionType(type_map[VOID], [dyn_array_struct_ptr, type_map[INT], type_map[INT]])
	create_range = ir.Function(compiler.module, create_range_type, 'create_range')
	create_range_entry = create_range.append_basic_block('entry')
	builder = ir.IRBuilder(create_range_entry)
	create_range_test = create_range.append_basic_block('test')
	create_range_body = create_range.append_basic_block('body')
	create_range_exit = create_range.append_basic_block('exit')

	builder.position_at_end(create_range_entry)
	array_ptr = builder.alloca(dyn_array_struct_ptr, name='array_ptr')
	builder.store(create_range.args[0], array_ptr)
	start_ptr = builder.alloca(type_map[INT], name='start_ptr')
	builder.store(create_range.args[1], start_ptr)
	stop_ptr = builder.alloca(type_map[INT], name='stop_ptr')
	builder.store(create_range.args[2], stop_ptr)

	num_ptr = builder.alloca(type_map[INT], name='num')
	builder.store(builder.load(start_ptr), num_ptr)
	builder.branch(create_range_test)

	builder.position_at_end(create_range_test)
	cond = builder.icmp_unsigned(LESS_THAN, builder.load(num_ptr), builder.load(stop_ptr))
	builder.cbranch(cond, create_range_body, create_range_exit)

	builder.position_at_end(create_range_body)
	builder.call(compiler.module.get_global('dyn_array_append'), [builder.load(array_ptr), builder.load(num_ptr)])
	builder.store(builder.add(one, builder.load(num_ptr)), num_ptr)

	builder.branch(create_range_test)

	# CLOSE
	builder.position_at_end(create_range_exit)
	builder.ret_void()


def define_printd(mod):  # TODO: Change to an Int -> Str function
	# function start
	func_type = ir.FunctionType(type_map[VOID], [type_map[INT]])
	func = ir.Function(mod, func_type, 'printd')
	entry_block = func.append_basic_block('entry')
	builder = ir.IRBuilder(entry_block)
	exit_block = func.append_basic_block('exit')
	n_addr = builder.alloca(type_map[INT], name='n')
	builder.store(func.args[0], n_addr)
	x_addr = builder.alloca(type_map[INT], name='x')

	# function body
	int_zero = ir.Constant(type_map[INT], 0)
	int_one = ir.Constant(type_map[INT], 1)
	int_two = ir.Constant(type_map[INT], 2)
	int_three = ir.Constant(type_map[INT], 3)
	int_four = ir.Constant(type_map[INT], 4)
	int_five = ir.Constant(type_map[INT], 5)
	int_six = ir.Constant(type_map[INT], 6)
	int_seven = ir.Constant(type_map[INT], 7)
	int_eight = ir.Constant(type_map[INT], 8)
	int_nine = ir.Constant(type_map[INT], 9)
	int_ten = ir.Constant(type_map[INT], 10)
	int_fourtyeight = ir.Constant(type_map[INT], 48)
	int_fourtynine = ir.Constant(type_map[INT], 49)
	int_fifty = ir.Constant(type_map[INT], 50)
	int_fiftyone = ir.Constant(type_map[INT], 51)
	int_fiftytwo = ir.Constant(type_map[INT], 52)
	int_fiftythree = ir.Constant(type_map[INT], 53)
	int_fiftyfour = ir.Constant(type_map[INT], 54)
	int_fiftyfive = ir.Constant(type_map[INT], 55)
	int_fiftysix = ir.Constant(type_map[INT], 56)
	int_fiftyseven = ir.Constant(type_map[INT], 57)

	div_ten = builder.udiv(builder.load(n_addr), int_ten, 'divten')
	greater_than_zero = builder.icmp_unsigned('>', div_ten, int_zero, 'greaterthanzero')
	mod_ten = builder.urem(builder.trunc(builder.load(n_addr), type_map[INT]), int_ten, 'modten')
	builder.store(mod_ten, x_addr)

	with builder.if_then(greater_than_zero):
		builder.call(mod.get_global('printd'), [div_ten])

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
	builder.call(mod.get_global('putchar'), [int_fourtyeight])
	builder.branch(exit_block)

	builder.position_at_start(case_1)
	builder.call(mod.get_global('putchar'), [int_fourtynine])
	builder.branch(exit_block)

	builder.position_at_start(case_2)
	builder.call(mod.get_global('putchar'), [int_fifty])
	builder.branch(exit_block)

	builder.position_at_start(case_3)
	builder.call(mod.get_global('putchar'), [int_fiftyone])
	builder.branch(exit_block)

	builder.position_at_start(case_4)
	builder.call(mod.get_global('putchar'), [int_fiftytwo])
	builder.branch(exit_block)

	builder.position_at_start(case_5)
	builder.call(mod.get_global('putchar'), [int_fiftythree])
	builder.branch(exit_block)

	builder.position_at_start(case_6)
	builder.call(mod.get_global('putchar'), [int_fiftyfour])
	builder.branch(exit_block)

	builder.position_at_start(case_7)
	builder.call(mod.get_global('putchar'), [int_fiftyfive])
	builder.branch(exit_block)

	builder.position_at_start(case_8)
	builder.call(mod.get_global('putchar'), [int_fiftysix])
	builder.branch(exit_block)

	builder.position_at_start(case_9)
	builder.call(mod.get_global('putchar'), [int_fiftyseven])
	builder.branch(exit_block)

	builder.position_at_start(default)
	builder.branch(exit_block)

	# function close
	builder.position_at_end(exit_block)
	builder.ret_void()


def define_int_to_str(mod):
	# function start
	func_type = ir.FunctionType(type_map[VOID], [type_map[INT]])
	func = ir.Function(mod, func_type, 'int_to_str')
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
		builder.call(mod.get_global('int_to_str'), [div_ten])

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
	builder.call(mod.get_global('putchar'), [int_fourtyeight])
	builder.branch(exit_block)

	builder.position_at_start(case_1)
	builder.call(mod.get_global('putchar'), [int_fourtynine])
	builder.branch(exit_block)

	builder.position_at_start(case_2)
	builder.call(mod.get_global('putchar'), [int_fifty])
	builder.branch(exit_block)

	builder.position_at_start(case_3)
	builder.call(mod.get_global('putchar'), [int_fiftyone])
	builder.branch(exit_block)

	builder.position_at_start(case_4)
	builder.call(mod.get_global('putchar'), [int_fiftytwo])
	builder.branch(exit_block)

	builder.position_at_start(case_5)
	builder.call(mod.get_global('putchar'), [int_fiftythree])
	builder.branch(exit_block)

	builder.position_at_start(case_6)
	builder.call(mod.get_global('putchar'), [int_fiftyfour])
	builder.branch(exit_block)

	builder.position_at_start(case_7)
	builder.call(mod.get_global('putchar'), [int_fiftyfive])
	builder.branch(exit_block)

	builder.position_at_start(case_8)
	builder.call(mod.get_global('putchar'), [int_fiftysix])
	builder.branch(exit_block)

	builder.position_at_start(case_9)
	builder.call(mod.get_global('putchar'), [int_fiftyseven])
	builder.branch(exit_block)

	builder.position_at_start(default)
	builder.branch(exit_block)

	# function close
	builder.position_at_end(exit_block)
	builder.ret_void()


def define_printb(mod):
	# function start
	func_type = ir.FunctionType(type_map[VOID], [type_map[BOOL]])
	func = ir.Function(mod, func_type, 'printb')
	entry_block = func.append_basic_block('entry')
	builder = ir.IRBuilder(entry_block)
	exit_block = func.append_basic_block('exit')

	# function body
	equalszero = builder.icmp_unsigned('==', func.args[0], ir.Constant(type_map[BOOL], 0), 'equalszero')

	with builder.if_else(equalszero) as (then, otherwise):
		with then:
			builder.call(mod.get_global('putchar'), [ir.Constant(type_map[INT], 102)])
			builder.call(mod.get_global('putchar'), [ir.Constant(type_map[INT], 97)])
			builder.call(mod.get_global('putchar'), [ir.Constant(type_map[INT], 108)])
			builder.call(mod.get_global('putchar'), [ir.Constant(type_map[INT], 115)])
			builder.call(mod.get_global('putchar'), [ir.Constant(type_map[INT], 101)])
			builder.branch(exit_block)
		with otherwise:
			builder.call(mod.get_global('putchar'), [ir.Constant(type_map[INT], 116)])
			builder.call(mod.get_global('putchar'), [ir.Constant(type_map[INT], 114)])
			builder.call(mod.get_global('putchar'), [ir.Constant(type_map[INT], 117)])
			builder.call(mod.get_global('putchar'), [ir.Constant(type_map[INT], 101)])
			builder.branch(exit_block)

	builder.branch(exit_block)

	# function close
	builder.position_at_end(exit_block)
	builder.ret_void()


def dynamic_array_init(compiler, dyn_array_struct_ptr):
	# START
	dyn_array_init_type = ir.FunctionType(type_map[VOID], [dyn_array_struct_ptr])
	dyn_array_init = ir.Function(compiler.module, dyn_array_init_type, 'dyn_array_init')
	dyn_array_init_entry = dyn_array_init.append_basic_block('entry')
	builder = ir.IRBuilder(dyn_array_init_entry)
	dyn_array_init_exit = dyn_array_init.append_basic_block('exit')
	builder.position_at_end(dyn_array_init_entry)
	array_ptr = builder.alloca(dyn_array_struct_ptr, name='array_ptr')
	builder.store(dyn_array_init.args[0], array_ptr)

	array_init_capacity = ir.Constant(type_map[INT], ARRAY_INITIAL_CAPACITY)

	# BODY
	size_ptr = builder.gep(builder.load(array_ptr), [zero_32, zero_32], inbounds=True)
	builder.store(zero, size_ptr)

	capacity_ptr = builder.gep(builder.load(array_ptr), [zero_32, one_32], inbounds=True)
	builder.store(array_init_capacity, capacity_ptr)

	data_ptr = builder.gep(builder.load(array_ptr), [zero_32, two_32], inbounds=True)
	size_of = builder.mul(builder.load(capacity_ptr), eight)
	mem_alloc = builder.call(compiler.module.get_global('malloc'), [size_of])
	mem_alloc = builder.bitcast(mem_alloc, type_map[INT].as_pointer())
	builder.store(mem_alloc, data_ptr)

	builder.branch(dyn_array_init_exit)

	# CLOSE
	builder.position_at_end(dyn_array_init_exit)
	builder.ret_void()


def dynamic_array_double_if_full(compiler, dyn_array_struct_ptr):
	# function 'array double capacity if full' START
	dyn_array_double_capacity_if_full_type = ir.FunctionType(type_map[VOID], [dyn_array_struct_ptr])
	dyn_array_double_capacity_if_full = ir.Function(compiler.module, dyn_array_double_capacity_if_full_type, 'dyn_array_double_capacity_if_full')
	dyn_array_double_capacity_if_full_entry = dyn_array_double_capacity_if_full.append_basic_block('entry')
	builder = ir.IRBuilder(dyn_array_double_capacity_if_full_entry)
	dyn_array_double_capacity_if_full_exit = dyn_array_double_capacity_if_full.append_basic_block('exit')
	dyn_array_double_capacity_block = dyn_array_double_capacity_if_full.append_basic_block('double_capacity')
	builder.position_at_end(dyn_array_double_capacity_if_full_entry)
	array_ptr = builder.alloca(dyn_array_struct_ptr, name='array_ptr')
	builder.store(dyn_array_double_capacity_if_full.args[0], array_ptr)

	# function 'array double capacity if full' BODY
	size_ptr = builder.gep(builder.load(array_ptr), [zero_32, zero_32], inbounds=True)
	size_val = builder.load(size_ptr)

	capacity_ptr = builder.gep(builder.load(array_ptr), [zero_32, one_32], inbounds=True)
	capacity_val = builder.load(capacity_ptr)

	data_ptr = builder.gep(builder.load(array_ptr), [zero_32, two_32], inbounds=True)

	compare_size_to_capactiy = builder.icmp_unsigned('>=', size_val, capacity_val)

	builder.cbranch(compare_size_to_capactiy, dyn_array_double_capacity_block, dyn_array_double_capacity_if_full_exit)

	builder.position_at_end(dyn_array_double_capacity_block)

	capacity_val = builder.mul(capacity_val, two)
	builder.store(capacity_val, capacity_ptr)
	capacity_val = builder.load(capacity_ptr)
	size_of = builder.mul(capacity_val, eight)

	data_ptr_8 = builder.bitcast(builder.load(data_ptr), type_map[INT8].as_pointer())
	re_alloc = builder.call(compiler.module.get_global('realloc'), [data_ptr_8, size_of])
	re_alloc = builder.bitcast(re_alloc, type_map[INT].as_pointer())
	builder.store(re_alloc, data_ptr)

	builder.branch(dyn_array_double_capacity_if_full_exit)

	# function 'array double capacity if full' CLOSE
	builder.position_at_end(dyn_array_double_capacity_if_full_exit)
	builder.ret_void()


def dynamic_array_append(compiler, dyn_array_struct_ptr):
	# START
	dyn_array_append_type = ir.FunctionType(type_map[VOID], [dyn_array_struct_ptr, type_map[INT]])
	dyn_array_append = ir.Function(compiler.module, dyn_array_append_type, 'dyn_array_append')
	dyn_array_append_entry = dyn_array_append.append_basic_block('entry')
	builder = ir.IRBuilder(dyn_array_append_entry)
	dyn_array_append_exit = dyn_array_append.append_basic_block('exit')
	builder.position_at_end(dyn_array_append_entry)
	array_ptr = builder.alloca(dyn_array_struct_ptr, name='array_ptr')
	builder.store(dyn_array_append.args[0], array_ptr)
	value_ptr = builder.alloca(type_map[INT], name='value_ptr')
	builder.store(dyn_array_append.args[1], value_ptr)

	# BODY
	builder.call(compiler.module.get_global('dyn_array_double_capacity_if_full'), [builder.load(array_ptr)])

	size_ptr = builder.gep(builder.load(array_ptr), [zero_32, zero_32], inbounds=True)
	size_val = builder.load(size_ptr)

	size_val = builder.add(size_val, one)
	builder.store(size_val, size_ptr)

	data_ptr = builder.gep(builder.load(array_ptr), [zero_32, two_32], inbounds=True)

	data_element_ptr = builder.gep(builder.load(data_ptr), [size_val])

	builder.store(builder.load(value_ptr), data_element_ptr)

	builder.branch(dyn_array_append_exit)

	# CLOSE
	builder.position_at_end(dyn_array_append_exit)
	builder.ret_void()


def dynamic_array_get(compiler, dyn_array_struct_ptr):
	# START
	dyn_array_get_type = ir.FunctionType(type_map[INT], [dyn_array_struct_ptr, type_map[INT]])
	dyn_array_get = ir.Function(compiler.module, dyn_array_get_type, 'dyn_array_get')
	dyn_array_get_entry = dyn_array_get.append_basic_block('entry')
	builder = ir.IRBuilder(dyn_array_get_entry)
	dyn_array_get_exit = dyn_array_get.append_basic_block('exit')
	dyn_array_get_index_out_of_bounds = dyn_array_get.append_basic_block('index_out_of_bounds')
	dyn_array_get_is_index_less_than_zero = dyn_array_get.append_basic_block('is_index_less_than_zero')
	dyn_array_get_negative_index = dyn_array_get.append_basic_block('negative_index')
	dyn_array_get_block = dyn_array_get.append_basic_block('get')
	builder.position_at_end(dyn_array_get_entry)
	array_ptr = builder.alloca(dyn_array_struct_ptr, name='array_ptr')
	builder.store(dyn_array_get.args[0], array_ptr)
	index_ptr = builder.alloca(type_map[INT], name='index_ptr')
	builder.store(dyn_array_get.args[1], index_ptr)

	# BODY
	index_val = builder.load(index_ptr)

	size_ptr = builder.gep(builder.load(array_ptr), [zero_32, zero_32], inbounds=True)
	size_val = builder.load(size_ptr)

	compare_index_to_size = builder.icmp_unsigned('>=', index_val, size_val)

	builder.cbranch(compare_index_to_size, dyn_array_get_index_out_of_bounds, dyn_array_get_is_index_less_than_zero)

	builder.position_at_end(dyn_array_get_index_out_of_bounds)
	builder.call(compiler.module.get_global('exit'), [one_32])
	builder.unreachable()

	builder.position_at_end(dyn_array_get_is_index_less_than_zero)

	compare_index_to_zero = builder.icmp_unsigned('<', index_val, zero)

	builder.cbranch(compare_index_to_zero, dyn_array_get_negative_index, dyn_array_get_block)

	builder.position_at_end(dyn_array_get_negative_index)

	add = builder.add(size_val, index_val)
	builder.store(add, index_ptr)
	builder.branch(dyn_array_get_block)

	builder.position_at_end(dyn_array_get_block)

	data_ptr = builder.gep(builder.load(array_ptr), [zero_32, two_32], inbounds=True)

	add_1 = builder.add(one, index_val)
	builder.store(add_1, index_ptr)
	index_val = builder.load(index_ptr)

	data_element_ptr = builder.gep(builder.load(data_ptr), [index_val])

	builder.branch(dyn_array_get_exit)

	# CLOSE
	builder.position_at_end(dyn_array_get_exit)
	builder.ret(builder.load(data_element_ptr))


def dynamic_array_set(compiler, dyn_array_struct_ptr):
	# START
	dyn_array_set_type = ir.FunctionType(type_map[VOID], [dyn_array_struct_ptr, type_map[INT], type_map[INT]])
	dyn_array_set = ir.Function(compiler.module, dyn_array_set_type, 'dyn_array_set')
	dyn_array_set_entry = dyn_array_set.append_basic_block('entry')
	builder = ir.IRBuilder(dyn_array_set_entry)
	dyn_array_set_exit = dyn_array_set.append_basic_block('exit')
	dyn_array_set_index_out_of_bounds = dyn_array_set.append_basic_block('index_out_of_bounds')
	dyn_array_set_is_index_less_than_zero = dyn_array_set.append_basic_block('is_index_less_than_zero')
	dyn_array_set_negative_index = dyn_array_set.append_basic_block('negative_index')
	dyn_array_set_block = dyn_array_set.append_basic_block('set')
	builder.position_at_end(dyn_array_set_entry)
	array_ptr = builder.alloca(dyn_array_struct_ptr, name='array_ptr')
	builder.store(dyn_array_set.args[0], array_ptr)
	index_ptr = builder.alloca(type_map[INT], name='index_ptr')
	builder.store(dyn_array_set.args[1], index_ptr)
	value_ptr = builder.alloca(type_map[INT], name='value_ptr')
	builder.store(dyn_array_set.args[2], value_ptr)

	# BODY
	index_val = builder.load(index_ptr)

	size_ptr = builder.gep(builder.load(array_ptr), [zero_32, zero_32], inbounds=True)
	size_val = builder.load(size_ptr)

	compare_index_to_size = builder.icmp_unsigned('>=', index_val, size_val)

	builder.cbranch(compare_index_to_size, dyn_array_set_index_out_of_bounds, dyn_array_set_is_index_less_than_zero)

	builder.position_at_end(dyn_array_set_index_out_of_bounds)
	builder.call(compiler.module.get_global('exit'), [one_32])
	builder.unreachable()

	builder.position_at_end(dyn_array_set_is_index_less_than_zero)

	compare_index_to_zero = builder.icmp_unsigned('<', index_val, zero)

	builder.cbranch(compare_index_to_zero, dyn_array_set_negative_index, dyn_array_set_block)

	builder.position_at_end(dyn_array_set_negative_index)

	add = builder.add(size_val, index_val)
	builder.store(add, index_ptr)
	builder.branch(dyn_array_set_block)

	builder.position_at_end(dyn_array_set_block)

	data_ptr = builder.gep(builder.load(array_ptr), [zero_32, two_32], inbounds=True)

	add_1 = builder.add(one, index_val)
	builder.store(add_1, index_ptr)
	index_val = builder.load(index_ptr)

	data_element_ptr = builder.gep(builder.load(data_ptr), [index_val])

	builder.store(builder.load(value_ptr), data_element_ptr)

	builder.branch(dyn_array_set_exit)

	# CLOSE
	builder.position_at_end(dyn_array_set_exit)
	builder.ret_void()


def dynamic_array_length(compiler, dyn_array_struct_ptr):
	# START
	dyn_array_length_type = ir.FunctionType(type_map[INT], [dyn_array_struct_ptr])
	dyn_array_length = ir.Function(compiler.module, dyn_array_length_type, 'dyn_array_length')
	dyn_array_length_entry = dyn_array_length.append_basic_block('entry')
	builder = ir.IRBuilder(dyn_array_length_entry)
	builder.position_at_end(dyn_array_length_entry)
	array_ptr = builder.alloca(dyn_array_struct_ptr, name='array_ptr')
	builder.store(dyn_array_length.args[0], array_ptr)

	size_ptr = builder.gep(builder.load(array_ptr), [zero_32, zero_32], inbounds=True)

	# CLOSE
	builder.ret(builder.load(size_ptr))

# TODO: add the following functions for dynamic array
# extend(iterable)
# insert(item, index)
# remove(item)
# pop([index])
# clear()
# index(x[, start[, end]])
# count(item)
# sort(key=None, reverse=False)
# reverse()
