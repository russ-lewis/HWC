
from ast import ASTNode;



class mt_PlugDecl(ASTNode):
    pass
class mt_PartDecl(ASTNode):
    pass
class mt_PlugExpr(ASTNode):
    pass
class mt_PartExpr(ASTNode):
    pass
class mt_StaticType(ASTNode):
    pass
class mt_StaticVar(ASTNode):
    pass
class mt_StaticExpr(ASTNode):
    pass

from ast_expr_plugdecl   import *
from ast_expr_partdecl   import *
from ast_expr_plugexpr   import *
from ast_expr_partexpr   import *
from ast_expr_statictype import *
from ast_expr_staticvar  import *
from ast_expr_staticexpr import *



plugType_bit = mt_PlugDecl_Simple(1)

staticType_int = mt_StaticType()



class mt_NumExpr(mt_StaticExpr):
    typ_ = staticType_int

    def __init__(self, num):
        self.num = num

    def print_tree(self, prefix):
        print(f"{prefix}mt_NumExpr: num={self.num}")

