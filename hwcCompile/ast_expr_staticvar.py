
from ast_expr_metatypes import *



class mt_StaticExpr_Var(mt_StaticExpr):
    is_lhs = True

    def __init__(self, decl):
        assert isinstance(decl.typ_, mt_StaticType)
        self.decl = decl

        self.typ_ = decl.typ_

    def calc_sizes(self):
        pass

    def resolve_static_expr(self):
        return self.decl.static_val

