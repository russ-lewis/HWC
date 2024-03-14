
class ASTNode:
    def print_tree(self, prefix):
        assert False, f"Need to override this in the child class: {type(self)}"

    # default value for the base class
    leafNode = False

    def populate_name_scopes(self):
        assert False, f"Need to override this in the child class: {type(self)}"
    def resolve_name_lookups(self):
        assert False, f"Need to override this in the child class: {type(self)}"
    def convert_exprs_to_metatypes(self):
        assert False, f"Need to override this in the child class: {type(self)}"
    def calc_sizes(self):
        assert False, f"Need to override this in the child class: {type(self)}"
    def  calc_top_down_offsets(self, offset):
        assert False, f"Need to override this in the child class: {type(self)}"
    def calc_bottom_up_offsets(self):
        assert False, f"Need to override this in the child class: {type(self)}"
    def print_bit_descriptions(self, name, start_bit):
        assert False, f"Need to override this in the child class: {type(self)}"
    def print_wiring_diagram(self, start_bit):
        assert False, f"Need to override this in the child class: {type(self)}"



from ast_expr_metatypes import *;



class g_File(ASTNode):
    def __init__(self, nameScope, decls):
        assert type(nameScope) == NameScope
        super().__init__()
        self.nameScope = nameScope
        self.decls     = decls
    def __repr__(self):
        return f"ast.File({self.decls})"

    def print_tree(self, prefix):
        print(f"{prefix}FILE:")
        for d in self.decls:
            d.print_tree(prefix+"  ")

    def populate_name_scopes(self):
        for d in self.decls:
            assert type(d) == g_PartOrPlugDecl    # TODO: someday, support functions and static constants

            self.nameScope.add(d.name, d)
            d.populate_name_scopes()

    def resolve_name_lookups(self):
        for d in self.decls:
            d.resolve_name_lookups()

    def convert_exprs_to_metatypes(self):
        for d in self.decls:
            d.convert_exprs_to_metatypes()

    def calc_sizes(self):
        # files don't have sizes, not even if it's the root file of the
        # compilation; the size of the "entire compilation" is the size
        # of the main *part* inside that file.  So we won't calculate one.
        # But of course, we must recurse into all of our declarations, and
        # calculate the sizes and offsets for all of them!
        for d in self.decls:
            d.calc_sizes()

    def calc_top_down_offsets(self, offset):
        assert offset is None
        for d in self.decls:
            d.calc_top_down_offsets(None)

    def calc_bottom_up_offsets(self):
        for d in self.decls:
            d.calc_bottom_up_offsets()



class g_PartOrPlugDecl(ASTNode):
    def __init__(self, isPart, ns_pub, name, stmts):
        assert type(ns_pub) == NameScope
        self.pub_nameScope = ns_pub
        self.isPart        = isPart
        self.name          = name
        self.stmts         = stmts
        self.decl_bitSize  = None
    def __repr__(self):
        return f"ast.g_PartDecl({self.name}, {self.stmts})"

    def print_tree(self, prefix):
        print(f"{prefix}PART-OR-PLUG DECL: isPart={self.isPart} name={self.name} id={id(self)}")
        for d in self.stmts:
            d.print_tree(prefix+"  ")
            print(f"{prefix}    decl_bitSize: {d.decl_bitSize}")


    def populate_name_scopes(self):
        for s in self.stmts:
            s.populate_name_scopes()

    def resolve_name_lookups(self):
        for s in self.stmts:
            s.resolve_name_lookups()

    def convert_exprs_to_metatypes(self):
        for d in self.stmts:
            d.convert_exprs_to_metatypes()

    def calc_sizes(self):
        if self.decl_bitSize == "in progress":
            assert False    # TODO: report cyclic declaration
        if self.decl_bitSize is not None:
            return
        self.decl_bitSize = "in progress"

        for s in self.stmts:
            s.calc_sizes()
        self.decl_bitSize = sum(s.decl_bitSize for s in self.stmts)

    def calc_top_down_offsets(self, offset):
        assert offset is None

        running_offset = 0
        for s in self.stmts:
            if s.decl_bitSize > 0:
                s.calc_top_down_offsets(running_offset)
                running_offset += s.decl_bitSize

    def calc_bottom_up_offsets(self):
        for s in self.stmts:
            s.calc_bottom_up_offsets()

    def print_bit_descriptions(self, name, start_bit):
        for s in self.stmts:
            s.print_bit_descriptions(name, start_bit)

    def print_wiring_diagram(self, start_bit):
        for s in self.stmts:
            s.print_wiring_diagram(start_bit)



class g_DeclStmt(ASTNode):
    def __init__(self, ns_pub,ns_pri, prefix, isMem, typ_, name, initVal):
        assert                   type(ns_pub) == NameScope
        assert ns_pri is None or type(ns_pri) == NameScope
        self.pub_nameScope = ns_pub
        self.pri_nameScope = ns_pri
        self.prefix        = prefix
        self.isMem         = isMem
        self.typ_          = typ_
        self.name          = name
        self.initVal       = initVal
        self.decl_bitSize  = None
        self.offset        = None
    def __repr__(self):
        return f"ast.DeclStmt({self.prefix}, mem={self.isMem}, {self.typ_}, {self.name}, init={self.initVal})"

    def print_tree(self, prefix):
        print(f"{prefix}DECL STATEMENT: name={self.name} prefix={self.prefix} isMem={self.isMem} id={id(self)}")

        if self.typ_.leafNode:
            print(f"{prefix}  type: {repr(self.typ_)}")
        else:
            print(f"{prefix}  type:")
            self.typ_.print_tree(prefix+"    ")

        if self.initVal is None:
            print(f"{prefix}  initVal: None")
        elif self.initVal.leafNode:
            print(f"{prefix}  initVal: {repr(self.initVal)}")
        else:
            print(f"{prefix}  initVal:")
            self.initVal.print_tree(prefix+"    ")

        print(f"{prefix}  decl_bitSize: {self.decl_bitSize}")
        print(f"{prefix}  offset      : {self.offset}")


    def populate_name_scopes(self):
        # declarations always add to the private nameScope.  But we only add to
        # the public nameScope if this is a public declaration.  (Note that
        # public declarations are not legal inside block statements.)

        self.pri_nameScope.add(self.name, self)

        if self.prefix == "public":
            if self.pub_nameScope is None:
                TODO()    # report syntax error
            self.pub_nameScope.add(self.name, self)

    def resolve_name_lookups(self):
        self.typ_.resolve_name_lookups()
        if self.initVal is not None:
            self.initVal.resolve_name_lookups()

    def convert_exprs_to_metatypes(self):
        self.typ_ = self.typ_.convert_to_metatype("right")

        if   isinstance(self.typ_, mt_PlugDecl):
            pass
        elif isinstance(self.typ_, mt_PartDecl):
            assert     self.prefix == "subpart"
            assert not self.isMem
        else:
            TODO()    # report syntax error

        if self.initVal is not None:
            self.initVal = self.initVal.convert_to_metatype("right")

            # if there is a type mismatch between the initVal and the
            # declaration, we need to build a converter for that.  So far,
            # I only support NUM->bit and NUM->bit[].  Are there any other
            # cases to handle in the future?
            if self.typ_ != self.initVal.typ_:
                if type(self.initVal) == mt_StaticExpr_NumExpr and self.typ_ == plugType_bit:
                    if self.initVal.num not in [0,1]:
                        TODO()    # report syntax error, cannot assign anything to a bit except 0,1
                    self.initVal = mt_PlugExpr_Bit(self.initVal.num)

                if type(self.initVal)  == mt_StaticExpr_NumExpr and \
                   type(self.typ_)     == mt_PlugDecl_ArrayOf   and \
                        self.typ_.base ==    plugType_bit:
                    dest_wid = self.typ_.len_
                    if self.initVal.num < 0 or (self.initVal.num >> dest_wid) != 0:
                        TODO()    # report syntax error, value doesn't fit
                    self.initVal = mt_PlugExpr_BitArray(dest_wid, self.initVal.num)

    def calc_sizes(self):
        if self.decl_bitSize == "in progress":
            assert False    # TODO: report cyclic declaration
        if self.decl_bitSize is not None:
            return
        self.decl_bitSize = "in progress"

        self.typ_.calc_sizes()

        if self.isMem:
            # the type of a memory cell *MUST* be plug, never a part
            assert isinstance(self.typ_, mt_PlugDecl)

        # if the type of the var doesn't match the type of the expression, then
        # we need to build a converter.  I haven't thought about how to do
        # that, yet.  Maybe build a wrapper expression at an earlier phase?
        if self.initVal is not None and self.typ_ != self.initVal.typ_:
            print("ABOUT TO CRASH.  DECLARATION INIT PLUGTYPE MISMATCH")
            print()
            self.typ_.print_tree("")
            print()
            self.initVal.typ_.print_tree("")
            print()

            assert False    # TODO

        if self.isMem == False:
            self.decl_bitSize = self.typ_.decl_bitSize
        else:
            self.decl_bitSize = self.typ_.decl_bitSize*2

    def calc_top_down_offsets(self, offset):
        assert type(offset) == int and offset >= 0
        self.offset = offset

        # a type reference can certainly have complex expressions inside of it,
        # but it cannot possibly have any *runtime* expressions.  So I don't
        # need to assign any offsets to any of its expressions; they are all
        # decls.
        assert isinstance(self.typ_, mt_PlugDecl) or isinstance(self.typ_, mt_PartDecl)

        if self.initVal is not None:
            soFar = self.typ_.decl_bitSize
            if self.isMem:
                soFar *= 2
            self.initVal.calc_top_down_offsets(offset + soFar)

    def calc_bottom_up_offsets(self):
        if self.initVal is not None:
            self.initVal.calc_bottom_up_offsets()

    def print_bit_descriptions(self, name, start_bit):
        if not self.isMem:
            self.typ_.print_bit_descriptions(f"{name}.{self.name}", start_bit + self.offset)
        else:
            self.typ_.print_bit_descriptions(f"{name}.{self.name}(r)", start_bit + self.offset)
            self.typ_.print_bit_descriptions(f"{name}.{self.name}(w)", start_bit+self.typ_.decl_bitSize + self.offset)

    def print_wiring_diagram(self, start_bit):
        if self.prefix == "subpart":
            assert type(self.typ_) == mt_PartDecl_Code
            self.typ_.code.print_wiring_diagram(start_bit + self.offset)

        if self.isMem:
            assert isinstance(self.typ_, mt_PlugDecl)
            print(f"mem r {start_bit + self.offset} w {start_bit + self.offset + self.typ_.decl_bitSize} size {self.typ_.decl_bitSize}    # TODO: line number")

        if self.initVal is not None:
            if type(self.initVal) == mt_PlugExpr_Bit:
                assert self.typ_ == plugType_bit
                initVal = self.initVal.val
                size    = 1
            elif type(self.initVal) == mt_PlugExpr_BitArray:
                assert type(self.typ_)           == mt_PlugDecl_ArrayOf
                assert      self.typ_.base       == plugType_bit
                assert self.initVal.decl_bitSize == self.typ_.len_
                initVal = self.initVal.val
                size    = self.typ_.len_
            else:
                assert False

            print(f"conn {start_bit + self.offset} <= int({initVal}) size {size}    # TODO: line number")



class g_ConnStmt(ASTNode):
    def __init__(self, lhs,rhs):
        self.lhs          = lhs
        self.rhs          = rhs
        self.decl_bitSize = None
    def __repr__(self):
        return f"ast.ConnStmt({self.lhs}, {self.rhs})"

    def print_tree(self, prefix):
        print(f"{prefix}CONN STATEMENT:")

        if self.lhs.leafNode:
            print(f"{prefix}  lhs: {repr(self.lhs)}")
        else:
            print(f"{prefix}  lhs:")
            self.lhs.print_tree(prefix+"    ")

        if self.rhs.leafNode:
            print(f"{prefix}  rhs: {repr(self.rhs)}")
        else:
            print(f"{prefix}  rhs:")
            self.rhs.print_tree(prefix+"    ")

    def populate_name_scopes(self):
        pass    # this statement does not have any declarations inside it
    def resolve_name_lookups(self):
        self.lhs.resolve_name_lookups()
        self.rhs.resolve_name_lookups()

    def convert_exprs_to_metatypes(self):
        self.lhs = self.lhs.convert_to_metatype("left")
        self.rhs = self.rhs.convert_to_metatype("right")

        if self.lhs.is_lhs == False:
            print(self.lhs)
            TODO()     # report syntax error

    def calc_sizes(self):
        if self.decl_bitSize == "in progress":
            assert False    # TODO: report cyclic declaration
        if self.decl_bitSize is not None:
            return
        self.decl_bitSize = "in progress"

        self.lhs.calc_sizes()
        self.rhs.calc_sizes()

        if isinstance(self.lhs, mt_PlugExpr) == False or \
           isinstance(self.rhs, mt_PlugExpr) == False:
            assert False    # TODO: implement other variants

        # if the type of the var doesn't match the type of the expression, then
        # we need to build a converter.  I haven't thought about how to do
        # that, yet.  Maybe build a wrapper expression at an earlier phase?
        if self.lhs.typ_ != self.rhs.typ_:
            assert False    # TODO

        self.decl_bitSize = self.lhs.decl_bitSize + self.rhs.decl_bitSize

    def calc_top_down_offsets(self, offset):
        self.lhs.calc_top_down_offsets(offset)
        self.rhs.calc_top_down_offsets(offset + self.lhs.decl_bitSize)

    def calc_bottom_up_offsets(self):
        self.lhs.calc_bottom_up_offsets()
        self.rhs.calc_bottom_up_offsets()

    def print_bit_descriptions(self, name, start_bit):
        if self.lhs.decl_bitSize > 0:
            self.lhs.print_bit_descriptions(name, start_bit)
        if self.rhs.decl_bitSize > 0:
            rgt_start = start_bit + self.lhs.decl_bitSize
            self.rhs.print_bit_descriptions(name, rgt_start)

    def print_wiring_diagram(self, start_bit):
        self.lhs.print_wiring_diagram(start_bit)
        self.rhs.print_wiring_diagram(start_bit + self.lhs.decl_bitSize)

        assert isinstance(self.lhs, mt_PlugExpr)
        assert isinstance(self.rhs, mt_PlugExpr)
        assert self.lhs.is_lhs

        print(f"conn {start_bit+self.lhs.offset} <= {start_bit+self.rhs.offset} size {self.lhs.typ_.decl_bitSize}    # TODO: line number")



class g_AssertStmt(ASTNode):
    def __init__(self, expr):
        self.expr = expr

    def populate_name_scopes(self):
        pass

    def resolve_name_lookups(self):
        self.expr.resolve_name_lookups()

    def convert_exprs_to_metatypes(self):
        self.expr = self.expr.convert_to_metatype("right")

    def calc_sizes(self):
        self.expr.calc_sizes()
        self.decl_bitSize = self.expr.decl_bitSize

    def calc_top_down_offsets(self, offset):
        self.expr.calc_top_down_offsets(offset)

    def calc_bottom_up_offsets(self):
        self.expr.calc_bottom_up_offsets()

    def print_bit_descriptions(self, name, start_bit):
        self.expr.print_bit_descriptions(name, start_bit)

    def print_wiring_diagram(self, start_bit):
        self.expr.print_wiring_diagram(start_bit)
        print(f"assert {start_bit + self.expr.offset}    # TODO: line number")



class g_BinaryExpr(ASTNode):
    def __init__(self, lft, op, rgt):
        self.lft = lft
        self.op  = op
        self.rgt = rgt

    def resolve_name_lookups(self):
        self.lft.resolve_name_lookups()
        self.rgt.resolve_name_lookups()

    def convert_to_metatype(self):
        self.lft = self.lft.convert_to_metatype("right")
        self.rgt = self.rgt.convert_to_metatype("right")

        if   self.op == "==":
            return mt_PlugExpr_Eq(self.lft, self.rgt)
        else:
            TODO()      # add support for more operators



class g_UnaryExpr(ASTNode):
    def __init__(self, op, rgt):
        self.op  = op
        self.rgt = rgt

    def resolve_name_lookups(self):
        self.rgt.resolve_name_lookups()

    def convert_to_metatype(self, side):
        self.rgt = self.rgt.convert_to_metatype("right")

        if   self.op == "!":
            return mt_PlugExpr_NOT(self.rgt)
        else:
            TODO()      # add support for more operators



class NameScope:
    def __init__(self, parent):
        super().__init__()
        self.parent    = parent
        self.directory = {}

    def add(self, name, obj):
        assert obj is not None
        if self.search(name) is not None:
            assert False, "report syntax error"
        self.directory[name] = obj

    def search(self, name):
        if name in self.directory:
            return self.directory[name]
        elif self.parent is None:
            return None
        else:
            return self.parent.search(name)



class g_IntType_(ASTNode):
    leafNode = True

    def __repr__(self):
        return "int"

    def resolve_name_lookups(self):
        pass
    def calc_sizes(self):
        assert False    # TODO: audit and port to the new design doc
g_IntType_.singleton = g_IntType_()
def IntType():
    return g_IntType_.singleton



class g_IdentExpr(ASTNode):
    leafNode  = True

    def __init__(self, nameScope, name):
        self.nameScope = nameScope
        self.name   = name
        self.target = None
    def __repr__(self):
        if self.target is None:
            return f"IDENT={self.name} target=None"
        else:
            return f"IDENT={self.name} target ID={id(self.target)}"

    def resolve_name_lookups(self):
        self.target = self.nameScope.search(self.name)
        if self.target is None:
            assert False, "report syntax error"

    def convert_to_metatype(self, side):
        # an IDENT (as a primary expression, not the right-hand side of a
        # dot-expr) can refer to:
        #   1) The first part of a file name (maybe all of it)
        #   2) The name of a plug or part declaration, in this file (or aliased into it)
        #   3) A public or private declaration within the current scope, or any enclosing scope (all the way up to the file scope, maybe)

        if False:   # TODO: handle case 1
            TODO()

        elif type(self.target) == g_PartOrPlugDecl:     # case 2
            if self.target.isPart:
                return mt_PartDecl_Code(self.target)
            else:
                return mt_PlugDecl_Code(self.target)

        elif type(self.target) == g_DeclStmt:      # case 3
            if   isinstance(self.target.typ_, mt_PartDecl):
                return mt_PartExpr_Var(self.target)
            elif isinstance(self.target.typ_, mt_PlugDecl):
                var = mt_PlugExpr_Var(self.target)

                if self.target.isMem == False:
                    return var

                else:
                    if side == "right":
                        offset_cb = lambda: 0
                    else:
                        assert side == "left"
                        offset_cb = lambda: var.typ_.decl_bitSize

                    return mt_PlugExpr_SubsetOf(var, offset_cb, self.target.typ_)

            elif type(self.target.typ_) == g_PartOrPlugDecl:
                TODO()   # handle IDENTs that come before their declarations

            else:
                TODO()

        else:
            assert False    # unexpected type

    def calc_sizes(self):
        assert False    # will never get here, is replaced by a metatype



class g_NumExpr(ASTNode):
    leafNode = True

    def __init__(self, num_txt):
        self.num = int(num_txt)
    def __repr__(self):
        return f"NUM={self.num}"

    def resolve_name_lookups(self):
        pass

    def convert_to_metatype(self):
        return mt_StaticExpr_NumExpr(self.num)



class g_Unresolved_Single_Index_Expr(ASTNode):
    def __init__(self, nameScope, base, indx):
        self.nameScope = nameScope
        self.base      = base
        self.indx      = indx

    def print_tree(self, prefix):
        print(f"{prefix}URSIE:")

        if self.base.leafNode:
            print(f"{prefix}  base: {repr(self.base)}")
        else:
            print(f"{prefix}  base:")
            self.base.print_tree(prefix+"    ")

        if self.indx.leafNode:
            print(f"{prefix}  indx: {repr(self.indx)}")
        else:
            print(f"{prefix}  indx:")
            self.indx.print_tree(prefix+"    ")


    def resolve_name_lookups(self):
        self.base.resolve_name_lookups()
        self.indx.resolve_name_lookups()

    def convert_to_metatype(self, side):
        base = self.base.convert_to_metatype(side)
        len_ = self.indx.convert_to_metatype("right")

        if type(len_) != mt_StaticExpr_NumExpr:
            TODO()    # need to resolve values of complex expressions
        len_ = len_.num

        if   isinstance(base, mt_PlugDecl):
            return mt_PlugDecl_ArrayOf(base,len_)
        elif isinstance(base, mt_PartDecl):
            return mt_PartDecl_ArrayOf(base,len_)

        elif isinstance(base, mt_PlugExpr):
            TODO()
        elif isinstance(base, mt_PartExpr):
            TODO()

        else:
            assert False    # TODO: unexpected case

    def calc_sizes(self):
        assert False, "If you get here, then you forgot to call resolve() on this object after name resolution, and then to save the resolved function into the enclosing object."



class g_ArraySlice(ASTNode):
    def __init__(self, base, start,end):
        # NOTE: no nameScope required, since we have already resolved names
        self.base  = base
        self.start = start
        self.end   = end

