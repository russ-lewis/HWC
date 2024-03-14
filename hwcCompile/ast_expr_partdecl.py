
from ast_expr_metatypes import *



class mt_PartDecl_Code(mt_PartDecl):
    def __init__(self, code):
        self.code = code
        self.decl_bitSize = None
    def print_tree(self, prefix):
        print(f"{prefix}mt_PartDecl_Code:")
        print(f"{prefix}  code:")
        self.code.print_tree(prefix+"    ")

    def calc_sizes(self):
        if self.decl_bitSize == "in progress":
            assert False    # TODO: report cyclic declaration
        if self.decl_bitSize is not None:
            return
        self.decl_bitSize = "in progress"

        self.code.calc_sizes()
        self.decl_bitSize = self.code.decl_bitSize

    def calc_top_down_offsets(self, offset):
        pass
    def calc_bottom_up_offsets(self):
        pass

    def print_bit_descriptions(self, name, start_bit):
        self.code.print_bit_descriptions(f"{name}", start_bit)

    def print_wiring_diagram(self, start_bit):
        self.code.print_wiring_diagram(start_bit)



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

