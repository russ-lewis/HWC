
from ast_expr_metatypes import *



class mt_PlugExpr_Var(mt_PlugExpr):
    def __init__(self, decl):
        assert isinstance(decl.typ_, mt_PlugDecl)
        self.decl = decl

        self.typ_ = decl.typ_

        self.decl_bitSize = None
        self.offset       = None

    def print_tree(self, prefix):
        print(f"{prefix}mt_PlugExpr_Var:")
        print(f"{prefix}  decl:")
        self.decl.print_tree(prefix+"    ")
        print(f"{prefix}  decl_bitSize: {self.decl_bitSize}")
        print(f"{prefix}  offset      : {self.offset}")

    def calc_sizes(self):
        self.decl.calc_sizes()
        assert type(self.decl.decl_bitSize) == int
        assert      self.decl.decl_bitSize  >  0

        self.decl_bitSize = 0



class mt_PlugExpr_BitArray(mt_PlugExpr):
    def __init__(self, bitSize, val):
        self.typ_         = mt_PlugDecl_ArrayOf(plugType_bit, bitSize)
        self.val          = val
        self.decl_bitSize = bitSize
    def __repr__(self):
        return f"mt_PlugExpr_BitArray: bitSize={self.decl_bitSize} val={self.val}"
    def print_tree(self, prefix):
        print(f"{prefix}{self}")



class mt_PlugExpr_Bit(mt_PlugExpr):
    leafNode = True
    typ_ = plugType_bit
    decl_bitSize = 1

    def __init__(self, val):
        assert val in [0,1]
        self.val = val
    def __repr__(self):
        return f"mt_PlugExpr_Bit: val={self.val}"
    def print_tree(self, prefix):
        print(f"{prefix}{self}")

