
from ast_expr_metatypes import *



class mt_StaticExpr_NumExpr(mt_StaticExpr):
    typ_ = staticType_int
    is_leaf = True

    def __init__(self, num):
        assert type(num) == int
        self.num = num
    def __repr__(self):
        return f"mt_StaticExpr_NumExpr: num={self.num}"
    def print_tree(self, prefix):
        print(f"{prefix}{self}")

    def convert_to_metatype(self, side):
        return self

    def calc_sizes(self):
        pass

    def resolve_static_expr(self):
        return self.num

    def calc_sizes(self):
        pass

    def resolve_static_expr(self):
        return self.num



class mt_StaticExpr_Bool(mt_StaticExpr):
    decl_bitSize = 1

    def __init__(self, val):
        assert val in ["true","false"]
        self.val = (val == "true")

    def resolve_static_expr(self):
        return self.val
    def calc_sizes(self):
        pass

