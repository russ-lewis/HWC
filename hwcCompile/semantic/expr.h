#ifndef __SEMANTIC_EXPR_H__INCLUDED__
#define __SEMANTIC_EXPR_H__INCLUDED__


#include "plug.h"
#include "partinstance.h"
#include "decl.h"
#include "names.h"

#include <pt/expr.h>    // we'll re-use the modes from the parser, but then
                        // add some more

enum {
	EXPR_PLUG = EXPR__LAST_PARSER_MODE+1,
	EXPR_SUBCOMPONENT,
};

typedef struct HWC_Decl HWC_Decl;

typedef struct HWC_Expr HWC_Expr;
struct HWC_Expr
{
	int mode;

	/* EXPR_PLUG */
	HWC_Plug *plug;

	/* EXPR_SUBCOMPONENT */
	HWC_PartInstance *subcomponent;

	/* EXPR_IDENT  - uses name                     */
	/* EXPR_NUM    - uses name                     */
	/* EXPR_BOOL   - uses       value              */
	/* EXPR_TWOOP  - uses       value, exprA,exprB */
	/* EXPR_NOT    - uses              exprA       */
   /* EXPR_BITNOT - uses              exprA       */
	/* EXPR_DOT    - uses              exprA,exprB */
	/* EXPR_ARR    - uses              exprA,exprB */
	/* EXPR_PAREN  - uses              exprA       */

	char     *name; // Rewritten in Phase 20 to create decl
	HWC_Decl *decl; // Points to decl that declared this expr
	int       value;
	HWC_Expr *exprA, *exprB;

	// Offset into current Part
	// For EXPR_NOT, BITNOT, and TWOOP add 1 bit for output of condition
	int offset;
};

void convertPTexprIntoHWCexpr(PT_expr *input, HWC_Expr *output);
int checkExprName(HWC_Expr *, HWC_NameScope *);

#endif

