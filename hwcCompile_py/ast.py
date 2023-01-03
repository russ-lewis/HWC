
class ASTNode:
    def populate_name_scopes(self):
        assert False, "Need to override this in the child classes"
    def do_name_lookups(self):
        assert False, "Need to override this in the child classes"



class File(ASTNode):
    def __init__(self, nameScope, decls):
        assert type(nameScope) == NameScope
        super().__init__()
        self.nameScope = nameScope
        self.decls     = decls

    def populate_name_scopes(self):
        for d in self.decls:
            self.names.add(d.name, d)
        for d in self.decls:
            d.populate_name_scopes()



class TypeDecl(ASTNode):
    def __init__(self, nameScope, type, name, stmts):
        assert type(nameScope) == NameScope
        super().__init__()
        self.type      = type
        self.name      = name
        self.stmts     = stmts
        self.prefix    = None
        self.nameScope = NameScope(nameScope)
    def __repr__(self):
        return f"ast.Decl({self.type}, {self.name}, {self.prefix}, {self.stmts})"

    def populate_name_scopes(self):
        for s in self.stmts:
            s.populate_name_scopes()



class BlockStmt(ASTNode):
    def __init__(self, stmts):
        super().__init__()
        self.stmts = stmts

#    def populate_name_scopes(self):
#        self.names.add(decl, self)

def flatten_statements(stmts_in):
    stmst_out = []
    for s in stmts_in:
        if type(s) == BlockStmt:
            stmts_out += s.stmts
        else:
            stmts_out.append(s)
    return stmts_out



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

#    def populate_name_scopes(self):
#        self.names.add(decl, self)



class ConnStmt(ASTNode):
    def __init__(self, lhs,rhs):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs
    def __repr__(self):
        return f"ast.ConnStmt({self.lhs}, {self.rhs})"

    def populate_name_scopes(self):
        pass    # this statement does not have any declarations inside it



class IdentExpr(ASTNode):
    def __init__(self, name):
        self.name      = name

class NumExpr(ASTNode):
    def __init__(self, num):
        self.num = num



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

