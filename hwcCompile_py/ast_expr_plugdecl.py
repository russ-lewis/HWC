
from ast_expr_metatypes import *



class mt_PlugDecl_Simple(mt_PlugDecl):
    leafNode = True
    def __init__(self, decl_bitSize):
        self.decl_bitSize = decl_bitSize
    def __repr__(self):
        return f"mt_PlugDecl_Simple: decl_bitSize = {self.decl_bitSize}"
    def print_tree(self, prefix):
        print(f"{prefix}{repr(self)}")

    def __eq__(self, other):
        return type(other) == type(self) and other.decl_bitSize == self.decl_bitSize

    def resolve_name_lookups(self):
        pass
    def convert_to_metatype(self):
        return self
    def calc_sizes(self):
        pass



class mt_PlugDecl_Code(mt_PlugDecl):
    def __init__(self, code):
        self.code = code
    def print_tree(self, prefix):
        print(f"{prefix}mt_PlugDecl_Code:")
        print(f"{prefix}  code:")
        self.code.print_tree(prefix+"    ")

    def calc_sizes(self):
        self.code.calc_sizes()
        self.decl_bitSize = self.code.decl_bitSize



class mt_PlugDecl_ArrayOf(mt_PlugDecl):
    def __init__(self, base, len_):
        # NOTE: no nameScope required, since we have already resolved names
        self.base = base
        self.len_ = len_
    def print_tree(self, prefix):
        print(f"{prefix}mt_PlugDecl_ArrayOf:")
        print(f"{prefix}  base:")
        self.base.print_tree(prefix+"    ")
        print(f"{prefix}  len_={self.len_}")

    def __eq__(self, other):
        return type(self) == type(other) and \
               self.base  == other.base  and \
               self.len_  == other.len_

    def resolve_name_lookups(self):
        assert False, "You should never create this object until you have passed the name-lookup phase and then called resolve()"

    def calc_sizes(self):
        self.base.calc_sizes()
        self.decl_bitSize = self.base.decl_bitSize * self.len_

