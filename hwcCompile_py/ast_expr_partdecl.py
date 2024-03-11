
from ast_expr_metatypes import *



class mt_PartDecl_Code(mt_PartDecl):
    def __init__(self, code):
        self.code = code
    def print_tree(self, prefix):
        print(f"{prefix}mt_PartDecl_Code:")
        print(f"{prefix}  code:")
        self.code.print_tree(prefix+"    ")



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

    def calc_sizes(self):
        assert False    # TODO: audit and port to the new design doc

