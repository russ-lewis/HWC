#include <stdio.h>
#include <malloc.h>
#include <assert.h>

#include "expr.h"

// Assumes the second parameter is an HWC_Expr you want to convert into
// We do this to match convertPTstmtIntoHWCstmt
// Is this good design? Should the functions return HWC_Expr/HWC_Stmt and take an int* as a param if required?
void convertPTexprIntoHWCexpr(PT_expr *input, HWC_Expr *output)
{
	output = malloc(sizeof(HWC_Expr));
	if(output == NULL)
	{
		assert(0); // TODO: Better error message?
	}

	output->mode = input->mode;
	switch(input->mode)
	{
		//TODO: Error message?
		default:
			break;
		case(EXPR_PLUG):
			// TODO
			printf("Still have not implemented conversion of PTexpr into EXPR_PLUG\n");
			// HWC_Plug *plug;
			break;
		case(EXPR_SUBCOMPONENT):
			// TODO
			printf("Still have not implemented conversion of PTexpr into EXPR_SUBCOMPONENT\n");
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
			convertPTexprIntoHWCexpr(input->lHand, output->exprA);
			convertPTexprIntoHWCexpr(input->rHand, output->exprB);
			break;
		case(EXPR_BITNOT):
			convertPTexprIntoHWCexpr(input->notExpr, output->exprA);
			break;
		case(EXPR_NOT):
			convertPTexprIntoHWCexpr(input->notExpr, output->exprA);
			break;
		case(EXPR_DOT):
			convertPTexprIntoHWCexpr(input->dotExpr, output->exprA);
			convertPTexprIntoHWCexpr(input->field  , output->exprB);
			break;
		case(EXPR_ARR):
			convertPTexprIntoHWCexpr(input->arrayExpr, output->exprA);
			convertPTexprIntoHWCexpr(input->indexExpr, output->exprB);
			break;
		case(EXPR_PAREN):
			convertPTexprIntoHWCexpr(input->paren, output->exprA);
			break;
	}
}

/*
TODO: Header comment
Retval is 0 if no errors, 1 or more oetherwise
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
			printf("Checking name of plug has not be implemented yet.\n");
			break;
		case(EXPR_SUBCOMPONENT):
			// TODO: Need conversion from PT to HWC before doing this.
			printf("Checking name of subcomponent has not be implemented yet.\n");
			break;
		case(EXPR_IDENT):
			currName = nameScope_search(currScope, currExpr->name);
			// TODO: Error messages
			if(currName == NULL)
				retval++;
			else if(currName->decl == NULL)
				retval++;
			else
				currExpr->decl = currName->decl;
			break;
		case(EXPR_NUM):
			currName = nameScope_search(currScope, currExpr->name);
			// TODO: Error messages
			if(currName == NULL)
				retval++;
			else if(currName->decl == NULL)
				retval++;
			else
				currExpr->decl = currName->decl;
			break;
		case(EXPR_BOOL):
			// TODO: NOP?
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
			retval += checkExprName(currExpr->exprB, currScope);
			break;
		case(EXPR_ARR):
			retval += checkExprName(currExpr->exprA, currScope);
			retval += checkExprName(currExpr->exprB, currScope);
			break;
		case(EXPR_PAREN):
			retval += checkExprName(currExpr->exprA, currScope);
			break;
	}

	return retval;
}
