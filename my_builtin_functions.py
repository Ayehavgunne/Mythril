def define_printd(ir, module):
	# function start
	func_type = ir.FunctionType(ir.VoidType(), [ir.IntType(64)])
	function = ir.Function(module, func_type, 'printd')
	entry_block = function.append_basic_block('entry')
	builder = ir.IRBuilder(entry_block)
	exit_block = function.append_basic_block('exit')
	n_addr = builder.alloca(ir.IntType(64), name='n')
	builder.store(function.args[0], n_addr)
	x_addr = builder.alloca(ir.IntType(64), name='x')

	# function body
	int_zero = ir.Constant(ir.IntType(64), 0)
	int_one = ir.Constant(ir.IntType(64), 1)
	int_two = ir.Constant(ir.IntType(64), 2)
	int_three = ir.Constant(ir.IntType(64), 3)
	int_four = ir.Constant(ir.IntType(64), 4)
	int_five = ir.Constant(ir.IntType(64), 5)
	int_six = ir.Constant(ir.IntType(64), 6)
	int_seven = ir.Constant(ir.IntType(64), 7)
	int_eight = ir.Constant(ir.IntType(64), 8)
	int_nine = ir.Constant(ir.IntType(64), 9)
	int_ten = ir.Constant(ir.IntType(64), 10)
	int_fourtyeight = ir.Constant(ir.IntType(64), 48)
	int_fourtynine = ir.Constant(ir.IntType(64), 49)
	int_fifty = ir.Constant(ir.IntType(64), 50)
	int_fiftyone = ir.Constant(ir.IntType(64), 51)
	int_fiftytwo = ir.Constant(ir.IntType(64), 52)
	int_fiftythree = ir.Constant(ir.IntType(64), 53)
	int_fiftyfour = ir.Constant(ir.IntType(64), 54)
	int_fiftyfive = ir.Constant(ir.IntType(64), 55)
	int_fiftysix = ir.Constant(ir.IntType(64), 56)
	int_fiftyseven = ir.Constant(ir.IntType(64), 57)

	div_ten = builder.udiv(builder.load(n_addr), int_ten, 'divten')
	greater_than_zero = builder.icmp_unsigned('>', div_ten, int_zero, 'greaterthanzero')
	mod_ten = builder.urem(builder.load(n_addr), int_ten, 'modten')
	builder.store(mod_ten, x_addr)
	equals_zero = builder.icmp_unsigned('==', builder.load(x_addr), int_zero, 'equalszero')
	equals_one = builder.icmp_unsigned('==', builder.load(x_addr), int_one, 'equalsone')
	equals_two = builder.icmp_unsigned('==', builder.load(x_addr), int_two, 'equalstwo')
	equals_three = builder.icmp_unsigned('==', builder.load(x_addr), int_three, 'equalsthree')
	equals_four = builder.icmp_unsigned('==', builder.load(x_addr), int_four, 'equalsfour')
	equals_five = builder.icmp_unsigned('==', builder.load(x_addr), int_five, 'equalsfive')
	equals_six = builder.icmp_unsigned('==', builder.load(x_addr), int_six, 'equalssix')
	equals_seven = builder.icmp_unsigned('==', builder.load(x_addr), int_seven, 'equalsseven')
	equals_eight = builder.icmp_unsigned('==', builder.load(x_addr), int_eight, 'equalseight')
	equals_nine = builder.icmp_unsigned('==', builder.load(x_addr), int_nine, 'equalsnine')

	with builder.if_then(greater_than_zero):
		builder.call(module.get_global('printd'), [div_ten])

	with builder.if_then(equals_zero):
		builder.call(module.get_global('putchar'), [int_fourtyeight])

	with builder.if_then(equals_one):
		builder.call(module.get_global('putchar'), [int_fourtynine])

	with builder.if_then(equals_two):
		builder.call(module.get_global('putchar'), [int_fifty])

	with builder.if_then(equals_three):
		builder.call(module.get_global('putchar'), [int_fiftyone])

	with builder.if_then(equals_four):
		builder.call(module.get_global('putchar'), [int_fiftytwo])

	with builder.if_then(equals_five):
		builder.call(module.get_global('putchar'), [int_fiftythree])

	with builder.if_then(equals_six):
		builder.call(module.get_global('putchar'), [int_fiftyfour])

	with builder.if_then(equals_seven):
		builder.call(module.get_global('putchar'), [int_fiftyfive])

	with builder.if_then(equals_eight):
		builder.call(module.get_global('putchar'), [int_fiftysix])

	with builder.if_then(equals_nine):
		builder.call(module.get_global('putchar'), [int_fiftyseven])
	builder.branch(exit_block)

	# function close
	builder.position_at_end(exit_block)
	builder.ret_void()

def define_prints(ir, module):
	func_type = ir.FunctionType(ir.VoidType(), [ir.PointerType(ir.IntType(8))])
	function = ir.Function(module, func_type, 'prints')
	entry_block = function.append_basic_block('entry')
	builder = ir.IRBuilder(entry_block)
	# exit_block = function.append_basic_block('exit')
	str_addr = builder.alloca(ir.IntType(8).as_pointer(), name='str')
	builder.store(function.args[0], str_addr)

	init_block = function.append_basic_block('for.init')
	test_block = function.append_basic_block('for.cond')
	body_block = function.append_basic_block('for.body')
	end_block = function.append_basic_block('for.end')
	builder.branch(init_block)
	builder.position_at_end(init_block)
	start = ir.Constant(ir.IntType(64), 0)
	stop = ir.Constant(ir.IntType(64), 6)
	step = ir.Constant(ir.IntType(64), 1)
	i_addr = builder.alloca(ir.IntType(64), name='i')
	builder.store(start, i_addr)
	builder.branch(test_block)
	builder.position_at_end(test_block)
	cond = builder.icmp_unsigned('<', builder.load(i_addr), stop)
	builder.cbranch(cond, body_block, end_block)
	builder.position_at_end(body_block)
	builder.call(module.get_global('putchar'), [builder.extract_value(builder.load(str_addr), builder.load(i_addr))])
	succ = builder.add(step, builder.load(i_addr))
	builder.store(succ, i_addr)
	builder.branch(test_block)
	builder.position_at_end(end_block)
	builder.ret_void()