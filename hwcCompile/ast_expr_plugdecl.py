
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

    def calc_top_down_offsets(self, offset):
        pass
    def calc_bottom_up_offsets(self):
        pass

    def resolve_name_lookups(self):
        pass
    def convert_to_metatype(self, side):
        return self
    def calc_sizes(self):
        pass

    def print_bit_descriptions(self, name, start_bit):
        print(f"# {start_bit:6d} {' ':6s} {name}")



class mt_PlugDecl_Code(mt_PlugDecl):
    def __init__(self, code):
        self.code = code
        self.decl_bitSize = None
    def print_tree(self, prefix):
        print(f"{prefix}mt_PlugDecl_Code:")
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

    def print_bit_descriptions(self, name, start_bit):
        self.code.print_bit_descriptions(f"{name}", start_bit)



class mt_PlugDecl_ArrayOf(mt_PlugDecl):
    def __init__(self, base, len_):
        # NOTE: no nameScope required, since we have already resolved names

        assert                                      isinstance(base, mt_PlugDecl)
        assert len_ is None or type(len_) == int or isinstance(len_, mt_StaticExpr), len_

        self.base = base
        self.len_ = len_
        self.decl_bitSize = None

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
        if self.decl_bitSize == "in progress":
            assert False    # TODO: report cyclic declaration
        if self.decl_bitSize is not None:
            return
        self.decl_bitSize = "in progress"

        self.base.calc_sizes()
        assert self.base.decl_bitSize > 0

        # it is permissible for the len_ to be None in the constructor, but if
        # so, then the caller must have fixed it up with an int or StaticExpr
        # before this call.

        if type(self.len_) != int:
            assert isinstance(self.len_, mt_StaticExpr)
            self.len_ = self.len_.resolve_static_expr()
            if type(self.len_) != int:
                TODO()    # report syntax error

        if self.len_ <= 0:
            TODO()    # report syntax error

        self.decl_bitSize = self.base.decl_bitSize * self.len_

    def print_bit_descriptions(self, name, start_bit):
        if type(self.base) == mt_PlugDecl_Bit:
            print(f"# {start_bit:6d} {start_bit+self.len_:6d} {name}")
        else:
            for i in range(self.len_):
                self.base.print_bit_descriptions(f"{name}[{i}]", start_bit + i*self.base.decl_bitSize)

