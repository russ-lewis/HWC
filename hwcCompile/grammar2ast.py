#! /usr/bin/python3

# https://github.com/AlanHohn/antlr4-python/blob/master/hello-simple/Hello.py
# https://github.com/antlr/antlr4/blob/master/doc/python-target.md
# https://medium.com/@raguiar2/building-a-working-calculator-in-python-with-antlr-d879e2ea9058

from antlr4 import *

from hwcLexer    import hwcLexer
from hwcParser   import hwcParser
from hwcListener import hwcListener

import ast;
import ast_expr_metatypes;



def grammar2ast():
    lexer  = hwcLexer(StdinStream())
    lexer.removeErrorListeners()
    lexer.addErrorListener(HWCErrorListener())

    parser = hwcParser(CommonTokenStream(lexer))
    parser.removeErrorListeners()
    parser.addErrorListener(HWCErrorListener())

    tree   = parser.file_()      # trailing underscore is because file is a Python type

    printer = HWCAstGenerator("stdin")
    ParseTreeWalker().walk(printer,tree)

    return tree.ast



class HWCErrorListener(error.ErrorListener.ErrorListener):    # https://snyk.io/advisor/npm-package/antlr4/functions/antlr4.error
    def syntaxError(self, recognizer, offending_symbol, line,col, msg, e):   # what is the 'e' param???
        lineInfo = ast.LineInfo("<TODO_filename>", line,col+1, 1)
        raise ast.HWCCompile_SyntaxError(lineInfo, msg)



# HELPER FUNCTION
def flatten(stmts):
    retval = []
    for s in stmts:
        if type(s) == hwcParser.Stmt_DeclContext:
            retval.extend(s.ast_arr)
        else:
            retval.append(s.ast)
    return retval


class HWCAstGenerator(hwcListener):
    def __init__(self, filename):
        self.filename = filename


    def build_line_info(self, root):
        root_line = root.line
        root_col  = root.column+1
        root_len  = len(root.text)
        return ast.LineInfo(self.filename, root_line,root_col,root_len)

    def build_line_range(self, ctx):
        start = ctx.start
        stop  = ctx.stop
        return ast.LineRange(self.filename, start.line, stop.line)


    def exitFile(self, ctx):
        ctx.ast = ast.g_File([c.ast for c in ctx.decls])


    def exitPartOrPlugOrFuncDecl(self, ctx):
        if ctx.retType is not None:
            TODO()    # implement function declarations

        partOrPlug = ctx.isPart.text
        name       = ctx.name.text

        assert partOrPlug in ["part","plug"]
        isPart = (partOrPlug == "part")

        ctx.ast = ast.g_PartOrPlugDecl(isPart, name, flatten(ctx.stmts))


    def exitStmt_Block(self, ctx):
        # if() statements that wrap this statement will want to know this
        ctx.uncovered_else = False
        ctx.if_type = None

        ctx.ast = ast.g_BlockStmt(flatten(ctx.stmts))


    def exitStmt_Decl(self, ctx):
        prefix =  ctx.prefix.text if ctx.prefix is not None else None
        mem    = (ctx.mem is not None)
        typ_   =  ctx.t.ast

        lineInfo = self.build_line_range(ctx)

        decls = []
        for d in ctx.decls:
            name    = d.name.text
            initVal = d.val.ast if d.val is not None else None
            stmt = ast.g_DeclStmt(lineInfo, prefix,mem,typ_, name,initVal)
            decls.append(stmt)

        assert len(decls) >= 1
        ctx.ast_arr = decls

        # it is *highly* unlikely that we'll ever see a declaration statement
        # that is not inside a {} but is inside an if().  But in case we do,
        # we should let them know this.
        ctx.uncovered_else = False
        ctx.if_type = None


    def exitStmt_Connection(self, ctx):
        assert len(ctx.lhs) >= 1
        if len(ctx.lhs) > 1:
            assert False, "TODO-implement-chain-assignment"    # maybe generate n-1 connection statements in a block?

        lineInfo = self.build_line_range(ctx)
        ctx.ast = ast.g_ConnStmt(lineInfo, ctx.lhs[0].ast, ctx.rhs.ast)

        # if() statements that wrap this statement will want to know this
        ctx.uncovered_else = False
        ctx.if_type = None


    def exitStmt_If(self, ctx):
        ctx.uncovered_else = (ctx.fals_ is not None)
        if not ctx.uncovered_else and ctx.tru_.uncovered_else:
            TODO()    # report syntax error

        ctx.if_type = "runtime" if ctx.static is None else "static"
        if ctx.tru_ .if_type is not None and \
           ctx.tru_ .if_type != ctx.if_type:
            TODO()    # report syntax error
        if ctx.fals_ is not None         and \
           ctx.fals_.if_type is not None and \
           ctx.fals_.if_type != ctx.if_type:
            TODO()    # report syntax error

        assert ctx.tru_ is not None
        cond  = ctx.cond.ast
        tru_  = ctx.tru_ .ast
        fals_ = ctx.fals_.ast if ctx.fals_ is not None else None

        lineInfo_whole = self.build_line_range(ctx)
        lineInfo_else  = self.build_line_info (ctx.els_) if ctx.fals_ is not None else None

        if ctx.static is None:
            ctx.ast = ast.g_RuntimeIfStmt(lineInfo_whole, lineInfo_else,
                                          cond, tru_, fals_)

        else:
            # VERSION 1 OF STATIC IF() DECLARATIONS
            #   - Create new nameScope for both blocks (if,else)
            #   - Add new names *only* to the new nameScope
            #   - Require static if() code to "reach out" to other, non-static-if variables
            # VERSION 2 OF STATIC IF() DECLARATIONS
            #   In addition to VERSION 1, also:
            #   - Add all declarations to the parent context as well, but under a "static-if-declaration" wrapper; the name points to the static-if wrapper, and there are many possible declarations underneath
            #   - Must add to both "private" and "public" nameScopes
            #   - Names in the parent scope map to the wrapper object, many possible actual-declarations under each wrapper
            #   - Early in compile, confirm that all declarations under a common wrapper are the same general sort (Expr metatype)
            #   - After size() phase in the compiler, resolve all static if()s and replace wrappers with final declarations
            #   - Have a check for "in this case, nothing is declared?"

            ctx.ast = ast.g_StaticIfStmt(lineInfo_whole, lineInfo_else,
                                         cond, tru_, fals_)

    def exitStmt_Assert(self, ctx):
        lineInfo = self.build_line_range(ctx)
        is_static = ctx.static is not None
        ctx.ast = ast.g_AssertStmt(lineInfo, is_static, ctx.exp_.ast)

        # if() statements that wrap this statement will want to know this
        ctx.uncovered_else = False
        ctx.if_type = None


    def exitStmt_For(self, ctx):
        var   = ctx.var.text
        start = ctx.start.ast
        end   = ctx.end  .ast
        body  = ctx.body .ast

        tuple_name = ctx.tuple_name.text if ctx.tuple_name is not None else None

        # most non-trivial for() loops will have {}, which means that uncovered
        # else's inside them are harmless.  However, we already have code that
        # handles {}.  But not all for() loops are harmless.  Consider this code,
        # which definitely has an uncovered else problem:
        #    if (foo)
        #        for (i; 0..32)
        #            if (bar)
        #                x == y;
        #
        # Thus, for() loops must *inherit* their uncovered-else property from
        # their body statement.
        ctx.uncovered_else = ctx.body.uncovered_else
        ctx.if_type        = ctx.body.if_type

        lineInfo = self.build_line_info(ctx.var)
        ctx.ast = ast.g_ForStmt(lineInfo, var, start,end, body, tuple_name)


    def exitExpr(self, ctx):
        assert ctx.left is not None
        if   len(ctx.right) == 0:
            ctx.ast = ctx.left.ast

        elif len(ctx.right) == 1:
            lineInfo = self.build_line_info(ctx.op)
            ctx.ast = ast.g_BinaryExpr(lineInfo, ctx.left.ast, ctx.op.text, ctx.right[0].ast)

        else:
            lineInfo = self.build_line_info(ctx.op)

            soFar = ctx.left.ast
            for r in ctx.right:
                soFar = ast.g_BinaryExpr(lineInfo, soFar, ctx.op.text, r.ast)

            ctx.ast = soFar


    # all binary operators have the same implementation in the AST.  We use
    # different rules to enforce associativity, but once it's established,
    # we just use the tree structure to maintain the associations.
    exitExpr2 = exitExpr
    exitExpr3a = exitExpr
    exitExpr3b = exitExpr
    exitExpr4 = exitExpr
    exitExpr5 = exitExpr
    exitExpr6 = exitExpr


    def exitExpr7(self, ctx):
        assert (ctx.base is not None) != (ctx.right is not None)

        if ctx.base is not None:
            ctx.ast = ctx.base.ast

        else:
            op = ctx.op.text
            assert op in ["!", "-", "~"]
            lineInfo = self.build_line_info(ctx.op)
            ctx.ast = ast.g_UnaryExpr(lineInfo, op, ctx.right.ast)


    def exitExpr8(self, ctx):
        assert (ctx.base is not None) != (ctx.left is not None)

        if ctx.base is not None:
            ctx.ast = ctx.base.ast

        elif ctx.field is not None:
            lineInfo = self.build_line_info(ctx.field)
            ctx.ast = ast.g_DotExpr(lineInfo, ctx.left.ast, ctx.field.text)

        elif ctx.a is not None and ctx.colon is None:
            # either declaration of an array type, if the underlying expression
            # is a type, or indexing into an array, if the underlying
            # expression is a runtime value.
            #
            # We must defer the resolution of what it is until later, when we
            # have resolved the names; then we will replace this object with
            # one of the proper type.
            lineInfo = self.build_line_range(ctx.a)
            ctx.ast = ast.g_Unresolved_Single_Index_Expr(lineInfo, ctx.left.ast, ctx.a.ast)

        elif ctx.a is not None and ctx.colon is not None and ctx.b is None:
            # slice of a runtime value, which goes to the end of the array
            lineInfo = self.build_line_range(ctx.a)
            ctx.ast = ast.g_ArraySlice(lineInfo,
                                       ctx.left.ast,
                                       ctx.a.ast,
                                       None)

        elif ctx.a is None and ctx.colon is not None and ctx.b is not None:
            # slice of a runtime value, which starts at the beginning of the array
            lineInfo = self.build_line_range(ctx.b)
            ctx.ast = ast.g_ArraySlice(lineInfo,
                                       ctx.left.ast,
                                       ast.g_NumExpr("0"),
                                       ctx.b.ast)

        elif ctx.a is not None and ctx.colon is not None and ctx.b is not None:
            # slice of a runtime value
            assert ctx.b.ast is not None
            lineInfo = self.build_line_range(ctx.a)
            ctx.ast = ast.g_ArraySlice(lineInfo,
                                       ctx.left.ast,
                                       ctx.a.ast,
                                       ctx.b.ast)

        else:
            assert False, "Unrecognized expression"


    def exitExpr9(self, ctx):
        if ctx.subexpr is not None:
            ctx.ast = ctx.subexpr.ast

        elif ctx.name is not None:
            lineInfo = self.build_line_info(ctx.name)
            ctx.ast = ast.g_IdentExpr(lineInfo, ctx.name.text)
        elif ctx.num is not None:
            ctx.ast = ast.g_NumExpr(ctx.num.text)

        elif ctx.children[0].getText() == "true":
            ctx.ast = ast.g_BoolExpr("true")
        elif ctx.children[0].getText() == "false":
            ctx.ast = ast.g_BoolExpr("false")

        elif ctx.funcName is not None:
            lineInfo = self.build_line_info(ctx.funcName)
            funcName = ctx.funcName.text

            # check all of the built-in functions; otherwise, it must be a
            # user function
            if funcName == "concat":
                if len(ctx.funcArgs) != 2:
                    raise HWC_SyntaxError(lineInfo, "The built-in function concat() requires exactly two arguments.  TODO: support arbitrary numbers of arguments.")
                ctx.ast = ast.g_BinaryExpr(lineInfo,
                                           ctx.funcArgs[0].ast,
                                           "concat",
                                           ctx.funcArgs[1].ast)

            elif funcName == "decode":
                if len(ctx.funcArgs) != 1:
                    raise HWC_SyntaxError(lineInfo, "The built-in function decode() requires exactly one argument.")
                ctx.ast = ast.g_DecodeExpr(lineInfo, ctx.funcArgs[0].ast)

            elif funcName == "masked_select":
                TODO()
                if len(ctx.funcArgs) != 2:
                    raise HWC_SyntaxError(lineInfo, "The built-in function masked_select() requires exactly two arguments.")
                ctx.ast = ast.g_MaskedSelectExpr(lineInfo, ctx.funcArgs[0].ast, ctx.funcArgs[1].ast)

            elif funcName in ["typeof","len","sizeof"]:
                if len(ctx.funcArgs) != 1:
                    raise HWC_SyntaxError(lineInfo, f"The built-in function {funcName}() requires exactly one argument.")
                ctx.ast = ast.g_GetExprProp(lineInfo, funcName, ctx.funcArgs[0].ast)

            else:
                TODO()    # implement user-defined functions

        elif ctx.children[0].getText() == "bit":
            ctx.ast = ast_expr_metatypes.plugType_bit
        elif ctx.children[0].getText() == "flag":
            ctx.ast = ast_expr_metatypes.plugType_flag

        elif ctx.children[0].getText() == "auto":
            ctx.ast = ast_expr_metatypes.plugType_auto

        elif ctx.children[0].getText() == "int":
            ctx.ast = ast_expr_metatypes.staticType_int
        elif ctx.children[0].getText() == "bool":
            ctx.ast = ast_expr_metatypes.staticType_bool

        else:
            assert False, "Unrecognized expression"

