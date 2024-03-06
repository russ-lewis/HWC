#! /usr/bin/python3

# https://github.com/AlanHohn/antlr4-python/blob/master/hello-simple/Hello.py
# https://github.com/antlr/antlr4/blob/master/doc/python-target.md
# https://medium.com/@raguiar2/building-a-working-calculator-in-python-with-antlr-d879e2ea9058

from antlr4 import *
from hwcLexer    import hwcLexer
from hwcParser   import hwcParser
from hwcListener import hwcListener

import ast;



def main():
    lexer  = hwcLexer(StdinStream())
    parser = hwcParser(CommonTokenStream(lexer))
    tree   = parser.file_()      # trailing underscore is because file is a Python type

    printer = HWCAstGenerator()
    ParseTreeWalker().walk(printer,tree)

    ast = tree.ast

    # this was called Phase 10 in the old (C++) compiler
    ast.populate_name_scopes()

    # this was called Phase 20 in the old (C++) compiler
    ast.resolve_name_lookups()

    print()
    ast.print_tree("")
    print()
    print("---------------")
    print()

    # this was not in the old compiler; I've added it, because sorting
    # expressions into their metatypes makes the rest of the phases
    # easier to handle.
    ast.convert_exprs_to_metatypes()

    # this was called Phase 30 in the old (C++) compiler
    ast.calc_sizes_and_offsets()

    ast.print_tree("")



class HWCAstGenerator(hwcListener):
    def enterFile(self, ctx):
        ctx.nameScope = ast.NameScope(None)
    def exitFile(self, ctx):
        ctx.ast = ast.File(ctx.nameScope, [c.ast for c in ctx.decls])


    def default_enter_newScope(self, ctx):
        ctx.nameScope = ast.NameScope(ctx.parentCtx.nameScope)
    def default_enter_sameScope(self, ctx):
        ctx.nameScope = ctx.parentCtx.nameScope


    enterTypeDecl = default_enter_newScope
    def exitTypeDecl(self, ctx):
        ns         = ctx.nameScope
        partOrPlug = ctx.children[0].getText()
        name       = ctx.name.text

        def flatten(stmts):
            retval = []
            for s in stmts:
                if type(s) in [hwcParser.Stmt_DeclContext,     # used for parts
                               hwcParser. DeclStmtContext ]:   # used for plugs
                    retval.extend(s.ast_arr)
                else:
                    retval.append(s.ast)
            return retval

        if partOrPlug == "part":
            assert len(ctx.decls) == 0
            ctx.ast = ast.PartDecl(ns, name, flatten(ctx.stmts))
        else:
            assert len(ctx.stmts) == 0
            ctx.ast = ast.PlugDecl(ns, name, flatten(ctx.decls))


    enterDeclStmt = default_enter_sameScope
    def exitDeclStmt(self, ctx):
        ns  =  ctx.nameScope
        mem = (ctx.mem is not None)
        typ =  ctx.t.ast

        ctx.ast_arr = []
        for d in ctx.decls:
            name    = d.name.text

            if d.val is None:
                initVal = None
            else:
                initVal = d.val.ast

            stmt = ast.DeclStmt(ns,mem,typ, name,initVal)
            ctx.ast_arr.append(stmt)


    enterDeclNameInit = default_enter_sameScope
    def exitDeclNameInit(self, ctx):
        pass


    enterStmt_Decl = default_enter_sameScope
    def exitStmt_Decl(self, ctx):
        prefix = ctx.children[0].getText()
        decls  = ctx.children[1].ast_arr

        # apply the prefix to all of the decls
        assert prefix in ["subpart", "public", "private", "static"]
        for d in decls:
            d.prefix = prefix

        assert len(decls) >= 1
        ctx.ast_arr = decls


    enterStmt_Connection = default_enter_sameScope
    def exitStmt_Connection(self, ctx):
        assert len(ctx.lhs) >= 1
        if len(ctx.lhs) > 1:
            assert False, "TODO-implement-chain-assignment"    # maybe generate n-1 connection statements in a block?
        ctx.ast = ast.ConnStmt(ctx.lhs[0].ast, ctx.rhs.ast)


    enterExpr = default_enter_sameScope
    def exitExpr(self, ctx):
        assert ctx.left is not None
        if ctx.right != []:
            assert False    # TODO implement me
        ctx.ast = ctx.left.ast


    # all binary operators have the same implementation in the AST.  We use
    # different rules to enforce associativity, but once it's established,
    # we just use the tree structure to maintain the associations.
    enterExpr2 = enterExpr
    exitExpr2  = exitExpr
    enterExpr3 = enterExpr
    exitExpr3  = exitExpr
    enterExpr4 = enterExpr
    exitExpr4  = exitExpr
    enterExpr5 = enterExpr
    exitExpr5  = exitExpr
    enterExpr6 = enterExpr
    exitExpr6  = exitExpr


    enterExpr7 = default_enter_sameScope
    def exitExpr7(self, ctx):
        assert (ctx.base is not None) != (ctx.right is not None)

        if ctx.base is not None:
            ctx.ast = ctx.base.ast

        else:
            assert False, "Unrecognized expression"


    enterExpr8 = default_enter_sameScope
    def exitExpr8(self, ctx):
        assert (ctx.base is not None) != (ctx.left is not None)

        if ctx.base is not None:
            ctx.ast = ctx.base.ast

        elif ctx.field is not None:
            ctx.ast = TODO()

        elif ctx.a is not None and ctx.colon is None:
            # either declaration of an array type, if the underlying expression
            # is a type, or indexing into an array, if the underlying
            # expression is a runtime value.
            #
            # We must defer the resolution of what it is until later, when we
            # have resolved the names; then we will replace this object with
            # one of the proper type.
            ctx.ast = ast.Unresolved_Single_Index_Expr(ctx.nameScope, ctx.left.ast, ctx.a.ast)

        elif ctx.a is not None and ctx.colon is not None:
            # slice of a runtime value, which goes to the end of the array

            ctx.ast = TODO()

        elif ctx.a is None and ctx.colon is not None and ctx.b is not None:
            # slice of a runtime value, which starts at the beginning of the array

            ctx.ast = TODO()

        elif ctx.a is not None and ctx.colon is not None and ctx.b is not None:
            # slice of a runtime value

            ctx.ast = TODO()

        else:
            assert False, "Unrecognized expression"


    enterExpr9 = default_enter_sameScope
    def exitExpr9(self, ctx):
        if ctx.subexpr is not None:
            ctx.ast = ctx.subexpr.ast

        elif ctx.name is not None:
            ctx.ast = ast.IdentExpr(ctx.nameScope, ctx.name.text)
        elif ctx.num is not None:
            ctx.ast = ast.NumExpr(ctx.num.text)

        elif ctx.children[0].getText() == "true":
            ctx.ast = TODO()
        elif ctx.children[0].getText() == "false":
            ctx.ast = TODO()

        elif ctx.children[0].getText() == "bit":
            ctx.ast = ast.BitType()
        elif ctx.children[0].getText() == "flag":
            ctx.ast = TODO()

        elif ctx.children[0].getText() == "typeof":
            ctx.ast = TODO()

        elif ctx.children[0].getText() == "int":
            ctx.ast = TODO()
        elif ctx.children[0].getText() == "bool":
            ctx.ast = TODO()

        else:
            assert False, "Unrecognized expression"


    enterType_Named = default_enter_sameScope
    def exitType_Named(self, ctx):
        ctx.ast = ast.IdentExpr(ctx.nameScope, ctx.name.text)



if __name__ == "__main__":
    main()

