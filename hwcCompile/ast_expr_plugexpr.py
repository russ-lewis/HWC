
from ast_expr_metatypes import *
import ast



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
        self.typ_.calc_sizes()

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

    def get_wiring_offset_and_len_from_indx(self, indx):
        # should only be called on array-type variables.
        assert type(self.typ_) == mt_PlugDecl_ArrayOf
        assert indx >= 0
        assert indx <  self.typ_.len_

        retval_offset = self.offset + indx * self.typ_.base.decl_bitSize
        retval_len    = self.typ_.len_ - indx
        return (retval_offset, retval_len)



class mt_PlugExpr_Dot(mt_PlugExpr):
    def __init__(self, base, target):
        assert isinstance(base, mt_PlugExpr) or isinstance(base, mt_PartExpr), base
        assert isinstance(target.typ_, mt_PlugDecl), target.typ_

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

    def convert_to_metatype(self, side):
        self.base = self.base.convert_to_metatype(side)
        self.typ_ = self.typ_.convert_to_metatype(side)
        return self

    def calc_sizes(self):
        self.base.calc_sizes()

        # our 'target' field doesn't need to do calc_sizes because it's a
        # declaration; sizes are handled where it was declared, not where
        # it gets used.
        self.target.calc_sizes()

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

        self.is_lhs = self.base.is_lhs

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
    def __init__(self, lineInfo, base, indx):
        self.lineInfo = lineInfo

        self.base = base
        self.indx = indx

        self.is_lhs = base.is_lhs

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



class mt_PlugExpr_MaskedSelect(mt_PlugExpr):
    is_lhs = False

    def __init__(self, lineInfo, arr, mask):
        self.lineInfo = lineInfo

        self.arr  = arr
        self.mask = mask

        assert isinstance(self.mask, mt_PlugExpr), (self.mask, type(self.mask))

        assert type(arr.typ_) == mt_PlugDecl_ArrayOf
        self.typ_ = arr.typ_.base

        self.decl_bitSize = None

    def print_tree(self, prefix):
        print(f"{prefix}mt_PlugExpr_MaskedSelect:")
        print(f"{prefix}  arr:")
        self.arr.print_tree(prefix+"    ")
        print(f"{prefix}  mask:")
        self.mask.print_tree(prefix+"    ")
        print(f"{prefix}  typ_:")
        self.typ_.print_tree(prefix+"    ")

    def resolve_name_lookups(self, ns_pri):
        self.arr .resolve_name_lookups(ns_pri)
        self.mask.resolve_name_lookups(ns_pri)

    def convert_to_metatype(self, side):
        return self

    def calc_sizes(self):
        if self.decl_bitSize == "in progress":
            assert False    # TODO: report cyclic declaration
        if self.decl_bitSize is not None:
            return
        self.decl_bitSize = "in progress"

        self.arr .calc_sizes()
        self.mask.calc_sizes()

        if type(self.arr .typ_) != mt_PlugDecl_ArrayOf:
            raise HWCCompile_SyntaxError(self.lineInfo, "The base of a masked_select() expression must be an array")
        if type(self.mask.typ_) != mt_PlugDecl_ArrayOf or self.mask.typ_.base != plugType_bit:
            raise HWCCompile_SyntaxError(self.lineInfo, "The mask of a masked_select() expression must be a bit[]")

        if self.mask.typ_.len_ < self.arr.typ_.len_:
            raise HWCCompile_SyntaxError(self.lineInfo, f"The length of the mask, in a masked_select() expression, must be no shorter than the base array.  base_len={self.arr.typ_.len_} mask_len={self.mask.typ_.len_}")

        # if the size of the base array is less than the decode length, then we
        # will check the remaining bits against zero, and assert.  But if there
        # is a perfect match, we'll just add NullStmt to make it easier to
        # handle.

        if self.mask.typ_.len_ == self.arr.typ_.len_:
            self.errchk = ast.g_NullStmt()

        else:
            lft = TODO()    # not sure how to build the 'lft' term for the EQ.
                            # Its offset is based on our bit offset (which
                            # isn't known yet).
            rgt = 0
            eq = mt_PlugExpr_EQ(self.lineInfo,
                                lft,"==",rgt,
                                single_bit_result=True)

            self.errchk = ast.g_AssertStmt(self.lineInfo, eq)

        self.errchk.calc_sizes()

        # this much for the output buffer that we'll write into
        dest_sz = self.arr.typ_.base.decl_bitSize

        # this much for the error check/assert
        errchk_sz = self.errchk.decl_bitSize

        # this much for the underlying expressions that started it all
        arr_sz  = self.arr .decl_bitSize
        mask_sz = self.mask.decl_bitSize

        self.internal_offsets = {"dest"  : 0,
                                 "errchk": dest_sz,
                                 "arr"   : dest_sz + errchk_sz,
                                 "mask"  : dest_sz + errchk_sz + arr_sz}
        self.decl_bitSize =                dest_sz + errchk_sz + arr_sz + mask_sz

    def calc_top_down_offsets(self, offset):
        self.offset = offset
        self.errchk.calc_top_down_offsets(offset + self.internal_offsets["errchk"])
        self.arr   .calc_top_down_offsets(offset + self.internal_offsets["arr"])
        self.mask  .calc_top_down_offsets(offset + self.internal_offsets["mask"])

    def calc_bottom_up_offsets(self):
        self.errchk.calc_bottom_up_offsets()
        self.arr   .calc_bottom_up_offsets()
        self.mask  .calc_bottom_up_offsets()

    def print_bit_descriptions(self, name, start_bit):
        start = start_bit + self.offset
        end   = start_bit + self.offset + self.arr.typ_.base.decl_bitSize
        print(f"# {start} {end} {name}._maskedSelect_{start}")

        self.errchk.print_bit_descriptions(name, start_bit)
        self.arr   .print_bit_descriptions(name, start_bit)
        self.mask  .print_bit_descriptions(name, start_bit)

    def print_wiring_diagram(self, start_bit):
        self.arr   .print_wiring_diagram(start_bit)
        self.mask  .print_wiring_diagram(start_bit)
        self.errchk.print_wiring_diagram(start_bit)

        dst_off = start_bit + self.offset
        dst_sz  = self.arr.typ_.base.decl_bitSize
        arr_off = start_bit + self.arr.offset
        arr_len = self.arr.typ_.len_
        msk_off = self.mask.offset
        assert self.mask.typ_.len_ >= arr_len

        print(f"maskedSelect {dst_off} size {dst_sz} <--masked_select-- {arr_off} mask {msk_off} elem_count {arr_len}")



class mt_PlugExpr_ArraySlice(mt_PlugExpr):
    def __init__(self, lineInfo, base, start,end):
        self.lineInfo = lineInfo

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
        self.typ_ = mt_PlugDecl_ArrayOf(self.lineInfo, base.typ_.base, None)

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

    def get_wiring_offset_and_len_from_indx(self, indx):
        assert indx >= 0
        assert indx <  self.typ_.len_

        retval_offset = self.offset + indx * self.typ_.base.decl_bitSize
        retval_len    = self.typ_.len_ - indx
        return (retval_offset, retval_len)



class mt_PlugExpr_BitArray(mt_PlugExpr):
    is_lhs = False
    decl_bitSize = 0    # consumes no space!

    def __init__(self, lineInfo, bitSize, val):
        assert type(val) == int
        assert (val >> bitSize) == 0

        self.typ_         = mt_PlugDecl_ArrayOf(lineInfo, plugType_bit, bitSize)
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
            print(self.lft.typ_, self.rgt.typ_, self.lineInfo)
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



# this type represnts something very much like an array, except that it is not
# expected to be physically contiguous in memory.  So it's a lot like ArrayOf,
# except that it doesn't have an offset in the traditional sense.  Instead, it
# has an array (with at least two elements), which are both ArrayOf using
# compatible types (but probably not the same length).
#
# Indexing into this type indexes into exactly one of the underlying ArrayOf
# types, resulting in an expression which is of the base type.
#
# Slicing this type chops through the various ArrayOf elements; sometimes, the
# entire slice will land inside a single underlying ArrayOf, and thus this
# essentially becomes slicing into that ArrayOf - but other times, the slice
# may cross multiple ArrayOf's, and thus the result will also be Discontig.
#
# Discontig expressions can be used in connections, on either side; the
# connection must be subdivided into multiple sub-connections, such that
# neither end is discontiguous.  Similarly, discontig expressions can be used
# in Unary and Binary expressions; the various operations are broken up into
# contiguous sub-sections.
#
# ----
#
# So, why does this expression type exist?  First, for concatenation
# expressions.  The first implementation of concatenation required creation
# of a temporary buffer; we read the various sub-arrays into the big, joined
# buffer.  This was not ideal, but it worked well.  But when we added
# Discontig, we dispensed with the temporary buffer; we can use a Discontig
# as the rhs (someday: lhs) of a connection, and send the bits directly to
# their destination.
#
# But the real reason that we created this type was for arrays of flags.  When
# we have arrays of flag variables, we need to be able to build an expression
# which represents "the right side of all the flags" or "the left side of all
# the flags".  This is conceptually an array of bits, but physically is not.
# Thus, the 'typ_' field of a Discontig will be an mt_PlugDecl_ArrayOf, but
# the Discontig object will *NOT* ever have an 'offset' field (so that we
# don't accidentally use it as if it was a contiguous range).

class mt_PlugExpr_Discontig(mt_PlugExpr):
    def __init__(self, lineInfo, pieces):
        self.lineInfo = lineInfo

        assert type(pieces) == list and len(pieces) > 0

        # all of the pieces should have the same side, and they must all be
        # arrays of some base type
        for p in pieces:
            assert isinstance(p, mt_PlugExpr)
            assert p.is_lhs == pieces[0].is_lhs
            assert type(p.typ_) == mt_PlugDecl_ArrayOf
            assert p.typ_.base == pieces[0].typ_.base

        # inherit the lhs and typ_ fields from the pieces
        self.is_lhs = pieces[0].is_lhs
        self.typ_   = mt_PlugDecl_ArrayOf(self.lineInfo, pieces[0].typ_.base, None)    # we will set the length later, when we know it

        self.pieces = pieces

        self.offset       = "discontig"    # we will never change it from this
        self.decl_bitSize = None

    def print_tree(self, prefix):
        print(f"{prefix}mt_PlugExpr_Discontig:")

        print(f"{prefix}  typ_:")
        self.typ_.print_tree(prefix+"    ")

        for i in range(len(self.pieces)):
            print(f"{prefix}  pieces: [{i}] of {len(self.pieces)}:")
            self.pieces[i].print_tree(prefix+"    ")

    def convert_to_metatype(self, side):
        return self    # the sub-expressions were already metatypes in the constructor

    def calc_sizes(self):
        if self.decl_bitSize == "in progress":
            assert False    # TODO: report cyclic declaration
        if self.decl_bitSize is not None:
            return
        self.decl_bitSize = "in progress"

        for p in self.pieces:
            p.calc_sizes()
            assert type(p.typ_.len_) == int and p.typ_.len_ >0, (p, p.typ_.len_, type(p.typ_))

        self.typ_.len_ = sum(p.typ_.len_ for p in self.pieces)
        self.typ_.calc_sizes()

        # decl_bitSize is however much we need to evaluate the two
        # sub-expressions (could be as little as 0 each), plus the size of
        # the destination buffer to hold the concatenated data (definitely
        # not zero!)
        self.decl_bitSize = sum(p.decl_bitSize for p in self.pieces)

        for p in self.pieces:
            assert type(p.typ_) == mt_PlugDecl_ArrayOf

    def calc_top_down_offsets(self, offset):
        running_offset = offset
        for p in self.pieces:
            p.calc_top_down_offsets(running_offset)
            running_offset += p.decl_bitSize

    def calc_bottom_up_offsets(self):
        for p in self.pieces:
            p.calc_bottom_up_offsets()

    def print_bit_descriptions(self, name, start_bit):
        for p in self.pieces:
            p.print_bit_descriptions(name, start_bit)

    def print_wiring_diagram(self, start_bit):
        for p in self.pieces:
            p.print_wiring_diagram(start_bit)

    def get_wiring_offset_and_len_from_indx(self, indx):
        indx_soFar = 0
        for p in self.pieces:
            assert indx_soFar <= indx

            if indx_soFar + p.typ_.len_ <= indx:
                indx_soFar += p.typ_.len_
                continue

            # found it!
            delta_indx = indx-indx_soFar
            return p.get_wiring_offset_and_len_from_indx(delta_indx)

        # should be impossible to get here
        assert False



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



class mt_PlugExpr_Decode(mt_PlugExpr):
    def __init__(self, indx):
        assert type(indx.typ_)     == mt_PlugDecl_ArrayOf
        assert      indx.typ_.base == plugType_bit
        self.indx = indx

    def print_tree(self, prefix):
        print(f"{prefix}mt_PlugExpr_Decode:")
        print(f"{prefix}  indx:")
        self.indx.print_tree(prefix+"    ")

    def calc_sizes(self):
        self.indx.calc_sizes()

        self.decl_bitSize = (1 << self.indx.typ_.len_) + self.indx.decl_bitSize

        self.typ_ = mt_PlugDecl_ArrayOf(None, plugType_bit, self.decl_bitSize)
        self.typ_.calc_sizes()

    def calc_top_down_offsets(self, offset):
        self.indx.calc_top_down_offsets(offset)
        self.offset = offset + self.indx.decl_bitSize

    def calc_bottom_up_offsets(self):
        self.indx.calc_bottom_up_offsets()

    def print_bit_descriptions(self, name, start_bit):
        len_  = (1 << self.indx.typ_.len_)
        start = start_bit + self.offset
        end   = start_bit + self.offset + len_
        print(f"# {start} {end} {name}._decode_{start}")

        self.indx.print_bit_descriptions(name, start_bit)

    def print_wiring_diagram(self, start_bit):
        self.indx.print_wiring_diagram(start_bit)

        dst_off = start_bit + self.offset
        dst_sz  = (1 << self.indx.typ_.len_)
        src_off = start_bit + self.indx.offset
        src_sz  =       self.indx.typ_.len_

        print(f"decode {dst_off} size {dst_sz} <--decode-- {src_off} size {src_sz}")

