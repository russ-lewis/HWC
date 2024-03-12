
from ast_expr_metatypes import *



class mt_PlugDecl_Bit(mt_PlugDecl):
    leafNode = True

    # BUGFIX: This used to have a decl_bitSize parameter.  But I also had
    #         ArrayOf(bit) to represent an array of bits.  In time, I
    #         realized that the *only* reason to have that parameter in
    #         this type was to support arrays...and we had a better way
    #         to do it over there.  So I considered *banning* using ArrayOf
    #         for 1D arrays of bits, but then I realized that I needed to
    #         handle bit, bit[1], bit[0] all as separate types.  So I
    #         decided that bit[x] must be ArrayOf(bit, x)

    decl_bitSize = 1

    def __init__(self):
        pass
    def __repr__(self):
        return f"mt_PlugDecl_Bit"
    def print_tree(self, prefix):
        print(f"{prefix}{repr(self)}")

    def __eq__(self, other):
        return type(other) == type(self)

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

