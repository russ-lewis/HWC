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

    # this was called Phase 10 in the old compiler, that was written in C++
    ast.populate_name_scopes()

    # this was called Phase 20 in the old compiler, that was written in C++
    ast.resolve_name_lookups()

    ast.print_tree("")



class HWCAstGenerator(hwcListener):
    def default_enter(self, ctx):
        ctx.nameScope = ast.NameScope(None)

    enterFile = default_enter
    def exitFile(self, ctx):
        ctx.ast = ast.File(ctx.nameScope, [c.ast for c in ctx.decls])


    enterTypeDecl = default_enter
    def exitTypeDecl(self, ctx):
        ns         = ctx.nameScope
        partOrPlug = ctx.children[0].getText()
        name       = ctx.name.text

        def flatten(stmts):
            retval = []
            for s in stmts:
                if type(s) == hwcParser.Stmt_DeclContext:
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


    enterDeclStmt = default_enter
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


    enterStmt_Decl = default_enter
    def exitStmt_Decl(self, ctx):
        prefix = ctx.children[0].getText()
        decls  = ctx.children[1].ast_arr

        # apply the prefix to all of the decls
        assert prefix in ["subpart", "public", "private", "static"]
        for d in decls:
            d.prefix = prefix

        assert len(decls) >= 1
        ctx.ast_arr = decls


    enterStmt_Connection = default_enter
    def exitStmt_Connection(self, ctx):
        assert len(ctx.lhs) >= 1
        if len(ctx.lhs) > 1:
            assert False, "TODO-implement-chain-assignment"    # maybe generate n-1 connection statements in a block?
        ctx.ast = ast.ConnStmt(ctx.lhs[0].ast, ctx.rhs.ast)


    enterExpr = default_enter
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


    enterExpr7 = default_enter
    def exitExpr7(self, ctx):
        assert (ctx.base is not None) != (ctx.right is not None)

        if ctx.base is not None:
            ctx.ast = ctx.base.ast
        else:
            assert False, "TODO"


    enterExpr8 = default_enter
    def exitExpr8(self, ctx):
        assert (ctx.base is not None) != (ctx.left is not None)

        if ctx.base is not None:
            ctx.ast = ctx.base.ast
        else:
            assert False, "TODO"


    enterExpr9 = default_enter
    def exitExpr9(self, ctx):
        if ctx.subexpr is not None:
            ctx.ast = ctx.subexpr.ast
        elif ctx.name is not None:
            ctx.ast = ast.IdentExpr(ctx.name.text)
        elif ctx.num is not None:
            ctx.ast = ast.NumExpr(ctx.num.text)

        else:
            assert False, "TODO-more-base-expressions"


    enterType_Bit = default_enter
    def exitType_Bit(self, ctx):
        ctx.ast = ast.BitType()
        


if __name__ == "__main__":
    main()

