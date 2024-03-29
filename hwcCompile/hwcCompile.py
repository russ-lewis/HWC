#! /usr/bin/python3

from grammar2ast import grammar2ast;
from ast import g_PartOrPlugDecl,SyntaxError



def main():
    ast = grammar2ast()

    # if() statements are weird for our parser, because we want to build our
    # conditions from the top-down (if statements applying their condition to
    # statements inside them), but the tree is built from the bottom-up.  I
    # tried to do this with ANLTR enter/exit functions, but that didn't work,
    # because the condition wasn't known in enter(), and the statement was
    # already built by the time that if() gets its exit().  So a
    # post-processing step is required.
    ast.deliver_if_conditions()

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

    # this was called Phase 35 in the old (C++) compiler.  But it is split
    # into two phases here, in order to prevent the need for recursion from
    # one type into another.  In the first call, we establish the offset of
    # each statement, based on decl_bitSize fields; it is *top-down*.  We
    # recurse through nested statements inside a single PartOrPlug, and we
    # also recurse into all expressions, since many expressions have their
    # own # temporary values, which need offsets which are assigned top-down.
    # However, we refuse to resolve the offset of any IDENTs or dot-exprs,
    # since those require lookup of offsets of other declarations, which might
    # not be declared yet.
    #
    # In the second call, we re-traverse the entire tree, but now fill in the
    # missing offsets (those that must be resolved bottom-up), which include
    # IDENTs, dot-exprs, array-index, and array-slicing.
    ast.calc_top_down_offsets(None)
    ast.calc_bottom_up_offsets()


    main_part = ast.nameScope.search("main")
    assert type(main_part) == g_PartOrPlugDecl, type(main_part)
    assert      main_part.isPart

    main_part.print_bit_descriptions("main", 0)
    print()
    main_part.print_wiring_diagram(0)



if __name__ == "__main__":
    try:
        main()
    except SyntaxError as e:
        print(f"{e.lineInfo}: {e.message}")

