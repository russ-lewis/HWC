
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

plugType_bit  = mt_PlugDecl_Bit()
plugType_flag = mt_PlugDecl_Flag()
plugType_auto = mt_PlugDecl_Auto()

from ast_expr_plugexpr   import *
from ast_expr_partexpr   import *

from ast_expr_statictype import *

staticType_int  = mt_StaticType_Int()
staticType_bool = mt_StaticType_Bool()

from ast_expr_staticvar  import *
from ast_expr_staticexpr import *

