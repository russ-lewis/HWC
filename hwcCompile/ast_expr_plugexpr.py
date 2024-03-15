
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
        # if this is a memory variable, then this Var object should be
        # wrapped inside a SubsetOf object (as part of a MemVar), and
        # the SubsetOf should never recurse into us.  Same for the next
        # func, too.
        assert not self.decl.isMem
    def print_wiring_diagram(self, start_bit):
        assert not self.decl.isMem



# this class is useful for any expression which needs to build a subset of a
# larger PlugExpr, such as array indexing, slicing, dot-expr, or Memory.  It
# has a base expression, along with an offset and a size into the base
# expression, plus a type of the underlying expression.  The true offset of
# this expression is not calculated until the offset of the underlying
# expression is known.

class mt_PlugExpr_SubsetOf(mt_PlugExpr):
    def __init__(self, base, offset_cb, typ_):
        self.base      = base
        self.offset_cb = offset_cb
        self.typ_      = typ_

        self.decl_bitSize = None
        self.offset       = None

        self.is_lhs = base.is_lhs

    def print_tree(self, prefix):
        print(f"{prefix}mt_PlugExpr_SubsetOf:")
        print(f"{prefix}  offset_from: {self.offset_from}")
        print(f"{prefix}  subset_size: {self.subset_size}")
        print(f"{prefix}  base:")
        self.base.print_tree("    ")

    def calc_sizes(self):
        if self.decl_bitSize == "in progress":
            assert False    # TODO: report cyclic declaration
        if self.decl_bitSize is not None:
            return
        self.decl_bitSize = "in progress"

        self.base.calc_sizes()

        self.decl_bitSize = self.base.decl_bitSize

    def calc_top_down_offsets(self, offset):
        self.base.calc_top_down_offsets(offset)
        assert self.offset is None    # we'll resolve this later

    def calc_bottom_up_offsets(self):
        self.base.calc_bottom_up_offsets()
        assert type(self.base.offset) == int
        self.offset = self.base.offset + self.offset_cb()

    def print_bit_descriptions(self, name, start_bit):
        pass
    def print_wiring_diagram(self, start_bit):
        pass



class mt_PlugExpr_ArrayIndex(mt_PlugExpr):
    def __init__(self, base, indx):
        self.base = base
        self.indx = indx

        self.is_lhs = base.is_lhs

        # TODO: I need a version of this class (maybe integrated into this?)
        # that can handle a runtime index.
        assert isinstance(self.indx, mt_StaticExpr)

        assert type(base.typ_) == mt_PlugDecl_ArrayOf
        self.typ_ = base.typ_.base

        self.decl_bitSize = None
        self.offset       = None

    def print_tree(self, prefix):
        print(f"{prefix}mt_PlugExpr_ArrayIndex:")
        print(f"{prefix}  base:")
        self.base.print_tree("    ")
        print(f"{prefix}  indx:")
        self.indx.print_tree("    ")
        print(f"{prefix}  typ_:")
        self.typ_.print_tree("    ")

    def calc_sizes(self):
        if self.decl_bitSize == "in progress":
            assert False    # TODO: report cyclic declaration
        if self.decl_bitSize is not None:
            return
        self.decl_bitSize = "in progress"

        self.base.calc_sizes()
        self.indx.calc_sizes()

        self.indx = self.indx.resolve_static_expr()
        if type(self.indx) != int:
            TODO()    # report syntax error
        if self.indx < 0 or self.indx >= self.base.typ_.len_:
            TODO()    # report syntax error

        self.decl_bitSize = self.base.decl_bitSize

    def calc_top_down_offsets(self, offset):
        self.base.calc_top_down_offsets(offset)

    def calc_bottom_up_offsets(self):
        self.base.calc_bottom_up_offsets()
        self.offset = self.base.offset + self.typ_.decl_bitSize * self.indx

    def print_bit_descriptions(self, name, start_bit):
        self.base.print_bit_descriptions(name, start_bit)



class mt_PlugExpr_ArraySlice(mt_PlugExpr):
    def __init__(self, base, start,end):
        self.base  = base
        self.start = start
        self.end   = end

        self.is_lhs = base.is_lhs

        # array index expressions can have runtime indices, but array
        # slices cannot, since the size would be variable.
        assert                                              isinstance(self.start, mt_StaticExpr)
        assert self.end is None or type(self.end) == int or isinstance(self.end  , mt_StaticExpr)

        # the type of our expression is *almost* identical to the base
        # type...but not exactly, because we have a shorter len.  But we
        # won't know the exact len until we can resolve the static
        # expressions (which can't happen until calc_sizes())

        assert type(base.typ_) == mt_PlugDecl_ArrayOf
        self.typ_ = mt_PlugDecl_ArrayOf(base.typ_.base, None)

        self.decl_bitSize = None
        self.offset       = None

    def print_tree(self, prefix):
        print(f"{prefix}mt_PlugExpr_ArraySlice:")
        print(f"{prefix}  base :")
        self.base.print_tree("    ")

        if type(self.start) == int:
            print(f"{prefix}  start: {self.start}")
        else:
            print(f"{prefix}  start:")
            self.start.print_tree("    ")

        if self.end is None or type(self.end) == int or self.end.is_leaf:
            print(f"{prefix}  end  : {self.end}")
        else:
            print(f"{prefix}  end  :")
            self.end.print_tree("    ")

    def calc_sizes(self):
        if self.decl_bitSize == "in progress":
            assert False    # TODO: report cyclic declaration
        if self.decl_bitSize is not None:
            return
        self.decl_bitSize = "in progress"

        self.base .calc_sizes()
        self.start.calc_sizes()
        if self.end is not None:
            self.end.calc_sizes()

        assert                     isinstance(self.start, mt_StaticExpr)
        assert self.end is None or isinstance(self.end  , mt_StaticExpr)

        assert type(self.base.typ_.len_) == int

        self.start = self.start.resolve_static_expr()
        if type(self.start) != int:
            TODO()    # report syntax error
        if self.start < 0:
            TODO()    # report syntax error

        if self.end is None:
            self.end = self.base.typ_.len_
        else:
            self.end = self.end.resolve_static_expr()
            if type(self.end) != int:
                TODO()    # resolve static expr
            if self.end <= self.start:
                print(self.start)
                print(self.end)
                TODO()    # resolve static expr

        if self.end > self.base.typ_.len_:
            self.print_tree("")
            TODO()    # report syntax error

        self.typ_.len_ = self.end - self.start
        self.typ_.calc_sizes()

        self.decl_bitSize = self.base.decl_bitSize    # we don't need to allocate more temporary bits

    def calc_top_down_offsets(self, offset):
        self.base.calc_top_down_offsets(offset)

    def calc_bottom_up_offsets(self):
        self.base.calc_bottom_up_offsets()
        self.offset = self.base.offset + self.typ_.base.decl_bitSize * self.start

    def print_bit_descriptions(self, name, start_bit):
        self.base.print_bit_descriptions(name, start_bit)



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

    def calc_top_down_offsets(self, offset):
        pass
    def calc_bottom_up_offsets(self):
        pass



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

    def calc_top_down_offsets(self, offset):
        pass
    def calc_bottom_up_offsets(self):
        pass



class mt_PlugExpr_EQ(mt_PlugExpr):
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



class mt_PlugExpr_CONCAT(mt_PlugExpr):
    is_lhs = False

    def __init__(self, lft,rgt):
        assert isinstance(lft, mt_PlugExpr)
        assert isinstance(rgt, mt_PlugExpr)

        if type(lft.typ_) != mt_PlugDecl_ArrayOf:
            TODO()    # report syntax error

        if lft.typ_ != rgt.typ_:
            TODO()    # report syntax error

        self.lft  = lft
        self.rgt  = rgt
        self.typ_ = mt_PlugDecl_ArrayOf(lft.typ_.base, None)    # we will set the length later, when we know it

        self.decl_bitSize = None
        self.offset       = None

    def print_tree(self, prefix):
        print(f"{prefix}mt_PlugExpr_CONCAT:")
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

        assert type(self.lft.typ_.len_) == int and self.lft.typ_.len_ >0
        assert type(self.rgt.typ_.len_) == int and self.rgt.typ_.len_ >0
        self.typ_.len_ = self.lft.typ_.len_ + self.rgt.typ_.len_
        self.typ_.calc_sizes()

        # decl_bitSize is however much we need to evaluate the two
        # sub-expressions (could be as little as 0 each), plus the size of
        # the destination buffer to hold the concatenated data (definitely
        # not zero!)
        self.decl_bitSize = self.typ_.decl_bitSize + self.lft.decl_bitSize + self.rgt.decl_bitSize

        # this was also confirmed in the constructor
        assert type(self.lft.typ_) == mt_PlugDecl_ArrayOf
        assert type(self.rgt.typ_) == mt_PlugDecl_ArrayOf

        # this is new, should be a side effect of calc_sizes() calls above
        assert type(self.lft.typ_.len_) == int and self.lft.typ_.len_ > 0
        assert type(self.rgt.typ_.len_) == int and self.rgt.typ_.len_ > 0
        self.typ_.len_ = self.lft.typ_.len_ + self.rgt.typ_.len_

    def calc_top_down_offsets(self, offset):
        self.offset = offset
        self.lft.calc_top_down_offsets(offset + self.typ_.decl_bitSize)
        self.rgt.calc_top_down_offsets(offset + self.typ_.decl_bitSize + self.lft.decl_bitSize)

    def calc_bottom_up_offsets(self):
        self.lft.calc_bottom_up_offsets()
        self.rgt.calc_bottom_up_offsets()

    def print_bit_descriptions(self, name, start_bit):
        start = self.offset
        end   = self.offset + self.typ_.decl_bitSize
        print(f"# {start:6d} {end:6d} {name}._CONCAT_{start}")

        self.lft.print_bit_descriptions(name, start_bit)
        self.rgt.print_bit_descriptions(name, start_bit)



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

