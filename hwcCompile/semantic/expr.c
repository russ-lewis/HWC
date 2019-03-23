#include <stdio.h>
#include <malloc.h>
#include <assert.h>

#include "semantic/expr.h"

#include "semantic/part.h"
#include "semantic/plugtype.h"

/*
Converts PT exprs into HWC exprs. What a good function name.

 - *input is a pointer to the PT_expr to convert
 - **output_out is a non-initialized HWC_Expr that this function will fill in

Returns nothing, since all meaningful work is done upon **output_out
*/
void convertPTexprIntoHWCexpr(PT_expr *input, HWC_Expr **output_out)
{
	assert(input != NULL);

	HWC_Expr *output = malloc(sizeof(HWC_Expr));
	if(output == NULL)
	{
		assert(0); // TODO: Better error message?
	}
	*output_out = output;

	fr_copy   (&output->fr, &input->fr);
	sizes_init(&output->sizes);
	sizes_init(&output->offsets);
	output->retvalSize = -1;
	output->retvalOffset = -1;
 
	output->mode = input->mode;
	switch(input->mode)
	{
		//TODO: Error message?
		default:
			break;
		case(EXPR_PLUG):
			// TODO
			fprintf(stderr, "Still have not implemented conversion of PTexpr into EXPR_PLUG\n");
			// HWC_Plug *plug;
			break;
		case(EXPR_SUBCOMPONENT):
			// TODO
			fprintf(stderr, "Still have not implemented conversion of PTexpr into EXPR_SUBCOMPONENT\n");
			// HWC_PartInstance *subcomponent;
			break;
		case(EXPR_IDENT):
			output->name  = input->name;
			break;
		case(EXPR_NUM):
			output->name  = input->num;
			break;
		case(EXPR_BOOL):
			output->value = input->value;
			break;
		case(EXPR_TWOOP):
			output->value = input->opMode;
			convertPTexprIntoHWCexpr(input->lHand, &output->exprA);
			convertPTexprIntoHWCexpr(input->rHand, &output->exprB);
			break;
		case(EXPR_BITNOT):
			convertPTexprIntoHWCexpr(input->notExpr, &output->exprA);
			break;
		case(EXPR_NOT):
			convertPTexprIntoHWCexpr(input->notExpr, &output->exprA);
			break;
		case(EXPR_DOT):
			convertPTexprIntoHWCexpr(input->dotExpr, &output->exprA);
			output->field = input->field;
			break;
		case(EXPR_ARR):
			convertPTexprIntoHWCexpr(input->arrayExpr, &output->exprA);
			convertPTexprIntoHWCexpr(input->indexExpr, &output->exprB);
			break;
	}
}

/*
Ensures that the names used within the given expression are valid within the expression's namescope.

 - *currExpr is the expression to check
 - *currScope is the relevant namescope for the expr

Returns 0 if no errors, >= 1 if errors to indicate how many errors.
*/
int checkExprName(HWC_Expr *currExpr, HWC_NameScope *currScope)
{
	int retval = 0;
	HWC_Nameable *currName;

	switch(currExpr->mode)
	{
		default:
			break;
		case(EXPR_PLUG):
			// TODO: Need conversion from PT to HWC before doing this.
			fprintf(stderr, "Checking name of plug has not be implemented yet.\n");
			break;
		case(EXPR_SUBCOMPONENT):
			// TODO: Need conversion from PT to HWC before doing this.
			fprintf(stderr, "Checking name of subcomponent has not be implemented yet.\n");
			break;

		case(EXPR_NUM):
			break;    // nothing to do!

		case(EXPR_IDENT):
			currName = nameScope_search(currScope, currExpr->name);
			// TODO: Error messages
			// If the name could not be found.
			if(currName == NULL)
			{
				fprintf(stderr, "%s:%d:%d: Symbol '%s' does not exist.\n",
				        currExpr->fr.filename,
				        currExpr->fr.s.l, currExpr->fr.s.c,
				        currExpr->name);
				return 1;
			}
			// If the name doesn't correspond to a declaration.
			else if(currName->decl == NULL)
			{
				fprintf(stderr, "%s:%d:%d: Symbol '%s' has a NULL 'decl' pointer.  TODO: what does this mean?\n",
				        currExpr->fr.filename,
				        currExpr->fr.s.l, currExpr->fr.s.c,
				        currExpr->name);
				return 1;
			}

			// save the decl for later.  We'll use this, later, to
			// figure out the exact size and position of this
			// expression's retval.
			currExpr->decl = currName->decl;
			break;

		case EXPR_BOOL:
			break;

		case(EXPR_TWOOP):
			// TODO: Anything to do with "currExpr->value" here?
			retval += checkExprName(currExpr->exprA, currScope);
			retval += checkExprName(currExpr->exprB, currScope);
			break;
		case(EXPR_BITNOT):
			retval += checkExprName(currExpr->exprA, currScope);
			break;
		case(EXPR_NOT):
			retval += checkExprName(currExpr->exprA, currScope);
			break;

		case EXPR_DOT:
			retval += checkExprName(currExpr->exprA, currScope);

			// look up the .field name in the *public* names of
			// the base expression.

			// TODO: refactor the expression to be more general;
			//       we should support part instances and plugs
			//       as value types, and then use those as the
			//       base of this lookup.

			assert(currExpr->exprA->decl != NULL);

			if (currExpr->exprA->decl->base_plugType != NULL)
				currScope = currExpr->exprA->decl->base_plugType->publicNames;
			else if (currExpr->exprA->decl->base_part != NULL)
				currScope = currExpr->exprA->decl->base_part->publicNames;
			else
				assert(0);   // should be impossible

			// now that we've found the right scope, perform the
			// lookup
			currName = nameScope_search(currScope, currExpr->field);

			// was the name not found?  Report that to the user.
			if(currName == NULL)
			{
				fprintf(stderr, "%s:%d:%d: Symbol '%s' does not exist.\n",
				        currExpr->fr.filename,
				        currExpr->fr.s.l, currExpr->fr.s.c,
				        currExpr->name);
				retval++;
			}
			// was the name valid, but not point to a declaration?  Is that even possible????
			else if(currName->decl == NULL)
			{
				fprintf(stderr, "%s:%d:%d: Symbol '%s' has a NULL 'decl' pointer.  TODO: what does this mean?\n",
				        currExpr->fr.filename,
				        currExpr->fr.s.l, currExpr->fr.s.c,
				        currExpr->name);
				retval++;
			}
			else
				currExpr->decl = currName->decl;
			break;

		case(EXPR_ARR):
			retval += checkExprName(currExpr->exprA, currScope);
			retval += checkExprName(currExpr->exprB, currScope);
			break;
	}

	return retval;
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

	case EXPR_PLUG:
		// TODO: Need conversion from PT to HWC before doing this.
		fprintf(stderr, "Checking size of plug has not be implemented yet.\n");
		retval = 1;
		break;

	case EXPR_SUBCOMPONENT:
		// TODO: Need conversion from PT to HWC before doing this.
		fprintf(stderr, "Checking size of subcomponent has not be implemented yet.\n");
		retval = 1;
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
		retval += semPhase30_expr(currExpr->exprA);
		retval += semPhase30_expr(currExpr->exprB);

		// the total size is the sizes of the two expressions, plus
		// the logical operator, plus space to store the result.
		sizes_add(&currExpr->sizes,
		          &currExpr->exprA->sizes, &currExpr->exprB->sizes);

		currExpr->sizes.logicOps++;

		switch(currExpr->value)
		{
		default:
			assert(0);   // TODO: implement the rest

		case OP_EQUALS:
			currExpr->sizes.bits++;
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

	case EXPR_PLUG:
		// TODO: Need conversion from PT to HWC before doing this.
		fprintf(stderr, "Checking size of plug has not be implemented yet.\n");
		retval = 1;
		break;

	case EXPR_SUBCOMPONENT:
		// TODO: Need conversion from PT to HWC before doing this.
		fprintf(stderr, "Checking size of subcomponent has not be implemented yet.\n");
		retval = 1;
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

		sizes_add(&currExpr->exprA->offsets,
		          &currExpr->offsets, &currExpr->sizes);
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

