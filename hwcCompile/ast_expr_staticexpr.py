
from ast_expr_metatypes import *



class mt_StaticExpr_NumExpr(mt_StaticExpr):
    typ_ = staticType_int
    is_leaf = True

    def __init__(self, num):
        assert type(num) == int
        self.num = num
    def dup(self):
        return self
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
    typ_ = staticType_bool

    def __init__(self, val):
        assert val in ["true","false"]
        self.val = (val == "true")
    def dup(self):
        return self

    def resolve_static_expr(self):
        return self.val
    def calc_sizes(self):
        pass



class mt_StaticExpr_ADD(mt_StaticExpr):
    typ_ = staticType_int

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



class mt_StaticExpr_MUL(mt_StaticExpr):
    typ_ = staticType_int

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

        return lft * rgt



class mt_StaticExpr_MOD(mt_StaticExpr):
    typ_ = staticType_int

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



class mt_StaticExpr_CMP(mt_StaticExpr):
    typ_ = staticType_bool

    def __init__(self, lineInfo, lft,op,rgt):
        assert lft is not None and rgt is not None
        assert not isinstance(lft, mt_PlugExpr) and not isinstance(lft, mt_PlugExpr)

        if isinstance(lft, mt_PartExpr) or isinstance(lft, mt_PartExpr):
            raise HWCCompile_SyntaxError(lineInfo, "Part expressions cannot be compared.  Compare the public fields of the parts instead.")

        self.lineInfo = lineInfo

        self.lft  = lft
        self.op   = op
        self.rgt  = rgt

    def print_tree(self, prefix):
        print(f"{prefix}mt_StaticExpr_EQ:")
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
        self.lft.calc_sizes()
        self.rgt.calc_sizes()
        self.calc_sizes_has_been_called = True

    def resolve_static_expr(self):
        assert self.calc_sizes_has_been_called    # sanity check.  TODO: remove soon

        if isinstance(self.rgt, mt_StaticExpr):
            if not isinstance(self.rgt, mt_StaticExpr):
                raise HWCCommpile_SyntaxError(self.lineInfo, "Mismatched types for comparison: '{self.lft.typ_}' {self.op} '{self.rgt.typ_}'")

            lft = self.lft.resolve_static_expr()
            rgt = self.rgt.resolve_static_expr()

            if self.op == "==":
                return lft == rgt
            if self.op == "!=":
                return lft != rgt
            if self.op == "<":
                return lft < rgt
            if self.op == "<=":
                return lft < rgt
            if self.op == ">":
                return lft < rgt
            if self.op == ">=":
                return lft < rgt

            print(self.op)
            TODO()    # what is this op???

        # the other expression types can only do simple equality checking.  So
        # sanity check that the left side and right side have matching types;
        # then you can use common code throughout.

        if isinstance(self.rgt, mt_PlugDecl):
            if not isinstance(self.rgt, mt_PlugDecl):
                raise HWCCommpile_SyntaxError(self.lineInfo, "Mismatched types for comparison: '{self.lft.typ_}' {self.op} '{self.rgt.typ_}'")

        elif isinstance(self.rgt, mt_PartDecl):
            if not isinstance(self.rgt, mt_PartDecl):
                raise HWCCommpile_SyntaxError(self.lineInfo, "Mismatched types for comparison: '{self.lft.typ_}' {self.op} '{self.rgt.typ_}'")

        elif isinstance(self.rgt, mt_StaticType):
            if not isinstance(self.rgt, mt_StaticType):
                raise HWCCommpile_SyntaxError(self.lineInfo, "Mismatched types for comparison: '{self.lft.typ_}' {self.op} '{self.rgt.typ_}'")

        else:
            print(self.lft)
            TODO()    # what type is this???

        # ready to do the actual comparison
        if self.op == "==":
            return self.lft == self.rgt
        if self.op == "!=":
            return self.lft != self.rgt

        print(self.op)
        TODO()    # what is this op???

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



class mt_StaticExpr_NOT(mt_StaticExpr):
    def __init__(self, lineInfo, rgt):
        self.lineInfo = lineInfo

        assert isinstance(rgt, mt_StaticExpr)
        self.rgt  = rgt
        self.typ_ = rgt.typ_
        self.decl_bitSize = None
        self.offset       = None

    def print_tree(self, prefix):
        print(f"{prefix}mt_StaticExpr_NOT:")
        self.rgt.print_tree(prefix+"  ")

    def convert_to_metatype(self, side):
        return self

    def resolve_static_expr(self):
        rgt = self.rgt.resolve_static_expr()
        if type(rgt) != bool:
            raise HWC_SyntaxError(self.lineInfo, "The ! operator is only valid on runtime bits and static bools")
        return not rgt



class mt_StaticExpr_GetProp(mt_StaticExpr):
    typ_ = staticType_int

    def __init__(self, lineInfo, prop, exp):
        self.lineInfo = lineInfo

        assert prop in ["sizeof","len"]    # typeof must be declared as a PartDecl or PlugDecl

        self.prop = prop
        self.exp  = exp

    def print_tree(self, prefix):
        print(f"{prefix}mt_StaticExpr_GetProp:    prop: {self.prop}")
        print(f"{prefix}  exp:")
        self.exp.print_tree(prefix+"    ")

    def convert_to_metatype(self, side):
        return self

    def calc_sizes(self):
        self.exp.calc_sizes()
        self.calc_sizes_has_been_called = True

    def resolve_static_expr(self):
        assert self.calc_sizes_has_been_called    # sanity check.  TODO: remove soon

        # sanity check the expression type
        if self.prop in ["sizeof","len"]:
            if not isinstance(self.exp, mt_PlugExpr) and not isinstance(self.exp, mt_plugDecl):
                raise HWCCompile_SyntaxError(self.lineInfo, "The parameter to the built-in function {self.prop}() must be a plug expression or plug type.")

        # convert the expression to its type, if appropriate
        if self.prop in ["sizeof","len"]:
            if isinstance(self.exp, mt_PlugExpr):
                self.exp = self.exp.typ_

        # return the value
        if self.prop == "sizeof":
            assert type(self.exp.decl_bitSize) == int
            return self.exp.decl_bitSize

        elif self.prop == "len":
            if type(self.exp) != mt_PlugDecl_ArrayOf:
                raise HWCCompile_SyntaxError(self.lineInfo, "The parameter to the built-in function len() must be an array type or expression")

            assert type(self.exp.len_) == int
            return self.exp.len_

        else:
            print(self.prop, self.exp)
            TODO()    # what property is this?

