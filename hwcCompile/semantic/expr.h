#ifndef __SEMANTIC_EXPR_H__INCLUDED__
#define __SEMANTIC_EXPR_H__INCLUDED__


#include "plug.h"
#include "partinstance.h"
#include "decl.h"
#include "names.h"

#include "wiring/fileRange.h"
#include "semantic/sizes.h"

#include <pt/expr.h>    // we'll re-use the modes from the parser, but then
                        // add some more

enum {
	EXPR_PLUG = EXPR__LAST_PARSER_MODE+1,
	EXPR_SUBCOMPONENT,
};

enum {
	EXPR_VALTYPE_INT = 401,
	EXPR_VALTYPE_BOOL,
};


typedef struct HWC_Decl HWC_Decl;

typedef struct HWC_Expr HWC_Expr;
struct HWC_Expr
{
	FileRange fr;
	HWC_Sizes sizes,offsets;    // see long description in semantic/sizes.h

	int mode;

	/* EXPR_PLUG */
	HWC_Plug *plug;

	/* EXPR_SUBCOMPONENT */
	HWC_PartInstance *subcomponent;

	/* EXPR_IDENT     - uses name                     */
	/* EXPR_NUM       - uses name                     */
	/* EXPR_BOOL      - uses       value              */
	/* EXPR_TWOOP     - uses       value, exprA,exprB */
	/* EXPR_NOT       - uses              exprA       */
	/* EXPR_BITNOT    - uses              exprA       */
	/* EXPR_DOT       - uses              exprA,field */
	/* EXPR_ARR       - uses              exprA,exprB */
	/* EXPR_ARR_SLICE - uses              exprA,exprB */
	/* EXPR_PAREN     - uses              exprA       */

	char     *name; // Rewritten in Phase 20 to create decl
	HWC_Decl *decl; // Points to decl that declared this expr
	int       value; // TWOOP uses value to store what type of TWOOP it is. See ../pt/expr.h
	HWC_Expr *exprA, *exprB;

	char *field;

	/* this stores information about the evaluated type and value of the
	 * expression.  It is filled in by semPhase20_expr().
	 */
	struct {
		/* use EXPR_VALTYPE_* (see above) */
		int type;

		union {
			int  intVal;
			int boolVal;
		};
	} val;
};

void convertPTexprIntoHWCexpr(PT_expr *input, HWC_Expr **output);
int checkExprName(HWC_Expr *, HWC_NameScope *);
int findExprSize(HWC_Expr *, int *logic);

#endif

