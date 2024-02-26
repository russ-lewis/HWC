
class ASTNode:
    def print_tree(self, prefix):
        assert False, f"Need to override this in the child class: {type(self)}"

    def populate_name_scopes(self):
        assert False, f"Need to override this in the child class: {type(self)}"
    def resolve_name_lookups(self):
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



class PartDecl(ASTNode):
    def __init__(self, nameScope, name, stmts):
        assert type(nameScope) == NameScope
        super().__init__()
        self.name      = name
        self.stmts     = stmts
        self.nameScope = NameScope(nameScope)
    def __repr__(self):
        return f"ast.PartDecl({self.name}, {self.stmts})"

    def print_tree(self, prefix):
        print(f"{prefix}PART DECL: name={self.name}")
        for d in self.stmts:
            d.print_tree(prefix+"  ")

    def populate_name_scopes(self):
        for s in self.stmts:
            s.populate_name_scopes()

    def resolve_name_lookups(self):
        for s in self.stmts:
            s.resolve_name_lookups()



class PlugDecl(ASTNode):
    def __init__(self, nameScope, name, stmts):
        assert type(nameScope) == NameScope
        super().__init__()
        self.name      = name
        self.stmts     = stmts
        self.nameScope = NameScope(nameScope)
    def __repr__(self):
        return f"ast.PlugDecl({self.name}, {self.stmts})"

    def populate_name_scopes(self):
        for s in self.stmts:
            s.populate_name_scopes()

    def resolve_name_lookups(self):
        for s in self.stmts:
            s.resolve_name_lookups()



class BlockStmt(ASTNode):
    def __init__(self, stmts):
        super().__init__()
        self.stmts = stmts



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
    def __repr__(self):
        return f"ast.DeclStmt({self.prefix}, mem={self.isMem}, {self.typ_}, {self.name}, init={self.initVal})"

    def print_tree(self, prefix):
        print(f"{prefix}DECL STATEMENT: name={self.name} prefix={self.prefix} isMem={self.isMem}")

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



class ConnStmt(ASTNode):
    def __init__(self, lhs,rhs):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs
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



class IdentExpr(ASTNode):
    leafNode = True

    def __init__(self, name):
        self.name      = name
    def __repr__(self):
        return f"IDENT={self.name}"

    def resolve_name_lookups(self):
        pass

class NumExpr(ASTNode):
    leafNode = True

    def __init__(self, num):
        self.num = num
    def __repr__(self):
        return f"NUM={self.num}"

    def resolve_name_lookups(self):
        pass

class BitType(ASTNode):
    leafNode = True

    def __repr__(self):
        return "bit"

    def resolve_name_lookups(self):
        pass



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

