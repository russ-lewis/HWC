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
    parser = hwcParser(CommonTokenStream(lexer))
    tree   = parser.file_()      # trailing underscore is because file is a Python type

    printer = HWCAstGenerator()
    ParseTreeWalker().walk(printer,tree)

    return tree.ast



def build_line_info(root):
    root_line = root.line
    root_col  = root.column+1
    root_len  = len(root.text)
    return ast.LineInfo(root_line,root_col,root_len)

def build_line_range(ctx):
    start = ctx.start
    stop  = ctx.stop
    return ast.LineRange(start.line, stop.line)



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
    def enterFile(self, ctx):
        ctx.nameScope = ast.NameScope(None)
    def exitFile(self, ctx):
        ctx.ast = ast.g_File(ctx.nameScope, [c.ast for c in ctx.decls])


    def enterPartOrPlugDecl(self, ctx):
        # a part or plug declaration has *TWO* nameScope objects.  The "public"
        # nameScope is for use by external code, which is attempting to access
        # the fields of the part.  This will *only* include fields that are
        # declared public, which cannot (currently) include static variables
        # and subparts.  (Note that in a plug, *all* declarations are assumed
        # to be public.)
        #
        # The "private" nameScope is for use by internal code, to access the
        # fields and subparts declared inside this part.  Or rather, this is
        # the nameScope used for *all* lookups by code inside this part (or
        # plug).  It has the public fields, of course, and the private fields -
        # but also includes a parent pointer to the enclosing scope.
        #
        # (Why do plugs have a private nameScope for lookup, when they can't
        # have any statements other than declarations?  Because those
        # declarations have expressions inside them, and the expressions might
        # do name lookups for the fields of the plug, such as "typeof(fieldX)".
        # Plus, we're planning ahead for the future, when plugs might include
        # static-if statements.)
        #
        # When we build a new nameScope inside a part or plug (as part of an
        # if() or curly-brace statement), it is always a child of the "private"
        # nameScope.
        ctx.pub_nameScope = ast.NameScope(None)
        ctx.pri_nameScope = ast.NameScope(ctx.parentCtx.nameScope)

    def exitPartOrPlugDecl(self, ctx):
        ns_pub     = ctx.pub_nameScope
        ns_pri     = ctx.pri_nameScope
        partOrPlug = ctx.isPart.text
        name       = ctx.name.text

        assert partOrPlug in ["part","plug"]
        isPart = (partOrPlug == "part")

        # NOTE: While we needed both the public and private nameScope's to
        #       build our AST (because our children in the grammar will need
        #       access to the private nameScope for their own lookups,
        #       eventually), the AST object which represents this part doesn't
        #       need both; it only needs the public.  This is because no one
        #       will use the AST object for the Plug/Part for name lookups
        #       *except* for field lookups.

        ctx.ast = ast.g_PartOrPlugDecl(isPart, ns_pub, name, flatten(ctx.stmts))


    def default_enter_stmt(self, ctx):
        # for every statement type except DeclStmt, public field declarations
        # nested inside it are illegal.  (You can declare public fields inside
        # a for() loop, but they are public only in the sense that they are
        # visible outside the for() loop.  They are not visible outside the
        # part that declares the for() loop.
        #
        # What about double for() loops?  Should the enclosing part be able to
        # see inside the 2nd-level for() loop?  That seems reasonable.  So
        # maybe we'll make a distinction about that in the future.  TODO
        # But remember to think about cases where the for() loops are not
        # contiguous.  What about the nasty case of:
        #      for (i; ...) as outer
        #          if (x)
        #              for (j; ...) as inner;
        #          else
        #              for (j; ...) as inner;
        # Big difficult TODO, it turns out!

        ctx.pub_nameScope = None
        ctx.pri_nameScope = ctx.parentCtx.pri_nameScope


    def enterDeclNameInit(self, ctx):
        ctx.pri_nameScope = ctx.parentCtx.pri_nameScope
    def exitDeclNameInit(self, ctx):
        pass


    def enterStmt_Block(self, ctx):
        # a {} block creates a new scope for declaring private fields, but
        # we don't support public declarations inside such a scope.
        ctx.pri_nameScope = ast.NameScope(ctx.parentCtx.pri_nameScope)
        ctx.pub_nameScope = None

    def exitStmt_Block(self, ctx):
        ns_pub =  ctx.pub_nameScope
        ns_pri =  ctx.pri_nameScope
        ctx.ast = ast.g_BlockStmt(ns_pub,ns_pri, flatten(ctx.stmts))


    def enterStmt_Decl(self, ctx):
        # decl statements are allowed to post public names
        ctx.pub_nameScope = ctx.parentCtx.pub_nameScope
        ctx.pri_nameScope = ctx.parentCtx.pri_nameScope
    def exitStmt_Decl(self, ctx):
        ns_pub =  ctx.pub_nameScope
        ns_pri =  ctx.pri_nameScope

        prefix =  ctx.prefix.text if ctx.prefix is not None else None
        mem    = (ctx.mem is not None)
        typ_   =  ctx.t.ast

        decls = []
        for d in ctx.decls:
            name    = d.name.text
            initVal = d.val.ast if d.val is not None else None
            stmt = ast.g_DeclStmt(ns_pub,ns_pri, prefix,mem,typ_, name,initVal)
            decls.append(stmt)

        assert len(decls) >= 1
        ctx.ast_arr = decls


    enterStmt_Connection = default_enter_stmt
    def exitStmt_Connection(self, ctx):
        assert len(ctx.lhs) >= 1
        if len(ctx.lhs) > 1:
            assert False, "TODO-implement-chain-assignment"    # maybe generate n-1 connection statements in a block?

        lineInfo = build_line_range(ctx)
        ctx.ast = ast.g_ConnStmt(lineInfo, ctx.lhs[0].ast, ctx.rhs.ast)

        # if() statements that wrap this statement will want to know this
        ctx.uncovered_else = False


    enterStmt_If = default_enter_stmt
    def exitStmt_If(self, ctx):
        if ctx.static != None:
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
            TODO()

        ctx.uncovered_else = (ctx.fals_ is not None)
        if not ctx.uncovered_else and ctx.tru_.uncovered_else:
            TODO()    # report syntax error

        cond  = ctx.cond.ast
        tru_  = ctx.tru_ .ast if ctx.tru_  is not None else None
        fals_ = ctx.fals_.ast if ctx.fals_ is not None else None

        lineInfo_whole = build_line_range(ctx)
        lineInfo_else  = build_line_info (ctx.els_) if ctx.fals_ is not None else None

        ctx.ast = ast.g_RuntimeIfStmt(lineInfo_whole, lineInfo_else,
                                      cond, tru_, fals_)


    enterStmt_Assert = default_enter_stmt
    def exitStmt_Assert(self, ctx):
        lineInfo = build_line_range(ctx)
        ctx.ast = ast.g_AssertStmt(lineInfo, ctx.exp_.ast)

        # if() statements that wrap this statement will want to know this
        ctx.uncovered_else = False


    def enterStmt_For(self, ctx):
        # see the long comment in default_enter_stmt() to understand the basics
        # here.  But then come back, and read about generics.
        #
        # A for() statement is implemented as a generic Part declaration, which
        # is then instantiated many times - once for each pass of the loop.
        # This makes it easy to handle the iterator variable, since it is
        # simply the one and only parameter of the generic type.
        #
        # But generic types are nastier than I realized at first, because all
        # of the expressions inside them have parameters (specifically, size
        # offset, but maybe more), which can vary from instantiation to
        # instantiation.
        #
        # The only solution, really, is to DUPLICATE THE AST for each
        # instantiation.  And each duplicate will need a different set of
        # name scopes, becuase at least the iterator variable will be different
        # in each expression.  But the NameScope tree is built early, in the
        # enter() functions - even though we won't be able to instantiate many
        # parts until the calc_sizes() phase!!!
        #
        # My solution is to create a *DUMMY NAMESCOPE* here.  A NameScope will
        # have a parent which is a *string* instead of a real NameScope; when
        # we instantiate the generic, we will, in each duplicate, replace the
        # string with a true parent object, which has as its own parent the
        # private name scope that enclosed the for() loop, and which has a
        # single name of its own: the value of the iterator variable.  As we
        # recurse through the AST, duplicating it, we will replace each 
TODO: we can use a class, with stub functions, and handle this in the ForStmt code.  And perhaps we can *defer* delivering any NameScope objects until later?  Maybe this becomes a post-processing recursion step (like deliver_if_condition()) instead of something that we figure out in the enter functions?  Time for a branch, I think!

        ctx.pub_nameScope = None
        ctx.pri_nameScope = ctx.parentCtx.pri_nameScope

    def exitStmt_For(self, ctx):
        ns_pri = ctx.pri_nameScope

        var   = ctx.var.text
        start = ctx.start.ast
        end   = ctx.end  .ast
        body  = ctx.body .ast

        tuple_name = ctx.tuple_name.text if ctx.tuple_name is not None else None

        ctx.ast = ast.g_ForStmt(ns_pri, var, start,end, body, tuple_name)


    def default_enter_expr(self, ctx):
        ctx.pri_nameScope = ctx.parentCtx.pri_nameScope


    enterExpr = default_enter_expr
    def exitExpr(self, ctx):
        assert ctx.left is not None
        if   len(ctx.right) == 0:
            ctx.ast = ctx.left.ast
        elif len(ctx.right) == 1:
            lineInfo = build_line_info(ctx.op)
            ctx.ast = ast.g_BinaryExpr(lineInfo, ctx.left.ast, ctx.op.text, ctx.right[0].ast)
        else:
            TODO()    # implement me, chain of more operations


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


    enterExpr7 = default_enter_expr
    def exitExpr7(self, ctx):
        assert (ctx.base is not None) != (ctx.right is not None)

        if ctx.base is not None:
            ctx.ast = ctx.base.ast

        else:
            op = ctx.op.text
            assert op in ["!", "-"]
            lineInfo = build_line_info(ctx.op)
            ctx.ast = ast.g_UnaryExpr(lineInfo, op, ctx.right.ast)


    enterExpr8 = default_enter_expr
    def exitExpr8(self, ctx):
        assert (ctx.base is not None) != (ctx.left is not None)

        if ctx.base is not None:
            ctx.ast = ctx.base.ast

        elif ctx.field is not None:
            ctx.ast = ast.g_DotExpr(ctx.left.ast, ctx.field.text)

        elif ctx.a is not None and ctx.colon is None:
            # either declaration of an array type, if the underlying expression
            # is a type, or indexing into an array, if the underlying
            # expression is a runtime value.
            #
            # We must defer the resolution of what it is until later, when we
            # have resolved the names; then we will replace this object with
            # one of the proper type.
            ctx.ast = ast.g_Unresolved_Single_Index_Expr(ctx.pri_nameScope, ctx.left.ast, ctx.a.ast)

        elif ctx.a is not None and ctx.colon is not None:
            # slice of a runtime value, which goes to the end of the array
            ctx.ast = ast.g_ArraySlice(ctx.left.ast,
                                       ctx.a.ast,
                                       None)

        elif ctx.a is None and ctx.colon is not None and ctx.b is not None:
            # slice of a runtime value, which starts at the beginning of the array
            ctx.ast = ast.g_ArraySlice(ctx.left.ast,
                                       ast.g_NumExpr("0"),
                                       ctx.b.ast)

        elif ctx.a is not None and ctx.colon is not None and ctx.b is not None:
            # slice of a runtime value
            ctx.ast = ast.g_ArraySlice(ctx.left.ast,
                                       ctx.a.ast,
                                       ctx.b.ast)

        else:
            assert False, "Unrecognized expression"


    enterExpr9 = default_enter_expr
    def exitExpr9(self, ctx):
        if ctx.subexpr is not None:
            ctx.ast = ctx.subexpr.ast

        elif ctx.name is not None:
            ctx.ast = ast.g_IdentExpr(ctx.pri_nameScope, ctx.name.text)
        elif ctx.num is not None:
            ctx.ast = ast.g_NumExpr(ctx.num.text)

        elif ctx.children[0].getText() == "true":
            ctx.ast = TODO()
        elif ctx.children[0].getText() == "false":
            ctx.ast = TODO()

        elif ctx.children[0].getText() == "bit":
            ctx.ast = ast_expr_metatypes.plugType_bit
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

