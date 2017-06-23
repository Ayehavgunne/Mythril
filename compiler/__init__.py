from llvmlite import ir
from my_grammar import *


RET_VAR = 'ret_var'

NUM_TYPES = (ir.IntType, ir.DoubleType, ir.FloatType)

# TODO: temorarily making Decimal a DoubleType till find (or make) a better representation
type_map = {
	ANY: ir.VoidType(),
	BOOL: ir.IntType(1),
	INT: ir.IntType(64),
	INT8: ir.IntType(8),
	INT32: ir.IntType(32),
	INT64: ir.IntType(64),
	INT128: ir.IntType(128),
	DEC: ir.DoubleType(),
	FLOAT: ir.FloatType(),
	FUNC: ir.FunctionType,
	VOID: ir.VoidType(),
	STR: ir.IntType(8).as_pointer,
}
type_table = {
	0: ANY,
	1: BOOL,
	2: INT,
	3: INT8,
	4: INT16,
	5: INT32,
	6: INT64,
	7: INT128,
	8: UINT8,
	9: UINT16,
	10: UINT32,
	11: UINT64,
	12: UINT128,
	13: DEC,
	14: FLOAT,
	15: COMPLEX,
	16: STR,
	17: BYTES,
	18: ARRAY,
	19: LIST,
	20: SET,
	21: DICT,
	22: ENUM,
	23: FUNC,
	24: STRUCT,
	25: CLASS,
}
