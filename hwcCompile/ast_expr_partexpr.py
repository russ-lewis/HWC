
from ast_expr_metatypes import *



class mt_PartExpr_Var(mt_PartExpr):
    decl_bitSize = 0
    is_lhs       = True

    def __init__(self, decl):
        assert isinstance(decl.typ_, mt_PartDecl)
        self.decl = decl
        assert not self.decl.isMem

        self.typ_ = decl.typ_

        self.offset       = None

    def print_tree(self, prefix):
        print(f"{prefix}mt_PartExpr_Var:")
        print(f"{prefix}  decl:")
        self.decl.print_tree(prefix+"    ")
        print(f"{prefix}  decl_bitSize: {self.decl_bitSize}")
        print(f"{prefix}  offset      : {self.offset}")

    def convert_to_metatype(self, side):
        return self

    def calc_sizes(self):
        self.decl.calc_sizes()
        assert type(self.decl.decl_bitSize) == int
        assert      self.decl.decl_bitSize  >  0

    def calc_top_down_offsets(self, offset):
        assert self.offset is None    # we'll resolve this later

    def calc_bottom_up_offsets(self):
        assert type(self.decl.offset) == int and self.decl.offset >= 0
        self.offset = self.decl.offset

    def print_bit_descriptions(self, name, start_bit):
        pass
    def print_wiring_diagram(self, start_bit):
        pass

