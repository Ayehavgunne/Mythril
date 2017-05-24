from llvmlite import ir

from compiler import type_map
from my_grammar import *


def define_vector(generator, data_type):
	vector_struct = generator.builder.LiteralStructType(type_map[INT], type_map[INT], data_type)
	vector_name = '{}vector'.format(data_type)
	generator.builder.alloc(vector_struct, name=vector_name)
	init_vector(generator, vector_struct)


def init_vector(generator, vector_struct):
	generator.start_function('vector_init', type_map[VOID], [vector_struct])