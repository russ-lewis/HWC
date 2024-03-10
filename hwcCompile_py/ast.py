
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
    def calc_sizes_and_offsets(self):
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

    def calc_sizes_and_offsets(self):
        # files don't have sizes, not even if it's the root file of the
        # compilation; the size of the "entire compilation" is the size
        # of the main *part* inside that file.

        for d in self.decls:
            d.calc_sizes_and_offsets()



class g_PartOrPlugDecl(ASTNode):
    def __init__(self, isPart, ns_pub, name, stmts):
        assert type(ns_pub) == NameScope
        self.pub_nameScope = ns_pub
        self.isPart        = isPart
        self.name          = name
        self.stmts         = stmts
        self.decl_bits     = None       # TODO: rename as decl_bitSize
    def __repr__(self):
        return f"ast.g_PartDecl({self.name}, {self.stmts})"

    def print_tree(self, prefix):
        print(f"{prefix}PART-OR-PLUG DECL: isPart={self.isPart} name={self.name} id={id(self)}")
        for d in self.stmts:
            d.print_tree(prefix+"  ")
            print(f"{prefix}    decl_bits: {d.decl_bits}")


    def populate_name_scopes(self):
        for s in self.stmts:
            s.populate_name_scopes()

    def resolve_name_lookups(self):
        for s in self.stmts:
            s.resolve_name_lookups()

    def convert_exprs_to_metatypes(self):
        for d in self.stmts:
            d.convert_exprs_to_metatypes()

    def calc_sizes_and_offsets(self):
        if self.decl_bits == "in progress":
            assert False    # TODO: report cyclic declaration
        if self.decl_bits is not None:
            return
        self.decl_bits = "in progress"

        for s in self.stmts:
            s.calc_sizes_and_offsets()
        self.decl_bits = sum(s.decl_bits for s in self.stmts)



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
        self.decl_bits     = None
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
        self.typ_ = self.typ_.convert_to_metatype()
        if self.initVal is not None:
            self.initVal = self.initVal.convert_to_metatype()

    def calc_sizes_and_offsets(self):
        if self.decl_bits == "in progress":
            assert False    # TODO: report cyclic declaration
        if self.decl_bits is not None:
            return
        self.decl_bits = "in progress"

        if   isinstance(self.typ_, mt_PlugDecl):
            TODO()
        elif isinstance(self.typ_, mt_PartDecl):
            assert(self.prefix == "subpart")
        else:
            assert False, f"Unexpected metatype {type(self.typ_)} of the declaration type expression"

        assert False    # TODO: audit and port to the new design doc

        self.typ_.calc_sizes_and_offsets()

        if self.isMem:
            # the type of a memory cell *MUST* be plug, never a part
            assert type(self.typ_.target     ) == DeclStmt and \
                   type(self.typ_.target.typ_) == PlugDecl

        # if the type of the var doesn't match the type of the expression, then
        # we need to build a converter.  I haven't thought about how to do
        # that, yet.  Maybe build a wrapper expression at an earlier phase?
        if self.initVal is not None and self.typ_ != self.initVal.typ_:
            assert False    # TODO

        self.plug_size = self.typ_.plug_size

        if not self.isMem:
            self.part_size = self.typ_.part_size
        else:
            self.part_size = self.typ_.part_size*2



class g_ConnStmt(ASTNode):
    def __init__(self, lhs,rhs):
        self.lhs       = lhs
        self.rhs       = rhs
        self.decl_bits = None
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
        self.lhs = self.lhs.convert_to_metatype()
        self.rhs = self.rhs.convert_to_metatype()

    def calc_sizes_and_offsets(self):
        if self.decl_bits == "in progress":
            assert False    # TODO: report cyclic declaration
        if self.decl_bits is not None:
            return
        self.decl_bits = "in progress"

        assert False    # TODO: audit and port to the new design doc

        if type(self.lhs.target) != DeclStmt or \
           type(self.rhs.target) != DeclStmt:
            assert False    # TODO: implement other variants

        assert self.lhs.target.prefix in ["", "subpart","public","private","static"]
        assert self.rhs.target.prefix in ["", "subpart","public","private","static"]

        if self.lhs.target.prefix == "subpart":
            assert False    # TODO: report syntax error
        if self.rhs.target.prefix == "subpart":
            assert False    # TODO: report syntax error

        if self.lhs.target.prefix not in ["", "public","private"]:
            assert False    # TODO: handle static assignments.
        if self.lhs.target.prefix not in ["", "public","private"]:
            assert False    # TODO: handle static assignments.

        # if the type of the var doesn't match the type of the expression, then
        # we need to build a converter.  I haven't thought about how to do
        # that, yet.  Maybe build a wrapper expression at an earlier phase?
        if self.lhs.plug_type != self.rhs.plug_type:
            print(self.lhs.typ_)
            print(self.rhs.typ_)
            assert False    # TODO

        self.lhs.calc_sizes_and_offsets()
        self.rhs.calc_sizes_and_offsets()

        self.part_size = self.lhs.part_size + self.rhs.part_size



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
    def calc_sizes_and_offsets(self):
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

    def convert_to_metatype(self):
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
                return mt_PartExpr(self.target)
            elif isinstance(self.target.typ_, mt_PlugDecl):
                return mt_PlugExpr(self.target)

            elif type(self.target.typ_) == g_PartOrPlugDecl:
                TODO()   # handle IDENTs that come before their declarations

            else:
                TODO()

        else:
            assert False    # unexpected type

    def calc_sizes_and_offsets(self):
        assert False    # TODO: audit and port to the new design doc



class g_NumExpr(ASTNode):
    leafNode = True

    def __init__(self, num_txt):
        self.num = int(num_txt)
    def __repr__(self):
        return f"NUM={self.num}"

    def resolve_name_lookups(self):
        pass

    def convert_to_metatype(self):
        return mt_NumExpr(self.num)



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

    def convert_to_metatype(self):
        base = self.base.convert_to_metatype()
        indx = self.indx.convert_to_metatype()

        if   isinstance(base, mt_PlugDecl):
            return mt_PlugDecl_ArrayOf(base,indx)
        elif isinstance(base, mt_PartDecl):
            return mt_PartDecl_ArrayOf(base,indx)

        elif isinstance(base, mt_PlugExpr):
            TODO()
        elif isinstance(base, mt_PartExpr):
            TODO()

        else:
            assert False    # TODO: unexpected case

    def calc_sizes_and_offsets(self):
        assert False, "If you get here, then you forgot to call resolve() on this object after name resolution, and then to save the resolved function into the enclosing object."



class g_ArraySlice(ASTNode):
    def __init__(self, base, start,end):
        # NOTE: no nameScope required, since we have already resolved names
        self.base  = base
        self.start = start
        self.end   = end

