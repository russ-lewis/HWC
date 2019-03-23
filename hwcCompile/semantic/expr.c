#include <stdio.h>
#include <malloc.h>
#include <assert.h>

#include "expr.h"

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
				retval++;
			}
			// If the name doesn't correspond to a declaration.
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
		case(EXPR_BOOL):
			// TODO: NOP?
			assert(0);
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
		case(EXPR_DOT):
			retval += checkExprName(currExpr->exprA, currScope);
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
	currExpr->retvalBits = -1;

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
		sizes_set_zero(&currExpr->sizes);

// TODO: assert that the decl *MUST* have already run phase 30
		currExpr->retvalBits = currExpr->decl->sizes.bits;
		if (currExpr->decl->isMem)
			currExpr->retvalBits /= 2;
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
		semPhase30_expr(currExpr->exprA);

		// sanity check that the expression has nonzero size.  Copy
		// that into our expression.
		assert(currExpr->exprA->retvalBits > 0);
		currExpr->retvalBits = currExpr->exprA->retvalBits;

		// first, copy in the sizes from the underlying expression,
		// since it might include many logical operators and bits used
		// for the temporaries
		sizes_copy(&currExpr->sizes, &currExpr->exprA->sizes);

		// then, add one additional logical operator for the NOT, and
		// space for it to write out its results.
		currExpr->sizes.logicOps++;
		currExpr->sizes.bits += currExpr->exprA->retvalBits;
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



int semPhase35_expr(HWC_Expr *currExpr)
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
		sizes_copy(&currExpr->exprA->offsets, &currExpr->offsets);
		semPhase35_expr(currExpr->exprA);
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

