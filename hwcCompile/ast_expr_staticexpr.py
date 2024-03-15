
from ast_expr_metatypes import *



class mt_StaticExpr_NumExpr(mt_StaticExpr):
    typ_ = staticType_int

    def __init__(self, num):
        self.num = num

    def print_tree(self, prefix):
        print(f"{prefix}mt_StaticExpr_NumExpr: num={self.num}")

