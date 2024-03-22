
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
    def calc_top_down_offsets(self, offset):
        assert False, f"Need to override this in the child class: {type(self)}"
    def calc_bottom_up_offsets(self):
        assert False, f"Need to override this in the child class: {type(self)}"
    def print_bit_descriptions(self, name, start_bit):
        assert False, f"Need to override this in the child class: {type(self)}"
    def print_wiring_diagram(self, start_bit):
        assert False, f"Need to override this in the child class: {type(self)}"



class LineInfo:
    def __init__(self, line,col,len_):
        self.line  = line
        self.col   = col
        self.len_  = len_
    def __str__(self):
        return f"FILE:{self.line}:{self.col}"

class LineRange:
    def __init__(self, start,endIncl):
        self.start   = start
        self.endIncl = endIncl
    def __str__(self):
        if self.start == self.endIncl:
            return f"FILE:{self.start}"
        else:
            return f"FILE:{self.start}-{self.endIncl}"



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

    def deliver_if_conditions(self):
        for d in self.decls:
            d.deliver_if_conditions()

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


    def deliver_if_conditions(self):
        for s in self.stmts:
            s.deliver_if_conditions(None)

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



class g_BlockStmt(ASTNode):
    def __init__(self, ns_pub,ns_pri, stmts):
        self.pub_nameScope = ns_pub
        self.pri_nameScope = ns_pri
        self.stmts         = stmts
        self.decl_bitSize  = None

    def deliver_if_conditions(self, cond):
        for s in self.stmts:
            s.deliver_if_conditions(cond)

    def populate_name_scopes(self):
        for s in self.stmts:
            s.populate_name_scopes()

    def resolve_name_lookups(self):
        for s in self.stmts:
            s.resolve_name_lookups()

    def convert_exprs_to_metatypes(self):
        for s in self.stmts:
            s.convert_exprs_to_metatypes()

    def calc_sizes(self):
        for s in self.stmts:
            s.calc_sizes()
        self.decl_bitSize = sum(s.decl_bitSize for s in self.stmts)

    def calc_top_down_offsets(self, offset):
        running_offset = offset
        for s in self.stmts:
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
        assert ns_pub is None or type(ns_pub) == NameScope
        assert                   type(ns_pri) == NameScope
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

        print(f"{prefix}  offset      : {self.offset}")
        print(f"{prefix}  decl_bitSize: {self.decl_bitSize}")


    def deliver_if_conditions(self, cond):
        pass

    def populate_name_scopes(self):
        # declarations always add to the private nameScope.  But we only add to
        # the public nameScope if this is a public declaration.  (Note that
        # public declarations are not legal inside block statements.)

        self.pri_nameScope.add(self.name, self)

        if self.prefix == "public":
            if self.pub_nameScope is None:
                print()
                self.print_tree("")
                print()
                TODO()    # report syntax error: can only declare public field at top scope
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

            # BUGFIX:
            #
            # Originally, I tried to convert static expressions to the
            # the appropriate type here.  However, as I thought about
            # complex static expressions (including those that might
            # include sizeof() expressions), I realized that I wouldn't
            # be able to resolve all static expressions until calc_sizes()
            # ran.  So I deferred the work until then.

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

        # if there is an initVal and it is a static expression, then convert
        # it to its Python type.
        if self.initVal is not None and isinstance(self.initVal, mt_StaticExpr):
            self.initVal = self.initVal.resolve_static_expr()

        # if there is a type mismatch between the initVal and the
        # declaration, we need to build a converter for that.  So far,
        # I only support NUM->bit and NUM->bit[].  Are there any other
        # cases to handle in the future?
        if self.initVal is not None and (type(self.initVal) == int or self.typ_ != self.initVal.typ_):
            if type(self.initVal) == int and self.typ_ == plugType_bit:
                if self.initVal not in [0,1]:
                    TODO()    # report syntax error, cannot assign anything to a bit except 0,1
                self.initVal = mt_PlugExpr_Bit(self.initVal)

            if type(self.initVal)  == int                 and \
               type(self.typ_)     == mt_PlugDecl_ArrayOf and \
                    self.typ_.base ==    plugType_bit:

                assert type(self.typ_.len_) == int
                dest_wid = self.typ_.len_

                if self.initVal < 0 or (self.initVal >> dest_wid) != 0:
                    TODO()    # report syntax error, value doesn't fit
                self.initVal = mt_PlugExpr_BitArray(dest_wid, self.initVal)

        if self.initVal is not None:
            self.initVal.calc_sizes()

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

        if self.initVal is None:
            initSize = 0
        else:
            initSize = self.initVal.decl_bitSize

        if self.isMem == False:
            self.decl_bitSize = initSize + self.typ_.decl_bitSize
        else:
            self.decl_bitSize = initSize + self.typ_.decl_bitSize*2

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

        if self.initVal is not None:
            self.initVal.print_bit_descriptions(name, start_bit)

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
                initStr = f"int({self.initVal.val})"
                size    = 1

            elif type(self.initVal) == mt_PlugExpr_BitArray:
                assert type(self.typ_)                == mt_PlugDecl_ArrayOf
                assert      self.typ_.base            == plugType_bit
                assert self.initVal.typ_.decl_bitSize == self.typ_.len_
                initStr = f"int({self.initVal.val})"
                size    = self.typ_.len_

            elif isinstance(self.initVal, mt_PlugExpr):
                self.initVal.print_wiring_diagram(start_bit)

                assert self.initVal.typ_ == self.typ_
                initStr = f"{self.initVal.offset}"
                size    = self.typ_.decl_bitSize

            else:
                assert False

            print(f"conn {start_bit + self.offset} <= {initStr} size {size}    # TODO: line number")



class g_ConnStmt(ASTNode):
    def __init__(self, lineRange, lhs,rhs):
        self.cond         = "not delivered yet"
        self.lhs          = lhs
        self.rhs          = rhs
        self.decl_bitSize = None
        self.lineRange = lineRange
    def __repr__(self):
        return f"ast.ConnStmt({self.lhs}, {self.rhs})"

    def deliver_if_conditions(self, cond):
        self.cond = cond

    def print_tree(self, prefix):
        print(f"{prefix}CONN STATEMENT:")

        if self.cond is None:
            print(f"{prefix}  cond: None")
        else:
            print(f"{prefix}  cond:")
            self.cond.print_tree(prefix+"    ")

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
        if self.cond is not None:
            self.cond.resolve_name_lookups()

        self.lhs .resolve_name_lookups()
        self.rhs .resolve_name_lookups()

    def convert_exprs_to_metatypes(self):
        if self.cond is not None:
            self.cond = self.cond.convert_to_metatype("right")

            # TODO: add support for statically-resolved runtime if() conditions
            if not isinstance(self.cond, mt_PlugExpr):
                TODO()    # report syntax error
            if self.cond.typ_ != plugType_bit:
                TODO()    # report syntax error

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

        if self.cond is not None:
            self.cond.calc_sizes()

        if isinstance(self.rhs, mt_StaticExpr):
            self.rhs = self.rhs.resolve_static_expr()

        # handle "assign integer to bit or bit[]" cases.  This code is
        # copy-pasted from the initVal handling in DeclStmt.
        #
        # TODO: unify the two with a common function or type

        if type(self.rhs) == int and self.lhs.typ_ == plugType_bit:
            if self.rhs not in [0,1]:
                TODO()    # report syntax error, cannot assign anything to a bit except 0,1
            self.rhs = mt_PlugExpr_Bit(self.rhs)

        if type(self.rhs)          == int                 and \
           type(self.lhs.typ_)     == mt_PlugDecl_ArrayOf and \
                self.lhs.typ_.base ==    plugType_bit:

            assert type(self.lhs.typ_.len_) == int
            dest_wid = self.lhs.typ_.len_

            if self.rhs < 0 or (self.rhs >> dest_wid) != 0:
                TODO()    # report syntax error, value doesn't fit
            self.rhs = mt_PlugExpr_BitArray(dest_wid, self.rhs)

        if isinstance(self.lhs, mt_PlugExpr) == False or \
           isinstance(self.rhs, mt_PlugExpr) == False:
            assert False    # TODO: implement other variants

        self.lhs.calc_sizes()
        self.rhs.calc_sizes()

        # if the type of the var doesn't match the type of the expression, then
        # we need to build a converter.  I haven't thought about how to do
        # that, yet.  Maybe build a wrapper expression at an earlier phase?
        if self.lhs.typ_ != self.rhs.typ_:
            if isinstance(self.lhs, mt_PlugExpr) and isinstance(self.rhs, mt_PlugExpr):
                print()
                self.print_tree("")
                print()
                self.lhs.typ_.print_tree("")
                print()
                self.rhs.typ_.print_tree("")
                print()
                TODO()    # report syntax error

            print()
            self.print_tree("")
            print()
            self.lhs.typ_.print_tree("")
            print()
            self.rhs.typ_.print_tree("")
            print()
            assert False    # TODO

        if self.cond is None:
            cond_size = 0
        else:
            cond_size = self.cond.decl_bitSize
        self.decl_bitSize = cond_size + self.lhs.decl_bitSize + self.rhs.decl_bitSize

    def calc_top_down_offsets(self, offset):
        if self.cond is None:
            running_offset = offset
        else:
            self.cond.calc_top_down_offsets(offset)
            running_offset = offset + self.cond.decl_bitSize

        self.lhs.calc_top_down_offsets(running_offset)
        self.rhs.calc_top_down_offsets(running_offset + self.lhs.decl_bitSize)

    def calc_bottom_up_offsets(self):
        if self.cond is not None:
            self.cond.calc_bottom_up_offsets()
        self.lhs .calc_bottom_up_offsets()
        self.rhs .calc_bottom_up_offsets()

    def print_bit_descriptions(self, name, start_bit):
        running_start_bit = start_bit

        if self.cond is not None and self.cond.decl_bitSize > 0:
            self.cond.print_bit_descriptions(name, running_start_bit)
            running_start_bit += self.cond.decl_bitSize

        if self.lhs.decl_bitSize > 0:
            self.lhs.print_bit_descriptions(name, running_start_bit)
            running_start_bit += self.lhs.decl_bitSize

        if self.rhs.decl_bitSize > 0:
            self.rhs.print_bit_descriptions(name, running_start_bit)

    def print_wiring_diagram(self, start_bit):
        running_start_bit = start_bit

        if self.cond is not None:
            self.cond.print_wiring_diagram(running_start_bit)
            running_start_bit += self.cond.decl_bitSize

        self.lhs.print_wiring_diagram(running_start_bit)
        running_start_bit += self.lhs.decl_bitSize

        self.rhs.print_wiring_diagram(running_start_bit)

        assert isinstance(self.lhs, mt_PlugExpr)
        assert isinstance(self.rhs, mt_PlugExpr)
        assert self.lhs.is_lhs

        if self.cond is not None:
            assert isinstance(self.cond, mt_PlugExpr)
            assert self.cond.typ_ == plugType_bit
            cond = f" cond {self.cond.offset}"
        else:
            cond = ""

        if   type(self.rhs) in [mt_PlugExpr_Bit, mt_PlugExpr_BitArray]:
            fromStr = f"int({self.rhs.val})"
        else:
            fromStr = f"{start_bit+self.rhs.offset}"

        print(f"conn {start_bit+self.lhs.offset} <= {fromStr} size {self.lhs.typ_.decl_bitSize}{cond}    # {self.lineRange}")



# used to give a non-None stmt for missing else blocks
class g_NullStmt(ASTNode):
    decl_bitSize = 0
    offset = 0

    def deliver_if_conditions(self, cond):
        pass
    def resolve_name_lookups(self):
        pass
    def convert_exprs_to_metatypes(self):
        pass
    def calc_sizes(self):
        pass
    def calc_top_down_offsets(self, offset):
        pass
    def calc_bottom_up_offsets(self):
        pass
    def print_bit_descriptions(self, name, start_bit):
        pass
    def print_wiring_diagram(self, start_bit):
        pass



class g_RuntimeIfStmt(ASTNode):
    def __init__(self, lineInfo_whole, lineInfo_else,
                       cond, true_stmt, fals_stmt):

        self.lineRange_whole = lineInfo_whole
        self. lineInfo_else  = lineInfo_else

        self.cond      = cond
        self.true_stmt = true_stmt
        self.fals_stmt = fals_stmt     # could be None

    def print_tree(self, prefix):
        print(f"{prefix}g_RuntimeIfStmt:")

        if type(self.cond) != str:
            print(f"{prefix}  cond:")
            self.cond.print_tree(prefix+"    ")
        else:
            print(f"{prefix}  true_cond:")
            self.true_cond.print_tree(prefix+"    ")

            if self.fals_cond is not None:
                print(f"{prefix}  fals_cond:")
                self.fals_cond.print_tree(prefix+"    ")


        print(f"{prefix}  true_stmt:")
        self.true_stmt.print_tree(prefix+"    ")

        if self.fals_stmt is not None:
            print(f"{prefix}  fals_stmt:")
            self.fals_stmt.print_tree(prefix+"    ")

    def deliver_if_conditions(self, cond):
        # we must build two conditions, which are sent recursively down through
        # the sub-statements: one for true, and its negation for false.
        #
        # Our original design simply treated the true expression as a simple
        # expression that we could evaluate, and the NOT as the negation of
        # same.  But this caused duplicate bits in our tree because we would
        # traverse through the same sub-expression multiple times (one for
        # true, another for false).  So we tried to implement once-only
        # expression evaluation - but we still were *consuming bit space* for
        # all of the copies.
        #
        # We then considered using an mt_PlugExpr_Alias class, which would
        # simply mirror an existing expression; it basically would be the
        # equivalent for mt_PlugExpr_Var, but for temporary expressions.  The
        # original expression would allocate space and would generate bits, and
        # multiple users could read the result.  (The idea was that the false
        # copy of the expression would be the alias, and the true would be the
        # actual expression.)
        #
        # But then I realized that, inside a single side of the if(), we are
        # likely to have multiple connection statements or assertions that must
        # use the same expression, which would cause this design to fail.  I
        # thought about using Alias on *both* sides, but how then would we
        # ensure that there was a non-Alias version of the expression somewhere
        # in the tree?
        #
        # In the end, I decided to use the double-Alias strategy, but to then
        # hang both of those conditions on this object; then, it would be the
        # if() statement itself which was responsible for ensuring that the
        # conditions allocate real space in the bit-space and have the proper
        # entries in the wiring diagram; both sides would have Alias objects,
        # which could read those bits but not allocate space for them.
        #
        # Is this wasteful?  Will we sometimes generate condition bits which
        # are never used?  Possibly.  But this should be rare.  How many HWC
        # programs will include if() statements that have no connections inside
        # them?  I'm willing to generate sub-optimal wiring diagrams for such
        # oddballs.  And you'll see that, if the else doesn't exist, we will
        # not even generate the false condition, so that's harmless, too.


        # the condition that was given for this if() statement, in the grammar,
        # is at self.cond.  We need to create a false version of that; this
        # will do a NOT of the condition, but before we fork the condition into
        # two pieces, we must wrap an Alias around it.  Note that we keep an
        # original, non-Alias-ed version of the condition around.
        true_cond_base = self.cond
        if self.fals_stmt is not None:
            fals_cond_base = g_UnaryExpr(self.lineInfo_else, "!", mt_PlugExpr_Alias(self.cond))

        # next, if an incoming condition was given, then we update those two
        # conditions to AND in the incoming condition.  These are saved into
        # the object for later inclusion in the wiring diagram
        if cond is None:
            self.true_cond = true_cond_base
            if self.fals_stmt is not None:
                self.fals_cond = fals_cond_base
        else:
            self.true_cond = g_BinaryExpr(self.lineRange_whole, cond, "&", true_cond_base)
            if self.fals_stmt is not None:
                self.fals_cond = g_BinaryExpr(self.lineRange_whole, cond, "&", fals_cond_base)

        # each of the two conditions is wrapped in an Alias before it is sent
        # down, into the statement below.
        true_cond_alias = mt_PlugExpr_Alias(self.true_cond)
        if self.fals_stmt is not None:
            fals_cond_alias = mt_PlugExpr_Alias(self.fals_cond)
        
        # forget the original, un-joined, un-Alias-ed condition expression.
        self.cond = "delivered down the tree, do not use here anymore"

        # now that we have built 2 versions of each condition, we can push
        # those versions down the tree
        self.true_stmt.deliver_if_conditions(true_cond_alias)
        if self.fals_stmt is not None:
            self.fals_stmt.deliver_if_conditions(fals_cond_alias)

    def populate_name_scopes(self):
        pass
    def resolve_name_lookups(self):
        self.true_cond.resolve_name_lookups()
        self.true_stmt.resolve_name_lookups()

        if self.fals_stmt is not None:
            self.fals_cond.resolve_name_lookups()
            self.fals_stmt.resolve_name_lookups()

    def convert_exprs_to_metatypes(self):
        self.true_cond = self.true_cond.convert_to_metatype("right")
        self.true_stmt.convert_exprs_to_metatypes()

        if self.fals_stmt is not None:
            self.fals_cond = self.fals_cond.convert_to_metatype("right")
            self.fals_stmt.convert_exprs_to_metatypes()

    def calc_sizes(self):
        self.true_cond.calc_sizes()
        self.true_stmt.calc_sizes()
        true_size = self.true_cond.decl_bitSize + self.true_stmt.decl_bitSize

        if self.fals_stmt is not None:
            self.fals_cond.calc_sizes()
            self.fals_stmt.calc_sizes()
            fals_size = self.fals_cond.decl_bitSize + self.fals_stmt.decl_bitSize
        else:
            fals_size = 0

        self.decl_bitSize = true_size + fals_size

#        print(f"SIZES {self.true_cond.decl_bitSize} {self.true_stmt.decl_bitSize} {self.fals_cond.decl_bitSize} {self.fals_stmt.decl_bitSize}")

    def calc_top_down_offsets(self, offset):
        running_offset = offset

        self.true_cond.calc_top_down_offsets(running_offset)
        running_offset += self.true_cond.decl_bitSize

        self.true_stmt.calc_top_down_offsets(running_offset)
        running_offset += self.true_stmt.decl_bitSize

        if self.fals_stmt is not None:
            self.fals_cond.calc_top_down_offsets(running_offset)
            running_offset += self.fals_cond.decl_bitSize

            self.fals_stmt.calc_top_down_offsets(running_offset)

#        print(f"TOP-DOWN OFFSETS {offset} : sizes {self.true_cond.decl_bitSize} {self.true_stmt.decl_bitSize} {self.fals_cond.decl_bitSize} {self.fals_stmt.decl_bitSize} : {self.true_cond.offset} {self.fals_cond.offset}")

    def calc_bottom_up_offsets(self):
        self.true_cond.calc_bottom_up_offsets()
        self.true_stmt.calc_bottom_up_offsets()

        if self.fals_stmt is not None:
            self.fals_cond.calc_bottom_up_offsets()
            self.fals_stmt.calc_bottom_up_offsets()

    def print_bit_descriptions(self, name, start_bit):
        self.true_cond.print_bit_descriptions(name, start_bit)
        self.true_stmt.print_bit_descriptions(name, start_bit)

        if self.fals_stmt is not None:
            self.fals_cond.print_bit_descriptions(name, start_bit)
            self.fals_stmt.print_bit_descriptions(name, start_bit)

    def print_wiring_diagram(self, start_bit):
#        print(f"A     id={self.true_cond.offset}")
        self.true_cond.print_wiring_diagram(start_bit)
#        print(f"B     id={self.true_cond.offset}")
        self.true_stmt.print_wiring_diagram(start_bit)

        if self.fals_stmt is not None:
#            print(f"C     id={self.true_cond.offset}")
            self.fals_cond.print_wiring_diagram(start_bit)
#            print(f"D     id={self.true_cond.offset}")
            self.fals_stmt.print_wiring_diagram(start_bit)

#        print(f"E     id={self.true_cond.offset}")



class g_AssertStmt(ASTNode):
    def __init__(self, lineRange, expr):
        self.lineRange = lineRange
        self.expr = expr

    def deliver_if_conditions(self, cond):
        if cond is not None:
            self.expr = g_BinaryExpr( self.lineRange,
                                      g_UnaryExpr(self.lineRange, "!", cond),
                                      "|",
                                      self.expr )

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
        print(f"assert {start_bit + self.expr.offset}    # {self.lineRange}")



class g_BinaryExpr(ASTNode):
    def __init__(self, lineInfo, lft, op, rgt):
        self.lineInfo = lineInfo

        assert type(op) == str
        self.lft = lft
        self.op  = op
        self.rgt = rgt

        self.saved_metatype = None

    def print_tree(self, prefix):
        print(f"{prefix}g_BinaryExpr:  op: {self.op}")
        print(f"{prefix}  lft:")
        self.lft.print_tree(prefix+"    ")
        print(f"{prefix}  rgt:")
        self.rgt.print_tree(prefix+"    ")

    def resolve_name_lookups(self):
        self.lft.resolve_name_lookups()
        self.rgt.resolve_name_lookups()

    def convert_to_metatype(self, side):
        # sometimes, the same tree node is used at multiple places in
        # the tree.  We don't want to generate duplicate mt_ objects, if
        # we can avoid it!

        # TODO: when the same expression is used multiple times (and the
        #       expression has a nonzero decl_bitSize), we end up allocating
        #       bit space for every use, even though we only need a single
        #       one.  We need to get rid of that waste, someday.

        if self.saved_metatype is None:
            self.saved_metatype = self._convert_to_metatype(side)
        return self.saved_metatype

    def _convert_to_metatype(self, side):
        self.lft = self.lft.convert_to_metatype("right")
        self.rgt = self.rgt.convert_to_metatype("right")

        if   self.op in ["==","!="]:
            eq = mt_PlugExpr_EQ(self.lineInfo,
                                self.lft, "EQ", self.rgt, single_bit_result=True)

            if self.op == "==":
                return eq
            else:
                return mt_PlugExpr_NOT(self.lineInfo, eq);

        elif self.op in ["&", "&&"]:
            return mt_PlugExpr_Logic(self.lineInfo, self.lft, "AND", self.rgt)
        elif self.op in ["|", "||"]:
            return mt_PlugExpr_Logic(self.lineInfo, self.lft, "OR",  self.rgt)
        elif self.op in ["^"]:
            return mt_PlugExpr_Logic(self.lineInfo, self.lft, "XOR", self.rgt)

        elif self.op == ":":
            return mt_PlugExpr_CONCAT(self.lineInfo, self.lft, self.rgt)

        else:
            print("failed op: "+self.op)
            TODO()      # add support for more operators



class g_UnaryExpr(ASTNode):
    def __init__(self, lineInfo, op, rgt):
        self.lineInfo = lineInfo

        self.op  = op
        self.rgt = rgt

        self.saved_metatype = None

    def print_tree(self, prefix):
        print(f"{prefix}g_UnaryExpr:   op: {repr(self.op)}")
        print(f"{prefix}  rgt:")
        self.rgt.print_tree(prefix+"    ")

    def resolve_name_lookups(self):
        self.rgt.resolve_name_lookups()

    def convert_to_metatype(self, side):
        if self.saved_metatype is None:
            self.saved_metatype = self._convert_to_metatype(side)
        return self.saved_metatype

    def _convert_to_metatype(self, side):
        self.rgt = self.rgt.convert_to_metatype("right")

        if   self.op == "!":
            return mt_PlugExpr_NOT(self.lineInfo, self.rgt)
        else:
            TODO()      # add support for more operators



class NameScope:
    def __init__(self, parent):
        super().__init__()
        self.parent    = parent
        self.directory = {}

    def dump(self):
        if self.parent is None:
            prefix = ""
        else:
            prefix = self.parent.dump()

        print(f"{prefix}---- {id(self)}")
        for n in self.directory:
            print(f"{prefix}{n}")

        return prefix+"  "

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

        self.saved_metatype = None

    def __repr__(self):
        if self.target is None:
            return f"IDENT={self.name} target=None"
        else:
            return f"IDENT={self.name} target ID={id(self.target)}"
    def print_tree(self, prefix):
        print(f"{prefix}{self}")

    def resolve_name_lookups(self):
        self.target = self.nameScope.search(self.name)
        if self.target is None:
            assert False, "report syntax error"

    def convert_to_metatype(self, side):
        if self.saved_metatype is None:
            self.saved_metatype = self._convert_to_metatype(side)
        return self.saved_metatype

    def _convert_to_metatype(self, side):
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
    def print_tree(self, prefix):
        print(f"{prefix}{self}")

    def resolve_name_lookups(self):
        pass

    def convert_to_metatype(self, side):
        return mt_StaticExpr_NumExpr(self.num)



class g_DotExpr(ASTNode):
    def __init__(self, base, fieldName):
        self.base      = base
        self.fieldName = fieldName

        self.offset = None

    def resolve_name_lookups(self):
        self.base.resolve_name_lookups()

    def convert_to_metatype(self, side):
        self.base = self.base.convert_to_metatype(side)
        assert type(self.base) in [mt_PlugExpr_Var, mt_PartExpr_Var]

        self.target = self.base.typ_.code.pub_nameScope.search(self.fieldName)
        if self.target is None:
            TODO()    # report syntax error
        assert(type(self.target) == g_DeclStmt)


        # dot expressions can only look up plug fields, because (currently)
        # only plug fields can be public.
        assert(           self.target.prefix in ["", "public"])
        assert(isinstance(self.target.typ_, mt_PlugDecl))

        # we don't (yet) support public memory fields.  Should we add it?
        assert(self.target.isMem == False)

        # build an Expr object which represents the reference to the field.
        # It will calculate its offset later.
        return mt_PlugExpr_Dot(self.base, self.target)



class g_Unresolved_Single_Index_Expr(ASTNode):
    def __init__(self, nameScope, base, indx):
        self.nameScope = nameScope
        self.base      = base
        self.indx      = indx

        self.saved_metatype = None

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
        if self.saved_metatype is None:
            self.saved_metatype = self._convert_to_metatype(side)
        return self.saved_metatype

    def _convert_to_metatype(self, side):
        base         = self.base.convert_to_metatype(side)
        len_or_index = self.indx.convert_to_metatype("right")

        if   isinstance(base, mt_PlugDecl):
            return mt_PlugDecl_ArrayOf(base,len_or_index)
        elif isinstance(base, mt_PartDecl):
            return mt_PartDecl_ArrayOf(base,len_or_index)

        elif isinstance(base, mt_PlugExpr):
            if type(base.typ_) == mt_PlugDecl_ArrayOf:
                return mt_PlugExpr_ArrayIndex(base, len_or_index)
            else:
                TODO()    # report syntax error

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

        self.saved_metatype = None

    def print_tree(self, prefix):
        print(f"{prefix}g_ArraySlice:")

        print(f"{prefix}  base:")
        self.base.print_tree(prefix+"    ")

        print(f"{prefix}  start:")
        self.start.print_tree(prefix+"    ")

        if self.end is None:
            print(f"{prefix}  end: {self.end}")
        else:
            print(f"{prefix}  end:")
            self.end.print_tree(prefix+"    ")

    def resolve_name_lookups(self):
        self.base .resolve_name_lookups()
        self.start.resolve_name_lookups()
        if self.end is not None:
            self.end  .resolve_name_lookups()

    def convert_to_metatype(self, side):
        if self.saved_metatype is None:
            self.saved_metatype = self._convert_to_metatype(side)
        return self.saved_metatype

    def _convert_to_metatype(self, side):
        base  = self.base .convert_to_metatype("right")
        start = self.start.convert_to_metatype("right")
        end   = self.end  .convert_to_metatype("right") if self.end is not None else None

        if type(base.typ_) == mt_PlugDecl_ArrayOf:
            return mt_PlugExpr_ArraySlice(base, start,end)
        else:
            TODO()

