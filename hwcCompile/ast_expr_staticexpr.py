
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

    def calc_sizes(self):
        pass

    def resolve_static_expr(self):
        return self.num

    def calc_sizes(self):
        pass

    def resolve_static_expr(self):
        return self.num

