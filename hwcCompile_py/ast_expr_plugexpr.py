
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

    def calc_sizes_and_offsets(self):
        self.decl.calc_sizes_and_offsets()
        assert type(self.decl.decl_bitSize) == int
        assert      self.decl.decl_bitSize  >  0

        self.decl_bitSize = self.decl.decl_bitSize

