from llvmlite import ir
from my_grammar import *


RET_VAR = 'ret_var'

NUM_TYPES = (ir.IntType, ir.DoubleType, ir.FloatType)

# TODO: temorarily making Decimal a DoubleType till find (or make) a better representation
type_map = {
	BOOL: ir.IntType(1),
	INT: ir.IntType(64),
	INT8: ir.IntType(8),
	INT32: ir.IntType(32),
	INT128: ir.IntType(128),
	DEC: ir.DoubleType(),
	FLOAT: ir.FloatType(),
	FUNC: ir.FunctionType,
	VOID: ir.VoidType(),
	STR: ir.IntType(8).as_pointer,
}
