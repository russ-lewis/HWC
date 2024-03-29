
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
    def __init__(self, val):
        assert val in ["true","false"]
        self.val = (val == "true")

    def resolve_static_expr(self):
        return self.val
    def calc_sizes(self):
        pass



class mt_StaticExpr_ADD(mt_StaticExpr):
    def __init__(self, lineInfo, lft,rgt):
        self.lineInfo = lineInfo
        self.lft      = lft
        self.rgt      = rgt

    def print_tree(self, prefix):
        print(f"{prefix}mt_StaticExpr_ADD:    {self.lineInfo}")
        print(f"{prefix}  lft:")
        self.lft.print_tree(prefix+"    ")
        print(f"{prefix}  rgt:")
        self.rgt.print_tree(prefix+"    ")

    def calc_sizes(self):
        self.lft.calc_sizes()
        self.rgt.calc_sizes()

    def resolve_static_expr(self):
        lft = self.lft.resolve_static_expr()
        rgt = self.rgt.resolve_static_expr()
        assert type(lft) == int
        assert type(rgt) == int

        return lft + rgt



class mt_StaticExpr_MOD(mt_StaticExpr):
    def __init__(self, lineInfo, lft,rgt):
        self.lineInfo = lineInfo
        self.lft      = lft
        self.rgt      = rgt

    def calc_sizes(self):
        self.lft.calc_sizes()
        self.rgt.calc_sizes()

    def resolve_static_expr(self):
        lft = self.lft.resolve_static_expr()
        rgt = self.rgt.resolve_static_expr()
        assert type(lft) == int
        assert type(rgt) == int

        return lft % rgt

