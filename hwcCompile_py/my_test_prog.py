#! /usr/bin/python3

# https://github.com/AlanHohn/antlr4-python/blob/master/hello-simple/Hello.py
# https://github.com/antlr/antlr4/blob/master/doc/python-target.md
# https://medium.com/@raguiar2/building-a-working-calculator-in-python-with-antlr-d879e2ea9058

from antlr4 import *
from hwcLexer    import hwcLexer
from hwcParser   import hwcParser
from hwcListener import hwcListener



def main():
    lexer  = hwcLexer(StdinStream())
    parser = hwcParser(CommonTokenStream(lexer))
    tree   = parser.file_()      # trailing underscore is because file is a Python type

    printer = HWCPrinter()
    ParseTreeWalker().walk(printer,tree)



class HWCPrinter(hwcListener):
    def enterFile(self, ctx):
        print(f"enterFile   {ctx} {type(ctx)}")
        print(ctx.getText())
        print(ctx.children)
        print()

    def exitFile(self, ctx):
        print(f"exitFile")
        print()



    def enterDecl(self, ctx):
        print(f"enterDecl   {ctx}")
        print(ctx.getText())
        print([str(e) for e in ctx.children])
        print()

    def exitDecl(self, ctx):
        print(f"exitDecl")
        print()



    def enterStmt_Decl(self, ctx):
        print(f"enterStmt_Decl   {ctx}")
        print(ctx.getText())
        print([str(e) for e in ctx.children])
        print()

    def exitStmt_Decl(self, ctx):
        print(f"exitStmt_Decl")
        print()



    def enterStmt_Connection(self, ctx):
        print(f"enterStmt_Connection   {ctx}")
        print(ctx.getText())
        print([str(e) for e in ctx.children])
        print()

    def exitStmt_Connection(self, ctx):
        print(f"exitStmt_Connection")
        print()



    def enterDeclStmt(self, ctx):
        print(f"enterDeclStmt   {ctx}")
        print(ctx.getText())
        print([str(e) for e in ctx.children])
        print()

    def exitDeclStmt(self, ctx):
        print(f"exitDeclStmt")
        print()



    def enterDeclList(self, ctx):
        print(f"enterDeclList   {ctx}")
        print(ctx.getText())
        print([str(e) for e in ctx.children])
        print()

    def exitDeclList(self, ctx):
        print(f"exitDeclList")
        print()



    def enterDeclInit(self, ctx):
        print(f"enterDeclInit   {ctx}")
        print(ctx.getText())
        print([str(e) for e in ctx.children])
        print()

    def exitDeclInit(self, ctx):
        print(f"exitDeclInit")
        print()



    def enterType_Bit(self, ctx):
        print(f"enterType_Bit   {ctx}")
        print(ctx.getText())
        print([str(e) for e in ctx.children])
        print()

    def exitType_Bit(self, ctx):
        print(f"exitType_Bit")
        print()



if __name__ == "__main__":
    main()

