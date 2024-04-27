
class ASTNode:
    def dup(self):
        assert False, f"Need to override this in the child class: {type(self)}"

    def print_tree(self, prefix):
        assert False, f"Need to override this in the child class: {type(self)}"

    # default value for the base class
    leafNode = False

    def populate_name_scopes(self, ns_pub,ns_pri):
        assert False, f"Need to override this in the child class: {type(self)}"
    def resolve_name_lookups(self, ns_pri):
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
    def __init__(self, fil_, line,col,len_):
        self.fil_  = fil_
        self.line  = line
        self.col   = col
        self.len_  = len_
    def __str__(self):
        return f"{self.fil_}:{self.line}:{self.col}"
    def __repr__(self):
        return f"LineInfo({self})"

class LineRange:
    def __init__(self, fil_, start,endIncl):
        self.fil_    = fil_
        self.start   = start
        self.endIncl = endIncl
    def __str__(self):
        if self.start == self.endIncl:
            return f"{self.fil_}:{self.start}"
        else:
            return f"{self.fil_}:{self.start}-{self.endIncl}"
    def __repr__(self):
        return f"LineRange({self})"



class HWCCompile_SyntaxError(Exception):
    def __init__(self, lineInfo, message):
        assert lineInfo is not None
        self.lineInfo = lineInfo
        self.message  = message



from ast_expr_metatypes import *;



class g_File(ASTNode):
    def __init__(self, decls):
        self.nameScope = NameScope(None)
        self.decls     = decls
    def dup(self):
        return g_File([d.dup() for d in self.decls])

    def __repr__(self):
        return f"ast.File({self.decls})"
    def print_tree(self, prefix):
        print(f"{prefix}FILE:")
        for d in self.decls:
            d.print_tree(prefix+"  ")

    def deliver_if_conditions(self):
        for d in self.decls:
            d.deliver_if_conditions(None)

    def populate_name_scopes(self):      # File has 0 parameters, since it inherits no name scopes.
        for d in self.decls:
            assert type(d) == g_PartOrPlugDecl    # TODO: someday, support functions and static constants

            assert d.name is not None     # name is none iff part was generic instantiation, which doesn't happen here (yet!)
            self.nameScope.add(d.name, d)
            d.populate_name_scopes(self.nameScope)    # POPDecl has only 1 parmeter, since it inherits only the public scope.

    def resolve_name_lookups(self):      # File has 0 paramters
        for d in self.decls:
            d.resolve_name_lookups(self.nameScope)

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
    def __init__(self, isPart, name, stmts):
        self.pub_nameScope = None      # for external lookup of our fields
        self.pri_nameScope = None      # for passing to statements in resolve_name_lookups()
        self.isPart        = isPart
        self.name          = name      # is None iff this is a generic instantiation
        self.stmts         = stmts
        self.decl_bitSize  = None
        self.offset        = None

    def dup(self):
        assert self.pub_nameScope is None
        assert self.pri_nameScope is None
        assert self.decl_bitSize  is None

        dup_stmts = [s.dup() for s in self.stmts]
        return g_PartOrPlugDecl(self.isPart, self.name, dup_stmts)

    def __repr__(self):
        return f"ast.g_PartDecl({self.name}, {self.stmts})"

    def print_tree(self, prefix):
        print(f"{prefix}PART-OR-PLUG DECL: isPart={self.isPart} name={self.name} id={id(self)}")
        for s in self.stmts:
            s.print_tree(prefix+"  ")


    def deliver_if_conditions(self, cond):
#        # if() conditions into a part do not exist except for instantiated generic parts
#        if cond is not None:
#            TODO()    # implement me

        for s in self.stmts:
            s.deliver_if_conditions(None)

    def populate_name_scopes(self, ns_pri):
        # a part or plug declaration has *TWO* nameScope objects.  The "public"
        # nameScope is for use by external code, which is attempting to access
        # the fields of the part.  This will *only* include fields that are
        # declared public, which cannot (currently) include static variables
        # and subparts.  (Note that in a plug, *all* declarations are assumed
        # to be public.)
        #
        # The "private" nameScope is for use by internal code, to access the
        # fields and subparts declared inside this part.  Or rather, this is
        # the nameScope used for *all* lookups by code inside this part (or
        # plug).  It has the public fields, of course, and the private fields -
        # but also includes a parent pointer to the enclosing scope.
        #
        # (Why do plugs have a private nameScope for lookup, when they can't
        # have any statements other than declarations?  Because those
        # declarations have expressions inside them, and the expressions might
        # do name lookups for the fields of the plug, such as "typeof(fieldX)".
        # Plus, we're planning ahead for the future, when plugs might include
        # static-if statements.)
        #
        # When we build a new nameScope inside a part or plug (as part of an
        # if() or curly-brace statement), it is always a child of the "private"
        # nameScope.

        self.pub_nameScope = NameScope(None)      # for others, to find our fields
        self.pri_nameScope = NameScope(ns_pri)    # for our own stmts

        for s in self.stmts:
            s.populate_name_scopes(self.pub_nameScope, self.pri_nameScope)

    def resolve_name_lookups(self, ns_pri):
        assert ns_pri == self.pri_nameScope.parent
        for s in self.stmts:
            s.resolve_name_lookups(self.pri_nameScope)

    def convert_exprs_to_metatypes(self):
        for s in self.stmts:
            s.convert_exprs_to_metatypes()

    def calc_sizes(self):
        if self.decl_bitSize == "in progress":
            assert False    # TODO: report cyclic declaration
        if self.decl_bitSize is not None:
            return
        self.decl_bitSize = "in progress"

        for s in self.stmts:
            s.calc_sizes()
        self.decl_bitSize = sum(s.decl_bitSize for s in self.stmts)

    def calc_top_down_offsets(self, offset, forLoop_instOffset=None):
        # we use offsets in our parts, instead of absolute bit addresses,
        # because a part can be instantiated multiple times.  So when we lay
        # out our bits, it's always as *offsets* from the start of the part.
        #
        # For this reason (with one exception we'll talk about below), we
        # always start at offset 0 when we are recursing into a g_PartOrPlugDecl;
        # and to sanity check that our calling code isn't (accidentally) doing
        # the wrong thing (or the right thing in a fragile way), we expect them
        # to pass None to us
        #
        # But the instantiated generic parts that we use to represent the passes
        # of our for() loops are weird.  First, (unlike all other parts!)
        # they have the ability to access fields outside their own physical
        # range - both before and after.  Second, (unlike other instantiated
        # generics), each of these will only be used exactly ONCE.  (The part
        # that encloses us might be used multiple times, but that's a different
        # question.)
        #
        # After struglling with how to handle offsets to get to the fields of
        # this part which are outside the loop, I finally stumbled on the simple
        # solution:
        #    1) All of the for() loops will use the same offset-space as the
        #       fields of the enclosing part.  So nonzero starting offsets will
        #       be routine, and different instantiations of the same generic
        #       will typically have different starting offsets.
        #    2) When we generate the wiring diagram, we will use the same
        #       start_bit as the enclosing part.
        #
        # We didn't want to give up our error checking, and so we added a
        # (normally omitted) parameter, which will *only* be used in ForStmt:
        # the forLoop_instOffset.  This is just the offset, but named funny so
        # that we don't give up our sanity-checking for all the other code.

        assert offset is None, offset
        running_offset = 0 if forLoop_instOffset is None else forLoop_instOffset

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



class g_BlockStmt(ASTNode):
    def __init__(self, stmts):
        self.pri_nameScope = None
        self.stmts         = stmts
        self.decl_bitSize  = None

    def dup(self):
        assert self.pri_nameScope is None
        assert self.decl_bitSize  is None
        return g_BlockStmt([s.dup() for s in self.stmts])

    def print_tree(self, prefix):
        print(f"{prefix}g_BlockStmt:")

        for i in range(len(self.stmts)):
            print(f"{prefix}  stmts[{i}] of {len(self.stmts)}:")
            self.stmts[i].print_tree(prefix+"    ")

    def deliver_if_conditions(self, cond):
        for s in self.stmts:
            s.deliver_if_conditions(cond)

    def populate_name_scopes(self, ns_pub,ns_pri):
        # we do *NOT* pass the public NameScope along, because we don't allow
        # public fields inside block statements.  And we wrap the existing
        # private NameScope in another because block statements create new
        # name scopes.

        self.pri_nameScope = NameScope(ns_pri)
        for s in self.stmts:
            s.populate_name_scopes(None, self.pri_nameScope)

    def resolve_name_lookups(self, ns_pri):
        assert ns_pri == self.pri_nameScope.parent
        for s in self.stmts:
            s.resolve_name_lookups(self.pri_nameScope)

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
    def __init__(self, lineInfo, prefix, isMem, typ_, name, initVal):
        self.lineInfo = lineInfo

        self.prefix        = prefix
        self.isMem         = isMem
        self.name          = name
        self.initVal       = initVal
        self.decl_bitSize  = None
        self.offset        = None

        # in the worse-case scenario, we won't be able to give a useful typ_
        # until convert_exprs_to_metatypes(), because this might be an Auto
        # that inherits from the initVal.  So we'll rename the field, to ensure
        # that nobody is using this field too early.
        self.raw_typ = typ_

        # but do this one sanity check, early!
        if type(self.raw_typ) == mt_PlugDecl_Auto and self.initVal is None:
            raise HWCCompile_SyntaxError(None, "'auto' declarations must have initializer expressions")

    def dup(self):
        assert self.decl_bitSize is None
        assert self.offset       is None

        dup_typ  = self.raw_typ.dup()
        dup_init = self.initVal.dup() if self.initVal is not None else None
        return g_DeclStmt(self.lineInfo,
                          self.prefix, self.isMem,
                          dup_typ,
                          self.name,
                          dup_init)

    def __repr__(self):
        return f"ast.DeclStmt({self.prefix}, mem={self.isMem}, {self.raw_typ}, {self.name}, init={self.initVal})"

    def print_tree(self, prefix):
        print(f"{prefix}DECL STATEMENT: name={self.name} prefix={self.prefix} isMem={self.isMem} id={id(self)}")

        if self.raw_typ.leafNode:
            print(f"{prefix}  type: {repr(self.raw_typ)}")
        else:
            print(f"{prefix}  type:")
            self.raw_typ.print_tree(prefix+"    ")

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

    def populate_name_scopes(self, ns_pub,ns_pri):
        # declarations always add to the private nameScope.  But we only add to
        # the public nameScope if this is a public declaration.  (Note that
        # public declarations are not legal inside block statements.)

        ns_pri.add(self.name, self)

        if self.prefix == "public":
            if ns_pub is None:
                print()
                self.print_tree("")
                print()
                TODO()    # report syntax error: can only declare public field at top scope
            ns_pub.add(self.name, self)

    def resolve_name_lookups(self, ns_pri):
        self.raw_typ.resolve_name_lookups(ns_pri)
        if self.initVal is not None:
            self.initVal.resolve_name_lookups(ns_pri)

    def convert_exprs_to_metatypes(self):
        self.raw_typ = self.raw_typ.convert_to_metatype("right")
        if self.initVal is not None:
            self.initVal = self.initVal.convert_to_metatype("right")

        if type(self.raw_typ) != mt_PlugDecl_Auto:
            self.typ_ = self.raw_typ
        else:
            if not isinstance(self.initVal.typ_, mt_PlugDecl):
                raise HWCCompile_SyntaxError(None, "auto declarations can only be initialized with runtime plug values")    # TODO: should I support static auto as well???
            self.typ_ = self.initVal.typ_

        if   isinstance(self.typ_, mt_PlugDecl):
            pass
        elif isinstance(self.typ_, mt_PartDecl):
            assert     self.prefix == "subpart", self
            assert not self.isMem
        elif isinstance(self.typ_, mt_StaticType):
            pass
        else:
            TODO()    # report syntax error

    def calc_sizes(self):
        if self.decl_bitSize == "in progress":
            assert False    # TODO: report cyclic declaration
        if self.decl_bitSize is not None:
            return
        self.decl_bitSize = "in progress"

        if self.initVal is not None:
            self.initVal.calc_sizes()

        # if there is an initVal and it is a static expression, then convert
        # it to its Python type.
        if self.initVal is not None and isinstance(self.initVal, mt_StaticExpr):
            self.initVal = self.initVal.resolve_static_expr()

        elif isinstance(self.initVal, mt_PlugExpr):
            self.initVal.calc_sizes()

        elif self.initVal is None:
            pass

        else:
            assert False   # TODO: are there any more cases to cover?

        # if this was an 'auto' declaration *AND* the underlying expression
        # was an array, then we need to copy over the length field from the
        # initVal, which (maybe) wasn't valid until this step.
        #
        # TODO: make the len_ field in a type a lambda, maybe?  Resolved during
        #       calc_sizes()?

        if type(self.raw_typ) == mt_PlugDecl_Auto and type(self.typ_) == mt_PlugDecl_ArrayOf:
            if self.typ_.len_ is None:
                assert type(self.initVal.typ_.len_) == int
                self.typ_.len_ = self.initVal.typ_.len_

        self.typ_.calc_sizes()

        if self.isMem:
            # the type of a memory cell *MUST* be plug, never a part
            assert isinstance(self.typ_, mt_PlugDecl)

        # if there is a type mismatch between the initVal and the
        # declaration, we need to build a converter for that.  So far,
        # I only support NUM->bit and NUM->bit[].  Are there any other
        # cases to handle in the future?
        if self.initVal is not None and (type(self.initVal) == int or self.typ_ != self.initVal.typ_):
            if type(self.initVal) == int and self.typ_ == plugType_bit:
                if self.initVal not in [0,1]:
                    TODO()    # report syntax error, cannot assign anything to a bit except 0,1
                self.initVal = mt_PlugExpr_Bit(self.initVal)

            elif type(self.initVal)  == int                 and \
               type(self.typ_)     == mt_PlugDecl_ArrayOf and \
                    self.typ_.base ==    plugType_bit:

                assert type(self.typ_.len_) == int
                dest_wid = self.typ_.len_

                if self.initVal < 0 or (self.initVal >> dest_wid) != 0:
                    TODO()    # report syntax error, value doesn't fit
                self.initVal = mt_PlugExpr_BitArray(self.lineInfo, dest_wid, self.initVal)

            elif type(self.initVal) == int and self.typ_ == staticType_int:
                self.static_val = self.initVal
                self.initVal    = None

            else:
                assert False, (self.lineInfo, self.typ_.len_, self.initVal.typ_.len_)    # some other weird case.  Maybe a syntax error???

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

        if isinstance(self.typ_, mt_StaticType):
            # a static variable declaration takes no bit-space
            self.decl_bitSize = 0

        else:
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
            def print_init_conn(lhs_offset, initStr, size):
                print(f"conn {start_bit + lhs_offset} <= {initStr} size {size}    # TODO: line number")

            if type(self.initVal) == mt_PlugExpr_Bit:
                assert self.typ_ == plugType_bit
                print_init_conn(self.offset,
                                f"int({self.initVal.val})",
                                1)

            elif type(self.initVal) == mt_PlugExpr_BitArray:
                assert type(self.typ_)                == mt_PlugDecl_ArrayOf
                assert      self.typ_.base            == plugType_bit
                assert self.initVal.typ_.decl_bitSize == self.typ_.len_
                print_init_conn(self.offset,
                                f"int({self.initVal.val})",
                                self.typ_.len_)

            elif isinstance(self.initVal, mt_PlugExpr):
                self.initVal.print_wiring_diagram(start_bit)

                assert self.initVal.typ_ == self.typ_

                if type(self.initVal.offset) == int:
                    print_init_conn(self.offset,
                                    f"{start_bit + self.initVal.offset}",
                                    self.typ_.decl_bitSize)

                else:
                    assert self.initVal.offset == "discontig"
                    assert type(self.initVal.typ_) == mt_PlugDecl_ArrayOf

                    # see also the similar code in ConnStmt
                    cur_indx = 0
                    while cur_indx < self.initVal.typ_.len_:
                        offset,len_ = self.initVal.get_wiring_offset_and_len_from_indx(cur_indx)
                        assert cur_indx + len_ <= self.initVal.typ_.len_

                        print_init_conn(self.offset + cur_indx * self.initVal.typ_.base.decl_bitSize,
                                        f"{offset}",
                                        len_ * self.initVal.typ_.base.decl_bitSize)
                        cur_indx += len_

            else:
                assert False



class g_ConnStmt(ASTNode):
    def __init__(self, lineInfo, lhs,rhs):
        self.cond         = "not delivered yet"
        self.lhs          = lhs
        self.rhs          = rhs
        self.decl_bitSize = None
        self.lineInfo = lineInfo

    def dup(self):
        assert self.cond == "not delivered yet"
        assert self.decl_bitSize is None
        return g_ConnStmt(self.lineInfo, self.lhs.dup(), self.rhs.dup())

    def __repr__(self):
        return f"ast.ConnStmt({self.lhs}, {self.rhs})"

    def deliver_if_conditions(self, cond):
        self.cond = cond

    def print_tree(self, prefix):
        print(f"{prefix}CONN STATEMENT:")

        if self.cond is None or type(self.cond) == str:
            print(f"{prefix}  cond: {repr(self.cond)}")
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

    def populate_name_scopes(self, ns_pub,ns_pri):
        pass    # this statement does not have any declarations inside it

    def resolve_name_lookups(self, ns_pri):
        if self.cond is not None:
            self.cond.resolve_name_lookups(ns_pri)

        self.lhs.resolve_name_lookups(ns_pri)
        self.rhs.resolve_name_lookups(ns_pri)

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

        # we are about to handle implicit casting of integers to bit and
        # bit-array types.  But before this is possible, we need to clearly
        # understand what the left-hand type is.
        self.lhs.calc_sizes()

        # flags are *severely* restricted!
        if self.lhs.typ_ == plugType_flag:
            if self.rhs != 1:
                raise HWCCompile_SyntaxError(self.lineInfo, "The only value that can be assigned to a flag variable is the constant 1")
            self.rhs = mt_PlugExpr_Bit(self.rhs)

            print(self.lhs)
            print(self.lhs.typ_)
            TODO()    # what to do with the lhs?  Do we convert it to bit?

        # if the rhs is an integer, then look for ways to make the conversion
        #
        # TODO: unify this code with similar code in DeclStmt->iniVal

        if type(self.rhs) == int:
            if self.lhs.typ_ == plugType_bit:
                if self.rhs not in [0,1]:
                    TODO()    # report syntax error, cannot assign anything to a bit except 0,1
                self.rhs = mt_PlugExpr_Bit(self.rhs)

            elif type(self.lhs.typ_) == mt_PlugDecl_ArrayOf and self.lhs.typ_.base == plugType_bit:
                assert type(self.lhs.typ_.len_) == int, type(self.lhs.typ_.len_)
                dest_wid = self.lhs.typ_.len_

                if self.rhs < 0 or (self.rhs >> dest_wid) != 0:
                    TODO()    # report syntax error, value doesn't fit
                self.rhs = mt_PlugExpr_BitArray(self.lineInfo, dest_wid, self.rhs)

            else:
                TODO()    # report syntax error

        if type(self.rhs) == bool:
            if self.lhs.typ_ == plugType_bit:
               if self.rhs:
                   self.rhs = mt_PlugExpr_Bit(1)
               else:
                   self.rhs = mt_PlugExpr_Bit(0)
            else:
                TODO()    # report syntax error.  Can't assign true/false to bit[]

        if isinstance(self.lhs, mt_PlugExpr) == False or \
           isinstance(self.rhs, mt_PlugExpr) == False:
            assert False    # TODO: implement other variants

        self.rhs.calc_sizes()

        # if the type of the var doesn't match the type of the expression, then
        # we need to build a converter.  I haven't thought about how to do
        # that, yet.  Maybe build a wrapper expression at an earlier phase?
        if self.lhs.typ_ != self.rhs.typ_:
            if isinstance(self.lhs, mt_PlugExpr) and isinstance(self.rhs, mt_PlugExpr):
                raise HWCCompile_SyntaxError(self.lineInfo, "The lhs and rhs have different types")

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
        if self.cond is not None:
            self.cond.print_bit_descriptions(name, start_bit)
        self.lhs.print_bit_descriptions(name, start_bit)
        self.rhs.print_bit_descriptions(name, start_bit)

    def print_wiring_diagram(self, start_bit):
        if self.cond is not None:
            self.cond.print_wiring_diagram(start_bit)

        self.lhs.print_wiring_diagram(start_bit)
        self.rhs.print_wiring_diagram(start_bit)

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
            print(f"conn {start_bit+self.lhs.offset} <= int({self.rhs.val}) size {self.lhs.typ_.decl_bitSize}{cond}    # {self.lineInfo}")

        elif self.lhs.offset != "discontig" and self.rhs.offset != "discontig":
            assert type(self.lhs.offset) == int
            assert type(self.rhs.offset) == int
            print(f"conn {start_bit+self.lhs.offset} <= {start_bit+self.rhs.offset} size {self.lhs.typ_.decl_bitSize}{cond}    # {self.lineInfo}")

        else:
            # one or both sides are discontig.  If only one side is, then we'll
            # convert the other to a trivial (1-piece) discontig.

            total_len = self.lhs.typ_.len_

            if self.lhs.offset != "discontig":
                self.lhs = mt_PlugExpr_Discontig(self.lineInfo, [self.lhs])
            if self.rhs.offset != "discontig":
                self.rhs = mt_PlugExpr_Discontig(self.lineInfo, [self.rhs])

            cur_indx = 0
            while cur_indx < total_len:

                # this function call returns two values with DIFFERENT
                # SEMANTICS.  The 'offset' is the bit-space offset of the
                # beginning of the contiguous range (of whatever size) that
                # starts with the index we provide.  The length is given in
                # ENTRIES NOT BITS.  We will ask both sides what their values
                # are, at the current index, and use the shorter length.

                offset_lhs,len_lhs = self.lhs.get_wiring_offset_and_len_from_indx(cur_indx)
                offset_rhs,len_rhs = self.rhs.get_wiring_offset_and_len_from_indx(cur_indx)
                assert cur_indx + len_lhs <= total_len
                assert cur_indx + len_rhs <= total_len
                len_ = min(len_lhs, len_rhs)

                print(f"conn {start_bit+offset_lhs} <= {start_bit+offset_rhs} size {self.lhs.typ_.base.decl_bitSize * len_}{cond}    # {self.lineInfo}")

                cur_indx += len_



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

        self.lineInfo_whole = lineInfo_whole
        self. lineInfo_else  = lineInfo_else

        self.cond      = cond
        self.true_stmt = true_stmt
        self.fals_stmt = fals_stmt     # could be None

    def dup(self):
        dup_cond = self.cond.dup()
        dup_true = self.true_stmt.dup()
        dup_fals = self.fals_stmt.dup() if self.fals_stmt is not None else None
        return g_RuntimeIfStmt(self.lineInfo_whole, self.lineInfo_else,
                               dup_cond, dup_true, dup_fals)

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
            self.true_cond = g_BinaryExpr(self.lineInfo_whole, cond, "&", true_cond_base)
            if self.fals_stmt is not None:
                self.fals_cond = g_BinaryExpr(self.lineInfo_whole, cond, "&", fals_cond_base)

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

    def populate_name_scopes(self, ns_pub,ns_pri):
        # see comments in BlockStmt about why we change the NameScope objs

        self.true_ns = NameScope(ns_pri)
        self.true_stmt.populate_name_scopes(None, self.true_ns)

        if self.fals_stmt is not None:
            self.fals_ns = NameScope(ns_pri)
            self.fals_stmt.populate_name_scopes(None, self.fals_ns)

    def resolve_name_lookups(self, ns_pri):
        # the *condition* expressions should use the enclosing name scope.
        # But the statements need the interior ones.

        self.true_cond.resolve_name_lookups(ns_pri)
        self.true_stmt.resolve_name_lookups(self.true_ns)

        if self.fals_stmt is not None:
            self.fals_cond.resolve_name_lookups(ns_pri)
            self.fals_stmt.resolve_name_lookups(self.fals_ns)

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
    def __init__(self, lineInfo, is_static, expr):
        self.lineInfo = lineInfo

        self.is_static = is_static
        self.expr = expr

    def dup(self):
        return g_AssertStmt(self.lineInfo, self.is_static, self.expr.dup())

    def deliver_if_conditions(self, cond):
        # if the statement is static, then it doesn't matter what conditions
        # we are sent, because they are all runtime expressions.
        if self.is_static:
            return

        if cond is not None:
            self.expr = g_BinaryExpr( self.lineInfo,
                                      g_UnaryExpr(self.lineInfo, "!", cond),
                                      "|",
                                      self.expr )

    def populate_name_scopes(self, ns_pub,ns_pri):
        pass

    def resolve_name_lookups(self, ns_pri):
        self.expr.resolve_name_lookups(ns_pri)

    def convert_exprs_to_metatypes(self):
        self.expr = self.expr.convert_to_metatype("right")

        # static assertions must have static values.  Non-static assertions are
        # allowed to have either runtime or static values.
        if self.is_static:
            if not isinstance(self.expr, mt_StaticExpr):
                raise HWCCompile_SyntaxError(self.lineInfo, "Static assertions must resolve to static expressions.")

    def calc_sizes(self):
        self.expr.calc_sizes()

        if self.is_static:
            val = self.expr.resolve_static_expr()
            if type(val) != bool:
                raise HWCCompile_SyntaxError(self.lineInfo, "Static assertions must resolve to static boolean expressions.")
            if val == False:
                raise HWCCompile_SyntaxError(self.lineInfo, "Static assertion failed.")

            self.decl_bitSize = 0

        else:
            self.decl_bitSize = self.expr.decl_bitSize

    def calc_top_down_offsets(self, offset):
        # static assertions are NOPS after calc_sizes()
        if self.is_static:
            return

        self.expr.calc_top_down_offsets(offset)

    def calc_bottom_up_offsets(self):
        # static assertions are NOPS after calc_sizes()
        if self.is_static:
            return

        self.expr.calc_bottom_up_offsets()

    def print_bit_descriptions(self, name, start_bit):
        # static assertions are NOPS after calc_sizes()
        if self.is_static:
            return

        self.expr.print_bit_descriptions(name, start_bit)

    def print_wiring_diagram(self, start_bit):
        # static assertions are NOPS after calc_sizes()
        if self.is_static:
            return

        self.expr.print_wiring_diagram(start_bit)
        print(f"assert {start_bit + self.expr.offset}    # {self.lineInfo}")



class g_BinaryExpr(ASTNode):
    def __init__(self, lineInfo, lft, op, rgt):
        self.lineInfo = lineInfo

        assert type(op) == str
        self.lft = lft
        self.op  = op
        self.rgt = rgt

    def dup(self):
        return g_BinaryExpr(self.lineInfo,
                            self.lft.dup(), self.op, self.rgt.dup())

    def print_tree(self, prefix):
        print(f"{prefix}g_BinaryExpr:  op: {self.op}")
        print(f"{prefix}  lft:")
        self.lft.print_tree(prefix+"    ")
        print(f"{prefix}  rgt:")
        self.rgt.print_tree(prefix+"    ")

    def resolve_name_lookups(self, ns_pri):
        self.lft.resolve_name_lookups(ns_pri)
        self.rgt.resolve_name_lookups(ns_pri)

    def convert_to_metatype(self, side):
        if not hasattr(self, "saved_metatype"):
            self.saved_metatype = self._convert_to_metatype(side)
        return self.saved_metatype

    def _convert_to_metatype(self, side):
        self.lft = self.lft.convert_to_metatype("right")
        self.rgt = self.rgt.convert_to_metatype("right")

        if   self.op in ["==","!="]:
            if   isinstance(self.lft, mt_PlugExpr) or isinstance(self.rgt, mt_PlugExpr):
                eq = mt_PlugExpr_EQ(self.lineInfo,
                                    self.lft, "EQ", self.rgt, single_bit_result=True)

                if self.op == "==":
                    return eq
                else:
                    return mt_PlugExpr_NOT(self.lineInfo, eq);

            else:
                return mt_StaticExpr_CMP(self.lineInfo, self.lft, self.op, self.rgt)

        elif self.op in ["&", "&&"]:
            return mt_PlugExpr_Logic(self.lineInfo, self.lft, "AND", self.rgt)
        elif self.op in ["|", "||"]:
            return mt_PlugExpr_Logic(self.lineInfo, self.lft, "OR",  self.rgt)
        elif self.op in ["^"]:
            return mt_PlugExpr_Logic(self.lineInfo, self.lft, "XOR", self.rgt)

        elif self.op == "concat":
            return mt_PlugExpr_Discontig(self.lineInfo, [self.lft, self.rgt])

        elif self.op == "+":
            return mt_StaticExpr_ADD(self.lineInfo, self.lft, self.rgt)
        elif self.op == "-":
            return mt_StaticExpr_SUB(self.lineInfo, self.lft, self.rgt)
        elif self.op == "*":
            return mt_StaticExpr_MUL(self.lineInfo, self.lft, self.rgt)
        elif self.op == "/":
            return mt_StaticExpr_DIV(self.lineInfo, self.lft, self.rgt)
        elif self.op == "%":
            return mt_StaticExpr_MOD(self.lineInfo, self.lft, self.rgt)

        else:
            print(f"failed op: {self.op}    line: {self.lineInfo}")
            TODO()      # add support for more operators



class g_UnaryExpr(ASTNode):
    def __init__(self, lineInfo, op, rgt):
        self.lineInfo = lineInfo

        self.op  = op
        self.rgt = rgt

    def dup(self):
        return g_UnaryExpr(self.lineInfo, self.op, self.rgt.dup())

    def print_tree(self, prefix):
        print(f"{prefix}g_UnaryExpr:   op: {repr(self.op)}")
        print(f"{prefix}  rgt:")
        self.rgt.print_tree(prefix+"    ")

    def resolve_name_lookups(self, ns_pri):
        self.rgt.resolve_name_lookups(ns_pri)

    def convert_to_metatype(self, side):
        if not hasattr(self, "saved_metatype"):
            self.saved_metatype = self._convert_to_metatype(side)
        return self.saved_metatype

    def _convert_to_metatype(self, side):
        self.rgt = self.rgt.convert_to_metatype("right")

        if self.op == "!":
            if self.rgt.typ_ != plugType_bit:
                TODO()    # report syntax error: ! is only valid on 'bit' or 'bool' types
            return mt_PlugExpr_NOT(self.lineInfo, self.rgt)

        elif self.op == "~":
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
        assert type(name) == str
        assert obj is not None
        if self.search(name) is not None:
            raise HWCCompile_SyntaxError(None, f"The symbol '{name}' already exists")
        self.directory[name] = obj

    def search(self, name):
        if name in self.directory:
            return self.directory[name]
        elif self.parent is None:
            return None
        else:
            return self.parent.search(name)

    def dump(self):
        if self.parent is not None:
            prefix = self.parent.dump()
        else:
            prefix = ""

        print(f"{prefix}---- id {id(self)} ----")
        for n in self.directory:
            print(f"{prefix}{n}")    # -> {self.directory[n]}")

        return prefix+"  "



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

    def __init__(self, lineInfo, name):
        self.lineInfo = lineInfo

        self.name   = name
        self.target = None

    def dup(self):
        assert self.target is None
        return g_IdentExpr(self.lineInfo, self.name)

    def __repr__(self):
        if self.target is None:
            return f"IDENT={self.name} target=None"
        else:
            return f"IDENT={self.name} target ID={id(self.target)}"
    def print_tree(self, prefix):
        print(f"{prefix}{self}")

    def resolve_name_lookups(self, ns_pri):
        self.target = ns_pri.search(self.name)
        if self.target is None:
            raise HWCCompile_SyntaxError(self.lineInfo, f"Symbol '{self.name}' not found")

    def convert_to_metatype(self, side):
        if not hasattr(self, "saved_metatype"):
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
            if type(self.target.typ_) == mt_StaticType_Int:
                return mt_StaticExpr_Var(self.target)

            elif isinstance(self.target.typ_, mt_PartDecl):
                return mt_PartExpr_Var(self.target)

            elif isinstance(self.target.typ_, mt_PlugDecl):
                # it's possible that the target has not reached this phase yet;
                # force it to do so.  Then we can use the typ_ field, which is
                # not defined in DeclStmt until this phase.

                self.target.convert_exprs_to_metatypes()

                # now that the target is ready to use, create an object which
                # specifically models "a reference to this variable"

                var = mt_PlugExpr_Var(self.lineInfo, self.target)

                # memory variables, and flag variables, are both weird, but in
                # different ways.  Memory variables are declared as a special
                # type that *wraps around* another type, like this:
                #    memory(bit[2]) foo;
                # which means that the bits are arranged like this:
                #    r[0] r[1] w[0] w[1]
                # Thus, the decision of "read or write" must happen at a high
                # level, *before* we (perhaps) index into the bits of the type
                # itself.  We do not know the exact offset to the write bits
                # yet (because calc_sizes() has not run yet), but once we know
                # that, we'll apply it.
                #
                # That's annoying, but it works OK: by the time that the
                # offsets have resolved, we have a PlugExpr which has a type
                # which is equal to the underlying type of the memory cell,
                # and the offset points to the read (or write) bits.  So from
                # there, things are pretty much like any other variable.
                #
                # ---
                #
                # On the other hand, flags are a native type of the language,
                # and have no flexibility about size: each flag is *exactly
                # one* two-part bit.  You can declare arrays of flags, but
                # each flag must be handled individually.  So the declaration
                #    flag[2] example;
                # produces the following bit pattern:
                #    [0].r [0].w [1].r [1].w
                # and thus the read/write question must be resolved at the
                # *bottom* of the expression.  This is harder!  Because an
                # an array of flags is *NOT* the same binary layout as an
                # array of bits (even if we know which side we are on),
                #
                # This is what motivated the creation of a "discontig" PlugExpr
                # class; we need a way to express "an array of bits, which are
                # not physically adjacent to each other."

                if self.target.typ_ == plugType_flag:
                    assert self.target.typ_.decl_bitSize == 2
                    if side == "right":
                        offset_cb = lambda: 0
                    else:
                        offset_cb = lambda: 1

                    return mt_PlugExpr_SubsetOf(self.lineInfo, var, offset_cb, plugType_bit)

                elif type(self.target.typ_) == mt_PlugDecl_ArrayOf and \
                   self.target.typ_.get_multidim_base() == plugType_flag:
                    TODO()

                elif self.target.isMem:
                    if side == "right":
                        offset_cb = lambda: 0
                    else:
                        assert side == "left"
                        offset_cb = lambda: var.typ_.decl_bitSize

                    return mt_PlugExpr_SubsetOf(self.lineInfo, var, offset_cb, self.target.typ_)

                else:
                    return var

            elif type(self.target.typ_) == g_PartOrPlugDecl:
                TODO()   # handle IDENTs that come before their declarations

            else:
                TODO()

        elif isinstance(self.target, mt_StaticExpr):
            return self.target

        else:
            assert False, (self.name, type(self.target))    # unexpected type

    def calc_sizes(self):
        assert False    # will never get here, is replaced by a metatype



class g_NumExpr(ASTNode):
    leafNode = True

    def __init__(self, num_txt):
        self.num = int(num_txt, base=0)

    def dup(self):
        return self
    def __repr__(self):
        return f"NUM={self.num}"
    def print_tree(self, prefix):
        print(f"{prefix}{self}")

    def resolve_name_lookups(self, ns_pri):
        pass

    def convert_to_metatype(self, side):
        return mt_StaticExpr_NumExpr(self.num)



class g_DotExpr(ASTNode):
    def __init__(self, lineInfo, base, fieldName):
        self.lineInfo = lineInfo

        self.base      = base
        self.fieldName = fieldName

        self.target = None

        self.offset = None

    def dup(self):
        assert self.target is None
        assert self.offset is None
        return g_DotExpr(self.lineInfo, self.base.dup(), self.fieldName)

    def print_tree(self, prefix):
        print(f"{prefix}g_DotExpr:    fieldName: {self.fieldName}    lineInfo: {self.lineInfo}")
        print(f"{prefix}  base:")
        self.base.print_tree("    ")

    def resolve_name_lookups(self, ns_pri):
        self.base.resolve_name_lookups(ns_pri)

    def convert_to_metatype(self, side):
        if not hasattr(self, "saved_metatype"):
            self.saved_metatype = self._convert_to_metatype(side)
        return self.saved_metatype

    def _convert_to_metatype(self, side):
        self.base = self.base.convert_to_metatype(side)
        assert type(self.base.typ_) in [mt_PlugDecl_Code, mt_PartDecl_Code], self.base.typ_

        self.target = self.base.typ_.code.pub_nameScope.search(self.fieldName)
        if self.target is None:
            raise HWCCompile_SyntaxError(self.lineInfo, f"Field name '{self.fieldName}' not found")
        assert(type(self.target) == g_DeclStmt)

        # if we reference a type that is later in the file, its declarations
        # will not have been converted to metatypes, yet.
        self.target.convert_exprs_to_metatypes()

        # dot expressions can only look up plug fields, because (currently)
        # only plug fields can be public.
        assert self.target.prefix in ["", "public"]
        assert isinstance(self.target.typ_, mt_PlugDecl)

        # we don't (yet) support public memory fields.  Should we add it?
        assert(self.target.isMem == False)

        # build an Expr object which represents the reference to the field.
        # It will calculate its offset later.
        return mt_PlugExpr_Dot(self.lineInfo, self.base, self.target)



class g_Unresolved_Single_Index_Expr(ASTNode):
    def __init__(self, lineInfo, base, indx):
        self.lineInfo = lineInfo

        self.base = base
        self.indx = indx

    def dup(self):
        return g_Unresolved_Single_Index_Expr(self.lineInfo, self.base.dup(), self.indx.dup())

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

    def resolve_name_lookups(self, ns_pri):
        self.base.resolve_name_lookups(ns_pri)
        self.indx.resolve_name_lookups(ns_pri)

    def convert_to_metatype(self, side):
        if not hasattr(self, "saved_metatype"):
            self.saved_metatype = self._convert_to_metatype(side)
        return self.saved_metatype

    def _convert_to_metatype(self, side):
        base         = self.base.convert_to_metatype(side)
        len_or_index = self.indx.convert_to_metatype("right")

        if   isinstance(base, mt_PlugDecl):
            return mt_PlugDecl_ArrayOf(self.lineInfo, base,len_or_index)
        elif isinstance(base, mt_PartDecl):
            return mt_PartDecl_ArrayOf(self.lineInfo, base,len_or_index)

        elif isinstance(base, mt_PlugExpr):
            if type(base.typ_) == mt_PlugDecl_ArrayOf:
                if   isinstance(len_or_index, mt_StaticExpr):
                    return mt_PlugExpr_ArrayIndex(self.lineInfo, base, len_or_index)

                elif isinstance(len_or_index, mt_PlugExpr):
                    decode = mt_PlugExpr_Decode(self.lineInfo, len_or_index)
                    return mt_PlugExpr_MaskedSelect(self.lineInfo, base, decode)

                else:
                    TODO()    # unexpected case

            else:
                raise HWCCompile_SyntaxError(self.lineInfo, "Cannot index into a non-array expression")

        elif isinstance(base, mt_PartExpr):
            TODO()

        else:
            assert False    # TODO: unexpected case

    def calc_sizes(self):
        assert False, "If you get here, then you forgot to call resolve() on this object after name resolution, and then to save the resolved function into the enclosing object."



class g_ArraySlice(ASTNode):
    def __init__(self, lineInfo, base, start,end):
        self.lineInfo = lineInfo

        self.base  = base
        self.start = start
        self.end   = end      # could be None

    def dup(self):
        base_dup  = self.base .dup()
        start_dup = self.start.dup()
        end_dup   = self.end  .dup() if self.end is not None else None
        return g_ArraySlice(self.lineInfo, base_dup, start_dup, end_dup)

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

    def resolve_name_lookups(self, ns_pri):
        self.base .resolve_name_lookups(ns_pri)
        self.start.resolve_name_lookups(ns_pri)
        if self.end is not None:
            self.end.resolve_name_lookups(ns_pri)

    def convert_to_metatype(self, side):
        if not hasattr(self, "saved_metatype"):
            self.saved_metatype = self._convert_to_metatype(side)
        return self.saved_metatype

    def _convert_to_metatype(self, side):
        base  = self.base .convert_to_metatype("right")
        start = self.start.convert_to_metatype("right")
        end   = self.end  .convert_to_metatype("right") if self.end is not None else None

        if type(base.typ_) == mt_PlugDecl_ArrayOf:
            return mt_PlugExpr_ArraySlice(self.lineInfo, base, start,end)
        else:
            TODO()



class g_Generic_PartOrPlugDecl(ASTNode):
    def __init__(self, arg_decls, isPart, stmts):
        self.arg_decls = arg_decls
        self.generic   = g_PartOrPlugDecl(isPart, None, stmts)

    def dup(self):
        TODO()

    def print_tree(self, prefix):
        print(f"{prefix}g_GenericPartOrPlugDecl:")
        print(f"{prefix}  arg_decls: {self.arg_decls}")
        print(f"{prefix}  generic:")
        self.generic.print_tree(prefix+"    ")

    def instantiate(self, cond, ns_pri):
        retval = self.generic.dup()

        # drive the instantiated part through the phases that it missed
        #
        # TODO: this is imperfect, when we have a for() loop, because
        #       we might make a forward reference to pass of the loop
        #       which hasn't been initialized yet.  It may be necessary
        #       to move this code into the ForStmt class, so that we can
        #       to each phase in parallel, across *ALL* instances, before
        #       starting the next phase.  TBD
        retval.deliver_if_conditions(cond)
        retval.populate_name_scopes(ns_pri)
        retval.resolve_name_lookups(ns_pri)
        retval.convert_exprs_to_metatypes()
        retval.calc_sizes()

        return retval



class g_Tuple(ASTNode):
    def __init__(self, vals):
        assert len(vals) > 0
        self.vals = vals

    def deliver_if_conditions(self, cond):
        for v in self.vals:
            v.deliver_if_conditions(cond)

    def populate_name_scopes(self):
        for v in self.vals:
            v.populate_name_scopes()

    def resolve_name_lookups(self):
        for v in self.vals:
            v.resolve_name_lookups()



class g_ForStmt(ASTNode):
    def __init__(self, lineInfo, var_name, start,end, body, tuple_name):
        self.lineInfo = lineInfo

        # we cannot do most of our work until calc_sizes(), because we won't
        # be able to resolve start and end until then.  However, we can build
        # the "generic part" right now, and save that.

        self.var_name   = var_name      # iterator variable, for inside
        self.start      = start
        self.end        = end
        self.tuple_name = tuple_name    # name to access the tuple, from outside

        generic_args = {var_name:"int"}

        self.generic_partDecl = g_Generic_PartOrPlugDecl(generic_args,
                                                         True,    # isPart
                                                         [body])

        self.if_conditions = None
        self.pri_nameScope = None

        self.decl_bitSize = None

    def print_tree(self, prefix):
        print(f"{prefix}ForStmt: var_name: {self.var_name}      {self.lineInfo}")

        if type(self.start) == int:
            print(f"{prefix}  start: {self.start}")
        else:
            print(f"{prefix}  start:")
            self.start.print_tree(prefix+"    ")

        if type(self.end) == int:
            print(f"{prefix}  end: {self.end}")
        else:
            print(f"{prefix}  end:")
            self.end.print_tree(prefix+"    ")

        print(f"{prefix}  bodY:")
        self.generic_partDecl.print_tree(prefix+"    ")


    def deliver_if_conditions(self, cond):
        assert self.if_conditions is None
        self.if_conditions = cond

    def populate_name_scopes(self, ns_pub,ns_pri):
        # all for() loops are private, automatically.  So we'll ignore the
        # public NameScope, even if we are given one.
        ns_pub = None

        assert type(self.var_name) == str
        if ns_pri.search(self.var_name) is not None:
            TODO()    # report syntax error

        # Even if tuple_name is not None, we cannot create the entry in the
        # NameScope object to look up the name yet, since we don't know how
        # large the tuple will be.  But in order to do that, we will need to be
        # able to resolve the (static) values start,end.
        #
        # So, from here through the beginning of calc_sizes(), we will do all
        # of the normal work (as if we were not generic), to *ONLY* start,end.
        # They will resolve once we get to calc_sizes().  Then, once we know
        # their values, we will create the array and will do the instantiations
        #
        # remember, we don't call p_n_s() on expressions.  So we "did" the step
        # for start,end - but it was a NOP!

        # We save the private name scope, so that it can be used for each of
        # the instantiated passes, later.
        self.pri_nameScope = ns_pri

    def resolve_name_lookups(self, ns_pri):
        assert ns_pri == self.pri_nameScope

        # see the comments in populate_name_scopes().  Note that we don't have
        # anything to save in this function for the future, that we hadn't
        # already saved.
        self.start.resolve_name_lookups(ns_pri)
        self.end  .resolve_name_lookups(ns_pri)

    def convert_exprs_to_metatypes(self):
        # see the comments in populate_name_scopes()
        self.start = self.start.convert_to_metatype("right")
        self.end   = self.end  .convert_to_metatype("right")

    def calc_sizes(self):
        if self.decl_bitSize == "in progress":
            assert False    # TODO: report cyclic declaration
        if self.decl_bitSize is not None:
            return
        self.decl_bitSize = "in progress"

        # at last!  We can now call calc_sizes() on our start,end expressions,
        # extract the (hopefully static, int) values, and then use them to
        # figure out the length of our array of passes.  Then we instantiate
        # the generic part many times.

        self.start.calc_sizes()
        self.end  .calc_sizes()
        if not isinstance(self.start, mt_StaticExpr):
            TODO()    # syntax error
        if not isinstance(self.end  , mt_StaticExpr):
            TODO()    # syntax error

        self.start = self.start.resolve_static_expr()
        self.end   = self.end  .resolve_static_expr()
        if type(self.start) != int:
            TODO()    # syntax error
        if type(self.start) != int:
            TODO()    # syntax error

        if self.start > self.end:
            TODO()    # syntax error
        if self.start == self.end:
            TODO()    # syntax error, for now.  Should I allow it in the future???

        self.passes = [None]*(self.end - self.start)

        # since the body of the for() loop might contain references to its own
        # name, we need to add the tuple name (if requested) to the name scope
        # that encloses us
        if self.tuple_name is not None:
            TODO()    # probably, just post the g_ForStmt there.  Simple.

        # build the instantiated parts
        for i in range(self.start, self.end):
            # create a private name scope for the instance we're about to
            # build, and populate it with a value for the iterator
            # variable.  That is, each instantiation has its own private
            # name scope; they are identical except for this one variable.
            ns_for_inst = NameScope(self.pri_nameScope)
            ns_for_inst.add(self.var_name, mt_StaticExpr_NumExpr(i))

            inst = self.generic_partDecl.instantiate(self.if_conditions, ns_for_inst)
            self.passes[i-self.start] = inst

            # the instantiate() function will call populate_name_scopes(),
            # resolve_name_lookups(), and convert_exprs_to_metatypes(), and
            # calc_sizes() on each new instance

        self.decl_bitSize = sum(inst.decl_bitSize for inst in self.passes)

    def calc_top_down_offsets(self, offset):
        running_offset = offset
        for inst in self.passes:
            inst.calc_top_down_offsets(None, forLoop_instOffset=running_offset)
            running_offset += inst.decl_bitSize

    def calc_bottom_up_offsets(self):
        for inst in self.passes:
            inst.calc_bottom_up_offsets()

    def print_bit_descriptions(self, name, start_bit):
        for i in range(len(self.passes)):
            self.passes[i].print_bit_descriptions(f"{name}.__for_{self.lineInfo.line}_{self.lineInfo.col}_{self.start+i}__", start_bit)

    def print_wiring_diagram(self, start_bit):
        for i in range(len(self.passes)):
            self.passes[i].print_wiring_diagram(start_bit)



class g_BoolExpr(ASTNode):
    def __init__(self, val):
        assert val in ["true","false"]
        self.val = val

    def resolve_name_lookups(self, ns_pri):
        pass
    def convert_to_metatype(self, side):
        return mt_StaticExpr_Bool(self.val)



class g_DecodeExpr(ASTNode):
    def __init__(self, lineInfo, indx):
        self.lineInfo = lineInfo
        self.indx = indx



class g_MaskedSelectExpr(ASTNode):
    def __init__(self, lineInfo, arr, mask):
        self.lineInfo = lineInfo
        self.arr  = arr
        self.mask = mask



class g_GetExprProp(ASTNode):
    def __init__(self, lineInfo, prop, exp):
        self.lineInfo = lineInfo
        self.prop = prop
        self.exp  = exp

    def resolve_name_lookups(self, ns_pri):
        self.exp.resolve_name_lookups(ns_pri)

    def convert_to_metatype(self, side):
        if not hasattr(self, "saved_metatype"):
            self.saved_metatype = self._convert_to_metatype(side)
        return self.saved_metatype

    def _convert_to_metatype(self, side):
        self.exp = self.exp.convert_to_metatype(side)

        if self.prop in ["sizeof","len"]:
            return mt_StaticExpr_GetProp(self.lineInfo, self.prop, self.exp)

        if self.prop == "typeof":
            if not isinstance(self.exp, mt_PlugExpr) and not isinstance(self.exp, mt_PartExpr):
                raise HWCCompile_SyntaxError(self.lineInfo, "The parameter to the built-in function typeof() must be a plug expression or part expression")
            return self.exp.typ_

        else:
            print(self.prop)
            TODO()    # what prop is this?

