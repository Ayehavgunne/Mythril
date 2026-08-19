from ast import Type
from decimal import Decimal
from enum import Enum

import my_types


class VisitorException(Exception):
    pass


class Symbol:
    def __init__(self, name: str, symbol_type=None):
        self.name = name
        self.type = symbol_type


class BuiltinTypeSymbol(Symbol):
    def __init__(self, name, c_type=None, return_type=None):
        super().__init__(name)
        self.c_type = c_type
        self.return_type = return_type

    def type(self):
        return self.c_type.type()

    def __str__(self):
        return self.name

    __repr__ = __str__


ANY_BUILTIN = BuiltinTypeSymbol(my_types.ANY)
INT_BUILTIN = BuiltinTypeSymbol(my_types.INT, "Int")
INT8_BUILTIN = BuiltinTypeSymbol(my_types.INT8, "Int8")
INT32_BUILTIN = BuiltinTypeSymbol(my_types.INT32, "Int32")
INT128_BUILTIN = BuiltinTypeSymbol(my_types.INT128, "Int128")
DEC_BUILTIN = BuiltinTypeSymbol(my_types.DEC, "Dec")
FLOAT_BUILTIN = BuiltinTypeSymbol(my_types.FLOAT, "Float")
COMPLEX_BUILTIN = BuiltinTypeSymbol(my_types.COMPLEX, "Complex")
BOOL_BUILTIN = BuiltinTypeSymbol(my_types.BOOL, "Bool")
BYTES_BUILTIN = BuiltinTypeSymbol(my_types.BYTES, "Bytes")
STR_BUILTIN = BuiltinTypeSymbol(my_types.STR, "Str")
STRUCT_BUILTIN = BuiltinTypeSymbol(my_types.STRUCT, "Str")
LIST_BUILTIN = BuiltinTypeSymbol(my_types.LIST, "List")
DICT_BUILTIN = BuiltinTypeSymbol(my_types.DICT, "Dict")
ENUM_BUILTIN = BuiltinTypeSymbol(my_types.ENUM, "Enum")
FUNC_BUILTIN = BuiltinTypeSymbol(my_types.FUNC, "Func")


class VarSymbol(Symbol):
    def __init__(self, name, var_type, read_only=False):
        super().__init__(name, var_type)
        self.accessed = False
        self.val_assigned = False
        self.read_only = read_only

    def __str__(self):
        return f"<{self.name}:{self.type}>"

    __repr__ = __str__


class StructSymbol(Symbol):
    def __init__(self, name, fields):
        super().__init__(name)
        self.fields = fields
        self.accessed = False
        self.val_assigned = False


class CollectionSymbol(Symbol):
    def __init__(self, name, var_type, item_types):
        super().__init__(name, var_type)
        self.item_types = item_types
        self.accessed = False
        self.val_assigned = False


class FuncSymbol(Symbol):
    def __init__(self, name, return_type, parameters, body, parameter_defaults=None):
        super().__init__(name, return_type)
        self.parameters = parameters
        self.parameter_defaults = parameter_defaults or {}
        self.body = body
        self.accessed = False
        self.val_assigned = True

    def __str__(self):
        return f"<{self.name}:{self.type} ({', '.join((f'{key}:{value.value}' for key, value in self.parameters.items()))})>"

    __repr__ = __str__


class AliasSymbol(Symbol):
    def __init__(self, name, types):
        super().__init__(name, types)
        self.accessed = False

    def __str__(self):
        return f"<{self.name}:{self.type}>"

    __repr__ = __str__


class BuiltinFuncSymbol(Symbol):
    def __init__(self, name, return_type, parameters, body):
        super().__init__(name, return_type)
        self.parameters = parameters
        self.body = body
        self.accessed = False
        self.val_assigned = True

    def __str__(self):
        return f"<{self.name}:{self.type} ({', '.join((f'{key}:{value.value}' for key, value in self.parameters.items()))})>"

    __repr__ = __str__


class NodeVisitor:
    def __init__(self):
        self._scope = [{}]
        self._init_builtins()

    def _init_builtins(self):
        self.define(my_types.ANY, ANY_BUILTIN)
        self.define(my_types.INT, INT_BUILTIN)
        self.define(my_types.INT8, INT8_BUILTIN)
        self.define(my_types.INT32, INT32_BUILTIN)
        self.define(my_types.INT128, INT128_BUILTIN)
        self.define(my_types.DEC, DEC_BUILTIN)
        self.define(my_types.FLOAT, FLOAT_BUILTIN)
        self.define(my_types.COMPLEX, COMPLEX_BUILTIN)
        self.define(my_types.BOOL, BOOL_BUILTIN)
        self.define(my_types.BYTES, BYTES_BUILTIN)
        self.define(my_types.STR, STR_BUILTIN)
        self.define(my_types.STRUCT, STRUCT_BUILTIN)
        self.define(my_types.LIST, LIST_BUILTIN)
        self.define(my_types.DICT, DICT_BUILTIN)
        self.define(my_types.ENUM, ENUM_BUILTIN)
        self.define(my_types.FUNC, FUNC_BUILTIN)

    def visit(self, node):
        method_name = "visit_" + type(node).__name__.lower()
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    @staticmethod
    def generic_visit(node):
        raise VisitorException(f"No visit_{type(node).__name__.lower()} method")

    @property
    def top_scope(self):
        return self._scope[-1] if len(self._scope) >= 1 else None

    @property
    def second_scope(self):
        return self._scope[-2] if len(self._scope) >= 2 else None

    def search_scopes(self, name, level=None):
        if level:
            if name in self._scope[level]:
                return self._scope[level][name]
        else:
            for scope in reversed(self._scope):
                if name in scope:
                    return scope[name]

    def define(self, key, value, level=0):
        level = (len(self._scope) - level) - 1
        self._scope[level][key] = value

    def new_scope(self):
        self._scope.append({})

    def drop_top_scope(self):
        self._scope.pop()

    @property
    def symbols(self):
        return [value for scope in self._scope for value in scope.values()]

    @property
    def keys(self):
        return [key for scope in self._scope for key in scope]

    @property
    def items(self):
        return [(key, value) for scope in self._scope for key, value in scope.items()]

    @property
    def unvisited_symbols(self):
        return [
            sym_name
            for sym_name, sym_val in self.items
            if not isinstance(sym_val, (BuiltinTypeSymbol, BuiltinFuncSymbol))
            and not sym_val.accessed
        ]

    def infer_type(self, value):
        if isinstance(value, BuiltinTypeSymbol):
            return value
        if isinstance(value, FuncSymbol):
            return self.search_scopes(my_types.FUNC)
        elif isinstance(value, VarSymbol):
            return value.type
        elif isinstance(value, Type):
            return self.search_scopes(value.value)
        else:
            if isinstance(value, int):
                return self.search_scopes(my_types.INT)
            elif isinstance(value, Decimal):
                return self.search_scopes(my_types.DEC)
            elif isinstance(value, float):
                return self.search_scopes(my_types.FLOAT)
            elif isinstance(value, complex):
                return self.search_scopes(my_types.COMPLEX)
            elif isinstance(value, str):
                return self.search_scopes(my_types.STR)
            elif isinstance(value, bool):
                return self.search_scopes(my_types.BOOL)
            elif isinstance(value, bytes):
                return self.search_scopes(my_types.BYTES)
            elif isinstance(value, list):
                return self.search_scopes(my_types.LIST)
            elif isinstance(value, dict):
                return self.search_scopes(my_types.DICT)
            elif isinstance(value, Enum):
                return self.search_scopes(my_types.ENUM)
            elif callable(value):
                return self.search_scopes(my_types.FUNC)
            else:
                raise TypeError(f"Type not recognized: {value}")
