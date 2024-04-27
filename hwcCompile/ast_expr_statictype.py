
from ast_expr_metatypes import *



class mt_StaticType_Int(mt_StaticType):
    leafNode = True

    def __init__(self):
        pass
    def dup(self):
        return self
    def __repr__(self):
        return f"mt_StaticType_Int"
    def print_tree(self, prefix):
        print(f"{prefix}{repr(self)}")

    def __eq__(self, other):
        return type(other) == type(self)

    def resolve_name_lookups(self, ns_pri):
        pass
    def convert_to_metatype(self, side):
        return self
    def calc_sizes(self):
        pass

