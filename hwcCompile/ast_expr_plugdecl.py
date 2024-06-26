
from ast_expr_metatypes import *
from ast import HWCCompile_SyntaxError



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
    def dup(self):
        return self
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

    def resolve_name_lookups(self, ns_pri):
        pass
    def convert_to_metatype(self, side):
        return self
    def calc_sizes(self):
        pass

    def print_bit_descriptions(self, name, start_bit):
        print(f"# {start_bit:6d} {' ':6s} {name}")



class mt_PlugDecl_Flag(mt_PlugDecl):
    leafNode = True
    decl_bitSize = 2

    def __init__(self):
        pass
    def dup(self):
        return self
    def __repr__(self):
        return f"mt_PlugDecl_Flag"
    def print_tree(self, prefix):
        print(f"{prefix}{repr(self)}")

    def __eq__(self, other):
        return type(other) == type(self)

    def calc_top_down_offsets(self, offset):
        pass
    def calc_bottom_up_offsets(self):
        pass

    def resolve_name_lookups(self, ns_pri):
        pass
    def convert_to_metatype(self, side):
        return self
    def calc_sizes(self):
        pass

    def print_bit_descriptions(self, name, start_bit):
        print(f"# {start_bit:6d} {' ':6s} {name}(r)")
        print(f"# {start_bit+1:6d} {' ':6s} {name}(w)")



class mt_PlugDecl_Auto(mt_PlugDecl):
    leafNode = True
    decl_bitSize = "unknown"

    def __init__(self):
        pass
    def dup(self):
        return self
    def __repr__(self):
        return f"mt_PlugDecl_Auto"
    def print_tree(self, prefix):
        print(f"{prefix}{repr(self)}")

    def __eq__(self, other):
        assert False    # any code that tries to compare 'auto' to something else is broken

    def resolve_name_lookups(self, ns_pri):
        pass
    def convert_to_metatype(self, side):
        return self
    def calc_sizes(self):
        pass



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
    def __init__(self, lineInfo, base, len_):
        self.lineInfo = lineInfo

        # NOTE: no nameScope required, since we have already resolved names

        if type(base) == mt_PlugDecl_Auto:
            raise HWCCompile_SyntaxError(None, "auto-array declarations are not yet supported by this compiler")

        assert                                      isinstance(base, mt_PlugDecl)
        assert len_ is None or type(len_) == int or isinstance(len_, mt_StaticExpr), len_

        self.base = base
        self.len_ = len_
        self.decl_bitSize = None
    def dup(self):
        assert self.decl_bitSize is None
        base_dup = self.base.dup()
        len_dup  = self.len_.dup() if self.len_ is not None else None
        return mt_PlugDecl_ArrayOf(self.lineInfo, base_dup, len_dup)

    def print_tree(self, prefix):
        print(f"{prefix}mt_PlugDecl_ArrayOf:")
        print(f"{prefix}  base:")
        self.base.print_tree(prefix+"    ")
        print(f"{prefix}  len_={self.len_}")

    def __eq__(self, other):
        if type(self) != type(other):
            return False

        # doing a type comparison, before the length is known, is invalid.
        assert self.len_ is not None and other.len_ is not None

        return self.len_ == other.len_ and self.base == other.base

    def get_multidim_base(self):
        if type(self.base) == mt_PlugDecl_ArrayOf:
            return self.base.get_multidim_base()
        else:
            return self.base

    def resolve_name_lookups(self, ns_pri):
        assert False, "You should never create this object until you have passed the name-lookup phase and then called resolve()"

    def convert_to_metatype(self, side):
        return self

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
            assert isinstance(self.len_, mt_StaticExpr), self.len_
            self.len_ = self.len_.resolve_static_expr()
            if type(self.len_) != int:
                TODO()    # report syntax error

        if self.len_ <= 0:
            raise HWCCompile_SyntaxError(self.lineInfo, f"Arrays of length {self.len_} are not valid in HWC")

        self.decl_bitSize = self.base.decl_bitSize * self.len_

    def print_bit_descriptions(self, name, start_bit):
        if type(self.get_multidim_base()) == mt_PlugDecl_Bit:
            print(f"# {start_bit:6d} {start_bit+self.decl_bitSize:6d} {name}")
        else:
            for i in range(self.len_):
                self.base.print_bit_descriptions(f"{name}[{i}]", start_bit + i*self.base.decl_bitSize)

