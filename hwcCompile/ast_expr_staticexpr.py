
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



class mt_StaticExpr_Bool(mt_StaticExpr):
    typ_ = staticType_bool

    def __init__(self, val):
        assert val in ["true","false"]
        self.val = (val == "true")
    def dup(self):
        return self

    def convert_to_metatype(self, side):
        return self
    def calc_sizes(self):
        pass
    def resolve_static_expr(self):
        return self.val



# these are static expressions, taking two int inputs, which produce int results
class mt_StaticExpr_BinaryOp_Int(mt_StaticExpr):
    typ_ = staticType_int

    def __init__(self, lineInfo, lft,op,rgt):
        self.lineInfo = lineInfo
        self.lft      = lft
        self.op       = op
        self.rgt      = rgt

    def print_tree(self, prefix):
        print(f"{prefix}mt_StaticExpr_BinaryOp_Int: op: {self.op}    {self.lineInfo}")
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

        if self.op == "+":
            return lft + rgt
        elif self.op == "-":
            return lft - rgt
        elif self.op == "*":
            return lft * rgt
        elif self.op == "/":
            return lft // rgt
        elif self.op == "%":
            return lft % rgt

        elif self.op == "&":
            return lft & rgt
        elif self.op == "|":
            return lft | rgt
        elif self.op == "^":
            return lft ^ rgt

        else:
            assert False



# these are expressions, taking two inputs (ints, bools, part decls, or plug decls)
# and compares them, producing a bool answer
class mt_StaticExpr_BinaryOp_Bool(mt_StaticExpr):
    typ_ = staticType_bool

    def __init__(self, lineInfo, lft,op,rgt):
        self.lineInfo = lineInfo

        if isinstance(lft, mt_PartDecl):
            if op not in ["==","!="]:
                raise HWCCompile_SyntaxError(self.lineInfo, "The operator '{op}' is not valid with a part type")
            if not isinstance(rgt, mt_PartDecl):
                raise HWCCompile_SyntaxError(self.lineInfo, "Part types can only be compared to other part types")

        elif isinstance(lft, mt_PlugDecl):
            if op not in ["==","!="]:
                raise HWCCompile_SyntaxError(self.lineInfo, "The operator '{op}' is not valid with a plug type")
            if not isinstance(rgt, mt_PlugDecl):
                raise HWCCompile_SyntaxError(self.lineInfo, "Plug types can only be compared to other plug types")

        else:
            if not isinstance(lft, mt_StaticExpr) or not isinstance(rgt, mt_StaticExpr):
                if op in ["==","!="]:
                    raise HWCCompile_SyntaxError(self.lineinfo, "The operator '{op}' can only compare similar types to each other")
                else:
                    raise HWCCompile_SyntaxError(self.lineinfo, "The operator '{op}' can only compare integers")
            if lft.typ_ != rgt.typ_:
                raise HWCCompile_SyntaxError(self.lineInfo, "Cannot compare mismatched static types")

        self.lft  = lft
        self.op   = op
        self.rgt  = rgt

    def print_tree(self, prefix):
        print(f"{prefix}mt_StaticExpr_BinaryOp_Bool: op {self.op}")
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

    def resolve_static_expr(self):
        if isinstance(self.lft, mt_StaticExpr):
            assert isinstance(self.rgt, mt_StaticExpr)
            self.lft = self.lft.resolve_static_expr()
            self.rgt = self.rgt.resolve_static_expr()

        if self.op in ["==","!="]:
            if self.op == "==":
                return self.lft == self.rgt
            else:
                return self.lft != self.rgt

        # for all other ops, we *must* have integer inputs
        assert type(self.lft) == int
        assert type(self.rgt) == int

        if self.op == "<":
            return self.lft < self.rgt
        elif self.op == "<=":
            return self.lft < self.rgt
        elif self.op == ">":
            return self.lft < self.rgt
        elif self.op == ">=":
            return self.lft < self.rgt

        else:
            assert False



class mt_StaticExpr_BitwiseNOT_Int(mt_StaticExpr):
    def __init__(self, lineInfo, rgt):
        self.lineInfo = lineInfo

        assert isinstance(rgt, mt_StaticExpr)
        self.rgt  = rgt
        self.typ_ = rgt.typ_

    def print_tree(self, prefix):
        print(f"{prefix}mt_StaticExpr_BitwiseNOT_Int:")
        self.rgt.print_tree(prefix+"  ")

    def convert_to_metatype(self, side):
        return self

    def calc_sizes(self):
        self.rgt.calc_sizes()

    def resolve_static_expr(self):
        rgt = self.rgt.resolve_static_expr()
        if type(rgt) != int:
            raise HWC_SyntaxError(self.lineInfo, "The ~ operator is only valid on runtime bit[] and static int")
        return ~rgt



class mt_StaticExpr_BooleanNOT_Bool(mt_StaticExpr):
    def __init__(self, lineInfo, rgt):
        self.lineInfo = lineInfo

        assert isinstance(rgt, mt_StaticExpr)
        self.rgt  = rgt
        self.typ_ = rgt.typ_

    def print_tree(self, prefix):
        print(f"{prefix}mt_StaticExpr_BooleanNOT_Bool:")
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

