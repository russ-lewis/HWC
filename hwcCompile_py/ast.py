
class ASTNode:
    pass



class Decl(ASTNode):
    def __init__(self, type, name, stmts, file_nameScope):
        super()
        self.type   = type
        self.name   = name
        self.stmts  = stmts
        self.prefix = None
        self.names  = NameScope(file_nameScope)
    def __repr__(self):
        return f"ast.Decl({self.type}, {self.name}, {self.prefix}, {self.stmts})"



class VarDecl(ASTNode):
    pass



class ConnStmt(ASTNode):
    pass



class Expr(ASTNode):
    pass



class NameScope:
    def __init__(self, parent):
        self.parent    = parent
        self.directory = {}

    def add(self, name, obj):
        assert obj is not None
        if obj.search(name) is not None:
            assert False, "report syntax error"
        self.directory[name] = obj

    def search(self, name):
        if name in self.directory:
            return self.directory[name]
        elif self.parent is None:
            return None
        else:
            return self.parent.search(name)

