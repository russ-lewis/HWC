#include <stdio.h>
#include <assert.h>
#include <stdlib.h>

#include "phase20.h"

#include "expr.h"



/*
 * Performs phase 20 on the given expression.
 *
 * To be specific, tries to evaluate an expression to a more specific value.
 *
 * Currently, this code is *only* called from findDeclSize(), to get the size
 * of an array declaration.  So we currently *ONLY* evaluate integer
 * expressions, and not even math involving those expressions.  We'll add
 * more support over time as needed.
 * 
 * Returns how many errors were found during this function.
 *
 * NOTE: Unlike the plugtype and part code for semPhase_*(), this does *NOT*
 *       have any phase level checking or recursion; it just gets called once,
 *       right where it's needed.  Since expressions never show up twice,
 *       multiple-evaluation isn't a worry.
 */
int semPhase20_expr(HWC_Expr *expr)
{
	switch (expr->mode)
	{
	default:
		assert(0);    // unrecognized mode, this is a compiler bug

	case EXPR_IDENT:
	case EXPR_BOOL:
	case EXPR_TWOOP:
	case EXPR_NOT:
	case EXPR_BITNOT:
	case EXPR_DOT:
	case EXPR_ARR:
	case EXPR_ARR_SLICE:
		assert(0);    // valid, but unimplemented.  TODO!

	case EXPR_NUM:
		if (strlen(expr->name) > 9)
			assert(0);    // add support for longer integers

		if (expr->name[0] == '0' && expr->name[1] == 'x')
			assert(0);    // TODO: add support for hex

		if (expr->name[0] == '0' && expr->name[1] == 'b')
			assert(0);    // TODO: add support for binary

		expr->val.type   = EXPR_VALTYPE_INT;
		expr->val.intVal = atoi(expr->name);
		break;
	}

	return 0;
}


