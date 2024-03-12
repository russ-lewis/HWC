#! /usr/bin/python3

from grammar2ast import grammar2ast;
from ast import g_PartOrPlugDecl



def main():
    ast = grammar2ast()

    # this was called Phase 10 in the old (C++) compiler
    ast.populate_name_scopes()

    # this was called Phase 20 in the old (C++) compiler
    ast.resolve_name_lookups()

    # this was not in the old compiler; I've added it, because sorting
    # expressions into their metatypes makes the rest of the phases
    # easier to handle.
    ast.convert_exprs_to_metatypes()

    # this was called Phase 30 in the old (C++) compiler
    ast.calc_sizes()

    # TODO: once static-if() is implemented, we will resolve all of
    #       those statements as part of the call above.  This is
    #       necessary (the two cannot be separated) because (a) some
    #       static-if expressions need to know the size of types; and
    #       (b) static-if expressions can impact the size of types.
    #
    # Note that even before static-if exists, static expressions (like
    # sizeof) could cause some complexity here.  I'm not using them yet -
    # but I'll probably add them soon.

    # this was called Phase 35 in the old (C++) compiler
    ast.calc_offsets()

    main_part = ast.nameScope.search("main")
    assert type(main_part) == g_PartOrPlugDecl
    assert      main_part.isPart

    main_part.print_tree("")

    print()
    print(f"main part size: {main_part.decl_bitSize}")
    print()
    for d in ast.decls:
        print(f"name: {d.name} isPart: {d.isPart} decl_bitSize: {d.decl_bitSize}")



if __name__ == "__main__":
    main()

