
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



class mt_PlugDecl_Simple(mt_PlugDecl):
    def __init__(self, decl_bits):
        self.decl_bits = decl_bits
    def print_tree(self, prefix):
        print(f"{prefix}decl_bits = {self.decl_bits}")

    def resolve_name_lookups(self):
        pass
    def convert_to_metatype(self):
        return self
    def calc_sizes_and_offsets(self):
        pass

plugType_bit = mt_PlugDecl_Simple(1)



class mt_PlugDecl_ArrayOf(mt_PlugDecl):
    def __init__(self, base, indx):
        # NOTE: no nameScope required, since we have already resolved names
        self.base = base
        self.indx = indx

    def resolve_name_lookups(self):
        assert False, "You should never create this object until you have passed the name-lookup phase and then called resolve()"

    def calc_sizes_and_offsets(self):
        assert False    # TODO: audit and port to the new design doc

