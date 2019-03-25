#ifndef __SEMANTIC_EXPR_H__INCLUDED__
#define __SEMANTIC_EXPR_H__INCLUDED__


#include "semantic/plug.h"
#include "semantic/partinstance.h"
#include "semantic/decl.h"
#include "semantic/names.h"

#include "wiring/fileRange.h"
#include "semantic/sizes.h"

#include "pt/expr.h"


enum {
	EXPR_VALTYPE_INVALID = 0,  // init state

	EXPR_VALTYPE_INT = 401,
	EXPR_VALTYPE_BOOL,

	// this is a runtime field; it has a plugtype and position
	// in the virtual space.
	EXPR_VALTYPE_PLUG,

	// this is a reference to a particular subcomponent; it is almost
	// always the base of a DOT expression, which will return a PLUG
	EXPR_VALTYPE_SUBCOMP,

	// these are expressions which are references to a specific type.
	// Currently, we don't support this, but we expect to eventually,
	// so that we can have typeof() and sizeof() expressions, as well
	// as casts.
	EXPR_VALTYPE_PLUGTYPE,
	EXPR_VALTYPE_PARTTYPE,
};


typedef struct HWC_Decl HWC_Decl;

typedef struct HWC_Expr HWC_Expr;
struct HWC_Expr
{
	FileRange fr;
	HWC_Sizes sizes,offsets;    // see long description in semantic/sizes.h

	/* NOTE: the 'sizes','offsets' fields above talk about *consumption*
	 *       of resources.  This is *NOT* the same as the size of the
	 *       retval.
	 *
	 *       For example, consider a huge, complex network of binary
	 *       operators; they consume many,many bits in the virtual space,
	 *       to store the various temporaries (not to mention many logical
	 *       operators).  But they might only produce a *single* bit of
	 *       returned data when evaluated.
	 *
	 *       This field stores that information.
	 */
	int retvalSize;

	/* similarly, the retval has a *position* which is distinct from "the
	 * position in the bit space where the next sub-component will
	 * allocate its output;" in fact, for some expressions (such as
	 * IDENT), this may be entirely dependent on a decl in a *totally
	 * different* part of the virtual space.
	 */
	int retvalOffset;


	int mode;

#if 0
	/* EXPR_PLUG */
	HWC_Plug *plug;

	/* EXPR_SUBCOMPONENT */
	HWC_PartInstance *subcomponent;
#endif

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
	int       twoOp;
	HWC_Expr *exprA, *exprB;

	char *field;

	/* this stores information about the evaluated type and value of the
	 * expression.  It is filled in by semPhase20_expr().
	 */
	struct {
		/* use EXPR_VALTYPE_* (see above) */
		int type;

		/* for most types, set to 1 if the value types below
		 * are valid.  However, PLUG is special and has three
		 * positive values:
		 *    1 - the plugtype is known (including the array
		 *        size expression being filled in), but the total
		 *        size and position are not yet set (perhaps
		 *        because the array expression has not yet evaluated
		 *        to an integer).
		 *    2 - same as 1, but now the total size is also known
		 *    3 - all fields are known (that is, same as 2, plus position)
		 */
		int ready;

		union {
			int  intVal;
			int boolVal;
		};
	} val;
};



/* TODO: replace this with semPhase10_*() */
void convertPTexprIntoHWCexpr(PT_expr *input, HWC_Expr **output);


/* can be called in any phase *after* semPhase20_expr() has been
 * called on the expression.  Attempts to figure out the value of
 * the expression.
 *
 * If it fails but force=0, then it ends silently (and returns 0);
 * if it fails but force=1 - or if their is some syntax error
 * detected - then it will print out a description of the problem
 * and return nonzero.
 */
int expr_evaluate(HWC_Expr*, int force);


/* debug */
void expr_dump(HWC_Expr*, int prefixLen);

#endif

