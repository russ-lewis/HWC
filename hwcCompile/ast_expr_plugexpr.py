
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

    def resolve_name_lookups(self, ns_pri):
        pass

    def convert_to_metatype(self, side):
        return self

    def calc_sizes(self):
        self.decl.calc_sizes()
        assert type(self.decl.decl_bitSize) == int
        assert      self.decl.decl_bitSize  >  0

    def calc_top_down_offsets(self, offset):
        assert self.offset is None    # we'll resolve this later

    def calc_bottom_up_offsets(self):
        assert self.offset is None

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



class mt_PlugExpr_Dot(mt_PlugExpr):
    def __init__(self, base, target):
        self.base   = base
        self.target = target

        self.typ_ = self.target.typ_

        self.is_lhs = self.base.is_lhs

        self.decl_bitSize = None
        self.offset       = None

    def print_tree(self, prefix):
        print(f"{prefix}mt_PlugExpr_Dot:")
        print(f"{prefix}  base:")
        self.base.print_tree(prefix+"    ")
        print(f"{prefix}  target:")
        self.target.print_tree(prefix+"    ")

    def calc_sizes(self):
        self.base.calc_sizes()

        # our 'target' field doesn't need to do calc_sizes because it's a
        # declaration; sizes are handled where it was declared, not where
        # it gets used.

        # a reference to a field never requires its own bits declared, but it's
        # possible that the underlying expression might.  It's rare, but one
        # could imagine someting like a CONCAT that joined two arrays, or even
        # something like
        #      (plugVarA & plugVarB).foo
        self.decl_bitSize = self.base.decl_bitSize

    def calc_top_down_offsets(self, offset):
        self.base.calc_top_down_offsets(offset)

    def calc_bottom_up_offsets(self):
        assert self.offset is None

        self.base.calc_bottom_up_offsets()

        self.offset = self.base.offset + self.target.offset

    def print_bit_descriptions(self, name, start_bit):
        self.base.print_bit_descriptions(name, self.base)

    def print_wiring_diagram(self, start_bit):
        self.base.print_wiring_diagram(start_bit)



# see long comment in class RuntimeIfStmt
class mt_PlugExpr_Alias(mt_PlugExpr):
    def __init__(self, base):
        self.base = base
        self.decl_bitSize = None
        self.offset       = None

    def print_tree(self, prefix):
        print(f"{prefix}mt_PlugExpr_Alias:")
        print(f"{prefix}base:")
        self.base.print_tree(prefix+"    ")

    def resolve_name_lookups(self, ns_pri):
        pass

    def convert_to_metatype(self, side):
        self.base = self.base.convert_to_metatype("right")

        assert self.base.typ_ is not None
        assert isinstance(self.base.typ_, mt_PlugDecl)
        self.typ_ = self.base.typ_

        return self

    def calc_sizes(self):
        self.decl_bitSize = 0

    def calc_top_down_offsets(self, offset):
        pass

    def calc_bottom_up_offsets(self):
        # NOTE: unlike all other Expr objects, we do *NOT* assert that we've
        #       never calculated our own offset, since (by definition) the
        #       point of Alias is that it's something that can be used in
        #       multiple places in the tree.

        # I don't have a great solution for the base here.  If I recurse into
        # the base, then I end up calculating the offset twice, which triggers
        # asserts elsewhere.  But if I don't do it, then, depending on the
        # order in which things are evaluated, I might need the offset before
        # it's ready.
        #
        # I've decided to risk it.  At time of writing, Alias is only used in
        # RuntimeIf, and RuntimeIf will always evaluate the true before the
        # false, so it's safe.  I think.  TODO: fix this!

        #self.base.calc_bottom_up_offsets()

        assert type(self.base.offset) == int
        assert      self.base.offset  >= 0
        self.offset = self.base.offset

    def print_bit_descriptions(self, name, start_bit):
        pass
    def print_wiring_diagram(self, start_bit):
        pass




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
        self.base.print_tree(prefix+"    ")

    def convert_to_metatype(self, side):
        return self

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
        assert self.offset is None

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
        assert isinstance(self.indx, mt_StaticExpr), (self.indx, type(self.indx))

        assert type(base.typ_) == mt_PlugDecl_ArrayOf
        self.typ_ = base.typ_.base

        self.decl_bitSize = None
        self.offset       = None

    def print_tree(self, prefix):
        print(f"{prefix}mt_PlugExpr_ArrayIndex:")
        print(f"{prefix}  base:")
        self.base.print_tree(prefix+"    ")

        if not isinstance(self.indx, mt_StaticExpr):
            print(f"{prefix}  indx: {self.indx}")
        else:
            print(f"{prefix}  indx:")
            self.indx.print_tree(prefix+"    ")

        print(f"{prefix}  typ_:")
        self.typ_.print_tree(prefix+"    ")

    def resolve_name_lookups(self, ns_pri):
        self.base.resolve_name_lookups(ns_pri)
        self.indx.resolve_name_lookups(ns_pri)

    def convert_to_metatype(self, side):
        return self

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
        assert self.offset is None

        self.base.calc_bottom_up_offsets()
        self.offset = self.base.offset + self.typ_.decl_bitSize * self.indx

    def print_bit_descriptions(self, name, start_bit):
        self.base.print_bit_descriptions(name, start_bit)

    def print_wiring_diagram(self, start_bit):
        self.base.print_wiring_diagram(start_bit)



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
        self.base.print_tree(prefix+"    ")

        if type(self.start) == int:
            print(f"{prefix}  start: {self.start}")
        else:
            print(f"{prefix}  start:")
            self.start.print_tree(prefix+"    ")

        if self.end is None or type(self.end) == int or self.end.is_leaf:
            print(f"{prefix}  end: {self.end}")
        else:
            print(f"{prefix}  end:")
            self.end.print_tree(prefix+"    ")

    def convert_to_metatype(self, side):
        return self

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
        assert self.offset is None

        self.base.calc_bottom_up_offsets()
        self.offset = self.base.offset + self.typ_.base.decl_bitSize * self.start

    def print_bit_descriptions(self, name, start_bit):
        self.base.print_bit_descriptions(name, start_bit)

    def print_wiring_diagram(self, start_bit):
        self.base.print_wiring_diagram(start_bit)



class mt_PlugExpr_BitArray(mt_PlugExpr):
    is_lhs = False
    decl_bitSize = 0    # consumes no space!

    def __init__(self, bitSize, val):
        assert type(val) == int
        assert (val >> bitSize) == 0

        self.typ_         = mt_PlugDecl_ArrayOf(plugType_bit, bitSize)
        self.val          = val

    def __repr__(self):
        return f"mt_PlugExpr_BitArray: bitSize={self.decl_bitSize} val={self.val}"
    def print_tree(self, prefix):
        print(f"{prefix}{self}")

    def convert_to_metatype(self, side):
        return self

    def calc_sizes(self):
        self.typ_.calc_sizes()

    def calc_top_down_offsets(self, offset):
        pass
    def calc_bottom_up_offsets(self):
        pass

    # this type represents a *value* which will be connected or init'd to a plug
    def print_bit_descriptions(self, name, start_bit):
        pass
    def print_wiring_diagram(self, start_bit):
        pass



class mt_PlugExpr_Bit(mt_PlugExpr):
    leafNode     = True
    typ_         = plugType_bit
    decl_bitSize = 0    # consumes no space!
    is_lhs       = False

    def __init__(self, val):
        assert val in [0,1]
        self.val = val

    def __repr__(self):
        return f"mt_PlugExpr_Bit: val={self.val}"
    def print_tree(self, prefix):
        print(f"{prefix}{self}")

    def convert_to_metatype(self, side):
        return self

    def calc_sizes(self):
        self.typ_.calc_sizes()

    def calc_top_down_offsets(self, offset):
        pass
    def calc_bottom_up_offsets(self):
        pass

    # this type represents a *value* which will be connected or init'd to a plug
    def print_bit_descriptions(self, name, start_bit):
        pass
    def print_wiring_diagram(self, start_bit):
        pass



class mt_PlugExpr_EQ(mt_PlugExpr):
    is_lhs = False

    def __init__(self, lineInfo, lft,op,rgt, single_bit_result=False):
        self.lineInfo = lineInfo

        assert isinstance(lft, mt_PlugExpr)
        assert isinstance(rgt, mt_PlugExpr) or isinstance(rgt, mt_StaticExpr)

        self.lft  = lft
        self.op   = op
        self.rgt  = rgt

        if single_bit_result:
            self.typ_ = plugType_bit
        else:
            self.typ_ = lft.typ_

        self.decl_bitSize = None
        self.offset       = None

    def print_tree(self, prefix):
        print(f"{prefix}mt_PlugExpr_EQ:")
        print(f"{prefix}  lft:")
        self.lft.print_tree(prefix+"    ")

        if type(self.rgt) == int:
            print(f"{prefix}  rgt: {self.rgt}")
        else:
            print(f"{prefix}  rgt:")
            self.rgt.print_tree(prefix+"    ")

        print(f"{prefix}  offset: {self.offset}")

    def convert_to_metatype(self, side):
        return self

    def calc_sizes(self):
        if self.decl_bitSize == "in progress":
            assert False    # TODO: report cyclic declaration
        if self.decl_bitSize is not None:
            return
        self.decl_bitSize = "in progress"

        self.lft.calc_sizes()
        self.rgt.calc_sizes()

        if isinstance(self.rgt, mt_StaticExpr):
            self.rgt = self.rgt.resolve_static_expr()

            if type(self.rgt) not in [int,bool]:
                TODO()    # report syntax error
            if type(self.rgt) == int:
                if self.rgt < 0 or (self.rgt >> self.lft.typ_.decl_bitSize) != 0:
                    TODO()    # report syntax error

            if type(self.rgt) == bool:
                self.rgt = 1 if self.rgt else 0

            # TODO: do better type checking when the rhs was a StaticExpr.  See ConnStmt for reference

        elif self.lft.typ_ != self.rgt.typ_:
            TODO()     # report syntax error

        if type(self.rgt) in [int,bool]:
            rgtSize = 0
        else:
            rgtSize = self.rgt.decl_bitSize

        # answer can be 1 bit (single_bit_result=True) or same as input exprs
        self.decl_bitSize = self.lft.decl_bitSize + rgtSize + self.typ_.decl_bitSize

    def calc_top_down_offsets(self, offset):
        assert self.offset is None

        self.lft.calc_top_down_offsets(offset)
        if isinstance(self.rgt, mt_PlugExpr):
            self.rgt.calc_top_down_offsets(offset + self.lft.decl_bitSize)

        if type(self.rgt) in [int,bool]:
            rgtSize = 0
        else:
            rgtSize = self.rgt.decl_bitSize

        self.offset = offset + self.lft.decl_bitSize + rgtSize

#        print(f"TOP-DOWN OFFSETS (EQ) : {offset} : sizes {self.lft.decl_bitSize} {self.rgt.decl_bitSize if type(self.rgt) != int else '<int>'} : {self.lft.offset} {self.rgt.offset if type(self.rgt) != int else '---'}")

    def calc_bottom_up_offsets(self):
        self.lft.calc_bottom_up_offsets()
        if isinstance(self.rgt, mt_PlugExpr):
            self.rgt.calc_bottom_up_offsets()

    def print_bit_descriptions(self, name, start_bit):
        self.lft.print_bit_descriptions(name, start_bit)
        if isinstance(self.rgt, mt_PlugExpr):
            self.rgt.print_bit_descriptions(name, start_bit)

        if self.typ_.decl_bitSize == 1:
            endStr = ""
        else:
            endStr = f"{start_bit+self.offset+self.typ_.decl_bitSize}"
        print(f"# {start_bit+self.offset:6d} {endStr:6s} {name}._{self.op}_{start_bit + self.offset}")

    def print_wiring_diagram(self, start_bit):
        self.lft.print_wiring_diagram(start_bit)

        if isinstance(self.rgt, mt_PlugExpr):
            self.rgt.print_wiring_diagram(start_bit)
            rgtStr = f"{start_bit + self.rgt.offset}"
        else:
            rgtStr = f"int({self.rgt})"

        print(f"logic {start_bit+self.offset} <= {start_bit+self.lft.offset} {self.op} {rgtStr} size {self.typ_.decl_bitSize}    # {self.lineInfo}")



class mt_PlugExpr_Logic(mt_PlugExpr):
    is_lhs = False

    def __init__(self, lineInfo, lft,op,rgt, single_bit_result=False):
        self.lineInfo = lineInfo

        assert isinstance(lft, mt_PlugExpr)
        assert isinstance(rgt, mt_PlugExpr) or isinstance(rgt, mt_StaticExpr)

        self.lft  = lft
        self.op   = op
        self.rgt  = rgt

        if single_bit_result:
            self.typ_ = plugType_bit
        else:
            self.typ_ = lft.typ_

        self.decl_bitSize = None
        self.offset       = None

    def print_tree(self, prefix):
        print(f"{prefix}mt_PlugExpr_Logic:   op: {self.op}")
        print(f"{prefix}  lft:")
        self.lft.print_tree(prefix+"    ")
        print(f"{prefix}  rgt:")
        self.rgt.print_tree(prefix+"    ")
        print(f"{prefix}  offset: {self.offset}")

    def convert_to_metatype(self, side):
        return self

    def calc_sizes(self):
        if self.decl_bitSize == "in progress":
            assert False    # TODO: report cyclic declaration
        if self.decl_bitSize is not None:
            return
        self.decl_bitSize = "in progress"

        self.lft.calc_sizes()
        self.rgt.calc_sizes()

        if isinstance(self.rgt, mt_StaticExpr):
            self.rgt = self.rgt.resolve_static_expr()

            if type(self.rgt) != int:
                TODO()    # report syntax error
            if self.rgt < 0 or (self.rgt >> self.lft.typ_.decl_bitSize) != 0:
                TODO()    # report syntax error

        elif self.lft.typ_ != self.rgt.typ_:
            TODO()     # report syntax error

        if type(self.rgt) == int:
            rgtSize = 0
        else:
            rgtSize = self.rgt.decl_bitSize

        # answer can be 1 bit (single_bit_result=True) or same as input exprs
        self.decl_bitSize = self.lft.decl_bitSize + rgtSize + self.typ_.decl_bitSize

    def calc_top_down_offsets(self, offset):
        assert self.offset is None

        self.lft.calc_top_down_offsets(offset)
        if isinstance(self.rgt, mt_PlugExpr):
            self.rgt.calc_top_down_offsets(offset + self.lft.decl_bitSize)

        if type(self.rgt) == int:
            rgtSize = 0
        else:
            rgtSize = self.rgt.decl_bitSize

        self.offset = offset + self.lft.decl_bitSize + rgtSize

#        print(f"TOP-DOWN OFFSETS (Logic) : {offset} : sizes {self.lft.decl_bitSize} {self.rgt.decl_bitSize} : {self.lft.offset} {self.rgt.offset}")

    def calc_bottom_up_offsets(self):
        self.lft.calc_bottom_up_offsets()
        if isinstance(self.rgt, mt_PlugExpr):
            self.rgt.calc_bottom_up_offsets()

    def print_bit_descriptions(self, name, start_bit):
        self.lft.print_bit_descriptions(name, start_bit)
        if isinstance(self.rgt, mt_PlugExpr):
            self.rgt.print_bit_descriptions(name, start_bit)

        if self.typ_.decl_bitSize == 1:
            endStr = ""
        else:
            endStr = f"{start_bit+self.offset+self.typ_.decl_bitSize}"
        print(f"# {start_bit+self.offset:6d} {endStr:6s} {name}._{self.op}_{self.offset}")

    def print_wiring_diagram(self, start_bit):
        self.lft.print_wiring_diagram(start_bit)

        if isinstance(self.rgt, mt_PlugExpr):
            self.rgt.print_wiring_diagram(start_bit)
            rgtStr = f"{start_bit + self.rgt.offset}"
        else:
            rgtStr = f"int({self.rgt})"

        print(f"logic {start_bit+self.offset} <= {start_bit+self.lft.offset} {self.op} {rgtStr} size {self.typ_.decl_bitSize}    # {self.lineInfo}")



class mt_PlugExpr_CONCAT(mt_PlugExpr):
    is_lhs = False

    def __init__(self, lineInfo, lft,rgt):
        self.lineInfo = lineInfo

        if not isinstance(lft, mt_PlugExpr):
            TODO()    # report syntax error
        if not isinstance(rgt, mt_PlugExpr):
            TODO()    # report syntax error

        assert type(lft.typ_) == mt_PlugDecl_ArrayOf
        assert type(rgt.typ_) == mt_PlugDecl_ArrayOf
        if lft.typ_.base != rgt.typ_.base:
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
        print(f"{prefix}  typ_:")
        self.typ_.print_tree(prefix+"    ")
        print(f"{prefix}  offset: {self.offset}")

    def convert_to_metatype(self, side):
        return self

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
        assert self.offset is None

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

    def print_wiring_diagram(self, start_bit):
        self.lft.print_wiring_diagram(start_bit)
        self.rgt.print_wiring_diagram(start_bit)

        print(f"conn {start_bit+self.offset} <= {start_bit+self.lft.offset} size {self.lft.typ_.decl_bitSize}    # {self.lineInfo}")
        print(f"conn {start_bit+self.offset+self.lft.typ_.decl_bitSize} <= {start_bit+self.rgt.offset} size {self.rgt.typ_.decl_bitSize}    # {self.lineInfo}")



class mt_PlugExpr_NOT(mt_PlugExpr):
    is_lhs = False

    def __init__(self, lineInfo, rgt):
        self.lineInfo = lineInfo

        assert isinstance(rgt, mt_PlugExpr)
        self.rgt  = rgt
        self.typ_ = rgt.typ_
        self.decl_bitSize = None
        self.offset       = None

    def print_tree(self, prefix):
        print(f"{prefix}mt_PlugExpr_NOT:")
        self.rgt.print_tree(prefix+"  ")

    def convert_to_metatype(self, side):
        return self

    def calc_sizes(self):
        if self.decl_bitSize == "in progress":
            assert False    # TODO: report cyclic declaration
        if self.decl_bitSize is not None:
            return
        self.decl_bitSize = "in progress"

        self.typ_.decl_bitSize
        self.rgt.calc_sizes()
        self.decl_bitSize = self.rgt.decl_bitSize + self.typ_.decl_bitSize

    def calc_top_down_offsets(self, offset):
        assert self.offset is None
        self.rgt.calc_top_down_offsets(offset)
        self.offset = offset + self.rgt.decl_bitSize

    def calc_bottom_up_offsets(self):
        self.rgt.calc_bottom_up_offsets()

    def print_bit_descriptions(self, name, start_bit):
        self.rgt.print_bit_descriptions(name, start_bit)

        start = start_bit + self.offset

        assert self.typ_.decl_bitSize >= 1
        if self.typ_.decl_bitSize == 1:
            end = ""
        else:
            end = f"{start_bit+self.offset+self.typ_.decl_bitSize}"

        print(f"# {start:6d} {end:6s} {name}._NOT_{start}")

    def print_wiring_diagram(self, start_bit):
        self.rgt.print_wiring_diagram(start_bit)
        print(f"logic {start_bit+self.offset} <= NOT {start_bit+self.rgt.offset} size {self.typ_.decl_bitSize}    # {self.lineInfo}")

