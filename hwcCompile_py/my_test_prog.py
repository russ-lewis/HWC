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
    print(ast)



class HWCAstGenerator(hwcListener):
    def enterFile(self, ctx):
        ctx.file_nameScope = ast.NameScope(None)
    def exitFile(self, ctx):
        ctx.ast = [c.ast for c in ctx.decls]


    def exitDecl(self, ctx):
        assert (ctx.stmts == []) != (ctx.decls == [])
        if ctx.stmts != []:
            stmts = ctx.stmts
        else:
            stmts = ctx.decls
        stmts = [s.ast for s in stmts]

        ctx.ast = ast.Decl("plug", ctx.name.text, stmts, ctx.parentCtx.file_nameScope)


    def exitStmt_Decl(self, ctx):
        ast = ctx.children[1].ast

        prefix = ctx.children[0].getText()
        assert prefix in ["", "subpart", "public", "private"]
        if prefix != "":
            ast.prefix = prefix

        ctx.ast = ast


    def exitStmt_Connection(self, ctx):
        ctx.ast = ast.ConnStmt()


    def exitDeclStmt_VarDecl(self, ctx):
        ctx.ast = ast.VarDecl()



if __name__ == "__main__":
    main()

