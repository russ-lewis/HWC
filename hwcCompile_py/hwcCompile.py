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

