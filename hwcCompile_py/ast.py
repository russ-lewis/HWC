
class ASTNode:
    def print_tree(self, prefix):
        assert False, f"Need to override this in the child class: {type(self)}"

    # default value for the base class
    leafNode = False

    def populate_name_scopes(self):
        assert False, f"Need to override this in the child class: {type(self)}"
    def resolve_name_lookups(self):
        assert False, f"Need to override this in the child class: {type(self)}"
    def calc_sizes_and_offsets(self):
        assert False, f"Need to override this in the child class: {type(self)}"



class File(ASTNode):
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
            self.nameScope.add(d.name, d)
        for d in self.decls:
            d.populate_name_scopes()

    def resolve_name_lookups(self):
        for d in self.decls:
            d.resolve_name_lookups()

    def calc_sizes_and_offsets(self):
        # files don't have sizes, not even if it's the root file of the
        # compilation; the size of the "entire compilation" is the size
        # of the main *part* inside that file.

        for d in self.decls:
            d.calc_sizes_and_offsets()



class PartDecl(ASTNode):
    def __init__(self, nameScope, name, stmts):
        assert type(nameScope) == NameScope
        super().__init__()
        self.nameScope = NameScope(nameScope)
        self.name      = name
        self.stmts     = stmts
        self.size      = None
    def __repr__(self):
        return f"ast.PartDecl({self.name}, {self.stmts})"

    def print_tree(self, prefix):
        print(f"{prefix}PART DECL: name={self.name} id={id(self)}")
        for d in self.stmts:
            d.print_tree(prefix+"  ")
            print(f"{prefix}    size: {d.size}")


    def populate_name_scopes(self):
        for s in self.stmts:
            s.populate_name_scopes()

    def resolve_name_lookups(self):
        for s in self.stmts:
            s.resolve_name_lookups()

    def calc_sizes_and_offsets(self):
        if self.size is not None:
            return

        for s in self.stmts:
            s.calc_sizes_and_offsets()

        # the 'part_size' is the number of storage bits that must be
        # allocated for each instance of this part.  All statements include
        # this field (even if it's zero).  For declarations, this field tells
        # us how many bits are required by this newly-declared item; for
        # connections, it tells us how many bits are required as temporary
        # values; for if() and for() statements, it summarizes declarations
        # embedded inside the statement (if any).

        self.part_size = sum(s.part_size for s in self.stmts)



class PlugDecl(ASTNode):
    def __init__(self, nameScope, name, stmts):
        assert type(nameScope) == NameScope
        super().__init__()
        self.nameScope = NameScope(nameScope)
        self.name      = name
        self.stmts     = stmts
    def __repr__(self):
        return f"ast.PlugDecl({self.name}, {self.stmts})"

    populate_name_scopes   = PartDecl.populate_name_scopes
    resolve_name_lookups   = PartDecl.resolve_name_lookups
    calc_sizes_and_offsets = PartDecl.calc_sizes_and_offsets

    def print_tree(self, prefix):
        print(f"{prefix}PLUG DECL: name={self.name} id={id(self)}")
        for d in self.stmts:
            d.print_tree(prefix+"  ")
            print(f"{prefix}    size: {d.size}")




class DeclStmt(ASTNode):
    def __init__(self, nameScope, isMem, typ_, name, initVal):
        assert type(nameScope) == NameScope
        super().__init__()
        self.nameScope = nameScope
        self.prefix    = None
        self.isMem     = isMem
        self.typ_      = typ_
        self.name      = name
        self.initVal   = initVal
        self.size      = None
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
        self.nameScope.add(self.name, self)

    def resolve_name_lookups(self):
        self.typ_.resolve_name_lookups()
        if self.initVal is not None:
            self.initVal.resolve_name_lookups()

    def calc_sizes_and_offsets(self):
        if self.size is not None:
            return

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



class ConnStmt(ASTNode):
    def __init__(self, lhs,rhs):
        super().__init__()
        self.lhs  = lhs
        self.rhs  = rhs
        self.size = None
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

    def calc_sizes_and_offsets(self):
        if self.size is not None:
            return

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



class BitType_(ASTNode):
    leafNode  = True
    plug_size = 1

    def __repr__(self):
        return "bit"

    def resolve_name_lookups(self):
        pass
    def calc_sizes_and_offsets(self):
        pass
BitType_.singleton = BitType_()
def BitType():
    return BitType_.singleton



class IntType_(ASTNode):
    leafNode = True

    def __repr__(self):
        return "int"

    def resolve_name_lookups(self):
        pass
    def calc_sizes_and_offsets(self):
        assert False
IntType_.singleton = IntType_()
def IntType():
    return IntType_.singleton



class IdentExpr(ASTNode):
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

        # an IDENT (as a primary expression, not the right-hand side of a
        # dot-expr) can refer to:
        #   1) The first part of a file name (maybe all of it)
        #   2) The name of a plug or part declaration, in this file (or aliased into it)
        #   3) A public or private declaration within the current scope, or any enclosing scope (all the way up to the file scope, maybe)
        assert type(self.target) in [ # TODO: case 1
                                      PartDecl, PlugDecl,
                                      DeclStmt           ]

        if   type(self.target) == PartDecl:
            pass
        elif type(self.target) == PlugDecl:
            pass

        elif type(self.target) == DeclStmt:
            print()
            print(self.target.prefix)
            print(self.target.isMem)
            print(self.target.typ_)
            print(self.target.name)
            self.plug_type = self.target.typ_;
            self.part_size = 0

        else:
            assert False

    def calc_sizes_and_offsets(self):
        pass



class NumExpr(ASTNode):
    leafNode = True
    typ_ = BitType()

    def __init__(self, num_txt):
        self.num = int(num_txt)
    def __repr__(self):
        return f"NUM={self.num}"

    def resolve_name_lookups(self):
        pass



class Unresolved_Single_Index_Expr(ASTNode):
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

    def resolve(self):
        if self.base.TODO_figure_out_if_is_declaration_type_or_runtime_val():
            return ArrayOf   (self.base, self.indx)
        else:
            return ArrayIndex(self.base, self.indx)

    def calc_sizes_and_offsets(self):
        assert False, "If you get here, then you forgot to call resolve() on this object after name resolution, and then to save the resolved function into the enclosing object."



class ArrayOf(ASTNode):
    def __init__(self, base, indx):
        # NOTE: no nameScope required, since we have already resolved names
        self.base = base
        self.indx = indx

    def resolve_name_lookups(self):
        assert False, "You should never create this object until you have passed the name-lookup phase and then called resolve()"

    def calc_sizes_and_offsets(self):
        TODO()



class ArrayIndex(ASTNode):
    def __init__(self, base, indx):
        # NOTE: no nameScope required, since we have already resolved names
        self.base = base
        self.indx = indx

    def resolve_name_lookups(self):
        assert False, "You should never create this object until you have passed the name-lookup phase and then called resolve()"

    def calc_sizes_and_offsets(self):
        TODO()



class ArraySlice(ASTNode):
    def __init__(self, base, start,end):
        # NOTE: no nameScope required, since we have already resolved names
        self.base  = base
        self.start = start
        self.end   = end

    def resolve_name_lookups(self):
        assert False, "You should never create this object until you have passed the name-lookup phase and then called resolve()"

    def calc_sizes_and_offsets(self):
        TODO()

