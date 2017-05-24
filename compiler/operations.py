from llvmlite import ir

from compiler import type_map
from compiler import NUM_TYPES
from my_grammar import *

I1 = 'i1'
I8 = 'i8'
I32 = 'i32'
I64 = 'i64'
I128 = 'i128'
DOUBLE = 'double'
FLOATINGPOINT = 'float'

def operations(generator, node):
	op = node.op.value
	left = generator.visit(node.left)
	right = generator.visit(node.right)
	if op == CAST:
		return cast_ops(generator, left, right, node)
	elif isinstance(left.type, ir.IntType) and isinstance(right.type, ir.IntType):
		return int_ops(generator, op, left, right, node)
	elif type(left.type) in NUM_TYPES and type(right.type) in NUM_TYPES:
		if isinstance(left.type, ir.IntType):
			left = generator.builder.uitofp(left, type_map[DEC])
		if isinstance(right.type, ir.IntType):
			right = generator.builder.uitofp(right, type_map[DEC])
		return float_ops(generator, op, left, right, node)
	elif isinstance(left, (ir.LoadInstr, ir.GEPInstr)) or isinstance(right, (ir.LoadInstr, ir.GEPInstr)):
		return str_ops(generator, op, left, right, node)


def int_ops(generator, op, left, right, node):
	if op == PLUS:
		return generator.builder.add(left, right, 'addtmp')
	elif op == MINUS:
		return generator.builder.sub(left, right, 'subtmp')
	elif op == MUL:
		return generator.builder.mul(left, right, 'multmp')
	elif op == FLOORDIV:
		return generator.builder.sdiv(left, right, 'divtmp')
	elif op == DIV:
		return generator.builder.fdiv(generator.builder.sitofp(left, type_map[DEC]),
			generator.builder.sitofp(right, type_map[DEC]), 'fdivtmp')
	elif op == MOD:
		return generator.builder.srem(left, right, 'modtmp')
	elif op == POWER:
		temp = generator.builder.alloca(type_map[INT])
		generator.builder.store(left, temp)
		for _ in range(node.right.value - 1):
			res = generator.builder.mul(generator.builder.load(temp), left)
			generator.builder.store(res, temp)
		return generator.builder.load(temp)
	elif op == AND:
		return generator.builder.and_(left, right)
	elif op == OR:
		return generator.builder.or_(left, right)
	elif op == XOR:
		return generator.builder.xor(left, right)
	elif op == ARITHMATIC_LEFT_SHIFT or op == BINARY_LEFT_SHIFT:
		return generator.builder.shl(left, right)
	elif op == ARITHMATIC_RIGHT_SHIFT:
		return generator.builder.ashr(left, right)
	elif op == BINARY_LEFT_SHIFT:
		return generator.builder.lshr(left, right)
	elif op in (EQUALS, NOT_EQUALS, LESS_THAN, LESS_THAN_OR_EQUAL_TO, GREATER_THAN, GREATER_THAN_OR_EQUAL_TO):
		cmp = generator.builder.icmp_signed(op, left, right, 'cmptmp')
		return generator.builder.uitofp(cmp, type_map[BOOL], 'booltmp')
	else:
		raise SyntaxError('Unknown binary operator', node.op)


def float_ops(generator, op, left, right, node):
	if op == PLUS:
		return generator.builder.fadd(left, right, 'faddtmp')
	elif op == MINUS:
		return generator.builder.fsub(left, right, 'fsubtmp')
	elif op == MUL:
		return generator.builder.fmul(left, right, 'fmultmp')
	elif op == FLOORDIV:
		return generator.builder.udiv(generator.builder.fptosi(left, ir.IntType(64)),
			generator.builder.fptosi(right, ir.IntType(64)), 'ffloordivtmp')
	elif op == DIV:
		return generator.builder.fdiv(left, right, 'fdivtmp')
	elif op == MOD:
		return generator.builder.frem(left, right, 'fmodtmp')
	elif op == POWER:
		temp = generator.builder.alloca(type_map[DEC])
		generator.builder.store(left, temp)
		for _ in range(node.right.value - 1):
			res = generator.builder.fmul(generator.builder.load(temp), left)
			generator.builder.store(res, temp)
		return generator.builder.load(temp)
	elif op in (EQUALS, NOT_EQUALS, LESS_THAN, LESS_THAN_OR_EQUAL_TO, GREATER_THAN, GREATER_THAN_OR_EQUAL_TO):
		cmp = generator.builder.fcmp_ordered(op, left, right, 'cmptmp')
		return generator.builder.sitofp(cmp, type_map[BOOL], 'booltmp')
	else:
		raise SyntaxError('Unknown binary operator', node.op)


def str_ops(generator, op, left, right, node):
	# TODO add strings together!
	left_len = str_get_len(left, generator) - 1
	right_len = str_get_len(right, generator)
	return


def str_get_len(string, generator):
	if isinstance(string, ir.LoadInstr):
		str_gep = generator.builder.gep(string, [generator.const(0), generator.const(0)])
		return str_gep
	if isinstance(string, ir.GEPInstr):
		return string.pointer.type.pointee.count


def cast_ops(generator, left, right, node):
	orig_type = str(left.type)
	cast_type = str(right)
	if cast_type == I64:
		if orig_type == DOUBLE:
			cast = generator.builder.fptoui(left, type_map[INT])
			return cast
	elif cast_type == DOUBLE:
		if orig_type == I64:
			cast = generator.builder.uitofp(left, type_map[DEC])
			return cast
	elif cast_type == FLOAT:
		return float(left)
	elif cast_type == COMPLEX:
		return complex(left)
	elif cast_type == STR:
		return str(left)
	elif cast_type == BOOL:
		return bool(left)
	elif cast_type == BYTES:
		return bytes(left)
	elif cast_type == LIST:
		return list(left)
	elif cast_type == TUPLE:
		return tuple(left)
	elif cast_type == DICT:
		return dict(left)
	elif cast_type == ENUM:
		return Enum(left.value, left)
	elif cast_type in (ANY, FUNC):
		raise TypeError('file={} line={}: Cannot cast to type {}'.format(
			generator.file_name,
			node.line_num,
			cast_type
		))
