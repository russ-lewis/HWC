
from ast_expr_metatypes import *



class mt_PlugExpr_Var(mt_PlugExpr):
    decl_bitSize = 0
    is_lhs       = True

    def __init__(self, decl):
        assert isinstance(decl.typ_, mt_PlugDecl)
        self.decl = decl

        self.typ_ = decl.typ_

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

    def calc_top_down_offsets(self, offset):
        assert self.offset is None    # we'll resolve this later

    def calc_bottom_up_offsets(self):
        assert type(self.decl.offset) == int and self.decl.offset >= 0
        self.offset = self.decl.offset

    def print_bit_descriptions(self, name, start_bit):
        pass

    def print_wiring_diagram(self, start_bit):
        pass



class mt_PlugExpr_BitArray(mt_PlugExpr):
    is_lhs = False

    def __init__(self, bitSize, val):
        self.typ_         = mt_PlugDecl_ArrayOf(plugType_bit, bitSize)
        self.val          = val
        self.decl_bitSize = bitSize
        self.offset       = None
    def __repr__(self):
        return f"mt_PlugExpr_BitArray: bitSize={self.decl_bitSize} val={self.val}"
    def print_tree(self, prefix):
        print(f"{prefix}{self}")



class mt_PlugExpr_Bit(mt_PlugExpr):
    leafNode     = True
    typ_         = plugType_bit
    decl_bitSize = 1
    is_lhs       = False

    def __init__(self, val):
        assert val in [0,1]
        self.val = val
    def __repr__(self):
        return f"mt_PlugExpr_Bit: val={self.val}"
    def print_tree(self, prefix):
        print(f"{prefix}{self}")



class mt_PlugExpr_Eq(mt_PlugExpr):
    is_lhs = False

    def __init__(self, lft,rgt):
        assert isinstance(lft, mt_PlugExpr)
        assert isinstance(rgt, mt_PlugExpr)

        if lft.typ_ != rgt.typ_:
            TODO()     # report syntax error

        self.lft  = lft
        self.rgt  = rgt
        self.typ_ = plugType_bit
        self.decl_bitSize = None
        self.offset       = None

    def print_tree(self, prefix):
        print(f"{prefix}mt_PlugExpr_EQ:")
        print(f"{prefix}  lft:")
        self.lft.print_tree(prefix+"    ")
        print(f"{prefix}  rgt:")
        self.rgt.print_tree(prefix+"    ")

    def calc_sizes(self):
        if self.decl_bitSize == "in progress":
            assert False    # TODO: report cyclic declaration
        if self.decl_bitSize is not None:
            return
        self.decl_bitSize = "in progress"

        self.lft.calc_sizes()
        self.rgt.calc_sizes()

        # 1 bit for the answer
        self.decl_bitSize = 1 + self.lft.decl_bitSize + self.rgt.decl_bitSize

    def calc_top_down_offsets(self, offset):
        self.offset = offset
        self.lft.calc_top_down_offsets(offset + 1)
        self.rgt.calc_top_down_offsets(offset + 1 + self.lft.decl_bitSize)

    def calc_bottom_up_offsets(self):
        self.lft.calc_bottom_up_offsets()
        self.rgt.calc_bottom_up_offsets()

    def print_bit_descriptions(self, name, start_bit):
        self.lft.print_bit_descriptions(name, start_bit)
        self.rgt.print_bit_descriptions(name, start_bit)
        print(f"# {self.offset:6d} {' ':6s} {name}._EQ_{self.offset}")

    def print_wiring_diagram(self, start_bit):
        self.lft.print_wiring_diagram(start_bit)
        self.rgt.print_wiring_diagram(start_bit + self.lft.decl_bitSize)
        print(f"logic {start_bit+self.offset} <= {start_bit+self.lft.offset} EQ {start_bit+self.rgt.offset} size {self.typ_.decl_bitSize}    # TODO: line number")



class mt_PlugExpr_NOT(mt_PlugExpr):
    is_lhs = False

    def __init__(self, rgt):
        assert isinstance(rgt, mt_PlugExpr)
        self.rgt  = rgt
        self.typ_ = rgt.typ_
        self.decl_bitSize = None
        self.offset       = None
    def print_tree(self, prefix):
        print(f"{prefix}mt_PlugExpr_NOT:")
        self.rgt.print_tree(prefix+"  ")

    def calc_sizes(self):
        if self.decl_bitSize == "in progress":
            assert False    # TODO: report cyclic declaration
        if self.decl_bitSize is not None:
            return
        self.decl_bitSize = "in progress"

        self.typ_.decl_bitSize
        self.rgt.calc_sizes()
        self.decl_bitSize = self.typ_.decl_bitSize + self.rgt.decl_bitSize

    def calc_top_down_offsets(self, offset):
        self.offset = offset
        self.rgt.calc_top_down_offsets(offset + self.typ_.decl_bitSize)

    def calc_bottom_up_offsets(self):
        self.rgt.calc_bottom_up_offsets()

    def print_bit_descriptions(self, name, start_bit):
        self.rgt.print_bit_descriptions(name, start_bit)

        assert self.typ_.decl_bitSize >= 1
        if self.typ_.decl_bitSize == 1:
            end = ""
        else:
            end = f"{start_bit+self.offset+self.typ_.decl_bitSize}"
        print(f"# {self.offset:6d} {end:>6s} {name}._NOT_{self.offset}")

    def print_wiring_diagram(self, start_bit):
        self.rgt.print_wiring_diagram(start_bit)
        print(f"logic {start_bit+self.offset} <= NOT {start_bit+self.rgt.offset} size {self.typ_.decl_bitSize}    # TODO: line number")

