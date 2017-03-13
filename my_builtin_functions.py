def define_printd(ir, module):
	# function start
	func_type = ir.FunctionType(ir.VoidType(), [ir.IntType(64)])
	function = ir.Function(module, func_type, 'printd')
	entry_block = function.append_basic_block('entry')
	builder = ir.IRBuilder(entry_block)
	exit_block = function.append_basic_block('exit')
	n_addr = builder.alloca(ir.IntType(64), name='n')
	builder.store(function.args[0], n_addr)
	x_addr = builder.alloca(ir.IntType(32), name='x')

	# function body
	int_zero = ir.Constant(ir.IntType(32), 0)
	int_one = ir.Constant(ir.IntType(32), 1)
	int_two = ir.Constant(ir.IntType(32), 2)
	int_three = ir.Constant(ir.IntType(32), 3)
	int_four = ir.Constant(ir.IntType(32), 4)
	int_five = ir.Constant(ir.IntType(32), 5)
	int_six = ir.Constant(ir.IntType(32), 6)
	int_seven = ir.Constant(ir.IntType(32), 7)
	int_eight = ir.Constant(ir.IntType(32), 8)
	int_nine = ir.Constant(ir.IntType(32), 9)
	int_ten = ir.Constant(ir.IntType(32), 10)
	int_fourtyeight = ir.Constant(ir.IntType(32), 48)
	int_fourtynine = ir.Constant(ir.IntType(32), 49)
	int_fifty = ir.Constant(ir.IntType(32), 50)
	int_fiftyone = ir.Constant(ir.IntType(32), 51)
	int_fiftytwo = ir.Constant(ir.IntType(32), 52)
	int_fiftythree = ir.Constant(ir.IntType(32), 53)
	int_fiftyfour = ir.Constant(ir.IntType(32), 54)
	int_fiftyfive = ir.Constant(ir.IntType(32), 55)
	int_fiftysix = ir.Constant(ir.IntType(32), 56)
	int_fiftyseven = ir.Constant(ir.IntType(32), 57)

	div_ten = builder.udiv(builder.load(n_addr), builder.zext(int_ten, ir.IntType(64)), 'divten')
	greater_than_zero = builder.icmp_unsigned('>', div_ten, int_zero, 'greaterthanzero')
	mod_ten = builder.urem(builder.trunc(builder.load(n_addr), ir.IntType(32)), int_ten, 'modten')
	builder.store(mod_ten, x_addr)

	with builder.if_then(greater_than_zero):
		builder.call(module.get_global('printd'), [div_ten])

	case_0 = function.append_basic_block('case')
	case_1 = function.append_basic_block('case')
	case_2 = function.append_basic_block('case')
	case_3 = function.append_basic_block('case')
	case_4 = function.append_basic_block('case')
	case_5 = function.append_basic_block('case')
	case_6 = function.append_basic_block('case')
	case_7 = function.append_basic_block('case')
	case_8 = function.append_basic_block('case')
	case_9 = function.append_basic_block('case')
	default = function.append_basic_block('default')

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
	builder.call(module.get_global('putchar'), [int_fourtyeight])
	builder.branch(exit_block)

	builder.position_at_start(case_1)
	builder.call(module.get_global('putchar'), [int_fourtynine])
	builder.branch(exit_block)

	builder.position_at_start(case_2)
	builder.call(module.get_global('putchar'), [int_fifty])
	builder.branch(exit_block)

	builder.position_at_start(case_3)
	builder.call(module.get_global('putchar'), [int_fiftyone])
	builder.branch(exit_block)

	builder.position_at_start(case_4)
	builder.call(module.get_global('putchar'), [int_fiftytwo])
	builder.branch(exit_block)

	builder.position_at_start(case_5)
	builder.call(module.get_global('putchar'), [int_fiftythree])
	builder.branch(exit_block)

	builder.position_at_start(case_6)
	builder.call(module.get_global('putchar'), [int_fiftyfour])
	builder.branch(exit_block)

	builder.position_at_start(case_7)
	builder.call(module.get_global('putchar'), [int_fiftyfive])
	builder.branch(exit_block)

	builder.position_at_start(case_8)
	builder.call(module.get_global('putchar'), [int_fiftysix])
	builder.branch(exit_block)

	builder.position_at_start(case_9)
	builder.call(module.get_global('putchar'), [int_fiftyseven])
	builder.branch(exit_block)

	builder.position_at_start(default)
	builder.branch(exit_block)

	# function close
	builder.position_at_end(exit_block)
	builder.ret_void()


def define_printb(ir, module):
	# function start
	func_type = ir.FunctionType(ir.VoidType(), [ir.IntType(1)])
	function = ir.Function(module, func_type, 'printb')
	entry_block = function.append_basic_block('entry')
	builder = ir.IRBuilder(entry_block)
	exit_block = function.append_basic_block('exit')

	# function body
	equalszero = builder.icmp_unsigned('==', function.args[0], ir.Constant(ir.IntType(1), 0), 'equalszero')

	with builder.if_else(equalszero) as (then, otherwise):
		with then:
			builder.call(module.get_global('putchar'), [ir.Constant(ir.IntType(32), 102)])
			builder.call(module.get_global('putchar'), [ir.Constant(ir.IntType(32), 97)])
			builder.call(module.get_global('putchar'), [ir.Constant(ir.IntType(32), 108)])
			builder.call(module.get_global('putchar'), [ir.Constant(ir.IntType(32), 115)])
			builder.call(module.get_global('putchar'), [ir.Constant(ir.IntType(32), 101)])
			builder.branch(exit_block)
		with otherwise:
			builder.call(module.get_global('putchar'), [ir.Constant(ir.IntType(32), 116)])
			builder.call(module.get_global('putchar'), [ir.Constant(ir.IntType(32), 114)])
			builder.call(module.get_global('putchar'), [ir.Constant(ir.IntType(32), 117)])
			builder.call(module.get_global('putchar'), [ir.Constant(ir.IntType(32), 101)])
			builder.branch(exit_block)

	builder.branch(exit_block)

	# function close
	builder.position_at_end(exit_block)
	builder.ret_void()