#include <stdio.h>
#include <malloc.h>
#include <stdlib.h>
#include <assert.h>

#include "semantic/expr.h"

#include "semantic/part.h"
#include "semantic/plugtype.h"



/* internal helper functions.  We offload the more complex parts of each
 * function to helpers, to keep the switch/case statements small.
 *
 * In each case, it returns the same format as the caller, so, in many
 * cases, tail recursion works well.
 */
static int semPhase20_expr_twoOpValType(HWC_Expr *expr);



/*
 * phase10_expr() - See phase10.h
 *
 * Converts a PT expression into an HWC expression.  Returns the
 * newly-malloc'ed expression, or NULL on error.  In the error case, this
 * function will print out an error message; the caller should not print
 * out anything.
 */
HWC_Expr *phase10_expr(PT_expr *input)
{
	assert(input != NULL);

	HWC_Expr *retval = malloc(sizeof(HWC_Expr));
	if (retval == NULL)
		assert(0); // TODO: Better error message?
	memset(retval, 0, sizeof(*retval));

	fr_copy   (&retval->fr, &input->fr);
	sizes_init(&retval->sizes);
	sizes_init(&retval->offsets);
	retval->retvalSize = -1;
	retval->retvalOffset = -1;
 
	retval->mode = input->mode;
	switch(input->mode)
	{
	default:
		printf("%d\n", input->mode);   fflush(NULL);
		assert(0);    // invalid expression type

	case EXPR_IDENT:
		retval->name = input->name;
		break;

	case EXPR_NUM:
		retval->val.type = EXPR_VALTYPE_INT;

		if (input->num[0] == '0' && input->num[1] == 'x')
			assert(0);    // TODO: handle hex
		else
			retval->val.intVal = atoi(input->num);

		retval->val.ready = 1;
		break;

	case EXPR_BOOL:
		retval->val.type = EXPR_VALTYPE_BOOL;
		retval->val.boolVal = input->value;
		retval->val.ready = 1;
		break;

	case EXPR_TWOOP:
		retval->twoOp = input->opMode;

		retval->exprA = phase10_expr(input->lHand);
		retval->exprB = phase10_expr(input->rHand);

		if (retval->exprA == NULL || retval->exprB == NULL)
		{
			free(retval->exprA);
			free(retval->exprB);
			free(retval);
			return NULL;
		}
		break;

	case EXPR_BITNOT:
	case EXPR_NOT:
		retval->exprA = phase10_expr(input->notExpr);
		if (retval->exprA == NULL)
		{
			free(retval);
			return NULL;
		}
		break;

	case EXPR_DOT:
		retval->exprA = phase10_expr(input->dotExpr);
		if (retval->exprA == NULL)
		{
			free(retval);
			return NULL;
		}

		retval->field = input->field;
		break;

	case EXPR_ARR:
		retval->exprA = phase10_expr(input->arrayExpr);
		retval->exprB = phase10_expr(input->indexExpr);

		if (retval->exprA == NULL || retval->exprB == NULL)
		{
			free(retval->exprA);
			free(retval->exprB);
			free(retval);
			return NULL;
		}
		break;

	case EXPR_ARR_SLICE:
		retval->exprA = phase10_expr(input->arrayExpr);

		if (input->indexExpr1 == NULL)
			retval->exprB = NULL;
		else
			retval->exprB = phase10_expr(input->indexExpr1);

		if (input->indexExpr2 == NULL)
			retval->exprC = NULL;
		else
			retval->exprC = phase10_expr(input->indexExpr2);

		if ( retval->exprA == NULL ||
		    (retval->exprB == NULL && input->indexExpr1 != NULL) ||
		    (retval->exprC == NULL && input->indexExpr2 != NULL))
		{
			free(retval->exprA);
			free(retval->exprB);
			free(retval->exprC);
			free(retval);
			return NULL;
		}
		break;

	case EXPR_BIT_TYPE:
		retval->val.type = EXPR_VALTYPE_PLUGTYPE;
		retval->val.plugtype.base   = &BitType;
		retval->val.plugtype.arrLen =  NULL;
		retval->val.ready = 1;
		break;
	}

	return retval;
}



/*
 * Ensures that the names used within the given expression are valid within
 * the expression's namescope.  We will then also set the 'type' of each
 * expression as we examine it.  In some cases, we may know the value as
 * well already; on other cases, we won't know it until later.
 *     - expr is the expression to check
 *     - scope is the namescope of the statement where the expr is used
 *
 * Returns 0 if no errors, >= 1 if errors to indicate how many errors.
 */
int semPhase20_expr(HWC_Expr *expr, HWC_NameScope *scope)
{
	int retval = 0;
	HWC_Nameable *currName;

	switch(expr->mode)
	{
	default:
		assert(0);   // invalid expression type

	case EXPR_NUM:
	case EXPR_BOOL:
		// type and value are set in phase 10, copied/interpreted
		// directly from the parse tree.
		assert(expr->val.ready);
		break;

	case EXPR_IDENT:
		currName = nameScope_search(scope, expr->name);

		if(currName == NULL)
		{
			fprintf(stderr, "%s:%d:%d: Symbol '%s' does not exist.\n",
			        expr->fr.filename,
			        expr->fr.s.l, expr->fr.s.c,
			        expr->name);
			return 1;
		}
		else if(currName->decl == NULL)
		{
assert(0);   // TODO: is this even possible?  explain, or remove
			fprintf(stderr, "%s:%d:%d: Symbol '%s' has a NULL 'decl' pointer.  TODO: what does this mean?\n",
			        expr->fr.filename,
			        expr->fr.s.l, expr->fr.s.c,
			        expr->name);
			return 1;
		}

		if (currName->decl->base_plugType != NULL)
		{
			expr->val.type = EXPR_VALTYPE_PLUG;
			expr->val.plug.base   = currName->decl->base_plugType;
			expr->val.plug.arrLen = currName->decl->expr;
			expr->val.ready = 1;
		}
		else if (currName->decl->base_part != NULL)
		{
assert(0);   // TODO: this is a subcomp, right?
		}
		else
			assert(0);   // TODO: is this even possible?

		// save the decl for later.  We'll use this, later, to
		// figure out the exact size and position of this
		// expression's retval.
		expr->decl = currName->decl;
		break;

	case EXPR_TWOOP:
		retval  = semPhase20_expr(expr->exprA, scope);
		retval += semPhase20_expr(expr->exprB, scope);
		if (retval != 0)
			return retval;

		return semPhase20_expr_twoOpValType(expr);
		break;

	case EXPR_BITNOT:
		retval = semPhase20_expr(expr->exprA, scope);
		if (retval != 0)
			return retval;

		if (expr->exprA->val.type == EXPR_VALTYPE_PLUG)
		{
			expr->val.type = EXPR_VALTYPE_PLUG;
			assert(0);   // TODO: copy over the plugtype info
		}
		else if (expr->exprA->val.type == EXPR_VALTYPE_BOOL)
		{
			expr->val.type = EXPR_VALTYPE_BOOL;
			assert(0);   // TODO: set value
		}
		else
		{
			fprintf(stderr, "%s:%d:%d: Bitwise negation is only valid for runtime expressions and compile-time booleans.\n",
			        expr->exprA->fr.filename,
			        expr->exprA->fr.s.l, expr->exprA->fr.s.c);
			return 1;
		}
		break;

	case EXPR_NOT:
		retval = semPhase20_expr(expr->exprA, scope);
		if (retval != 0)
			return retval;

		if (expr->exprA->val.type == EXPR_VALTYPE_BOOL)
		{
			/* boolean */
			expr->val.type = EXPR_VALTYPE_BOOL;
			assert(0);   // TODO: set value
		}
		else if(expr->exprA->val.type == EXPR_VALTYPE_INT)
		{
			/* integer, check to see if either 0 or 1 */
			expr->val.type = EXPR_VALTYPE_BOOL;
assert(0);   // only allow 0,1.  Print syntax error otherwise.  Report the retval as a boolean.
		}
		else if (expr->exprA->val.type == EXPR_VALTYPE_PLUG &&
		         expr->exprA->val.ready >= 1 &&
		         expr->exprA->val.plug.base   == &BitType   &&
		         expr->exprA->val.plug.arrLen ==  NULL)
		{
			/* single bit */
			expr->val.type = EXPR_VALTYPE_PLUG;
			expr->val.plug.base   = &BitType;
			expr->val.plug.arrLen =  NULL;
			expr->val.ready = 1;
		}
		else if (expr->exprA->val.type == EXPR_VALTYPE_PLUG &&
		         0 /* TODO: is bit[1] */)
		{
			expr->val.type = EXPR_VALTYPE_PLUG;
assert(0);   // TODO: set the valtype to (simple) bit.  Same as previous
		}
		else
		{
			fprintf(stderr, "%s:%d:%d: Logical negation is only valid for expressions that can be intepreted as true or false: compile-time booleans; compile-time integers 0,1; runtime 'bit'; runtime 'bit[1]'.\n",
			        expr->exprA->fr.filename,
			        expr->exprA->fr.s.l, expr->exprA->fr.s.c);
			return 1;
		}
		break;

	case EXPR_DOT:
		retval += semPhase20_expr(expr->exprA, scope);

		// look up the .field name in the *public* names of
		// the base expression.

		// TODO: refactor the expression to be more general;
		//       we should support part instances and plugs
		//       as value types, and then use those as the
		//       base of this lookup.

		assert(expr->exprA->decl != NULL);

		if (expr->exprA->decl->base_plugType != NULL)
			scope = expr->exprA->decl->base_plugType->publicNames;
		else if (expr->exprA->decl->base_part != NULL)
			scope = expr->exprA->decl->base_part->publicNames;
		else
			assert(0);   // should be impossible

		// now that we've found the right scope, perform the
		// lookup
		currName = nameScope_search(scope, expr->field);

		// was the name not found?  Report that to the user.
		if(currName == NULL)
		{
			fprintf(stderr, "%s:%d:%d: Symbol '%s' does not exist.\n",
			        expr->fr.filename,
			        expr->fr.s.l, expr->fr.s.c,
			        expr->name);
			retval++;
		}
		// was the name valid, but not point to a declaration?  Is that even possible????
		else if(currName->decl == NULL)
		{
			fprintf(stderr, "%s:%d:%d: Symbol '%s' has a NULL 'decl' pointer.  TODO: what does this mean?\n",
			        expr->fr.filename,
			        expr->fr.s.l, expr->fr.s.c,
			        expr->name);
			retval++;
		}
		else
			expr->decl = currName->decl;
		break;

	case EXPR_ARR:
		retval += semPhase20_expr(expr->exprA, scope);
		retval += semPhase20_expr(expr->exprB, scope);
		break;

	case EXPR_ARR_SLICE:
		retval += semPhase20_expr(expr->exprA, scope);
		if (expr->exprB != NULL)
			retval += semPhase20_expr(expr->exprB, scope);
		if (expr->exprC != NULL)
			retval += semPhase20_expr(expr->exprC, scope);
		break;
	}

	return retval;
}

static int semPhase20_expr_twoOpValType(HWC_Expr *expr)
{
assert(0);   // TODO
}



int semPhase30_expr(HWC_Expr *currExpr)
{
	assert(currExpr != NULL);

	int retval = 0;

	// these defaults are overridden as necessary, below
	sizes_set_zero(&currExpr->sizes);

	switch(currExpr->mode)
	{
	default:
		break;

	case EXPR_IDENT:
		// an IDENT expression doesn't consume any new wiring diagram
		// components - although it will *return* something of
		// nonzero size.
		sizes_set_zero(&currExpr->sizes);

// TODO: assert that the decl *MUST* have already run phase 30

		currExpr->retvalSize = currExpr->decl->sizes.bits;
		if (currExpr->decl->isMem)
			currExpr->retvalSize /= 2;
		break;

	case EXPR_NUM:
	case EXPR_BOOL:
		break;

	case EXPR_TWOOP:
		/* we should have determined the types (though not evaluated
		 * all of the values) in phase 20.
		 */
		assert(currExpr->exprA->val.type != EXPR_VALTYPE_INVALID);
		assert(currExpr->exprB->val.type != EXPR_VALTYPE_INVALID);

		/* do phase 30 work (figuring out the sizes of the
		 * sub-expressions.  This involves two different-but-related
		 * pieces:
		 *   - Figure out the resources consumed, and store them in
		 *     the 'sizes' struct
		 *   - Figure out the size of the *retval* for all runtime
		 *     expressions.  (The offset - that is, the position in
		 *     the virtual space - is determined in phase 35.)
		 */
		retval += semPhase30_expr(currExpr->exprA);
		retval += semPhase30_expr(currExpr->exprB);

		// the total size is the sizes of the two expressions, plus
		// the logical operator, plus space to store the result.
		// We'll initialize the size of our big expression to be the
		// sum of the sub-epressions, and then check the operator to
		// figure out what additional elements are required.
		sizes_add(&currExpr->sizes,
		          &currExpr->exprA->sizes, &currExpr->exprB->sizes);

		currExpr->sizes.logicOps++;

		switch(currExpr->twoOp)
		{
		default:
			printf("%d\n", currExpr->twoOp);  fflush(NULL);
			assert(0);   // TODO: implement the rest

		case OP_EQUALS:
		case OP_NEQUAL:
			// ==  !=
			//
			// When the inputs are integers (or booleans), our
			// result will be a (compile-time) bool, and the
			// expression won't consume any bits or other
			// resources.
			//
			// But, if we have a runtime expression on either side
			// (or both), then this will be evaluated at runtime;
			// it will need a single logcial operator, and a
			// single bit in the virtual space to hold the output.

			assert(currExpr->exprA->val.type == EXPR_VALTYPE_INT  ||
			       currExpr->exprA->val.type == EXPR_VALTYPE_BOOL ||
			       currExpr->exprA->val.type == EXPR_VALTYPE_PLUG);

			assert(currExpr->exprB->val.type == EXPR_VALTYPE_INT  ||
			       currExpr->exprB->val.type == EXPR_VALTYPE_BOOL ||
			       currExpr->exprB->val.type == EXPR_VALTYPE_PLUG);

			if ((currExpr->exprA->val.type == EXPR_VALTYPE_INT ||
			     currExpr->exprA->val.type == EXPR_VALTYPE_BOOL) &&
			    (currExpr->exprB->val.type == EXPR_VALTYPE_INT ||
			     currExpr->exprB->val.type == EXPR_VALTYPE_BOOL))
			{
				assert(currExpr->val.type == EXPR_VALTYPE_BOOL);
				/* no additional resources required */
			}
			else
			{
				/* this is a runtime expression.  The size is
				 * definitely 1 bit, no matter the input size.
				 */
				assert(currExpr->val.type == EXPR_VALTYPE_PLUG);
				currExpr->sizes.logicOps++;
				currExpr->sizes.bits++;
			}
			break;

		case OP_LESS:
		case OP_LESSEQ:
		case OP_GREATER:
		case OP_GREATEREQ:
		case OP_PLUS:
		case OP_MINUS:
		case OP_TIMES:
		case OP_DIVIDE:
		case OP_MODULO:
			// these operators can only take integer inputs.
			// They will not consume any resources; they will
			// be entirely evaluated (later).
			assert(currExpr->exprA->val.type == EXPR_VALTYPE_INT);
			assert(currExpr->exprB->val.type == EXPR_VALTYPE_INT);
			break;
		}
		break;

	case EXPR_BITNOT:
assert(0);
#if 0
		// TODO: Increment indexLogic here as well?
		retval += 1;
		retval += findExprSize(currExpr->exprA, currOffset, numLogic, 0);
#endif
		break;

	case EXPR_NOT:
		semPhase30_expr(currExpr->exprA);

		// sanity check that the expression has nonzero size.  Copy
		// that into our expression.
		assert(currExpr->exprA->retvalSize > 0);
		currExpr->retvalSize   = currExpr->exprA->retvalSize;

		// first, copy in the sizes from the underlying expression,
		// since it might include many logical operators and bits used
		// for the temporaries
		sizes_copy(&currExpr->sizes, &currExpr->exprA->sizes);

		// then, add one additional logical operator for the NOT, and
		// space for it to write out its results.
		currExpr->sizes.logicOps++;
		currExpr->sizes.bits += currExpr->exprA->retvalSize;
		break;

	case EXPR_DOT:
		retval += semPhase30_expr(currExpr->exprA);

		// the size (consumption) of the expression is the same as the
		// base expression size.  But the size (retval) of the
		// expression is found by doing a lookup into the names of
		// the base expression.
		sizes_copy(&currExpr->sizes, &currExpr->exprA->sizes);

		// the size of the new expression is determined by the type
		// associated with this decl.  The offset (figured out in
		// phase 35) is the offset of the base expression *plus* the
		// offset of this decl.
		assert(currExpr->exprA->retvalSize >= 0);
		currExpr->retvalSize = currExpr->exprA->retvalSize;

		break;

	case EXPR_ARR:
		retval += semPhase30_expr(currExpr->exprA);
		retval += semPhase30_expr(currExpr->exprB);

		sizes_add(&currExpr->sizes,
		          &currExpr->exprA->sizes, &currExpr->exprB->sizes);
		break;
	}

	return retval;
}



int semPhase35_expr(HWC_Expr *currExpr, int isLHS)
{
	int retval = 0;

	/* the caller has initialized the offset */
	assert(sizes_are_ready(&currExpr->offsets));

	switch(currExpr->mode)
	{
	default:
		break;

	case EXPR_IDENT:

// TODO: assert that the decl *MUST* have already run phase 35

		currExpr->retvalOffset = currExpr->decl->offsets.bits;

		if (currExpr->decl->isMem && isLHS)
			currExpr->retvalOffset += currExpr->retvalSize;
		break;

	case EXPR_NUM:
	case EXPR_BOOL:
		break;

	case EXPR_TWOOP:
assert(0);
#if 0
		// TODO: Anything to do with "currExpr->value" here?
		// TODO: numLogic might not want to be incremented for every value
		currExpr->offsets.bits = *numLogic;
		*numLogic += 1;
		retval += 1;
		retval += findExprSize(currExpr->exprA, currOffset, numLogic, 0);
		retval += findExprSize(currExpr->exprB, currOffset, numLogic, 0);
#endif
		break;

	case EXPR_BITNOT:
assert(0);
#if 0
		// TODO: Increment indexLogic here as well?
		retval += 1;
		retval += findExprSize(currExpr->exprA, currOffset, numLogic, 0);
#endif
		break;

	case EXPR_NOT:
		// At first, it seemed desirable to have the output from this
		// operator come *AFTER* (in the offsets) any components in the
		// sub-expression.  But then I realized that the wiring diagram
		// generator is going to use the offset (of this expression) as
		// the position of the output from this operator.
		//
		// We cannot advance our offest beyond our sub-expressions,
		// since our convention is that the offset of any object, plus
		// its size, is equal the offset of the next, and thus we have
		// to say that the output from this expression comes *before*
		// the offset of any subexpression.

		currExpr->retvalOffset = currExpr->offsets.bits;

		sizes_copy(&currExpr->exprA->offsets, &currExpr->offsets);
		currExpr->exprA->offsets.bits++;

		semPhase35_expr(currExpr->exprA, 0);
		break;

	case EXPR_DOT:
assert(0);
#if 0
		retval += findExprSize(currExpr->exprA, currOffset, numLogic, isLeft);
#endif
		break;

	case EXPR_ARR:
assert(0);
#if 0
		retval += findExprSize(currExpr->exprA, currOffset, numLogic, isLeft);
		retval += findExprSize(currExpr->exprB, currOffset, numLogic, 0);
#endif
		break;
	}

	return retval;
}

