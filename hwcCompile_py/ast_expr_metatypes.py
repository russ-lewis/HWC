
from ast import ASTNode;



class mt_PlugDecl(ASTNode):
    pass
class mt_PartDecl(ASTNode):
    pass

class mt_PlugExpr(ASTNode):
    def __init__(self, var):
        self.var = var
    def print_tree(self, prefix):
        print(f"{prefix}mt_PlugExpr:")
        self.var.print_tree(prefix+"  ")

class mt_PartExpr(ASTNode):
    pass

class mt_StaticType(ASTNode):
    pass
class mt_StaticVar(ASTNode):
    pass
class mt_StaticExpr(ASTNode):
    pass



class mt_PlugDecl_Simple(mt_PlugDecl):
    leafNode = True
    def __init__(self, decl_bits):
        self.decl_bits = decl_bits
    def __repr__(self):
        return f"mt_PlugDecl_Simple: decl_bits = {self.decl_bits}"
    def print_tree(self, prefix):
        print(f"{prefix}{repr(self)}")

    def resolve_name_lookups(self):
        pass
    def convert_to_metatype(self):
        return self
    def calc_sizes_and_offsets(self):
        pass

plugType_bit = mt_PlugDecl_Simple(1)



class mt_PlugDecl_Code(mt_PlugDecl):
    def __init__(self, code):
        self.code = code
    def print_tree(self, prefix):
        print(f"{prefix}mt_PlugDecl_Code:")
        print(f"{prefix}  code:")
        self.code.print_tree(prefix+"    ")



class mt_PartDecl_Code(mt_PartDecl):
    def __init__(self, code):
        self.code = code
    def print_tree(self, prefix):
        print(f"{prefix}mt_PartDecl_Code:")
        print(f"{prefix}  code:")
        self.code.print_tree(prefix+"    ")



class mt_PlugDecl_ArrayOf(mt_PlugDecl):
    def __init__(self, base, indx):
        # NOTE: no nameScope required, since we have already resolved names
        self.base = base
        self.indx = indx
    def print_tree(self, prefix):
        print(f"{prefix}mt_PlugDecl_ArrayOf:")
        print(f"{prefix}  base:")
        self.base.print_tree(prefix+"    ")
        print(f"{prefix}  indx:")
        self.indx.print_tree(prefix+"    ")

    def resolve_name_lookups(self):
        assert False, "You should never create this object until you have passed the name-lookup phase and then called resolve()"

    def calc_sizes_and_offsets(self):
        assert False    # TODO: audit and port to the new design doc



class mt_PartDecl_ArrayOf(mt_PartDecl):
    def __init__(self, base, indx):
        # NOTE: no nameScope required, since we have already resolved names
        self.base = base
        self.indx = indx
    def print_tree(self, prefix):
        print(f"{prefix}mt_PartDecl_ArrayOf:")
        print(f"{prefix}  base:")
        self.base.print_tree(prefix+"    ")
        print(f"{prefix}  indx:")
        self.indx.print_tree(prefix+"    ")

    def resolve_name_lookups(self):
        assert False, "You should never create this object until you have passed the name-lookup phase and then called resolve()"

    def calc_sizes_and_offsets(self):
        assert False    # TODO: audit and port to the new design doc



staticType_int = mt_StaticType()



class mt_NumExpr(mt_StaticExpr):
    typ_ = staticType_int

    def __init__(self, num):
        self.num = num

    def print_tree(self, prefix):
        print(f"{prefix}mt_NumExpr: num={self.num}")

